"""
Pipeline Orchestrator — automatically resolves engine dependencies, executes engines
in the correct order, validates outputs after each phase, and generates reports.
If any engine fails, downstream engines are skipped with a detailed error report.

Usage:
    orchestrator = Orchestrator(config)
    report = orchestrator.run_all()
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Type
from collections import defaultdict

import pandas as pd
from loguru import logger

from configs.config_loader import PlatformConfig, get_config
from engines.base_engine import BaseEngine, DataStore, EngineStatus


class Orchestrator:
    """
    The pipeline orchestrator that manages the execution of all simulation engines.
    Features:
    - Automatic dependency resolution via topological sort
    - Sequential execution in dependency order
    - Post-phase validation
    - Failure propagation (downstream engines skip on upstream failure)
    - Comprehensive generation report
    """

    def __init__(self, config: Optional[PlatformConfig] = None, output_base: str = "output"):
        self.config = config or get_config()
        self.output_base = output_base
        self.store = DataStore()
        self.engines: Dict[str, BaseEngine] = {}
        self.execution_order: List[str] = []
        self.report: Dict[str, dict] = {}
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Register all engines
        self._register_engines()

        # Resolve execution order
        self.execution_order = self._topological_sort()

        logger.info(f"Orchestrator initialized with {len(self.engines)} engines")
        logger.info(f"Execution order: {' → '.join(self.execution_order)}")

    def _register_engines(self):
        """Import and register all engine classes."""
        from engines.master_engine import MasterEngine
        from engines.population_engine import PopulationEngine
        from engines.police_engine import PoliceEngine
        from engines.time_engine import TimeEngine
        from engines.weather_engine import WeatherEngine
        from engines.festival_engine import FestivalEngine
        from engines.scenario_engine import ScenarioEngine
        from engines.media_engine import MediaEngine
        from engines.crime_engine.engine import CrimeEngine
        from engines.behaviour_engine.engine import BehaviourEngine
        from engines.gang_engine.engine import GangEngine
        from engines.investigation_engine.engine import InvestigationEngine
        from engines.narrative_engine.engine import NarrativeEngine
        from engines.evidence_engine.engine import EvidenceEngine
        from engines.communication_engine.engine import CommunicationEngine
        from engines.financial_engine.engine import FinancialEngine
        from engines.export_engine.engine import ExportEngine

        engine_classes = [
            MasterEngine,
            PopulationEngine,
            PoliceEngine,
            TimeEngine,
            WeatherEngine,
            FestivalEngine,
            ScenarioEngine,
            MediaEngine,
            CrimeEngine,
            BehaviourEngine,
            GangEngine,
            InvestigationEngine,
            NarrativeEngine,
            EvidenceEngine,
            CommunicationEngine,
            FinancialEngine,
            ExportEngine,
        ]

        for cls in engine_classes:
            engine = cls(config=self.config, store=self.store, output_base=self.output_base)
            self.engines[engine.name] = engine

    def _topological_sort(self) -> List[str]:
        """
        Resolve engine execution order using topological sort based on dependencies.
        Raises RuntimeError if a circular dependency is detected.
        """
        # Build adjacency list
        in_degree = defaultdict(int)
        graph = defaultdict(list)

        for name, engine in self.engines.items():
            if name not in in_degree:
                in_degree[name] = 0
            for dep in engine.dependencies:
                if dep in self.engines:
                    graph[dep].append(name)
                    in_degree[name] += 1

        # Kahn's algorithm
        queue = [name for name in self.engines if in_degree[name] == 0]
        order = []

        while queue:
            # Sort for deterministic order
            queue.sort()
            node = queue.pop(0)
            order.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.engines):
            missing = set(self.engines.keys()) - set(order)
            raise RuntimeError(
                f"Circular dependency detected among engines: {missing}. "
                f"Check the 'dependencies' property of each engine."
            )

        return order

    def run_all(self) -> Dict:
        """
        Execute all engines in dependency order.
        Returns a comprehensive generation report.
        """
        self.start_time = time.time()
        logger.info("=" * 60)
        logger.info("CRIME SIMULATION LABORATORY — FULL PIPELINE EXECUTION")
        logger.info("=" * 60)
        logger.info(f"Seed: {self.config.seed}")
        logger.info(f"Scale: {self.config.scale.cases} cases, {self.config.scale.population} population")
        logger.info(f"Years: {self.config.years.start} - {self.config.years.end}")
        logger.info("")

        failed_engines = set()

        for engine_name in self.execution_order:
            engine = self.engines[engine_name]

            # Check if any dependency has failed
            failed_deps = [dep for dep in engine.dependencies if dep in failed_engines]
            if failed_deps:
                reason = f"Skipped: dependency engine(s) failed: {failed_deps}"
                engine.status.skip(reason)
                self.report[engine_name] = engine.status.to_dict()
                logger.warning(f"SKIPPED '{engine_name}': {reason}")
                failed_engines.add(engine_name)
                continue

            # Run the engine
            try:
                logger.info(f"{'─' * 40}")
                logger.info(f"Running engine: {engine_name}")
                engine.run()
                self.report[engine_name] = engine.status.to_dict()
            except Exception as e:
                self.report[engine_name] = engine.status.to_dict()
                failed_engines.add(engine_name)
                logger.error(f"Engine '{engine_name}' FAILED: {e}")

        self.end_time = time.time()

        # Generate final report
        final_report = self._build_report(failed_engines)

        # Save report
        self._save_report(final_report)

        return final_report

    def run_engine(self, engine_name: str) -> Dict:
        """Run a single engine (and its dependencies if they haven't run yet)."""
        if engine_name not in self.engines:
            raise ValueError(f"Engine '{engine_name}' not found. Available: {list(self.engines.keys())}")

        engine = self.engines[engine_name]

        # Run dependencies first if they haven't produced data
        for dep in engine.dependencies:
            if dep in self.engines and self.engines[dep].status.status == EngineStatus.PENDING:
                logger.info(f"Auto-running dependency: {dep}")
                self.run_engine(dep)

        # Run the engine
        engine.run()
        self.report[engine_name] = engine.status.to_dict()

        return engine.status.to_dict()

    def _build_report(self, failed_engines: set) -> Dict:
        """Build the comprehensive generation report."""
        total_duration = (self.end_time - self.start_time) if self.end_time and self.start_time else 0
        total_records = sum(
            r.get("records_generated", 0) for r in self.report.values()
        )
        total_tables = sum(
            len(r.get("tables_generated", [])) for r in self.report.values()
        )

        success_count = sum(1 for r in self.report.values() if r["status"] == "COMPLETED")
        failed_count = sum(1 for r in self.report.values() if r["status"] == "FAILED")
        skipped_count = sum(1 for r in self.report.values() if r["status"] == "SKIPPED")

        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "seed": self.config.seed,
                "version": self.config.version,
                "years": f"{self.config.years.start}-{self.config.years.end}",
                "scale": self.config.scale.model_dump(),
            },
            "summary": {
                "total_duration_seconds": round(total_duration, 2),
                "total_records_generated": total_records,
                "total_tables_generated": total_tables,
                "engines_succeeded": success_count,
                "engines_failed": failed_count,
                "engines_skipped": skipped_count,
                "pipeline_status": "SUCCESS" if failed_count == 0 else "PARTIAL_FAILURE" if success_count > 0 else "FAILURE",
            },
            "datastore_summary": self.store.summary(),
            "engine_reports": self.report,
            "execution_order": self.execution_order,
            "failed_engines": list(failed_engines),
        }

    def _save_report(self, report: Dict):
        """Save the generation report to disk."""
        report_dir = Path(self.output_base) / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_path = report_dir / "generation_report.json"

        # Convert non-serializable types
        def _serialize(obj):
            if isinstance(obj, (pd.Timestamp, datetime)):
                return obj.isoformat()
            if hasattr(obj, "item"):  # numpy types
                return obj.item()
            return str(obj)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=_serialize)

        logger.info(f"Generation report saved to: {report_path}")

        # Print summary to console
        logger.info("")
        logger.info("=" * 60)
        logger.info("GENERATION REPORT SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {report['summary']['pipeline_status']}")
        logger.info(f"Duration: {report['summary']['total_duration_seconds']}s")
        logger.info(f"Records: {report['summary']['total_records_generated']}")
        logger.info(f"Tables: {report['summary']['total_tables_generated']}")
        logger.info(f"Succeeded: {report['summary']['engines_succeeded']}")
        logger.info(f"Failed: {report['summary']['engines_failed']}")
        logger.info(f"Skipped: {report['summary']['engines_skipped']}")
        logger.info("")

        if report["datastore_summary"]:
            logger.info("DataStore Contents:")
            for table, count in report["datastore_summary"].items():
                logger.info(f"  {table}: {count} records")
        logger.info("=" * 60)


def run_full_pipeline(config_path: Optional[str] = None, output_base: str = "output") -> Dict:
    """
    Convenience function: run the full pipeline from a config file path.
    This is the single command entry point.
    """
    config = get_config(config_path)
    orchestrator = Orchestrator(config=config, output_base=output_base)
    return orchestrator.run_all()
