"""Linux process observation backend and finite sibling-worker entry point."""

from __future__ import annotations

import json
import math
import os
import select
import subprocess
import sys
import tempfile
import time
from collections import deque
from pathlib import Path

from ._diagnostics import ObservationError

_PROC = Path("/proc")
_MAX_REPORT_BYTES = 64 * 1024 * 1024


def _linux():
    if not sys.platform.startswith("linux") or not _PROC.is_dir():
        raise ObservationError("SMONITOR-OBSERVATION-UNSUPPORTED")


def _read(path, limit=65536):
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError
    return raw.decode("utf-8", errors="surrogateescape")


def _stat(pid):
    raw = _read(_PROC / str(pid) / "stat")
    # comm may contain spaces and parentheses. No command/name is retained.
    values = raw[raw.rfind(")") + 2 :].split()
    return {
        "pid": pid,
        "start_ticks": int(values[19]),
        "ppid": int(values[1]),
        "state": values[0],
        "self_cpu_ticks": int(values[11]) + int(values[12]),
        "waited_children_cpu_ticks": int(values[13]) + int(values[14]),
        "threads": int(values[17]),
        "rss_bytes": int(values[21]) * os.sysconf("SC_PAGE_SIZE"),
    }


def _category(error):
    if isinstance(error, PermissionError):
        return "permission_denied"
    if isinstance(error, ProcessLookupError):
        return "process_lookup"
    if isinstance(error, FileNotFoundError):
        return "not_found_or_exited"
    return (
        "invalid_read" if isinstance(error, (ValueError, IndexError, StopIteration)) else "os_error"
    )


def _require_owned_descendant(root):
    current = root
    for _ in range(1024):
        if current["pid"] == os.getpid() or current["ppid"] <= 0:
            break
        if current["ppid"] == os.getpid():
            return
        current = _stat(current["ppid"])
    raise ObservationError("SMONITOR-OBSERVATION-CONFLICT", extra={"operation": "family_scope"})


def linux_resource_snapshot(pid: int) -> dict:
    """Read process affinity, visible cgroup-v2 controls, host memory and PSI.

    Capacity, pressure and quota facts are returned separately. Ancestors are
    limited to the visible cgroup mount; no reservation or admission is implied.
    """
    _linux()
    if type(pid) is not int or pid <= 0:
        raise ObservationError("SMONITOR-OBSERVATION-INVALID", extra={"field": "pid"})
    start = time.monotonic_ns()
    errors = []

    def read(operation, function):
        try:
            return function()
        except (OSError, ValueError, IndexError) as error:
            errors.append({"operation": operation, "category": _category(error)})
            return None

    identity = read("stat", lambda: _stat(pid))
    affinity = read("affinity", lambda: sorted(os.sched_getaffinity(pid)))
    memory = read(
        "meminfo",
        lambda: {
            line.split(":")[0]: int(line.split()[1]) * 1024
            for line in _read(_PROC / "meminfo").splitlines()
            if line.split(":")[0] in ("MemAvailable", "SwapFree", "SwapTotal")
        },
    )
    pressure = {
        kind: read(f"pressure_{kind}", lambda kind=kind: _read(_PROC / "pressure" / kind, 4096))
        for kind in ("cpu", "memory", "io")
    }
    cgroups = read("cgroup_membership", lambda: _read(_PROC / str(pid) / "cgroup"))
    ancestors = []
    if cgroups is not None:
        membership = next(
            (line[3:] for line in cgroups.splitlines() if line.startswith("0::")), None
        )
        if membership is not None and ".." not in Path(membership).parts:
            mount = Path("/sys/fs/cgroup")
            current = mount / membership.lstrip("/")
            for depth in range(64):
                controls = {
                    name: read(
                        f"cgroup_{depth}_{name}",
                        lambda name=name, current=current: _read(current / name, 4096),
                    )
                    for name in ("cpu.max", "cpu.stat", "memory.max", "memory.high")
                }
                ancestors.append({"visible_ancestor": depth, "controls": controls})
                if current == mount:
                    break
                current = current.parent
            else:
                errors.append({"operation": "cgroup_ancestors", "category": "limit"})
        else:
            errors.append({"operation": "cgroup_v2", "category": "unavailable"})
    after = read("stat_after", lambda: _stat(pid))
    verified = (
        identity is not None
        and after is not None
        and identity["start_ticks"] == after["start_ticks"]
    )
    if not verified:
        errors.append({"operation": "identity", "category": "unverified"})
    return {
        "schema": "smonitor.linux-resources@1",
        "pid": pid,
        "start_ticks": identity["start_ticks"] if identity else None,
        "identity_verified": verified,
        "start_ns": start,
        "end_ns": time.monotonic_ns(),
        "affinity_cpus": affinity,
        "host_memory_bytes": memory,
        "host_pressure_raw": pressure,
        "visible_cgroup_v2_ancestors": ancestors,
        "errors": errors,
        "status": "incomplete" if errors else "observed",
    }


