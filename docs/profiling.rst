Profiling
=========

When `profiling=True`, smonitor records `duration_ms` per frame and aggregates
basic timing stats in `report()`.

Example
-------

::

  import smonitor
  smonitor.configure(profiling=True)

  @smonitor.signal
  def work():
      return 1

  work()
  print(smonitor.report()["timings"])

Output (example)
----------------

::

  {
    "mymodule.work": {
      "count": 1,
      "p50_ms": 0.12,
      "p95_ms": 0.12,
      "max_ms": 0.12
    }
  }
