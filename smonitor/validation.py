from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


REQUIRED_FIELDS = ["timestamp", "level", "message"]


def validate_event(event: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for key in REQUIRED_FIELDS:
        if key not in event or event.get(key) in (None, ""):
            errors.append(f"Missing required field: {key}")

    level = event.get("level")
    if level and level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        errors.append(f"Invalid level: {level}")

    timestamp = event.get("timestamp")
    if timestamp is not None:
        if not isinstance(timestamp, str):
            errors.append("timestamp must be a string in ISO format")
        else:
            try:
                datetime.fromisoformat(timestamp)
            except ValueError:
                errors.append("timestamp is not valid ISO format")

    tags = event.get("tags")
    if tags is not None:
        if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
            errors.append("tags must be a list of strings")

    extra = event.get("extra")
    if extra is not None and not isinstance(extra, dict):
        errors.append("extra must be a dict")

    context = event.get("context")
    if context is not None and not isinstance(context, dict):
        errors.append("context must be a dict")

    source = event.get("source")
    if source is not None and not isinstance(source, str):
        errors.append("source must be a string")

    code = event.get("code")
    if code is not None and not isinstance(code, str):
        errors.append("code must be a string")

    category = event.get("category")
    if category is not None and not isinstance(category, str):
        errors.append("category must be a string")

    if event.get("code") is None and event.get("category") is None:
        errors.append("Missing code/category")

    return errors


def enforce_schema(event: Dict[str, Any], *, strict: bool = False) -> List[str]:
    errors = validate_event(event)
    if errors and strict:
        raise ValueError("; ".join(errors))
    return errors
