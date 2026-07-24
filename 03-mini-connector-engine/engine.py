"""
engine.py

The core of the mini connector engine: loads a workflow definition
(trigger + filter + transform + action) from YAML and runs an incoming event
through it. This is a tiny version of what Zapier calls a "Zap" or n8n calls
a "workflow".

Run against a sample event file, no server needed:
    python3 engine.py --workflow workflows/sample_workflow.yaml --event sample_events/sample_event.json

Or start the HTTP trigger and POST events to it (see webhook_trigger.py).
"""

import argparse
import json

import yaml

from connectors.actions import run_action
from connectors.filters import apply_filter
from connectors.transforms import apply_transform


def load_workflow(path: str) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def run_workflow(event: dict, workflow: dict) -> dict:
    # 1. Trigger check: does this event even match what this workflow listens for?
    trigger = workflow.get("trigger", {})
    expected_type = trigger.get("event_type")
    if expected_type and event.get("type") != expected_type:
        return {
            "status": "skipped",
            "reason": f"event type '{event.get('type')}' does not match trigger '{expected_type}'",
        }

    # 2. Filter: should this specific event continue?
    if not apply_filter(event, workflow.get("filter")):
        return {"status": "filtered_out"}

    # 3. Transform: reshape the event into whatever the action needs.
    transformed = apply_transform(event, workflow.get("transform"))

    # 4. Action: do something with the result.
    action_config = workflow.get("action")
    if not action_config:
        return {"status": "no_action_configured", "transformed": transformed}

    output = transformed.get("message", transformed) if isinstance(transformed, dict) else transformed
    result = run_action(action_config, output)

    return {"status": "completed", "transformed": transformed, "action_result": result}


def main():
    parser = argparse.ArgumentParser(description="Run a single event through a workflow")
    parser.add_argument("--workflow", default="workflows/sample_workflow.yaml")
    parser.add_argument("--event", default="sample_events/sample_event.json")
    args = parser.parse_args()

    workflow = load_workflow(args.workflow)
    with open(args.event) as f:
        event = json.load(f)

    result = run_workflow(event, workflow)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
