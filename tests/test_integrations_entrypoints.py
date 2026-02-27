import smonitor._version as version_module
from smonitor.integrations import argdigest, depdigest, molsysmt


def test_version_module_exposes_version_string():
    assert isinstance(version_module.__version__, str)
    assert version_module.__version__


def test_configure_argdigest_delegates_to_smonitor(monkeypatch):
    called = {}

    def fake_configure(**kwargs):
        called["kwargs"] = kwargs
        return "ok-arg"

    monkeypatch.setattr(argdigest.smonitor, "configure", fake_configure)
    out = argdigest.configure_argdigest(profile="qa")
    assert out == "ok-arg"
    assert called["kwargs"]["profile"] == "qa"


def test_configure_depdigest_delegates_to_smonitor(monkeypatch):
    called = {}

    def fake_configure(**kwargs):
        called["kwargs"] = kwargs
        return "ok-dep"

    monkeypatch.setattr(depdigest.smonitor, "configure", fake_configure)
    out = depdigest.configure_depdigest(level="INFO")
    assert out == "ok-dep"
    assert called["kwargs"]["level"] == "INFO"


def test_configure_molsysmt_delegates_to_smonitor(monkeypatch):
    called = {}

    def fake_configure(**kwargs):
        called["kwargs"] = kwargs
        return "ok-msm"

    monkeypatch.setattr(molsysmt.smonitor, "configure", fake_configure)
    out = molsysmt.configure_molsysmt(theme="plain")
    assert out == "ok-msm"
    assert called["kwargs"]["theme"] == "plain"
