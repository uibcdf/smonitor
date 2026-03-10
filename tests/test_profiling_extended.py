from pathlib import Path

import pytest

import smonitor
import smonitor.profiling as profiling
from smonitor.core import decorator as decorator_module
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


def test_signal_extra_factory_attaches_context_to_timeline():
    smonitor.configure(profile="user", profiling=True, profiling_buffer_size=10)

    def _selection_extra(args, kwargs):
        return {"selection": kwargs.get("selection")}

    @smonitor.signal(tags=["api", "demo"], extra_factory=_selection_extra)
    def sample(*, selection=None):
        return selection

    sample(selection="name CA")
    timeline = smonitor.report()["timeline"]
    entry = timeline[-1]
    assert entry["tags"] == ["api", "demo"]
    assert entry["meta"]["selection"] == "name CA"



def test_report_exposes_timings_by_tag():
    smonitor.configure(profile="user", profiling=True, profiling_buffer_size=10)

    @smonitor.signal(tags=["api", "structure"])
    def tagged():
        return 1

    tagged()
    report = smonitor.report()
    assert report["timings_by_tag"]["api"]["count"] >= 1
    assert report["timings_by_tag"]["structure"]["count"] >= 1



def test_slow_signal_event_is_emitted_when_threshold_is_crossed():
    manager = smonitor.configure(
        profile="dev",
        profiling=False,
        event_buffer_size=10,
        slow_signal_ms=0.0,
        slow_signal_level="WARNING",
        handlers=[],
    )
    manager._event_buffer.clear()

    def _selection_extra(args, kwargs):
        return {"selection": kwargs.get("selection")}

    @smonitor.signal(tags=["api", "slow"], extra_factory=_selection_extra)
    def sample(*, selection=None):
        return selection

    original_perf_counter = decorator_module.perf_counter
    values = iter([0.0, 0.050])
    decorator_module.perf_counter = lambda: next(values)
    try:
        manager.configure(slow_signal_ms=10.0, slow_signal_level="WARNING")
        sample(selection="all")
    finally:
        decorator_module.perf_counter = original_perf_counter
        manager.configure(slow_signal_ms=0.0)

    event = manager.recent_events(limit=1)[0]
    assert event["code"] == "SMONITOR-SIGNAL-SLOW"
    assert event["level"] == "WARNING"
    assert event["source"] == f"{sample.__module__}.{sample.__name__}"
    assert event["extra"]["duration_ms"] == 50.0
    assert event["extra"]["threshold_ms"] == 10.0
    assert event["extra"]["selection"] == "all"
    assert event["tags"] == ["api", "slow"]
