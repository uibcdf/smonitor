from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

_FINGERPRINT_EXTRA_KEYS = [
    "caller",
    "form",
    "requested_attribute",
    "resource",
    "provider",
    "operation",
    "retry_attempt",
    "retry_max",
    "retry_exhausted",
    "failure_class",
    "cause_exception_type",
    "cause_code",
]


def fingerprint_extra_subset(extra: Dict[str, Any] | None) -> Dict[str, Any]:
    payload = extra or {}
    subset: Dict[str, Any] = {}
    for key in _FINGERPRINT_EXTRA_KEYS:
        if key in payload:
            subset[key] = payload[key]
    return subset


def build_event_fingerprint(
    *,
    code: Any,
    source: Any,
    exception_type: Any,
    extra: Dict[str, Any] | None,
) -> str:
    base = {
        "code": code or "",
        "source": source or "",
        "exception_type": exception_type or "",
        "extra": fingerprint_extra_subset(extra),
    }
    raw = json.dumps(base, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
