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

Generate catalog
----------------

::

  python docs/_gen_catalog.py
