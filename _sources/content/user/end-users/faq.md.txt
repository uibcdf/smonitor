# End-User FAQ

## Do I need to install extra tools to use a host library?

Usually no. If the host library integrates SMonitor, diagnostics are part of normal usage.

## Do I need to learn SMonitor architecture?

No. You can keep using your host library as usual and only use message hints when needed.

## Can I disable extra diagnostics?

Possibly, depending on what controls the host library exposes. Check your host library documentation
for verbosity/debug options.

## Will SMonitor slow down my normal workflow?

For standard usage, impact should generally be low. Advanced modes (debug,
profiling, deep tracing) are typically meant for troubleshooting sessions.

## What is the fastest way to get help?

Share:
- exact warning/error text and code ID,
- minimal reproducer,
- version and environment info,
- optional redacted bundle if the host library recommends it.
