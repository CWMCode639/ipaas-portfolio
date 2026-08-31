# 04 — Lead Trigger Dashboard

A live extension of the trigger -> filter -> transform -> action pattern from
project 03, swapping the file/CLI-based workflow for an HTTP endpoint and a
real-time dashboard. Simulates the most common Salesforce integration
pattern: a Lead is created or updated, and downstream systems react to it.

```
trigger  ->  filter  ->  transform  ->  action
```

- **Trigger** — a POST request hits `/webhook/lead/salesforce`, standing in
  for a Salesforce Outbound Message, Platform Event, or Flow/Apex HTTP
  callout firing on Lead create/update.
- **Filter** — only leads with an "Open" status and an allowed `LeadSource`
  (Web, Webinar, Referral, Partner) are treated as real leads worth acting
  on; everything else is marked filtered out.
- **Transform** — the raw Salesforce-shaped payload (`FirstName`,
  `LastName`, `Company`, `Email`, `LeadSource`, `Status`) is reshaped into a
  row the dashboard can render.
- **Action** — accepted leads are appended to `slack_log.txt` (same
  simulated-Slack pattern as project 03) and pushed into an in-memory store
  that the dashboard polls.

No external dependencies — the server is built entirely on Python's
standard library (`http.server`), no Flask/pip install required.

## Run it

```
python lead_dashboard.py
```

Open `http://127.0.0.1:5002` in a browser. In a second terminal, from the
same folder, simulate a Salesforce Lead trigger:

```
curl.exe -X POST http://127.0.0.1:5002/webhook/lead/salesforce -H "Content-Type: application/json" -d "@sample_lead_event.json"
```

PowerShell alternative (avoids curl/alias quoting issues):

```
Invoke-RestMethod -Uri http://127.0.0.1:5002/webhook/lead/salesforce -Method Post -ContentType "application/json" -InFile sample_lead_event.json
```

The dashboard auto-refreshes every 3 seconds and shows the lead as
**Accepted**. Edit `sample_lead_event.json` — set `LeadSource` to something
outside the allowed list, or remove "Open" from `Status` — and resend to
see a **Filtered** row instead.

## Files

- `lead_dashboard.py` — the trigger endpoint, filter/transform logic, and
  dashboard UI, all in one dependency-free file.
- `sample_lead_event.json` — an example Salesforce Lead payload to POST at
  the trigger endpoint.
- `slack_log.txt` — generated at runtime; one line per accepted lead.

## Extending it

- Point a real Salesforce Outbound Message or Platform Event subscriber at
  this endpoint (once deployed somewhere reachable) to replace the
  simulated trigger with a live one.
- Add an `on_failure` path that retries or dead-letters events if the
  downstream action fails, matching the resilience patterns real iPaaS
  tools (Zapier, n8n) build in.
- Swap the in-memory `LEADS` list for a small SQLite file if you want the
  dashboard to persist across restarts.
