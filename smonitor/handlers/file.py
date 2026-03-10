from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .console import _format_extra_value


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
            extra = event.get("extra") or {}
            hint = extra.get("hint")
            hint_part = f" | Hint: {hint}" if hint else ""
            extras = []
            for key, value in extra.items():
                if key in {"hint", "smonitor", "title", "contract_warning", "schema_warning"}:
                    continue
                extras.append(f"{key}={_format_extra_value(value, profile=profile)}")
            extra_part = f" | {'; '.join(extras)}" if extras else ""
            return f"{ts} {prefix}{level} {source} | {message} | {chain}{hint_part}{extra_part}"
        if profile == "agent":
            return f"{ts} code={code} level={level} source={source} message={message}"
        return f"{ts} {prefix}{level} {source} | {message}"
