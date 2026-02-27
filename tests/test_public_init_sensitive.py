import smonitor
from smonitor.core.manager import get_manager


def test_configure_adds_rich_handler_when_theme_rich(monkeypatch):
    manager = get_manager()
    manager._handlers = []

    class _FakeRich:
        name = "console_rich"

        def handle(self, *args, **kwargs):
            return None

    monkeypatch.setattr(smonitor, "RichConsoleHandler", _FakeRich)
    smonitor.configure(theme="rich")
    assert manager._handlers
    assert manager._handlers[0].name == "console_rich"
