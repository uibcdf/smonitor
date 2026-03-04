import smonitor
from smonitor.core.manager import get_manager
from smonitor.policy.engine import PolicyEngine


def test_manager_strict_signals_raises_when_code_missing_and_no_contract():
    # Force WARNING events through threshold gates so strict_signals is exercised.
    smonitor.configure(
        profile="dev",
        level="DEBUG",
        strict_signals=True,
        handlers=[],
        signals={},
        silence=[],
    )
    try:
        smonitor.emit("WARNING", "x", source="pkg.fn", code=None, extra={})
    except ValueError as exc:
        assert "Missing code for event" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_manager_recent_events_limit_zero_and_negative():
    manager = smonitor.configure(profile="user", handlers=[], event_buffer_size=5)
    smonitor.emit("WARNING", "x", source="s", code="C")
    assert manager.recent_events(0) == []
    assert manager.recent_events(-1) == []


def test_manager_report_ignores_bad_profiling_hooks():
    manager = smonitor.configure(profile="user", handlers=[], profiling_hooks=[])

    def _bad():
        raise RuntimeError("boom")

    def _nondict():
        return "not-dict"

    def _good():
        return {"ok": True}

    manager.configure(profiling_hooks=[_bad, _nondict, _good])
    rep = manager.report()
    assert rep["profiling_meta"]["ok"] is True


def test_manager_setup_default_handler_rich_fallback(monkeypatch):
    manager = get_manager()
    manager._handlers = []
    manager.configure(profile="user", handlers=[], theme="rich")

    class _Boom:
        def __init__(self):
            raise RuntimeError("no-rich")

    monkeypatch.setattr("smonitor.handlers.console.RichConsoleHandler", _Boom)
    manager._handlers = []
    manager._setup_default_handler()
    assert manager._handlers
    assert manager._handlers[0].name == "console"


def test_policy_match_ops_negative_paths():
    engine = PolicyEngine()
    assert engine._match_ops("x", {"eq": "y"}) is False
    assert engine._match_ops("x", {"in": ["a", "b"]}) is False
    assert engine._match_ops("x", {"prefix": "yy"}) is False
    assert engine._match_ops(None, {"contains": "x"}) is False
    assert engine._match_ops("abc", {"regex": r"^z+$"}) is False


def test_policy_rate_limit_bad_window_is_tolerated():
    engine = PolicyEngine()
    engine.set_filters([{"when": {"code": "X"}, "rate_limit": "1/2@bad"}])
    event = {"code": "X"}
    _, hs = engine.apply(event, [object()])
    assert hs


def test_manager_configure_disable_logging_with_warnings_enabled(monkeypatch):
    manager = get_manager()
    manager.configure(handlers=[])
    calls = []
    monkeypatch.setattr(
        "smonitor.emitters.logging.disable_logging",
        lambda: calls.append("disable_logging"),
    )
    monkeypatch.setattr(
        "smonitor.emitters.warnings.enable_warnings",
        lambda: calls.append("enable_warnings"),
    )
    monkeypatch.setattr(
        "smonitor.emitters.warnings.disable_warnings",
        lambda: calls.append("disable_warnings"),
    )
    monkeypatch.setattr(
        "smonitor.emitters.exceptions.disable_exceptions",
        lambda: calls.append("disable_exceptions"),
    )
    manager.configure(
        capture_logging=False,
        capture_warnings=True,
        capture_exceptions=False,
        handlers=[],
    )
    assert "disable_logging" in calls
    assert "enable_warnings" in calls
    assert "disable_exceptions" in calls


def test_manager_configure_disable_logging_with_warnings_disabled(monkeypatch):
    manager = get_manager()
    manager.configure(handlers=[])
    calls = []
    monkeypatch.setattr(
        "smonitor.emitters.logging.disable_logging",
        lambda: calls.append("disable_logging"),
    )
    monkeypatch.setattr(
        "smonitor.emitters.warnings.disable_warnings",
        lambda: calls.append("disable_warnings"),
    )
    monkeypatch.setattr(
        "smonitor.emitters.exceptions.enable_exceptions",
        lambda: calls.append("enable_exceptions"),
    )
    manager.configure(
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=True,
        handlers=[],
    )
    assert "disable_logging" in calls
    assert "disable_warnings" in calls
    assert "enable_exceptions" in calls


