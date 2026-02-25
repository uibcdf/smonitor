from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import smonitor

_configured_packages: set[str] = set()


def ensure_configured(package_root: Path) -> None:
    key = str(package_root.resolve())
    if key in _configured_packages:
        return
    smonitor.configure(config_path=package_root)
    _configured_packages.add(key)


def reset_configured_packages() -> None:
    """Clears the package configuration memoization cache.

    Useful for test suites and dynamic multi-config sessions.
    """
    _configured_packages.clear()


def merge_extra(meta: Optional[Dict[str, Any]], extra: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    if meta:
        merged.update(meta)
    if extra:
        merged.update(extra)
    return merged


def emit_from_catalog(
    entry: Dict[str, Any],
    *,
    extra: Optional[Dict[str, Any]] = None,
    package_root: Optional[Path] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if package_root is not None:
        ensure_configured(package_root)
    return smonitor.emit(
        entry.get("level", "WARNING"),
        "",
        source=entry.get("source"),
        code=entry.get("code"),
        category=entry.get("category"),
        extra=merge_extra(meta, extra),
    )
