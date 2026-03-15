"""
Dashboard Data Reader — Reads pipeline output JSON for real data display.

Replaces mock data_generator.py when real pipeline data is available.
Supports both real data mode (from pipeline JSON) and mock mode (for demos).
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional


class PipelineDataReader:
    """Reads pipeline output JSON and provides DataFrames for the dashboard."""

    def __init__(self, data_dir: str = "./output"):
        self.data_dir = data_dir
        self._pipeline_data = None
        self._load_data()

    def _load_data(self):
        """Load the latest pipeline output JSON."""
        json_path = os.path.join(self.data_dir, "pipeline_output.json")
        if os.path.isfile(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                self._pipeline_data = json.load(f)
        else:
            self._pipeline_data = None

    def has_data(self) -> bool:
        """Check if real pipeline data is available."""
        return self._pipeline_data is not None

    def tick(self):
        """Reload data from disk (for auto-refresh)."""
        self._load_data()

    def get_test_df(self) -> pd.DataFrame:
        """Get a DataFrame of test results from all analyses."""
        if not self.has_data():
            return pd.DataFrame(
                columns=[
                    "Test ID",
                    "Suite",
                    "Status",
                    "Start Time",
                    "End Time",
                    "Duration (s)",
                ]
            )

        rows = []
        for analysis in self._pipeline_data.get("analyses", []):
            for result in analysis.get("results", []):
                status_map = {
                    "pass": "Passed",
                    "fail": "Failed",
                    "error": "Failed",
                    "skip": "Skipped",
                }
                rows.append(
                    {
                        "Test ID": result.get("test_id", ""),
                        "Suite": analysis.get("tool_name", ""),
                        "Status": status_map.get(
                            result.get("status", ""), result.get("status", "")
                        ),
                        "Start Time": pd.Timestamp(
                            self._pipeline_data.get(
                                "timestamp", datetime.now().isoformat()
                            )
                        ),
                        "End Time": pd.Timestamp(
                            self._pipeline_data.get(
                                "timestamp", datetime.now().isoformat()
                            )
                        ),
                        "Duration (s)": result.get("duration_seconds"),
                    }
                )

        df = pd.DataFrame(rows)
        return df

    def get_logs_df(self) -> pd.DataFrame:
        """Get a DataFrame of execution logs from analyses."""
        if not self.has_data():
            return pd.DataFrame(columns=["Timestamp", "Test ID", "Level", "Message"])

        rows = []
        for analysis in self._pipeline_data.get("analyses", []):
            # Create log entries from issues
            for issue in analysis.get("issues", []):
                rows.append(
                    {
                        "Timestamp": pd.Timestamp(
                            self._pipeline_data.get(
                                "timestamp", datetime.now().isoformat()
                            )
                        ),
                        "Test ID": analysis.get("tool_name", ""),
                        "Level": "ERROR",
                        "Message": issue,
                    }
                )

            # Create log entries from results
            for result in analysis.get("results", []):
                level = "ERROR" if result.get("status") == "fail" else "INFO"
                rows.append(
                    {
                        "Timestamp": pd.Timestamp(
                            self._pipeline_data.get(
                                "timestamp", datetime.now().isoformat()
                            )
                        ),
                        "Test ID": result.get("test_id", ""),
                        "Level": level,
                        "Message": result.get("message", ""),
                    }
                )

        df = pd.DataFrame(rows)
        return df

    def get_summary(self) -> dict:
        """Get a summary dict from pipeline data."""
        if not self.has_data():
            return {}

        return {
            "run_id": self._pipeline_data.get("run_id", ""),
            "timestamp": self._pipeline_data.get("timestamp", ""),
            "log_files": self._pipeline_data.get("log_files", []),
            "num_analyses": len(self._pipeline_data.get("analyses", [])),
            "report_path": self._pipeline_data.get("report_path", ""),
        }


def get_reader(data_dir: Optional[str] = None):
    """Get a PipelineDataReader instance.

    If real data is available, returns a PipelineDataReader.
    Otherwise, falls back to the mock data generator.
    """
    import streamlit as st

    if "data_reader" not in st.session_state:
        dir_to_use = data_dir or os.environ.get("TTT_DATA_DIR", "./output")

        reader = PipelineDataReader(dir_to_use)

        if reader.has_data():
            st.session_state.data_reader = reader
            st.session_state.data_mode = "real"
        else:
            # Fall back to mock data for demos
            from tools.dashboard.data_generator import MockTestGenerator

            st.session_state.data_reader = MockTestGenerator()
            st.session_state.data_mode = "mock"

    return st.session_state.data_reader
