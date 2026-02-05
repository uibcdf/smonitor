from __future__ import annotations

from pathlib import Path

from .core.manager import get_manager
from .core.decorator import signal
from .handlers.console import ConsoleHandler
from .config import load_project_config, build_effective_config, extract_policy

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
    project_cfg = load_project_config(Path.cwd())
    effective = build_effective_config(project_cfg, kwargs)
    policy = extract_policy(project_cfg)
    if "handlers" not in kwargs or kwargs["handlers"] is None:
        # Default to a console handler if none provided
        if not manager._handlers:
            manager.add_handler(ConsoleHandler())
    manager.configure(**effective, **policy)
    return manager


def emit(level, message, **kwargs):
    manager = get_manager()
    if not manager._handlers:
        manager.add_handler(ConsoleHandler())
    return manager.emit(level, message, **kwargs)


def report():
    manager = get_manager()
    return manager.report()
