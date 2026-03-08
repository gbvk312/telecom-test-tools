# testwatch Usage Guide

## Installation

### Option 1: Direct Execution

No installation required. Run directly from the repo:

```bash
python3 testwatch/main.py <logfile>
```

### Option 2: Package Installation

Install as a system command:

```bash
python3 setup.py install
```

Then use from anywhere:

```bash
testwatch <logfile>
```

## Basic Usage

### Simple Example

```bash
python3 testwatch/main.py sample_log.txt
```

**Output:**
```
✔ TestCase_1 PASSED
✔ TestCase_2 PASSED
❌ TestCase_3 FAILED
✔ TestCase_4 PASSED

Summary
Passed: 3
Failed: 1
```

## Examples

### Example 1: Analyzing Standard Test Logs

**Input file: `test_results.txt`**
```
Test_Unit_1 PASSED
Test_Unit_2 PASSED
Test_Unit_3 FAILED - Connection timeout
Test_Unit_4 PASSED
```

**Command:**
```bash
python3 testwatch/main.py test_results.txt
```

**Output:**
```
✔ Test_Unit_1 PASSED
✔ Test_Unit_2 PASSED
❌ Test_Unit_3 FAILED - Connection timeout
✔ Test_Unit_4 PASSED

Summary
Passed: 3
Failed: 1
```

### Example 2: Telecom Log Analysis

**Input file: `examples/telecom_log.txt`**
```
2026-03-07 10:00:00 [INFO] Call Setup Initiated
2026-03-07 10:00:01 [INFO] Call Connected Successfully
2026-03-07 10:00:05 [INFO] Call Terminated PASSED
2026-03-07 10:00:06 [ERROR] Signal Lost - FAILED
2026-03-07 10:01:00 [INFO] reconnection PASSED
```

**Command:**
```bash
python3 testwatch/main.py examples/telecom_log.txt
```

**Output:**
```
✔ 2026-03-07 10:00:00 [INFO] Call Setup Initiated
✔ 2026-03-07 10:00:01 [INFO] Call Connected Successfully
✔ 2026-03-07 10:00:05 [INFO] Call Terminated PASSED
❌ 2026-03-07 10:00:06 [ERROR] Signal Lost - FAILED
✔ 2026-03-07 10:01:00 [INFO] reconnection PASSED

Summary
Passed: 4
Failed: 1
```

### Example 3: Complex Error Scenarios

**Input file: `crash_logs.txt`**
```
[00:00:01] Service started
[00:00:02] Processing request A
[00:00:03] Request A completed
[00:00:04] Processing request B
[00:00:05] CRASH - Memory overflow
[00:00:06] Service restarted
[00:00:07] ERROR - Database connection failed
[00:00:08] Processing request C
[00:00:09] Request C TIMEOUT - No response received
```

**Command:**
```bash
python3 testwatch/main.py crash_logs.txt
```

**Output:**
```
✔ [00:00:01] Service started
✔ [00:00:02] Processing request A
✔ [00:00:03] Request A completed
✔ [00:00:04] Processing request B
❌ [00:00:05] CRASH - Memory overflow
✔ [00:00:06] Service restarted
❌ [00:00:07] ERROR - Database connection failed
✔ [00:00:08] Processing request C
❌ [00:00:09] Request C TIMEOUT - No response received

Summary
Passed: 6
Failed: 3
```

## Pattern Matching Details

### Default Failure Patterns

The following patterns trigger a FAIL result (case-insensitive):

- `FAIL` - Generic failure
- `FAILED` - Test failed
- `ERROR` - Error occurred
- `CRASH` - System crash
- `TIMEOUT` - Operation timed out

**Examples of lines that trigger FAIL:**
```
Test failed
An ERROR occurred
CRASH: System halted
Request TIMEOUT
ERROR: Connection refused
fail: test_case_1
```

### Custom Pattern Matching

To add custom failure patterns:

1. Open `testwatch/parser.py`
2. Edit the `FAIL_PATTERNS` list:

```python
FAIL_PATTERNS = [
    "FAIL",
    "FAILED",
    "ERROR",
    "CRASH",
    "TIMEOUT",
    "SEVERE",      # Add custom pattern
    "CRITICAL",    # Add custom pattern
    "WARNING",     # Add custom pattern
]
```

3. Save and run testwatch:

```bash
python3 testwatch/main.py <logfile>
```

## Output Explanation

### Line Format

Each log line is prefixed with a status indicator:

- ✔ (checkmark) = PASS - No failure keywords detected
- ❌ (cross) = FAIL - Failure keyword detected

### Summary Format

After processing all lines, testwatch displays:

```
Summary
Passed: <number of passing lines>
Failed: <number of failing lines>
```

## Common Use Cases

### 1. Post-Test Analysis

After running automated tests:

```bash
# Save test output to file
npm test > test_output.txt 2>&1

# Analyze with testwatch
python3 testwatch/main.py test_output.txt
```

### 2. CI/CD Pipeline Integration

```bash
# Run tests and pipe to testwatch
python3 testwatch/main.py ci_logs/run_$(date +%Y%m%d).txt
```

### 3. Log Monitoring

For system logs or service logs:

```bash
python3 testwatch/main.py /var/log/application.log
```

### 4. Multiple Test Runs

Process multiple test result files:

```bash
for logfile in test_results/*.txt; do
    echo "Processing: $logfile"
    python3 testwatch/main.py "$logfile"
    echo "---"
done
```

## Troubleshooting

### File Not Found

```bash
python3 testwatch/main.py nonexistent.txt
# Error: [Errno 2] No such file or directory: 'nonexistent.txt'
```

**Solution:** Verify the log file path is correct and the file exists.

### Import Errors

```bash
cd testwatch
python3 testwatch/main.py ../sample_log.txt
# Error: ModuleNotFoundError: No module named 'watcher'
```

**Solution:** Run from the project root directory or use full paths.

### Empty Results

**Input:** Empty log file or all lines contain failure keywords

**Output:**
```
Summary
Passed: 0
Failed: 0
```

or

```
Summary
Passed: 0
Failed: 5
```

## Tips & Best Practices

1. **Pre-process logs**: For complex log formats, pre-process them to extract relevant lines before piping to testwatch
2. **Version your logs**: Save logs with timestamps for trend analysis
3. **Pipe operations**: Combine with grep or awk for advanced filtering
4. **Batch processing**: Create shell scripts to process multiple log files

## More Information

- For architecture details, see [../README.md](../README.md)
- For development info, see [../.github/copilot-instructions.md](../.github/copilot-instructions.md)
