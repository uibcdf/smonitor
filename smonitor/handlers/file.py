from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class FileHandler:
    def __init__(self, path: str, mode: str = "a") -> None:
        self.path = path
        self.mode = mode
        self.name = "file"

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        line = self._format(event, profile)
        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(self.mode, encoding="utf-8") as fh:
            fh.write(line + "\n")

    def _format(self, event: Dict[str, Any], profile: str) -> str:
        ts = event.get("timestamp") or datetime.utcnow().isoformat()
        level = event.get("level") or "INFO"
        source = event.get("source") or ""
        message = event.get("message") or ""
        code = event.get("code")
        context = event.get("context") or {}
        prefix = f"[{code}] " if code else ""
        message = str(message).replace("\n", "\\n")
        if profile == "user":
            return f"{ts} {level} | {message}"
        if profile == "qa":
            return f"{ts} {prefix}{level} {source} | {message}"
        if profile in {"dev", "debug"}:
            chain = " -> ".join(context.get("chain", []))
            hint = (event.get("extra") or {}).get("hint")
            hint_part = f" | Hint: {hint}" if hint else ""
            return f"{ts} {prefix}{level} {source} | {message} | {chain}{hint_part}"
        if profile == "agent":
            return f"{ts} code={code} level={level} source={source} message={message}"
        return f"{ts} {prefix}{level} {source} | {message}"
