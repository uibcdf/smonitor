"""The sweep in `devtools/verify_integration.py` runs the guide's section 7 checks.

It exists so that a suite-wide answer is one command rather than nine copies of a
test file, and it is tested here so it cannot quietly stop finding things. Both
fixtures below are the shapes it found in the ecosystem on 2026-09-06: a catalog
whose `CODES` are indexed by group rather than by code, and one whose codes point
straight at message strings.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "devtools" / "verify_integration.py"


@pytest.fixture(scope="module")
def verifier():
    spec = importlib.util.spec_from_file_location("verify_integration", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    yield module
    sys.modules.pop(spec.name, None)


def _library(root: Path, name: str, *, config: str, catalog: str, extra: str = "") -> Path:
    repo = root / name
    pkg = repo / name
    private = pkg / "_private" / "smonitor"
    private.mkdir(parents=True)
    (pkg / "__init__.py").write_text("raise AssertionError('must not be imported')\n")
    (pkg / "_smonitor.py").write_text(config, encoding="utf-8")
    (private / "__init__.py").write_text("", encoding="utf-8")
    (private / "catalog.py").write_text(catalog, encoding="utf-8")
    if extra:
        (pkg / "errors.py").write_text(extra, encoding="utf-8")
    return repo


GOOD_CATALOG = '''
CATALOG = {"warnings": {"Thing": {"code": "GOOD-W001", "source": "good.thing"}}}
CODES = {"GOOD-W001": {"user_message": "Thing {name} went sideways."}}
'''


def test_a_correct_integration_passes_every_check(verifier, tmp_path):
    repo = _library(tmp_path, "good", config='PROFILE = "user"\n', catalog=GOOD_CATALOG)
    result = verifier.verify(repo)
    assert not result.failed, result.rows
    # The library's own __init__ raises if imported; reaching the catalog anyway
    # is the point of the synthetic package chain.
    assert dict((c, ok) for c, ok, _ in result.rows)["3 renders"] is True


def test_it_reports_a_code_with_no_template(verifier, tmp_path):
    repo = _library(
        tmp_path,
        "orphan",
        config='PROFILE = "user"\n',
        catalog='CATALOG = {"warnings": {"T": {"code": "O-W001"}}}\nCODES = {}\n',
    )
    rows = {check: (ok, detail) for check, ok, detail in verifier.verify(repo).rows}
    assert rows["2 templates"][0] is False
    assert "O-W001" in rows["2 templates"][1]


def test_it_reports_codes_that_render_empty(verifier, tmp_path):
    repo = _library(
        tmp_path,
        "blank",
        config='PROFILE = "user"\n',
        catalog='CATALOG = {}\nCODES = {"B-W001": {"title": "no message field"}}\n',
    )
    rows = {check: (ok, detail) for check, ok, detail in verifier.verify(repo).rows}
    assert rows["3 renders"][0] is False
    assert "user:1/1" in rows["3 renders"][1]


def test_it_reports_an_assignment_to_a_base_owned_name(verifier, tmp_path):
    repo = _library(
        tmp_path,
        "reserved",
        config='PROFILE = "user"\n',
        catalog=GOOD_CATALOG,
        extra=(
            "from smonitor.integrations import CatalogWarning\n\n\n"
            "class Mine(CatalogWarning):\n"
            "    def __init__(self, message=None):\n"
            "        self.hint = 'mine'\n"
            "        super().__init__(message)\n"
        ),
    )
    rows = {check: (ok, detail) for check, ok, detail in verifier.verify(repo).rows}
    assert rows["5 reserved"][0] is False
    assert "Mine.self.hint" in rows["5 reserved"][1]


def test_it_reports_an_invalid_configuration(verifier, tmp_path):
    repo = _library(
        tmp_path,
        "badconfig",
        config='PROFILE = "user"\nSMONITOR = {"levl": "DEBUG"}\n',
        catalog=GOOD_CATALOG,
    )
    rows = {check: (ok, detail) for check, ok, detail in verifier.verify(repo).rows}
    assert rows["1 config"][0] is False
    assert "levl" in rows["1 config"][1]
