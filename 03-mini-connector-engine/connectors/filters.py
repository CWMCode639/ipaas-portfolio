"""
filters.py

Filters decide whether an event should keep moving through a workflow.
Every real iPaaS has some version of this (Zapier calls it a "Filter" step).
"""


def get_field(obj: dict, dotted_path: str):
    """Look up event['data']['plan'] using the string 'data.plan'."""
    current = obj
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def apply_filter(event: dict, filter_config: dict) -> bool:
    """Returns True if the event should continue through the workflow."""
    if not filter_config:
        return True  # no filter configured = everything passes

    field = filter_config.get("field")
    operator = filter_config.get("operator", "equals")
    expected = filter_config.get("value")
    actual = get_field(event, field)

    if operator == "equals":
        return actual == expected
    if operator == "not_equals":
        return actual != expected
    if operator == "exists":
        return actual is not None
    if operator == "contains":
        return expected in (actual or "")

    raise ValueError(f"Unknown filter operator: {operator}")
