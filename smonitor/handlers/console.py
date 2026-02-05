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
            hint = (event.get("extra") or {}).get("hint")
            hint_part = f" | Hint: {hint}" if hint else ""
            return f"{prefix}{level} {source} | {message} | {ctx_chain}{hint_part}"
        if profile == "qa":
            prefix = f"[{code}] " if code else ""
            return f"{prefix}{level} {source} | {message}"
        if profile == "agent":
            return f"code={code} level={level} source={source} message={message}"
        if profile == "debug":
            ctx_chain = " -> ".join(context.get("chain", []))
            prefix = f"[{code}] " if code else ""
            hint = (event.get("extra") or {}).get("hint")
            hint_part = f" | Hint: {hint}" if hint else ""
            return f"{prefix}{level} {source} | {message} | {ctx_chain}{hint_part}"
        # user (default)
        hint = (event.get("extra") or {}).get("hint")
        hint_part = f" | {hint}" if hint else ""
        return f"{level}: {message}{hint_part}"


class RichConsoleHandler(ConsoleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.name = "console_rich"
        try:
            from rich.console import Console
            from rich.theme import Theme
        except Exception as exc:  # pragma: no cover - fallback
            raise ImportError("rich is not installed") from exc
        theme = Theme(
            {
                "debug": "dim",
                "info": "cyan",
                "warning": "yellow",
                "error": "bold red",
            }
        )
        self._console = Console(theme=theme)

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        message = self._format(event, profile)
        level = (event.get("level") or "INFO").lower()
        style = "info"
        if level == "warning":
            style = "warning"
        elif level == "error":
            style = "error"
        elif level == "debug":
            style = "debug"
        self._console.print(message, style=style)
