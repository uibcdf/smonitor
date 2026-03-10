from __future__ import annotations

from functools import wraps
from random import random
from time import perf_counter
from typing import Any, Callable, Optional

from .context import Frame, pop_frame, push_frame
from .manager import get_manager

ExtraFactory = Callable[[tuple[Any, ...], dict[str, Any]], Optional[dict[str, Any]]]


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
    extra_factory: Optional[ExtraFactory] = None,
):
    def decorator(fn: Callable[..., Any]):
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            manager = get_manager()
            if not manager.config.enabled:
                return fn(*args, **kwargs)
            manager.record_call()
            should_profile = (
                manager.config.profiling
                and random() <= manager.config.profiling_sample_rate
            )
            should_measure_slow = manager.config.slow_signal_ms > 0
            if should_profile or should_measure_slow:
                start = perf_counter()
            else:
                start = None
            args_summary = _summarize_args(args, kwargs) if manager.config.args_summary else None
            frame_extra = None
            if extra_factory is not None:
                frame_extra = extra_factory(args, kwargs)
            frame = Frame(
                function=fn.__name__,
                module=fn.__module__,
                args=args_summary,
                tags=tags,
                extra=frame_extra,
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
                    source = f"{fn.__module__}.{fn.__name__}"
                    extra = {"source_module": fn.__module__}
                    if frame.extra:
                        extra.update(frame.extra)
                    manager.emit(
                        exception_level,
                        str(exc),
                        source=source,
                        exception_type=exc.__class__.__name__,
                        extra=extra,
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
                    if should_profile:
                        manager.record_timing(
                            key,
                            frame.duration_ms,
                            tags=frame.tags,
                            meta=frame.extra,
                        )
                    if should_measure_slow and frame.duration_ms >= manager.config.slow_signal_ms:
                        extra = {
                            "module": fn.__module__,
                            "function": fn.__name__,
                            "duration_ms": frame.duration_ms,
                            "threshold_ms": manager.config.slow_signal_ms,
                            "cache_state": "n/a",
                        }
                        if frame.tags:
                            extra["signal_tags"] = list(frame.tags)
                        if frame.extra:
                            extra.update(frame.extra)
                        manager.emit(
                            manager.config.slow_signal_level,
                            f"Slow signal call detected for {key}.",
                            source=key,
                            category="profiling",
                            code="SMONITOR-SIGNAL-SLOW",
                            tags=frame.tags,
                            extra=extra,
                        )
                pop_frame()
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
