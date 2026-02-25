from __future__ import annotations

import sys
from typing import Callable, Optional, Type

from ..core.manager import get_manager

_original_excepthook: Optional[Callable[[Type[BaseException], BaseException, object], None]] = None
_enabled = False


def _smonitor_excepthook(exc_type, exc, tb):
    manager = get_manager()
    manager.emit(
        "ERROR",
        str(exc),
        source=getattr(exc_type, "__name__", "Exception"),
        exception_type=getattr(exc_type, "__name__", "Exception"),
    )
    if _original_excepthook is not None:
        _original_excepthook(exc_type, exc, tb)


def enable_exceptions() -> None:
    global _original_excepthook, _enabled
    if not _enabled:
        _original_excepthook = sys.excepthook
        sys.excepthook = _smonitor_excepthook
        _enabled = True


def disable_exceptions() -> None:
    global _original_excepthook, _enabled
    if _enabled and _original_excepthook is not None:
        sys.excepthook = _original_excepthook
        _original_excepthook = None
        _enabled = False
