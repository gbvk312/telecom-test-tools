import streamlit as st
import pandas as pd
import plotly.express as px
from time import sleep

from data_generator import get_generator

# Must be the first Streamlit command
st.set_page_config(page_title="Test Monitor Dashboard", page_icon="🧪", layout="wide")

# Initialize data generator
gen = get_generator()


# Auto-refresh loop handling
def auto_refresh(refresh_rate):
    if refresh_rate > 0:
        sleep(refresh_rate)
        gen.tick()  # Simulate tests progressing
        st.rerun()


# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Dashboard Settings")
    st.markdown("Control the mock test monitor behavior.")

    auto_refresh_rate = st.slider(
        "Auto-refresh interval (seconds)",
        min_value=0,
        max_value=30,
        value=2,
        help="Set to 0 to disable auto-refresh.",
    )

    st.subheader("Filters")
    status_filter = st.multiselect(
        "Filter by Status",
        options=["Passed", "Failed", "Running", "Skipped"],
        default=["Passed", "Failed", "Running", "Skipped"],
    )

    st.markdown("---")
    if st.button("Trigger Manual Tick"):
        gen.tick()
        st.rerun()

# --- Main Dashboard ---
st.title("🧪 Test Monitor Dashboard")
st.markdown("Real-time simulation of test execution results and metrics.")

# Fetch data
df_tests = gen.get_test_df()
df_logs = gen.get_logs_df()

# Apply filters
if status_filter:
    df_tests_filtered = df_tests[df_tests["Status"].isin(status_filter)]
else:
    df_tests_filtered = pd.DataFrame(columns=df_tests.columns)
    st.warning("Please select at least one Test Status filter.")

# --- Top Level Metrics ---
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)

total_tests = len(df_tests_filtered)
passed_tests = len(df_tests_filtered[df_tests_filtered["Status"] == "Passed"])
failed_tests = len(df_tests_filtered[df_tests_filtered["Status"] == "Failed"])
running_tests = len(df_tests_filtered[df_tests_filtered["Status"] == "Running"])

with col1:
    st.metric("Total Tests", total_tests)
with col2:
    st.metric(
        "Passed",
        passed_tests,
        delta=f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
    )
with col3:
    st.metric(
        "Failed",
        failed_tests,
        delta=f"{-failed_tests}" if failed_tests > 0 else "0",
        delta_color="inverse",
    )
with col4:
    st.metric("Running", running_tests)


# --- Charts Section ---
st.subheader("Metrics Visualization")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # Pass/Fail Distribution Pie Chart
    status_counts = df_tests_filtered["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]

    # Consistent coloring for status
    color_discrete_map = {
        "Passed": "#2ca02c",  # green
        "Failed": "#d62728",  # red
        "Running": "#ff7f0e",  # orange
        "Skipped": "#7f7f7f",  # gray
    }

    fig_pie = px.pie(
        status_counts,
        values="Count",
        names="Status",
        title="Test Status Distribution",
        color="Status",
        color_discrete_map=color_discrete_map,
        hole=0.4,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with chart_col2:
    # Duration Scatter/Bar Chart (only for finished tests)
    finished_tests = df_tests_filtered[
        df_tests_filtered["Status"].isin(["Passed", "Failed"])
    ].copy()
    if not finished_tests.empty:
        # Sort by start time mostly to make it look sequential
        finished_tests = finished_tests.sort_values(by="Start Time").tail(
            50
        )  # Last 50 tests to avoid clutter

        fig_bar = px.scatter(
            finished_tests,
            x="Test ID",
            y="Duration (s)",
            color="Status",
            title="Recent Test Execution Durations",
            color_discrete_map=color_discrete_map,
        )
        # remove x axis labels for cleanliness if too many
        fig_bar.update_xaxes(showticklabels=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Not enough completed tests to show duration chart.")


# --- Detail Sections ---
st.markdown("---")
tab1, tab2 = st.tabs(["Test Runs", "Execution Logs"])

with tab1:
    st.subheader("Test Execution Detail")

    # Format datetimes nicely before displaying
    display_df = df_tests_filtered.copy()
    display_df["Start Time"] = display_df["Start Time"].dt.strftime("%H:%M:%S")
    # Handle NaT for running tests
    display_df["End Time"] = display_df["End Time"].apply(
        lambda x: x.strftime("%H:%M:%S") if pd.notnull(x) else "-"
    )
    # Format float format
    display_df["Duration (s)"] = display_df["Duration (s)"].apply(
        lambda x: f"{x:.2f}" if pd.notnull(x) else "-"
    )

    # Style styling for dataview
    def color_status(val):
        color_map = {
            "Passed": "color: green",
            "Failed": "color: red",
            "Running": "color: orange",
            "Skipped": "color: gray",
        }
        return color_map.get(val, "")

    st.dataframe(
        display_df.style.map(color_status, subset=["Status"]),
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.subheader("System Logs")

    log_level_filter = st.multiselect(
        "Filter Logs by Level",
        options=["INFO", "DEBUG", "WARNING", "ERROR"],
        default=["INFO", "WARNING", "ERROR"],
    )

    if log_level_filter:
        df_logs_filtered = df_logs[df_logs["Level"].isin(log_level_filter)]
    else:
        df_logs_filtered = pd.DataFrame(columns=df_logs.columns)
        st.warning("Please select at least one Log Level filter.")

    df_logs_filtered = (
        df_logs_filtered.sort_values(by="Timestamp", ascending=False)
        if not df_logs_filtered.empty
        else df_logs_filtered
    )

    # Format Timestamp
    df_logs_filtered["Timestamp"] = (
        df_logs_filtered["Timestamp"].dt.strftime("%H:%M:%S.%f").str[:-3]
    )

    def log_color(row):
        level = row["Level"]
        if level == "ERROR":
            return ["background-color: #ffe6e6"] * len(row)
        if level == "WARNING":
            return ["background-color: #fff3cd"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_logs_filtered.style.apply(log_color, axis=1),
        use_container_width=True,
        hide_index=True,
        height=400,
    )

# Execute auto-refresh at the end of the script run
auto_refresh(auto_refresh_rate)
