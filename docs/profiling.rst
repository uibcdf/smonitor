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

Timeline buffer
---------------

`profiling_buffer_size` controls how many recent timings are stored in memory.

:: 

  smonitor.configure(profiling=True, profiling_buffer_size=200)
  print(smonitor.report()["timeline"][:5])

Sampling
--------

`profiling_sample_rate` controls sampling (0.0–1.0).

::

  smonitor.configure(profiling=True, profiling_sample_rate=0.1)

Sampling also applies to `span(...)` context blocks.

GPU and accelerator hooks
-------------------------

You can provide `profiling_hooks` (list of callables) to include accelerator
metadata in `report()` without hard dependencies.

Example (pseudo-code):: 

  def gpu_hook():
      # Use pynvml or torch if available
      return {"gpu_name": "A100", "gpu_mem_used_mb": 1024}

  smonitor.configure(profiling=True, profiling_hooks=[gpu_hook])

Export timeline
---------------

::

  from smonitor.profiling import export_timeline
  export_timeline(\"timeline.json\", format=\"json\")
  export_timeline(\"timeline.csv\", format=\"csv\")

Timeline entries may include a `span=True` flag and an optional `meta` dict
when recorded via `span(...)`.

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
