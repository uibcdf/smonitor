# Scoped observation

SMonitor 0.23.0 introduces explicit developer observation operations under
`smonitor.profiling`. Each operation returns its own bounded primitive report.
Select representative work and retain its original result and exit evidence.

## Selected synchronous calls

```python
from smonitor.profiling import observe_calls

# Existing function objects are supplied directly.
with observe_calls({"prepare": prepare, "calculate": calculate},
                   identity="callable", threads="current") as observation:
    result = calculate()
report = observation.report()
```

`observe_calls(targets, *, identity="code", threads="current", mode="timings",
tool_id=3, max_events=100000, max_threads=64, max_depth=128)` returns a single-use
context manager. Target labels are caller-approved ASCII identifiers of at most
64 characters. Supply at most 64 synchronous Python functions, bound methods,
code objects or `NativeCallTarget` selections. Generator/coroutine targets are
rejected. Enter after application setup and leave after the selected work.

The backend requires CPython 3.12–3.14 with the GIL enabled. Python 3.11 and other
unsupported interpreters raise catalog-backed `ObservationError` before entry.
The observer claims its explicitly selected unused `sys.monitoring` tool ID,
registers callbacks and removes its own local/global events and callbacks on
exit. Occupied slots raise `SMONITOR-OBSERVATION-CONFLICT`. Nested independent
scopes use different tool IDs, e.g. 3 and 4. The observer preserves application
profile/trace hooks, function/code identities and GC policy/callbacks.

Selection meanings are explicit:

- `identity="code"` aggregates every invocation sharing a selected code object,
  including unlisted closures/decorator wrappers. A code object receives one
  label. Distinct code objects are compared by identity.
- `identity="callable"` additionally observes Python CALL events to match the
  selected function and, for bound methods, its receiver identity. Unlisted
  aliases sharing that code remain excluded. Entries without an attributable
  Python CALL, such as some C-initiated callbacks, are counted as unattributed
  and make the observation incomplete.
- `threads="current"` restricts delivery to the entering thread.
  `threads="all"` includes current and future Python threads in this interpreter.
  Per-thread stacks keep recursive and nested selected calls independent.
- `mode="counts"` records calls, returns and exception unwinds without selected
  timing clocks, whose fields remain `None`. `mode="timings"` also reports inclusive and selected-exclusive
  wall nanoseconds and thread CPU nanoseconds. Selected-exclusive subtracts
  nested selected work on that same thread. Unselected nested work remains in
  its enclosing selected duration. Inclusive nested durations overlap.

`scope_process_cpu_ns` is measured once for the whole scope. It includes all
process threads and observer overhead. Thread CPU covers the Python thread
receiving each event. CPU spent in other native threads needs a process/resource
observation. Scope wall and all selected clocks include instrumentation and
scheduling costs.

GC collection/collected/uncollectable counters are process-wide before/after
snapshots. `gc_elapsed_ns` is unavailable (`None`) because the supported elapsed
callback route would change an application's callback admission. Observation
allocations can themselves affect collection counts.

For a precise supported native call:

```python
from smonitor.profiling import NativeCallTarget, observe_calls

selection = NativeCallTarget(caller=consume, function=list.pop, receiver=items)
with observe_calls({"pop": selection}) as observation:
    consume(items)
```

`caller` selects its Python code identity. `function` accepts a builtin function,
a method descriptor, or a bound builtin with a resolvable descriptor. Optional
receiver matching uses object identity. Returns and native raises have distinct
counts. Other native callable implementations require their own supported
monitoring contract. The report declares native caller code aggregation even
when Python targets use callable identity.

Reports use `smonitor.call-observation@1` and contain approved labels, thread
identifiers, counts, clocks, GC counter deltas and completeness counters.
Argument/return/receiver/frame payloads and exception text are excluded. Selection
references are released when the scope closes. Events, threads and stack depth
are bounded, with an additional 65536-frame product limit. Dropped entries,
unmatched exits, callback failures, unattributed entries and open calls at stop
produce `status="incomplete"`. Closing preserves the original body exception.
Read the report after context exit. Reusing a scope is rejected.

