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

MemoryHandler usage
-------------------

For testing or debugging purposes, you can use the ``MemoryHandler`` to
capture events in-memory and inspect them later.

.. code-block:: python

  from smonitor.handlers.memory import MemoryHandler
  import smonitor

  mem = MemoryHandler()
  smonitor.configure(handlers=[mem])

  smonitor.emit("INFO", "Hello world")
  
  # Retrieve captured events
  events = mem.get_events()
  assert events[0]["message"] == "Hello world"

Generate catalog
----------------

::

  python docs/_gen_catalog.py
