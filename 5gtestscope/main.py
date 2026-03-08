import sys

from parser.log_parser import parse_log
from analyzer.failure_detector import detect_failures
from reports.report import print_report
from analyzer.failure_detector import detect_failures
from analyzer.failure_detector import detect_failures

from analyzer.failure_detector import detect_failures
from analyzer.failure_detector import detect_failures

from analyzer.failure_detector import detect_failures

def calculate_kpis(events):

    total = len(events)
    failures = events.count("FAILURE")

    success_rate = ((total - failures) / total) * 100

    return {
        "total_events": total,
        "failures": failures,
        "success_rate": round(success_rate, 2)
    }


def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py <logfile>")
        return

    logfile = sys.argv[1]

    events = parse_log(logfile)

    failures = detect_failures(events)

    kpis = calculate_kpis(events)

    print_report(kpis, failures)


if __name__ == "__main__":
    main()