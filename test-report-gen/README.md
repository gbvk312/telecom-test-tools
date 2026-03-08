# test-report-gen

A robust Python CLI tool that parses execution logs (Pytest, Network, Automation) and generates interactive, beautifully designed HTML summary reports using Chart.js.

## Features
- **Multi-format Support**: Currently supports Pytest logs, Network logs, and generic Automation logs.
- **Interactive Visualizations**: Generates dynamic Doughnut charts via Chart.js indicating the pass/fail success ratio.
- **Detailed Summary**: Lists each parsed test execution result in a clean, responsive table using Bootstrap 5.
- **Extensible Architecture**: Easy to add new parsers for different log formats.

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Use the CLI to provide the log files you want to parse. You can provide one or multiple log types at the same time:

### Basic Example
```bash
python main.py --pytest-logs dummy_pytest.log --network-logs dummy_network.log --output report.html
```

### All Arguments
- `--pytest-logs`: Path to your Pytest format log file.
- `--automation-logs`: Path to your generic automation log file.
- `--network-logs`: Path to your network diagnostics log file.
- `--output`: Destination path for the generated HTML report (default: `report.html`).

## Example Workflow
To see the tool in action using the provided dummy logs:
```bash
python main.py --pytest-logs dummy_pytest.log --network-logs dummy_network.log --output sample_report.html
```
Open `sample_report.html` in your web browser to view the interactive dashboard.

## Architecture & Project Structure
```text
test-report-gen/
├── main.py                     # CLI entrypoint
├── requirements.txt            # Python dependencies (Jinja2)
├── src/
│   ├── generator.py            # HTML rendering logic using Jinja2
│   └── parsers.py              # Log parsing strategy (Pytest, Network, Automation)
├── templates/
│   └── report.html             # HTML/JS scaffold using Bootstrap and Chart.js
└── dummy_*.log                 # Sample logs for testing
```

- **Parsers (`src/parsers.py`)**: Contains configurable regex-based methods matching specific test log outputs. Returns standard dictionary objects mapping execution results.
- **Generator (`src/generator.py`)**: Interacts with the `jinja2` package to interpolate the aggregated parser dictionary into the HTML.
## Future Improvements
- Add support for structured input formats like JUnit XML or Pytest JSON.

## 🌐 Part of Telecom Test Toolkit

This project is part of the **Telecom Test Toolkit ecosystem**.

Other tools:

- 5GTestScope
- Test Monitor Dashboard
- Regression Flakiness Analyzer
- Test Report Generator

🔗 Main project:
https://github.com/gbvk312/telecom-test-toolkit
