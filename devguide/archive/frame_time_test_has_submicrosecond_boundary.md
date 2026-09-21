---
summary: Avoid a one-microsecond false failure in the frame-time test
issue: uibcdf/smonitor#18
status: resolved
opened: 2026-09-21
closed: 2026-09-21
severity: medium
verification: reproduced
area: [testing, time, ci]
guard: tests/test_core.py::test_frame_time_bound_allows_only_one_microsecond_quantization
normative:
blocked_by: []
supersedes: []
---

# The frame-time test has a submicrosecond boundary

**Reported:** 2026-09-21 from the Windows Python 3.12 job in the hosted SMonitor
Python 3.14 candidate matrix, run `35580019186` (`uibcdf/smonitor#17`).

## What

`tests/test_core.py::test_frame_time_is_iso_utc_in_emitted_context` failed although
the parsed frame timestamp differed from the upper bound by only one microsecond:

```text
parsed = 2026-09-21 08:51:31.766422+00:00
after  = 2026-09-21 08:51:31.766421+00:00
assert before <= parsed <= after
```

Eleven of the twelve matrix cells passed; this was the only failing assertion in the
Windows Python 3.12 cell. The installed-package and interpreter steps had already passed.

## How

SMonitor stores a breadcrumb frame time as a float epoch from `time.time()` and renders
it using `datetime.fromtimestamp(..., timezone.utc)`. The test bounds the call with
`datetime.now(timezone.utc)`. Float-to-microsecond quantization can put the rendered
timestamp one microsecond outside the test's independently sampled bounds. The strict
comparison therefore checks a precision agreement the representations do not promise,
not the intended ISO/UTC and near-call-time behavior.

The proposed repair allows exactly one microsecond of quantization at either bound.
A deterministic helper test accepts a one-microsecond discrepancy and rejects two
microseconds, so the relaxation cannot silently grow into a broad timing window.
The original runtime test still verifies timezone-aware ISO output and all frame keys.

## Why

One imprecise test can block a twelve-cell release gate and misclassify the failure as
Windows or Python 3.14 incompatibility. The producer's timestamp contract is not being
changed, and its hot-path storage remains a float epoch.

## What was refuted

- The failure is not caused by a missing dependency or package install: the job reached
  `Run tests` and failed only this timestamp assertion.
- Changing the stored frame timestamp to an eagerly formatted datetime would affect a
  measured hot path to satisfy a test precision assumption; the public value is already
  valid ISO-8601 UTC.
- A large wall-clock tolerance is unnecessary; the observed and derived representation
  discrepancy is one microsecond.

## Acceptance criteria

- The deterministic bound test accepts a one-microsecond discrepancy on either side and
  rejects two microseconds.
- The original frame-time test still checks ISO, UTC, near-call timing and frame shape.
- Ruff and the complete local suites pass on Python 3.13 and 3.14.
- A new exact-commit hosted matrix no longer has this false failure.

## Resolution

Commit `a30438d` bounds the independently sampled frame time by exactly one
microsecond at either end. The guard
`tests/test_core.py::test_frame_time_bound_allows_only_one_microsecond_quantization`
accepts a one-microsecond representation discrepancy and rejects two; the runtime
test continues to check ISO/UTC, frame shape, and near-call timing.

On the final candidate SHA `1e48f7d9b7308adb85e5d763d7e26c5da25101cd`, hosted
matrix run `35585349618` passed all twelve Linux, macOS, and Windows cells on Python
3.11--3.14, including the formerly failing Windows Python 3.12 cell. Locally, the
complete suite passed on Python 3.13 and 3.14 with twelve workers (469 passed,
3 skipped on each); Ruff lint and format checks passed.