class _FamilySampler:
    def __init__(self, config):
        self.config = config
        self.root = config["pid"]
        self.known = {self.root: config["start_ticks"]}
        self.last_success = {}
        self.first_cpu = {}
        self.last_cpu = {}
        self.errors_total = self.omitted_errors = self.discovery_limits = 0
        self.success_history_omitted = 0
        self.samples = []
        self.ticks_per_second = os.sysconf("SC_CLK_TCK")

    def _remember(self, pid, operation, tid=None):
        key = (pid, operation, tid)
        if key not in self.last_success and len(self.last_success) >= 4096:
            self.last_success.pop(next(iter(self.last_success)))
            self.success_history_omitted += 1
        self.last_success[key] = time.monotonic_ns()

    def _error(self, sample, pid, operation, category, *, tid=None):
        self.errors_total += 1
        sample["read_failures"] += 1
        entry = {
            "pid": pid,
            "start_ticks": self.known.get(pid),
            "tid": tid,
            "operation": operation,
            "category": category,
            "time_ns": time.monotonic_ns(),
            "last_success_ns": self.last_success.get((pid, operation, tid)),
        }
        if len(sample["errors"]) < 128 and self.errors_total - self.omitted_errors <= 4096:
            sample["errors"].append(entry)
        else:
            self.omitted_errors += 1
            sample["errors_omitted"] += 1

    def _children(self, pid, sample):
        children = set()
        try:
            with os.scandir(_PROC / str(pid) / "task") as tasks:
                for number, task in enumerate(tasks):
                    if number >= self.config["max_tasks"]:
                        self.discovery_limits += 1
                        self._error(sample, pid, "task_discovery", "limit")
                        break
                    if not task.name.isdecimal():
                        continue
                    try:
                        raw = _read(Path(task.path) / "children")
                        for value in raw.split():
                            children.add(int(value))
                            if len(children) > self.config["max_processes"]:
                                self.discovery_limits += 1
                                self._error(sample, pid, "child_discovery", "limit")
                                return set(sorted(children)[: self.config["max_processes"]])
                        self._remember(pid, "task_children", int(task.name))
                    except (OSError, ValueError) as error:
                        self._error(
                            sample, pid, "task_children", _category(error), tid=int(task.name)
                        )
                else:
                    self._remember(pid, "task_discovery")
        except OSError as error:
            self._error(sample, pid, "task_discovery", _category(error))
        return children

    def sample(self):
        sample = {
            "start_ns": time.monotonic_ns(),
            "processes": [],
            "errors": [],
            "read_failures": 0,
            "errors_omitted": 0,
        }
        pending = deque((pid, None) for pid in self.known)
        queued = set(self.known)
        while pending:
            pid, parent = pending.popleft()
            read_start = time.monotonic_ns()
            try:
                before = _stat(pid)
            except (OSError, ValueError, IndexError) as error:
                self._error(sample, pid, "stat", _category(error))
                continue
            expected = self.known.get(pid)
            if expected is not None and before["start_ticks"] != expected:
                self._error(sample, pid, "identity", "pid_reused")
                continue
            if expected is None and before["ppid"] != parent:
                self._error(sample, pid, "discovery_parent", "parent_changed")
                continue
            self.known[pid] = before["start_ticks"]
            self._remember(pid, "stat")
            self._remember(pid, "identity")
            row = {
                **before,
                "read_start_ns": read_start,
                "pss_bytes": None,
                "identity_verified": False,
            }
            try:
                memory = _read(_PROC / str(pid) / "smaps_rollup")
                pss = next(line for line in memory.splitlines() if line.startswith("Pss:"))
                parts = pss.split()
                if parts[2] != "kB" or int(parts[1]) < 0:
                    raise ValueError
                row["pss_bytes"] = int(parts[1]) * 1024
            except (OSError, ValueError, IndexError, StopIteration) as error:
                self._error(sample, pid, "smaps_rollup", _category(error))
            children = self._children(pid, sample)
            try:
                after = _stat(pid)
                row["identity_verified"] = after["start_ticks"] == before["start_ticks"]
                if not row["identity_verified"]:
                    self._error(sample, pid, "identity_after", "pid_reused")
                else:
                    self._remember(pid, "stat_after")
            except (OSError, ValueError, IndexError) as error:
                self._error(sample, pid, "stat_after", _category(error))
            if not row["identity_verified"]:
                row["pss_bytes"] = None
                children.clear()
            elif row["pss_bytes"] is not None:
                self._remember(pid, "smaps_rollup")
            self.first_cpu.setdefault(
                pid, (before["self_cpu_ticks"], before["waited_children_cpu_ticks"])
            )
            self.last_cpu[pid] = (before["self_cpu_ticks"], before["waited_children_cpu_ticks"])
            row["read_end_ns"] = time.monotonic_ns()
            sample["processes"].append(row)
            for child in sorted(children):
                if child in queued:
                    continue
                if len(queued) >= self.config["max_processes"]:
                    self.discovery_limits += 1
                    self._error(sample, child, "process_discovery", "limit")
                    break
                queued.add(child)
                pending.append((child, pid))
        values = [row["pss_bytes"] for row in sample["processes"]]
        sample["observed_pss_bytes"] = (
            sum(v for v in values if v is not None) if any(v is not None for v in values) else None
        )
        sample["family_pss_bytes"] = (
            sum(values)
            if values and all(v is not None for v in values) and not sample["read_failures"]
            else None
        )
        sample["observed_rss_bytes"] = (
            sum(row["rss_bytes"] for row in sample["processes"]) if sample["processes"] else None
        )
        sample["end_ns"] = time.monotonic_ns()
        self.samples.append(sample)

    def report(self):
        cpu = [
            {
                "pid": pid,
                "start_ticks": self.known[pid],
                "observed_self_cpu_ticks_delta": self.last_cpu[pid][0] - initial[0],
                "observed_waited_children_cpu_ticks_delta": self.last_cpu[pid][1] - initial[1],
            }
            for pid, initial in self.first_cpu.items()
        ]
        peaks = [s["family_pss_bytes"] for s in self.samples if s["family_pss_bytes"] is not None]
        return {
            "schema": "smonitor.process-family-observation@1",
            "backend": "linux.proc",
            "root_pid": self.root,
            "root_start_ticks": self.config["start_ticks"],
            "observer_pid": os.getpid(),
            "requested_wait_s": self.config["interval_s"],
            "status": "incomplete"
            if self.errors_total or self.discovery_limits or self.success_history_omitted
            else "observed",
            "continuous_coverage": False,
            "atomic_family_sample": False,
            "true_peak_pss_bytes": None,
            "maximum_sampled_family_pss_bytes": max(peaks) if peaks else None,
            "read_failures": self.errors_total,
            "errors_omitted": self.omitted_errors,
            "success_history_omitted": self.success_history_omitted,
            "discovery_limits": self.discovery_limits,
            "cpu_ticks_per_second": self.ticks_per_second,
            "process_cpu_deltas": cpu,
            "samples": self.samples,
        }


