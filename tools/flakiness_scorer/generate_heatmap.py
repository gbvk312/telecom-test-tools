import pandas as pd
import argparse
import os
import warnings


def load_and_merge_data(input_file, history_file, window):
    # Read the new daily results
    try:
        daily_df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Error reading input file {input_file}: {e}")
        return pd.DataFrame()

    # We expect columns like TestCase_ID, gNB_Build, Status
    if not all(
        col in daily_df.columns for col in ["TestCase_ID", "gNB_Build", "Status"]
    ):
        print(
            "Error: Input CSV must contain 'TestCase_ID', 'gNB_Build', and 'Status' columns."
        )
        return pd.DataFrame()

    # Pivot the daily data: Rows=TestCase, Cols=Build, Values=Status
    daily_pivot = daily_df.pivot(
        index="TestCase_ID", columns="gNB_Build", values="Status"
    )

    # Read historical data if it exists
    if os.path.exists(history_file):
        try:
            history_df = pd.read_csv(history_file, index_col="TestCase_ID")
        except Exception as e:
            print(f"Error reading history file {history_file}: {e}. Starting fresh.")
            history_df = pd.DataFrame()
    else:
        history_df = pd.DataFrame()

    # Merge history with new data
    if not history_df.empty:
        # Suppress FutureWarnings during DataFrame combination
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            # Update existing tests and add new ones (columns will also expand for new builds)
            merged_df = history_df.combine_first(daily_pivot)
    else:
        merged_df = daily_pivot

    # Enforce rolling window: keep only the last `window` builds (columns)
    # Sorting columns assuming build strings are sortable chronologically (e.g. Build_101, Build_102)
    sorted_columns = sorted(merged_df.columns.astype(str))
    merged_df = merged_df[sorted_columns[-window:]]

    # Save the updated history for the next run
    merged_df.to_csv(history_file)

    return merged_df


def evaluate_flakiness(row):
    # Drop NaN values (builds where the test did not run)
    runs = row.dropna()
    if runs.empty:
        return "No Data"

    statuses = runs.unique()

    # If it's all same
    if len(statuses) == 1:
        return "Stable" if statuses[0] == "Pass" else "Persistent Fail"

    # Calculate transitions
    # Shift array by 1 and compare to original to see when state changes
    transitions = (runs != runs.shift()).sum() - 1

    last_status = runs.iloc[-1]

    if transitions >= 2:
        return "High (Flaky)"
    elif transitions == 1:
        if last_status == "Fail":
            return "Recent Hard Fail"
        else:
            return "Fixed (Recent Pass)"

    return "Stable"  # Fallback


def color_cells(val):
    color = ""
    if val == "Pass" or val == "Fixed (Recent Pass)":
        color = "#c8e6c9"  # Light Green
    elif val == "Fail":
        color = "#ffcdd2"  # Light Red
    elif val == "High (Flaky)":
        color = "#fff9c4"  # Light Yellow
    elif val == "Recent Hard Fail" or val == "Persistent Fail":
        color = "#ff8a80"  # Dark Red
    elif val == "Stable":
        color = "#e2f0cb"  # Very Light Green

    return (
        f"background-color: {color}; color: black; text-align: center; border: 1px solid #ddd;"
        if color
        else ""
    )


def generate_report(heatmap_df, output_file):
    if heatmap_df.empty:
        print("No data available to generate the report.")
        return

    # Add diagnosis column
    diagnosis_df = heatmap_df.copy()
    diagnosis_df["Diagnosis"] = diagnosis_df.apply(evaluate_flakiness, axis=1)

    # Apply styles using map (Pandas 2.1+) or applymap (older Pandas)
    try:
        styled_df = diagnosis_df.style.map(color_cells)
    except AttributeError:
        styled_df = diagnosis_df.style.applymap(color_cells)

    html_output = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            h2 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th {{ background-color: #f2f2f2; padding: 10px; text-align: center; border: 1px solid #ddd; }}
            td {{ padding: 10px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>gNB Daily Regression - Flakiness Heatmap</h2>
        <p>This report highlights which test failures are likely real bugs vs. simulator flakiness.</p>
        <p><strong>Note:</strong> Data is merged with historical executions.</p>
        {styled_df.to_html()}
    </body>
    </html>
    """

    with open(output_file, "w") as f:
        f.write(html_output)

    print(f"✅ Success! Report generated at '{output_file}'.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a regression test flakiness heatmap."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to the latest daily test results CSV.",
    )
    parser.add_argument(
        "--history",
        type=str,
        default="historical_data.csv",
        help="Path to the running historical data CSV.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="regression_heatmap.html",
        help="Path to save the generated HTML output.",
    )
    parser.add_argument(
        "--window",
        type=int,
        default=14,
        help="Number of latest builds to track in history (default 14).",
    )

    args = parser.parse_args()

    merged_history = load_and_merge_data(args.input, args.history, args.window)
    generate_report(merged_history, args.output)
