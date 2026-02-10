from __future__ import annotations

from functools import wraps
from time import perf_counter
from random import random
from typing import Any, Callable, Optional

from .context import Frame, pop_frame, push_frame
from .manager import get_manager


def _summarize_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if args:
        summary["args"] = [repr(a)[:80] for a in args]
    if kwargs:
        summary["kwargs"] = {k: repr(v)[:80] for k, v in kwargs.items()}
    return summary


def signal(
    func: Callable[..., Any] | None = None,
    *,
    tags: Optional[list[str]] = None,
    exception_level: str = "ERROR",
):
    def decorator(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            manager = get_manager()
            if not manager.config.enabled:
                return fn(*args, **kwargs)
            manager.record_call()
            if manager.config.profiling and random() <= manager.config.profiling_sample_rate:
                start = perf_counter()
            else:
                start = None
            args_summary = _summarize_args(args, kwargs) if manager.config.args_summary else None
            frame = Frame(
                function=fn.__name__,
                module=fn.__module__,
                args=args_summary,
                tags=tags,
            )
            push_frame(frame)
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                # Capture args summary on error if not already captured
                if frame.args is None:
                    frame.args = _summarize_args(args, kwargs)
                
                # Prevent "Error Echo": only emit if this exception hasn't been handled by smonitor
                if not getattr(exc, "__smonitor_emitted__", False):
                    manager.emit(
                        exception_level,
                        str(exc),
                        source=fn.__module__,
                        exception_type=exc.__class__.__name__,
                    )
                    try:
                        setattr(exc, "__smonitor_emitted__", True)
                    except Exception:
                        pass
                raise
            finally:
                if start is not None:
                    frame.duration_ms = (perf_counter() - start) * 1000.0
                    key = f"{fn.__module__}.{fn.__name__}"
                    manager.record_timing(key, frame.duration_ms)
                pop_frame()
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