class ProcessFamilyObservation:
    """A finite sibling observer for a descendant calculation owned by the caller."""

    def __init__(
        self,
        pid,
        *,
        interval_s=0.1,
        max_samples=1000,
        max_processes=64,
        max_tasks=1024,
        max_duration_s=300,
        include_host=False,
    ):
        for field, value, maximum in (
            ("pid", pid, 2**31 - 1),
            ("max_samples", max_samples, 10000),
            ("max_processes", max_processes, 4096),
            ("max_tasks", max_tasks, 16384),
        ):
            if type(value) is not int or not 1 <= value <= maximum:
                raise ObservationError("SMONITOR-OBSERVATION-INVALID", extra={"field": field})
        if max_samples * max_processes > 100_000 or type(include_host) is not bool:
            raise ObservationError("SMONITOR-OBSERVATION-INVALID", extra={"field": "sample_budget"})
        for field, value, minimum, maximum in (
            ("interval_s", interval_s, 0.001, 60),
            ("max_duration_s", max_duration_s, 0.001, 86400),
        ):
            if (
                type(value) not in (int, float)
                or not math.isfinite(value)
                or not minimum <= value <= maximum
            ):
                raise ObservationError("SMONITOR-OBSERVATION-INVALID", extra={"field": field})
        self._config = dict(
            pid=pid,
            interval_s=interval_s,
            max_samples=max_samples,
            max_processes=max_processes,
            max_tasks=max_tasks,
            max_duration_s=max_duration_s,
            include_host=include_host,
        )
        self._worker = self._temporary = self._report = None

    def __enter__(self):
        _linux()
        if self._worker is not None or self._report is not None:
            raise ObservationError(
                "SMONITOR-OBSERVATION-INVALID", extra={"field": "single_use_scope"}
            )
        try:
            initial = _stat(self._config["pid"])
            _require_owned_descendant(initial)
        except (OSError, ValueError, IndexError) as error:
            if isinstance(error, ObservationError):
                raise
            raise ObservationError(
                "SMONITOR-OBSERVATION-IO", extra={"operation": "root_identity"}
            ) from None
        self._config["start_ticks"] = initial["start_ticks"]
        self._temporary = tempfile.TemporaryDirectory(prefix="smonitor-family-")
        self._config["report_path"] = str(Path(self._temporary.name) / "report.json")
        startup = time.monotonic_ns()
        try:
            self._worker = subprocess.Popen(
                [sys.executable, "-m", "smonitor._process_observation"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                encoding="utf-8",
            )
            self._worker.stdin.write(json.dumps(self._config) + "\n")
            self._worker.stdin.flush()
            if not select.select([self._worker.stdout], [], [], 10)[0]:
                raise TimeoutError
            ready = json.loads(self._worker.stdout.readline())
            if ready != {"ready": True, "pid": self._worker.pid}:
                raise ValueError
            self._startup_wall_ns = time.monotonic_ns() - startup
        except BaseException as error:
            self.stop()
            if not isinstance(error, Exception):
                raise
            raise ObservationError(
                "SMONITOR-OBSERVATION-IO", extra={"operation": "observer_start"}
            ) from None
        return self

    def stop(self):
        if self._report is not None:
            return
        worker = self._worker
        result = {
            "schema": "smonitor.process-family-observation@1",
            "status": "incomplete",
            "observer_failure": "no_report",
            "samples": [],
        }
        try:
            if worker is not None:
                try:
                    worker.communicate(input="stop\n", timeout=10)
                except (BrokenPipeError, subprocess.TimeoutExpired):
                    worker.terminate()
                    try:
                        worker.communicate(timeout=3)
                    except subprocess.TimeoutExpired:
                        worker.kill()
                        worker.communicate(timeout=3)
                path = Path(self._config["report_path"])
                if path.is_file():
                    with path.open("rb") as stream:
                        raw = stream.read(_MAX_REPORT_BYTES + 1)
                    if len(raw) <= _MAX_REPORT_BYTES:
                        parsed = json.loads(raw)
                        if isinstance(parsed, dict) and parsed.get("schema") == result["schema"]:
                            result = parsed
                result["observer_exit_code"] = worker.returncode
                result["observer_startup_wall_ns"] = getattr(self, "_startup_wall_ns", None)
                if worker.returncode != 0:
                    result["status"] = "incomplete"
                    result["observer_failure"] = "worker_exit"
        except (OSError, ValueError, subprocess.TimeoutExpired):
            result["status"] = "incomplete"
            result["observer_failure"] = "report_or_cleanup"
        finally:
            self._report = result
            if self._temporary is not None:
                try:
                    self._temporary.cleanup()
                except OSError:
                    self._report["status"] = "incomplete"
                    self._report["observer_failure"] = "temporary_cleanup"

    def __exit__(self, *exc):
        self.stop()
        return False

    def report(self):
        from copy import deepcopy

        if self._report is None:
            raise ObservationError(
                "SMONITOR-OBSERVATION-INVALID", extra={"field": "report_requires_closed_scope"}
            )
        return deepcopy(self._report)


def observe_process_family(pid: int, **options) -> ProcessFamilyObservation:
    """Sample a caller-owned descendant from a separate sibling process.

    Enter after creating the calculation process and before releasing its work
    barrier. The application keeps its Popen/wait/exit and execution policy.
    """
    return ProcessFamilyObservation(pid, **options)


def _worker_main():
    config = json.loads(sys.stdin.readline())
    sampler = _FamilySampler(config)
    wall, cpu = time.monotonic_ns(), time.process_time_ns()
    host = linux_resource_snapshot(config["pid"]) if config["include_host"] else None
    reason = "sample_limit"
    try:
        sampler.sample()
        print(json.dumps({"ready": True, "pid": os.getpid()}), flush=True)
        while len(sampler.samples) < config["max_samples"]:
            if (time.monotonic_ns() - wall) / 1e9 >= config["max_duration_s"]:
                reason = "duration_limit"
                break
            remaining = config["max_duration_s"] - (time.monotonic_ns() - wall) / 1e9
            if select.select([sys.stdin], [], [], min(config["interval_s"], max(0, remaining)))[0]:
                sys.stdin.readline()
                reason = "caller_stop_or_eof"
                break
            if (time.monotonic_ns() - wall) / 1e9 >= config["max_duration_s"]:
                reason = "duration_limit"
                break
            sampler.sample()
    finally:
        report = sampler.report()
        report.update(
            stop_reason=reason,
            observation_start_ns=wall,
            observation_end_ns=time.monotonic_ns(),
            observer_cpu_ns=time.process_time_ns() - cpu,
            observer_process_cpu_ns=time.process_time_ns(),
            resources_at_start=host,
        )
        if reason != "caller_stop_or_eof":
            report["status"] = "incomplete"
        Path(config["report_path"]).write_text(json.dumps(report), encoding="utf-8")


if __name__ == "__main__":
    _worker_main()
