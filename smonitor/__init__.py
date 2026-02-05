from __future__ import annotations

from .core.manager import get_manager
from .core.decorator import signal
from .handlers.console import ConsoleHandler

__all__ = [
    "configure",
    "emit",
    "report",
    "signal",
    "get_manager",
]

__version__ = "0.1.0"


def configure(**kwargs):
    manager = get_manager()
    if "handlers" not in kwargs or kwargs["handlers"] is None:
        # Default to a console handler if none provided
        if not manager._handlers:
            manager.add_handler(ConsoleHandler())
    manager.configure(**kwargs)
    return manager


def emit(level, message, **kwargs):
    manager = get_manager()
    if not manager._handlers:
        manager.add_handler(ConsoleHandler())
    return manager.emit(level, message, **kwargs)


def report():
    manager = get_manager()
    return manager.report()
