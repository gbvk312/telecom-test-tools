"""
Pipeline engine for the Telecom Test Toolkit.

Chains tools together in sequence:
  logs → testwatch → log_analyzer → testscope → flakiness_scorer → report_gen

Each stage reads from the shared PipelineOutput and appends its results.
"""

import glob
import json
import logging
import os
from datetime import datetime
from typing import List, Optional

from rich.logging import RichHandler

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)
logger = logging.getLogger("ttt.pipeline")

from ttt.config import TTTConfig, load_config
from ttt.models import AnalysisResult, PipelineOutput
from ttt.registry import ToolRegistry


def discover_log_files(log_directory: str) -> List[str]:
    """Find all log/txt files in the given directory."""
    patterns = ["*.log", "*.txt"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(log_directory, pattern)))
    return sorted(set(files))


def run_tool(tool_name: str, log_files: List[str]) -> AnalysisResult:
    """Run an analysis tool securely via the registry."""
    try:
        tool_func = ToolRegistry.get_tool(tool_name)

        # Testwatch runs on all files and aggregates
        if tool_name == "testwatch":
            all_results = []
            for log_file in log_files:
                results = tool_func(log_file)
                all_results.extend(results)

            passed = sum(1 for r in all_results if r.status == "pass")
            failed = sum(1 for r in all_results if r.status == "fail")
            total = len(all_results)
            success_rate = round((passed / total * 100), 2) if total > 0 else 0.0

            return AnalysisResult(
                tool_name=tool_name,
                total_events=total,
                passed=passed,
                failed=failed,
                success_rate=success_rate,
                results=all_results,
            )

        # Other analyzers run on the first relevant file
        for log_file in log_files:
            result = tool_func(log_file)
            if result.total_events > 0:
                return result

        return AnalysisResult(tool_name=tool_name, raw_summary="No relevant logs found")

    except ImportError as e:
        logger.error(f"{tool_name} is not installed or available: {e}")
        return AnalysisResult(
            tool_name=tool_name, raw_summary=f"Missing Dependency: {e}"
        )
    except Exception as e:
        logger.error(f"{tool_name} failed unexpectedly: {e}")
        return AnalysisResult(tool_name=tool_name, raw_summary=f"Error: {e}")


def run_report_gen(pipeline_output: PipelineOutput, output_dir: str) -> str:
    """Stage 4: Generate HTML report from pipeline data."""
    try:
        from tools.report_gen.api import generate

        report_path = os.path.join(output_dir, "report.html")
        generate(pipeline_output, report_path)
        return report_path
    except Exception as e:
        logger.error(f"report_gen failed: {e}")
        return ""


def save_pipeline_output(pipeline_output: PipelineOutput, output_dir: str) -> str:
    """Save pipeline output as JSON for dashboard consumption."""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "pipeline_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(pipeline_output.to_dict(), f, indent=2, default=str)
    return output_path


def run_pipeline(
    log_directory: Optional[str] = None,
    output_directory: Optional[str] = None,
    config: Optional[TTTConfig] = None,
) -> PipelineOutput:
    """Run the complete analysis pipeline.

    Args:
        log_directory: Directory containing log files to analyze.
        output_directory: Directory to write results and reports.
        config: Pipeline configuration. Loaded from ttt.config.yaml if not provided.

    Returns:
        PipelineOutput with all analysis results aggregated.
    """
    if config is None:
        config = load_config()

    log_dir = log_directory or config.log_directory
    out_dir = output_directory or config.output_directory

    os.makedirs(out_dir, exist_ok=True)

    # Create pipeline output
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    pipeline_output = PipelineOutput(
        run_id=run_id,
        timestamp=datetime.now().isoformat(),
    )

    # Discover log files
    log_files = discover_log_files(log_dir)
    pipeline_output.log_files = log_files

    if not log_files:
        logger.warning(f"No log files found in {log_dir}")
        return pipeline_output

    logger.info(f"📁 Found {len(log_files)} log file(s) in {log_dir}")

    enabled = config.enabled_tools

    # Stage 1: TestWatch (quick triage)
    if "testwatch" in enabled:
        logger.info("🔍 Stage 1: Running testwatch...")
        result = run_tool("testwatch", log_files)
        pipeline_output.analyses.append(result)
        logger.info(
            f"   → {result.total_events} events ({result.passed} pass, {result.failed} fail)"
        )

    # Stage 2a: Log Analyzer (protocol analysis)
    if "log_analyzer" in enabled:
        logger.info("📡 Stage 2a: Running log_analyzer...")
        result = run_tool("log_analyzer", log_files)
        pipeline_output.analyses.append(result)
        logger.info(
            f"   → {result.total_events} events, {result.success_rate}% success rate"
        )

    # Stage 2b: TestScope (KPI engine)
    if "testscope" in enabled:
        logger.info("🔬 Stage 2b: Running testscope...")
        result = run_tool("testscope", log_files)
        pipeline_output.analyses.append(result)
        logger.info(f"   → {result.total_events} events, {len(result.issues)} issues")

    # Stage 4: Report Generation
    if "report_gen" in enabled:
        logger.info("📑 Stage 4: Generating HTML report...")
        report_path = run_report_gen(pipeline_output, out_dir)
        pipeline_output.report_path = report_path
        if report_path:
            logger.info(f"   → Report saved to {report_path}")

    # Save pipeline output as JSON
    json_path = save_pipeline_output(pipeline_output, out_dir)
    logger.info(f"💾 Pipeline output saved to {json_path}")

    return pipeline_output
