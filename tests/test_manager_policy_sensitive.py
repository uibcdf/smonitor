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
