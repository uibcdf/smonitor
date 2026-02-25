# Quick Start

This is the fastest path to a real SMonitor integration.

## Goal

In this page you will:
- configure SMonitor for your library,
- emit a catalog-based warning,
- decorate one public function for traceability.

At the end, you should see clear user-facing diagnostics and structured context.

## 1. Install

```bash
conda install -c uibcdf smonitor
```

or from source:

```bash
python -m pip install --no-deps --editable .
```

## 2. Create `_smonitor.py` in your package root

If your package is `mylib`, create `mylib/_smonitor.py`:

```python
PROFILE = "user"

SMONITOR = {
    "level": "WARNING",
    "trace_depth": 3,
    "capture_warnings": True,
    "capture_logging": True,
    "theme": "plain",
}
```

## 3. Create the catalog

Create `mylib/_private/smonitor/catalog.py`:

```python
CATALOG = {
    "codes": {
        "MYLIB-W001": {
            "title": "Selection is broad",
            "user_message": "Selection '{selection}' may be too broad.",
            "user_hint": "Use a more specific selector, for example '{example}'.",
            "dev_message": "Broad selection received in parser path.",
            "dev_hint": "Review selector normalization for this call.",
        }
    },
    "signals": {},
}
```

## 4. Enable SMonitor on import

In `mylib/__init__.py`:

```python
from smonitor.integrations import ensure_configured
from ._private.smonitor import PACKAGE_ROOT

ensure_configured(PACKAGE_ROOT)
```

## 5. Emit via catalog and instrument one API function

```python
from smonitor import signal
from ._private.smonitor.emitter import warn

@signal(tags=["selection"])
def select_atoms(selection: str):
    if selection == "all":
        warn(
            code="MYLIB-W001",
            extra={"selection": selection, "example": "atom_name == 'CA'"},
        )
```

## Expected result

When `selection == "all"`, users get a warning that:
- explains what happened,
- suggests a concrete fix,
- stays consistent with your library profile.

## Next

Continue with [Mini Library Walkthrough](mini-library-walkthrough.md) for a complete example.
