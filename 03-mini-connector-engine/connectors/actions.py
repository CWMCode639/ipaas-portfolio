"""
actions.py

Actions are the "do something" step at the end of a workflow. Real iPaaS
platforms call a destination app's API here (post to Slack, create a row in
a spreadsheet, send an email). This demo keeps it local: writing to a file
stands in for "notify Slack" so the whole project runs with no external
accounts or API keys.
"""

import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def log_to_file(output, target: str = "action_log.txt"):
    path = BASE_DIR / target
    with open(path, "a") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {output}\n")
    return f"logged to {target}"


def print_action(output, **_kwargs):
    print(f"[action:print] {output}")
    return "printed"


ACTIONS = {
    "log_to_file": log_to_file,
    "print": print_action,
}


def run_action(action_config: dict, output):
    action_type = action_config.get("type")
    func = ACTIONS.get(action_type)
    if not func:
        raise ValueError(f"Unknown action type: {action_type}")

    target = action_config.get("target")
    if target:
        return func(output, target=target)
    return func(output)
