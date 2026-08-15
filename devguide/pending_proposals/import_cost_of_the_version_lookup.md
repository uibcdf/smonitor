# Proposal: stop paying 55 ms to learn our own version number

**Status:** proposal (2026-08-15). Measured on this host, with the command next to each figure.
**Origin:** PyUnitWizard, while accounting for its startup cost. `import pyunitwizard` costs 62 ms,
of which **55.7 ms is `import smonitor`** and 1.5 ms is PyUnitWizard itself. Every library that
depends on SMonitor pays this before doing anything.

---

## 1. Where the time goes

```bash
python -X importtime -c "import smonitor" 2>&1 | sort -t'|' -k2 -rn | head -8
```

| module | cumulative |
|---|---:|
| `smonitor` | 71.8 ms |
| `importlib.metadata` | **33.1 ms** |
| `importlib.metadata._adapters` | 16.7 ms |
| `email.message` | 16.0 ms |
| `smonitor.bundle` | 11.9 ms |
| `zipfile` | 5.8 ms |

`importlib.metadata` is 46% of the import, and it drags in `email.message`, `zipfile`, `quopri`
and `inspect` — the machinery for parsing package metadata out of distributions.

## 2. What it is used for

`smonitor/__init__.py`, lines 3-12:

```python
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("smonitor")
except PackageNotFoundError:
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"
```

A version string. The expensive route is tried **first**, and the cheap one — `smonitor/_version.py`,
which exists and currently reads `__version__ = "0.12.0"` — only on failure.

```bash
python -c "
import time
t=time.perf_counter(); import importlib.metadata
print(f'{(time.perf_counter()-t)*1000:.1f} ms  import importlib.metadata')
t=time.perf_counter(); importlib.metadata.version('smonitor')
print(f'{(time.perf_counter()-t)*1000:.1f} ms  version() once imported')"
```

**32.0 ms** to import, **22.8 ms** to call. About 55 ms of a 71.8 ms import, to read a string that
is already sitting in a file next to `__init__.py`.

## 3. The change

Try the local file first, and import `importlib.metadata` only inside the branch that needs it:

```python
try:
    from ._version import __version__
except ImportError:                       # not built: fall back to distribution metadata
    try:
        from importlib.metadata import version
        __version__ = version("smonitor")
    except Exception:
        __version__ = "0.0.0+unknown"
```

This is what PyUnitWizard already does — it tries `._version` first — except that it also imports
`importlib.metadata` at module level, so it pays the 32 ms anyway. Both repositories want the same
correction; PyUnitWizard's is currently masked because SMonitor has already paid it.

Two things to check before adopting:

- **`_version.py` must be reliably present in an installed distribution.** It is versioningit-written
  and git-ignored, so it exists in a build but not in a fresh clone. Trying it first means a
  development checkout without a build takes the slow path — correct, and only in development.
- **The version must not go stale.** Reading `_version.py` reports what the last build wrote, while
  `version()` reports the installed distribution. For an editable install these can disagree. That is
  already true of PyUnitWizard, where `puw.__version__` reported `0.22.0` on a checkout describing as
  `0.24.0` — worth deciding deliberately rather than inheriting.

## 4. A second item, smaller

`smonitor.bundle` costs 11.9 ms and pulls in `importlib.resources` and `zipfile`. `__init__.py`
imports four names from it eagerly (`collect_bundle`, `compare_bundles`, `export_bundle`, ...), none
of which are on any hot path — they are support-bundle operations. PEP 562 module-level
`__getattr__`, which SMonitor's consumers already use, would defer it without changing the public
surface.

## 5. What it would be worth

If both land, `import smonitor` goes from 71.8 ms to roughly 5 ms, and every dependent library
inherits that. It is the cheapest startup win available anywhere in the stack: PyUnitWizard's own
import is already 1.5 ms, so SMonitor is currently 97% of what a consumer pays to reach it.

## 6. How to verify

```bash
python -X importtime -c "import smonitor" 2>&1 | tail -1
python -c "import smonitor; print(smonitor.__version__)"
```

The second is the one that matters: the version string must not change.
