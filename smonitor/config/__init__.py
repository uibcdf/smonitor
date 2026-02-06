from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from .discovery import discover_config


def load_project_config(start: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    base = start or Path.cwd()
    return discover_config(base)


def build_effective_config(project_cfg: Optional[Dict[str, Any]], overrides: Dict[str, Any]) -> Dict[str, Any]:
    if not project_cfg:
        return dict(overrides)

    smonitor_cfg = project_cfg.get("SMONITOR", {}) or {}
    profiles = project_cfg.get("PROFILES", {}) or {}
    profile_name = overrides.get("profile") or project_cfg.get("PROFILE")

    effective = dict(smonitor_cfg)
    if profile_name and profile_name in profiles:
        effective.update(profiles[profile_name] or {})
        effective.setdefault("profile", profile_name)

    # Apply overrides (highest priority)
    effective.update({k: v for k, v in overrides.items() if v is not None})
    return effective


def load_env_config() -> Dict[str, Any]:
    def _get_bool(key: str) -> Optional[bool]:
        val = os.getenv(key)
        if val is None:
            return None
        return val.strip().lower() in {"1", "true", "yes", "on"}

    def _get_int(key: str) -> Optional[int]:
        val = os.getenv(key)
        if val is None:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    return {
        "profile": os.getenv("SMONITOR_PROFILE"),
        "level": os.getenv("SMONITOR_LEVEL"),
        "trace_depth": _get_int("SMONITOR_TRACE_DEPTH"),
        "capture_warnings": _get_bool("SMONITOR_CAPTURE_WARNINGS"),
        "capture_logging": _get_bool("SMONITOR_CAPTURE_LOGGING"),
        "capture_exceptions": _get_bool("SMONITOR_CAPTURE_EXCEPTIONS"),
        "show_traceback": _get_bool("SMONITOR_SHOW_TRACEBACK"),
        "args_summary": _get_bool("SMONITOR_ARGS_SUMMARY"),
        "profiling": _get_bool("SMONITOR_PROFILING"),
        "strict_signals": _get_bool("SMONITOR_STRICT_SIGNALS"),
        "strict_schema": _get_bool("SMONITOR_STRICT_SCHEMA"),
        "enabled": _get_bool("SMONITOR_ENABLED"),
        "profiling_buffer_size": _get_int("SMONITOR_PROFILING_BUFFER"),
        "profiling_sample_rate": float(os.getenv("SMONITOR_PROFILING_SAMPLE", "1.0")),
        "event_buffer_size": _get_int("SMONITOR_EVENT_BUFFER"),
    }


def extract_policy(project_cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not project_cfg:
        return {}
    return {
        "routes": project_cfg.get("ROUTES"),
        "filters": project_cfg.get("FILTERS"),
    }


def extract_codes(project_cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not project_cfg:
        return {}
    return project_cfg.get("CODES") or {}


def extract_signals(project_cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not project_cfg:
        return {}
    return project_cfg.get("SIGNALS") or {}


def validate_config(project_cfg: Optional[Dict[str, Any]]) -> list[str]:
    if not project_cfg:
        return []
    errors: list[str] = []
    allowed_top = {"PROFILE", "SMONITOR", "PROFILES", "ROUTES", "FILTERS", "CODES", "SIGNALS"}
    for key in project_cfg.keys():
        if key not in allowed_top:
            errors.append(f"Unknown top-level key: {key}")

    if "SMONITOR" in project_cfg and not isinstance(project_cfg["SMONITOR"], dict):
        errors.append("SMONITOR must be a dict")
    if "PROFILES" in project_cfg and not isinstance(project_cfg["PROFILES"], dict):
        errors.append("PROFILES must be a dict")
    if "ROUTES" in project_cfg and not isinstance(project_cfg["ROUTES"], list):
        errors.append("ROUTES must be a list")
    if "FILTERS" in project_cfg and not isinstance(project_cfg["FILTERS"], list):
        errors.append("FILTERS must be a list")
    if "CODES" in project_cfg and not isinstance(project_cfg["CODES"], dict):
        errors.append("CODES must be a dict")
    if "SIGNALS" in project_cfg and not isinstance(project_cfg["SIGNALS"], dict):
        errors.append("SIGNALS must be a dict")
    return errors
