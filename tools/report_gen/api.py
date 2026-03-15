"""
Report Generator API — Programmatic interface for HTML report generation.

Accepts PipelineOutput (from the pipeline engine) and generates a
comprehensive HTML report combining results from all tools.
"""

import os

from ttt.models import PipelineOutput


def _generate_html(pipeline_output: PipelineOutput) -> str:
    """Generate HTML content from pipeline output."""
    analyses_html = ""
    for analysis in pipeline_output.analyses:
        # Results table
        results_rows = ""
        for r in analysis.results[:50]:  # Limit to 50 for readability
            status_class = "pass" if r.status == "pass" else "fail"
            icon = "✔️" if r.status == "pass" else "❌"
            results_rows += f"""
            <tr class="{status_class}">
                <td>{icon} {r.test_id}</td>
                <td>{r.status.upper()}</td>
                <td>{r.message}</td>
            </tr>"""

        issues_html = ""
        if analysis.issues:
            issues_list = "".join(f"<li>❌ {issue}</li>" for issue in analysis.issues)
            issues_html = f"""
            <div class="issues">
                <h4>Detected Issues</h4>
                <ul>{issues_list}</ul>
            </div>"""

        kpis_html = ""
        if analysis.kpis:
            kpi_items = "".join(
                f"<div class='kpi-card'><span class='kpi-label'>{k}</span><span class='kpi-value'>{v}</span></div>"
                for k, v in analysis.kpis.items()
            )
            kpis_html = f"<div class='kpi-grid'>{kpi_items}</div>"

        analyses_html += f"""
        <div class="tool-section">
            <h3>📊 {analysis.tool_name}</h3>
            <div class="summary-bar">
                <span class="total">Total: {analysis.total_events}</span>
                <span class="passed">Passed: {analysis.passed}</span>
                <span class="failed">Failed: {analysis.failed}</span>
                <span class="rate">Success Rate: {analysis.success_rate}%</span>
            </div>
            {kpis_html}
            {issues_html}
            <table class="results-table">
                <thead>
                    <tr><th>Test ID</th><th>Status</th><th>Message</th></tr>
                </thead>
                <tbody>
                    {results_rows}
                </tbody>
            </table>
        </div>
        <hr>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telecom Test Report — Run {pipeline_output.run_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a; color: #e2e8f0; padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; margin-bottom: 0.5rem; font-size: 1.8rem; }}
        h3 {{ color: #7dd3fc; margin-bottom: 1rem; }}
        .meta {{ color: #94a3b8; margin-bottom: 2rem; font-size: 0.9rem; }}
        .tool-section {{
            background: #1e293b; border-radius: 12px; padding: 1.5rem;
            margin-bottom: 1.5rem; border: 1px solid #334155;
        }}
        .summary-bar {{
            display: flex; gap: 1.5rem; margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .summary-bar span {{
            padding: 0.4rem 1rem; border-radius: 6px; font-weight: 600;
            font-size: 0.85rem;
        }}
        .total {{ background: #334155; }}
        .passed {{ background: #166534; color: #4ade80; }}
        .failed {{ background: #7f1d1d; color: #fca5a5; }}
        .rate {{ background: #1e40af; color: #93c5fd; }}
        .kpi-grid {{
            display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 0.75rem; margin-bottom: 1rem;
        }}
        .kpi-card {{
            background: #0f172a; border: 1px solid #334155; border-radius: 8px;
            padding: 0.75rem; text-align: center;
        }}
        .kpi-label {{ display: block; color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; }}
        .kpi-value {{ display: block; color: #f1f5f9; font-size: 1.2rem; font-weight: 700; margin-top: 0.25rem; }}
        .issues {{ margin-bottom: 1rem; }}
        .issues h4 {{ color: #fca5a5; margin-bottom: 0.5rem; }}
        .issues ul {{ list-style: none; padding-left: 0.5rem; }}
        .issues li {{ color: #fca5a5; margin-bottom: 0.25rem; }}
        .results-table {{
            width: 100%; border-collapse: collapse; font-size: 0.85rem;
        }}
        .results-table th {{
            background: #334155; color: #cbd5e1; padding: 0.6rem 1rem;
            text-align: left; border-bottom: 2px solid #475569;
        }}
        .results-table td {{
            padding: 0.5rem 1rem; border-bottom: 1px solid #1e293b;
        }}
        .results-table tr.pass {{ background: #0f2a1a; }}
        .results-table tr.fail {{ background: #2a0f0f; }}
        .results-table tr:hover {{ background: #334155; }}
        hr {{ border: none; border-top: 1px solid #334155; margin: 1rem 0; }}
        .files-list {{ color: #94a3b8; font-size: 0.8rem; }}
        .files-list li {{ margin-bottom: 0.2rem; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Telecom Test Report</h1>
        <div class="meta">
            Run ID: {pipeline_output.run_id} | Timestamp: {pipeline_output.timestamp}
            | Files Analyzed: {len(pipeline_output.log_files)}
        </div>

        {analyses_html}

        <div class="tool-section">
            <h3>📁 Log Files Analyzed</h3>
            <ul class="files-list">
                {"".join(f'<li>{f}</li>' for f in pipeline_output.log_files)}
            </ul>
        </div>
    </div>
</body>
</html>"""

    return html


def generate(pipeline_output: PipelineOutput, output_path: str) -> str:
    """Generate an HTML report from pipeline output.

    Args:
        pipeline_output: Aggregated results from the pipeline.
        output_path: Path to write the HTML report file.

    Returns:
        The output path where the report was saved.
    """
    html = _generate_html(pipeline_output)

    os.makedirs(
        os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
        exist_ok=True,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
