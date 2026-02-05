from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Tuple


@dataclass
class PolicyState:
    counters: Dict[str, int] = field(default_factory=dict)
    last_seen: Dict[str, float] = field(default_factory=dict)


class PolicyEngine:
    """Policy engine for routing/filtering/transforms."""

    def __init__(self) -> None:
        self._routes: List[Dict[str, Any]] = []
        self._filters: List[Dict[str, Any]] = []
        self._state = PolicyState()

    def set_routes(self, routes: List[Dict[str, Any]]) -> None:
        self._routes = routes or []

    def set_filters(self, filters: List[Dict[str, Any]]) -> None:
        self._filters = filters or []

    def apply(self, event: Dict[str, Any], handlers: Iterable[Any]) -> Tuple[Dict[str, Any], List[Any]]:
        # Filters (rate limiting etc.)
        for rule in self._filters:
            when = rule.get("when", {})
            if not self._match(event, when):
                continue
            if rule.get("drop") is True:
                return event, []
            rate = rule.get("rate_limit")
            if rate and not self._allow_rate(event, rate):
                return event, []

        # Routing
        target_handlers = list(handlers)
        for rule in self._routes:
            when = rule.get("when", {})
            if not self._match(event, when):
                continue
            transform = rule.get("transform")
            if isinstance(transform, dict):
                event.update(transform)
            rename = rule.get("rename")
            if isinstance(rename, dict):
                for old, new in rename.items():
                    if old in event:
                        event[new] = event.pop(old)
            drop_fields = rule.get("drop_fields")
            if isinstance(drop_fields, list):
                for key in drop_fields:
                    event.pop(key, None)
            add_tags = rule.get("add_tags")
            if isinstance(add_tags, list):
                current = event.get("tags") or []
                if isinstance(current, list):
                    event["tags"] = list(dict.fromkeys(current + add_tags))
            names = rule.get("send_to") or []
            if names:
                target_handlers = [h for h in target_handlers if getattr(h, "name", None) in names or h.__class__.__name__ in names]
        return event, target_handlers

    def _allow_rate(self, event: Dict[str, Any], rate: str) -> bool:
        # rate format: "1/100" or "1/100@seconds" -> allow 1 of each 100 events per key
        try:
            window_s = None
            if "@" in rate:
                rate, window = rate.split("@", 1)
                try:
                    window_s = float(window)
                except ValueError:
                    window_s = None
            keep, total = rate.split("/")
            keep_n = int(keep)
            total_n = int(total)
        except Exception:
            return True
        if event.get("code"):
            key = f"{event.get('code')}|{event.get('source')}"
        else:
            key = event.get("message") or "__default__"
        from time import time

        now = time()
        if window_s is not None:
            last = self._state.last_seen.get(key, 0.0)
            if now - last > window_s:
                self._state.counters[key] = 0
            self._state.last_seen[key] = now

        count = self._state.counters.get(key, 0) + 1
        self._state.counters[key] = count
        return (count - 1) % total_n < keep_n

    def _match(self, event: Dict[str, Any], when: Dict[str, Any]) -> bool:
        for key, value in when.items():
            if key.endswith("_prefix"):
                field = key[:-7]
                if not self._op_prefix(event.get(field), value):
                    return False
                continue
            if isinstance(value, dict):
                if not self._match_ops(event.get(key), value):
                    return False
            else:
                field_value = event.get(key)
                if isinstance(field_value, list):
                    if value not in field_value:
                        return False
                else:
                    if field_value != value:
                        return False
        return True

    def _match_ops(self, field_value: Any, ops: Dict[str, Any]) -> bool:
        for op, val in ops.items():
            if op == "eq" and field_value != val:
                return False
            if op == "in" and field_value not in val:
                return False
            if op == "prefix" and not self._op_prefix(field_value, val):
                return False
            if op == "contains" and (field_value is None or val not in field_value):
                return False
            if op == "regex" and (field_value is None or re.search(val, str(field_value)) is None):
                return False
        return True

    def _op_prefix(self, field_value: Any, prefix: Any) -> bool:
        if field_value is None:
            return False
        return str(field_value).startswith(str(prefix))
