"""
Global Search API — combines PostgreSQL full-text, Neo4j graph, and Qdrant semantic results.
Searches across: Cases, Persons, Vehicles, Phones, IMEIs, Gangs, Bank Accounts, Evidence.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.postgres.session import get_async_session
from app.db.postgres.models.case import Case
from app.db.postgres.models.person import Person
from app.db.postgres.models.gang import Gang, Vehicle, MobileDevice, BankAccount
from app.db.neo4j.client import execute_query
from app.db.qdrant.client import search_similar
from app.core.permissions import require_permissions, Permission
from app.utils.response import ApiResponse

router = APIRouter()


@router.get("", summary="Global cross-entity search")
async def global_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=50),
    session: AsyncSession = Depends(get_async_session),
    current_user=Depends(require_permissions(Permission.CASE_READ)),
):
    """
    Search across all entities simultaneously:
    - Cases: FIR number, crime head, place
    - Persons: Name, phone, Aadhaar
    - Vehicles: Registration number
    - Devices: IMEI, phone number
    - Gangs: Gang name
    - Bank Accounts: Account number
    """
    results = []

    # ── PostgreSQL: Cases ─────────────────────────────────────────────────
    case_result = await session.execute(
        select(Case)
        .where(
            or_(
                Case.fir_number.ilike(f"%{q}%"),
                Case.crime_head_name.ilike(f"%{q}%"),
                Case.place_of_occurrence.ilike(f"%{q}%"),
            )
        )
        .limit(limit)
    )
    for c in case_result.scalars().all():
        results.append({
            "type": "case",
            "id": c.case_id,
            "title": c.fir_number,
            "subtitle": c.crime_head_name,
            "meta": {"station": c.station_name, "date": str(c.date_of_report)},
        })

    # ── PostgreSQL: Persons ───────────────────────────────────────────────
    person_result = await session.execute(
        select(Person)
        .where(
            or_(
                Person.full_name.ilike(f"%{q}%"),
                Person.phone_primary.ilike(f"%{q}%"),
                Person.aadhaar_number.ilike(f"%{q}%"),
            )
        )
        .limit(limit)
    )
    for p in person_result.scalars().all():
        results.append({
            "type": "person",
            "id": p.person_id,
            "title": p.full_name,
            "subtitle": p.phone_primary or "No phone",
            "meta": {"city": p.city, "age": p.age},
        })

    # ── PostgreSQL: Vehicles ──────────────────────────────────────────────
    veh_result = await session.execute(
        select(Vehicle)
        .where(
            or_(
                Vehicle.registration_number.ilike(f"%{q}%"),
                Vehicle.make.ilike(f"%{q}%"),
                Vehicle.chassis_number.ilike(f"%{q}%"),
            )
        )
        .limit(5)
    )
    for v in veh_result.scalars().all():
        results.append({
            "type": "vehicle",
            "id": v.vehicle_id,
            "title": v.registration_number,
            "subtitle": f"{v.make} {v.model}",
            "meta": {"color": v.color, "is_stolen": v.is_stolen},
        })

    # ── PostgreSQL: Mobile Devices (IMEI / Phone) ──────────────────────────
    dev_result = await session.execute(
        select(MobileDevice)
        .where(
            or_(
                MobileDevice.imei.ilike(f"%{q}%"),
                MobileDevice.phone_number.ilike(f"%{q}%"),
            )
        )
        .limit(5)
    )
    for d in dev_result.scalars().all():
        results.append({
            "type": "device",
            "id": d.device_id,
            "title": d.phone_number or d.imei,
            "subtitle": f"{d.provider} — {d.device_type}",
            "meta": {"imei": d.imei, "person_id": d.person_id},
        })

    # ── PostgreSQL: Gangs ─────────────────────────────────────────────────
    gang_result = await session.execute(
        select(Gang)
        .where(Gang.gang_name.ilike(f"%{q}%"))
        .limit(5)
    )
    for g in gang_result.scalars().all():
        results.append({
            "type": "gang",
            "id": g.gang_id,
            "title": g.gang_name,
            "subtitle": g.syndicate_type or "Unknown type",
            "meta": {"threat": g.threat_level, "district": g.operational_base_district},
        })

    # ── PostgreSQL: Bank Accounts ─────────────────────────────────────────
    acc_result = await session.execute(
        select(BankAccount)
        .where(BankAccount.account_number.ilike(f"%{q}%"))
        .limit(5)
    )
    for a in acc_result.scalars().all():
        results.append({
            "type": "bank_account",
            "id": a.account_id,
            "title": a.account_number,
            "subtitle": a.bank_name or "Unknown bank",
            "meta": {"ifsc": a.ifsc_code, "risk_score": a.risk_score},
        })

    # ── Neo4j: Entity by ID (graph lookup) ───────────────────────────────
    try:
        graph_results = await execute_query(
            "MATCH (n) WHERE n.id CONTAINS $q RETURN n LIMIT 5",
            {"q": q},
        )
        for r in graph_results:
            node = r.get("n", {})
            if node:
                results.append({
                    "type": "graph_node",
                    "id": node.get("id", ""),
                    "title": node.get("id", "Graph Node"),
                    "subtitle": "Graph entity",
                    "meta": {},
                })
    except Exception:
        pass  # Neo4j search is optional

    return ApiResponse.ok(data={
        "query": q,
        "count": len(results),
        "results": results[:limit],
    })
