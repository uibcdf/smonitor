Examples
========

User profile
------------

::

  import smonitor
  smonitor.configure(profile="user")
  smonitor.emit("WARNING", "Selección ambigua", source="molsysmt.select")

Dev profile
-----------

::

  import smonitor
  smonitor.configure(profile="dev", args_summary=True)

  @smonitor.signal
  def select(molsys, selection):
      if not selection:
          raise ValueError("selection is required")

  select(None, "")

QA profile
----------

::

  import smonitor
  smonitor.configure(profile="qa")
  smonitor.emit("WARNING", "Selection ambiguous", code="MSM-W010")
