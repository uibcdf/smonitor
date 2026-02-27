import types

from smonitor.handlers.console import RichConsoleHandler


def _install_fake_rich(monkeypatch):
    rich = types.ModuleType("rich")
    console_mod = types.ModuleType("rich.console")
    theme_mod = types.ModuleType("rich.theme")
    box_mod = types.ModuleType("rich.box")
    panel_mod = types.ModuleType("rich.panel")
    text_mod = types.ModuleType("rich.text")
    rule_mod = types.ModuleType("rich.rule")
    table_mod = types.ModuleType("rich.table")

    class _Color:
        name = "blue"

    class _Style:
        color = _Color()

    class Console:
        def __init__(self, theme=None):
            self.theme = theme
            self.calls = []

        def get_style(self, style):
            return _Style()

        def print(self, *args, **kwargs):
            self.calls.append((args, kwargs))

    class Theme(dict):
        pass

    class Text:
        def __init__(self, text="", end=None, style=None):
            self.value = str(text)

        @classmethod
        def assemble(cls, *parts):
            out = cls("")
            for part in parts:
                if isinstance(part, tuple):
                    out.value += str(part[0])
                else:
                    out.value += str(part)
            return out

        def append(self, text, style=None):
            self.value += str(text)

        def __str__(self):
            return self.value

    class Panel:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class Rule:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    class Table:
        def __init__(self):
            self.rows = []

        @classmethod
        def grid(cls, padding=(0, 0)):
            return cls()

        def add_column(self, **kwargs):
            return None

        def add_row(self, *args):
            self.rows.append(args)

        @property
        def row_count(self):
            return len(self.rows)

    console_mod.Console = Console
    theme_mod.Theme = Theme
    box_mod.ROUNDED = object()
    panel_mod.Panel = Panel
    text_mod.Text = Text
    rule_mod.Rule = Rule
    table_mod.Table = Table

    monkeypatch.setitem(__import__("sys").modules, "rich", rich)
    monkeypatch.setitem(__import__("sys").modules, "rich.console", console_mod)
    monkeypatch.setitem(__import__("sys").modules, "rich.theme", theme_mod)
    monkeypatch.setitem(__import__("sys").modules, "rich.box", box_mod)
    monkeypatch.setitem(__import__("sys").modules, "rich.panel", panel_mod)
    monkeypatch.setitem(__import__("sys").modules, "rich.text", text_mod)
    monkeypatch.setitem(__import__("sys").modules, "rich.rule", rule_mod)
    monkeypatch.setitem(__import__("sys").modules, "rich.table", table_mod)


def test_rich_console_handler_user_and_technical_paths(monkeypatch):
    _install_fake_rich(monkeypatch)
    handler = RichConsoleHandler()
    handler.handle(
        {
            "level": "WARNING",
            "message": "user-msg",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "extra": {"hint": "do"},
            "context": {"chain": ["a", "b"]},
        },
        profile="user",
    )
    handler.handle(
        {
            "level": "ERROR",
            "message": "tech-msg",
            "source": "pkg.mod",
            "code": "E1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "extra": {"hint": "fix", "contract_warning": "cw", "x": 1},
            "context": {"chain": ["c"]},
        },
        profile="dev",
    )
    assert handler._console.calls


def test_rich_console_handler_fallback_path(monkeypatch):
    _install_fake_rich(monkeypatch)
    handler = RichConsoleHandler()
    handler.handle(
        {"level": "INFO", "source": "s", "message": "m", "code": "C"},
        profile="agent",
    )
    assert handler._console.calls
