from __future__ import annotations

from .core import (
    context_extra,
    emit_from_catalog,
    ensure_configured,
    merge_extra,
    reset_configured_packages,
)
from .diagnostic import (
    CatalogException,
    CatalogWarning,
    DiagnosticBundle,
    FormatError,
    InconsistencyError,
    SupportTierRegistry,
)
from .diagnostic import (
    _catalog_entry as _catalog_entry,
)

# `_catalog_entry` is re-exported for integrators that resolve catalog entries
# directly, but stays out of `__all__` on purpose: the leading underscore marks
# it as not part of the public contract frozen for 1.0.
__all__ = [
    "ensure_configured",
    "reset_configured_packages",
    "merge_extra",
    "context_extra",
    "emit_from_catalog",
    "CatalogException",
    "CatalogWarning",
    "DiagnosticBundle",
    "FormatError",
    "InconsistencyError",
    "SupportTierRegistry",
]
