from pathlib import Path

import smonitor
from smonitor.integrations.diagnostic import DiagnosticBundle, _catalog_entry


def test_catalog_entry_none_conditions():
    assert _catalog_entry(None, "warnings", "X") is None
    assert _catalog_entry({}, "warnings", None) is None
    assert _catalog_entry({"warnings": []}, "warnings", "X") is None


def test_diagnostic_warn_success_path_also_raises_the_python_warning(monkeypatch):
    """A catalog hit emits the structured event *and* warns.

    This used to return early, leaving the diagnostic visible only as an
    SMonitor event. That silently took `pytest.warns`, `filterwarnings` and
    `simplefilter("error")` away from the adopting library's own users and test
    suites, which is why downstream libraries kept calling `warnings.warn`
    directly and lost their catalog metadata instead.
    """
    bundle = DiagnosticBundle(
        catalog={"warnings": {"UserWarning": {"code": "X1"}}},
        meta={},
        package_root=Path.cwd(),
    )
    called = {}
    warned = []

    def _ok(*args, **kwargs):
        called["ok"] = True
        return {}

    monkeypatch.setattr("smonitor.integrations.diagnostic.emit_from_catalog", _ok)
    monkeypatch.setattr("warnings.warn", lambda *a, **k: warned.append((a, k)))
    bundle.warn("hello", UserWarning)
    assert called["ok"] is True
    assert warned, "the catalog path must still raise the Python warning"


def test_diagnostic_warn_fallback_when_smonitor_emit_fails(monkeypatch):
    smonitor.configure(profile="user", handlers=[], event_buffer_size=5)
    bundle = DiagnosticBundle(
        catalog={"warnings": {"UserWarning": {"code": "X1"}}},
        meta={},
        package_root=Path.cwd(),
    )

    def _boom_emit_from_catalog(*args, **kwargs):
        raise RuntimeError("boom")

    def _boom_emit(*args, **kwargs):
        raise RuntimeError()

    monkeypatch.setattr(
        "smonitor.integrations.diagnostic.emit_from_catalog",
        _boom_emit_from_catalog,
    )
    monkeypatch.setattr(
        "smonitor.integrations.diagnostic.smonitor.emit",
        _boom_emit,
    )
    seen = []
    monkeypatch.setattr("warnings.warn", lambda *a, **k: seen.append((a, k)))

    bundle.warn("hello", UserWarning)
    assert seen


def test_diagnostic_bundle_resolve_empty_returns_empty_string():
    bundle = DiagnosticBundle(catalog={}, meta={}, package_root=Path.cwd())
    assert bundle.resolve(message=None, code=None, extra=None) == ""
