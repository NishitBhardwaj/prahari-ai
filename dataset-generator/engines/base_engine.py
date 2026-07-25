"""
Base Engine class.
Every simulation engine inherits from BaseEngine, which provides:
- Configuration access
- Seeded random number generation for reproducibility
- Logging
- Output directory management
- Status tracking for the orchestrator
- Dependency declaration
"""

import os
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import numpy as np
import pandas as pd
from faker import Faker
from loguru import logger

from configs.config_loader import PlatformConfig, get_config


class EngineStatus:
    """Tracks the status of an engine's execution."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

    def __init__(self):
        self.status: str = self.PENDING
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.records_generated: int = 0
        self.tables_generated: List[str] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def start(self):
        self.status = EngineStatus.RUNNING
        self.start_time = time.time()

    def complete(self, records: int, tables: List[str]):
        self.status = EngineStatus.COMPLETED
        self.end_time = time.time()
        self.records_generated = records
        self.tables_generated = tables

    def fail(self, error: str):
        self.status = EngineStatus.FAILED
        self.end_time = time.time()
        self.errors.append(error)

    def skip(self, reason: str):
        self.status = EngineStatus.SKIPPED
        self.warnings.append(reason)

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "duration_seconds": round(self.duration_seconds, 2),
            "records_generated": self.records_generated,
            "tables_generated": self.tables_generated,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class DataStore:
    """
    Central in-memory data store that engines read from and write to.
    This ensures engines can depend on data from prior engines without
    writing/reading intermediate files during simulation.
    """

    def __init__(self):
        self._data: Dict[str, pd.DataFrame] = {}
        self._graph_edges: List[Dict[str, Any]] = []

    def add_edge(self, source: str, relation: str, target: str, properties: Dict[str, Any] = None):
        """Add a semantic edge to the live knowledge graph."""
        self._graph_edges.append({
            "source": source,
            "relation": relation,
            "target": target,
            "properties": properties or {}
        })

    def get_graph(self) -> pd.DataFrame:
        """Return the live knowledge graph as a DataFrame."""
        return pd.DataFrame(self._graph_edges)

    def put(self, table_name: str, df: pd.DataFrame):
        """Store a DataFrame under a table name."""
        self._data[table_name] = df
        logger.info(f"DataStore: stored '{table_name}' with {len(df)} records")

    def get(self, table_name: str) -> pd.DataFrame:
        """Retrieve a DataFrame by table name. Raises KeyError if missing."""
        if table_name not in self._data:
            raise KeyError(
                f"DataStore: table '{table_name}' not found. "
                f"Available tables: {list(self._data.keys())}"
            )
        return self._data[table_name]

    def has(self, table_name: str) -> bool:
        """Check if a table exists in the store."""
        return table_name in self._data

    def tables(self) -> List[str]:
        """List all available table names."""
        return list(self._data.keys())

    def summary(self) -> Dict[str, int]:
        """Return a summary of all tables and their record counts."""
        res = {name: len(df) for name, df in self._data.items()}
        res["knowledge_graph_edges"] = len(self._graph_edges)
        return res


class BaseEngine(ABC):
    """
    Abstract base class for all simulation engines.

    Every engine must implement:
        - name: str property — unique engine name
        - dependencies: List[str] — list of engine names this engine depends on
        - generate() — the main generation method

    The engine has access to:
        - self.config: PlatformConfig — the validated platform configuration
        - self.rng: np.random.Generator — seeded random number generator
        - self.fake: Faker — seeded Faker instance for Indian locale data
        - self.store: DataStore — shared data store for inter-engine communication
        - self.output_dir: Path — directory for this engine's output files
        - self.status: EngineStatus — tracks execution status
    """

    def __init__(self, config: PlatformConfig, store: DataStore, output_base: str = "output"):
        self.config = config
        self.store = store
        self.status = EngineStatus()

        # Seeded RNG for reproducibility
        self.rng = np.random.default_rng(config.seed)
        self.fake = Faker("en_IN")
        Faker.seed(config.seed)

        # Output directory
        self.output_dir = Path(output_base) / self.name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Logger
        self.logger = logger.bind(engine=self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name for this engine (e.g., 'master', 'population', 'crime')."""
        ...

    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        """List of engine names this engine depends on (executed before this engine)."""
        ...

    @abstractmethod
    def generate(self) -> Dict[str, pd.DataFrame]:
        """
        Main generation method. Must return a dict of {table_name: DataFrame}.
        All DataFrames are automatically stored in the DataStore after generation.
        """
        ...

    def run(self) -> EngineStatus:
        """
        Execute this engine with full status tracking, error handling, and DataStore integration.
        This is called by the orchestrator — engines should NOT override this method.
        """
        self.logger.info(f"Engine '{self.name}' starting...")
        self.status.start()

        try:
            # Check dependencies
            for dep in self.dependencies:
                required_tables = self._get_dependency_tables(dep)
                for table in required_tables:
                    if not self.store.has(table):
                        raise RuntimeError(
                            f"Engine '{self.name}' requires table '{table}' from engine '{dep}', "
                            f"but it is not available in the DataStore. "
                            f"Ensure engine '{dep}' runs successfully before '{self.name}'."
                        )

            # Run generation
            results = self.generate()

            # Store results
            total_records = 0
            table_names = []
            for table_name, df in results.items():
                self.store.put(table_name, df)
                total_records += len(df)
                table_names.append(table_name)

            self.status.complete(total_records, table_names)
            self.logger.info(
                f"Engine '{self.name}' completed: {total_records} records across {len(table_names)} tables "
                f"in {self.status.duration_seconds:.2f}s"
            )

        except Exception as e:
            self.status.fail(str(e))
            self.logger.error(f"Engine '{self.name}' FAILED: {e}")
            raise

        return self.status

    def _get_dependency_tables(self, engine_name: str) -> List[str]:
        """
        Map an engine name to the tables it is expected to produce.
        Used for dependency validation before running.
        """
        engine_table_map = {
            "master": [
                "states", "districts", "taluks", "police_stations", "courts",
                "ranks", "designations", "occupations", "religions", "castes",
                "case_categories", "case_statuses", "gravity_offences",
                "crime_heads", "crime_sub_heads", "acts", "sections", "unit_types",
            ],
            "population": ["persons", "households", "family_relationships"],
            "police": ["employees", "postings"],
            "social": ["social_links_family", "social_links_friends", "social_links_work",
                       "social_links_neighbour", "social_links_online"],
            "activity": ["daily_activities"],
            "time": ["time_context"],
            "weather": ["weather_records"],
            "festival": ["festival_calendar"],
            "scenario": ["active_scenarios", "probability_modifiers"],
            "crime": ["cases", "case_acts", "case_sections", "crime_events",
                      "victims", "accused_records", "complainants"],
            "behaviour": ["modus_operandi", "mo_similarities"],
            "criminal_career": ["criminal_careers"],
            "gang": ["gangs", "gang_memberships", "gang_territories"],
            "victimization": [],  # modifies existing victims
            "witness": ["witnesses"],
            "timeline": ["case_timelines", "arrests", "bails", "chargesheets",
                        "court_proceedings", "judgements"],
            "communication": ["phone_calls", "sms_records", "email_metadata", "social_connections"],
            "finance": ["bank_accounts", "transactions", "upi_records"],
            "mobility": ["travel_records", "gps_tracks", "vehicle_routes"],
            "vehicle": ["vehicles"],
            "evidence": ["evidence_items", "chain_of_custody", "weapons"],
            "cctv": ["cctv_cameras", "cctv_recordings", "cctv_frames", "cctv_detections"],
            "documents": [
                "fir_narratives", "complaint_statements", "witness_statements",
                "investigation_diaries", "officer_notes", "forensic_reports",
                "evidence_reports", "chargesheet_summaries", "court_orders",
            ],
            "features": ["crime_features", "spatial_features", "temporal_features",
                        "network_features", "behavioural_features"],
            "risk": [
                "risk_scores", "hotspot_scores", "repeat_offender_scores",
                "network_scores", "anomaly_scores", "investigation_priorities",
                "crime_clusters", "mo_similarity_scores",
            ],
        }
        return engine_table_map.get(engine_name, [])

    def save_csv(self, df: pd.DataFrame, filename: str):
        """Save a DataFrame to CSV in this engine's output directory."""
        path = self.output_dir / f"{filename}.csv"
        df.to_csv(path, index=False)
        self.logger.info(f"Saved {len(df)} records to {path}")

    def save_parquet(self, df: pd.DataFrame, filename: str):
        """Save a DataFrame to Parquet in this engine's output directory."""
        path = self.output_dir / f"{filename}.parquet"
        df.to_parquet(path, index=False)
        self.logger.info(f"Saved {len(df)} records to {path}")

    def random_choice(self, options: list, size: int = 1, p: list = None):
        """Seeded random choice from a list."""
        return self.rng.choice(options, size=size, p=p, replace=True)

    def random_int(self, low: int, high: int, size: int = 1) -> np.ndarray:
        """Seeded random integers."""
        return self.rng.integers(low, high + 1, size=size)

    def random_float(self, low: float, high: float, size: int = 1) -> np.ndarray:
        """Seeded random floats."""
        return self.rng.uniform(low, high, size=size)

    def random_normal(self, mean: float, std: float, size: int = 1) -> np.ndarray:
        """Seeded normal distribution."""
        return self.rng.normal(mean, std, size=size)

    def random_date(self, start_year: int, end_year: int) -> str:
        """Generate a random date string between two years."""
        year = int(self.rng.integers(start_year, end_year + 1))
        month = int(self.rng.integers(1, 13))
        day = int(self.rng.integers(1, 29))  # Safe for all months
        return f"{year:04d}-{month:02d}-{day:02d}"
