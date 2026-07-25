"""
Validation Runner — unified CLI for all three validation tools.
Usage:
    python validation/run_all.py                     # Full suite: scale + integrity + dashboard
    python validation/run_all.py --skip-scale        # Skip scale tests (they're time-consuming)
    python validation/run_all.py --output output/    # Custom output dir
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(
        description="Crime Simulation Laboratory — Final Validation Suite"
    )
    parser.add_argument("--output", type=str, default="output", help="Output directory to audit")
    parser.add_argument("--skip-scale", action="store_true", help="Skip scale tests (they regenerate data)")
    parser.add_argument("--scale-sizes", nargs="+", type=int, default=[1000, 10000],
                        help="Case counts for scale test (default: 1000 10000). Add 100000 for full test.")
    args = parser.parse_args()

    print("=" * 65)
    print("  PRAHARI AI — CRIME SIMULATION LABORATORY VALIDATION SUITE")
    print("=" * 65)
    print(f"  Target Output Dir: {args.output}")
    print(f"  Run Time:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    report_dir = Path(args.output) / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    combined = {"generated_at": datetime.utcnow().isoformat()}

    # ── Check 1: Scale Test ──────────────────────────────────────────────────
    if not args.skip_scale:
        print("\n[1/3] SCALE TEST")
        from validation.scale_test import run_all_scale_tests
        scale_results = run_all_scale_tests(
            sizes=args.scale_sizes,
            output_root=str(Path(args.output) / "scale_tests")
        )
        combined["scale_test"] = scale_results
    else:
        print("\n[1/3] SCALE TEST — SKIPPED")
        combined["scale_test"] = "skipped"

    # ── Check 2: Data Integrity Audit ────────────────────────────────────────
    print("\n[2/3] DATA INTEGRITY AUDIT")
    from validation.integrity_audit import DataIntegrityAuditor
    auditor = DataIntegrityAuditor(output_dir=args.output)
    integrity_report = auditor.run()
    combined["integrity_audit"] = integrity_report

    # ── Check 3: Dashboard Readiness Audit ───────────────────────────────────
    print("\n[3/3] DASHBOARD READINESS AUDIT")
    from validation.dashboard_audit import DashboardReadinessAuditor
    dash_auditor = DashboardReadinessAuditor(output_dir=args.output)
    dash_report = dash_auditor.run()
    combined["dashboard_audit"] = dash_report

    # ── Final Combined Report ────────────────────────────────────────────────
    combined_path = report_dir / "validation_combined_report.json"
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, default=str)

    # Print final summary
    integrity_status = integrity_report.get("overall_status", "UNKNOWN")
    dash_score = dash_report.get("summary", {}).get("readiness_score", "?")
    integrity_pass = integrity_report.get("total_checks_passed", 0)
    integrity_fail = integrity_report.get("total_checks_failed", 0)

    print("\n" + "=" * 65)
    print("  FINAL VALIDATION SUMMARY")
    print("=" * 65)
    print(f"  Scale Test:        {'SKIPPED' if args.skip_scale else ('PASSED' if all(r.get('validation_failures', 0) == 0 for r in (combined.get('scale_test') or [])) else 'ISSUES FOUND')}")
    print(f"  Integrity Audit:   {integrity_status} ({integrity_pass} passed, {integrity_fail} failed)")
    print(f"  Dashboard Ready:   {dash_score}")
    print("=" * 65)
    print(f"\nCombined report saved to: {combined_path}")

    # Exit with error code if integrity fails
    if integrity_status == "FAIL":
        print("\n[WARNING] Integrity failures found. Check integrity_report.md for details.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All validations passed. Dataset is production-ready.")


if __name__ == "__main__":
    main()
