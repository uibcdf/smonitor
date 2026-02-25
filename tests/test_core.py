import pytest

import smonitor
from smonitor.core.manager import get_manager
from smonitor.handlers.memory import MemoryHandler


def test_import_smonitor():
    assert smonitor is not None


def test_configure_defaults_add_handler():
    manager = smonitor.configure(profile="user", strict_signals=False)
    assert manager is get_manager()
    assert manager._handlers


def test_emit_increments_counts():
    manager = get_manager()
    smonitor.configure(profile="user", strict_signals=False)
    start = manager.report()["warnings_total"]
    smonitor.emit("WARNING", "warn test")
    assert manager.report()["warnings_total"] == start + 1


def test_signal_records_call_and_context():
    manager = get_manager()
    smonitor.configure(profile="user", strict_signals=False)
    start_calls = manager.report()["calls_total"]

    @smonitor.signal
    def foo(x):
        smonitor.emit("INFO", "inside", source="test")
        return x

    assert foo(1) == 1
    assert manager.report()["calls_total"] == start_calls + 1


def test_args_summary_in_context():
    smonitor.configure(profile="user", strict_signals=False, args_summary=True)

    @smonitor.signal
    def bar(x, y=2):
        return smonitor.emit("INFO", "ctx", source="test")

    event = bar(1, y=3)
    context = event.get("context")
    assert context and context["frames"][0]["args"] is not None


def test_profiling_adds_duration():
    smonitor.configure(profile="user", strict_signals=False, profiling=True)

    @smonitor.signal
    def baz():
        return smonitor.emit("INFO", "ctx", source="test")

    event = baz()
    context = event.get("context")
    assert context and context["frames"][0]["duration_ms"] is not None
    report = smonitor.report()
    assert "timings" in report


def test_level_threshold_filters_console_routing():
    memory = MemoryHandler(max_events=10)
    smonitor.configure(
        profile="user",
        strict_signals=False,
        level="WARNING",
        handlers=[memory],
        event_buffer_size=10,
    )

    smonitor.emit("DEBUG", "debug message", source="test")
    smonitor.emit("WARNING", "warning message", source="test")

    assert len(memory.events) == 1
    assert memory.events[0]["level"] == "WARNING"


def test_signal_exception_source_keeps_module_contract_compatibility():
    manager = smonitor.configure(
        profile="dev",
        strict_signals=True,
        signals={__name__: {"extra_required": ["source_module"]}},
        level="DEBUG",
        event_buffer_size=5,
    )

    @smonitor.signal
    def will_fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        will_fail()

    events = manager.recent_events()
    assert events
    event = events[-1]
    assert event["source"].startswith(__name__ + ".")
    assert event["extra"]["source_module"] == __name__
