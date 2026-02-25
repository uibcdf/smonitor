from pathlib import Path

import pytest

import smonitor
from smonitor.integrations.core import ensure_configured, reset_configured_packages
from smonitor.integrations.diagnostic import CatalogWarning, DiagnosticBundle


class MyCatalogWarning(CatalogWarning):
    catalog_key = "MyCatalogWarning"


def test_catalog_warning_supports_flat_catalog():
    smonitor.configure(profile="user", codes={"X-FLAT": {"user_message": "Flat warning message"}})
    warning = MyCatalogWarning(catalog={"MyCatalogWarning": {"code": "X-FLAT"}})
    assert "Flat warning message" in str(warning)


def test_diagnostic_bundle_warn_does_not_silently_swallow(monkeypatch):
    smonitor.configure(profile="user", level="DEBUG", event_buffer_size=10)
    bundle = DiagnosticBundle(
        catalog={"warnings": {"UserWarning": {"code": "X-WARN", "source": "lib.warn"}}},
        meta={"doc_url": "https://example.org"},
        package_root=Path.cwd(),
    )

    def _boom(*args, **kwargs):
        raise RuntimeError("catalog emit failed")

    monkeypatch.setattr("smonitor.integrations.diagnostic.emit_from_catalog", _boom)

    with pytest.warns(UserWarning, match="hello"):
        bundle.warn("hello", UserWarning)

    events = smonitor.get_manager().recent_events()
    assert events
    assert any(e.get("source") == "smonitor.integrations.diagnostic" for e in events)


def test_ensure_configured_reset_allows_reconfiguration(monkeypatch, tmp_path):
    calls: list[Path] = []

    def _fake_configure(*, config_path):
        calls.append(Path(config_path))

    reset_configured_packages()
    monkeypatch.setattr("smonitor.integrations.core.smonitor.configure", _fake_configure)

    ensure_configured(tmp_path)
    ensure_configured(tmp_path)
    assert len(calls) == 1

    reset_configured_packages()
    ensure_configured(tmp_path)
    assert len(calls) == 2
