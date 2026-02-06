import json
from pathlib import Path

import smonitor
from smonitor.bundle import export_bundle


def test_event_buffer_and_export(tmp_path: Path):
    cfg = tmp_path / "_smonitor.py"
    cfg.write_text("SMONITOR = {}\n")
    smonitor.configure(profile="user", handlers=[], event_buffer_size=2)
    smonitor.emit("INFO", "a", source="x", code="X1")
    smonitor.emit("INFO", "b", source="x", code="X2")
    smonitor.emit("INFO", "c", source="x", code="X3")

    out = export_bundle(tmp_path / "bundle.json", config_base=tmp_path, force=True)
    data = json.loads(out.read_text())
    assert data["events"][-1]["message"] == "c"
    assert len(data["events"]) == 2
