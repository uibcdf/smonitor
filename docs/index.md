```{eval-rst}
:html_theme.sidebar_secondary.remove:
```

:::{figure} _static/logo.svg
:width: 45%
:align: center

Signal Monitor for the scientific Python stack.

```{image} https://img.shields.io/badge/release-0.11.0-white.svg
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
