"""
TestWatch API — Programmatic interface for the testwatch tool.

Returns structured TestResult objects instead of printing to stdout.
"""

import os
from typing import List, Optional

from ttt.models import TestResult

# Add the testwatch directory to path for imports
_tool_dir = os.path.dirname(__file__)

FAIL_PATTERNS = ["FAIL", "FAILED", "ERROR", "CRASH", "TIMEOUT"]


def _parse_line(line: str, patterns: Optional[List[str]] = None) -> str:
    """Check if a line matches any failure pattern."""
    import re

    if patterns is None:
        patterns = FAIL_PATTERNS
    for pattern in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return "FAIL"
    return "PASS"


def scan(log_file: str, patterns: Optional[List[str]] = None) -> List[TestResult]:
    """Scan a log file and return structured TestResult objects.

    Args:
        log_file: Path to the log file to scan.
        patterns: Optional custom failure patterns. Defaults to FAIL_PATTERNS.

    Returns:
        List of TestResult, one per line in the log file.
    """
    if patterns is None:
        patterns = FAIL_PATTERNS

    results = []
    with open(log_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue

            status_raw = _parse_line(stripped, patterns)
            status = "pass" if status_raw == "PASS" else "fail"

            results.append(
                TestResult(
                    test_id=stripped,
                    status=status,
                    source_tool="testwatch",
                    message=stripped,
                    metadata={
                        "line_number": i,
                        "source_file": os.path.basename(log_file),
                    },
                )
            )

    return results
