import logging
import smonitor
from smonitor.core.manager import get_manager
from smonitor.emitters import warnings as sm_warnings


def test_warnings_emitter_increments_count():
    manager = get_manager()
    start = manager.report()["warnings_total"]
    smonitor.configure(capture_warnings=True)
    sm_warnings._smonitor_showwarning("warn from test", UserWarning, "file.py", 1)
    assert manager.report()["warnings_total"] == start + 1


def test_logging_emitter_increments_count():
    manager = get_manager()
    start = manager.report()["warnings_total"]
    smonitor.configure(capture_logging=True)
    logging.getLogger().warning("log warning")
    assert manager.report()["warnings_total"] == start + 1
