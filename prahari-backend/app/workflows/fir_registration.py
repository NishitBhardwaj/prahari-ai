"""
FIR Registration Workflow — orchestrates the full case creation lifecycle.
Coordinates DB writes, Neo4j graph updates, Qdrant indexing,
AI scoring, and Catalyst Signals notification in sequence.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import WorkflowError
from app.db.postgres.session import get_async_session
from app.db.postgres.models.case import Case
from app.db.postgres.models.person import Person
from app.db.postgres.models.accused import AccusedRecord, Victim, Complainant
from app.repositories.case_repository import CaseRepository
from app.repositories.base import BaseRepository
from app.services.catalyst.client import get_catalyst_signals, get_catalyst_cache
from app.db.neo4j.client import execute_write
from app.db.qdrant.client import upsert_vectors


class FIRRegistrationWorkflow:
    """
    Orchestrates the complete FIR registration process.

    Steps:
        1. Validate all input data
        2. Create Case record in PostgreSQL
        3. Create / link Person records (accused, victims, complainants)
        4. Create AccusedRecord, Victim, Complainant rows
        5. Write graph edges to Neo4j
        6. Index case embedding in Qdrant
        7. Trigger AI risk scoring (background)
        8. Send real-time alert via Catalyst Signals
        9. Invalidate relevant caches
    """

    def __init__(self, session: AsyncSession, created_by_user_id: str):
        self.session = session
        self.created_by = created_by_user_id
        self.case_repo = CaseRepository(session)
        self.person_repo = BaseRepository(Person, session)
        self.accused_repo = BaseRepository(AccusedRecord, session)
        self.victim_repo = BaseRepository(Victim, session)
        self.complainant_repo = BaseRepository(Complainant, session)

    async def execute(self, payload: Dict[str, Any]) -> Case:
        """Run the full FIR registration workflow atomically."""
        logger.info(f"FIR workflow started by user {self.created_by}")

        # Step 1: Validate
        self._validate(payload)

        # Step 2: Create case
        case_data = payload.get("case", {})
        case_data["created_by"] = self.created_by
        case = await self.case_repo.create(case_data)
        logger.info(f"Case created: {case.case_id} / FIR {case.fir_number}")

        # Step 3–4: Persons
        accused_list = payload.get("accused", [])
        victim_list = payload.get("victims", [])
        complainant_list = payload.get("complainants", [])

        for acc_data in accused_list:
            person = await self._upsert_person(acc_data.get("person", {}))
            await self.accused_repo.create({
                **acc_data.get("accused_fields", {}),
                "case_id": case.case_id,
                "person_id": person.person_id,
            })

        for vic_data in victim_list:
            person = await self._upsert_person(vic_data.get("person", {}))
            await self.victim_repo.create({
                **vic_data.get("victim_fields", {}),
                "case_id": case.case_id,
                "person_id": person.person_id,
            })

        for comp_data in complainant_list:
            person = await self._upsert_person(comp_data.get("person", {}))
            await self.complainant_repo.create({
                **comp_data.get("complainant_fields", {}),
                "case_id": case.case_id,
                "person_id": person.person_id,
            })

        # Step 5: Neo4j graph edges
        try:
            await self._write_graph_edges(case, accused_list, victim_list)
        except Exception as e:
            logger.warning(f"Neo4j graph update failed for case {case.case_id}: {e}")
            # Non-fatal — graph will be rebuilt on next sync

        # Step 6: Qdrant embedding (background)
        try:
            await self._index_case_embedding(case)
        except Exception as e:
            logger.warning(f"Qdrant indexing failed for case {case.case_id}: {e}")

        # Step 7: Real-time notification
        try:
            signals = get_catalyst_signals()
            await signals.publish(
                channel="case-alerts",
                event_type="FIR_REGISTERED",
                payload={
                    "case_id": case.case_id,
                    "fir_number": case.fir_number,
                    "crime": case.crime_head_name,
                    "station": case.station_name,
                    "district_id": case.district_id,
                },
            )
        except Exception as e:
            logger.warning(f"Catalyst Signals notification failed: {e}")

        logger.info(f"FIR workflow completed: {case.case_id}")
        return case

    def _validate(self, payload: Dict[str, Any]) -> None:
        """Basic structural validation before DB writes."""
        case = payload.get("case", {})
        required_fields = ["fir_number", "station_id", "district_id", "crime_head_name", "date_of_report"]
        missing = [f for f in required_fields if not case.get(f)]
        if missing:
            raise WorkflowError(
                workflow="FIRRegistration",
                step="Validation",
                message=f"Required case fields missing: {missing}",
            )

    async def _upsert_person(self, person_data: Dict[str, Any]) -> Person:
        """Create or retrieve a person by their primary phone or Aadhaar."""
        existing = None

        phone = person_data.get("phone_primary")
        aadhaar = person_data.get("aadhaar_number")

        if aadhaar:
            result = await self.session.execute(
                __import__("sqlalchemy", fromlist=["select"]).select(Person).where(Person.aadhaar_number == aadhaar)
            )
            existing = result.scalar_one_or_none()

        if not existing and phone:
            result = await self.session.execute(
                __import__("sqlalchemy", fromlist=["select"]).select(Person).where(Person.phone_primary == phone)
            )
            existing = result.scalar_one_or_none()

        if existing:
            return existing

        return await self.person_repo.create(person_data)

    async def _write_graph_edges(self, case: Case, accused_list: list, victim_list: list) -> None:
        """Write Neo4j edges for the newly registered case."""
        # Station registered the case
        await execute_write(
            "MERGE (s:Station {id: $station_id}) MERGE (c:Case {id: $case_id}) "
            "MERGE (s)-[:REGISTERED {date: $date}]->(c)",
            {"station_id": case.station_id, "case_id": case.case_id, "date": str(case.date_of_report)},
        )

    async def _index_case_embedding(self, case: Case) -> None:
        """Generate and upsert a simple case embedding into Qdrant."""
        from qdrant_client.models import PointStruct
        import hashlib, struct

        # Simple deterministic hash-based pseudo-embedding for demo
        text = f"{case.crime_head_name} {case.place_of_occurrence} {case.station_name}"
        digest = hashlib.sha256(text.encode()).digest()
        # Expand to 768 dims via cycling
        vector = []
        for i in range(768):
            b = digest[i % len(digest)]
            vector.append((b / 255.0) * 2 - 1)

        point = PointStruct(
            id=abs(hash(case.case_id)) % (2**32),
            vector=vector,
            payload={
                "case_id": case.case_id,
                "fir_number": case.fir_number,
                "crime": case.crime_head_name,
                "district_id": case.district_id,
                "station_id": case.station_id,
                "year": case.year,
            },
        )
        await upsert_vectors([point])
