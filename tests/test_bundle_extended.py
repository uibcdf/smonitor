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
