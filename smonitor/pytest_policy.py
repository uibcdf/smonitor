"""Opt-in QA policy over Pytest Receptor's canonical artifact.

This module reads finalized evidence after pytest exits. It neither hooks pytest
outcomes nor writes another event stream. Rules use diagnostic identity rather
than occurrence counts or test-node assignments, which may change under xdist.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from .config import validate_project_config
from .config.discovery import load_config_from_path

_BASELINE_SCHEMA = "smonitor.pytest-baseline@1"
_EVENT_SCHEMA = "smonitor.pytest-event@1"
_NAMESPACE = "uibcdf.smonitor@1"
_CODE = re.compile(r"[A-Z][A-Z0-9-]{0,63}\Z")
_FINGERPRINT = re.compile(r"[0-9a-f]{16}\Z")
_LEVELS = frozenset({"WARNING", "ERROR", "CRITICAL"})


def _identity(value: Mapping[str, Any]) -> tuple[str, str, str] | None:
    code = value.get("code")
    source = value.get("source", value.get("signal"))
    fingerprint = value.get("fingerprint")
    if not (isinstance(code, str) and _CODE.fullmatch(code)):
        return None
    if not (isinstance(source, str) and source):
        return None
    if not (isinstance(fingerprint, str) and _FINGERPRINT.fullmatch(fingerprint)):
        return None
    return code, source, fingerprint


def _as_dict(identity: tuple[str, str, str]) -> dict[str, str]:
    return dict(zip(("code", "source", "fingerprint"), identity))


def load_baseline(path: str | Path) -> set[tuple[str, str, str]]:
    """Load a versioned identity set; reject malformed or duplicate entries."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != _BASELINE_SCHEMA:
        raise ValueError("smonitor.pytest-baseline.schema")
    entries = data.get("identities")
    if not isinstance(entries, list):
        raise ValueError("smonitor.pytest-baseline.identities")
    identities: set[tuple[str, str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"code", "source", "fingerprint"}:
            raise ValueError("smonitor.pytest-baseline.identity")
        identity = _identity(entry)
        if identity is None or identity in identities:
            raise ValueError("smonitor.pytest-baseline.identity")
        identities.add(identity)
    return identities


def write_baseline(path: str | Path, identities: Iterable[tuple[str, str, str]]) -> None:
    """Write an explicitly accepted, deterministic identity set."""
    normalized = set(identities)
    if any(_identity(_as_dict(identity)) != identity for identity in normalized):
        raise ValueError("smonitor.pytest-baseline.identity")
    destination = Path(path)
    payload = {
        "schema": _BASELINE_SCHEMA,
        "identities": [_as_dict(identity) for identity in sorted(normalized)],
    }
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, indent=2) + "\n")


def load_provider_codes(roots: Iterable[str | Path]) -> tuple[set[str], list[dict[str, str]]]:
    """Validate explicit provider configurations and return their code registry.

    Roots are trusted package directories containing ``_smonitor.py``. Loading
    them follows the same Python configuration semantics as provider registration.
    """
    codes: dict[str, Any] = {}
    problems: list[dict[str, str]] = []
    for root_value in roots:
        root = Path(root_value)
        config_file = root / "_smonitor.py"
        if not config_file.is_file():
            problems.append({"rule": "provider_config_missing", "provider": str(root)})
            continue
        try:
            config = load_config_from_path(config_file)
        except Exception as exc:
            problems.append(
                {
                    "rule": "provider_config_error",
                    "provider": str(root),
                    "exception_type": type(exc).__name__,
                }
            )
            continue
        errors = validate_project_config(config)
        if errors:
            problems.extend(
                {"rule": "provider_catalog_invalid", "provider": str(root), "detail": error}
                for error in errors
            )
            continue
        declared = (config or {}).get("CODES")
        if not isinstance(declared, dict) or not declared:
            problems.append({"rule": "provider_codes_missing", "provider": str(root)})
            continue
        for code, entry in declared.items():
            if code in codes and codes[code] != entry:
                problems.append(
                    {"rule": "provider_code_conflict", "provider": str(root), "code": code}
                )
            else:
                codes[code] = entry
    return set(codes), problems


