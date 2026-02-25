# Profile Decision Matrix

Use this matrix to choose the right SMonitor profile and options for each stage
of your library lifecycle.

| Stage | Recommended profile | Typical options | Why |
|---|---|---|---|
| Local user-facing demos | `user` | `level="WARNING"`, `theme="plain"` | Keep output clear and calm. |
| Feature development | `dev` | `level="INFO"`, `args_summary=True` | More context while iterating quickly. |
| QA validation | `qa` | `strict_signals=True`, `strict_schema=True` | Catch contract and schema drift early. |
| Debugging incidents | `debug` | `level="DEBUG"`, `show_traceback=True` | Maximum diagnostic depth. |
| Agent/automation parsing | `agent` | structured outputs, minimal noise | Deterministic machine consumption. |
| Performance triage | `dev` or `qa` | `profiling=True`, `profiling_sample_rate=0.1` | Compare slow boundaries with low overhead. |

## Quick rules

1. Default to `user` in production-facing runtime.
2. Use `dev` for day-to-day coding.
3. Reserve `qa` strict modes for CI and release gates.
4. Enable `debug` only when diagnosing incidents.
5. Keep profiling off by default for normal user workflows.

## Runtime examples

```python
import smonitor

# Development
smonitor.configure(profile="dev", level="INFO", args_summary=True)

# QA gate
smonitor.configure(profile="qa", strict_signals=True, strict_schema=True)

# Profiling pass
smonitor.configure(profile="dev", profiling=True, profiling_sample_rate=0.2)
```

## You are done when

- each environment (dev/qa/prod) has an explicit profile policy,
- CI enforces strict modes in QA jobs,
- user-facing runtime remains simple and actionable.
