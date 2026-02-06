Cookbook
========

Basic setup
-----------

::

  import smonitor
  smonitor.configure(profile="user", theme="plain")

Emit with CODES
---------------

::

  smonitor.emit(
      "WARNING",
      "",
      code="MSM-W010",
      extra={"selection": "atom_name==", "example": "atom_name=='CA'"}
  )

Policy routing
--------------

::

  ROUTES = [
    {"when": {"level": "ERROR"}, "send_to": ["file"]}
  ]

Strict signals (dev/qa)
-----------------------

::

  smonitor.configure(profile="dev", strict_signals=True)

  # Missing required extras in SIGNALS will raise ValueError

CLI check with JSON
-------------------

::

  smonitor --check --check-event '{"level":"WARNING","message":"x","source":"molsysmt.select","code":"MSM-W010","extra":{"selection":"atom_name==","example":"atom_name==\\'CA\\'"}}'

CLI exit codes
--------------

- `0`: success
- `1`: no `_smonitor.py` found (validate)
- `2`: invalid configuration

Generate catalog
----------------

::

  python docs/_gen_catalog.py
