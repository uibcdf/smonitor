from __future__ import annotations

from typing import Any, Dict


class ConsoleHandler:
    def __init__(self, stream=None) -> None:
        import sys

        self._stream = stream or sys.stderr
        self.name = "console"

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        message = self._format(event, profile)
        self._stream.write(message + "\n")
        self._stream.flush()

    def _format(self, event: Dict[str, Any], profile: str) -> str:
        level = event.get("level") or "INFO"
        source = event.get("source") or ""
        message = event.get("message") or ""
        code = event.get("code")
        context = event.get("context") or {}

        if profile == "dev":
            ctx_chain = " -> ".join(context.get("chain", []))
            prefix = f"[{code}] " if code else ""
            return f"{prefix}{level} {source} | {message} | {ctx_chain}"
        if profile == "qa":
            prefix = f"[{code}] " if code else ""
            return f"{prefix}{level} {source} | {message}"
        if profile == "agent":
            return f"code={code} level={level} source={source} message={message}"
        if profile == "debug":
            ctx_chain = " -> ".join(context.get("chain", []))
            prefix = f"[{code}] " if code else ""
            return f"{prefix}{level} {source} | {message} | {ctx_chain}"
        # user (default)
        return f"{level}: {message}"
