# 5G Test Scope

A smart 5G log analyzer tool designed for test engineers to automatically analyze 5G gNodeB and simulator logs, detect failures, calculate key performance indicators (KPIs), and generate comprehensive reports.

## Features

- **Log Parsing**: Parses 5G log files to extract relevant events and messages
- **Failure Detection**: Automatically identifies and categorizes failures in the logs
- **KPI Calculation**: Computes key metrics including success rates and failure counts
- **Rich Reporting**: Generates colorized, formatted reports using Rich library
- **Modular Architecture**: Organized into separate modules for parsing, analysis, and reporting

## Project Structure

```
5gtestscope/
├── main.py                 # Main entry point
├── parser/
│   ├── __init__.py
│   └── log_parser.py       # Log file parsing logic
├── analyzer/
│   ├── __init__.py
│   ├── failure_detector.py # Failure detection algorithms
│   └── kpi_calculator.py   # KPI calculation functions
├── reports/
│   ├── __init__.py
│   └── report.py           # Report generation and formatting
└── examples/
    └── sample_log.txt      # Sample log file for testing
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/5gtestscope.git
   cd 5gtestscope
   ```

2. Install dependencies:
   ```bash
   pip install rich
   ```

## Usage

Run the analyzer on a log file:

```bash
python3 main.py <path_to_log_file>
```

Example:
```bash
python3 main.py examples/sample_log.txt
```

### Sample Output

```
5G Test Summary

Total Events: 5
Failures: 1
Success Rate: 80.0 %

Detected Issues
❌ Generic Failure Detected
```

## Log Format

The tool expects log files with timestamped entries. Example format:

```
[10:01] RRC Setup Request
[10:02] RRC Setup Complete
[10:03] Registration Accept
[10:04] PDU Session Establishment
[10:05] ERROR RRC Reconfiguration Failure
```

## Supported Events

- RRC Setup events
- Registration events
- PDU Session events
- Error and failure messages

## Dependencies

- Python 3.6+
- Rich (for console formatting)

## 🌐 Part of Telecom Test Toolkit

This project is part of the **Telecom Test Toolkit ecosystem**.

Other tools:

- 5GTestScope
- Test Monitor Dashboard
- Regression Flakiness Analyzer
- Test Report Generator

🔗 Main project:
https://github.com/gbvk312/telecom-test-toolkit

## License

See LICENSE file for details.
