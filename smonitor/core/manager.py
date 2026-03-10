from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import time
from typing import Any, Dict, Iterable, List, Optional

from ..policy.engine import PolicyEngine
from ..validation import validate_event
from .context import get_context
from .fingerprint import build_event_fingerprint
from .identifiers import new_identifier

_LEVEL_ORDER = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
}


def _level_value(level: str) -> int:
    return _LEVEL_ORDER.get(str(level).upper(), _LEVEL_ORDER["INFO"])


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
    silence: list[str] = field(default_factory=list)
    handler_error_threshold: int = 0
    slow_signal_ms: float = 0.0
    slow_signal_level: str = "INFO"
    warning_coalesce_window_s: float = 0.0


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
        self._runtime_warnings: List[str] = []
        self._degraded_handlers_announced: set[str] = set()
        self._warning_coalesce_state: Dict[str, Dict[str, Any]] = {}
        self._coalesced_warning_summaries: List[Dict[str, Any]] = []
        self._session_id = new_identifier()
        self._run_id = new_identifier()
        self._default_correlation_id: Optional[str] = None

    def _apply_config_dict(self, data: Dict[str, Any]) -> None:
        """Applies a configuration dictionary (e.g. from _smonitor.py) to the manager."""
        config_block = data.get("SMONITOR", {})
        self.configure(
            level=config_block.get("level"),
            theme=config_block.get("theme"),
            capture_warnings=config_block.get("capture_warnings"),
            capture_logging=config_block.get("capture_logging"),
            capture_exceptions=config_block.get("capture_exceptions"),
            trace_depth=config_block.get("trace_depth"),
            show_traceback=config_block.get("show_traceback"),
            args_summary=config_block.get("args_summary"),
            profiling=config_block.get("profiling"),
            strict_signals=config_block.get("strict_signals"),
            strict_schema=config_block.get("strict_schema"),
            enabled=config_block.get("enabled"),
            event_buffer_size=config_block.get("event_buffer_size"),
            silence=config_block.get("silence"),
            handler_error_threshold=config_block.get("handler_error_threshold"),
            slow_signal_ms=config_block.get("slow_signal_ms"),
            slow_signal_level=config_block.get("slow_signal_level"),
            warning_coalesce_window_s=config_block.get("warning_coalesce_window_s"),
        )
        if profile := data.get("PROFILE"):
            self.configure(profile=profile)
        if routes := data.get("ROUTES"):
            self.configure(routes=routes)
        if filters := data.get("FILTERS"):
            self.configure(filters=filters)
        if codes := data.get("CODES"):
            self.configure(codes=codes)
        if signals := data.get("SIGNALS"):
            self.configure(signals=signals)

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
        config_path: Optional[str | Path] = None,
        silence: Optional[List[str]] = None,
        handler_error_threshold: Optional[int] = None,
        slow_signal_ms: Optional[float] = None,
        slow_signal_level: Optional[str] = None,
        warning_coalesce_window_s: Optional[float] = None,
        run_id: Optional[str] = None,
        session_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        if config_path is not None:
            from ..config.discovery import discover_config, load_config_from_path
            p = Path(config_path)
            data = load_config_from_path(p) if p.is_file() else discover_config(p)
            if data:
                # Apply discovery data first, so manual args can override them below
                self._apply_config_dict(data)

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
        if silence is not None:
            self._config.silence = silence
        if handler_error_threshold is not None:
            self._config.handler_error_threshold = handler_error_threshold
        if slow_signal_ms is not None:
            self._config.slow_signal_ms = slow_signal_ms
        if slow_signal_level is not None:
            self._config.slow_signal_level = slow_signal_level
        if warning_coalesce_window_s is not None:
            self._config.warning_coalesce_window_s = warning_coalesce_window_s
        if run_id is not None:
            self._run_id = run_id
        if session_id is not None:
            self._session_id = session_id
        if correlation_id is not None:
            self._default_correlation_id = correlation_id
        
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
        from ..emitters.exceptions import disable_exceptions, enable_exceptions
        from ..emitters.logging import disable_logging, enable_logging
        from ..emitters.warnings import disable_warnings, enable_warnings
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
        tags: Optional[List[str]] = None,
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
            if tags:
                entry["tags"] = list(tags)
            self._timeline.append(entry)
            if len(self._timeline) > self._config.profiling_buffer_size:
                self._timeline.pop(0)

    def resolve(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, Optional[str]]:
        """Resolves a message and hint from code/template without emitting an event."""
        resolved_msg, hint, _ = self._resolve_message_and_hint(message or "", code, extra or {})
        return resolved_msg, hint

    def _resolve_message_and_hint(
        self, message: str, code: Optional[str], extra: Dict[str, Any]
    ) -> tuple[str, Optional[str], Optional[Dict[str, Any]]]:
        """Internal helper to resolve profile-based messages and hints."""
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

        # Interpolate message using extra fields if templated
        if message and "{" in message:
            try:
                message = message.format(**extra)
            except Exception:
                pass

        hint = None
        if code_meta:
            if self._config.profile == "user":
                hint = code_meta.get("user_hint")
            elif self._config.profile == "qa":
                hint = code_meta.get("qa_hint") or code_meta.get("dev_hint")
            elif self._config.profile == "agent":
                hint = code_meta.get("agent_hint") or code_meta.get("dev_hint")
            else:
                hint = code_meta.get("dev_hint")

        if hint and "{" in hint:
            try:
                hint = hint.format(**extra)
            except Exception:
                pass

        return message, hint, code_meta

    def _coalesce_warning_key(self, event: Dict[str, Any]) -> Optional[str]:
        if event.get("level") != "WARNING":
            return None
        if event.get("code") == "SMONITOR-WARNING-COALESCED":
            return None
        if self._config.warning_coalesce_window_s <= 0:
            return None
        extra = event.get("extra") or {}
        parts = [
            str(event.get("code") or ""),
            str(event.get("source") or ""),
            str(extra.get("resource") or ""),
            str(extra.get("caller") or ""),
            str(event.get("message") or ""),
        ]
        return "|".join(parts)

    def _build_coalesced_warning_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "code": state.get("code"),
            "source": state.get("source"),
            "resource": state.get("resource"),
            "caller": state.get("caller"),
            "suppressed_count": state.get("count", 0),
            "total_occurrences": state.get("count", 0) + 1,
            "message": state.get("message"),
            "last_message": state.get("message"),
            "retry_attempt": state.get("retry_attempt"),
            "retry_max": state.get("retry_max"),
            "retry_exhausted": state.get("retry_exhausted"),
            "retry_delay_s": state.get("retry_delay_s"),
            "failure_class": state.get("failure_class"),
            "last_failure_reason": state.get("last_failure_reason"),
            "cause_exception_type": state.get("cause_exception_type"),
            "cause_code": state.get("cause_code"),
            "causal_chain": state.get("causal_chain"),
        }

    def _finalize_coalesced_warning(self, key: str) -> Optional[Dict[str, Any]]:
        state = self._warning_coalesce_state.get(key)
        if not state or state.get("count", 0) <= 0:
            return None
        summary = self._build_coalesced_warning_summary(state)
        self._coalesced_warning_summaries.append(summary)
        self._coalesced_warning_summaries = self._coalesced_warning_summaries[-20:]
        self._warning_coalesce_state[key] = {
            **state,
            "count": 0,
        }
        self.emit(
            "INFO",
            "Coalesced repeated warning events.",
            source=state.get("source"),
            category="diagnostics",
            code="SMONITOR-WARNING-COALESCED",
            extra=summary,
        )
        return summary

    def flush_coalesced_warnings(self) -> List[Dict[str, Any]]:
        summaries: List[Dict[str, Any]] = []
        for key in list(self._warning_coalesce_state):
            summary = self._finalize_coalesced_warning(key)
            if summary is not None:
                summaries.append(summary)
        return summaries

    def _maybe_coalesce_warning(self, event: Dict[str, Any]) -> bool:
        key = self._coalesce_warning_key(event)
        if key is None:
            return False
        now = time()
        state = self._warning_coalesce_state.get(key)
        if state is None:
            self._warning_coalesce_state[key] = {
                "count": 0,
                "last_timestamp": now,
                "message": event.get("message"),
                "source": event.get("source"),
                "code": event.get("code"),
                "resource": (event.get("extra") or {}).get("resource"),
                "caller": (event.get("extra") or {}).get("caller"),
                "retry_attempt": (event.get("extra") or {}).get("retry_attempt"),
                "retry_max": (event.get("extra") or {}).get("retry_max"),
                "retry_exhausted": (event.get("extra") or {}).get("retry_exhausted"),
                "retry_delay_s": (event.get("extra") or {}).get("retry_delay_s"),
                "failure_class": (event.get("extra") or {}).get("failure_class"),
                "last_failure_reason": (event.get("extra") or {}).get("last_failure_reason"),
                "cause_exception_type": (event.get("extra") or {}).get("cause_exception_type"),
                "cause_code": (event.get("extra") or {}).get("cause_code"),
                "causal_chain": (event.get("extra") or {}).get("causal_chain"),
            }
            return False
        if now - state["last_timestamp"] > self._config.warning_coalesce_window_s:
            self._finalize_coalesced_warning(key)
            self._warning_coalesce_state[key] = {
                "count": 0,
                "last_timestamp": now,
                "message": event.get("message"),
                "source": event.get("source"),
                "code": event.get("code"),
                "resource": (event.get("extra") or {}).get("resource"),
                "caller": (event.get("extra") or {}).get("caller"),
                "retry_attempt": (event.get("extra") or {}).get("retry_attempt"),
                "retry_max": (event.get("extra") or {}).get("retry_max"),
                "retry_exhausted": (event.get("extra") or {}).get("retry_exhausted"),
                "retry_delay_s": (event.get("extra") or {}).get("retry_delay_s"),
                "failure_class": (event.get("extra") or {}).get("failure_class"),
                "last_failure_reason": (event.get("extra") or {}).get("last_failure_reason"),
                "cause_exception_type": (event.get("extra") or {}).get("cause_exception_type"),
                "cause_code": (event.get("extra") or {}).get("cause_code"),
                "causal_chain": (event.get("extra") or {}).get("causal_chain"),
            }
            return False
        state["count"] += 1
        state["last_timestamp"] = now
        state["message"] = event.get("message")
        extra = event.get("extra") or {}
        for extra_key in (
            "retry_attempt",
            "retry_max",
            "retry_exhausted",
            "retry_delay_s",
            "failure_class",
            "last_failure_reason",
            "cause_exception_type",
            "cause_code",
            "causal_chain",
        ):
            if extra_key in extra:
                state[extra_key] = extra.get(extra_key)
        self._warning_coalesce_state[key] = state
        return True

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
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        extra_data = extra or {}
        resolved_correlation_id = (
            correlation_id
            or extra_data.get("correlation_id")
            or self._default_correlation_id
        )
        if not self._config.enabled:
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": level,
                "source": source,
                "message": message,
                "context": None,
                "extra": extra_data,
                "category": category,
                "code": code,
                "tags": tags,
                "exception_type": exception_type,
                "run_id": self._run_id,
                "session_id": self._session_id,
                "correlation_id": resolved_correlation_id,
                "fingerprint": build_event_fingerprint(
                    code=code,
                    source=source,
                    exception_type=exception_type,
                    extra=extra_data,
                ),
            }

        # Filter out silenced sources
        if source and self._config.silence:
            for s in self._config.silence:
                if source == s or source.startswith(s + "."):
                    return {}

        message, hint, code_meta = self._resolve_message_and_hint(message, code, extra_data)

        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": str(level).upper(),
            "source": source,
            "message": message,
            "context": get_context(self._config.trace_depth),
            "extra": extra_data,
            "category": category,
            "code": code,
            "tags": tags,
            "exception_type": exception_type,
            "run_id": self._run_id,
            "session_id": self._session_id,
            "correlation_id": resolved_correlation_id,
            "fingerprint": build_event_fingerprint(
                code=code,
                source=source,
                exception_type=exception_type,
                extra=extra_data,
            ),
        }
        # mark as smonitor-emitted
        event["extra"].setdefault("smonitor", True)

        if code_meta:
            event["extra"].setdefault("title", code_meta.get("title"))
        
        if hint:
            event["extra"].setdefault("hint", hint)

        # Honor configured threshold before routing/printing.
        if _level_value(event["level"]) < _level_value(self._config.level):
            return event

        if self._maybe_coalesce_warning(event):
            return event

        # Soft enforcement for signals/contracts in dev/qa profiles
        if self._config.profile in {"dev", "qa"} and source:
            contract = self._signals.get(source)
            if contract is None:
                # Backward-compatible fallback: match nearest source prefix.
                # Example: source "pkg.mod.func" can match SIGNALS["pkg.mod"].
                parts = source.split(".")
                for idx in range(len(parts) - 1, 0, -1):
                    prefix = ".".join(parts[:idx])
                    contract = self._signals.get(prefix)
                    if contract is not None:
                        break
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

        if event["level"] == "WARNING":
            self._counts["warnings_total"] += 1
        if event["level"] == "ERROR":
            self._counts["errors_total"] += 1

        routed_event, target_handlers = self._policy.apply(event, self._handlers)
        for handler in target_handlers:
            try:
                handler.handle(routed_event, profile=self._config.profile)
            except Exception:
                # Handlers must not raise
                name = getattr(handler, "name", handler.__class__.__name__)
                self._handler_errors[name] = self._handler_errors.get(name, 0) + 1
                threshold = self._config.handler_error_threshold
                count = self._handler_errors[name]
                if (
                    threshold > 0
                    and count >= threshold
                    and name not in self._degraded_handlers_announced
                ):
                    warning_msg = (
                        f"Handler '{name}' reached error threshold "
                        f"({count}/{threshold}) and is considered degraded."
                    )
                    self._runtime_warnings.append(warning_msg)
                    self._degraded_handlers_announced.add(name)
                    warnings.warn(warning_msg, RuntimeWarning, stacklevel=2)

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
            mod = timings_by_module.setdefault(
                module,
                {"count": 0, "p50_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0},
            )
            mod["count"] += summary["count"]
            mod["p50_ms"] = max(mod["p50_ms"], summary["p50_ms"])
            mod["p95_ms"] = max(mod["p95_ms"], summary["p95_ms"])
            mod["max_ms"] = max(mod["max_ms"], summary["max_ms"])

        timings_by_tag: Dict[str, Dict[str, float]] = {}
        durations_by_tag: Dict[str, List[float]] = {}
        for entry in self._timeline:
            if "duration_ms" not in entry:
                continue
            for tag in entry.get("tags", []) or []:
                durations_by_tag.setdefault(tag, []).append(entry["duration_ms"])

        for tag, values in durations_by_tag.items():
            values_sorted = sorted(values)
            n = len(values_sorted)
            timings_by_tag[tag] = {
                "count": n,
                "p50_ms": values_sorted[int(0.5 * (n - 1))],
                "p95_ms": values_sorted[int(0.95 * (n - 1))],
                "max_ms": max(values_sorted),
            }

        events_by_code: Dict[str, int] = {}
        events_by_category: Dict[str, int] = {}
        events_by_fingerprint: Dict[str, int] = {}
        slow_signals_recent: List[Dict[str, Any]] = []
        coalesced_warnings: List[Dict[str, Any]] = list(self._coalesced_warning_summaries)
        for event in self._event_buffer:
            code = event.get("code")
            if code:
                events_by_code[str(code)] = events_by_code.get(str(code), 0) + 1
            category = event.get("category")
            if category:
                events_by_category[str(category)] = events_by_category.get(str(category), 0) + 1
            fingerprint = event.get("fingerprint")
            if fingerprint:
                key = str(fingerprint)
                events_by_fingerprint[key] = events_by_fingerprint.get(key, 0) + 1
            if code == "SMONITOR-SIGNAL-SLOW":
                extra = event.get("extra") or {}
                slow_signals_recent.append(
                    {
                        "timestamp": event.get("timestamp"),
                        "source": event.get("source"),
                        "duration_ms": extra.get("duration_ms"),
                        "threshold_ms": extra.get("threshold_ms"),
                        "signal_tags": extra.get("signal_tags") or event.get("tags"),
                    }
                )
        slow_signals_recent = slow_signals_recent[-10:]
        for state in self._warning_coalesce_state.values():
            if state.get("count", 0) > 0:
                coalesced_warnings.append(self._build_coalesced_warning_summary(state))
        coalesced_warnings = coalesced_warnings[-20:]

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
            "run_id": self._run_id,
            "session_id": self._session_id,
            "handler_errors": dict(self._handler_errors),
            "handler_errors_total": sum(self._handler_errors.values()),
            "degraded_handlers": [
                name for name, count in self._handler_errors.items() if count > 0
            ],
            "timings": timings_summary,
            "timings_by_module": timings_by_module,
            "timings_by_tag": timings_by_tag,
            "timeline": list(self._timeline),
            "profiling_meta": profiling_meta,
            "peak_memory": None,
            "events_buffered": len(self._event_buffer),
            "runtime_warnings": list(self._runtime_warnings),
            "events_by_code": events_by_code,
            "events_by_category": events_by_category,
            "events_by_fingerprint": events_by_fingerprint,
            "slow_signals_recent": slow_signals_recent,
            "coalesced_warnings": coalesced_warnings,
        }

    def get_codes(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._codes)

    def get_signals(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._signals)

    def get_runtime_identifiers(self) -> Dict[str, Optional[str]]:
        return {
            "run_id": self._run_id,
            "session_id": self._session_id,
            "correlation_id": self._default_correlation_id,
        }


_manager_singleton: Optional[Manager] = None


def get_manager() -> Manager:
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = Manager()
    return _manager_singleton
