"""
Pipeline engine for the Telecom Test Toolkit.

Chains tools together in sequence:
  logs → testwatch → log_analyzer → testscope → flakiness_scorer → report_gen

Each stage reads from the shared PipelineOutput and appends its results.
"""

import os
import json
import glob
from datetime import datetime
from typing import List, Optional

from ttt.models import PipelineOutput, AnalysisResult, TestResult
from ttt.config import TTTConfig, load_config


def discover_log_files(log_directory: str) -> List[str]:
    """Find all log/txt files in the given directory."""
    patterns = ["*.log", "*.txt"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(log_directory, pattern)))
    return sorted(set(files))


def run_testwatch(log_files: List[str]) -> AnalysisResult:
    """Stage 1: Quick triage scan using testwatch."""
    try:
        from tools.testwatch.api import scan
        all_results = []
        for log_file in log_files:
            results = scan(log_file)
            all_results.extend(results)

        passed = sum(1 for r in all_results if r.status == "pass")
        failed = sum(1 for r in all_results if r.status == "fail")
        total = len(all_results)

        return AnalysisResult(
            tool_name="testwatch",
            total_events=total,
            passed=passed,
            failed=failed,
            success_rate=round((passed / total * 100), 2) if total > 0 else 0.0,
            results=all_results,
        )
    except Exception as e:
        print(f"  ⚠ testwatch failed: {e}")
        return AnalysisResult(tool_name="testwatch", raw_summary=f"Error: {e}")


def run_log_analyzer(log_files: List[str]) -> AnalysisResult:
    """Stage 2a: Protocol-level analysis using 5g-log-analyzer."""
    try:
        from tools.log_analyzer.api import analyze
        # Use first log file that looks like a gNodeB log
        for log_file in log_files:
            result = analyze(log_file)
            if result.total_events > 0:
                return result
        return AnalysisResult(tool_name="log_analyzer", raw_summary="No relevant logs found")
    except Exception as e:
        print(f"  ⚠ log_analyzer failed: {e}")
        return AnalysisResult(tool_name="log_analyzer", raw_summary=f"Error: {e}")


def run_testscope(log_files: List[str]) -> AnalysisResult:
    """Stage 2b: KPI & failure intelligence using 5gtestscope."""
    try:
        from tools.testscope.api import analyze
        for log_file in log_files:
            result = analyze(log_file)
            if result.total_events > 0:
                return result
        return AnalysisResult(tool_name="testscope", raw_summary="No relevant logs found")
    except Exception as e:
        print(f"  ⚠ testscope failed: {e}")
        return AnalysisResult(tool_name="testscope", raw_summary=f"Error: {e}")


def run_report_gen(pipeline_output: PipelineOutput, output_dir: str) -> str:
    """Stage 4: Generate HTML report from pipeline data."""
    try:
        from tools.report_gen.api import generate
        report_path = os.path.join(output_dir, "report.html")
        generate(pipeline_output, report_path)
        return report_path
    except Exception as e:
        print(f"  ⚠ report_gen failed: {e}")
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
        print(f"  ⚠ No log files found in {log_dir}")
        return pipeline_output

    print(f"  📁 Found {len(log_files)} log file(s) in {log_dir}")

    enabled = config.enabled_tools

    # Stage 1: TestWatch (quick triage)
    if "testwatch" in enabled:
        print("  🔍 Stage 1: Running testwatch...")
        result = run_testwatch(log_files)
        pipeline_output.analyses.append(result)
        print(f"     → {result.total_events} events ({result.passed} pass, {result.failed} fail)")

    # Stage 2a: Log Analyzer (protocol analysis)
    if "log_analyzer" in enabled:
        print("  📡 Stage 2a: Running log_analyzer...")
        result = run_log_analyzer(log_files)
        pipeline_output.analyses.append(result)
        print(f"     → {result.total_events} events, {result.success_rate}% success rate")

    # Stage 2b: TestScope (KPI engine)
    if "testscope" in enabled:
        print("  🔬 Stage 2b: Running testscope...")
        result = run_testscope(log_files)
        pipeline_output.analyses.append(result)
        print(f"     → {result.total_events} events, {len(result.issues)} issues")

    # Stage 4: Report Generation
    if "report_gen" in enabled:
        print("  📑 Stage 4: Generating HTML report...")
        report_path = run_report_gen(pipeline_output, out_dir)
        pipeline_output.report_path = report_path
        if report_path:
            print(f"     → Report saved to {report_path}")

    # Save pipeline output as JSON
    json_path = save_pipeline_output(pipeline_output, out_dir)
    print(f"  💾 Pipeline output saved to {json_path}")

    return pipeline_output
