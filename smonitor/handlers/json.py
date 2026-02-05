from __future__ import annotations

import json
from typing import Any, Dict


class JsonHandler:
    def __init__(self, path: str, mode: str = "a") -> None:
        self.path = path
        self.mode = mode
        self.name = "json"

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        payload = dict(event)
        payload["profile"] = profile
        with open(self.path, self.mode, encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
