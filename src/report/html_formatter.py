from typing import Dict, Any, List

from report.reporter import TestResult


def render_html(summary: Dict[str, Any], results: List[TestResult]) -> str:
    rows = []
    for r in results:
        if r.status == "PASSED":
            color = "#4caf50"
        elif r.status in ("FAILED", "ERROR"):
            color = "#f44336"
        else:
            color = "#9e9e9e"
        tags_str = ", ".join(r.tags)
        dur = f"{r.duration_ms:.2f}" if r.duration_ms is not None else "-"
        details = (r.details or "").replace("<", "<").replace(">", ">")
        rows.append(
            "<tr>"
            f"<td>{r.name}</td>"
            f"<td style='color:{color};font-weight:bold;'>{r.status}</td>"
            f"<td>{dur}</td>"
            f"<td>{tags_str}</td>"
            f"<td><pre style='white-space:pre-wrap;font-size:0.8em;'>{details}</pre></td>"
            "</tr>"
        )
    rows_html = "\n".join(rows)

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>IT Tester Report</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 20px;
      background: #111;
      color: #f5f5f5;
    }}
    h1, h2 {{
      margin-bottom: 0.4em;
    }}
    .summary {{
      margin-bottom: 20px;
      padding: 10px 14px;
      border-radius: 8px;
      background: #1e1e1e;
      border: 1px solid #333;
    }}
    .summary span {{
      margin-right: 16px;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      font-size: 0.9em;
      background: #1b1b1b;
    }}
    th, td {{
      border: 1px solid #333;
      padding: 8px;
    }}
    th {{
      background: #222;
    }}
    tr:nth-child(even) {{
      background: #161616;
    }}
  </style>
</head>
<body>
  <h1>IT Tester Report</h1>
  <div class="summary">
    <div><span><strong>ENV:</strong> {summary["env"]}</span><span><strong>BASE_API_URL:</strong> {summary["base_api_url"]}</span></div>
    <div>
      <span><strong>Total:</strong> {summary["total"]}</span>
      <span><strong>Passed:</strong> {summary["passed"]}</span>
      <span><strong>Failed:</strong> {summary["failed"]}</span>
      <span><strong>Error:</strong> {summary["error"]}</span>
      <span><strong>Anomaly:</strong> {summary["anomaly_count"]}</span>
      <span><strong>Total Time (ms):</strong> {summary["total_duration_ms"]:.2f}</span>
    </div>
  </div>
  <table>
    <thead>
      <tr>
        <th>Test Name</th>
        <th>Status</th>
        <th>Duration (ms)</th>
        <th>Tags</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</body>
</html>"""
    return html
