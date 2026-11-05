"""Filtered observations must not hide eligible enclosing failures (#59)."""

import asyncio
import json

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler


def _configure(**kwargs):
    handler = MemoryHandler()
    kwargs.setdefault("enabled", True)
    smonitor.configure(
        handlers=[handler],
        profile="user",
        capture_warnings=False,
        capture_logging=False,
        event_buffer_size=50,
        **kwargs,
    )
    return handler


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "threshold,inner_level,expected_source,expected_level",
    [
        ("WARNING", "DEBUG", "outer", "ERROR"),
        ("ERROR", "WARNING", "outer", "ERROR"),
        ("WARNING", "debug", "outer", "ERROR"),
        ("DEBUG", "DEBUG", "inner", "DEBUG"),
        ("WARNING", "ERROR", "inner", "ERROR"),
    ],
)
def test_first_eligible_signal_observes_exception(
    threshold, inner_level, expected_source, expected_level, asynchronous
):
    handler = _configure(level=threshold)
    failure = ValueError("native failure", 17)
    cause = RuntimeError("original cause")

    if asynchronous:

        @smonitor.signal(exception_level=inner_level)
        async def inner():
            raise failure from cause

        @smonitor.signal(exception_level="ERROR")
        async def outer():
            await inner()

        def run():
            asyncio.run(outer())
    else:

        @smonitor.signal(exception_level=inner_level)
        def inner():
            raise failure from cause

        @smonitor.signal(exception_level="ERROR")
        def outer():
            inner()

        run = outer

    with pytest.raises(ValueError) as caught:
        run()
    assert caught.value is failure
    assert failure.args == ("native failure", 17)
    assert failure.__cause__ is cause
    assert len(handler.events) == 1
    event = handler.events[0]
    assert event["source"].endswith("." + expected_source)
    assert event["level"] == expected_level
    assert event["exception_type"] == "ValueError"
    assert [event["level"] for event in smonitor.get_manager().recent_events()] == [expected_level]


@pytest.mark.parametrize("inner_silenced", [True, False])
def test_source_silence_is_applied_before_deduplication(inner_silenced):
    source = f"{__name__}.inner" if inner_silenced else __name__
    handler = _configure(level="DEBUG", silence=[source])
    failure = ValueError("native failure")

    @smonitor.signal
    def inner():
        raise failure

    @smonitor.signal
    def outer():
        inner()

    with pytest.raises(ValueError) as caught:
        outer()
    assert caught.value is failure
    if inner_silenced:
        assert len(handler.events) == 1
        assert handler.events[0]["source"].endswith(".outer")
    else:
        assert not handler.events
        assert not getattr(failure, "__smonitor_emitted__", False)


def test_filtering_uses_current_configuration_after_call_started():
    handler = _configure(level="DEBUG")
    failure = ValueError("native failure")

    @smonitor.signal(exception_level="DEBUG")
    def inner():
        smonitor.configure(level="WARNING")
        raise failure

    @smonitor.signal
    def outer():
        inner()

    with pytest.raises(ValueError) as caught:
        outer()
    assert caught.value is failure
    assert [event["level"] for event in handler.events] == ["ERROR"]
    assert handler.events[0]["source"].endswith(".outer")


@pytest.mark.parametrize("disabled_during_call", [False, True])
def test_disabled_diagnostics_leave_exception_unobserved(disabled_during_call):
    handler = _configure(level="DEBUG", enabled=disabled_during_call)
    failure = ValueError("native failure")

    @smonitor.signal
    def target():
        smonitor.configure(enabled=False)
        raise failure

    with pytest.raises(ValueError) as caught:
        target()
    assert caught.value is failure
    assert not handler.events
    assert not getattr(failure, "__smonitor_emitted__", False)


def test_filtered_nested_failure_preserves_metadata_only_capture():
    handler = _configure(level="WARNING", args_summary=True)

    class OpaqueFailure(ValueError):
        calls = 0

        def __str__(self):
            self.calls += 1
            raise AssertionError("Native failure text must not be evaluated")

    failure = OpaqueFailure("NATIVE_MARKER")

    @smonitor.signal(exception_level="DEBUG")
    def inner(value):
        raise failure

    @smonitor.signal(capture_policy=smonitor.METADATA_ONLY)
    def outer(value):
        inner(value)

    with pytest.raises(OpaqueFailure) as caught:
        outer("ARGUMENT_MARKER")
    assert caught.value is failure
    assert failure.calls == 0
    assert len(handler.events) == 1
    assert handler.events[0]["code"] == "SMONITOR-NATIVE-FAILURE"
    assert handler.events[0]["level"] == "ERROR"
    wire = json.dumps(handler.events)
    assert "NATIVE_MARKER" not in wire
    assert "ARGUMENT_MARKER" not in wire


def test_filtered_manager_emit_still_returns_preview():
    handler = _configure(level="WARNING", silence=["ignored"])
    manager = smonitor.get_manager()
    preview = manager.emit("DEBUG", "preview", source="visible")
    assert preview["level"] == "DEBUG"
    assert preview["message"] == "preview"
    assert manager.emit("ERROR", "silenced", source="ignored.child") == {}
    assert not handler.events
    assert not manager.recent_events()


def test_filter_change_during_exception_formatting_uses_actual_emission():
    handler = _configure(level="DEBUG")

    class ReconfiguringFailure(ValueError):
        def __str__(self):
            smonitor.configure(level="WARNING")
            return "native failure"

    failure = ReconfiguringFailure("native failure")

    @smonitor.signal(exception_level="DEBUG")
    def inner():
        raise failure

    @smonitor.signal
    def outer():
        inner()

    with pytest.raises(ReconfiguringFailure) as caught:
        outer()
    assert caught.value is failure
    assert [event["level"] for event in handler.events] == ["ERROR"]
    assert handler.events[0]["source"].endswith(".outer")


def test_nested_diagnostic_does_not_acknowledge_filtered_exception(monkeypatch):
    handler = _configure(level="WARNING")
    manager = smonitor.get_manager()
    resolve = manager._resolve_message_and_hint
    nested = False

    def instrumented_resolve(message, code, extra):
        nonlocal nested
        if not nested:
            nested = True
            manager.emit("ERROR", "separate diagnostic", source="template_callback")
        return resolve(message, code, extra)

    monkeypatch.setattr(manager, "_resolve_message_and_hint", instrumented_resolve)
    failure = ValueError("native failure")

    @smonitor.signal(exception_level="DEBUG")
    def inner():
        raise failure

    @smonitor.signal
    def outer():
        inner()

    with pytest.raises(ValueError) as caught:
        outer()
    assert caught.value is failure
    assert len(handler.events) == 2
    assert handler.events[0]["source"] == "template_callback"
    assert handler.events[1]["source"].endswith(".outer")


def test_exception_formatter_diagnostic_has_its_own_admission():
    handler = _configure(level="WARNING")
    manager = smonitor.get_manager()

    class ReportingFailure(ValueError):
        def __str__(self):
            if not getattr(self, "reported", False):
                self.reported = True
                manager.emit("ERROR", "formatter diagnostic", source="exception_formatter")
            return "native failure"

    failure = ReportingFailure("native failure")

    @smonitor.signal(exception_level="DEBUG")
    def inner():
        raise failure

    @smonitor.signal
    def outer():
        inner()

    with pytest.raises(ReportingFailure) as caught:
        outer()
    assert caught.value is failure
    assert len(handler.events) == 2
    assert handler.events[0]["source"] == "exception_formatter"
    assert handler.events[1]["source"].endswith(".outer")
