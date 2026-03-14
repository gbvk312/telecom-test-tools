"""
Flakiness Scorer API — Programmatic interface for the heatmap scorer.

Returns structured FlakinessReport objects from CSV test data.
"""

import os
import pandas as pd
import warnings
from typing import List

from ttt.models import FlakinessReport


def _evaluate_flakiness(row) -> dict:
    """Evaluate the flakiness of a test case based on its history."""
    runs = row.dropna()
    if runs.empty:
        return {"diagnosis": "No Data", "transitions": 0, "last_status": ""}

    statuses = runs.unique()

    if len(statuses) == 1:
        diagnosis = "Stable" if statuses[0] == "Pass" else "Persistent Fail"
        return {"diagnosis": diagnosis, "transitions": 0, "last_status": str(runs.iloc[-1])}

    transitions = int((runs != runs.shift()).sum() - 1)
    last_status = str(runs.iloc[-1])

    if transitions >= 2:
        diagnosis = "High (Flaky)"
    elif transitions == 1:
        diagnosis = "Recent Hard Fail" if last_status == "Fail" else "Fixed (Recent Pass)"
    else:
        diagnosis = "Stable"

    return {
        "diagnosis": diagnosis,
        "transitions": transitions,
        "last_status": last_status,
    }


def score(
    input_csv: str,
    history_csv: str = "historical_data.csv",
    window: int = 14,
) -> List[FlakinessReport]:
    """Score test cases for flakiness based on historical data.

    Args:
        input_csv: Path to the latest daily test results CSV.
        history_csv: Path to the running historical data CSV.
        window: Number of latest builds to track.

    Returns:
        List of FlakinessReport, one per test case.
    """
    # Read daily results
    try:
        daily_df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading input file {input_csv}: {e}")
        return []

    required_cols = ['TestCase_ID', 'gNB_Build', 'Status']
    if not all(col in daily_df.columns for col in required_cols):
        print(f"Error: CSV must contain columns: {required_cols}")
        return []

    # Pivot daily data
    daily_pivot = daily_df.pivot(index='TestCase_ID', columns='gNB_Build', values='Status')

    # Read historical data if exists
    if os.path.exists(history_csv):
        try:
            history_df = pd.read_csv(history_csv, index_col='TestCase_ID')
        except Exception:
            history_df = pd.DataFrame()
    else:
        history_df = pd.DataFrame()

    # Merge
    if not history_df.empty:
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            merged_df = history_df.combine_first(daily_pivot)
    else:
        merged_df = daily_pivot

    # Rolling window
    sorted_columns = sorted(merged_df.columns.astype(str))
    merged_df = merged_df[sorted_columns[-window:]]

    # Save updated history
    merged_df.to_csv(history_csv)

    # Evaluate each test case
    reports = []
    for test_id in merged_df.index:
        row = merged_df.loc[test_id]
        eval_result = _evaluate_flakiness(row)
        builds_analyzed = int(row.notna().sum())

        reports.append(FlakinessReport(
            test_id=str(test_id),
            diagnosis=eval_result["diagnosis"],
            builds_analyzed=builds_analyzed,
            transitions=eval_result["transitions"],
            last_status=eval_result["last_status"],
        ))

    return reports
