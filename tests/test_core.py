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


def test_event_fingerprint_is_stable_for_same_incident_shape():
    manager = smonitor.configure(profile="user", handlers=[], event_buffer_size=10)
    event_a = smonitor.emit(
        "WARNING",
        "retry first text",
        source="pkg.mod",
        code="W1",
        exception_type="TimeoutError",
        extra={"resource": "181l", "caller": "pkg.mod.fn"},
    )
    event_b = smonitor.emit(
        "WARNING",
        "retry second text",
        source="pkg.mod",
        code="W1",
        exception_type="TimeoutError",
        extra={"resource": "181l", "caller": "pkg.mod.fn"},
    )
    assert event_a["fingerprint"] == event_b["fingerprint"]
    report = manager.report()
    assert report["events_by_fingerprint"][event_a["fingerprint"]] >= 2


def test_runtime_identifiers_are_propagated_to_events_and_report():
    manager = smonitor.configure(
        profile="user",
        handlers=[],
        event_buffer_size=10,
        run_id="run-1",
        session_id="session-1",
        correlation_id="corr-default",
    )
    event = smonitor.emit("WARNING", "warn test", source="pkg.mod", code="W1")
    assert event["run_id"] == "run-1"
    assert event["session_id"] == "session-1"
    assert event["correlation_id"] == "corr-default"
    report = manager.report()
    assert report["run_id"] == "run-1"
    assert report["session_id"] == "session-1"


def test_emit_correlation_id_override_wins_over_default():
    smonitor.configure(
        profile="user",
        handlers=[],
        event_buffer_size=10,
        run_id="run-2",
        session_id="session-2",
        correlation_id="corr-default",
    )
    event = smonitor.emit(
        "WARNING",
        "warn test",
        source="pkg.mod",
        code="W1",
        correlation_id="corr-explicit",
    )
    assert event["correlation_id"] == "corr-explicit"


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


def test_warning_coalescing_suppresses_repeated_events():
    memory = MemoryHandler(max_events=10)
    manager = smonitor.configure(
        profile="user",
        handlers=[memory],
        event_buffer_size=10,
        warning_coalesce_window_s=60.0,
    )
    manager._warning_coalesce_state.clear()
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={"resource": "181l", "caller": "pkg.mod.fn"},
    )
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={"resource": "181l", "caller": "pkg.mod.fn"},
    )
    assert len(memory.events) == 1
    report = manager.report()
    assert report["coalesced_warnings"][-1]["suppressed_count"] == 1


def test_warning_coalescing_finalizes_with_summary_event():
    memory = MemoryHandler(max_events=10)
    manager = smonitor.configure(
        profile="user",
        handlers=[memory],
        event_buffer_size=10,
        warning_coalesce_window_s=60.0,
    )
    manager._warning_coalesce_state.clear()
    manager._coalesced_warning_summaries.clear()
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={
            "resource": "181l",
            "caller": "pkg.mod.fn",
            "retry_attempt": 2,
            "retry_max": 5,
            "last_failure_reason": "timeout",
        },
    )
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={
            "resource": "181l",
            "caller": "pkg.mod.fn",
            "retry_attempt": 3,
            "retry_max": 5,
            "last_failure_reason": "timeout",
        },
    )

    summaries = manager.flush_coalesced_warnings()

    assert summaries[-1]["suppressed_count"] == 1
    assert summaries[-1]["total_occurrences"] == 2
    assert summaries[-1]["retry_attempt"] == 3
    assert summaries[-1]["retry_max"] == 5
    assert summaries[-1]["last_failure_reason"] == "timeout"
    assert any(event["code"] == "SMONITOR-WARNING-COALESCED" for event in memory.events)


def test_warning_coalescing_expired_window_emits_summary_before_reset(monkeypatch):
    memory = MemoryHandler(max_events=10)
    manager = smonitor.configure(
        profile="user",
        handlers=[memory],
        event_buffer_size=10,
        warning_coalesce_window_s=5.0,
    )
    manager._warning_coalesce_state.clear()
    manager._coalesced_warning_summaries.clear()
    moments = iter([10.0, 11.0, 20.5])
    monkeypatch.setattr("smonitor.core.manager.time", lambda: next(moments))

    smonitor.emit("WARNING", "retry", source="pkg.mod", code="W1", extra={"resource": "181l"})
    smonitor.emit("WARNING", "retry", source="pkg.mod", code="W1", extra={"resource": "181l"})
    smonitor.emit("WARNING", "retry", source="pkg.mod", code="W1", extra={"resource": "181l"})

    summary_events = [
        event for event in memory.events if event["code"] == "SMONITOR-WARNING-COALESCED"
    ]
    assert summary_events
    assert summary_events[-1]["extra"]["suppressed_count"] == 1
