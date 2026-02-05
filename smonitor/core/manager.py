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
        if handlers is not None:
            self._handlers = list(handlers)
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

    def add_handler(self, handler: Any) -> None:
        self._handlers.append(handler)

    def remove_handler(self, handler: Any) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def record_call(self) -> None:
        self._counts["calls_total"] += 1

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
                    event["extra"].setdefault(
                        "contract_warning",
                        f"Missing extra fields: {', '.join(missing)}",
                    )
            elif code is None:
                event["extra"].setdefault(
                    "contract_warning",
                    "Missing code for event (dev/qa profile).",
                )

        # Event schema validation (dev/qa only)
        if self._config.profile in {"dev", "qa"}:
            errors = validate_event(event)
            if errors:
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
                pass

        return event

    def report(self) -> Dict[str, Any]:
        return {
            **self._counts,
            "peak_memory": None,
        }


_manager_singleton: Optional[Manager] = None


def get_manager() -> Manager:
    global _manager_singleton
    if _manager_singleton is None:
        _manager_singleton = Manager()
    return _manager_singleton
