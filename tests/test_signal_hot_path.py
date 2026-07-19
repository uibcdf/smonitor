"""Invariants of the `@signal` hot path.

The wrapper caches configuration-derived decisions and stores breadcrumb frames
in a compact list rather than an object. Both are invisible when they work and
silent when they break, so the behaviour they must preserve is pinned here.
"""

from __future__ import annotations

import smonitor
from smonitor.handlers.memory import MemoryHandler


def _configured(**kwargs):
    handler = MemoryHandler(max_events=50)
    smonitor.configure(handlers=[handler], event_buffer_size=50, **kwargs)
    return handler


class TestConfigPlanCache:
    """The cached plan is keyed on config identity; `configure()` must invalidate it."""

    def test_enabling_profiling_after_first_call_takes_effect(self):
        _configured(profile="user", level="INFO", profiling=False)

        @smonitor.signal
        def work():
            return 1

        work()
        assert not smonitor.report()["timings"]

        smonitor.configure(profiling=True)
        work()
        assert any(key.endswith(".work") for key in smonitor.report()["timings"])

    def test_disabling_profiling_after_first_call_takes_effect(self):
        _configured(profile="user", level="INFO", profiling=True)

        @smonitor.signal
        def work():
            return 1

        work()
        before = len(smonitor.report()["timings"].get("tests.test_signal_hot_path.work", []))

        smonitor.configure(profiling=False)
        work()
        after = smonitor.report()["timings"]
        recorded = after.get("tests.test_signal_hot_path.work")
        # No new timing entry was added by the second call.
        assert recorded is None or recorded["count"] == max(before, 1)

    def test_enabling_args_summary_after_first_call_takes_effect(self):
        handler = _configured(profile="user", level="INFO", args_summary=False)

        @smonitor.signal
        def work(value):
            smonitor.emit("INFO", "inside", source="test", code="HP-1")
            return value

        work(1)
        assert handler.events[-1]["context"]["frames"][0]["args"] is None

        smonitor.configure(args_summary=True)
        work(2)
        assert handler.events[-1]["context"]["frames"][0]["args"] is not None

    def test_toggling_enabled_at_runtime_takes_effect(self):
        handler = _configured(profile="user", level="INFO", enabled=True)

        @smonitor.signal
        def work():
            smonitor.emit("INFO", "inside", source="test", code="HP-2")
            return 1

        work()
        assert len(handler.events) == 1

        smonitor.configure(enabled=False)
        work()
        assert len(handler.events) == 1  # nothing emitted while disabled

        smonitor.configure(enabled=True)
        work()
        assert len(handler.events) == 2


class TestFrameContents:
    def test_slow_signal_event_carries_its_duration(self):
        """The frame is populated before it is popped, so the event sees it."""
        handler = _configured(
            profile="user", level="INFO", slow_signal_ms=0.0001, slow_signal_level="INFO"
        )

        @smonitor.signal(tags=["io"])
        def slow():
            return sum(range(1000))

        slow()

        slow_events = [e for e in handler.events if e.get("code") == "SMONITOR-SIGNAL-SLOW"]
        assert slow_events
        event = slow_events[-1]
        assert event["extra"]["duration_ms"] > 0
        frame = event["context"]["frames"][-1]
        assert frame["function"] == "slow"
        assert frame["duration_ms"] is not None
        assert frame["tags"] == ["io"]

    def test_error_event_carries_the_call_arguments(self):
        """Arguments are summarized lazily on the failure path, even when
        `args_summary` is off, so an error report shows the inputs."""
        handler = _configured(profile="user", level="INFO", args_summary=False)

        @smonitor.signal
        def boom(value, keyword=None):
            raise ValueError("nope")

        try:
            boom(41, keyword="x")
        except ValueError:
            pass

        errors = [e for e in handler.events if e["level"] == "ERROR"]
        assert errors
        frame = errors[-1]["context"]["frames"][-1]
        assert frame["args"] is not None
        assert "41" in str(frame["args"])
        assert "x" in str(frame["args"])

    def test_extra_factory_reaches_both_frame_and_error_event(self):
        handler = _configured(profile="user", level="INFO")

        @smonitor.signal(extra_factory=lambda a, k: {"resource": "traj.h5"})
        def boom():
            raise RuntimeError("nope")

        try:
            boom()
        except RuntimeError:
            pass

        errors = [e for e in handler.events if e["level"] == "ERROR"]
        assert errors[-1]["extra"]["resource"] == "traj.h5"
        assert errors[-1]["context"]["frames"][-1]["extra"] == {"resource": "traj.h5"}
