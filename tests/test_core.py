def test_import_smonitor():
    import smonitor  # noqa: F401


import smonitor
from smonitor.core.manager import get_manager


def test_configure_defaults_add_handler():
    manager = smonitor.configure()
    assert manager is get_manager()
    assert manager._handlers


def test_emit_increments_counts():
    manager = get_manager()
    start = manager.report()["warnings_total"]
    smonitor.emit("WARNING", "warn test")
    assert manager.report()["warnings_total"] == start + 1


def test_signal_records_call_and_context():
    manager = get_manager()
    start_calls = manager.report()["calls_total"]

    @smonitor.signal
    def foo(x):
        smonitor.emit("INFO", "inside", source="test")
        return x

    assert foo(1) == 1
    assert manager.report()["calls_total"] == start_calls + 1


def test_args_summary_in_context():
    smonitor.configure(args_summary=True)

    @smonitor.signal
    def bar(x, y=2):
        return smonitor.emit("INFO", "ctx", source="test")

    event = bar(1, y=3)
    context = event.get("context")
    assert context and context["frames"][0]["args"] is not None


def test_profiling_adds_duration():
    smonitor.configure(profiling=True)

    @smonitor.signal
    def baz():
        return smonitor.emit("INFO", "ctx", source="test")

    event = baz()
    context = event.get("context")
    assert context and context["frames"][0]["duration_ms"] is not None
