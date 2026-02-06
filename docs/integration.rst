Integrations
============

smonitor provides thin integration helpers for ecosystem libraries.

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
-----------------------------------

Use the same package-level pattern and emit via catalog entries.

Catalog pattern
---------------

Keep library-specific catalogs under `A/_private/smonitor/catalog.py` with optional
metadata in `A/_private/smonitor/meta.py`. Load them in `A/_smonitor.py`.

Canonical guide
---------------

Use `standards/SMONITOR_GUIDE.md` as the source of truth for integration.
