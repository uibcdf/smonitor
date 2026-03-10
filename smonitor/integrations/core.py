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




def context_extra(
    *,
    caller: Optional[str] = None,
    form: Optional[str] = None,
    requested_attribute: Optional[str] = None,
    resource: Optional[str] = None,
    provider: Optional[str] = None,
    operation: Optional[str] = None,
    retry_attempt: Optional[int] = None,
    retry_max: Optional[int] = None,
    retry_exhausted: Optional[bool] = None,
    retry_delay_s: Optional[float] = None,
    failure_class: Optional[str] = None,
    last_failure_reason: Optional[str] = None,
    cause_exception_type: Optional[str] = None,
    cause_code: Optional[str] = None,
    causal_chain: Optional[Any] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if caller is not None:
        payload["caller"] = caller
    if form is not None:
        payload["form"] = form
    if requested_attribute is not None:
        payload["requested_attribute"] = requested_attribute
    if resource is not None:
        payload["resource"] = resource
    if provider is not None:
        payload["provider"] = provider
    if operation is not None:
        payload["operation"] = operation
    if retry_attempt is not None:
        payload["retry_attempt"] = retry_attempt
    if retry_max is not None:
        payload["retry_max"] = retry_max
    if retry_exhausted is not None:
        payload["retry_exhausted"] = retry_exhausted
    if retry_delay_s is not None:
        payload["retry_delay_s"] = retry_delay_s
    if failure_class is not None:
        payload["failure_class"] = failure_class
    if last_failure_reason is not None:
        payload["last_failure_reason"] = last_failure_reason
    if cause_exception_type is not None:
        payload["cause_exception_type"] = cause_exception_type
    if cause_code is not None:
        payload["cause_code"] = cause_code
    if causal_chain is not None:
        payload["causal_chain"] = causal_chain
    if extra:
        payload.update(extra)
    return payload


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
