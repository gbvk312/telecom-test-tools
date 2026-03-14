# Regression-Flakiness-Heatmap-Scorer

### The "Regression Flakiness Heatmap & Scorer"

**The Problem:**
When we trigger daily executions for gNB and simulator builds, we often encounter "flaky" tests—test cases that fail randomly due to test environment glitches, simulator timing issues, or CPU spikes, rather than genuine bugs in the 5G NodeB software. When we see a failure, we waste time debating, "Is this a real software bug, or did the simulator just choke again?" We often end up manually re-triggering the test just to see if it passes the second time.

**The Solution:**
A lightweight analytics script that parses your daily regression result files (like CSVs) over a rolling window (e.g., 14 builds). It calculates a "Flakiness Score" for each test case based on state transitions and generates a simple, color-coded HTML heatmap showing the pass/fail history across recent gNB builds.

#### Features

1. **Data Harvesting & Memory:** The script reads daily test result CSVs and merges them into a running `--history` CSV file. It automatically truncates the history to a specified `--window` to keep calculations relevant to recent builds.
2. **Scoring Logic:** The script calculates stability based on state transitions (Pass <-> Fail flips) across time:
   * **Stable**: Consistently passing.
   * **Persistent Fail**: Consistently failing.
   * **Recent Hard Fail**: Flipped from Pass to Fail exactly once and stayed failing (highly likely to be a real bug).
   * **Fixed (Recent Pass)**: Flipped from Fail to Pass exactly once.
   * **High (Flaky)**: Multiple transitions between Pass and Fail.
3. **Visual Output:** Generates a static HTML page with a grid. Rows are Test Case IDs, columns are Build Numbers, and cells are color-coded based on their flakiness diagnosis.

#### Usage

The script `generate_heatmap.py` requires `pandas` and `jinja2`. Run it via the command line, providing your daily test results CSV.

```bash
# Basic usage
python generate_heatmap.py --input latest_run.csv 

# Full usage with all arguments
python generate_heatmap.py \
    --input test_results.csv \
    --history historical_data.csv \
    --output regression_heatmap.html \
    --window 14
```

* `--input`: (Required) Path to the latest daily test results CSV. The CSV must contain `TestCase_ID`, `gNB_Build`, and `Status` columns.
* `--history`: (Optional) Path to the running historical data CSV. Defaults to `historical_data.csv`. The script creates this file if it doesn't exist and updates it on subsequent runs.
* `--output`: (Optional) Path to save the generated HTML output. Defaults to `regression_heatmap.html`.
* `--window`: (Optional) Number of latest builds to track in history. Defaults to `14`.

#### Why is this "Easily Implementable"?

* **No Database Required:** You don’t need to set up a complex SQL database. The script simply uses a CSV file as its "memory" of past executions.
* **Standard Libraries:** You only need Python with the `pandas` and `jinja2` libraries.
* **Passive Execution:** It simply reads post-execution reports. It doesn't interact with the live gNB or simulator, meaning there is zero risk of it breaking your actual test environment.

#### The Value Add (ROI):

* **Faster Triage:** Instead of manually investigating every red "FAIL", the team can instantly look at the heatmap. If it's flagged as "Flaky," they know to investigate the simulator environment first. If it's a "Recent Hard Fail," they immediately raise a Problem Report.
* **Metrics for Management:** It provides concrete data to management to show *why* the automation team needs dedicated time to fix unstable test scripts or why the simulator vendor needs to fix stability issues.

## 🌐 Part of Telecom Test Toolkit

This project is part of the **Telecom Test Toolkit ecosystem**.

Other tools:

- 5GTestScope
- Test Monitor Dashboard
- Regression Flakiness Analyzer
- Test Report Generator

🔗 Main project:
https://github.com/gbvk312/telecom-test-toolkit