def test_manager_resolve_hint_selection_for_profiles():
    manager = get_manager()
    manager.configure(
        handlers=[],
        codes={
            "C1": {
                "qa_hint": "qa-hint",
                "dev_hint": "dev-hint",
            }
        },
    )
    manager.configure(profile="qa", handlers=[])
    _, hint = manager.resolve("", code="C1", extra={})
    assert hint == "qa-hint"

    manager.configure(profile="dev", handlers=[])
    _, hint = manager.resolve("", code="C1", extra={})
    assert hint == "dev-hint"


def test_manager_resolve_hint_template_format_error_is_tolerated():
    manager = get_manager()
    manager.configure(
        profile="dev",
        handlers=[],
        codes={"C2": {"dev_hint": "hint {missing}"}},
    )
    _, hint = manager.resolve("", code="C2", extra={"ok": "x"})
    assert hint == "hint {missing}"


def test_manager_apply_config_dict_ignores_falsy_optional_blocks():
    manager = get_manager()
    manager.configure(profile="user", handlers=[])
    manager._apply_config_dict(
        {
            "SMONITOR": {"level": "INFO"},
            "PROFILE": "",
            "ROUTES": [],
            "FILTERS": [],
            "CODES": {},
            "SIGNALS": {},
        }
    )
    assert manager.config.level == "INFO"
    # PROFILE is falsy, so it should not overwrite current profile.
    assert manager.config.profile == "user"


def test_manager_setup_default_handler_rich_success(monkeypatch):
    manager = get_manager()
    manager._handlers = []
    manager.configure(theme="rich", handlers=[])

    class _Rich:
        name = "rich-ok"

        def handle(self, *args, **kwargs):
            return None

    monkeypatch.setattr("smonitor.handlers.console.RichConsoleHandler", _Rich)
    manager._setup_default_handler()
    assert manager._handlers[0].name == "rich-ok"


def test_manager_remove_handler_present_and_recent_events_limit_positive():
    manager = get_manager()
    manager.configure(handlers=[], event_buffer_size=10)

    class _H:
        def handle(self, *args, **kwargs):
            return None

    h = _H()
    manager.add_handler(h)
    manager.remove_handler(h)
    assert h not in manager._handlers

    smonitor.emit("WARNING", "x", source="pkg.mod", code="C")
    assert len(manager.recent_events(1)) == 1


def test_manager_record_timing_no_buffer_and_trim_behavior():
    manager = get_manager()
    manager.configure(handlers=[], profiling_buffer_size=0)
    manager._timeline = []
    manager.record_timing("pkg.fn", 1.0)
    assert manager.report()["timeline"] == []

    manager.configure(handlers=[], profiling_buffer_size=1)
    manager.record_timing("pkg.fn", 2.0, span=True)
    manager.record_timing("pkg.fn", 3.0, meta={"x": 1})
    assert len(manager.report()["timeline"]) == 1


def test_manager_remove_handler_absent_and_config_path_without_data(monkeypatch, tmp_path):
    manager = get_manager()
    manager.configure(handlers=[])

    class _H:
        pass

    manager.remove_handler(_H())
    manager.configure(show_traceback=True, handlers=[])
    assert manager.config.show_traceback is True

    monkeypatch.setattr("smonitor.config.discovery.discover_config", lambda p: None)
    manager.configure(config_path=tmp_path, handlers=[])


def test_manager_emit_with_non_matching_silence_and_valid_dev_schema(monkeypatch):
    manager = get_manager()
    manager.configure(
        profile="dev",
        level="DEBUG",
        silence=["other.pkg"],
        handlers=[],
        strict_schema=False,
    )
    monkeypatch.setattr("smonitor.core.manager.validate_event", lambda event: [])
    out = smonitor.emit("WARNING", "ok", source="pkg.mod", code="C")
    assert out["source"] == "pkg.mod"


def test_manager_report_skips_empty_timing_lists():
    manager = get_manager()
    manager.configure(handlers=[])
    manager._timings = {"empty.key": []}
    rep = manager.report()
    assert rep["timings"] == {}
