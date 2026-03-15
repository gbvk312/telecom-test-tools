"""
Unified CLI for the Telecom Test Toolkit.

Provides a single entry point for all ecosystem tools:
  ttt pipeline run --logs <dir> --output <dir>
  ttt analyze --tool <name> --input <file>
  ttt dashboard
  ttt version
"""

import os
import sys
import click

from ttt import __version__
from ttt.config import load_config


@click.group()
@click.version_option(version=__version__, prog_name="ttt")
def cli():
    """🚀 Telecom Test Toolkit — Unified CLI for telecom test analysis."""
    pass


@cli.group()
def pipeline():
    """Run the analysis pipeline on log files."""
    pass


@pipeline.command("run")
@click.option(
    "--logs", "-l", default=None, help="Directory containing log files to analyze."
)
@click.option(
    "--output", "-o", default=None, help="Directory for output results and reports."
)
@click.option("--config", "-c", default=None, help="Path to ttt.config.yaml.")
def pipeline_run(logs, output, config):
    """Run the full analysis pipeline: logs → analyze → score → report."""
    from ttt.pipeline import run_pipeline

    cfg = load_config(config)

    print("🚀 Telecom Test Toolkit — Pipeline Run")
    print("=" * 50)

    result = run_pipeline(
        log_directory=logs,
        output_directory=output,
        config=cfg,
    )

    print("=" * 50)
    print(f"✅ Pipeline complete! Run ID: {result.run_id}")
    print(f"   Analyses run: {len(result.analyses)}")
    if result.report_path:
        print(f"   Report: {result.report_path}")


@cli.command()
@click.option(
    "--tool",
    "-t",
    required=True,
    type=click.Choice(["testwatch", "log_analyzer", "testscope"]),
    help="Which analysis tool to run.",
)
@click.option("--input", "-i", "input_file", required=True, help="Path to log file.")
@click.option("--json-output", is_flag=True, help="Output results as JSON.")
def analyze(tool, input_file, json_output):
    """Run a single analysis tool on a log file."""
    import json as json_lib

    if not os.path.isfile(input_file):
        click.echo(f"Error: File not found: {input_file}", err=True)
        sys.exit(1)

    if tool == "testwatch":
        from tools.testwatch.api import scan

        results = scan(input_file)
        if json_output:
            click.echo(json_lib.dumps([r.to_dict() for r in results], indent=2))
        else:
            passed = sum(1 for r in results if r.status == "pass")
            failed = sum(1 for r in results if r.status == "fail")
            for r in results:
                icon = "✔" if r.status == "pass" else "❌"
                click.echo(f"{icon} {r.test_id}")
            click.echo(f"\nSummary: {passed} passed, {failed} failed")

    elif tool == "log_analyzer":
        from tools.log_analyzer.api import analyze as run_analyze

        result = run_analyze(input_file)
        if json_output:
            click.echo(json_lib.dumps(result.to_dict(), indent=2))
        else:
            click.echo(
                f"Attach Success Rate: {result.kpis.get('attach_success_rate', 0)}%"
            )
            click.echo(f"RRC Failures: {result.kpis.get('rrc_failures', 0)}")
            click.echo(f"Setup Failures: {result.kpis.get('setup_failures', 0)}")

    elif tool == "testscope":
        from tools.testscope.api import analyze as run_analyze

        result = run_analyze(input_file)
        if json_output:
            click.echo(json_lib.dumps(result.to_dict(), indent=2))
        else:
            click.echo(f"Total Events: {result.total_events}")
            click.echo(f"Failures: {result.failed}")
            click.echo(f"Success Rate: {result.success_rate}%")
            if result.issues:
                click.echo("Issues:")
                for issue in result.issues:
                    click.echo(f"  ❌ {issue}")


@cli.command()
@click.option("--port", "-p", default=8501, help="Port for the Streamlit dashboard.")
@click.option(
    "--data-dir", "-d", default=None, help="Directory with pipeline output JSON."
)
def dashboard(port, data_dir):
    """Launch the Test Monitor Dashboard."""
    dashboard_app = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "tools", "dashboard", "app.py"
    )

    if not os.path.isfile(dashboard_app):
        click.echo(f"Error: Dashboard app not found at {dashboard_app}", err=True)
        sys.exit(1)

    cmd = f"streamlit run {dashboard_app} --server.port {port}"
    if data_dir:
        cmd += f" -- --data-dir {data_dir}"

    click.echo(f"🖥️  Launching dashboard on port {port}...")
    os.system(cmd)


@cli.command()
def version():
    """Show the TTT version."""
    click.echo(f"Telecom Test Toolkit v{__version__}")


def main():
    cli()


if __name__ == "__main__":
    main()
