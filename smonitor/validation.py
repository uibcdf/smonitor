from __future__ import annotations

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

    if event.get("code") is None and event.get("category") is None:
        errors.append("Missing code/category")

    return errors


def enforce_schema(event: Dict[str, Any], *, strict: bool = False) -> List[str]:
    errors = validate_event(event)
    if errors and strict:
        raise ValueError("; ".join(errors))
    return errors
