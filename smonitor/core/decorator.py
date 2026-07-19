from __future__ import annotations

import warnings
from functools import wraps
from random import random
from time import perf_counter
from typing import Any, Callable, Optional

from . import runtime
from .context import frame_args, pop_frame, push_frame, set_frame_args, set_frame_duration
from .manager import get_manager

ExtraFactory = Callable[[tuple[Any, ...], dict[str, Any]], Optional[dict[str, Any]]]


def _summarize_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    if args:
        summary["args"] = [repr(a)[:80] for a in args]
    if kwargs:
        summary["kwargs"] = {k: repr(v)[:80] for k, v in kwargs.items()}
    return summary


def _resolve_owner_module(fn: Callable[..., Any], args: tuple[Any, ...]) -> str:
    """Resolve the logical owner module of a decorated callable.

    For methods (whose ``__qualname__`` is ``Class.method``) the logical owner is
    the *runtime* class of the bound instance, which may differ from the module
    where the function was physically defined — e.g. classes assembled from
    mixins living in separate modules. Resolving from ``type(self)`` reports the
    class's real module without requiring module-level ``__name__`` spoofing in
    the defining files. Free functions keep their defining module.
    """
    qualname = getattr(fn, "__qualname__", "") or ""
    if args and "." in qualname and "<locals>" not in qualname:
        owner = type(args[0])
        if isinstance(owner, type) and hasattr(owner, fn.__name__):
            module = getattr(owner, "__module__", None)
            if isinstance(module, str) and module:
                return module
    return fn.__module__


def signal(
    func: Callable[..., Any] | None = None,
    *,
    tags: Optional[list[str]] = None,
    exception_level: str = "ERROR",
    extra_factory: Optional[ExtraFactory] = None,
):
    def decorator(fn: Callable[..., Any]):
        # Decided once, at decoration time: only a callable whose qualname is
        # `Class.method` can ever resolve its module from a bound instance, so
        # free functions skip that lookup on every call.
        fn_module = fn.__module__
        _qualname = getattr(fn, "__qualname__", "") or ""
        may_be_method = "." in _qualname and "<locals>" not in _qualname
        signal_label = f"{fn_module}.{fn.__name__}"
        fn_name = fn.__name__

        # Per-call decisions derived from the configuration, cached because the
        # config rarely changes but is consulted on every call. `ManagerConfig`
        # is a frozen dataclass that `configure()` replaces wholesale, so object
        # identity is an exact invalidation signal — there is no version counter
        # anyone could forget to bump.
        # Layout: [config, profiling, sample_rate, slow_ms, args_summary]
        plan: list[Any] = [None, False, 1.0, 0.0, False]

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            if not runtime.signals_enabled:
                return fn(*args, **kwargs)

            try:
                manager = get_manager()
                config = manager.config
                if config is not plan[0]:
                    plan[0] = config
                    plan[1] = config.profiling
                    plan[2] = config.profiling_sample_rate
                    plan[3] = config.slow_signal_ms
                    plan[4] = config.args_summary
            except Exception as exc:
                warnings.warn(
                    f"SMonitor signal setup failed for {signal_label}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                return fn(*args, **kwargs)

            if not config.enabled:
                return fn(*args, **kwargs)

            try:
                manager.record_call()
            except Exception as exc:
                warnings.warn(
                    f"SMonitor signal record_call failed for {signal_label}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )

            should_profile = False
            should_measure_slow = False
            start = None
            try:
                should_profile = plan[1] and random() <= plan[2]
                should_measure_slow = plan[3] > 0
                if should_profile or should_measure_slow:
                    start = perf_counter()
            except Exception as exc:
                warnings.warn(
                    f"SMonitor signal profiling setup failed for {signal_label}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )

            try:
                args_summary = _summarize_args(args, kwargs) if plan[4] else None
            except Exception as exc:
                warnings.warn(
                    f"SMonitor signal argument summary failed for {signal_label}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                args_summary = None

            frame_extra = None
            if extra_factory is not None:
                try:
                    frame_extra = extra_factory(args, kwargs)
                except Exception as exc:
                    warnings.warn(
                        f"SMonitor signal extra_factory failed for {signal_label}: {exc}",
                        RuntimeWarning,
                        stacklevel=2,
                    )

            module = _resolve_owner_module(fn, args) if may_be_method and args else fn_module

            frame = None
            try:
                frame = push_frame(
                    fn_name, module, args=args_summary, tags=tags, extra=frame_extra
                )
            except Exception as exc:
                warnings.warn(
                    f"SMonitor signal push_frame failed for {signal_label}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )

            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                try:
                    if frame is not None and frame_args(frame) is None:
                        set_frame_args(frame, _summarize_args(args, kwargs))
                    if not getattr(exc, "__smonitor_emitted__", False):
                        source = f"{module}.{fn_name}"
                        extra = {"source_module": module}
                        if frame_extra:
                            extra.update(frame_extra)
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
                except Exception as smonitor_exc:
                    warnings.warn(
                        f"SMonitor signal exception emission failed for "
                        f"{signal_label}: {smonitor_exc}",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                raise
            finally:
                if start is not None:
                    try:
                        duration_ms = (perf_counter() - start) * 1000.0
                        if frame is not None:
                            # Set before the frame is popped, so a slow-signal
                            # event emitted just below carries it in its context.
                            set_frame_duration(frame, duration_ms)
                        key = f"{module}.{fn_name}"
                        if should_profile:
                            manager.record_timing(
                                key,
                                duration_ms,
                                tags=tags,
                                meta=frame_extra,
                            )
                        if should_measure_slow and duration_ms >= plan[3]:
                            extra = {
                                "module": module,
                                "function": fn_name,
                                "duration_ms": duration_ms,
                                "threshold_ms": plan[3],
                                "cache_state": "n/a",
                            }
                            if tags:
                                extra["signal_tags"] = list(tags)
                            if frame_extra:
                                extra.update(frame_extra)
                            manager.emit(
                                config.slow_signal_level,
                                f"Slow signal call detected for {key}.",
                                source=key,
                                category="profiling",
                                code="SMONITOR-SIGNAL-SLOW",
                                tags=tags,
                                extra=extra,
                            )
                    except Exception as exc:
                        warnings.warn(
                            f"SMonitor signal finalization failed for {signal_label}: {exc}",
                            RuntimeWarning,
                            stacklevel=2,
                        )
                if frame is not None:
                    try:
                        pop_frame()
                    except Exception as exc:
                        warnings.warn(
                            f"SMonitor signal pop_frame failed for {signal_label}: {exc}",
                            RuntimeWarning,
                            stacklevel=2,
                        )
        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
