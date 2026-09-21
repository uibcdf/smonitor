from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from versioningit.basics import basic_tag2version
from versioningit.errors import InvalidTagError

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("tag", ["0.16.0", "1.0.0", "12.34.567"])
def test_versioningit_accepts_canonical_release_tags(tag: str) -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    params = config["tool"]["versioningit"]["tag2version"]
    assert basic_tag2version(tag=tag, params=params) == tag


@pytest.mark.parametrize(
    "tag",
    ["v0.16.0", "0.16", "01.0.0", "0.16.0rc1", "0.16.0.dev1", "0.16.0+local"],
)
def test_versioningit_rejects_noncanonical_release_tags(tag: str) -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    params = config["tool"]["versioningit"]["tag2version"]
    with pytest.raises(InvalidTagError):
        basic_tag2version(tag=tag, params=params)
