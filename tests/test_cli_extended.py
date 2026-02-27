import json
import sys
from pathlib import Path

import pytest

import smonitor.cli as cli


def test_cli_validate_config_missing_file(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["smonitor", "--validate-config"])
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "No _smonitor.py found" in out


def test_cli_validate_config_invalid(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {'trace_depth': 'bad'}\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["smonitor", "--validate-config", "--config-path", str(tmp_path)],
    )
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 2
    assert "Invalid _smonitor.py" in out


def test_cli_validate_config_success(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["smonitor", "--validate-config", "--config-path", str(tmp_path)],
    )
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "SMONITOR" in out


def test_cli_export_invalid_config(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {'trace_depth': 'bad'}\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["smonitor", "export", "--config-path", str(tmp_path)],
    )
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 2
    assert "Invalid _smonitor.py" in out


def test_cli_export_forwards_options(monkeypatch, capsys, tmp_path: Path):
    calls = {}

    def fake_export_bundle(out, **kwargs):
        calls["out"] = out
        calls["kwargs"] = kwargs
        return Path(out)

    monkeypatch.setattr(cli, "export_bundle", fake_export_bundle)
    monkeypatch.setattr(cli, "load_project_config", lambda *_: {"SMONITOR": {}})
    monkeypatch.setattr(cli, "validate_project_config", lambda *_: [])
    monkeypatch.setattr(cli.smonitor, "configure", lambda **_: None)

    out_path = tmp_path / "bundle.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smonitor",
            "export",
            "--out",
            str(out_path),
            "--max-events",
            "10",
            "--since",
            "2026-01-01T00:00:00",
            "--drop-extra",
            "--drop-context",
            "--redact",
            "extra.password",
            "--append-events",
            "--force",
        ],
    )
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert str(out_path) in out
    assert calls["kwargs"]["max_events"] == 10
    assert calls["kwargs"]["since"] == "2026-01-01T00:00:00"
    assert calls["kwargs"]["drop_extra"] is True
    assert calls["kwargs"]["drop_context"] is True
    assert calls["kwargs"]["redact_fields"] == ["extra.password"]
    assert calls["kwargs"]["append_events"] is True
    assert calls["kwargs"]["force"] is True


def test_cli_check_event_with_json_payload(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    emitted = {}

    def fake_emit(level, message, **kwargs):
        emitted["level"] = level
        emitted["message"] = message
        emitted["kwargs"] = kwargs
        return {}

    monkeypatch.setattr(cli.smonitor, "emit", fake_emit)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smonitor",
            "--check",
            "--config-path",
            str(tmp_path),
            "--check-event",
            json.dumps(
                {
                    "level": "ERROR",
                    "message": "boom",
                    "source": "tests.x",
                    "code": "T-1",
                    "extra": {"hint": "do this"},
                    "category": "test",
                    "tags": ["ci"],
                }
            ),
        ],
    )
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK" in out
    assert emitted["level"] == "ERROR"
    assert emitted["message"] == "boom"
    assert emitted["kwargs"]["source"] == "tests.x"
    assert emitted["kwargs"]["code"] == "T-1"


def test_cli_check_without_event_uses_defaults(tmp_path: Path, monkeypatch, capsys):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    emitted = {}

    def fake_emit(level, message, **kwargs):
        emitted["level"] = level
        emitted["message"] = message
        emitted["kwargs"] = kwargs
        return {}

    monkeypatch.setattr(cli.smonitor, "emit", fake_emit)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smonitor",
            "--check",
            "--config-path",
            str(tmp_path),
            "--check-level",
            "WARNING",
            "--check-source",
            "tests.default",
            "--check-code",
            "C-1",
        ],
    )
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "OK" in out
    assert emitted["level"] == "WARNING"
    assert emitted["message"] == "smonitor check event"
    assert emitted["kwargs"]["source"] == "tests.default"
    assert emitted["kwargs"]["code"] == "C-1"


def test_cli_report_branch(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["smonitor", "--report"])
    monkeypatch.setattr(cli.smonitor, "configure", lambda **_: None)
    monkeypatch.setattr(cli.smonitor, "report", lambda: {"calls_total": 1})
    rc = cli.main()
    out = capsys.readouterr().out
    assert rc == 0
    assert "calls_total" in out


def test_cli_check_event_invalid_json_raises(tmp_path: Path, monkeypatch):
    (tmp_path / "_smonitor.py").write_text("SMONITOR = {}\n")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "smonitor",
            "--check",
            "--config-path",
            str(tmp_path),
            "--check-event",
            "{not-json}",
        ],
    )
    with pytest.raises(json.JSONDecodeError):
        cli.main()
