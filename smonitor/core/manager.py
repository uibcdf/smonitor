from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from .context import get_context
from ..policy.engine import PolicyEngine
from ..validation import validate_event


@dataclass
class ManagerConfig:
    level: str = "WARNING"
    theme: str = "plain"
    capture_warnings: bool = True
    capture_logging: bool = True
    trace_depth: int = 3
    show_traceback: bool = False
    profile: str = "user"
    capture_exceptions: bool = False
    args_summary: bool = False
    profiling: bool = False
    strict_signals: bool = False
    strict_schema: bool = False
    enabled: bool = True
    profiling_buffer_size: int = 1000
    profiling_hooks: list | None = None
    profiling_sample_rate: float = 1.0
    event_buffer_size: int = 0


class Manager:
    def __init__(self) -> None:
        self._config = ManagerConfig()
        self._handlers: List[Any] = []
        self._policy = PolicyEngine()
        self._codes: Dict[str, Dict[str, Any]] = {}
        self._signals: Dict[str, Dict[str, Any]] = {}
        self._counts = {
            "calls_total": 0,
            "warnings_total": 0,
            "errors_total": 0,
        }
        self._handler_errors: Dict[str, int] = {}
        self._timings: Dict[str, List[float]] = {}
        self._timeline: List[Dict[str, Any]] = []
        self._event_buffer: List[Dict[str, Any]] = []

    @property
    def config(self) -> ManagerConfig:
        return self._config

    def configure(
        self,
        *,
        level: Optional[str] = None,
        theme: Optional[str] = None,
        capture_warnings: Optional[bool] = None,
        capture_logging: Optional[bool] = None,
        capture_exceptions: Optional[bool] = None,
        trace_depth: Optional[int] = None,
        show_traceback: Optional[bool] = None,
        profile: Optional[str] = None,
        handlers: Optional[Iterable[Any]] = None,
        routes: Optional[List[Dict[str, Any]]] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
        args_summary: Optional[bool] = None,
        profiling: Optional[bool] = None,
        codes: Optional[Dict[str, Dict[str, Any]]] = None,
        signals: Optional[Dict[str, Dict[str, Any]]] = None,
        strict_signals: Optional[bool] = None,
        strict_schema: Optional[bool] = None,
        enabled: Optional[bool] = None,
        profiling_buffer_size: Optional[int] = None,
        profiling_hooks: Optional[List[Any]] = None,
        profiling_sample_rate: Optional[float] = None,
        event_buffer_size: Optional[int] = None,
    ) -> None:
        if level is not None:
            self._config.level = level
        if theme is not None:
            self._config.theme = theme
        if capture_warnings is not None:
            self._config.capture_warnings = capture_warnings
        if capture_logging is not None:
            self._config.capture_logging = capture_logging
        if capture_exceptions is not None:
            self._config.capture_exceptions = capture_exceptions
        if trace_depth is not None:
            self._config.trace_depth = trace_depth
        if show_traceback is not None:
            self._config.show_traceback = show_traceback
        if profile is not None:
            self._config.profile = profile
        if args_summary is not None:
            self._config.args_summary = args_summary
        if profiling is not None:
            self._config.profiling = profiling
        if codes is not None:
            self._codes = codes
        if signals is not None:
            self._signals = signals
        if strict_signals is not None:
            self._config.strict_signals = strict_signals
        if strict_schema is not None:
            self._config.strict_schema = strict_schema
        if enabled is not None:
            self._config.enabled = enabled
        if profiling_buffer_size is not None:
            self._config.profiling_buffer_size = profiling_buffer_size
        if profiling_hooks is not None:
            self._config.profiling_hooks = profiling_hooks
        if profiling_sample_rate is not None:
            self._config.profiling_sample_rate = profiling_sample_rate
        if event_buffer_size is not None:
            self._config.event_buffer_size = event_buffer_size
        
        if handlers is not None:
            self._handlers = list(handlers)
        elif not self._handlers:
            # Automatic setup of default console handler
            self._setup_default_handler()

        if routes is not None:
            self._policy.set_routes(routes)
        if filters is not None:
            self._policy.set_filters(filters)

        # Enable/disable emitters based on config
        from ..emitters.warnings import enable_warnings, disable_warnings
        from ..emitters.logging import enable_logging, disable_logging
        from ..emitters.exceptions import enable_exceptions, disable_exceptions
        if self._config.capture_logging:
            enable_logging(capture_warnings=self._config.capture_warnings)
            if self._config.capture_warnings:
                disable_warnings()
            else:
                enable_warnings()
        else:
            disable_logging()
            if self._config.capture_warnings:
                enable_warnings()
            else:
                disable_warnings()
        if self._config.capture_exceptions:
            enable_exceptions()
        else:
            disable_exceptions()

    def _setup_default_handler(self) -> None:
        """Internal helper to setup the best available console handler based on theme."""
        if self._config.theme == "rich":
            try:
                from ..handlers.console import RichConsoleHandler
                self._handlers = [RichConsoleHandler()]
                return
            except (ImportError, Exception):
                pass
        
        from ..handlers.console import ConsoleHandler
        self._handlers = [ConsoleHandler()]

    def add_handler(self, handler: Any) -> None:
        self._handlers.append(handler)

    def remove_handler(self, handler: Any) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def record_call(self) -> None:
        self._counts["calls_total"] += 1

    def record_timing(
        self,
        key: str,
        duration_ms: float,
        *,
        span: bool = False,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._timings.setdefault(key, []).append(duration_ms)
        # timeline buffer
        if self._config.profiling_buffer_size > 0:
            entry = {
                "key": key,
                "duration_ms": duration_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            if span:
                entry["span"] = True
            if meta:
                entry["meta"] = meta
            self._timeline.append(entry)
            if len(self._timeline) > self._config.profiling_buffer_size:
                self._timeline.pop(0)

    def emit(
        self,
        level: str,
        message: str,
        *,
        source: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        category: Optional[str] = None,
        code: Optional[str] = None,
        tags: Optional[List[str]] = None,
        exception_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self._config.enabled:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level,
                "source": source,
                "message": message,
                "context": None,
                "extra": extra or {},
                "category": category,
                "code": code,
                "tags": tags,
                "exception_type": exception_type,
            }
        code_meta = self._codes.get(code) if code else None
        if code_meta and (message is None or message == ""):
            # Fallback to code-specific message per profile
            if self._config.profile == "user":
                message = code_meta.get("user_message", "")
            elif self._config.profile == "qa":
                message = code_meta.get("qa_message", "")
            elif self._config.profile == "agent":
                message = code_meta.get("agent_message", "")
            else:
                message = code_meta.get("dev_message", "") or code_meta.get("message", "")

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "source": source,
            "message": message,
            "context": get_context(self._config.trace_depth),
            "extra": extra or {},
            "category": category,
            "code": code,
            "tags": tags,
            "exception_type": exception_type,
        }
        # mark as smonitor-emitted
        event["extra"].setdefault("smonitor", True)

        # Interpolate message and hint using extra fields if templated
        if event["message"] and "{" in event["message"]:
            try:
                event["message"] = event["message"].format(**event["extra"])
            except Exception:
                pass

        if code_meta:
            event["extra"].setdefault("title", code_meta.get("title"))
            if self._config.profile == "user":
                event["extra"].setdefault("hint", code_meta.get("user_hint"))
            elif self._config.profile == "qa":
                event["extra"].setdefault("hint", code_meta.get("qa_hint") or code_meta.get("dev_hint"))
            elif self._config.profile == "agent":
                event["extra"].setdefault("hint", code_meta.get("agent_hint") or code_meta.get("dev_hint"))
            else:
                event["extra"].setdefault("hint", code_meta.get("dev_hint"))

        hint = event["extra"].get("hint")
        if hint and "{" in hint:
            try:
                event["extra"]["hint"] = hint.format(**event["extra"])
            except Exception:
                pass

        # Soft enforcement for signals/contracts in dev/qa profiles
        if self._config.profile in {"dev", "qa"} and source:
            contract = self._signals.get(source)
            if contract:
                required = contract.get("extra_required", [])
                missing = [k for k in required if k not in event["extra"]]
                if missing:
                    msg = f"Missing extra fields: {', '.join(missing)}"
                    if self._config.strict_signals:
                        raise ValueError(msg)
                    event["extra"].setdefault("contract_warning", msg)
            elif code is None:
                msg = "Missing code for event (dev/qa profile)."
                if self._config.strict_signals:
                    raise ValueError(msg)
                event["extra"].setdefault("contract_warning", msg)

        # Event schema validation (dev/qa only)
        if self._config.profile in {"dev", "qa"}:
            errors = validate_event(event)
            if errors:
                if self._config.strict_schema:
                    raise ValueError("; ".join(errors))
                event["extra"].setdefault("schema_warning", "; ".join(errors))

        if level == "WARNING":
            self._counts["warnings_total"] += 1
        if level == "ERROR":
            self._counts["errors_total"] += 1

        routed_event, target_handlers = self._policy.apply(event, self._handlers)
        for handler in target_handlers:
            try:
                handler.handle(routed_event, profile=self._config.profile)
            except Exception:
                # Handlers must not raise
                name = getattr(handler, "name", handler.__class__.__name__)
                self._handler_errors[name] = self._handler_errors.get(name, 0) + 1

        self._record_event(routed_event)
        return event

    def _record_event(self, event: Dict[str, Any]) -> None:
        size = self._config.event_buffer_size
        if size <= 0:
            return
        from copy import deepcopy

        self._event_buffer.append(deepcopy(event))
        if len(self._event_buffer) > size:
            self._event_buffer.pop(0)

    def recent_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if limit is None:
            return list(self._event_buffer)
        if limit <= 0:
            return []
        return list(self._event_buffer[-limit:])

    def report(self) -> Dict[str, Any]:
        timings_summary = {}
        for key, values in self._timings.items():
            if not values:
                continue
            values_sorted = sorted(values)
            n = len(values_sorted)
            p50 = values_sorted[int(0.5 * (n - 1))]
            p95 = values_sorted[int(0.95 * (n - 1))]
            timings_summary[key] = {
                "count": n,
                "p50_ms": p50,
                "p95_ms": p95,
                "max_ms": max(values_sorted),
            }
        # Aggregate by module prefix
        timings_by_module: Dict[str, Dict[str, float]] = {}
        for key, summary in timings_summary.items():
            module = key.rsplit(".", 1)[0] if "." in key else key
            mod = timings_by_module.setdefault(module, {"count": 0, "p50_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0})
            mod["count"] += summary["count"]
            mod["p50_ms"] = max(mod["p50_ms"], summary["p50_ms"])
            mod["p95_ms"] = max(mod["p95_ms"], summary["p95_ms"])
            mod["max_ms"] = max(mod["max_ms"], summary["max_ms"])

        profiling_meta = {}
        hooks = self._config.profiling_hooks or []
        for hook in hooks:
            try:
                data = hook()
                if isinstance(data, dict):
                    profiling_meta.update(data)
            except Exception:
                continue
        return {
            **self._counts,
            "handler_errors": dict(self._handler_errors),
            "timings": timings_summary,
            "timings_by_module": timings_by_module,
            "timeline": list(self._timeline),
            "profiling_meta": profiling_meta,
            "peak_memory": None,
            "events_buffered": len(self._event_buffer),
        }

    def get_codes(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._codes)

    def get_signals(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._signals)


_manager_singleton: Optional[Manager] = None


def get_manager() -> Manager:
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = Manager()
    return _manager_singleton
