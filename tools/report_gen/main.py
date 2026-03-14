import argparse
import sys
import os

from src.parsers import get_parser
from src.generator import generate_report

def main():
    parser = argparse.ArgumentParser(description="Generate HTML Test Reports from various log formats.")
    parser.add_argument("--pytest-logs", type=str, help="Path to pytest log file")
    parser.add_argument("--automation-logs", type=str, help="Path to generic automation log file")
    parser.add_argument("--network-logs", type=str, help="Path to network test log file")
    parser.add_argument("--output", type=str, default="report.html", help="Path for output HTML report")
    
    args = parser.parse_args()

    # Collect data from all provided logs
    combined_data = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }

    files_processed = 0

    if args.pytest_logs:
        result = _process_log(args.pytest_logs, "pytest")
        _merge_results(combined_data, result)
        files_processed += 1
        
    if args.automation_logs:
        result = _process_log(args.automation_logs, "automation")
        _merge_results(combined_data, result)
        files_processed += 1

    if args.network_logs:
        result = _process_log(args.network_logs, "network")
        _merge_results(combined_data, result)
        files_processed += 1

    if files_processed == 0:
        print("Error: Please provide at least one log file (--pytest-logs, --automation-logs, or --network-logs).")
        parser.print_help()
        sys.exit(1)

    print(f"Total Tests Found: {combined_data['total']} (Passed: {combined_data['passed']}, Failed: {combined_data['failed']})")
    print("Generating report...")
    
    generate_report(combined_data, args.output)


def _process_log(filepath: str, log_type: str) -> dict:
    if not os.path.exists(filepath):
        print(f"Warning: File not found {filepath}")
        return {"total": 0, "passed": 0, "failed": 0, "details": []}
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return {"total": 0, "passed": 0, "failed": 0, "details": []}
        
    parser = get_parser(log_type)
    return parser.parse(content)

def _merge_results(main_dict: dict, new_dict: dict):
    main_dict["total"] += new_dict.get("total", 0)
    main_dict["passed"] += new_dict.get("passed", 0)
    main_dict["failed"] += new_dict.get("failed", 0)
    main_dict["details"].extend(new_dict.get("details", []))


if __name__ == "__main__":
    main()
