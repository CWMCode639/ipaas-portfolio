"""
Lead Trigger Dashboard
----------------------
A minimal extension of the connector-engine pattern (trigger -> filter ->
transform -> action) that receives simulated Salesforce Lead events over
HTTP and shows them live on a dashboard, instead of (or in addition to)
posting to Slack.

Dependency-free (standard library only), same spirit as the rest of the
project.

Run:
    python3 lead_dashboard.py

Then open http://127.0.0.1:5002 in a browser, and in another terminal fire
a simulated Salesforce Lead trigger at it:

    curl -X POST http://127.0.0.1:5002/webhook/lead/salesforce \
      -H "Content-Type: application/json" \
      -d @sample_lead_event.json
"""

import json
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# In-memory store standing in for a database. Newest first.
LEADS = []

ALLOWED_SOURCES = {"Web", "Webinar", "Referral", "Partner"}


def passes_filter(lead: dict) -> bool:
    """Filter step: only forward leads that look like real, open leads."""
    status_ok = "open" in lead.get("Status", "").lower()
    source_ok = lead.get("LeadSource") in ALLOWED_SOURCES
    return status_ok and source_ok


def transform(lead: dict, accepted: bool) -> dict:
    """Transform step: reshape the raw Salesforce Lead payload into a row
    the dashboard can render."""
    name = " ".join(filter(None, [lead.get("FirstName"), lead.get("LastName")])) or "Unknown"
    return {
        "id": lead.get("Id", f"local-{len(LEADS) + 1}"),
        "name": name,
        "company": lead.get("Company", "-"),
        "email": lead.get("Email", "-"),
        "source": lead.get("LeadSource", "-"),
        "status": lead.get("Status", "-"),
        "accepted": accepted,
        "received_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }


def notify_slack(row: dict) -> None:
    """Action step (kept from the original project): log accepted leads
    to a flat file, standing in for a real Slack post."""
    with open("slack_log.txt", "a") as f:
        f.write(
            f"[{row['received_at']}] New lead: {row['name']} "
            f"({row['company']}) via {row['source']}\n"
        )


DASHBOARD_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Lead Trigger Dashboard</title>
<style>
  body { font-family: -apple-system, Segoe UI, sans-serif; background: #f7f7f8; margin: 0; padding: 24px; color: #1a1a1a; }
  h1 { font-size: 20px; margin-bottom: 4px; }
  .sub { color: #666; font-size: 13px; margin-bottom: 20px; }
  .stats { display: flex; gap: 16px; margin-bottom: 20px; }
  .card { background: white; border-radius: 8px; padding: 12px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .card .num { font-size: 22px; font-weight: 600; }
  .card .label { font-size: 12px; color: #666; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  th, td { text-align: left; padding: 10px 14px; font-size: 13px; border-bottom: 1px solid #eee; }
  th { background: #fafafa; color: #555; font-weight: 600; }
  .badge { padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 600; }
  .accepted { background: #e3f8e3; color: #1a7a1a; }
  .filtered { background: #f1f1f1; color: #888; }
  button { border: none; background: #1a1a1a; color: white; padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; }
</style>
</head>
<body>
  <h1>Lead Trigger Dashboard</h1>
  <div class="sub">Listening for simulated Salesforce Lead triggers on <code>/webhook/lead/salesforce</code> &mdash; auto-refreshes every 3s.</div>

  <div class="stats">
    <div class="card"><div class="num" id="total">0</div><div class="label">Total received</div></div>
    <div class="card"><div class="num" id="accepted-count">0</div><div class="label">Passed filter</div></div>
    <div class="card"><div class="num" id="filtered-count">0</div><div class="label">Filtered out</div></div>
    <div class="card"><button onclick="clearLeads()">Clear</button></div>
  </div>

  <table>
    <thead>
      <tr><th>Received</th><th>Status</th><th>Name</th><th>Company</th><th>Email</th><th>Source</th><th>SF Status</th></tr>
    </thead>
    <tbody id="rows"></tbody>
  </table>

<script>
async function refresh() {
  const res = await fetch('/api/leads');
  const leads = await res.json();
  document.getElementById('total').textContent = leads.length;
  document.getElementById('accepted-count').textContent = leads.filter(l => l.accepted).length;
  document.getElementById('filtered-count').textContent = leads.filter(l => !l.accepted).length;

  document.getElementById('rows').innerHTML = leads.map(l => `
    <tr>
      <td>${l.received_at}</td>
      <td><span class="badge ${l.accepted ? 'accepted' : 'filtered'}">${l.accepted ? 'Accepted' : 'Filtered'}</span></td>
      <td>${l.name}</td>
      <td>${l.company}</td>
      <td>${l.email}</td>
      <td>${l.source}</td>
      <td>${l.status}</td>
    </tr>
  `).join('');
}

async function clearLeads() {
  await fetch('/api/leads/clear', { method: 'POST' });
  refresh();
}

refresh();
setInterval(refresh, 3000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # keep stdout quiet

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status, html):
        body = html.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self._send_html(200, DASHBOARD_HTML)
        elif self.path == "/api/leads":
            self._send_json(200, LEADS)
        else:
            self._send_json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"

        if self.path == "/webhook/lead/salesforce":
            try:
                payload = json.loads(raw or b"{}")
            except json.JSONDecodeError:
                self._send_json(400, {"error": "invalid JSON"})
                return

            accepted = passes_filter(payload)
            row = transform(payload, accepted)
            LEADS.insert(0, row)
            if accepted:
                notify_slack(row)

            self._send_json(200, {"status": "accepted" if accepted else "filtered_out", "lead": row})

        elif self.path == "/api/leads/clear":
            LEADS.clear()
            self._send_json(200, {"status": "cleared"})

        else:
            self._send_json(404, {"error": "not found"})


if __name__ == "__main__":
    port = 5002
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Lead dashboard running at http://127.0.0.1:{port}")
    server.serve_forever()