The interpreter event and callback contracts are documented in
[Python's monitoring reference](https://docs.python.org/3.14/library/sys.monitoring.html).
GC snapshot and callback semantics follow the
[GC reference](https://docs.python.org/3.14/library/gc.html).

## Linux process-family samples

```python
from smonitor.profiling import observe_process_family

# The application starts an owned calculation process behind a work barrier.
with observe_process_family(process.pid, interval_s=0.1) as observation:
    release_calculation()
    result = receive_result()
report = observation.report()
returncode = process.wait()
```

`observe_process_family(pid, *, interval_s=0.1, max_samples=1000,
max_processes=64, max_tasks=1024, max_duration_s=300, include_host=False)` supports
Linux `/proc`. The root must be an existing descendant of the calling process.
Its PID/start ticks are verified before observation. The worker is a sibling of
the calculation subtree. A readiness handshake follows its initial sample, so
the caller can then release a work barrier. Startup time is outside that sample
window. The caller keeps its process handle, wait/return-code handling and
scientific result. The observer closes on normal exit, body exceptions, bounds,
duration or parent EOF. Cleanup targets only its own worker and temporary files.

The worker discovers children through every live task's `children` file,
deduplicates PIDs, verifies start ticks, and retains already discovered
identities across reparenting/root disappearance. Reused PIDs and newly found
children with a changed parent are rejected with retained errors. At most
`max_processes` distinct process identities are retained for the whole scope.
Task discovery is bounded per sample. The sample/process product is limited to
100000 records. Error history retains at most 128 entries per sample and 4096
in total; previous-success history is also limited to 4096 keys. Omissions are
reported explicitly and make coverage incomplete.

Each `smonitor.process-family-observation@1` report retains sample/read start and
end monotonic nanoseconds, PID/start ticks, CPU tick counters, RSS and PSS bytes,
read errors and previous successful operation timestamps. Failed/unverified
memory reads remain `None`. Error categories preserve uncertainty about process
exit, reaping, permissions and discovery races. `family_pss_bytes` requires all
reads/discovery in that sample to succeed. `observed_pss_bytes` retains the
available subset when coverage is partial. `maximum_sampled_family_pss_bytes`
uses qualifying samples only. Continuous coverage, atomic family samples and a
true instantaneous peak remain unavailable. Short-lived undiscovered children
and peaks between samples can be missed even with zero read errors.

Requested wait is **additional to read time**. Actual sample/read windows and
`observer_cpu_ns` expose effective cadence and sampler overhead.
`observer_startup_wall_ns` covers launch-to-readiness, and
`observer_process_cpu_ns` retains total observer-process CPU including startup. Sample and
duration limits stop observation with incomplete status. Duration is checked
between reads. Choose cadence and limits for the workload's peak duration and
retain separate unobserved latency/CPU cohorts when measuring performance.

RSS sums can count shared mappings more than once. PSS and RSS describe process
mappings; device memory requires a separate backend.

CPU counters are per process. `self_cpu_ticks` includes that process's threads;
`waited_children_cpu_ticks` contains its reaped children. Deltas span the first
to last successful observation of each discovered identity, with
`cpu_ticks_per_second` specifying clock quantization. Short lifetimes and work
before discovery can be missed. Root, joined-child and observed-descendant data
are retained individually. Summing descendant lifetime deltas with joined-child
counters can double-count the same work after reaping. The application can retain
its independent `wait`/rusage evidence for a complete owned execution.

## Capacity and pressure snapshots

`linux_resource_snapshot(pid)` exposes effective affinity CPU IDs, raw host
CPU/memory/I/O PSI, available RAM/swap bytes and visible cgroup-v2 ancestor
`cpu.max`, `cpu.stat`, `memory.max` and `memory.high` contents. `include_host=True`
adds one such initial snapshot to a process-family report. Values and read errors
are separate fields, with before/after process identity verification. Cgroup
inspection covers at most 64 ancestors under the visible `/sys/fs/cgroup` mount.
Unavailable or inaccessible controls retain incomplete status. The execution
owner interprets demand, quotas, pressure and admission using its own policy.

The backend's stat, RSS, PSS and task interfaces follow the
[Linux proc filesystem reference](https://docs.kernel.org/filesystems/proc.html).
