from __future__ import annotations

import logging
from typing import Optional

from ..core import runtime
from ..core.manager import get_manager

#: `logging.captureWarnings(True)` routes Python warnings through this logger.
_WARNINGS_LOGGER = "py.warnings"


class SmonitorLoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        manager = get_manager()
        if getattr(record, "smonitor", False):
            return
        if record.name == _WARNINGS_LOGGER and runtime.replaying_catalog_warning():
            # Already emitted as a structured catalog event; this is the same
            # diagnostic coming back as formatted text with no code or fields.
            return
        try:
            message = record.getMessage()
        except Exception:
            message = str(record.msg)
        manager.emit(
            record.levelname,
            message,
            source=record.name,
            extra={"module": record.module, "funcName": record.funcName},
        )


_installed_handler: Optional[SmonitorLoggingHandler] = None
_capture_warnings_enabled = False


def enable_logging(*, capture_warnings: bool = False) -> None:
    global _installed_handler, _capture_warnings_enabled
    root_logger = logging.getLogger()
    if _installed_handler is None and not root_logger.handlers:
        _installed_handler = SmonitorLoggingHandler()
        root_logger.addHandler(_installed_handler)
    if capture_warnings and not _capture_warnings_enabled:
        logging.captureWarnings(True)
        _capture_warnings_enabled = True


def disable_logging() -> None:
    global _installed_handler, _capture_warnings_enabled
    if _installed_handler is not None:
        logging.getLogger().removeHandler(_installed_handler)
        _installed_handler = None
    if _capture_warnings_enabled:
        logging.captureWarnings(False)
        _capture_warnings_enabled = False
