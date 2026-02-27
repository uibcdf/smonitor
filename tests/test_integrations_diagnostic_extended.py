from pathlib import Path

import pytest

import smonitor
from smonitor.integrations.diagnostic import CatalogException, CatalogWarning, DiagnosticBundle


class MyException(CatalogException):
    catalog_key = "MyException"


class MyWarning(CatalogWarning):
    catalog_key = "MyWarning"


def test_catalog_entry_nested_resolution_for_exception_and_warning():
    smonitor.configure(
        profile="user",
        codes={
            "X-E": {"user_message": "Error happened", "user_hint": "do e"},
            "X-W": {"user_message": "Warn happened", "user_hint": "do w"},
        },
    )
    catalog = {
        "exceptions": {"MyException": {"code": "X-E"}},
        "warnings": {"MyWarning": {"code": "X-W"}},
    }
    exc = MyException(catalog=catalog)
    warn = MyWarning(catalog=catalog)
    assert "Error happened" in str(exc)
    assert "Warn happened" in str(warn)


def test_diagnostic_bundle_warn_once_emits_once(monkeypatch):
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10, enabled=True)
    bundle = DiagnosticBundle(catalog={"warnings": {}}, meta={}, package_root=Path.cwd())
    captured = []

    def _fake_warn(msg, cat=None, stacklevel=2):
        captured.append((str(msg), cat, stacklevel))

    monkeypatch.setattr("warnings.warn", _fake_warn)
    bundle.warn_once("hello", UserWarning)
    bundle.warn_once("hello", UserWarning)
    assert len(captured) == 1


def test_diagnostic_bundle_resolve_message_and_hint():
    smonitor.configure(
        profile="user",
        codes={"X-R": {"user_message": "M {x}", "user_hint": "H {x}"}},
    )
    bundle = DiagnosticBundle(catalog={}, meta={"library": "demo"}, package_root=Path.cwd())
    text = bundle.resolve(code="X-R", extra={"x": "1"})
    assert text == "M 1 H 1"


def test_diagnostic_bundle_warn_with_warning_instance(monkeypatch):
    smonitor.configure(profile="user", handlers=[], event_buffer_size=10, enabled=True)
    bundle = DiagnosticBundle(catalog={"warnings": {}}, meta={}, package_root=Path.cwd())
    seen = []

    def _fake_warn(msg, stacklevel=2):
        seen.append((msg, stacklevel))

    monkeypatch.setattr("warnings.warn", _fake_warn)
    bundle.warn(UserWarning("custom"), stacklevel=3)
    assert seen
    assert "custom" in str(seen[0][0])
    assert seen[0][1] == 3


def test_diagnostic_bundle_warn_fallback_emits_debug_event(monkeypatch):
    smonitor.configure(profile="user", level="DEBUG", handlers=[], event_buffer_size=10)
    bundle = DiagnosticBundle(
        catalog={"warnings": {"UserWarning": {"code": "X-W", "source": "lib.warn"}}},
        meta={"lib": "demo"},
        package_root=Path.cwd(),
    )

    def _boom(*args, **kwargs):
        raise RuntimeError("emit-fail")

    monkeypatch.setattr("smonitor.integrations.diagnostic.emit_from_catalog", _boom)
    with pytest.warns(UserWarning, match="hello"):
        bundle.warn("hello", UserWarning, extra={"ctx": "1"})
    events = smonitor.get_manager().recent_events()
    assert any(e.get("message") == "Catalog warning emission failed" for e in events)
