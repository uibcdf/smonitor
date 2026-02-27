import logging

import smonitor
from smonitor.core.manager import get_manager
from smonitor.emitters import exceptions as ex_emit
from smonitor.emitters import logging as log_emit


def test_logging_handler_ignores_smonitor_tagged_records():
    manager = smonitor.configure(profile="user", handlers=[], event_buffer_size=10)
    start = manager.report()["warnings_total"]

    record = logging.LogRecord(
        name="x",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    setattr(record, "smonitor", True)
    log_emit.SmonitorLoggingHandler().emit(record)
    assert manager.report()["warnings_total"] == start


def test_logging_handler_fallback_when_getmessage_breaks():
    class BadMsg:
        def __str__(self):
            return "fallback-msg"

    class BadRecord(logging.LogRecord):
        def getMessage(self):
            raise RuntimeError("broken")

    manager = smonitor.configure(profile="user", handlers=[], event_buffer_size=10)
    record = BadRecord(
        name="x",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg=BadMsg(),
        args=(),
        exc_info=None,
    )
    log_emit.SmonitorLoggingHandler().emit(record)
    events = manager.recent_events()
    assert events[-1]["message"] == "fallback-msg"


def test_enable_logging_does_not_install_if_root_has_handlers():
    root = logging.getLogger()
    old_handlers = list(root.handlers)
    temp_handler = logging.StreamHandler()
    root.handlers = [temp_handler]

    log_emit._installed_handler = None
    log_emit.enable_logging(capture_warnings=False)
    assert log_emit._installed_handler is None

    root.handlers = old_handlers


def test_exception_emitter_calls_original_excepthook(monkeypatch):
    called = {}

    def fake_original(exc_type, exc, tb):
        called["type"] = exc_type.__name__

    manager = get_manager()
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10)
    monkeypatch.setattr(ex_emit, "_original_excepthook", fake_original)

    ex_emit._smonitor_excepthook(RuntimeError, RuntimeError("boom"), None)
    events = manager.recent_events()
    assert events[-1]["exception_type"] == "RuntimeError"
    assert called["type"] == "RuntimeError"
