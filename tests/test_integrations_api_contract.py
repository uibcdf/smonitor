from pathlib import Path

import smonitor
from smonitor import integrations


def test_integrations_public_exports_contract():
    expected = {
        "ensure_configured",
        "reset_configured_packages",
        "merge_extra",
        "emit_from_catalog",
        "CatalogException",
        "CatalogWarning",
        "DiagnosticBundle",
    }
    assert expected.issubset(set(integrations.__all__))


def test_merge_extra_contract():
    merged = integrations.merge_extra({"a": 1}, {"b": 2, "a": 3})
    assert merged == {"a": 3, "b": 2}


def test_emit_from_catalog_contract_without_package_config():
    smonitor.configure(profile="dev", handlers=[])
    entry = {"level": "WARNING", "code": "X-01", "source": "mylib.core"}
    event = integrations.emit_from_catalog(entry, meta={"library": "mylib"}, extra={"x": 1})
    assert event["level"] == "WARNING"
    assert event["code"] == "X-01"
    assert event["source"] == "mylib.core"
    assert event["extra"]["library"] == "mylib"
    assert event["extra"]["x"] == 1


def test_ensure_configured_is_idempotent(monkeypatch, tmp_path):
    calls: list[Path] = []

    def _fake_configure(*, config_path):
        calls.append(Path(config_path))

    integrations.reset_configured_packages()
    monkeypatch.setattr("smonitor.integrations.core.smonitor.configure", _fake_configure)

    integrations.ensure_configured(tmp_path)
    integrations.ensure_configured(tmp_path)
    assert len(calls) == 1
