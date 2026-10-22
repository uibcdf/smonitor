# Pytest diagnostic policy

Pytest Receptor owns the pytest result and the canonical JSONL artifact. SMonitor
adds bounded diagnostic extension records. `smonitor pytest-check` is an
**optional, separate QA gate** over a completed artifact; it does not modify
pytest's result, install a reporter, or upload evidence.

Install `smonitor[pytest]`, create the artifact directory, then run pytest:

```bash
mkdir -p .pytest-receptor
python -m pytest --receptor=ci --receptor-events=.pytest-receptor/events.jsonl
smonitor pytest-check .pytest-receptor/events.jsonl \
  --provider-root ./my_library \
  --forbid-code MYLIB-DEPRECATED-001
```

`--provider-root` is a trusted package directory containing `_smonitor.py`.
SMonitor validates its `CODES` and `SIGNALS` declarations with the same
validator used for provider registration, and checks that emitted codes are
declared there. The configuration file is Python code, so inspect untrusted
repositories before loading it. The check does not claim to validate every
runtime template substitution; test each catalog-backed diagnostic with its
representative structured fields.

The command prints a versioned JSON result. Exit status is `0` when policy
passes, `1` for policy violations, and `2` for unreadable artifacts, invalid
rules, or missing optional dependencies. `pytest_outcome` is reported separately:
CI must still check pytest's own exit status. The policy never changes it.

## Accepted identity baseline

After reviewing a representative passing run, create a baseline once:

```bash
smonitor pytest-baseline .pytest-receptor/events.jsonl \
  --out tests/accepted_diagnostics.json
```

Then compare later runs, including xdist runs:

```bash
smonitor pytest-check .pytest-receptor/events.jsonl \
  --baseline tests/accepted_diagnostics.json \
  --provider-root ./my_library
```

The baseline is a sorted set of `(code, source, fingerprint)` for SMonitor
warning, error, and critical records. New identities fail the gate; disappeared
ones are reported for review. Repeated occurrences, worker IDs, test nodes and
phase assignments do not affect it. This is important when worker-local caches
change warning counts under xdist. Baselines cannot be created from a failed,
partial, truncated, or extension-incomplete run. Empty baselines require
`--allow-empty`; they give no proof that the SMonitor plugin was active.

SMonitor's fingerprint also includes selected structured fields such as
`caller`, `resource`, and `retry_attempt`. A baseline is reproducible only when
those fields are stable for the covered workflow. Review a representative run
before accepting it, and use code-level forbidden rules for a diagnostic whose
resource or retry context legitimately varies.

Use `--require-diagnostics` on `pytest-check` when a smoke test must emit at
least one SMonitor record. Without that explicit witness, an artifact containing
zero diagnostics cannot distinguish a clean run from a missing producer.

An artifact with invalid integrity, incomplete execution, truncated evidence,
or dropped/incomplete extensions fails the gate because missing records cannot
prove a forbidden identity was absent. The receptor's `read_artifact` validates
its digest before policy evaluation. The policy uses only `uibcdf.smonitor@1`
records with the `smonitor.pytest-event@1` schema; other producers are ignored.

## Test assertions and support bundles

Use `pytest.warns`, `pytest.raises`, and SMonitor's existing structured tests
for assertions inside individual tests. The receptor already associates
extensions with the node, phase, worker and attempt. A new SMonitor fixture or
marker would duplicate those contracts, so this policy adds neither.

The standalone SMonitor support bundle is optional and has different retention
and redaction settings from the receptor artifact. Do not insert it into the
canonical JSONL stream or infer that the two files cover the same history. If a
workflow publishes both, its link manifest must name each relative artifact,
record a SHA-256 for each complete file, identify the receptor schema and the
SMonitor bundle profile/schema, state receptor integrity and execution
completeness, and state the bundle's redaction and coverage limits. The rich
bundle currently has no versioned schema or guaranteed complete history; a
generic automatic link would overstate its reliability. SMonitor therefore does
not publish one until a consumer demonstrates a concrete paired-bundle workflow.
