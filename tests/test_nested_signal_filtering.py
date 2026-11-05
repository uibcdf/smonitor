"""Only admitted observations suppress enclosing exception signals (#59)."""

import asyncio
from contextlib import nullcontext

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("restricted", [False, True])
@pytest.mark.parametrize(
    "threshold,inner_level,enabled,silenced,expected",
    [
        ("WARNING", "DEBUG", True, False, ["ERROR"]),
        ("DEBUG", "DEBUG", True, False, ["DEBUG"]),
        ("WARNING", "ERROR", True, False, ["ERROR"]),
        ("CRITICAL", "DEBUG", True, False, []),
        ("WARNING", "DEBUG", False, False, []),
        ("DEBUG", "DEBUG", True, True, ["ERROR"]),
    ],
)
def test_nested_signal_admission(
    asynchronous, restricted, threshold, inner_level, enabled, silenced, expected
):
    handler = MemoryHandler()
    manager = smonitor.configure(
        handlers=[handler],
        level=threshold,
        enabled=enabled,
        silence=[__name__ + ".inner"] if silenced else [],
        capture_warnings=False,
        capture_logging=False,
        capture_exceptions=False,
        event_buffer_size=20,
        duplicate_policy="off",
    )
    failure = ValueError("private controlled failure")
    cause = RuntimeError("original cause")

    if asynchronous:

        @smonitor.signal(exception_level=inner_level)
        async def inner():
            raise failure from cause

        @smonitor.signal(exception_level="ERROR")
        async def outer():
            await inner()

        def invoke():
            return asyncio.run(outer())
    else:

        @smonitor.signal(exception_level=inner_level)
        def inner():
            raise failure from cause

        @smonitor.signal(exception_level="ERROR")
        def outer():
            inner()

        invoke = outer

    scope = smonitor.diagnostic_scope() if restricted else nullcontext()
    with scope, pytest.raises(ValueError) as caught:
        invoke()
    assert caught.value is failure
    assert failure.args == ("private controlled failure",)
    assert failure.__cause__ is cause
    assert [event["level"] for event in handler.events] == expected
    assert [event["level"] for event in manager.recent_events()] == expected
    assert bool(getattr(failure, "__smonitor_emitted__", False)) == bool(expected)
    if restricted:
        assert all("private controlled failure" not in str(event) for event in handler.events)


@pytest.mark.parametrize(
    "changed_policy",
    [{"level": "WARNING"}, {"enabled": False}, {"silence": [__name__ + ".inner"]}],
)
def test_admission_uses_policy_after_exception_formatting(changed_policy):
    handler = MemoryHandler()
    smonitor.configure(
        handlers=[handler],
        level="DEBUG",
        enabled=True,
        silence=[],
        capture_warnings=False,
        capture_logging=False,
        capture_exceptions=False,
    )

    class PolicyChangingFailure(ValueError):
        def __str__(self):
            if not getattr(self, "formatted", False):
                self.formatted = True
                smonitor.configure(**changed_policy)
            return "controlled failure"

    failure = PolicyChangingFailure("controlled failure")

    @smonitor.signal(exception_level="DEBUG")
    def inner():
        raise failure

    @smonitor.signal(exception_level="ERROR")
    def outer():
        try:
            inner()
        except PolicyChangingFailure:
            assert not getattr(failure, "__smonitor_emitted__", False)
            # Restore the application's policy for the enclosing observation.
            smonitor.configure(level="WARNING", enabled=True, silence=[])
            raise

    with pytest.raises(PolicyChangingFailure) as caught:
        outer()
    assert caught.value is failure
    assert failure.args == ("controlled failure",)
    assert [event["level"] for event in handler.events] == ["ERROR"]
