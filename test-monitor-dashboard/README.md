# Test Monitor Dashboard 🧪

A real-time Python dashboard built with Streamlit, Pandas, and Plotly to visualize testing metrics, execution logs, and system performance. 

## Features
- **Real-Time Simulation**: Mocks a live testing environment where tests progress dynamically and emit execution logs. 
- **Auto-Refresh**: Configurable ticking loop to continuously refresh the dashboard to view changes.
- **Top-Level Metrics**: Summarizes test executions (Passed, Failed, Running, Skipped) with informative deltas.
- **Metrics Visualization**: Interactive pie charts and timeline duration plots.
- **Actionable Execution Logs**: Complete execution flow, with dynamic logs, and error-highlighting.
- **Memory Optimization**: Automatically prevents memory exhaustion by limiting history tracking bounds.

## Getting Started

1. **Install Requirements**
```bash
pip install -r requirements.txt
```

2. **Run the Dashboard**
```bash
streamlit run app.py
```

## Dashboard Structure
- `app.py`: The entry-point for the Streamlit dashboard rendering application state and controlling layout.
- `data_generator.py`: Generates mocked historical base data and simulates continuous real-time execution states via periodic ticks.
