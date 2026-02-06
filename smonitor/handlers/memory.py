from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional


class MemoryHandler:
    def __init__(self, max_events: Optional[int] = None) -> None:
        self.name = "memory"
        self.max_events = max_events
        self.events: List[Dict[str, Any]] = []

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        payload = deepcopy(event)
        payload["profile"] = profile
        self.events.append(payload)
        if self.max_events is not None and self.max_events > 0:
            if len(self.events) > self.max_events:
                self.events.pop(0)
