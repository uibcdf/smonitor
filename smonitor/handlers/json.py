from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ..core.fingerprint import build_event_fingerprint

_NORMALIZED_EXTRA_KEYS = [
    "hint",
    "caller",
    "form",
    "requested_attribute",
    "resource",
    "provider",
    "operation",
    "retry_attempt",
    "retry_max",
    "retry_exhausted",
    "retry_delay_s",
    "failure_class",
    "last_failure_reason",
    "cause_exception_type",
    "cause_code",
    "causal_chain",
]


def _normalized_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    extra = event.get("extra") or {}
    normalized = {
        "level": event.get("level"),
        "message": event.get("message"),
        "source": event.get("source"),
        "code": event.get("code"),
        "category": event.get("category"),
        "exception_type": event.get("exception_type"),
        "tags": list(event.get("tags") or []),
        "fingerprint": event.get("fingerprint")
        or build_event_fingerprint(
            code=event.get("code"),
            source=event.get("source"),
            exception_type=event.get("exception_type"),
            extra=extra,
        ),
    }
    for key in _NORMALIZED_EXTRA_KEYS:
        if key in extra:
            normalized[key] = extra.get(key)
    return normalized


class JsonHandler:
    def __init__(self, path: str, mode: str = "a") -> None:
        self.path = path
        self.mode = mode
        self.name = "json"

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        payload = dict(event)
        payload["profile"] = profile
        payload["fingerprint"] = payload.get("fingerprint") or build_event_fingerprint(
            code=event.get("code"),
            source=event.get("source"),
            exception_type=event.get("exception_type"),
            extra=event.get("extra") or {},
        )
        # Provide a stable subset for external ingestion
        payload.setdefault("level", event.get("level"))
        payload.setdefault("message", event.get("message"))
        payload.setdefault("source", event.get("source"))
        payload.setdefault("code", event.get("code"))
        payload.setdefault("category", event.get("category"))
        payload["normalized"] = _normalized_payload(event)
        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(self.mode, encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")
