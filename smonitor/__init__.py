from __future__ import annotations

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("smonitor")
except PackageNotFoundError:
    # Package is not installed
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"

from pathlib import Path

from .core.manager import get_manager
from .core.decorator import signal
from .handlers.console import ConsoleHandler
from .handlers.console import RichConsoleHandler
from .config import load_project_config, build_effective_config, extract_policy, load_env_config, extract_codes, extract_signals

__all__ = [
    "configure",
    "emit",
    "report",
    "signal",
    "get_manager",
]


def configure(**kwargs):
    manager = get_manager()
    project_cfg = load_project_config(Path.cwd())
    env_cfg = load_env_config()
    effective = build_effective_config(project_cfg, env_cfg)
    effective.update({k: v for k, v in kwargs.items() if v is not None})
    policy = extract_policy(project_cfg)
    codes = extract_codes(project_cfg)
    signals = extract_signals(project_cfg)
    if "handlers" not in kwargs or kwargs["handlers"] is None:
        # Default to a console handler if none provided
        if not manager._handlers:
            theme = effective.get("theme", "plain")
            if theme == "rich":
                manager.add_handler(RichConsoleHandler())
            else:
                manager.add_handler(ConsoleHandler())
    manager.configure(**effective, **policy, codes=codes, signals=signals)
    return manager


def emit(level, message, **kwargs):
    manager = get_manager()
    if not manager._handlers:
        manager.add_handler(ConsoleHandler())
    return manager.emit(level, message, **kwargs)


def report():
    manager = get_manager()
    return manager.report()
