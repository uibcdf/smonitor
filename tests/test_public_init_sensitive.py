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


def test_configure_strict_config_raises_for_invalid_project(monkeypatch):
    monkeypatch.setattr(smonitor, "load_project_config", lambda *a, **k: {"SMONITOR": {}})
    monkeypatch.setattr(smonitor, "load_env_config", lambda: {})
    monkeypatch.setattr(
        smonitor,
        "build_effective_config",
        lambda project, env: {"strict_config": True},
    )
    monkeypatch.setattr(smonitor, "validate_project_config", lambda cfg: ["bad-config"])
    monkeypatch.setattr(smonitor, "extract_policy", lambda cfg: {"routes": [], "filters": []})
    monkeypatch.setattr(smonitor, "extract_codes", lambda cfg: None)
    monkeypatch.setattr(smonitor, "extract_signals", lambda cfg: None)
    try:
        smonitor.configure(handlers=[])
    except ValueError as exc:
        assert "Invalid _smonitor.py" in str(exc)
    else:
        raise AssertionError("Expected ValueError when strict_config is enabled")


def test_configure_routes_and_filters_overrides(monkeypatch):
    class _FakeManager:
        def __init__(self):
            self._handlers = []
            self.called = None

        def get_codes(self):
            return {}

        def get_signals(self):
            return {}

        def add_handler(self, handler):
            self._handlers.append(handler)

        def configure(self, **kwargs):
            self.called = kwargs
            return self

    fake = _FakeManager()
    monkeypatch.setattr(smonitor, "get_manager", lambda: fake)
    monkeypatch.setattr(smonitor, "load_project_config", lambda *a, **k: {})
    monkeypatch.setattr(smonitor, "load_env_config", lambda: {})
    monkeypatch.setattr(smonitor, "build_effective_config", lambda project, env: {})
    monkeypatch.setattr(smonitor, "validate_project_config", lambda cfg: [])
    monkeypatch.setattr(
        smonitor,
        "extract_policy",
        lambda cfg: {
            "routes": [{"when": {"level": "ERROR"}}],
            "filters": [{"when": {"code": "X"}}],
        },
    )
    monkeypatch.setattr(smonitor, "extract_codes", lambda cfg: None)
    monkeypatch.setattr(smonitor, "extract_signals", lambda cfg: None)
    routes = [{"when": {"level": "WARNING"}}]
    filters = [{"when": {"code": "Y"}, "drop": True}]
    out = smonitor.configure(handlers=[], routes=routes, filters=filters)
    assert out is fake
    assert fake.called["routes"] == routes
    assert fake.called["filters"] == filters


def test_configure_strict_config_param_overrides_effective(monkeypatch):
    class _FakeManager:
        def __init__(self):
            self._handlers = []
            self.called = None

        def get_codes(self):
            return {}

        def get_signals(self):
            return {}

        def add_handler(self, handler):
            self._handlers.append(handler)

        def configure(self, **kwargs):
            self.called = kwargs
            return self

    fake = _FakeManager()
    monkeypatch.setattr(smonitor, "get_manager", lambda: fake)
    monkeypatch.setattr(smonitor, "load_project_config", lambda *a, **k: {})
    monkeypatch.setattr(smonitor, "load_env_config", lambda: {})
    monkeypatch.setattr(
        smonitor,
        "build_effective_config",
        lambda project, env: {"strict_config": True, "profile": "qa"},
    )
    monkeypatch.setattr(smonitor, "validate_project_config", lambda cfg: ["would-fail"])
    monkeypatch.setattr(smonitor, "extract_policy", lambda cfg: {"routes": [], "filters": []})
    monkeypatch.setattr(smonitor, "extract_codes", lambda cfg: None)
    monkeypatch.setattr(smonitor, "extract_signals", lambda cfg: None)

    out = smonitor.configure(strict_config=False, handlers=[])
    assert out is fake
    assert "strict_config" not in fake.called
