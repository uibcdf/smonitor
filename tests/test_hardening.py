import smonitor


def test_handler_errors_counted():
    class BadHandler:
        name = "bad"
        def handle(self, event, profile="user"):
            raise RuntimeError("boom")

    manager = smonitor.configure(profile="user", handlers=[BadHandler()])
    smonitor.emit("WARNING", "x")
    report = manager.report()
    assert report["handler_errors"]["bad"] == 1
    assert report["handler_errors_total"] == 1
    assert "bad" in report["degraded_handlers"]


def test_handler_degradation_threshold_flagged():
    class BadHandler:
        name = "flaky"

        def handle(self, event, profile="user"):
            raise RuntimeError("boom")

    manager = smonitor.configure(profile="user", handlers=[BadHandler()], handler_error_threshold=2)
    smonitor.emit("WARNING", "x")
    smonitor.emit("WARNING", "y")
    report = manager.report()
    assert report["handler_errors"]["flaky"] == 2
    assert any("flaky" in msg for msg in report["runtime_warnings"])


def test_handler_degradation_warning_announced_once():
    class BadHandler:
        name = "once"

        def handle(self, event, profile="user"):
            raise RuntimeError("boom")

    manager = smonitor.configure(
        profile="user",
        handlers=[BadHandler()],
        handler_error_threshold=1,
    )
    smonitor.emit("WARNING", "x")
    smonitor.emit("WARNING", "y")
    report = manager.report()
    msgs = [m for m in report["runtime_warnings"] if "once" in m]
    assert len(msgs) == 1


def test_disabled_noop():
    smonitor.configure(enabled=False)

    @smonitor.signal
    def foo():
        return 1

    assert foo() == 1
    smonitor.configure(enabled=True)


def test_emit_does_not_mutate_the_caller_extra():
    """The caller's `extra` dict is an input, not scratch space.

    `emit()` enriches the event's extra with `smonitor`, `title` and the
    resolved `hint`. Writing those into the caller's dict made a reused dict
    accumulate them, so a later event carried a stale hint from an earlier,
    unrelated one.
    """
    smonitor.configure(
        profile="user",
        handlers=[],
        codes={"X-1": {"title": "Titled", "user_message": "msg", "user_hint": "do this"}},
    )

    shared = {"resource": "file.h5"}
    event = smonitor.emit("WARNING", "", code="X-1", source="mylib.f", extra=shared)

    assert shared == {"resource": "file.h5"}
    assert event["extra"] is not shared
    assert event["extra"]["hint"] == "do this"

    # The same dict reused for an unrelated, uncoded event stays clean.
    second = smonitor.emit("WARNING", "other", source="mylib.g", extra=shared)
    assert "hint" not in second["extra"]
    assert "title" not in second["extra"]
