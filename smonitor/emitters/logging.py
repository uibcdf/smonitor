from __future__ import annotations

import logging
from typing import Optional

from ..core.manager import get_manager


class SmonitorLoggingHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        manager = get_manager()
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


def enable_logging() -> None:
    global _installed_handler
    if _installed_handler is None:
        _installed_handler = SmonitorLoggingHandler()
        logging.getLogger().addHandler(_installed_handler)


def disable_logging() -> None:
    global _installed_handler
    if _installed_handler is not None:
        logging.getLogger().removeHandler(_installed_handler)
        _installed_handler = None
