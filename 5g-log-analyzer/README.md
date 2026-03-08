# 5G Log Analyzer

A Python script that parses 5G gNodeB logs to detect attach flows, RRC failures, and setup failures. It calculates attach success rates and provides a summarized report of the events found in the log file.

## Features

- Parses gNodeB logs for specific 3GPP messages:
  - Attach Requests, Accepts, and Rejects
  - RRC Rejects / RRCConnectionReject
  - Setup Failures
- Calculates Attach Success Rate.
- Provides a high-level test summary and detailed statistics.

## Prerequisites

- Python 3.x

## Usage

Run the analyzer script by passing the path to the log file as an argument:

```bash
python analyzer.py <path_to_log_file>
```

For example, if you have a `sample_logs.txt` file:

```bash
python analyzer.py sample_logs.txt
```

## Example Output

```text
Test Summary:
  Attach Success Rate: 98%
  RRC Failures: 2
  Setup Failures: 1

Detailed Stats:
  Total Attach Attempts: 100
  Total Attach Successes: 98
  Total Attach Rejects: 2
```

## 🌐 Part of Telecom Test Toolkit

This project is part of the **Telecom Test Toolkit ecosystem**.

Other tools:

- 5GTestScope
- Test Monitor Dashboard
- Regression Flakiness Analyzer
- Test Report Generator

🔗 Main project:
https://github.com/gbvk312/telecom-test-toolkit
