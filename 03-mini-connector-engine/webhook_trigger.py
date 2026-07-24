"""
webhook_trigger.py

Exposes the mini connector engine over HTTP: POST an event here and it runs
through every workflow file in workflows/, the same way a real iPaaS receives
a webhook and checks it against all of your configured automations.

Run it:
    python3 webhook_trigger.py

Then, in a second terminal:
    curl -X POST http://127.0.0.1:5001/event \
      -H "Content-Type: application/json" \
      -d @sample_events/sample_event.json
"""

import glob

from flask import Flask, jsonify, request

from engine import load_workflow, run_workflow

app = Flask(__name__)

WORKFLOW_PATHS = glob.glob("workflows/*.yaml")


@app.route("/event", methods=["POST"])
def receive_event():
    event = request.get_json(force=True, silent=True)
    if event is None:
        return jsonify(error="request body must be JSON"), 400

    results = []
    for path in WORKFLOW_PATHS:
        workflow = load_workflow(path)
        result = run_workflow(event, workflow)
        results.append({"workflow": path, **result})

    return jsonify(results)


if __name__ == "__main__":
    print(f"[webhook_trigger] loaded {len(WORKFLOW_PATHS)} workflow(s): {WORKFLOW_PATHS}")
    print("[webhook_trigger] listening on http://127.0.0.1:5001")
    app.run(port=5001)
