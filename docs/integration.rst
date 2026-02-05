Integrations
============

smonitor provides thin integration helpers for ecosystem libraries.

MolSysMT
--------

Replace MolSysMT logging setup with:

::

  from smonitor.integrations import configure_molsysmt
  configure_molsysmt(profile="user")

ArgDigest / DepDigest
---------------------

Use the same pattern to centralize diagnostics:

::

  from smonitor.integrations import configure_argdigest, configure_depdigest
  configure_argdigest(profile="dev")
  configure_depdigest(profile="dev")
