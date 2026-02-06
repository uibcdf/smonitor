Bundles
=======

Local bundles are privacy-first exports that capture the current smonitor state,
recent events, and profiling summaries for reproducible diagnosis.

CLI export
----------

.. code-block:: bash

   smonitor export --out smonitor_bundle --max-events 500

This produces a directory with:

- `bundle.json` (config, policy, codes/signals, report)
- `events.jsonl` (recent events, optional)

Use `--out bundle.json` to generate a single JSON file instead of a directory.

Configuration
-------------

To enable event buffering for exports:

.. code-block:: python

   # _smonitor.py
   SMONITOR = {
       "event_buffer_size": 500,
   }

You can also override at runtime:

.. code-block:: python

   smonitor.configure(event_buffer_size=500)

Notes
-----

Bundles are local-only by default. Users decide if and when to share them.
