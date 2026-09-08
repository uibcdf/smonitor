# First Runnable Integration

This page gives you a minimal, fully runnable wiring you can copy and execute
in a fresh package.

## Minimal package layout

```text
mylib/
  __init__.py
  _smonitor.py
  _private/
    smonitor/
      __init__.py
      catalog.py
      emitter.py
  api.py
```

## Files

`mylib/_private/smonitor/catalog.py`

```python
CATALOG = {
    "codes": {
        "MYLIB-W001": {
            "user_message": "Selection '{selection}' may be too broad.",
            "user_hint": "Use a more specific selector, for example '{example}'.",
        }
    },
    "warnings": {
        "BroadSelectionWarning": {
            "code": "MYLIB-W001",
            "source": "mylib.select_atoms",
            "category": "selection",
            "level": "WARNING",
        }
    },
    "signals": {},
}

CODES = CATALOG["codes"]
SIGNALS = CATALOG["signals"]
```

`DiagnosticBundle` finds a warning in the `warnings` group by its class name, so
without that group `warn()` emits nothing.

`mylib/_private/smonitor/__init__.py`

```python
from pathlib import Path

from .catalog import CATALOG

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
```

`mylib/_private/smonitor/emitter.py`

```python
from smonitor.integrations import DiagnosticBundle

from . import CATALOG, PACKAGE_ROOT

bundle = DiagnosticBundle(CATALOG, {"library": "mylib"}, PACKAGE_ROOT)
warn = bundle.warn
```

`mylib/_private/smonitor/warnings.py`

```python
from smonitor.integrations import CatalogWarning

from . import CATALOG


class BroadSelectionWarning(CatalogWarning):
    catalog_key = "BroadSelectionWarning"

    def __init__(self, message=None, *, selection=None, example=None):
        super().__init__(
            message,
            catalog=CATALOG,
            extra={"selection": selection, "example": example},
        )
```

`mylib/_smonitor.py`

```python
from mylib._private.smonitor.catalog import CODES, SIGNALS

PROFILE = "user"
SMONITOR = {"level": "WARNING", "capture_warnings": True, "capture_logging": True}
```

`mylib/api.py`

```python
from smonitor import signal
from ._private.smonitor.emitter import warn
from ._private.smonitor.warnings import BroadSelectionWarning


@signal(tags=["selection"])
def select_atoms(selection: str):
    if selection == "all":
        warn(BroadSelectionWarning(selection=selection, example="atom_name == 'CA'"))
```

`mylib/__init__.py`

```python
from smonitor.integrations import ensure_configured
from ._private.smonitor import PACKAGE_ROOT

ensure_configured(PACKAGE_ROOT)
```

## Smoke run

```bash
python -c "import mylib.api as a; a.select_atoms('all')"
```

Expected behavior:
- import succeeds,
- one warning is emitted with code `MYLIB-W001`,
- message/hint come from catalog template.
