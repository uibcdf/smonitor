# Proposal: retain structured `extra` on catalog signals

**Status:** pending
**Reported from:** MolSysMT (2026-07-12), while wiring `GpuNotAvailableWarning` and
`MultipleMolecularSystemsError` to their catalog templates.

## Abstract

`CatalogWarning` and `CatalogException` accept structured data in `extra`, use it once to
interpolate the catalog template, and then throw it away. Only the rendered string survives on
the instance. Two consequences follow: templates for warnings emitted through
`DiagnosticBundle.warn()` cannot use any placeholder other than `{message}` and `{caller}`, and
code that catches a catalog exception cannot read the code or the structured fields that
produced it. We propose retaining `extra` and `code` on the instance, and having `warn()` merge
an instance's `extra` when it re-emits from the catalog.

---

## The Problem

### 1. `warn(instance)` drops the instance's structured data

`CatalogWarning.__init__` (`smonitor/integrations/diagnostic.py:74-98`) resolves the message and
keeps nothing else:

```python
resolved_msg, hint = smonitor.resolve(
    message=message, code=target_code, extra=merge_extra(meta, extra)
)
full_message = resolved_msg
if hint:
    full_message = f"{full_message} {hint}" if full_message else hint

self.message = full_message
super().__init__(full_message)
```

`extra` and `target_code` are local variables. They are never stored.

`DiagnosticBundle.warn()` (`diagnostic.py:166-217`) is then handed the instance and has no way to
recover them, so it re-emits from the catalog with a synthetic `extra` built from the rendered
string:

```python
if isinstance(message_or_warning, Warning):
    cls_name = type(message_or_warning).__name__
    msg = str(message_or_warning)
    cat = type(message_or_warning)
...
emit_from_catalog(
    entry,
    extra=merge_extra(self.meta, {**(extra or {}), "message": msg,
                                  "caller": caller or (extra or {}).get("caller")}),
    meta=self.meta,
)
```

The practical effect, observed in MolSysMT:

```python
warn(GpuNotAvailableWarning(reason='the taichi package is not installed'))
# emitted: "GPU acceleration was requested but is not available: {reason} (Hint: ...)"
```

`{reason}` renders literally. The instance interpolated it correctly for its own message, but the
catalog re-emission does not see it.

This forces every warning template to be written against `{message}` — that is, the emitting code
must pre-render the sentence and pass it as a string, which is precisely the "Zero String
Hardcoding" pattern the SMonitor guide forbids. The rule and the mechanism are in conflict.

The workaround downstream libraries end up using is to bypass the bundle entirely and call
`warnings.warn(MyWarning(reason=...))`, because the *instance* does hydrate correctly. That works
for the user-facing message but skips the SMonitor emission channel altogether, so the event never
reaches `report()`.

### 2. Structured context is lost to telemetry

Because `emit_from_catalog` receives only `{"message": <rendered string>, "caller": ...}`, the
structured fields never reach the event stream. `report()` sections that depend on them —
`events_by_code`, `events_by_fingerprint`, `most_noisy_resources` — see a rendered sentence where
they should see typed fields. For a diagnostics library this is the load-bearing loss: the data
was structured at the raise site and is downgraded to prose before it is recorded.

### 3. Caught exceptions cannot be inspected

The same discard happens in `CatalogException`. A caller that catches one gets no programmatic
handle on what happened:

```python
try:
    ...
except MultipleMolecularSystemsError as e:
    e.code    # AttributeError
    e.extra   # AttributeError
    dir(e)    # ['add_note', 'args', 'catalog_key', 'with_traceback']
```

Only `catalog_key` survives, and it survives because it is a class attribute, not because the
instance recorded anything. Downstream code that wants to branch on the error code, or read the
fields that caused it, has to parse the rendered English message.

---

## Proposed Solution

### 1. Retain `extra` and `code` on the instance

In both `CatalogWarning.__init__` and `CatalogException.__init__`, keep what was resolved:

```python
self.code = target_code
self.extra = merge_extra(meta, extra)
self.message = full_message
super().__init__(full_message)
```

Backward compatible: it only adds attributes.

### 2. Merge the instance's `extra` in `warn()`

When `warn()` is given a `CatalogWarning` instance, prefer the structured data it carries over the
rendered string:

```python
if isinstance(message_or_warning, Warning):
    cls_name = type(message_or_warning).__name__
    msg = str(message_or_warning)
    cat = type(message_or_warning)
    instance_extra = getattr(message_or_warning, 'extra', None) or {}
else:
    ...
    instance_extra = {}

emit_from_catalog(
    entry,
    extra=merge_extra(self.meta, {**instance_extra, **(extra or {}),
                                  "message": msg,
                                  "caller": caller or ...}),
    meta=self.meta,
)
```

With this, a template may use its own placeholders, the emitting code passes typed data rather
than a sentence, and the event stream records the fields.

### 3. Keep `{message}` working

Templates that already interpolate `{message}` keep working unchanged, because `message` is still
injected. The change is additive: it widens what a template may reference, it does not narrow it.

---

## Benefits

- **The guide becomes implementable.** "Pass raw data in `extra` and let SMonitor handle the
  interpolation" currently cannot be followed for warnings routed through `warn()`. After this it
  can.
- **Telemetry regains its fields.** Codes, fingerprints and resource counters see typed data
  instead of rendered prose.
- **Catch sites become programmable.** Downstream libraries can branch on `e.code` and read
  `e.extra` rather than pattern-matching English.
- **One emission path.** Libraries stop having to choose between `warnings.warn(Instance(...))`
  (correct message, no telemetry) and `warn(Instance(...))` (telemetry, broken message).

## Verification

A regression test should assert that a warning whose template uses a custom placeholder emits with
that placeholder interpolated, through `bundle.warn(Instance(...))` — not only through
`str(Instance(...))`.
