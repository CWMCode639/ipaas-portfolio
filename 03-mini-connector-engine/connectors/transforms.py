"""
transforms.py

Transforms reshape an event from the source app's format into whatever the
destination action needs. Here it's a simple template mapping: config says
"put {data.name} into a field called message", and we fill it in.
"""

import re

from .filters import get_field

_PLACEHOLDER = re.compile(r"\{([\w.]+)\}")


def _render_template(template: str, event: dict) -> str:
    def replace(match):
        path = match.group(1)
        value = get_field(event, path)
        return str(value) if value is not None else ""

    return _PLACEHOLDER.sub(replace, template)


def apply_transform(event: dict, transform_config: dict) -> dict:
    if not transform_config:
        return event

    mapping = transform_config.get("mapping", {})
    return {key: _render_template(template, event) for key, template in mapping.items()}
