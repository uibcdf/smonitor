# Scoped diagnostic capture

SMonitor's default diagnostics include native exception text and collect arguments
on errors even when `args_summary=False`. Applications with a stricter capture
contract can explicitly restrict collection before calling a provider:

```python
import smonitor

with smonitor.diagnostic_scope(safe_extra={"operation_id": "op-17", "attempt": 1}):
    result = provider_call(configuration)
```

The default scope policy is `METADATA_ONLY`. SMonitor skips argument summaries,
native exception stringification and `extra_factory` calls. Events omit inherited
frames, ordinary `extra`, tags and caller-supplied messages. They retain catalog
identity, exception type, configured runtime identifiers and explicitly approved
safe facts. Profiling keeps numeric timings and approved facts. Default detailed
diagnostics resume when the scope exits, including after exceptions.

The equivalent callable policy is:

```python
@smonitor.signal(capture_policy=smonitor.METADATA_ONLY,
                 safe_extra={"operation": "validate-config"})
def validate(configuration):
    return provider_call(configuration)
```

`@signal` supports ordinary and async functions; an async policy spans the actual
awaited execution. Generator iteration is not instrumented by this decorator;
put a scope around iteration when it calls providers.

## Separate capture permissions

`CapturePolicy` is immutable and has four boolean permissions:

| Field | What `False` prohibits |
| --- | --- |
| `arguments` | Automatic argument `repr`, including the lazy error summary; inherited frame arguments are omitted. |
| `exception_text` | Native exception stringification and explicit free-text diagnostic messages. |
| `inherited_context` | Attaching enclosing breadcrumb frames to an event. |
| `extra` | Ordinary event/frame extras, tags, `extra_factory` and profiling-hook payloads. |

`CapturePolicy()` preserves detailed defaults. `METADATA_ONLY` sets all four
permissions to `False`. Nested scopes combine permissions with AND, so a provider
cannot relax a caller's restriction. `get_capture_policy()` lets providers inspect
the current permissions **before** constructing diagnostic payloads.

`safe_extra` accepts an exact `dict` containing at most 32 aggregate fields, including
inherited safe facts. Keys are nonempty strings of at most 80 characters. Values
are exact builtin `str` (at most 256 characters), `bool`, `None`, signed integers
with at most 64 magnitude bits, or finite floats. Containers, subclasses and arbitrary
objects raise `CapturePolicyError` with code `SMONITOR-CAPTURE-INVALID`, without
stringification. Facts are copied at entry; mutation of the input dictionary does
not change the scope. Inner declarations may override an outer fact. Automatic
slow-call/summary metadata uses available slots without exceeding this budget.

These facts are explicitly approved by the caller. A string containing scientific
data or a credential is still a string; this API is not a content classifier or
redaction service. Identity arguments such as `source` and `correlation_id` likewise
must be deliberately chosen identifiers.

## Emit without inherited payloads

An individual event can request the same policy:

```python
smonitor.emit("ERROR", "", code="MYLIB-CONFIG-INVALID", source="mylib.configure",
              metadata_only=True, safe_extra={"operation_id": "op-17"})
```

Restrictions apply before catalog rendering, fingerprinting, summaries, coalescing,
observers, handlers and buffering. Route/filter selection still runs; event-mutating
route transformations are skipped under a restrictive policy so they cannot add
unapproved payloads. Deferred duplicate/coalesced events retain the originating
policy and facts even when flushed outside the scope. Aggregation separates capture
policies and safe facts without changing event fingerprints.

An event-only option cannot undo argument `repr` already evaluated by an enclosing
provider. Put the scope around the entire provider call to prevent that collection.
Scopes also do not erase events or profiling data collected before entry.

## Catalog descriptions and failure precedence

Catalogs can provide `metadata_message` and `metadata_hint` using approved primitive
fields. Otherwise the selected audience's catalog message is used when all fields
are available; unavailable or unsupported fields produce a fixed catalog description.
Explicit native/free-text messages and exception-owned extras are omitted. Known
catalog codes are preserved; unknown native failures use `SMONITOR-NATIVE-FAILURE`
and a bounded exception type. Bundles expose SMonitor's fixed descriptions under
`internal_codes` alongside provider catalogs.

SMonitor re-raises the same native object with its cause and traceback. Signal and
profiling fallbacks use fixed catalog descriptions under the restrictive policy.
Diagnostic errors, including warnings promoted to errors, cannot replace the
operation's exception or prevent its successful return.

## Tasks, threads and ownership

Scopes use immutable `ContextVar` state and restore their tokens. Async tasks inherit
the context at task creation and can interleave independent scopes. For threads and
thread pools, propagate explicitly with a fresh `copy_context().run(callable, ...)`
per submission; use `Context().run(...)` for an independent detailed context.
Do not assume a Python version or thread-pool configuration propagates context.

The contract governs SMonitor-owned automatic collection and rendering. It does
not prevent provider/user code from evaluating `str(error)` or `repr(value)` before
calling SMonitor, nor replace Python's own warning machinery, existing logging
formatters or a delegated original exception hook. Bundle configuration/provenance
snapshots and previously retained data keep their existing export/redaction contract.
ArgDigest's explicit `cause_message=str(error)` paths require adoption in the owning
issue [uibcdf/argdigest#29](https://github.com/uibcdf/argdigest/issues/29); SMonitor
provides the shared policy rather than a second provider-specific policy engine.
