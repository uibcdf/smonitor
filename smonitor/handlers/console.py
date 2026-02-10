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

        if profile in {"dev", "debug"}:
            ctx_chain = " \u276f ".join(context.get("chain", []))
            prefix = f"[{code}] " if code else ""
            extra = event.get("extra") or {}
            hint = extra.get("hint")
            hint_part = f" | Hint: {hint}" if hint else ""
            
            output = f"{prefix}{level} {source} | {message} | {ctx_chain}{hint_part}"
            
            # Show arguments for ERRORs if captured in frames
            if level == "ERROR" and "frames" in context:
                args_details = []
                for frame in context["frames"]:
                    if frame.get("args"):
                        func_name = f"{frame['module']}.{frame['function']}"
                        args_str = str(frame["args"])
                        args_details.append(f"  \u2514\u2500 {func_name}({args_str})")
                if args_details:
                    output += "\n" + "\n".join(args_details)
            
            return output
        if profile == "qa":
            prefix = f"[{code}] " if code else ""
            return f"{prefix}{level} {source} | {message}"
        if profile == "agent":
            # Plain machine-readable format
            return f"code={code} level={level} source={source} message={message}"
        
        # user (default)
        hint = (event.get("extra") or {}).get("hint")
        hint_part = f" (Hint: {hint})" if hint else ""
        return f"{level}: {message}{hint_part}"


class RichConsoleHandler(ConsoleHandler):
    def __init__(self) -> None:
        super().__init__()
        self.name = "console_rich"
        try:
            from rich.console import Console
            from rich.theme import Theme
        except ImportError as exc:
            raise ImportError("rich is not installed") from exc
            
        theme = Theme(
            {
                "level.debug": "dim italic gray62",
                "level.info": "bold cyan",
                "level.warning": "bold orange3",
                "level.error": "bold bright_red",
                "ts": "dim white",
                "source": "italic magenta",
                "code": "bold reverse blue",
                "path": "dim cyan",
                "hint.label": "bold green",
                "hint.text": "green",
                "msg.user": "white",
                "msg.tech": "bold white",
            }
        )
        self._console = Console(theme=theme)

    def handle(self, event: Dict[str, Any], *, profile: str = "user") -> None:
        level = (event.get("level") or "INFO").upper()
        style = f"level.{level.lower()}"
        
        # Format Timestamp
        ts = ""
        if timestamp := event.get("timestamp"):
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                ts = dt.strftime("%H:%M:%S")
            except: ts = ""

        if profile == "user":
            self._handle_user(event, level, style, ts)
        elif profile in {"dev", "debug", "qa"}:
            self._handle_technical(event, level, style, ts)
        else:
            # Fallback for agent or others
            msg = self._format(event, profile)
            self._console.print(msg)

    def _handle_user(self, event: Dict[str, Any], level: str, style: str, ts: str) -> None:
        from rich.panel import Panel
        from rich.text import Text
        from rich.box import ROUNDED

        # Icon mapping
        icons = {"DEBUG": "⚙", "INFO": "ℹ", "WARNING": "⚠", "ERROR": "✘"}
        icon = icons.get(level, "•")

        # Header: [LEVEL] HH:MM:SS
        title = Text.assemble(
            (f" {icon} {level} ", f"white on {self._console.get_style(style).color.name}"),
            (f" {ts} ", "ts")
        )

        # Content
        content = Text("\n", end="")
        content.append(event.get("message") or "", style="msg.user")
        
        if hint := (event.get("extra") or {}).get("hint"):
            content.append("\n\n")
            content.append(" \u25c6 ", style="hint.label")
            content.append("Hint: ", style="hint.label")
            content.append(hint, style="hint.text")

        # Footer: Path
        footer = None
        if chain := (event.get("context") or {}).get("chain", []):
            footer = Text(" \u276f ".join(chain), style="path")

        self._console.print(
            Panel(
                content,
                title=title,
                title_align="left",
                subtitle=footer,
                subtitle_align="right",
                border_style=style,
                box=ROUNDED,
                padding=(0, 2, 1, 2)
            )
        )

    def _handle_technical(self, event: Dict[str, Any], level: str, style: str, ts: str) -> None:
        from rich.table import Table
        from rich.text import Text
        from rich.rule import Rule

        # Top Rule with Metadata
        source = event.get("source") or "unknown"
        code_tag = f" {event.get('code')} " if event.get('code') else ""
        
        header = Text.assemble(
            (f" {level} ", style),
            (f" {ts} ", "ts"),
            (f" {source} ", "source"),
            (f" {code_tag} ", "code") if code_tag else ""
        )
        
        self._console.print(Rule(header, style=style, align="left"))

        # Message (The core of the event)
        self._console.print(f" [msg.tech]{event.get('message')}[/]")

        # Details Grid
        details = Table.grid(padding=(0, 2))
        details.add_column(justify="right", style="dim")
        details.add_column()

        extra = event.get("extra") or {}
        if hint := extra.get("hint"):
            details.add_row("hint", f"[hint.text]{hint}[/]")
        
        if chain := (event.get("context") or {}).get("chain", []):
            path_str = " [dim]\u276f[/] ".join([f"[path]{c}[/]" for c in chain])
            details.add_row("path", path_str)

        for k, v in extra.items():
            if k in {"hint", "smonitor", "title", "contract_warning", "schema_warning"}: continue
            details.add_row(k, str(v))

        # Specialized warnings
        if cw := extra.get("contract_warning"):
            details.add_row("contract", f"[bold bright_red]{cw}[/]")
        if sw := extra.get("schema_warning"):
            details.add_row("schema", f"[bold bright_red]{sw}[/]")

        if details.row_count > 0:
            self._console.print(details)
        
        # Bottom spacing
        self._console.print()
