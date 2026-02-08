from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

import smonitor
from .core import emit_from_catalog, merge_extra

T = TypeVar("T", bound="CatalogException")
W = TypeVar("W", bound="CatalogWarning")


class CatalogException(Exception):
    """Base class for exceptions backed by an SMonitor catalog.

    Subclasses should define `catalog_key`.
    """

    catalog_key: str | None = None

    def __init__(
        self,
        *,
        message: Optional[str] = None,
        code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        catalog: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        target_code = code
        # If no code but we have a key, try to find the code in the catalog
        if not target_code and self.catalog_key and catalog:
            entry = catalog.get("exceptions", {}).get(self.catalog_key)
            if entry:
                target_code = entry.get("code")

        resolved_msg, hint = smonitor.resolve(
            message=message, code=target_code, extra=merge_extra(meta, extra)
        )

        full_message = resolved_msg
        if hint:
            full_message = f"{full_message} {hint}" if full_message else hint

        super().__init__(full_message)


class CatalogWarning(Warning):
    """Base class for warnings backed by an SMonitor catalog."""

    catalog_key: str | None = None

    def __init__(
        self,
        *,
        message: Optional[str] = None,
        code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        catalog: Optional[Dict[str, Any]] = None,
        meta: Optional[Dict[str, Any]] = None,
    ):
        target_code = code
        if not target_code and self.catalog_key and catalog:
            entry = catalog.get("warnings", {}).get(self.catalog_key)
            if entry:
                target_code = entry.get("code")

        resolved_msg, hint = smonitor.resolve(
            message=message, code=target_code, extra=merge_extra(meta, extra)
        )

        full_message = resolved_msg
        if hint:
            full_message = f"{full_message} {hint}" if full_message else hint

        self.message = full_message
        super().__init__(full_message)


class DiagnosticBundle:
    """A bundle of diagnostic tools for a library integration."""

    def __init__(
        self,
        catalog: Dict[str, Any],
        meta: Dict[str, Any],
        package_root: Path,
    ):
        self.catalog = catalog
        self.meta = meta
        self.package_root = package_root
        self._warned_once_cache: set[tuple[Type[Warning], str]] = set()

    def warn(
        self,
        message_or_warning: str | Warning,
        category: Optional[Type[Warning]] = None,
        *,
        stacklevel: int = 2,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if isinstance(message_or_warning, Warning):
            cls_name = type(message_or_warning).__name__
            msg = str(message_or_warning)
            cat = type(message_or_warning)
        else:
            cat = category or UserWarning
            cls_name = cat.__name__
            msg = message_or_warning

        if cls_name in self.catalog.get("warnings", {}):
            try:
                emit_from_catalog(
                    self.catalog["warnings"][cls_name],
                    package_root=self.package_root,
                    extra=merge_extra(self.meta, {**(extra or {}), "message": msg}),
                    meta=self.meta,
                )
                return
            except Exception:
                pass

        if isinstance(message_or_warning, Warning):
            warnings.warn(message_or_warning, stacklevel=stacklevel)
        else:
            warnings.warn(msg, cat, stacklevel=stacklevel)

    def warn_once(
        self,
        message_or_warning: str | Warning,
        category: Optional[Type[Warning]] = None,
        *,
        stacklevel: int = 2,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        if isinstance(message_or_warning, Warning):
            msg, cat = str(message_or_warning), type(message_or_warning)
        else:
            msg, cat = message_or_warning, category or UserWarning

        key = (cat, msg)
        if key in self._warned_once_cache:
            return
        self._warned_once_cache.add(key)
        self.warn(message_or_warning, category, stacklevel=stacklevel, extra=extra)

    def resolve(
        self,
        message: Optional[str] = None,
        *,
        code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Resolves and combines message and hint into a single string."""
        resolved_msg, hint = smonitor.resolve(
            message=message, code=code, extra=merge_extra(self.meta, extra)
        )
        if hint:
            return f"{resolved_msg} {hint}" if resolved_msg else hint
        return resolved_msg or ""
