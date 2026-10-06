---
summary: Scoped capture avoids argument repr and native failure text before emission.
issue: uibcdf/smonitor#37
status: resolved
opened: 2026-10-06
closed: 2026-10-06
severity: high
verification: reproduced
area: [signal, context, integration, diagnostics]
guard: tests/test_capture_policy.py
normative: docs/content/user/library-integrators/scoped-capture.md
blocked_by: []
supersedes: []
---

# Scoped metadata-only capture

The original probes reproduced successful argument `repr`, native exception `str`
and inherited values under `args_summary=False`, and a fallback RuntimeWarning
promoted to an error replacing the active native failure. Detailed capture remains
the default; turning off normal summaries still permits the historical lazy error
summary.

The opt-in public contract is `CapturePolicy`, `METADATA_ONLY`,
`diagnostic_scope()`, `get_capture_policy()`, and
`emit(metadata_only=True, safe_extra=...)`. Policies and context state are immutable,
combined restrictively across nesting and restored with ContextVar tokens. Approved
facts are copied exact primitives with aggregate field/type/size limits; arbitrary
payloads are excluded before template rendering, fingerprints, summaries and delivery.
Known codes remain stable; unknown native failures use a fixed SMonitor catalog code.

`@signal(capture_policy=..., safe_extra=...)` applies to actual sync/async execution.
Preparation, failure emission and finalization are shared, retaining configuration
identity caching and the disabled fast path. Argument collection failures are
isolated from emission, incidentally protecting the mechanism in uibcdf/smonitor#36.
Profiling metadata, slow calls and diagnostic fallback warnings obey the scope.
Native object, cause, traceback and successful result take precedence over diagnostic
failure, including promoted RuntimeWarnings.

Deferred summaries retain policy and safe facts; aggregation separates capture
contexts while fingerprints keep their published semantics. Routing/filter selection
continues; transforms that could reintroduce unapproved payloads are skipped under
restricted capture. SMonitor-owned bridge formatting consults capture permissions.
Python/user/provider formatting that runs before SMonitor remains outside the contract.
Existing bundle snapshots and pre-scope events are not retroactively scrubbed.

The guard covers zero-call repr/str counters on success/error/profiling, native
identity/cause/traceback, safe catalog rendering, unsafe inherited frames, primitive
validation, nesting/restoration, asyncio interleaving, explicit thread propagation
and independent threaded calls, fallback failures, deferred summaries, transformations,
the full field budget, spans, observers/buffer/report/export and detailed compatibility.

Validation command: `python -m pytest --receptor=llm tests/test_capture_policy.py`
(35 passed on CPython 3.14.7). Full-suite validation passed on CPython 3.13.15
and 3.14.7. A locally built wheel passed installed contract smoke checks in
isolated, non-editable Python 3.11.11, 3.12.9, 3.13.15 and 3.14.7 environments:
provider registration preserves selected policy, explicit audience rendering is
pure, sync/async restrictive calls evaluate neither repr nor native str, and
events/reports/bundles retain no probe markers. These are local qualification
results, not claims of PyPI/Conda publication. Sphinx HTML compilation passed
after the normal catalog-generation step; a preliminary strict build exposed
pre-existing H2-first heading warnings in `docs/index.md`.

A microbenchmark against commit `677dc0f` measured
1.45 us/call before and 1.71 us/call after, minimum of five 100,000-call runs with an
enabled default signal, profiling/args disabled and a MemoryHandler. This is a local
cost measurement, not a platform-wide latency promise.

Ownership/adoption: uibcdf/argdigest#29 must replace its explicit `cause_message=str(e)`
paths and other provider-owned formatting with this shared policy. The SMonitor scope
cannot undo those calls. Central/consumer coordination remains linked through
uibcdf/molsyssuite#106, uibcdf/moli#62 and uibcdf/recorda#2/#14/#15. No consumer code,
quantity policy, Recorda-specific switch or provider release is included here.
