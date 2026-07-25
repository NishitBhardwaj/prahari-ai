"""
Scale Test — runs the generator at 1K, 10K, and 100K case sizes.
Records: generation time, peak memory usage, image count, graph stats, validation failures.
"""

import time
import tracemalloc
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_scale_test(n_cases: int, output_root: str) -> dict:
    """Run a single scale test for n_cases and return metrics."""
    from configs.config_loader import get_config, reset_config
    from orchestrator import Orchestrator

    # Override scale in config
    reset_config()
    cfg = get_config()

    # Proportionally scale supporting entities
    ratio = n_cases / 1000
    cfg.scale.cases = n_cases
    cfg.scale.population = max(5000, int(50000 * ratio))
    cfg.scale.households = max(1200, int(12000 * ratio))
    cfg.scale.victims = max(200, int(1600 * ratio))
    cfg.scale.accused = max(100, int(700 * ratio))
    cfg.scale.complainants = max(200, int(1200 * ratio))
    cfg.scale.witnesses = max(400, int(2000 * ratio))
    cfg.scale.employees = max(500, int(3000 * ratio))
    cfg.scale.vehicles = max(1000, int(8000 * ratio))
    cfg.scale.gangs = max(5, int(50 * ratio))
    cfg.scale.cctv_cameras = max(50, int(500 * ratio))

    output_dir = Path(output_root) / f"scale_{n_cases}"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[SCALE TEST] Starting {n_cases:,} cases -> {output_dir}")

    # Track memory
    tracemalloc.start()
    start_time = time.time()

    try:
        orch = Orchestrator(config=cfg, output_base=str(output_dir))
        report = orch.run_all()
    except Exception as e:
        elapsed = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {
            "n_cases": n_cases,
            "status": "FAILED",
            "error": str(e),
            "elapsed_seconds": round(elapsed, 2),
            "peak_memory_mb": round(peak / 1024 / 1024, 2),
        }

    elapsed = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Count generated images
    media_dir = output_dir / "media"
    image_count = 0
    if media_dir.exists():
        for ext in ["*.jpg", "*.jpeg", "*.png"]:
            image_count += len(list(media_dir.rglob(ext)))

    # Count exported CSVs
    csv_dir = output_dir / "csv"
    csv_count = len(list(csv_dir.glob("*.csv"))) if csv_dir.exists() else 0

    # Graph stats
    ds_summary = report.get("datastore_summary", {})
    graph_edges = ds_summary.get("knowledge_graph_edges", 0)

    # Validation failures from engine reports
    validation_failures = sum(
        1 for r in report.get("engine_reports", {}).values()
        if r.get("status") == "FAILED"
    )

    result = {
        "n_cases": n_cases,
        "status": report.get("summary", {}).get("pipeline_status", "UNKNOWN"),
        "elapsed_seconds": round(elapsed, 2),
        "records_per_second": round(report.get("summary", {}).get("total_records_generated", 0) / max(elapsed, 0.01)),
        "peak_memory_mb": round(peak / 1024 / 1024, 2),
        "total_records": report.get("summary", {}).get("total_records_generated", 0),
        "total_tables": report.get("summary", {}).get("total_tables_generated", 0),
        "image_count": image_count,
        "csv_files": csv_count,
        "neo4j_edges": graph_edges,
        "engines_succeeded": report.get("summary", {}).get("engines_succeeded", 0),
        "engines_failed": report.get("summary", {}).get("engines_failed", 0),
        "validation_failures": validation_failures,
        "output_dir": str(output_dir),
    }

    print(f"  [DONE] {n_cases:,} cases | {elapsed:.1f}s | {result['peak_memory_mb']:.0f} MB | {graph_edges:,} edges | {image_count:,} images | failures={validation_failures}")
    return result


def run_all_scale_tests(sizes: list = None, output_root: str = "output/scale_tests"):
    """Run scale tests for all provided sizes and produce a summary report."""
    if sizes is None:
        sizes = [1_000, 10_000, 100_000]

    Path(output_root).mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("   CRIME SIMULATION LABORATORY — SCALE TEST")
    print("=" * 60)

    results = []
    for n in sizes:
        result = run_scale_test(n, output_root)
        results.append(result)

    # Save JSON report
    report_path = Path(output_root) / "scale_test_report.json"
    with open(report_path, "w") as f:
        json.dump({
            "generated_at": datetime.utcnow().isoformat(),
            "sizes_tested": sizes,
            "results": results
        }, f, indent=2)

    # Print summary table
    print("\n" + "=" * 70)
    print(f"  {'Cases':>10} | {'Status':>12} | {'Time(s)':>8} | {'Mem(MB)':>8} | {'Edges':>10} | {'Failures':>8}")
    print("-" * 70)
    for r in results:
        print(f"  {r['n_cases']:>10,} | {r['status']:>12} | {r['elapsed_seconds']:>8.1f} | {r['peak_memory_mb']:>8.0f} | {r.get('neo4j_edges', 0):>10,} | {r['validation_failures']:>8}")
    print("=" * 70)
    print(f"\nFull report saved to: {report_path}")

    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run scale tests for the Crime Simulation Laboratory")
    parser.add_argument("--sizes", nargs="+", type=int, default=[1000, 10000, 100000], help="Case counts to test")
    parser.add_argument("--output", type=str, default="output/scale_tests", help="Base output directory")
    args = parser.parse_args()

    run_all_scale_tests(sizes=args.sizes, output_root=args.output)
