Integrations
============

smonitor provides thin integration helpers for ecosystem libraries.

MolSysMT
--------

Replace MolSysMT logging setup with:

::

  from smonitor.integrations import configure_molsysmt
  configure_molsysmt(profile="user")

Suggested `_smonitor.py` for MolSysMT
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
