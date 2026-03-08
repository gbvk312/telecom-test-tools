---
description: "Instructions for working with the 5G test scope log analysis tool - a Python-based log parser for 5G network testing that detects failures and calculates KPIs"
---

# 5G Test Scope Log Analysis Tool

## Project Overview
This is a 5G log analysis tool designed for test engineers. It processes timestamped log files to extract events, detect failures, calculate key performance indicators (KPIs), and generate formatted reports using the Rich library for console output.

## Architecture
The tool follows a simple pipeline architecture with four main components:

- **Parser** (`parser/log_parser.py`): Extracts structured events from log files using string matching
- **Analyzer** (`analyzer/`): 
  - `failure_detector.py`: Identifies failure events
  - `kpi_calculator.py`: Computes statistics (total events, failure count, success rate)
- **Reporter** (`reports/report.py`): Formats and displays results with colored output using Rich
- **Main** (`main.py`): Orchestrates the entire pipeline

## How to Run
```bash
# Install dependencies
pip install rich

# Run the analyzer on a log file
python3 main.py examples/sample_log.txt
```

## Key Conventions
- **Log Format**: `[HH:MM] message` (e.g., `[14:30] RRC Setup Complete`)
- **Event Types**: `RRC_SETUP`, `REGISTRATION_SUCCESS`, `PDU_SESSION`, `FAILURE`
- **Output Formatting**: Use Rich console API for colored, structured output
- **Module Structure**: Pure Python with no external build tools - direct interpreter execution

## Common Pitfalls & Best Practices
- **Function Duplication**: `calculate_kpis()` exists in both `main.py` and `analyzer/kpi_calculator.py`. Always use the module version in `analyzer/kpi_calculator.py` and remove the duplicate from `main.py`.
- **Error Handling**: Add try/catch blocks for file operations (file not found) and prevent division-by-zero in success rate calculations.
- **Dependencies**: Create a `requirements.txt` file to document dependencies like Rich.
- **Parsing Limitations**: Uses naive substring matching which may create false positives (e.g., "ERROR" anywhere in a line). Consider regex for more robust parsing.
- **Import Cleanup**: Remove duplicate imports in `main.py` (detect_failures imported multiple times).
- **Testing**: No formal test framework - validate manually with sample logs.

## Key Files for Reference
- `main.py`: Complete pipeline execution
- `examples/sample_log.txt`: Sample log format
- `parser/log_parser.py`: Event extraction logic
- `reports/report.py`: Output formatting with Rich