def evaluate_pytest_artifact(
    path: str | Path,
    *,
    known_codes: Iterable[str] | None = None,
    forbidden_codes: Iterable[str] = (),
    baseline: Iterable[tuple[str, str, str]] | None = None,
    require_diagnostics: bool = False,
) -> dict[str, Any]:
    """Evaluate identity rules without changing the recorded pytest result.

    A missing, partial, truncated or extension-incomplete artifact cannot pass a
    strict gate: absence of an identity is then not evidence of absence.
    ``known_codes`` enables a catalog membership gate; pass validated provider
    declarations, not an inferred code prefix.
    """
    from pytest_receptor import read_artifact

    artifact = read_artifact(path)
    violations: list[dict[str, Any]] = []
    identities: set[tuple[str, str, str]] = set()
    diagnostic_records = 0
    observed_codes = set(known_codes) if known_codes is not None else None
    forbidden = set(forbidden_codes)
    if any(not isinstance(code, str) or not _CODE.fullmatch(code) for code in forbidden):
        raise ValueError("smonitor.pytest-policy.forbidden_code")
    if observed_codes is not None and any(
        not isinstance(code, str) or not _CODE.fullmatch(code) for code in observed_codes
    ):
        raise ValueError("smonitor.pytest-policy.known_code")

    if not artifact.complete or not artifact.integrity_valid:
        violations.append({"rule": "artifact_incomplete", "detail": artifact.issue})
    final = artifact.final.data if artifact.final is not None else {}
    if final.get("complete") is not True:
        violations.append({"rule": "execution_incomplete"})
    extension_status = final.get("extensions")
    if not isinstance(extension_status, dict) or extension_status.get("incomplete") is not False:
        violations.append({"rule": "extensions_incomplete"})
    if isinstance(extension_status, dict) and extension_status.get("dropped", 0) != 0:
        violations.append({"rule": "extensions_dropped", "count": extension_status["dropped"]})
    artifact_policy = final.get("artifact_policy")
    if not isinstance(artifact_policy, dict) or artifact_policy.get("truncated") is not False:
        violations.append({"rule": "artifact_truncated"})

    for record in artifact.events:
        if record.type != "extension" or record.data.get("namespace") != _NAMESPACE:
            continue
        diagnostic_records += 1
        payload = record.data.get("payload")
        if not isinstance(payload, dict) or payload.get("schema") != _EVENT_SCHEMA:
            violations.append({"rule": "diagnostic_payload_invalid"})
            continue
        identity = _identity(payload)
        if identity is None:
            violations.append({"rule": "diagnostic_identity_invalid"})
            continue
        code, _, _ = identity
        if observed_codes is not None and code not in observed_codes:
            violations.append({"rule": "code_not_in_catalog", "identity": _as_dict(identity)})
        if code in forbidden:
            violations.append({"rule": "forbidden_code", "identity": _as_dict(identity)})
        if payload.get("level") in _LEVELS:
            identities.add(identity)

    if require_diagnostics and diagnostic_records == 0:
        violations.append({"rule": "diagnostics_missing"})

    expected = set(baseline) if baseline is not None else None
    if expected is not None and any(_identity(_as_dict(item)) != item for item in expected):
        raise ValueError("smonitor.pytest-policy.baseline")
    new = identities - expected if expected is not None else set()
    disappeared = expected - identities if expected is not None else set()
    for identity in sorted(new):
        violations.append({"rule": "new_diagnostic_identity", "identity": _as_dict(identity)})

    unique_violations = {
        json.dumps(violation, sort_keys=True): violation for violation in violations
    }
    violations = [unique_violations[key] for key in sorted(unique_violations)]
    return {
        "schema": "smonitor.pytest-policy-result@1",
        "ok": not violations,
        "pytest_outcome": final.get("outcome"),
        "diagnostic_records": diagnostic_records,
        "identities": [_as_dict(identity) for identity in sorted(identities)],
        "new_identities": [_as_dict(identity) for identity in sorted(new)],
        "disappeared_identities": [_as_dict(identity) for identity in sorted(disappeared)],
        "violations": violations,
    }
