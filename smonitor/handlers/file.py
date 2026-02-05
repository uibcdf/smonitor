from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional


class FileHandler:
    def __init__(self, path: str, mode: str = "a") -> None:
        self.path = path
        self.mode = mode
        self.name = "file"

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        line = self._format(event, profile)
        with open(self.path, self.mode, encoding="utf-8") as fh:
            fh.write(line + "\n")

    def _format(self, event: Dict[str, Any], profile: str) -> str:
        ts = event.get("timestamp") or datetime.utcnow().isoformat()
        level = event.get("level") or "INFO"
        source = event.get("source") or ""
        message = event.get("message") or ""
        code = event.get("code")
        prefix = f"[{code}] " if code else ""
        return f"{ts} {prefix}{level} {source} | {message}"
