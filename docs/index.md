```{eval-rst}
:html_theme.sidebar_secondary.remove:
```

# SMonitor

:::{figure} _static/logo.svg
:width: 45%
:align: center

Signal Monitor for the scientific Python stack.

```{image} https://img.shields.io/badge/release-0.10.0-white.svg
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

## Install

```bash
conda install -c uibcdf smonitor
```

## Start in one minute

```python
import smonitor

smonitor.configure(profile="user", theme="plain")
smonitor.emit("WARNING", "Selection is ambiguous", source="mylib.select")
```

## Documentation map

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
