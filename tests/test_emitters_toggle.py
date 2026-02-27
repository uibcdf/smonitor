import sys
import warnings

from smonitor.emitters import exceptions as ex_emit
from smonitor.emitters import logging as log_emit
from smonitor.emitters import warnings as warn_emit


def test_warnings_enable_and_disable_roundtrip():
    original = warnings.showwarning
    warn_emit.disable_warnings()
    warn_emit.enable_warnings()
    assert warnings.showwarning == warn_emit._smonitor_showwarning
    warn_emit.disable_warnings()
    assert warnings.showwarning == original


def test_logging_disable_when_enabled():
    log_emit.disable_logging()
    log_emit.enable_logging(capture_warnings=True)
    # coverage target: disable paths for installed handler and capture_warnings flag
    log_emit.disable_logging()
    assert log_emit._installed_handler is None


def test_exceptions_enable_and_disable_roundtrip():
    original = sys.excepthook
    ex_emit.disable_exceptions()
    ex_emit.enable_exceptions()
    assert sys.excepthook == ex_emit._smonitor_excepthook
    ex_emit.disable_exceptions()
    assert sys.excepthook == original
