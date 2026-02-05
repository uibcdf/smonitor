from __future__ import annotations

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


def extract_policy(project_cfg: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not project_cfg:
        return {}
    return {
        "routes": project_cfg.get("ROUTES"),
        "filters": project_cfg.get("FILTERS"),
    }
