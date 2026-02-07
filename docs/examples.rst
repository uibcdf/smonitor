Examples
========

The following examples demonstrate how ``smonitor`` can be used to improve
the diagnostic experience in different scenarios.

User-Facing Warnings
--------------------

When building a library for end users, you want warnings to be clear and
helpful, without overwhelming them with stack traces.

.. code-block:: python

  import smonitor
  
  # Configure for high-quality user output
  smonitor.configure(profile="user", theme="rich")
  
  # Emit a warning with a helpful hint
  smonitor.emit("WARNING", 
                "Selection string 'all' is very broad", 
                source="molsysmt.select",
                extra={"hint": "Specify a more granular selection to improve performance."})

Developer Diagnostics
---------------------

For developers, ``smonitor`` provides deep traceability and structured data.

.. code-block:: python

  import smonitor
  
  # Configure for detailed developer output
  smonitor.configure(profile="dev", theme="rich", args_summary=True)

  @smonitor.signal(tags=["topology"])
  def find_atoms(molsys, selection="*"):
      # Standard logging is automatically captured
      import logging
      logging.info("Starting atom search...")
      
      if not molsys:
          # Exceptions are captured before being re-raised
          raise ValueError("Molecular system cannot be None")

  try:
      find_atoms(None)
  except ValueError:
      pass

Nested Call-Chains (Breadcrumbs)
-------------------------------

``smonitor`` shines when multiple libraries are integrated.

.. code-block:: python

  import smonitor
  smonitor.configure(profile="debug", theme="rich")

  @smonitor.signal
  def high_level_api():
      low_level_logic()

  @smonitor.signal
  def low_level_logic():
      smonitor.emit("INFO", "Executing deep logic")

  high_level_api()
  # Output will show the breadcrumb trail: [high_level_api ❯ low_level_logic]

Policy-Driven Filtering
-----------------------

Prevent "log flooding" in repetitive loops using the policy engine.

.. code-block:: python

  import smonitor
  
  # Only allow 1 warning every 100 calls for a specific code
  smonitor.configure(
      filters=[
          {"when": {"code": "W001"}, "rate_limit": "1/100"}
      ]
  )

  for i in range(1000):
      smonitor.emit("WARNING", "Repetitive warning", code="W001")
  
  # Only 10 warnings will actually be shown.