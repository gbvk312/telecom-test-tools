import re
from typing import Dict, Any


class BaseParser:
    def parse(self, content: str) -> Dict[str, Any]:
        """
        Parses log content and returns a standardized dictionary:
        {
            "total": int,
            "passed": int,
            "failed": int,
            "details": [{"name": str, "status": str, "duration": str, "message": str}]
        }
        """
        raise NotImplementedError("Each parser must implement parse()")


class PytestParser(BaseParser):
    def parse(self, content: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # very basic pytest parsing
        # Ex: test_main.py::test_something PASSED [ 50%]
        # Ex: test_main.py::test_fail FAILED [100%]

        passed_pattern = re.compile(r"^(.*::.*?)\s+PASSED", re.MULTILINE)
        failed_pattern = re.compile(r"^(.*::.*?)\s+FAILED", re.MULTILINE)

        passed_tests = passed_pattern.findall(content)
        failed_tests = failed_pattern.findall(content)

        for p in passed_tests:
            result["details"].append(
                {"name": p.strip(), "status": "passed", "duration": "-", "message": ""}
            )
            result["passed"] += 1
            result["total"] += 1

        for f in failed_tests:
            result["details"].append(
                {
                    "name": f.strip(),
                    "status": "failed",
                    "duration": "-",
                    "message": "Test failed.",
                }
            )
            result["failed"] += 1
            result["total"] += 1

        return result


class AutomationLogParser(BaseParser):
    def parse(self, content: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # matching general automation logs like "[PASS] test_login"
        pass_pattern = re.compile(r"\[(?:PASS|SUCCESS)\]\s+(.*)", re.IGNORECASE)
        fail_pattern = re.compile(r"\[(?:FAIL|ERROR)\]\s+(.*)", re.IGNORECASE)

        for match in pass_pattern.finditer(content):
            result["details"].append(
                {
                    "name": match.group(1).strip(),
                    "status": "passed",
                    "duration": "-",
                    "message": "",
                }
            )
            result["passed"] += 1
            result["total"] += 1

        for match in fail_pattern.finditer(content):
            result["details"].append(
                {
                    "name": match.group(1).strip(),
                    "status": "failed",
                    "duration": "-",
                    "message": "Failure in automation log",
                }
            )
            result["failed"] += 1
            result["total"] += 1

        return result


class NetworkLogParser(BaseParser):
    def parse(self, content: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {"total": 0, "passed": 0, "failed": 0, "details": []}

        # e.g Ping to 192.168.1.1 successful
        # e.g Timeout connecting to 10.0.0.5

        success_pattern = re.compile(r"(.*successful.*)", re.IGNORECASE)
        error_pattern = re.compile(
            r"(.*timeout.*|.*error.*|.*unreachable.*)", re.IGNORECASE
        )

        for lines in content.splitlines():
            line = lines.strip()
            if not line:
                continue

            if success_pattern.search(line):
                result["details"].append(
                    {
                        "name": "Network Test",
                        "status": "passed",
                        "duration": "-",
                        "message": line,
                    }
                )
                result["passed"] += 1
                result["total"] += 1
            elif error_pattern.search(line):
                result["details"].append(
                    {
                        "name": "Network Test",
                        "status": "failed",
                        "duration": "-",
                        "message": line,
                    }
                )
                result["failed"] += 1
                result["total"] += 1

        return result


def get_parser(log_type: str) -> BaseParser:
    log_type = log_type.lower()
    if log_type == "pytest":
        return PytestParser()
    elif log_type == "automation":
        return AutomationLogParser()
    elif log_type == "network":
        return NetworkLogParser()
    else:
        raise ValueError(f"Unknown log type: {log_type}")
