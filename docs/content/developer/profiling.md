# Profiling

When `profiling=True`, SMonitor records durations per decorated frame and aggregates timing stats in `report()`.

## Decorator-based timing

```python
import smonitor

smonitor.configure(profiling=True)

@smonitor.signal
def work():
    return 1
```

## Manual spans

```python
from smonitor.profiling import span

with span("data_loading", source="database"):
    pass
```

## Sampling and buffer

```python
smonitor.configure(
    profiling=True,
    profiling_sample_rate=0.1,
    profiling_buffer_size=200,
)
```

## Export timeline

```python
from smonitor.profiling import export_timeline

export_timeline("timeline.json", format="json")
```

## Scoped observation

SMonitor 0.23.0 adds selected-call observation and Linux process-family samples.
The [observation contract](observation.md) describes identity, threads, clocks,
coverage bounds and resource ownership.
