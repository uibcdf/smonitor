import smonitor
from smonitor.core.manager import get_manager


def test_handler_errors_counted():
    class BadHandler:
        name = "bad"
        def handle(self, event, profile="user"):
            raise RuntimeError("boom")

    manager = smonitor.configure(profile="user", handlers=[BadHandler()])
    smonitor.emit("WARNING", "x")
    report = manager.report()
    assert report["handler_errors"]["bad"] == 1


def test_disabled_noop():
    smonitor.configure(enabled=False)

    @smonitor.signal
    def foo():
        return 1

    assert foo() == 1
    smonitor.configure(enabled=True)
