from __future__ import annotations

import warnings
from typing import Any, Callable, Optional

from ..core.manager import get_manager


_original_showwarning: Optional[Callable[..., Any]] = None


def _smonitor_showwarning(message, category, filename, lineno, file=None, line=None):
    manager = get_manager()
    source = None
    if filename:
        source = filename
    manager.emit(
        "WARNING",
        str(message),
        source=source,
        category=getattr(category, "__name__", str(category)),
    )


def enable_warnings() -> None:
    global _original_showwarning
    if _original_showwarning is None:
        _original_showwarning = warnings.showwarning
        warnings.showwarning = _smonitor_showwarning


def disable_warnings() -> None:
    global _original_showwarning
    if _original_showwarning is not None:
        warnings.showwarning = _original_showwarning
        _original_showwarning = None
