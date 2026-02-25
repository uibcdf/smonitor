Integrations
============

smonitor provides thin integration helpers for ecosystem libraries to ensure
automatic configuration and consistent emission.

Standard Pattern
----------------

The recommended way to integrate a library is:

1. Create a ``_smonitor.py`` in your package root.
2. Call ``ensure_configured`` in your library's ``__init__.py``.
3. Use ``@signal`` on public functions.
4. Use ``emit_from_catalog`` for structured diagnostics.

Example
-------

.. code-block:: python

  # mylib/__init__.py
  from pathlib import Path
  from smonitor.integrations import ensure_configured
  
  PACKAGE_ROOT = Path(__file__).parent
  ensure_configured(PACKAGE_ROOT)

.. code-block:: python

  # mylib/core.py
  from smonitor import signal
  from smonitor.integrations import emit_from_catalog
  from .catalog import ERRORS

  @signal(tags=["core"])
  def process(data):
      if not data:
          emit_from_catalog(ERRORS["MISSING_DATA"])
          return
      ...

MolSysMT
--------

Use package-level configuration and ensure smonitor is configured on import:

::

  from smonitor.integrations import ensure_configured
  from molsysmt._private.smonitor import PACKAGE_ROOT
  ensure_configured(PACKAGE_ROOT)

The package `_smonitor.py` controls default profiles and messages.

MolSysViewer
------------

Use package-level configuration and emit catalog-driven diagnostics for
frontend init failures and payload issues.

ArgDigest / DepDigest / PyUnitWizard
------------------------------------

Use the same package-level pattern and emit via catalog entries.

Catalog pattern
---------------

Keep library-specific catalogs under `A/_private/smonitor/catalog.py` with optional
metadata in `A/_private/smonitor/meta.py`. Load them in `A/_smonitor.py`.

Canonical guide
---------------

Use `standards/SMONITOR_GUIDE.md` as the source of truth for integration.
