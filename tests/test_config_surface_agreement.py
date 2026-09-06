"""The three lists of configuration keys must agree.

`Manager.configure`'s signature, the `SMONITOR` allowlist in `smonitor.config`,
and what `smonitor.configure()` forwards to the manager had drifted apart, in
all three directions at once:

- `silence` and `duplicate_policy` were accepted by the manager and rejected by
  the validator — `silence` in the canonical guide's own first example;
- `style` sat in the shipped template, accepted by nobody, and reached
  `Manager.configure` as a keyword argument, so copying the template raised
  `TypeError` inside the host library's import.

These tests fail on the shape of the drift rather than on the individual keys,
so a keyword added to `Manager.configure` cannot reopen it.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import smonitor
from smonitor.config import ALLOWED_SMONITOR_KEYS, validate_project_config
from smonitor.config.discovery import load_config_from_path
from smonitor.core.manager import CONFIGURE_PARAMETERS, Manager

TEMPLATE = Path(smonitor.__file__).parent / "templates" / "_smonitor.py"


def test_configure_parameters_match_the_signature():
    expected = set(inspect.signature(Manager.configure).parameters) - {"self"}
    assert CONFIGURE_PARAMETERS == expected


def test_every_allowed_config_key_is_one_the_manager_accepts():
    # `strict_config` governs validation rather than the manager, and is the
    # only key allowed in a config file that `Manager.configure` never sees.
    assert ALLOWED_SMONITOR_KEYS - CONFIGURE_PARAMETERS == {"strict_config"}


@pytest.mark.parametrize("key", ["silence", "duplicate_policy", "duplicate_every_n"])
def test_keys_the_manager_reads_from_the_config_block_validate(key):
    assert key in ALLOWED_SMONITOR_KEYS


def _write(tmp_path: Path, body: str) -> Path:
    (tmp_path / "_smonitor.py").write_text(body, encoding="utf-8")
    return tmp_path


def test_the_canonical_guide_first_example_validates(tmp_path):
    # standards/SMONITOR_GUIDE.md, section 1.
    root = _write(
        tmp_path,
        '''PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
    "silence": ["pint", "networkx"],
}
''',
    )
    assert validate_project_config(load_config_from_path(root / "_smonitor.py")) == []


def test_the_shipped_template_validates_and_configures(tmp_path):
    root = _write(tmp_path, TEMPLATE.read_text(encoding="utf-8"))
    assert validate_project_config(load_config_from_path(root / "_smonitor.py")) == []
    # Copying the template used to raise `TypeError: Manager.configure() got an
    # unexpected keyword argument 'style'`.
    manager = smonitor.configure(config_path=root, handlers=[])
    assert manager.config.level == "WARNING"


def test_an_unknown_config_file_key_is_reported_but_does_not_raise(tmp_path):
    root = _write(tmp_path, 'SMONITOR = {"level": "INFO", "levl": "DEBUG"}\n')
    cfg = load_config_from_path(root / "_smonitor.py")

    assert validate_project_config(cfg) == ["Unknown SMONITOR key: levl"]

    # A typo in a config file must not take down the import of the library that
    # loads it, and must not be silently accepted either.
    manager = smonitor.configure(config_path=root, handlers=[])
    assert manager.config.level == "INFO"

    with pytest.raises(ValueError, match="Unknown SMONITOR key: levl"):
        smonitor.configure(config_path=root, handlers=[], strict_config=True)


def test_an_unknown_keyword_passed_directly_still_raises(tmp_path):
    # The caller wrote it on the line they are looking at; an immediate
    # `TypeError` is the right answer there.
    with pytest.raises(TypeError, match="levl"):
        smonitor.configure(config_path=tmp_path, handlers=[], levl="DEBUG")
