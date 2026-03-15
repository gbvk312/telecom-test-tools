import re
import sys
import argparse


def analyze_logs(log_file_path: str) -> None:
    """Parses gNodeB logs and detects attach/RRC failures."""

    # Counters
    stats = {
        "attach_attempts": 0,
        "attach_successes": 0,
        "attach_failures": 0,
        "rrc_failures": 0,
        "setup_failures": 0,
    }

    # Simple regex rules defining events
    # In a real scenario, these would match specific 3GPP messages in the log
    rules = {
        "ATTACH_REQUEST": re.compile(r"ATTACH_REQUEST|Attach Request"),
        "ATTACH_ACCEPT": re.compile(r"ATTACH_ACCEPT|Attach Accept"),
        "ATTACH_REJECT": re.compile(r"ATTACH_REJECT|Attach Reject"),
        "RRC_REJECT": re.compile(r"RRC_REJECT|RRC Reject|RRCConnectionReject"),
        "SETUP_FAILURE": re.compile(r"SETUP_FAILURE|Setup Failure"),
    }

    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Attach flow
                if rules["ATTACH_REQUEST"].search(line):
                    stats["attach_attempts"] += 1
                elif rules["ATTACH_ACCEPT"].search(line):
                    stats["attach_successes"] += 1
                elif rules["ATTACH_REJECT"].search(line):
                    stats["attach_failures"] += 1

                # RRC / Setup failures
                elif rules["RRC_REJECT"].search(line):
                    stats["rrc_failures"] += 1
                elif rules["SETUP_FAILURE"].search(line):
                    stats["setup_failures"] += 1

    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    # Calculate metrics
    success_rate = 0.0
    if stats["attach_attempts"] > 0:
        # Assuming attach_successes correspond to attempts for simplicity.
        # In a stateful parser, we'd track per UE ID.
        success_rate = (stats["attach_successes"] / stats["attach_attempts"]) * 100

    # Example Output matching README
    # Attach Success Rate: 98%
    # RRC Failures: 2
    # Setup Failures: 1
    print("Test Summary:")
    print(f"  Attach Success Rate: {success_rate:.0f}%")
    print(f"  RRC Failures: {stats['rrc_failures']}")
    print(f"  Setup Failures: {stats['setup_failures']}")

    # Additional helpful info
    print("\nDetailed Stats:")
    print(f"  Total Attach Attempts: {stats['attach_attempts']}")
    print(f"  Total Attach Successes: {stats['attach_successes']}")
    print(f"  Total Attach Rejects: {stats['attach_failures']}")


def main():
    parser = argparse.ArgumentParser(description="5G gNodeB Log Analyzer")
    parser.add_argument("log_file", help="Path to the gNodeB log file to analyze")
    args = parser.parse_args()

    analyze_logs(args.log_file)


if __name__ == "__main__":
    main()
