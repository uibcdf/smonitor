# Proposal: reduce `@signal` overhead on the enabled path

**Status:** pending — rewritten 2026-07-18 against the current code.
**Supersedes:** the original "Static Profile Opt-In and Production Performance
Optimization" draft. Its measured evidence is preserved below; its design
section is withdrawn, for the reasons in "What the original draft assumed".

## Abstract

The disabled-signal fast path proposed in the original draft is implemented and
measured. The remaining cost is on the *enabled* path, and it is larger than
the problem the draft set out to solve: a decorated call costs **~54× a bare
call even when it emits nothing**, and over half of that is a UTC timestamp
formatted on every call and discarded unless an event fires. This proposal is
narrow: make that timestamp lazy, and stop paying per call for work only
emission needs.

---

## Where things stand

### Implemented

The fast path is in place. `smonitor/core/decorator.py` consults the module-level
flag in `smonitor/core/runtime.py` before touching the manager, and
`Manager.configure(enabled=...)` keeps that flag synchronized.

Measured on this host (Python 3.13.12, x86_64, Linux 6.17), 1M calls via
`python benchmarks/signal_disabled.py`:

| call | ns |
|---|---:|
| bare function | 72.8 |
| `@signal`, SMonitor disabled | 241.5 |
| wrapper overhead | 168.7 |

That matches the ~175 ns the original draft recorded. **This part is done and
needs no further work.**

### What the original draft assumed

Two of its premises do not hold against the code:

1. **"Eliminate magic environment autodetection."** There is no autodetection.
   `PROFILE` resolves strictly through `configure()` > environment >
   `_smonitor.py` (`smonitor/config/__init__.py`). There is no heuristic to
   remove, so no silent regression of the kind described can occur.

2. **A `production`/`development`/`disabled` profile triad.** SMonitor already
   has five profiles with settled semantics — `user`, `dev`, `qa`, `agent`,
   `debug` — that select catalog message variants, output format, and strict
   validation. Adding a second, orthogonal profile axis would collide with all
   of them, and renaming the existing set is a breaking change to a public
   contract during the pre-1.0 freeze. "Disabled" is already expressed by
   `enabled=False`, which now drives the fast path.

The cross-library coordination idea (§3 of the draft — ArgDigest reading
`smonitor.PROFILE`) is deferred: it couples sibling libraries to an attribute
that does not exist, and the measurements below suggest it would not be where
the time goes anyway.

---

## The real remaining cost

Measured on the same host, 200k calls, handlers disabled, **no event emitted**:

| call | ns | vs bare |
|---|---:|---:|
| bare function | 79.2 | 1× |
| `@signal`, `enabled=False` | 248.4 | 3.1× |
| **`@signal`, `enabled=True`, default config** | **4 305.8** | **54×** |
| `@signal`, `enabled=True` + `args_summary` | 4 941.4 | 62× |
| `@signal`, `enabled=True` + `profiling` | 8 895.1 | 112× |

The enabled path is where scientific users actually run. Breaking it down:

| component | ns |
|---|---:|
| **`Frame(...)` construction** | **2 400.5** |
| — of which `datetime.now(timezone.utc).isoformat()` | **1 746.8** |
| `push_frame` + `pop_frame` | 715.1 |
| `_resolve_owner_module` | 134.6 |
| `get_manager()` | 54.1 |
| `random()` (profiling sample check) | 47.8 |
| `get_context(3)`, only on emission | 997.4 |

### The dominant cost is a discarded timestamp

`Frame.time` in `smonitor/core/context.py` is:

```python
time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

It is computed eagerly on **every decorated call**. It is read only when
`get_context()` serializes frames into an emitted event — that is, only when a
diagnostic actually fires. On a quiet hot path the string is formatted and
thrown away, and it is the single largest line item in the wrapper.

---

## Proposed change

### 1. Make the frame timestamp lazy (primary)

Store a cheap epoch float at push time and format ISO only when a frame is
serialized into an event:

```python
@dataclass
class Frame:
    ...
    _time: float = field(default_factory=time.time)

    @property
    def time(self) -> str:
        return datetime.fromtimestamp(self._time, timezone.utc).isoformat()
```

Prototyped and measured:

| | ns |
|---|---:|
| `Frame(...)` today (eager ISO) | 3 188.3 |
| `Frame(...)` with epoch float | **708.5** |
| materializing `.time` on demand | 1 859.9 |

A **4.5× cheaper frame**, with the ISO cost moved to emission, where it is paid
once per event instead of once per call. Wall-clock semantics are unchanged:
the timestamp still records when the frame was pushed, not when the event fired.

`Frame` is internal (`smonitor/core/context.py`); nothing outside SMonitor
constructs one. The exposure to check is `get_context()`, which serializes via
`frame.__dict__` — that would need to emit the rendered `time` rather than the
raw `_time`, so the event schema stays byte-identical. This is the one place
where the change is not purely mechanical, and it needs a test asserting the
event `context.frames[*].time` field is unchanged in shape.

### 2. Reduce per-call frame-stack copying (secondary)

`push_frame`/`pop_frame` cost 715 ns combined because each copies the whole
stack list (`list(_context_stack.get())`) to preserve `ContextVar` semantics.
That is O(depth) allocation twice per call. Worth investigating whether a
persistent immutable structure, or mutating a per-context list with explicit
copy-on-fork, preserves the async/thread isolation the current design buys.
Lower value than §1 and higher risk — treat as a separate slice, not part of
this one.

### 3. Not proposed

Static profile triads, import-time decorator elimination, and cross-library
profile coupling. Should §1 and §2 prove insufficient for the ecosystem targets
below, revisit with fresh measurements rather than reinstating the original
design.

---

## Verification

```bash
python benchmarks/signal_disabled.py   # disabled path must not regress
```

The benchmark only covers the disabled path. This proposal needs a companion
case for the enabled-but-quiet path, since that is what it targets. Acceptance:

- enabled/quiet decorated call drops from ~4 300 ns toward ~2 600 ns;
- disabled path unchanged (~240 ns);
- emitted events keep an identical `context.frames[*].time` field;
- full suite green.

---

## Ecosystem context (preserved from the original draft)

Measured 2026-07-12 from MolSysViewer. See
`molsysviewer/devguide/pending_proposals/import_cost_and_lazy_loading.md` and
`pyunitwizard/devguide/pending_proposals/python_overhead_before_rusterization.md`.

Measured on `puw.get_value(q, to_unit="nanometers")`, the hottest operation in
the ecosystem:

| | cost | % |
|---|---:|---:|
| real work (bare pint) | 17 µs | 7 % |
| decorator overhead, SMonitor **disabled** | 127 µs | 49 % |
| active telemetry | 118 µs | 45 % |
| **total** | **262 µs** | **15× pint** |

Profiling 300 calls to `puw.get_value` showed **4 800 SMonitor wrapper
invocations** — 16 per call, because PyUnitWizard also decorates its internal
helpers.

After the fast path landed, the integrated measurement with SMonitor disabled
was **137.9 µs** on that host. So the fast path removed the unnecessary manager
access but cannot on its own reach the 17 µs target: the intrinsic cost of
variadic wrappers, plus the DepDigest and PyUnitWizard work described in their
own proposals, remains. **The 16-wrappers-per-call figure suggests the largest
ecosystem win is fewer decorated functions on hot paths, not a cheaper
decorator** — that belongs in the sibling repos, not here.
