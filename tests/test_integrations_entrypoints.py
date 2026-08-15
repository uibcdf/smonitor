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


def test_package_version_matches_the_version_module():
    """`smonitor.__version__` reads `_version.py` when the tree has a build.

    The lookup order matters for startup cost, not just correctness: reaching
    for `importlib.metadata` first pulled in `email.message`, `zipfile` and
    `inspect` on every import of the package, and every dependent library paid
    it. The two sources agree in an installed distribution, so preferring the
    cheap one must not change the string anyone reads.
    """
    import smonitor

    assert smonitor.__version__ == version_module.__version__


def test_importing_smonitor_does_not_pull_in_importlib_metadata():
    """Guard the startup cost against regressions.

    Asserted in a subprocess because the test session itself has already
    imported plenty; only a clean interpreter shows what `import smonitor`
    actually costs.
    """
    import subprocess
    import sys

    # Asks whether *smonitor* introduced the module, not whether it is loaded:
    # an unrelated .pth in site-packages (editable installs of sibling repos do
    # this) can load it before any of our code runs, and that is not a failure.
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys\n"
            "before = 'importlib.metadata' in sys.modules\n"
            "import smonitor\n"
            "after = 'importlib.metadata' in sys.modules\n"
            "sys.exit(1 if after and not before else 0)\n",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "importing smonitor pulled in importlib.metadata; "
        "the version lookup should read _version.py first"
    )
