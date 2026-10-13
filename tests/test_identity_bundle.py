"""Narrow, nonemitting diagnostic identity export (#40)."""

import json
import sys

import pytest

import smonitor
from smonitor.handlers.memory import MemoryHandler


def test_identity_bundle_omits_unreviewed_payloads_and_top_level_sections(tmp_path, monkeypatch):
    canary = "SYNTHETIC_ARGV_CANARY"
    monkeypatch.setattr(sys, "argv", ["probe", canary])
    tmp_path.joinpath("_smonitor.py").write_text(
        f"SMONITOR = {{'level': 'DEBUG'}}\nSECRET = {canary!r}\n"
    )
    handler = MemoryHandler()
    smonitor.configure(
        profile="user",
        handlers=[handler],
        level="DEBUG",
        event_buffer_size=4,
        codes={"T-W001": {"user_message": "Warning"}},
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=False,
    )
    smonitor.emit("WARNING", canary, source=canary, code="T-W001", extra={"secret": canary})
    before = len(handler.events)

    bundle = smonitor.collect_identity_bundle(allowed_codes={"T-W001"})
    out = smonitor.export_identity_bundle(tmp_path / "identity.json", allowed_codes={"T-W001"})
    written = json.loads(out.read_text())

    assert set(bundle) == {"schema", "generated_at", "producer", "coverage", "events", "omitted"}
    assert bundle["schema"] == "smonitor.identity-bundle@1"
    assert bundle["producer"] == "smonitor"
    assert set(bundle["events"][0]) == {"level", "fingerprint", "code"}
    assert bundle["events"][0]["code"] == "T-W001"
    assert bundle["events"][0]["level"] == "WARNING"
    assert len(bundle["events"][0]["fingerprint"]) == 16
    assert bundle["coverage"]["history_complete"] is False
    assert bundle["coverage"]["pending_summaries_flushed"] is False
    assert set(bundle["coverage"]) == {
        "retained_events",
        "selected_events",
        "limit",
        "omitted_before_selection",
        "codes_omitted",
        "history_complete",
        "pending_summaries_flushed",
    }
    assert "argv" in bundle["omitted"]
    assert canary not in json.dumps(bundle)
    assert canary not in out.read_text()
    assert written["events"][0]["code"] == "T-W001"
    assert len(handler.events) == before
    with pytest.raises(FileExistsError):
        smonitor.export_identity_bundle(out)
    assert json.loads(out.read_text()) == written
    assert smonitor.export_identity_bundle(out, force=True) == out


def test_identity_bundle_requires_explicit_code_approval_and_bounds_selection():
    smonitor.configure(
        profile="user",
        handlers=[MemoryHandler()],
        level="INFO",
        event_buffer_size=150,
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=False,
    )
    for index in range(120):
        smonitor.emit("INFO", f"message {index}", code="UNREVIEWED-SECRET")

    bundle = smonitor.collect_identity_bundle(max_events=1000)
    assert len(bundle["events"]) == 100
    assert bundle["coverage"]["retained_events"] == 120
    assert bundle["coverage"]["selected_events"] == 100
    assert bundle["coverage"]["omitted_before_selection"] == 20
    assert all(item["code"] is None for item in bundle["events"])
    assert "UNREVIEWED-SECRET" not in json.dumps(bundle)
    assert smonitor.collect_identity_bundle(max_events=0)["events"] == []


def test_identity_bundle_discards_corrupted_identity_fields():
    manager = smonitor.configure(
        profile="user",
        handlers=[MemoryHandler()],
        level="INFO",
        event_buffer_size=1,
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=False,
    )
    smonitor.emit("INFO", "ordinary", code="T-W001")
    retained = manager.recent_events()[0]
    retained["level"] = "PRIVATE-LEVEL"
    retained["fingerprint"] = "PRIVATE-FINGERPRINT"
    retained["code"] = "PRIVATE-CODE"

    bundle = smonitor.collect_identity_bundle(allowed_codes={"T-W001"})

    assert bundle["events"] == [{"level": None, "fingerprint": None, "code": None}]
    assert "PRIVATE" not in json.dumps(bundle)


def test_identity_bundle_does_not_flush_pending_warning_summaries():
    handler = MemoryHandler()
    manager = smonitor.configure(
        profile="user",
        handlers=[handler],
        level="WARNING",
        event_buffer_size=10,
        warning_coalesce_window_s=60,
        capture_logging=False,
        capture_warnings=False,
        capture_exceptions=False,
    )
    smonitor.emit("WARNING", "repeat", code="T-W001")
    smonitor.emit("WARNING", "repeat", code="T-W001")
    before_events = len(handler.events)
    before_history = len(manager.recent_events())

    bundle = smonitor.collect_identity_bundle()

    assert bundle["coverage"]["pending_summaries_flushed"] is False
    assert len(handler.events) == before_events
    assert len(manager.recent_events()) == before_history
    smonitor.collect_bundle()
    assert len(handler.events) > before_events


@pytest.mark.parametrize("limit", [-1, "100", True])
def test_identity_bundle_rejects_invalid_limit(limit):
    with pytest.raises(ValueError, match="identity bundle selection"):
        smonitor.collect_identity_bundle(max_events=limit)


@pytest.mark.parametrize("codes", [{"bad space"}, {"T-W001", 7}])
def test_identity_bundle_rejects_invalid_allowlist(codes):
    with pytest.raises(ValueError, match="identity bundle selection"):
        smonitor.collect_identity_bundle(allowed_codes=codes)
