import os
import argparse

try:
    from .watcher import watch_log
    from .parser import FAIL_PATTERNS
except ImportError:
    from watcher import watch_log  # type: ignore
    from parser import FAIL_PATTERNS  # type: ignore


def main():
    parser = argparse.ArgumentParser(
        description="Monitor and parse log files for test results."
    )
    parser.add_argument("logfile", help="Path to the log file to be monitored.")
    parser.add_argument(
        "--patterns", help="Comma-separated list of custom failure patterns."
    )
    parser.add_argument("--json", action="store_true", help="Enable JSON output.")
    args = parser.parse_args()

    if not os.path.exists(args.logfile):
        print(f"Error: File not found at '{args.logfile}'")
        return

    custom_patterns = args.patterns.split(",") if args.patterns else FAIL_PATTERNS

    watch_log(args.logfile, custom_patterns, args.json)


if __name__ == "__main__":
    main()
