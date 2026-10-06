"""Register provider declarations without selecting application policy."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from .._diagnostics import ProviderRegistrationError
from ..config import validate_codes_signals
from ..config.discovery import load_config_from_path
from ..core.manager import get_manager


def register_provider(package_root: Path, *, provider: str | None = None) -> dict:
    """Atomically register the exact package's CODES/SIGNALS and provenance.

    The default identity is the resolved package directory. Explicit identities
    must be unique. Equal shared definitions are accepted; conflicting names
    reject the complete registration. Runtime policy is never applied here.
    """
    root = Path(package_root).resolve()
    identity = provider if provider is not None else str(root)
    if type(identity) is not str or not identity:
        raise ProviderRegistrationError("SMONITOR-PROVIDER-INVALID")
    # Never walk upward into an application's configuration when registering a
    # provider. Import/loader errors propagate with no partial registration.
    cfg = load_config_from_path(root / "_smonitor.py") or {}
    codes = cfg.get("CODES")
    signals = cfg.get("SIGNALS")
    errors = validate_codes_signals(codes, signals)
    if errors:
        raise ProviderRegistrationError(
            "SMONITOR-PROVIDER-INVALID", extra={"provider": identity, "errors": errors}
        )
    codes = codes or {}
    signals = signals or {}
    record = deepcopy(
        {
            "provider": identity,
            "package_root": str(root),
            "codes": codes,
            "signals": signals,
            "recommendations": {
                key: cfg[key]
                for key in ("PROFILE", "SMONITOR", "PROFILES", "ROUTES", "FILTERS")
                if key in cfg
            },
        }
    )
    manager = get_manager()
    with manager._catalog_lock:
        previous = manager._providers.get(identity)
        if previous is not None:
            if previous != record:
                raise ProviderRegistrationError(
                    "SMONITOR-PROVIDER-IDENTITY", extra={"provider": identity}
                )
            return deepcopy(previous)
        conflicts = sorted(
            [key for key in codes if key in manager._codes and manager._codes[key] != codes[key]]
            + [
                key
                for key in signals
                if key in manager._signals and manager._signals[key] != signals[key]
            ]
        )
        if conflicts:
            raise ProviderRegistrationError(
                "SMONITOR-PROVIDER-CONFLICT",
                extra={"provider": identity, "names": conflicts},
            )
        manager._codes = {**manager._codes, **record["codes"]}
        manager._signals = {**manager._signals, **record["signals"]}
        manager._providers[identity] = record
        return deepcopy(record)
