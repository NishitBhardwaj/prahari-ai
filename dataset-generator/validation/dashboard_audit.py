"""
Dashboard Readiness Audit — verifies that every planned visualization
panel has all the columns and tables it needs.

Returns a detailed readiness matrix with gap analysis and gap resolution advice.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Visualization Requirements Matrix ────────────────────────────────────────
#
# Format:  "Panel Name": [
#     (table_name, [required_columns], "Description"),
#     ...  # A panel can require data from multiple tables
# ]
#
VISUALIZATION_REQUIREMENTS: Dict[str, List[tuple]] = {
    "District Heatmaps": [
        ("cases", ["latitude", "longitude", "district_id", "crime_head_name", "year"], "Case locations for heatmap density"),
    ],
    "Police Station Drill-Down": [
        ("cases", ["station_id", "station_name", "district_id", "crime_head_name", "status_name"], "Cases per station"),
        ("employees", ["station_id", "employee_id", "rank_name"], "Officer count per station"),
    ],
    "Crime Timelines": [
        ("crime_events", ["case_id", "event_date", "event_time", "event_type", "description"], "Temporal crime event log"),
        ("cases", ["case_id", "date_of_report", "crime_head_name", "status_name"], "Case anchors for timeline"),
    ],
    "Network Graph / Link Analysis": [
        ("accused_records", ["person_id", "case_id", "gang_id", "arrest_status"], "Accused nodes"),
        ("knowledge_graph_edges", ["source", "relation", "target"], "Neo4j relationship edges"),
        ("gangs", ["gang_id", "gang_name", "syndicate_type"], "Gang cluster nodes"),
        ("call_detail_records", ["caller_device_id", "receiver_device_id", "call_timestamp"], "Communication edges"),
        ("financial_transactions", ["sender_account_id", "receiver_account_id", "amount", "is_suspicious"], "Financial edges"),
    ],
    "Sankey Diagrams (Legal Flow)": [
        ("cases", ["case_id", "status_name", "crime_head_name"], "Case status nodes"),
        ("court_proceedings", ["case_id", "proceeding_type", "status"], "Legal flow stages"),
        ("chargesheet_details", ["case_id", "status"], "Chargesheet state"),
    ],
    "Repeat Offender Dashboard": [
        ("accused_records", ["person_id", "case_id", "is_habitual_offender", "label_repeat_offender", "arrest_status"], "Habitual offender flags"),
        ("modus_operandi_records", ["person_id", "primary_method", "violence_risk_score", "flight_risk_score"], "Behavioural profile"),
    ],
    "Risk Score Dashboard": [
        ("modus_operandi_records", ["person_id", "violence_risk_score", "flight_risk_score", "psychological_traits"], "Risk scores"),
        ("cases", ["case_id", "explainability_metadata", "label_is_gang_related", "label_is_solved"], "Explainability context"),
        ("accused_records", ["person_id", "gang_id", "label_repeat_offender"], "Gang & recidivism context"),
    ],
    "Investigation Timelines": [
        ("investigation_diaries", ["case_id", "entry_date", "activity_type", "notes", "officer_id"], "IO procedural log"),
        ("crime_events", ["case_id", "event_date", "event_type"], "Event anchors"),
    ],
    "Explainability Panels": [
        ("cases", ["case_id", "explainability_metadata", "crime_head_name", "label_is_gang_related", "label_is_cyber"], "XAI metadata payload"),
        ("modus_operandi_records", ["person_id", "violence_risk_score", "flight_risk_score", "psychological_traits"], "Behavioural XAI"),
    ],
    "Geospatial Crime Hotspot Map": [
        ("cases", ["latitude", "longitude", "crime_head_name", "year", "district_id"], "Point data for PostGIS"),
    ],
    "Gang Intelligence Dashboard": [
        ("gangs", ["gang_id", "gang_name", "syndicate_type", "threat_level", "operational_base_district"], "Gang profiles"),
        ("accused_records", ["gang_id", "person_id", "case_id"], "Member-case links"),
        ("financial_transactions", ["is_suspicious", "amount", "transaction_type"], "Hawala / money flow"),
    ],
    "Cyber Fraud Analytics": [
        ("cases", ["case_id", "crime_head_name", "label_is_cyber", "year"], "Cyber crime flagging"),
        ("financial_transactions", ["is_suspicious", "amount", "remarks"], "Financial fraud trails"),
        ("call_detail_records", ["caller_device_id", "receiver_device_id", "call_timestamp"], "CDRs for pre-fraud contacts"),
    ],
    "AI Model Training Datasets": [
        ("cases", ["label_is_solved", "label_is_gang_related", "label_is_cyber", "explainability_metadata"], "Supervised labels"),
        ("accused_records", ["label_repeat_offender", "label_is_gang_related"], "Recidivism labels"),
    ],
    "Evidence & Forensics Panel": [
        ("evidence", ["evidence_id", "case_id", "category", "description", "seizure_date"], "Seizure records"),
        ("fsl_reports", ["report_id", "evidence_id", "result_status", "findings"], "FSL results"),
    ],
    "CDR / Communication Analysis": [
        ("call_detail_records", ["caller_device_id", "receiver_device_id", "call_timestamp", "duration_seconds", "call_type"], "CDR rows"),
        ("mobile_devices", ["device_id", "person_id", "phone_number", "provider"], "Device registry"),
    ],
}


class DashboardReadinessAuditor:
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.csv_dir = self.output_dir / "csv"
        self._tables: Dict[str, pd.DataFrame] = {}
        self.results: List[Dict[str, Any]] = []

    def _load(self, name: str) -> pd.DataFrame:
        if name in self._tables:
            return self._tables[name]
        path = self.csv_dir / f"{name}.csv"
        if path.exists():
            df = pd.read_csv(path, nrows=5, low_memory=False)  # We only need headers
            self._tables[name] = df
            return df
        return pd.DataFrame()

    def run(self) -> Dict[str, Any]:
        print("\n[DASHBOARD AUDIT] Checking visualization readiness...")

        ready_count = 0
        partial_count = 0
        gap_count = 0

        for panel, requirements in VISUALIZATION_REQUIREMENTS.items():
            panel_issues = []
            panel_available = []

            for table_name, required_cols, description in requirements:
                df = self._load(table_name)
                if df.empty:
                    panel_issues.append({
                        "table": table_name,
                        "issue": "TABLE_MISSING",
                        "description": description,
                        "missing_columns": required_cols,
                    })
                    continue

                missing_cols = [c for c in required_cols if c not in df.columns]
                if missing_cols:
                    panel_issues.append({
                        "table": table_name,
                        "issue": "COLUMNS_MISSING",
                        "description": description,
                        "missing_columns": missing_cols,
                        "available_columns": list(df.columns),
                    })
                else:
                    panel_available.append({
                        "table": table_name,
                        "columns": required_cols,
                        "description": description,
                    })

            if not panel_issues:
                status = "READY"
                ready_count += 1
            elif panel_available:
                status = "PARTIAL"
                partial_count += 1
            else:
                status = "NOT_READY"
                gap_count += 1

            self.results.append({
                "panel": panel,
                "status": status,
                "available": panel_available,
                "gaps": panel_issues,
            })

        total = len(VISUALIZATION_REQUIREMENTS)
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "output_dir": str(self.output_dir),
            "summary": {
                "total_panels": total,
                "ready": ready_count,
                "partial": partial_count,
                "not_ready": gap_count,
                "readiness_score": f"{round((ready_count + 0.5 * partial_count) / total * 100)}%",
            },
            "panels": self.results,
        }

        # Save outputs
        report_dir = self.output_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)

        json_path = report_dir / "dashboard_readiness_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        md_path = report_dir / "dashboard_readiness_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            s = report["summary"]
            f.write("# Dashboard Readiness Audit\n\n")
            f.write(f"**Generated:** {report['generated_at']}\n\n")
            f.write(f"**Readiness Score:** {s['readiness_score']}\n\n")
            f.write(f"| Metric | Count |\n|---|---|\n")
            f.write(f"| Total Panels | {s['total_panels']} |\n")
            f.write(f"| Ready | {s['ready']} |\n")
            f.write(f"| Partial | {s['partial']} |\n")
            f.write(f"| Not Ready | {s['not_ready']} |\n\n")
            f.write("---\n\n## Panel Status\n\n")
            f.write("| Panel | Status |\n|---|---|\n")
            for r in self.results:
                icon = "READY" if r["status"] == "READY" else ("PARTIAL" if r["status"] == "PARTIAL" else "NOT READY")
                f.write(f"| {r['panel']} | {icon} |\n")

            gaps = [r for r in self.results if r["gaps"]]
            if gaps:
                f.write("\n---\n\n## Gap Analysis\n\n")
                for r in gaps:
                    f.write(f"### {r['panel']} ({r['status']})\n\n")
                    for g in r["gaps"]:
                        f.write(f"- **Table `{g['table']}`**: {g['issue']}")
                        if g.get("missing_columns"):
                            f.write(f" — Missing: `{'`, `'.join(g['missing_columns'])}`")
                        f.write("\n")
                    f.write("\n")

        # Print summary
        print(f"\n  Readiness Score: {report['summary']['readiness_score']}")
        print(f"  Ready:           {ready_count}/{total}")
        print(f"  Partial:         {partial_count}/{total}")
        print(f"  Not Ready:       {gap_count}/{total}")
        print(f"\n  Reports saved to:")
        print(f"    {md_path}")
        print(f"    {json_path}")

        return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run dashboard readiness audit on generated output")
    parser.add_argument("--output", type=str, default="output", help="Output directory to audit")
    args = parser.parse_args()

    auditor = DashboardReadinessAuditor(output_dir=args.output)
    auditor.run()
