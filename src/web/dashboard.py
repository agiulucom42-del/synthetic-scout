import html
import json
from pathlib import Path

from flask import Flask, Response, jsonify

app = Flask(__name__)


def load_summary():
    summary_path = Path("reports/summary.json")
    if not summary_path.exists():
        return None
    try:
        return json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - resilient dashboard
        return None


@app.get("/api/summary")
def api_summary():
    summary = load_summary()
    if summary is None:
        return jsonify({"error": "summary.json bulunamadý, önce testleri çalýþtýrýn."}), 404
    return jsonify(summary)


@app.get("/")
def index():
    summary = load_summary()
    if summary is None:
        body = "<h1>ULU QA EVOLVER Dashboard</h1><p>Henüz rapor bulunamadý. Lütfen önce testleri çalýþtýrýn.</p>"
        return Response(body, mimetype="text/html")

    rows = []
    for result in summary.get("results", []):
        status = result.get("status", "UNKNOWN")
        color = "#4caf50" if status == "PASSED" else "#f44336" if status in {"FAILED", "ERROR"} else "#9e9e9e"
        tags_str = ", ".join(result.get("tags", []))
        duration_value = result.get("duration_ms")
        duration = f"{duration_value:.2f}" if duration_value is not None else "-"
        details = html.escape(result.get("details") or "")
        rows.append(
            "<tr>"
            f"<td>{html.escape(result.get('name', 'N/A'))}</td>"
            f"<td style='color:{color};font-weight:bold;'>{html.escape(status)}</td>"
            f"<td>{duration}</td>"
            f"<td>{html.escape(tags_str)}</td>"
            f"<td><pre style='white-space:pre-wrap;font-size:0.8em;'>{details}</pre></td>"
            "</tr>"
        )
    rows_html = "\n".join(rows)

    body = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>ULU QA EVOLVER Dashboard</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      margin: 20px;
      background: #050505;
      color: #f5f5f5;
    }}
    h1 {{
      margin-bottom: 0.3em;
    }}
    .summary {{
      margin-bottom: 20px;
      padding: 10px 14px;
      border-radius: 8px;
      background: #101010;
      border: 1px solid #333;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
      font-size: 0.9em;
      background: #111;
    }}
    th, td {{
      border: 1px solid #333;
      padding: 8px;
    }}
    th {{
      background: #181818;
    }}
    tr:nth-child(even) {{
      background: #161616;
    }}
  </style>
</head>
<body>
  <h1>ULU QA EVOLVER Dashboard</h1>
  <div class="summary">
    <div>
      <span><strong>ENV:</strong> {html.escape(str(summary['env']))}</span>
      <span><strong>BASE_API_URL:</strong> {html.escape(str(summary['base_api_url']))}</span>
    </div>
    <div style="margin-top:6px;">
      <span><strong>Total:</strong> {summary['total']}</span>
      <span><strong>Passed:</strong> {summary['passed']}</span>
      <span><strong>Failed:</strong> {summary['failed']}</span>
      <span><strong>Error:</strong> {summary['error']}</span>
      <span><strong>Anomaly:</strong> {summary['anomaly_count']}</span>
      <span><strong>Total Time (ms):</strong> {summary['total_duration_ms']:.2f}</span>
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
    return Response(body, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
