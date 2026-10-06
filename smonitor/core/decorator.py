from __future__ import annotations

import warnings
from functools import wraps
from inspect import iscoroutinefunction
from random import random
from time import perf_counter
from typing import Any, Callable, Optional

from .._diagnostics import CODES
from . import runtime
from .capture import (
    CapturePolicy,
    capture_facts,
    derived_metadata,
    diagnostic_scope,
    get_capture_policy,
    safe_metadata,
)
from .context import frame_args, pop_frame, push_frame, set_frame_args, set_frame_duration
from .manager import get_manager

ExtraFactory = Callable[[tuple[Any, ...], dict[str, Any]], Optional[dict[str, Any]]]


def _signal_warning(stage, signal_label, exc):
    entry = CODES["SMONITOR-SIGNAL-FALLBACK"]
    facts = {"stage": stage, "signal": signal_label}
    if get_capture_policy().exception_text:
        try:
            facts["detail"] = str(exc)
        except Exception:
            facts["detail"] = type(exc).__name__
        template = entry["dev_message"]
    else:
        template = entry["message"]
        facts["signal"] = signal_label[:256] if type(signal_label) is str else "unknown"
    try:
        warnings.warn(template.format_map(facts), RuntimeWarning, stacklevel=3)
    except Exception:
        # Diagnostic failures, including warnings promoted to errors, cannot
        # replace the operation's exception or prevent a successful call.
        pass


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
    capture_policy: Optional[CapturePolicy] = None,
    safe_extra: Optional[dict[str, Any]] = None,
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

        def begin(args, kwargs):
            if not runtime.signals_enabled:
                return None
            policy = get_capture_policy()

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
                _signal_warning("setup", signal_label, exc)
                return None

            if not config.enabled:
                return None

            try:
                manager.record_call()
            except Exception as exc:
                _signal_warning("record_call", signal_label, exc)

            should_profile = False
            should_measure_slow = False
            start = None
            try:
                should_profile = plan[1] and random() <= plan[2]
                should_measure_slow = plan[3] > 0
                if should_profile or should_measure_slow:
                    start = perf_counter()
            except Exception as exc:
                _signal_warning("profiling setup", signal_label, exc)

            try:
                args_summary = (
                    _summarize_args(args, kwargs) if plan[4] and policy.arguments else None
                )
            except Exception as exc:
                _signal_warning("argument summary", signal_label, exc)
                args_summary = None

            frame_extra = None
            if not policy.extra:
                frame_extra = capture_facts()
            if extra_factory is not None and policy.extra:
                try:
                    frame_extra = extra_factory(args, kwargs)
                except Exception as exc:
                    _signal_warning("extra_factory", signal_label, exc)

            module = _resolve_owner_module(fn, args) if may_be_method and args else fn_module

            frame = None
            try:
                frame = push_frame(
                    fn_name,
                    module,
                    args=args_summary,
                    tags=tags if policy.extra else None,
                    extra=frame_extra,
                )
            except Exception as exc:
                _signal_warning("push_frame", signal_label, exc)

            return (
                manager,
                config,
                policy,
                frame,
                module,
                start,
                should_profile,
                should_measure_slow,
                frame_extra,
            )

        def on_failure(call, args, kwargs, exc):
            (
                manager,
                config,
                policy,
                frame,
                module,
                start,
                should_profile,
                should_measure_slow,
                frame_extra,
            ) = call

            if policy.arguments and frame is not None and frame_args(frame) is None:
                try:
                    set_frame_args(frame, _summarize_args(args, kwargs))
                except Exception as summary_exc:
                    _signal_warning("argument summary", signal_label, summary_exc)
            try:
                state = BaseException.__getattribute__(exc, "__dict__")
                already_emitted = (
                    getattr(exc, "__smonitor_emitted__", False)
                    if policy.exception_text
                    else state.get("__smonitor_emitted__", False)
                )
                if not already_emitted:
                    source = f"{module}.{fn_name}"
                    # A CatalogException already resolved its own code and
                    # structured extra; carry both onto the event rather
                    # than emitting an uncoded one that drops what the
                    # exception knows about itself.
                    code = (
                        getattr(exc, "code", None) if policy.exception_text else state.get("code")
                    )
                    if type(code) is not str:
                        code = None
                    if not policy.exception_text and code not in manager.get_codes():
                        code = "SMONITOR-NATIVE-FAILURE"
                    extra = {}
                    catalog_extra = getattr(exc, "extra", None) if policy.extra else None
                    if isinstance(catalog_extra, dict):
                        extra.update(catalog_extra)
                    extra["source_module"] = module
                    if frame_extra:
                        extra.update(frame_extra)
                    manager.emit(
                        exception_level,
                        str(exc) if policy.exception_text else "",
                        source=source,
                        code=code,
                        exception_type=type(exc).__name__,
                        extra=extra,
                    )
                    try:
                        if policy.exception_text:
                            setattr(exc, "__smonitor_emitted__", True)
                        else:
                            state["__smonitor_emitted__"] = True
                    except Exception:
                        pass
            except Exception as smonitor_exc:
                _signal_warning("exception emission", signal_label, smonitor_exc)

        def finish(call):
            (
                manager,
                config,
                policy,
                frame,
                module,
                start,
                should_profile,
                should_measure_slow,
                frame_extra,
            ) = call

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
                            tags=tags if policy.extra else None,
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
                        if tags and policy.extra:
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
                            safe_extra=derived_metadata(extra) if not policy.extra else None,
                        )
                except Exception as exc:
                    _signal_warning("finalization", signal_label, exc)
            if frame is not None:
                try:
                    pop_frame()
                except Exception as exc:
                    _signal_warning("pop_frame", signal_label, exc)

        def invoke_scope():
            from contextlib import nullcontext

            from .capture import DETAILED

            return (
                diagnostic_scope(capture_policy or DETAILED, safe_extra=approved)
                if capture_policy is not None or approved
                else nullcontext()
            )

        approved = safe_metadata(safe_extra)
        if capture_policy is not None and type(capture_policy) is not CapturePolicy:
            from .._diagnostics import CapturePolicyError

            raise CapturePolicyError()

        @wraps(fn)
        def invoke(*args: Any, **kwargs: Any):
            if not runtime.signals_enabled:
                return fn(*args, **kwargs)
            call = begin(args, kwargs)
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                if call is not None:
                    on_failure(call, args, kwargs, exc)
                raise
            finally:
                if call is not None:
                    finish(call)

        if iscoroutinefunction(fn):

            @wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any):
                with invoke_scope():
                    call = begin(args, kwargs)
                    try:
                        return await fn(*args, **kwargs)
                    except Exception as exc:
                        if call is not None:
                            on_failure(call, args, kwargs, exc)
                        raise
                    finally:
                        if call is not None:
                            finish(call)

            return async_wrapper

        if capture_policy is None and not approved:
            return invoke

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            with invoke_scope():
                return invoke(*args, **kwargs)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
