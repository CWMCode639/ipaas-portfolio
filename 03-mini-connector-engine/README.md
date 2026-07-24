# 03 — Mini Connector Engine

This ties projects 1 and 2 together into the pattern every iPaaS platform is
built on:

```
trigger  ->  filter  ->  transform  ->  action
```

- **Trigger** — an event comes in (here, either a JSON file or a POSTed
  webhook) and is checked against the workflow's `event_type`.
- **Filter** — should this *specific* event continue? (e.g. only `plan: pro` users)
- **Transform** — reshape the event into whatever the action needs (build a message string from event fields).
- **Action** — do something with the result. To keep this dependency-free, "notify Slack" is simulated by appending a line to `slack_log.txt`.

Workflows are defined declaratively in YAML (see `workflows/sample_workflow.yaml`) rather than hard-coded — the same way Zapier/n8n let you configure a workflow instead of writing code for each one.

## Run it — no server, just a file

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python3 engine.py --workflow workflows/sample_workflow.yaml --event sample_events/sample_event.json
```

This event has `plan: pro`, so it passes the filter and you'll see a new line appended to `slack_log.txt`. Try it with `sample_events/sample_event_free_plan.json` instead — it gets `filtered_out` since the plan isn't `pro`.

## Run it — as an HTTP trigger

```
python3 webhook_trigger.py
```

In a second terminal:

```
curl -X POST http://127.0.0.1:5001/event \
  -H "Content-Type: application/json" \
  -d @sample_events/sample_event.json
```

## Writing your own workflow

Copy `workflows/sample_workflow.yaml`, change the `trigger.event_type`, `filter`, `transform.mapping`, and `action`, then point `engine.py --workflow` (or drop the file in `workflows/` for `webhook_trigger.py` to pick up automatically).

## Files

- `engine.py` — loads a workflow and runs a single event through it.
- `webhook_trigger.py` — HTTP endpoint that runs incoming events through every workflow in `workflows/`.
- `connectors/filters.py`, `connectors/transforms.py`, `connectors/actions.py` — the building blocks each workflow step uses.
- `workflows/sample_workflow.yaml` — an example workflow definition.
- `sample_events/` — example event payloads to test with.
