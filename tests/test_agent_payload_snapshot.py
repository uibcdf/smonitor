"""The machine payload is pinned as a whole, not field by field.

`profile="agent"` exists so a triage agent can read structure instead of parsing
prose, and `normalized` is the section it reads. That section is frozen for 1.0:
a key that disappears breaks every consumer reading it, and a key that appears
is a key we are then obliged to keep.

The tests around it assert fields one at a time, which protects what somebody
remembered to write. Measured on 2026-09-07 by removing each field in turn:
23 of the 25 promoted `extra` keys were guarded, but `form`, `requested_attribute`,
`message`, `category` and `exception_type` could be deleted from the payload with
the whole suite still green, and a new key could be added — `normalized` grew an
`internal_debug_state` holding `repr(event)` and nothing failed.

A snapshot closes both directions at once. It says *these are the fields, and
there are no others*, so any change to the contract arrives as a reviewable diff
rather than as a silent one.

Regenerate deliberately, never to make a red test green:

    SMONITOR_UPDATE_SNAPSHOTS=1 pytest tests/test_agent_payload_snapshot.py

and read the diff in the commit: it is the contract change, stated.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import smonitor
from smonitor.handlers.json import JsonHandler
from smonitor.integrations import context_extra

SNAPSHOTS = Path(__file__).parent / "snapshots"

#: Values that differ on every run and carry no contract. Replaced by a marker so
#: the snapshot pins the shape without pinning a clock or a UUID. `fingerprint` is
#: deliberately *not* here: it is deterministic across processes, and pinning it
#: guards the recipe that groups two occurrences into one incident.
VOLATILE = ("timestamp", "run_id", "session_id")

CODES = {
    "MYLIB-W010": {
        "agent_message": "Download of {resource} from {provider} failed.",
        "agent_hint": "Retry, or select a mirror.",
        "user_message": "Could not download {resource}.",
        "title": "Download failed",
    },
    "MYLIB-E001": {"agent_message": "Nothing optional was supplied."},
}


def _emit(tmp_path: Path, code: str, **kwargs) -> dict:
    """Emit through the real path -- manager, then handler -- and read it back."""
    path = tmp_path / "agent.jsonl"
    smonitor.configure(
        profile="agent",
        level="DEBUG",
        handlers=[JsonHandler(str(path), mode="w")],
        codes=CODES,
        run_id="run-fixed",
        session_id="session-fixed",
    )
    smonitor.emit("WARNING", "", code=code, **kwargs)
    payload = json.loads(path.read_text(encoding="utf-8").strip())
    for key in VOLATILE:
        if key in payload:
            payload[key] = f"<{key}>"
        if key in payload.get("normalized", {}):
            payload["normalized"][key] = f"<{key}>"
    return payload


def _compare(name: str, payload: dict) -> None:
    stored = SNAPSHOTS / f"{name}.json"
    rendered = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if os.environ.get("SMONITOR_UPDATE_SNAPSHOTS"):
        stored.write_text(rendered, encoding="utf-8")
        pytest.skip(f"snapshot rewritten: {stored.name}")
    assert stored.is_file(), (
        f"{stored.name} is missing. Create it with SMONITOR_UPDATE_SNAPSHOTS=1 "
        "and commit it as the contract it is."
    )
    assert rendered == stored.read_text(encoding="utf-8"), (
        f"the machine payload no longer matches {stored.name}. If the change is "
        "intended, regenerate with SMONITOR_UPDATE_SNAPSHOTS=1 and let the diff "
        "stand as the record of a contract change."
    )


def test_the_full_machine_payload_matches_its_snapshot(tmp_path):
    """Every canonical field at once, so the promoted keys are pinned together."""
    payload = _emit(
        tmp_path,
        "MYLIB-W010",
        source="mylib.io.download",
        category="network",
        tags=["io", "network"],
        correlation_id="corr-fixed",
        extra=context_extra(
            caller="mylib.io.fetch",
            form="file:pdb",
            requested_attribute="coordinates",
            resource="181l.pdb",
            provider="RCSB",
            operation="download",
            retry_attempt=2,
            retry_max=5,
            retry_exhausted=False,
            retry_delay_s=1.5,
            failure_class="network",
            last_failure_reason="timeout",
            cause_exception_type="TimeoutError",
            cause_code="NET-001",
            causal_chain=["NET-001", "MYLIB-W010"],
            incident_kind="network",
            severity="medium",
            priority="normal",
            diagnostic_confidence="high",
            recommended_action="retry",
            next_step="check-network",
            retryable=True,
            support_needed=False,
            evidence={"expected": "200 OK", "observed": "timeout after 30s"},
        ),
    )
    _compare("agent_payload_full", payload)


def test_the_minimal_machine_payload_matches_its_snapshot(tmp_path):
    """Nothing optional supplied, which pins the fields that are always present."""
    payload = _emit(tmp_path, "MYLIB-E001", source="mylib.core")
    _compare("agent_payload_minimal", payload)


def test_the_normalized_key_set_is_stated_in_one_place(tmp_path):
    """A legible failure for the common case, alongside the whole-document diff.

    A snapshot mismatch is a diff of the entire record, which is the right thing
    to review and the wrong thing to read when one key vanished.
    """
    stored = json.loads((SNAPSHOTS / "agent_payload_full.json").read_text(encoding="utf-8"))
    payload = _emit(
        tmp_path,
        "MYLIB-W010",
        source="mylib.io.download",
        category="network",
        tags=["io", "network"],
        correlation_id="corr-fixed",
        extra=context_extra(
            caller="mylib.io.fetch",
            form="file:pdb",
            requested_attribute="coordinates",
            resource="181l.pdb",
            provider="RCSB",
            operation="download",
            retry_attempt=2,
            retry_max=5,
            retry_exhausted=False,
            retry_delay_s=1.5,
            failure_class="network",
            last_failure_reason="timeout",
            cause_exception_type="TimeoutError",
            cause_code="NET-001",
            causal_chain=["NET-001", "MYLIB-W010"],
            incident_kind="network",
            severity="medium",
            priority="normal",
            diagnostic_confidence="high",
            recommended_action="retry",
            next_step="check-network",
            retryable=True,
            support_needed=False,
            evidence={"expected": "200 OK", "observed": "timeout after 30s"},
        ),
    )
    expected, actual = set(stored["normalized"]), set(payload["normalized"])
    assert actual == expected, (
        f"gone: {sorted(expected - actual) or 'none'}; "
        f"new: {sorted(actual - expected) or 'none'}"
    )


def test_the_record_keys_are_pinned_too(tmp_path):
    """`normalized` is the contract, but a consumer reads the record around it."""
    stored = json.loads((SNAPSHOTS / "agent_payload_minimal.json").read_text(encoding="utf-8"))
    payload = _emit(tmp_path, "MYLIB-E001", source="mylib.core")
    expected, actual = set(stored), set(payload)
    assert actual == expected, (
        f"gone: {sorted(expected - actual) or 'none'}; "
        f"new: {sorted(actual - expected) or 'none'}"
    )
