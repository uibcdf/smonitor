Integrations
============

smonitor provides thin integration helpers for ecosystem libraries.

MolSysMT
--------

Replace MolSysMT logging setup with:

::

  from smonitor.integrations import configure_molsysmt
  configure_molsysmt(profile="user")

Suggested `_smonitor.py` for MolSysMT (package root)
------------------------------------

:: 

  PROFILE = "user"

  SMONITOR = {
    "level": "WARNING",
    "capture_warnings": True,
    "capture_logging": True,
    "trace_depth": 3,
  }

  PROFILES = {
    "user": {"level": "WARNING", "style": "user"},
    "dev": {"level": "INFO", "style": "dev"},
  }

  ROUTES = [
    {"when": {"source_prefix": "molsysmt."}, "send_to": ["console"]},
  ]

ArgDigest / DepDigest
---------------------

Use the same pattern to centralize diagnostics:

::

  from smonitor.integrations import configure_argdigest, configure_depdigest
  configure_argdigest(profile="dev")
  configure_depdigest(profile="dev")

Catalog pattern
---------------

Keep library-specific catalogs under `A/_private/smonitor/catalog.py` with optional
metadata in `A/_private/smonitor/meta.py`. Load them in `A/_smonitor.py`.
