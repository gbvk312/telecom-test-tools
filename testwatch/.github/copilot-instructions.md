# testwatch Development Guide

## Project Overview

**testwatch** is a Python-based log monitoring tool that parses test result logs and provides formatted summaries with visual indicators (✔️ for passes, ❌ for failures).

**Purpose**: Process test logs to identify test results through pattern matching for keywords like FAIL, ERROR, CRASH, TIMEOUT. Each result is displayed with clear visual indicators and summary statistics.

**Version**: 1.0.0  
**Author**: gbvk312  
**License**: MIT

## Quick Start

```bash
# Run from project root
python3 testwatch/main.py sample_log.txt

# Or install as system command
python3 setup.py install
testwatch <logfile>
```

## Architecture

### Project Structure
```
testwatch/
├── main.py              # CLI entry point, argument handling
├── parser.py            # Pattern matching logic for result classification
├── watcher.py           # Core logic: file I/O, iteration, formatting
└── __init__.py          # Package initialization (empty)

docs/
├── usage.md             # Detailed usage examples & troubleshooting
└── (docs structure)

examples/
└── telecom_log.txt      # Sample telecom log for testing

sample_log.txt           # Basic sample test log
setup.py                 # Package configuration (setuptools)
requirement.txt          # Dependencies (none, stdlib only)
README.md                # Main documentation
LICENSE                  # MIT License
.github/
└── copilot-instructions.md  # This file
```

### Component Responsibilities

- **main.py**: Command-line interface, handles logfile argument parsing
- **watcher.py**: Main business logic (file I/O, line iteration, output formatting, statistics)
- **parser.py**: Test result classification via regex pattern matching against FAIL_PATTERNS

## Development Commands

### Running the Tool

```bash
# Basic execution
python3 testwatch/main.py <logfile>

# Examples
python3 testwatch/main.py sample_log.txt
python3 testwatch/main.py examples/telecom_log.txt
python3 testwatch/main.py test_results/2026_03_07.txt
```

### Expected Output Format

```
✔ TestCase_1 PASSED
✔ TestCase_2 PASSED
❌ TestCase_3 FAILED
✔ TestCase_4 PASSED

Summary
Passed: 3
Failed: 1
```

Each log line is printed with a prefix (✔ for PASS, ❌ for FAIL), followed by the summary.

### Testing Changes

1. Create or modify log files in `sample_log.txt` or `examples/`
2. Run: `python3 testwatch/main.py <logfile>`
3. Verify output displays correct indicators and counts
4. Iterate on `parser.py` or `watcher.py` as needed

## Conventions & Patterns

### Pattern Matching (parser.py)

**Default Failure Patterns** (case-insensitive):
- `FAIL`
- `FAILED`
- `ERROR`
- `CRASH`
- `TIMEOUT`

**Logic**: Returns `"FAIL"` if any pattern matches, otherwise `"PASS"`

**Extension**: Add new patterns to `FAIL_PATTERNS` list in `parser.py`:
```python
FAIL_PATTERNS = [
    "FAIL",
    "FAILED",
    "ERROR",
    "CRASH",
    "TIMEOUT",
    "SEVERE",     # Add custom pattern here
    "CRITICAL",   # Add custom pattern here
]
```

### Output Formatting (watcher.py)

- Each log line prefixed with ✔ (pass) or ❌ (fail) and emoji
- Summary always printed after all lines processed
- Statistics tracked via two counters: `passed` and `failed`
- Zero-indexed line processing with `.readlines()`

## Common Development Tasks

### Adding New Failure Patterns

1. Open `testwatch/parser.py`
2. Add pattern to `FAIL_PATTERNS` list (any case)
3. Test: `python3 testwatch/main.py examples/telecom_log.txt`

### Creating Test Log Files

- Place in `examples/` or use `sample_log.txt`
- One test result per line
- Include keywords (FAIL, ERROR, etc.) to test new patterns

### Customizing Output Format

Edit print statements in `watcher.py`:
- Change emoji indicators (✔/❌)
- Adjust summary format
- Add filtering or log-level support

## Technical Details

### Python Requirements

- **Python 3.6+** (uses f-strings, dict ordering)
- **Standard Library Only**: `sys`, `re`
- **No External Dependencies**

See [requirement.txt](requirement.txt) for details.

### Module Imports

**main.py**
```python
import sys
from watcher import watch_log
```

**watcher.py**
```python
from parser import parse_line
```

**parser.py**
```python
import re
```

### Design Decisions

1. **Regex Pattern Matching**: Case-insensitive for robustness
2. **Eager File Reading**: Loads entire file into memory (suitable for typical log sizes)
3. **Simple Statistics**: Pass/fail counters (no advanced metrics)
4. **Minimal Dependencies**: Uses only stdlib for portability

## Known Limitations & Future Improvements

### Current Limitations
- Reads entire file into memory (not suitable for very large logs >1GB)
- No real-time monitoring (processes completed file only)
- Limited statistics (only pass/fail counts)

### Planned Enhancements
- ✅ Package setup (done in setup.py)
- ⬜ Unit tests for parser and watcher
- ⬜ Configuration file support (JSON/YAML)
- ⬜ Real-time log monitoring with file watching
- ⬜ Support for structured logs (JSON, XML)
- ⬜ Performance optimization for large files
- ⬜ Advanced statistics and filtering
- ⬜ CLI progress indicators

## References

- [Full Usage Guide](docs/usage.md) - Detailed examples and troubleshooting
- [README](../README.md) - Project overview and installation
- [LICENSE](../LICENSE) - MIT License details
