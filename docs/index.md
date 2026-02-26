```{eval-rst}
:html_theme.sidebar_secondary.remove:
```

:::{figure} _static/logo.svg
:width: 45%
:align: center

Precision diagnostics for scientific Python ecosystems.

```{image} https://img.shields.io/github/v/release/uibcdf/smonitor?color=white&label=release
:target: https://github.com/uibcdf/smonitor/releases
```
```{image} https://img.shields.io/badge/license-MIT-white.svg
:target: https://github.com/uibcdf/smonitor/blob/main/LICENSE
```
```{image} https://img.shields.io/badge/install%20with-conda-white.svg
:target: https://anaconda.org/uibcdf/smonitor
```
```{image} https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-white.svg
:target: https://www.python.org/downloads/
```
:::

## Why adopt now

- Make warnings and errors clearer and more actionable for end users.
- Reduce support time with stable diagnostic contracts (`code`, `signal`).
- Improve QA and automation workflows with structured events and bundles.

## Install it

```bash
conda install -c uibcdf smonitor
```

## Use it

```python
import smonitor

smonitor.configure(profile="user", theme="rich")

@smonitor.signal(name="mylib.select")
def select(items, query):
    if query == "all":
        smonitor.emit(
            "WARNING",
            "Selection is ambiguous.",
            code="MYLIB-W001",
            source="mylib.select",
            extra={"hint": "Use a more specific selector, for example atom_name == 'CA'."},
        )
    return items
```

What happens here:
- End users get a clear warning plus an actionable hint.
- Library maintainers keep stable contracts (`code`, `signal`) for support and QA.
- Teams can route the same events to bundles and machine-readable workflows.

Before:
- `ValueError: invalid argument`

With SMonitor:
- `ERROR [MYLIB-E001]: Input is invalid. Hint: Use a non-negative value.`

## Profiling and observability

SMonitor includes lightweight profiling for library workflows:
- decorator timing,
- manual spans,
- timeline buffering and export.

Use this for QA/debug observability without introducing heavy profiler dependencies.

## Ecosystem proof

Integrated across the current UIBCDF scientific stack:
- [MolSysMT](https://github.com/uibcdf/molsysmt)
- [MolSysViewer](https://github.com/uibcdf/molsysviewer)
- [ArgDigest](https://github.com/uibcdf/argdigest)
- [DepDigest](https://github.com/uibcdf/depdigest)
- [PyUnitWizard](https://github.com/uibcdf/pyunitwizard)

Start with the [User Guide](content/user/index.md) and follow the route matching your role.


```{eval-rst}

.. toctree::
   :maxdepth: 2
   :hidden:

   content/about/index.md

.. toctree::
   :maxdepth: 2
   :hidden:

   content/showcase/index.md

.. toctree::
   :maxdepth: 2
   :hidden:

   content/user/index.md

.. toctree::
   :maxdepth: 2
   :hidden:

   content/developer/index.md

.. toctree::
   :maxdepth: 2
   :hidden:

   api/index.md

```
