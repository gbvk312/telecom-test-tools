import re

FAIL_PATTERNS = [
    "FAIL",
    "FAILED",
    "ERROR",
    "CRASH",
    "TIMEOUT"
]

def parse_line(line, patterns):
    for pattern in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return "FAIL"
    return "PASS"