# testwatch

A simple yet powerful Python-based log monitoring tool that parses test result logs and provides formatted summaries with visual indicators.

## Overview

**testwatch** processes test logs line-by-line, identifying test results through pattern matching for common failure keywords (FAIL, ERROR, CRASH, TIMEOUT). Each result is displayed with visual indicators (✔️ for passes, ❌ for failures), followed by a summary of pass/fail counts.

## Features

- 🚀 **Fast & Lightweight**: Simple pattern-matching logic with no external dependencies
- 📊 **Visual Feedback**: Clear ✔️/❌ indicators for each test result
- 📈 **Summary Statistics**: Pass/fail counters at the end of analysis
- 🔧 **Extensible Patterns**: Easy to add new failure patterns
- 📝 **Case-Insensitive Matching**: Recognizes patterns regardless of case

## Installation

### From Source

```bash
git clone <repository-url>
cd testwatch
python3 setup.py install
```

### Manual Usage

No installation required. Run directly:

```bash
python3 testwatch/main.py <logfile>
```

## Usage

### Basic Command

```bash
python3 testwatch/main.py sample_log.txt
```

### Output Example

```
✔ TestCase_1 PASSED
✔ TestCase_2 PASSED
❌ TestCase_3 FAILED
✔ TestCase_4 PASSED

Summary
Passed: 3
Failed: 1
```

### With Different Log Files

```bash
# Analyze test results
python3 testwatch/main.py results/test_run_2026.txt

# Analyze telecom logs
python3 testwatch/main.py examples/telecom_log.txt
```

See [docs/usage.md](docs/usage.md) for more examples.

## Project Structure

```
testwatch/
├── main.py              # CLI entry point
├── parser.py            # Pattern matching logic
├── watcher.py           # Core monitoring & output formatting
└── __init__.py          # Package initialization

docs/
├── usage.md             # Detailed usage examples
└── copyright/           # License info

examples/
└── telecom_log.txt      # Sample telecom log for testing

sample_log.txt           # Basic sample log file
setup.py                 # Package configuration
requirement.txt          # Dependencies list
README.md                # This file
LICENSE                  # MIT License
```

## How It Works

### Components

1. **main.py**: Command-line interface that accepts a logfile path and invokes the watcher
2. **parser.py**: Contains pattern matching logic to classify lines as PASS or FAIL
3. **watcher.py**: Reads the entire log file, processes each line, and outputs formatted results with summary

### Pattern Matching

Default failure patterns (case-insensitive):
- `FAIL`
- `FAILED`
- `ERROR`
- `CRASH`
- `TIMEOUT`

Any line matching one of these patterns is marked as FAIL. All other lines are marked as PASS.

To add new patterns, edit `FAIL_PATTERNS` in `parser.py`.

## Configuration

### Adding Custom Failure Patterns

Edit `testwatch/parser.py`:

```python
FAIL_PATTERNS = [
    "FAIL",
    "FAILED",
    "ERROR",
    "CRASH",
    "TIMEOUT",
    "WARNING",        # Add custom pattern here
    "SEVERE",         # Add custom pattern here
]
```

Then rerun the tool:

```bash
python3 testwatch/main.py <logfile>
```

## Requirements

- Python 3.x
- Standard library only (no external dependencies)

See [requirement.txt](requirement.txt) for full dependency info.

## Examples

### Telecom Log Analysis

```bash
python3 testwatch/main.py examples/telecom_log.txt
```

### Custom Log Files

Create your own log file with test results and run:

```bash
python3 testwatch/main.py path/to/your/logfile.txt
```

## Development

### Running Tests

```bash
# Basic functionality test
python3 testwatch/main.py sample_log.txt

# With custom patterns
# Edit parser.py, then run
python3 testwatch/main.py sample_log.txt
```

### Modifying Output Format

Edit the print statements in `testwatch/watcher.py` to customize the output format.

## Future Enhancements

- Unit tests for parser and watcher modules
- Configuration file support for pattern customization
- Real-time log monitoring (currently reads entire file)
- Support for multiple log formats (JSON, XML, etc.)
- Performance optimizations for large log files
- Advanced filtering and statistics

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

MIT License - See [LICENSE](LICENSE) file for details.

## Author

Created by gbvk312

## Changelog

### Version 1.0 (Current)
- Initial release
- Pattern-based log parsing
- Visual pass/fail indicators
- Summary statistics
