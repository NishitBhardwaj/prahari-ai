"""
CLI entry point for the Karnataka Police Crime Simulation Laboratory.
Usage:
    python cli.py generate all            # Run full pipeline
    python cli.py generate master          # Generate master data only
    python cli.py generate population      # Generate population (auto-runs master)
    python cli.py stats                    # Print DataStore stats
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import typer
from typing import Optional
from pathlib import Path
from loguru import logger

from configs.config_loader import get_config, reset_config

app = typer.Typer(
    name="crime-sim-lab",
    help="Karnataka Police Crime Simulation Laboratory — Generate production-grade synthetic crime datasets.",
    add_completion=False,
)

generate_app = typer.Typer(help="Generate datasets using simulation engines.")
app.add_typer(generate_app, name="generate")

export_app = typer.Typer(help="Export generated datasets to various formats.")
app.add_typer(export_app, name="export")


def _setup_logging(log_level: str = "INFO"):
    """Configure loguru logging."""
    logger.remove()
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{extra[engine]}</cyan> | {message}" if "engine" in logger._core.extra else "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        colorize=True,
    )
    logger.add(
        "logs/simulation_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
    )


@generate_app.command("all")
def generate_all(
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config.yaml"),
    output: str = typer.Option("output", "--output", "-o", help="Output directory"),
    log_level: str = typer.Option("INFO", "--log-level", "-l", help="Log level"),
):
    """Run the full simulation pipeline — all engines in dependency order."""
    _setup_logging(log_level)

    reset_config()
    cfg = get_config(config)

    logger.info("Starting full pipeline execution...")

    from orchestrator import Orchestrator
    orchestrator = Orchestrator(config=cfg, output_base=output)
    report = orchestrator.run_all()

    status = report["summary"]["pipeline_status"]
    if status == "SUCCESS":
        typer.echo(typer.style("\n[SUCCESS] Pipeline completed successfully!", fg=typer.colors.GREEN, bold=True))
    elif status == "PARTIAL_FAILURE":
        typer.echo(typer.style("\n[WARNING] Pipeline completed with failures.", fg=typer.colors.YELLOW, bold=True))
    else:
        typer.echo(typer.style("\n[ERROR] Pipeline failed.", fg=typer.colors.RED, bold=True))
        raise typer.Exit(code=1)


@generate_app.command("master")
def generate_master(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Generate master/lookup tables only."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("master")
    typer.echo(typer.style("[SUCCESS] Master data generated.", fg=typer.colors.GREEN))


@generate_app.command("population")
def generate_population(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Generate population (auto-runs master dependency)."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("population")
    typer.echo(typer.style("[SUCCESS] Population generated.", fg=typer.colors.GREEN))


@generate_app.command("police")
def generate_police(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Generate police personnel."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("police")
    typer.echo(typer.style("[SUCCESS] Police personnel generated.", fg=typer.colors.GREEN))


@generate_app.command("weather")
def generate_weather(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Generate weather data."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("weather")
    typer.echo(typer.style("[SUCCESS] Weather data generated.", fg=typer.colors.GREEN))


@generate_app.command("festivals")
def generate_festivals(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Generate festival calendar."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("festival")
    typer.echo(typer.style("[SUCCESS] Festival calendar generated.", fg=typer.colors.GREEN))


@generate_app.command("scenarios")
def generate_scenarios(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run scenario simulation engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("scenario")
    typer.echo(typer.style("[SUCCESS] Scenarios simulated.", fg=typer.colors.GREEN))


@generate_app.command("media")
def generate_media(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run media asset generation engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("media")
    typer.echo(typer.style("[SUCCESS] Media assets generated.", fg=typer.colors.GREEN))


@generate_app.command("crime")
def generate_crime(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run crime simulation engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("crime")
    typer.echo(typer.style("[SUCCESS] Crime cases generated.", fg=typer.colors.GREEN))


@generate_app.command("behaviour")
def generate_behaviour(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run behaviour and MO engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("behaviour")
    typer.echo(typer.style("[SUCCESS] Behaviour and MO profiles generated.", fg=typer.colors.GREEN))


@generate_app.command("gang")
def generate_gang(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run gang & syndicate engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("gang")
    typer.echo(typer.style("[SUCCESS] Gangs and syndicates generated.", fg=typer.colors.GREEN))


@generate_app.command("investigation")
def generate_investigation(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run investigation lifecycle engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("investigation")
    typer.echo(typer.style("[SUCCESS] Case investigations generated.", fg=typer.colors.GREEN))


@generate_app.command("narrative")
def generate_narrative(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run narrative consistency engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("narrative")
    typer.echo(typer.style("[SUCCESS] Consistent narratives generated.", fg=typer.colors.GREEN))


@generate_app.command("evidence")
def generate_evidence(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run evidence & forensics engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("evidence")
    typer.echo(typer.style("[SUCCESS] Evidence and forensics generated.", fg=typer.colors.GREEN))


@generate_app.command("communication")
def generate_communication(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run communication (CDR) engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("communication")
    typer.echo(typer.style("[SUCCESS] CDRs and device links generated.", fg=typer.colors.GREEN))


@generate_app.command("financial")
def generate_financial(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run financial transaction engine."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("financial")
    typer.echo(typer.style("[SUCCESS] Financial transactions generated.", fg=typer.colors.GREEN))


@generate_app.command("export")
def generate_export(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run export engine (must run after others)."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)
    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    orch.run_engine("export")
    typer.echo(typer.style("[SUCCESS] Dataset exported successfully.", fg=typer.colors.GREEN))


@app.command("stats")
def stats(
    output: str = typer.Option("output", "--output", "-o"),
):
    """Print generation statistics from the last run."""
    report_path = Path(output) / "reports" / "generation_report.json"
    if not report_path.exists():
        typer.echo(typer.style("No generation report found. Run 'generate all' first.", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    import json
    with open(report_path, "r") as f:
        report = json.load(f)

    typer.echo(typer.style("\n[STATS] Generation Statistics", fg=typer.colors.CYAN, bold=True))
    typer.echo(f"  Status:   {report['summary']['pipeline_status']}")
    typer.echo(f"  Duration: {report['summary']['total_duration_seconds']}s")
    typer.echo(f"  Records:  {report['summary']['total_records_generated']}")
    typer.echo(f"  Tables:   {report['summary']['total_tables_generated']}")
    typer.echo(f"  Seed:     {report['metadata']['seed']}")
    typer.echo(f"  Version:  {report['metadata']['version']}")
    typer.echo("")

    if "datastore_summary" in report:
        typer.echo(typer.style("  Tables:", bold=True))
        for table, count in report["datastore_summary"].items():
            typer.echo(f"    {table}: {count:,}")


@app.command("benchmark")
def benchmark(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
    output: str = typer.Option("output", "--output", "-o"),
):
    """Run a benchmark of the generation pipeline."""
    _setup_logging()
    reset_config()
    cfg = get_config(config)

    import time
    typer.echo("Running benchmark...")
    start = time.time()

    from orchestrator import Orchestrator
    orch = Orchestrator(config=cfg, output_base=output)
    report = orch.run_all()

    elapsed = time.time() - start
    records = report["summary"]["total_records_generated"]
    rate = records / elapsed if elapsed > 0 else 0

    typer.echo(typer.style(f"\n[BENCHMARK] Results", fg=typer.colors.CYAN, bold=True))
    typer.echo(f"  Total time:  {elapsed:.2f}s")
    typer.echo(f"  Records:     {records:,}")
    typer.echo(f"  Throughput:  {rate:,.0f} records/second")


validate_app = typer.Typer(help="Run validation checks on generated output.")
app.add_typer(validate_app, name="validate")


@validate_app.command("integrity")
def validate_integrity(
    output: str = typer.Option("output", "--output", "-o", help="Output directory to audit"),
):
    """Run the Data Integrity Audit: FK checks, chronology, graph, narratives, media, parquet schemas."""
    _setup_logging()
    from validation.integrity_audit import DataIntegrityAuditor
    auditor = DataIntegrityAuditor(output_dir=output)
    report = auditor.run()
    status = report.get("overall_status", "UNKNOWN")
    color = typer.colors.GREEN if status == "PASS" else typer.colors.RED
    typer.echo(typer.style(f"\n[INTEGRITY] Status: {status}", fg=color, bold=True))
    typer.echo(f"  Passed: {report['total_checks_passed']}  Failed: {report['total_checks_failed']}")
    typer.echo(f"  Report: {output}/reports/integrity_report.md")


@validate_app.command("dashboard")
def validate_dashboard(
    output: str = typer.Option("output", "--output", "-o", help="Output directory to audit"),
):
    """Run the Dashboard Readiness Audit: checks every visualization panel has required data."""
    _setup_logging()
    from validation.dashboard_audit import DashboardReadinessAuditor
    auditor = DashboardReadinessAuditor(output_dir=output)
    report = auditor.run()
    score = report.get("summary", {}).get("readiness_score", "?")
    typer.echo(typer.style(f"\n[DASHBOARD] Readiness Score: {score}", fg=typer.colors.CYAN, bold=True))
    typer.echo(f"  Report: {output}/reports/dashboard_readiness_report.md")


@validate_app.command("scale")
def validate_scale(
    sizes: str = typer.Option("1000,10000", "--sizes", "-s", help="Comma-separated case counts"),
    output: str = typer.Option("output/scale_tests", "--output", "-o", help="Output directory"),
):
    """Run Scale Tests at multiple dataset sizes and record performance metrics."""
    _setup_logging()
    size_list = [int(x.strip()) for x in sizes.split(",")]
    from validation.scale_test import run_all_scale_tests
    run_all_scale_tests(sizes=size_list, output_root=output)
    typer.echo(typer.style("\n[SCALE] Scale tests complete.", fg=typer.colors.GREEN, bold=True))
    typer.echo(f"  Report: {output}/scale_test_report.json")


@validate_app.command("all")
def validate_all(
    output: str = typer.Option("output", "--output", "-o", help="Output directory"),
    skip_scale: bool = typer.Option(False, "--skip-scale", help="Skip scale tests"),
    scale_sizes: str = typer.Option("1000,10000", "--scale-sizes", help="Comma-separated case counts for scale test"),
):
    """Run the full validation suite: Scale Test + Integrity Audit + Dashboard Readiness."""
    _setup_logging()
    sizes = [int(x.strip()) for x in scale_sizes.split(",")]

    typer.echo(typer.style("\n[VALIDATION] Starting full validation suite...", fg=typer.colors.CYAN, bold=True))

    import sys
    from pathlib import Path
    old_args = sys.argv
    sys.argv = [sys.argv[0], "--output", output]
    if skip_scale:
        sys.argv.append("--skip-scale")

    from validation.run_all import main as run_main
    try:
        run_main()
    except SystemExit as e:
        if e.code and e.code != 0:
            typer.echo(typer.style("\n[FAIL] Validation suite completed with failures.", fg=typer.colors.RED, bold=True))
        else:
            typer.echo(typer.style("\n[PASS] Validation suite completed successfully.", fg=typer.colors.GREEN, bold=True))
    finally:
        sys.argv = old_args


if __name__ == "__main__":
    app()

