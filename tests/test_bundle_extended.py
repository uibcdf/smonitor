import json
from pathlib import Path

import smonitor
from smonitor.bundle import collect_bundle, export_bundle, write_bundle
from smonitor.core.manager import get_manager


def test_collect_bundle_since_invalid_is_ignored(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    smonitor.configure(profile="user", handlers=[], event_buffer_size=5, enabled=True)
    smonitor.emit("WARNING", "a", source="x", code="X1")
    data = collect_bundle(since="not-an-iso-date")
    assert data["events"]


def test_collect_bundle_since_filters_and_skips_bad_timestamp(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    manager = get_manager()
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10, enabled=True)
    smonitor.emit("WARNING", "a", source="x", code="X1")
    # Inject malformed timestamp event to cover tolerant path.
    manager._event_buffer.append({"timestamp": "bad-date", "message": "bad"})
    data = collect_bundle(since="2999-01-01T00:00:00+00:00")
    assert data["events"] == []


def test_collect_bundle_since_keeps_recent_and_drop_extra_and_redact_non_dict_path(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    manager = get_manager()
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10, enabled=True)
    smonitor.emit("WARNING", "a", source="x", code="X1", extra={"secret": "v"})
    # Inject event with non-dict extra so redact path traverses a non-dict segment.
    manager._event_buffer.append(
        {
            "timestamp": "2099-01-01T00:00:00+00:00",
            "level": "WARNING",
            "message": "b",
            "source": "x",
            "extra": ["not-dict"],
        }
    )
    data = collect_bundle(
        since="2000-01-01T00:00:00+00:00",
        drop_extra=True,
        redact_fields=["extra.secret"],
    )
    assert data["events"]
    assert all("extra" not in event for event in data["events"])


def test_write_bundle_directory_and_append_events(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10, enabled=True)
    smonitor.emit("WARNING", "one", source="x", code="X1")
    out_dir = tmp_path / "outdir"
    write_bundle(out_dir, append_events=False, force=True)
    events_path = out_dir / "events.jsonl"
    initial_lines = events_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(initial_lines) >= 1

    smonitor.emit("WARNING", "two", source="x", code="X2")
    write_bundle(out_dir, append_events=True, force=True)
    later_lines = events_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(later_lines) >= len(initial_lines)


def test_write_bundle_existing_json_and_dir_require_force(tmp_path: Path):
    out_json = tmp_path / "bundle.json"
    out_json.write_text("{}", encoding="utf-8")
    try:
        write_bundle(out_json, force=False)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Expected FileExistsError for existing json file")

    out_dir = tmp_path / "outdir"
    out_dir.mkdir()
    try:
        write_bundle(out_dir, force=False)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Expected FileExistsError for existing directory")


def test_export_bundle_with_drop_flags_and_redaction(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    smonitor.configure(profile="user", handlers=[], event_buffer_size=2, enabled=True)
    smonitor.emit(
        "WARNING",
        "m",
        source="x",
        code="X1",
        extra={"secret": "token"},
    )
    out = export_bundle(
        tmp_path / "bundle.json",
        config_base=tmp_path,
        force=True,
        drop_context=True,
        redact_fields=["extra.secret"],
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    event = data["events"][-1]
    assert "context" not in event
    assert event["extra"]["secret"] == "***"


def test_collect_bundle_exposes_triage_summary_for_slow_signals(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    manager = get_manager()
    smonitor.configure(profile="dev", handlers=[], event_buffer_size=10, enabled=True)
    manager.emit(
        "WARNING",
        "Slow signal call detected for pkg.mod.fn.",
        source="pkg.mod.fn",
        code="SMONITOR-SIGNAL-SLOW",
        category="profiling",
        tags=["api", "slow"],
        extra={"duration_ms": 50.0, "threshold_ms": 10.0, "signal_tags": ["api", "slow"]},
    )
    data = collect_bundle()
    assert data["triage"]["events_by_code"]["SMONITOR-SIGNAL-SLOW"] >= 1
    assert data["triage"]["events_by_category"]["profiling"] >= 1
    assert data["triage"]["events_by_fingerprint"]
    recent = data["triage"]["slow_signals_recent"][-1]
    assert recent["source"] == "pkg.mod.fn"
    assert recent["duration_ms"] == 50.0
    assert recent["threshold_ms"] == 10.0


def test_collect_bundle_exposes_coalesced_warning_summary(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    manager = get_manager()
    smonitor.configure(
        profile="user",
        handlers=[],
        event_buffer_size=10,
        enabled=True,
        warning_coalesce_window_s=60.0,
    )
    manager._warning_coalesce_state.clear()
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={"resource": "181l", "caller": "pkg.mod.fn"},
    )
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={"resource": "181l", "caller": "pkg.mod.fn"},
    )
    data = collect_bundle()
    summary = data["triage"]["coalesced_warnings"][-1]
    assert summary["code"] == "W1"
    assert summary["resource"] == "181l"
    assert summary["caller"] == "pkg.mod.fn"
    assert summary["suppressed_count"] == 1


def test_collect_bundle_flushes_pending_coalesced_warning_summary_event(tmp_path: Path):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    manager = get_manager()
    smonitor.configure(
        profile="user",
        handlers=[],
        event_buffer_size=10,
        enabled=True,
        warning_coalesce_window_s=60.0,
    )
    manager._warning_coalesce_state.clear()
    manager._coalesced_warning_summaries.clear()
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={"resource": "181l", "caller": "pkg.mod.fn", "retry_attempt": 2, "retry_max": 5},
    )
    smonitor.emit(
        "WARNING",
        "retry",
        source="pkg.mod",
        code="W1",
        extra={"resource": "181l", "caller": "pkg.mod.fn", "retry_attempt": 3, "retry_max": 5},
    )

    data = collect_bundle()

    assert data["triage"]["coalesced_warnings"][-1]["retry_attempt"] == 3
    assert data["triage"]["coalesced_warnings"][-1]["retry_max"] == 5
    assert any(event.get("code") == "SMONITOR-WARNING-COALESCED" for event in data["events"])
