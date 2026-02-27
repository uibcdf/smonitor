from pathlib import Path

import pytest

import smonitor
import smonitor.profiling as profiling
from smonitor.core.manager import get_manager


def test_span_noop_when_profiling_disabled():
    smonitor.configure(profile="user", profiling=False, profiling_buffer_size=10)
    before = len(smonitor.report()["timeline"])
    with profiling.span("noop"):
        pass
    after = len(smonitor.report()["timeline"])
    assert after == before


def test_span_respects_sampling(monkeypatch):
    smonitor.configure(
        profile="user",
        profiling=True,
        profiling_buffer_size=10,
        profiling_sample_rate=0.2,
    )
    monkeypatch.setattr("random.random", lambda: 0.9)
    before = len(smonitor.report()["timeline"])
    with profiling.span("sampled-out"):
        pass
    after = len(smonitor.report()["timeline"])
    assert after == before


def test_export_timeline_json_and_csv(tmp_path: Path):
    smonitor.configure(
        profile="user",
        profiling=True,
        profiling_buffer_size=10,
        profiling_sample_rate=1.0,
    )
    with profiling.span("block", detail="ok"):
        pass

    json_path = tmp_path / "timeline.json"
    csv_path = tmp_path / "timeline.csv"
    profiling.export_timeline(str(json_path), format="json")
    profiling.export_timeline(str(csv_path), format="csv")
    assert json_path.exists()
    assert csv_path.exists()
    assert "duration_ms" in json_path.read_text(encoding="utf-8")


def test_export_timeline_csv_empty_does_not_create_file(tmp_path: Path):
    manager = get_manager()
    manager._timeline.clear()
    smonitor.configure(profile="user", profiling=False, profiling_buffer_size=10)
    csv_path = tmp_path / "empty.csv"
    profiling.export_timeline(str(csv_path), format="csv")
    assert not csv_path.exists()


def test_export_timeline_invalid_format_raises(tmp_path: Path):
    smonitor.configure(profile="user", profiling=True, profiling_buffer_size=10)
    with pytest.raises(ValueError, match="Unsupported format"):
        profiling.export_timeline(str(tmp_path / "x.out"), format="yaml")
