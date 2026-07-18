from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

import smonitor

from .core import emit_from_catalog, merge_extra

T = TypeVar("T", bound="CatalogException")
W = TypeVar("W", bound="CatalogWarning")


def _catalog_entry(
    catalog: Optional[Dict[str, Any]],
    group: str,
    key: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not catalog or not key:
        return None
    nested = catalog.get(group, {})
    if isinstance(nested, dict):
        entry = nested.get(key)
        if isinstance(entry, dict):
            return entry
    # Backward-compatible fallback for flat catalogs keyed directly by class/key.
    flat = catalog.get(key)
    if isinstance(flat, dict):
        return flat
    return None


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
            entry = _catalog_entry(catalog, "exceptions", self.catalog_key)
            if entry:
                target_code = entry.get("code")

        resolved_extra = merge_extra(meta, extra)
        resolved_msg, hint = smonitor.resolve(
            message=message, code=target_code, extra=resolved_extra
        )

        full_message = resolved_msg
        if hint:
            full_message = f"{full_message} {hint}" if full_message else hint

        # Retain the structured state that produced this instance so callers can
        # branch on `code`/`extra` instead of parsing the rendered message.
        self.code = target_code
        self.extra = resolved_extra
        self.raw_message = message
        self.message = full_message
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
            entry = _catalog_entry(catalog, "warnings", self.catalog_key)
            if entry:
                target_code = entry.get("code")

        resolved_extra = merge_extra(meta, extra)
        resolved_extra.setdefault("caller", self.catalog_key or type(self).__name__)
        resolved_msg, hint = smonitor.resolve(
            message=message, code=target_code, extra=resolved_extra
        )

        full_message = resolved_msg
        if hint:
            full_message = f"{full_message} {hint}" if full_message else hint

        self.code = target_code
        self.extra = resolved_extra
        self.raw_message = message
        self.message = full_message
        super().__init__(full_message)



class FormatError(CatalogException):
    """Exception raised when a data or file format standard is violated."""
    catalog_key = "FormatError"

class InconsistencyError(CatalogException):
    """Exception raised when internal data structures are inconsistent."""
    catalog_key = "InconsistencyError"

class SupportTierRegistry:
    """Registry mapping names (forms, objects, functions) to their support tier.

    Obtain an instance from :py:meth:`DiagnosticBundle.tier_registry`.  The
    registry is bound to a ``DiagnosticBundle`` and uses its emission
    machinery, so all signals pass through the same catalog and meta context.

    Tier semantics
    --------------
    - **Tier 1**: contractual, no signal emitted.
    - **Tier 2**: best-effort, a WARNING is emitted once per name per session.
    - **Tier 3**: experimental/niche, an INFO signal is emitted once per name
      per session.
    """

    def __init__(self, bundle: "DiagnosticBundle") -> None:
        self._bundle = bundle
        self._tiers: Dict[str, int] = {}

    def register(self, name: str, tier: int) -> None:
        """Register *name* with its support *tier* (1, 2, or 3)."""
        self._tiers[name] = tier

    def register_many(self, mapping: Dict[str, int]) -> None:
        """Register multiple names at once from a ``{name: tier}`` mapping."""
        self._tiers.update(mapping)

    def check(self, name: str) -> None:
        """Emit the appropriate tier signal for *name*, at most once per session.

        Tier 1 items (or unregistered names) produce no signal.
        Tier 2 items emit a WARNING the first time they are checked.
        Tier 3 items emit an INFO signal the first time they are checked.
        """
        tier = self._tiers.get(name)
        if tier is None or tier == 1:
            return
        self._bundle._emit_tier_signal(tier=tier, name=name, kind="form")


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
        self._tier_dedup_cache: set[str] = set()

    def warn(
        self,
        message_or_warning: str | Warning,
        category: Optional[Type[Warning]] = None,
        *,
        stacklevel: int = 2,
        caller: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        instance_extra: Dict[str, Any] = {}
        if isinstance(message_or_warning, Warning):
            cls_name = type(message_or_warning).__name__
            msg = str(message_or_warning)
            cat = type(message_or_warning)
            if isinstance(message_or_warning, CatalogWarning):
                # The instance already rendered itself from this same catalog.
                # Re-injecting its rendered text as `message` would interpolate
                # it into the template a second time (and append the hint
                # twice), so carry the structured fields it was built from and
                # fall back to the *raw* message it was given.
                instance_extra = dict(getattr(message_or_warning, "extra", None) or {})
                msg = getattr(message_or_warning, "raw_message", None) or ""
        else:
            cat = category or UserWarning
            cls_name = cat.__name__
            msg = message_or_warning

        entry = _catalog_entry(self.catalog, "warnings", cls_name)
        if entry:
            try:
                payload = {**instance_extra, **(extra or {})}
                payload.setdefault("message", msg)
                payload["caller"] = (
                    caller or (extra or {}).get("caller") or payload.get("caller")
                )
                emit_from_catalog(
                    entry,
                    package_root=self.package_root,
                    extra=merge_extra(self.meta, payload),
                    meta=self.meta,
                )
                return
            except Exception as exc:
                # Do not silently swallow emission failures. Try a minimal
                # fallback diagnostic; always preserve python warnings behavior.
                try:
                    smonitor.emit(
                        "DEBUG",
                        "Catalog warning emission failed",
                        source="smonitor.integrations.diagnostic",
                        category="integration",
                        extra=merge_extra(
                            self.meta,
                            {
                                "catalog_warning_class": cls_name,
                                "original_message": msg,
                                "emit_error": str(exc),
                            },
                        ),
                    )
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
        caller: Optional[str] = None,
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
        self.warn(message_or_warning, category, stacklevel=stacklevel, caller=caller, extra=extra)

    def info(
        self,
        key: str,
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit an INFO signal from the catalog."""
        entry = _catalog_entry(self.catalog, "info", key)
        if entry:
            emit_from_catalog(
                entry,
                package_root=self.package_root,
                extra=merge_extra(self.meta, extra),
                meta=self.meta,
            )

    def experimental(self, message: Optional[str] = None, *, key: str = "ExperimentalPath"):
        """Decorator to mark a function or module as experimental.

        .. deprecated::
            Use :py:meth:`support_tier` with ``tier=3`` instead.
            ``experimental()`` is now an alias for ``support_tier(3, key=key)``.
            The key defaults to ``"ExperimentalPath"`` for backward compatibility.
        """
        return self.support_tier(3, message=message, key=key)

    def _emit_tier_signal(
        self,
        *,
        tier: int,
        name: str,
        kind: str = "item",
        module: Optional[str] = None,
        message: Optional[str] = None,
        key: Optional[str] = None,
    ) -> None:
        """Emit the appropriate support-tier signal for *name*, at most once per session.

        Uses an internal deduplication cache keyed on ``(tier, name)`` so each
        name only triggers a signal once regardless of how many times it is used.
        """
        dedup_key = f"tier:{tier}:{name}"
        if dedup_key in self._tier_dedup_cache:
            return
        self._tier_dedup_cache.add(dedup_key)

        extra: Dict[str, Any] = {"name": name, "kind": kind, "tier": tier}
        if module:
            extra["module"] = module
        if message:
            extra["custom_message"] = message

        if tier == 2:
            catalog_key = key or "SupportTier2Warning"
            entry = _catalog_entry(self.catalog, "warnings", catalog_key)
            if entry:
                emit_from_catalog(
                    entry,
                    package_root=self.package_root,
                    extra=merge_extra(self.meta, extra),
                    meta=self.meta,
                )
            else:
                smonitor.emit(
                    "WARNING",
                    f"'{name}' is a best-effort supported {kind} (Tier 2). "
                    "Results are supported but not contractually guaranteed for all workflows.",
                    source="smonitor.integrations.support_tier",
                    category="support_tier",
                    extra=merge_extra(self.meta, extra),
                )
        elif tier >= 3:
            catalog_key = key or "SupportTier3Info"
            entry = _catalog_entry(self.catalog, "info", catalog_key)
            if not entry:
                entry = _catalog_entry(self.catalog, "info", "ExperimentalPath")
            if entry:
                emit_from_catalog(
                    entry,
                    package_root=self.package_root,
                    extra=merge_extra(self.meta, extra),
                    meta=self.meta,
                )
            else:
                smonitor.emit(
                    "INFO",
                    f"'{name}' is an experimental {kind} (Tier 3). Use with caution.",
                    source="smonitor.integrations.support_tier",
                    category="support_tier",
                    extra=merge_extra(self.meta, extra),
                )

    def support_tier(
        self,
        tier: int,
        *,
        message: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Any:
        """Decorator marking a function with its support tier.

        - **Tier 1**: no-op; the original function is returned unchanged.
        - **Tier 2**: emits a WARNING signal the first time the function is
          called in a session (deduplicated per function per session).
        - **Tier 3**: emits an INFO signal the first time the function is
          called in a session (deduplicated per function per session).

        Unlike :py:meth:`experimental`, this decorator deduplicates per
        function per session and is intended for the systematic support-tier
        protocol across the MolSysSuite ecosystem.

        Parameters
        ----------
        tier:
            Support tier (1, 2, or 3).
        message:
            Optional additional context appended to the emitted signal.
        key:
            Catalog key override.  Defaults to ``"SupportTier2Warning"`` for
            tier 2 and ``"SupportTier3Info"`` for tier 3.
        """
        if tier == 1:
            def passthrough(fn: Any) -> Any:
                return fn
            return passthrough

        def decorator(fn: Any) -> Any:
            from functools import wraps

            @wraps(fn)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                self._emit_tier_signal(
                    tier=tier,
                    name=fn.__qualname__,
                    kind="function",
                    module=fn.__module__,
                    message=message,
                    key=key,
                )
                return fn(*args, **kwargs)

            return wrapper

        return decorator

    def tier_registry(self) -> "SupportTierRegistry":
        """Return the :class:`SupportTierRegistry` associated with this bundle.

        The registry is created lazily on first access and persists for the
        lifetime of the bundle, so tier signals are deduplicated across the
        entire session.
        """
        if not hasattr(self, "_tier_registry"):
            self._tier_registry = SupportTierRegistry(self)
        return self._tier_registry

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
