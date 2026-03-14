"""
5G Test Scope API — Programmatic interface for the testscope tool.

Returns structured AnalysisResult with KPIs and detected failures.
"""

import re
from typing import List

from ttt.models import AnalysisResult, TestResult


def _parse_log(file_path: str) -> List[str]:
    """Parse a 5G log file and extract events."""
    events = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if "RRC Setup" in stripped:
                events.append("RRC_SETUP")
            elif "Registration Accept" in stripped:
                events.append("REGISTRATION_SUCCESS")
            elif "PDU Session" in stripped:
                events.append("PDU_SESSION")
            elif "FAIL" in stripped or "ERROR" in stripped:
                events.append("FAILURE")
            elif stripped:
                events.append("OTHER")
    return events


def _detect_failures(events: List[str]) -> List[str]:
    """Detect failures from the event list."""
    failures = []
    for event in events:
        if event == "FAILURE":
            failures.append("Generic Failure Detected")
    return failures


def _calculate_kpis(events: List[str]) -> dict:
    """Calculate key performance indicators."""
    # Filter out OTHER events for KPI calculation
    relevant_events = [e for e in events if e != "OTHER"]
    total = len(relevant_events)
    failures = relevant_events.count("FAILURE")
    success_rate = round(((total - failures) / total) * 100, 2) if total > 0 else 0.0

    return {
        "total_events": total,
        "failures": failures,
        "success_rate": success_rate,
        "rrc_setups": relevant_events.count("RRC_SETUP"),
        "registrations": relevant_events.count("REGISTRATION_SUCCESS"),
        "pdu_sessions": relevant_events.count("PDU_SESSION"),
    }


def analyze(log_file: str) -> AnalysisResult:
    """Analyze a 5G log file for KPIs and failures.

    Args:
        log_file: Path to the 5G log file.

    Returns:
        AnalysisResult with KPIs, failure detection, and individual results.
    """
    events = _parse_log(log_file)
    failures = _detect_failures(events)
    kpis = _calculate_kpis(events)

    # Build individual test results
    results = []
    for i, event in enumerate(events, 1):
        if event == "OTHER":
            continue
        status = "fail" if event == "FAILURE" else "pass"
        results.append(TestResult(
            test_id=f"{event}_{i}",
            status=status,
            source_tool="testscope",
            message=event,
            metadata={"event_type": event, "sequence": i},
        ))

    total = kpis["total_events"]
    failed = kpis["failures"]
    passed = total - failed

    return AnalysisResult(
        tool_name="testscope",
        total_events=total,
        passed=passed,
        failed=failed,
        success_rate=kpis["success_rate"],
        results=results,
        kpis=kpis,
        issues=failures,
    )
