# Profiling in Your Library

SMonitor includes lightweight profiling for diagnostics-oriented performance
analysis. It is not a replacement for full profilers, but it is excellent for:
- comparing call-path costs,
- identifying slow orchestration boundaries,
- exporting timing evidence for QA/support.

## 1. Enable profiling

```python
import smonitor

smonitor.configure(
    profiling=True,
    profiling_sample_rate=0.2,
    profiling_buffer_size=500,
)
```

## 2. Use `@signal` timings

Decorated functions automatically contribute timing data:

```python
import smonitor

@smonitor.signal(tags=["analysis"])
def run_workflow(data):
    ...
```

Inspect summary:

```python
report = smonitor.report()
print(report["timings"])
print(report["timings_by_module"])
```

## 3. Add manual spans for critical blocks

```python
from smonitor.profiling import span

def run_workflow():
    with span("io.load", source="dataset"):
        ...
    with span("compute.optimize", backend="cpu"):
        ...
```

## 4. Export timeline

```python
from smonitor.profiling import export_timeline

export_timeline("timeline.json", format="json")
export_timeline("timeline.csv", format="csv")
```

## 5. Optional hardware hooks (GPU/accelerators)

You can attach `profiling_hooks` (list of callables) that return dictionaries
with metadata (for example, GPU memory or device name). These fields appear in
`report()["profiling_meta"]`.

## Recommendation

- enable profiling in `dev`/`qa`, not in default user workflows,
- use sampling (`profiling_sample_rate`) in large workloads,
- instrument boundaries, not tight inner loops.

## You are done when

- timing summaries are visible in `report()`,
- timeline export works in JSON/CSV,
- profiling helps triage real slow paths in your library.
