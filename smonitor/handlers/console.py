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
            extra = event.get("extra") or {}
            hint = extra.get("hint")
            cw = extra.get("contract_warning")
            sw = extra.get("schema_warning")
            hint_part = f" | Hint: {hint}" if hint else ""
            cw_part = f" | Contract: {cw}" if cw else ""
            sw_part = f" | Schema: {sw}" if sw else ""
            return f"{prefix}{level} {source} | {message} | {ctx_chain}{hint_part}{cw_part}{sw_part}"
        if profile == "qa":
            prefix = f"[{code}] " if code else ""
            return f"{prefix}{level} {source} | {message}"
        if profile == "agent":
            return f"code={code} level={level} source={source} message={message}"
        if profile == "debug":
            ctx_chain = " -> ".join(context.get("chain", []))
            prefix = f"[{code}] " if code else ""
            extra = event.get("extra") or {}
            hint = extra.get("hint")
            cw = extra.get("contract_warning")
            sw = extra.get("schema_warning")
            hint_part = f" | Hint: {hint}" if hint else ""
            cw_part = f" | Contract: {cw}" if cw else ""
            sw_part = f" | Schema: {sw}" if sw else ""
            return f"{prefix}{level} {source} | {message} | {ctx_chain}{hint_part}{cw_part}{sw_part}"
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
        level = (event.get("level") or "INFO").lower()
        style = "info"
        if level == "warning":
            style = "warning"
        elif level == "error":
            style = "error"
        elif level == "debug":
            style = "debug"

        if profile in {"dev", "debug", "qa"}:
            from rich.table import Table
            from rich.panel import Panel

            table = Table(show_header=True, header_style="bold")
            table.add_column("Level", style=style, width=8)
            table.add_column("Source", style="dim")
            table.add_column("Message")
            table.add_column("Code", style="dim", width=10)
            table.add_row(
                (event.get("level") or "INFO"),
                (event.get("source") or ""),
                (event.get("message") or ""),
                (event.get("code") or ""),
            )
            hint = (event.get("extra") or {}).get("hint")
            if hint:
                table.add_row("", "", f"Hint: {hint}", "")
            chain = (event.get("context") or {}).get("chain", [])
            if chain:
                table.add_row("", "", "Context: " + " -> ".join(chain), "")
            self._console.print(table)
            extra = event.get("extra") or {}
            hint = extra.get("hint")
            contract = extra.get("contract_warning")
            schema = extra.get("schema_warning")
            if hint or contract:
                body = []
                if hint:
                    body.append(f"Hint: {hint}")
                if contract:
                    body.append(f"Contract: {contract}")
                if schema:
                    body.append(f"Schema: {schema}")
                self._console.print(Panel("\n".join(body), title="Notes", style="dim"))
            return

        message = self._format(event, profile)
        self._console.print(message, style=style)
