"""
5G Log Analyzer API — Programmatic interface for the log analyzer tool.

Returns structured AnalysisResult instead of printing to stdout.
"""

import re
from typing import Optional

from ttt.models import AnalysisResult, TestResult


# Regex rules for 3GPP protocol event detection
RULES = {
    'ATTACH_REQUEST': re.compile(r'ATTACH_REQUEST|Attach Request'),
    'ATTACH_ACCEPT': re.compile(r'ATTACH_ACCEPT|Attach Accept'),
    'ATTACH_REJECT': re.compile(r'ATTACH_REJECT|Attach Reject'),
    'RRC_REJECT': re.compile(r'RRC_REJECT|RRC Reject|RRCConnectionReject'),
    'SETUP_FAILURE': re.compile(r'SETUP_FAILURE|Setup Failure'),
}


def analyze(log_file: str) -> AnalysisResult:
    """Analyze a gNodeB log file for protocol events.

    Args:
        log_file: Path to the gNodeB log file.

    Returns:
        AnalysisResult with protocol-level KPIs and individual test results.
    """
    stats = {
        'attach_attempts': 0,
        'attach_successes': 0,
        'attach_failures': 0,
        'rrc_failures': 0,
        'setup_failures': 0,
    }

    results = []

    with open(log_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue

            event_type = None
            status = "pass"

            if RULES['ATTACH_REQUEST'].search(stripped):
                stats['attach_attempts'] += 1
                event_type = "ATTACH_REQUEST"
            elif RULES['ATTACH_ACCEPT'].search(stripped):
                stats['attach_successes'] += 1
                event_type = "ATTACH_ACCEPT"
            elif RULES['ATTACH_REJECT'].search(stripped):
                stats['attach_failures'] += 1
                event_type = "ATTACH_REJECT"
                status = "fail"
            elif RULES['RRC_REJECT'].search(stripped):
                stats['rrc_failures'] += 1
                event_type = "RRC_REJECT"
                status = "fail"
            elif RULES['SETUP_FAILURE'].search(stripped):
                stats['setup_failures'] += 1
                event_type = "SETUP_FAILURE"
                status = "fail"

            if event_type:
                results.append(TestResult(
                    test_id=f"{event_type}_{i}",
                    status=status,
                    source_tool="log_analyzer",
                    message=stripped,
                    metadata={"event_type": event_type, "line_number": i},
                ))

    # Calculate KPIs
    success_rate = 0.0
    if stats['attach_attempts'] > 0:
        success_rate = round((stats['attach_successes'] / stats['attach_attempts']) * 100, 2)

    total_events = len(results)
    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")

    return AnalysisResult(
        tool_name="log_analyzer",
        total_events=total_events,
        passed=passed,
        failed=failed,
        success_rate=success_rate,
        results=results,
        kpis={
            "attach_attempts": stats['attach_attempts'],
            "attach_successes": stats['attach_successes'],
            "attach_failures": stats['attach_failures'],
            "attach_success_rate": success_rate,
            "rrc_failures": stats['rrc_failures'],
            "setup_failures": stats['setup_failures'],
        },
        issues=[
            f"RRC Failures: {stats['rrc_failures']}" for _ in [1] if stats['rrc_failures'] > 0
        ] + [
            f"Setup Failures: {stats['setup_failures']}" for _ in [1] if stats['setup_failures'] > 0
        ] + [
            f"Attach Rejections: {stats['attach_failures']}" for _ in [1] if stats['attach_failures'] > 0
        ],
    )
