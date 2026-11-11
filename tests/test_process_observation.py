import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from smonitor import _process_observation as backend
from smonitor.profiling import ObservationError, linux_resource_snapshot, observe_process_family

linux = pytest.mark.skipif(sys.platform != "linux", reason="Linux /proc capability")


def fake_process(root, pid, *, ppid=1, start=10, cpu=20, children=(), secondary_children=()):
    directory = root / str(pid)
    directory.mkdir(exist_ok=True)
    fields = ["0"] * 22
    fields[0], fields[1] = "S", str(ppid)
    fields[11], fields[12], fields[13], fields[14] = str(cpu), "0", "5", "0"
    fields[17], fields[19], fields[21] = "2", str(start), "100"
    (directory / "stat").write_text(f"{pid} (private name (with spaces)) " + " ".join(fields))
    (directory / "smaps_rollup").write_text("Pss: 32 kB\n")
    for tid, values in ((pid, children), (pid + 1000, secondary_children)):
        task = directory / "task" / str(tid)
        task.mkdir(parents=True, exist_ok=True)
        (task / "children").write_text(" ".join(map(str, values)))


@pytest.fixture
def fake_proc(tmp_path, monkeypatch):
    monkeypatch.setattr(backend, "_PROC", tmp_path)
    monkeypatch.setattr(
        backend.os, "sysconf", lambda name: 100 if name == "SC_CLK_TCK" else 4096, raising=False
    )
    return tmp_path


def sampler(pid=7, **options):
    return backend._FamilySampler(
        {
            "pid": pid,
            "start_ticks": 10,
            "interval_s": 0.1,
            "max_processes": 16,
            "max_tasks": 32,
            **options,
        }
    )


def test_all_task_discovery_and_cpu_fields_are_separate(fake_proc):
    fake_process(fake_proc, 7, secondary_children=[9])
    fake_process(fake_proc, 9, ppid=7)
    observation = sampler()
    observation.sample()
    sample = observation.samples[0]
    assert {p["pid"] for p in sample["processes"]} == {7, 9}
    assert sample["family_pss_bytes"] == 64 * 1024
    fake_process(fake_proc, 7, cpu=23, secondary_children=[9])
    fake_process(fake_proc, 9, ppid=7, cpu=25)
    observation.sample()
    report = observation.report()
    assert [row["observed_self_cpu_ticks_delta"] for row in report["process_cpu_deltas"]] == [3, 5]
    assert report["cpu_ticks_per_second"] == 100
    assert report["true_peak_pss_bytes"] is None
    assert not report["continuous_coverage"]
    assert not report["atomic_family_sample"]
    assert "private name" not in json.dumps(report)


def test_pss_read_gap_keeps_pid_operation_time_and_previous_success(fake_proc):
    fake_process(fake_proc, 7)
    observation = sampler()
    observation.sample()
    (fake_proc / "7" / "smaps_rollup").unlink()
    observation.sample()
    sample = observation.samples[-1]
    assert sample["family_pss_bytes"] is None
    assert sample["observed_pss_bytes"] is None
    error = sample["errors"][0]
    assert error["pid"] == 7 and error["start_ticks"] == 10
    assert error["operation"] == "smaps_rollup"
    assert error["category"] == "not_found_or_exited"
    assert error["time_ns"] >= error["last_success_ns"] > 0
    assert observation.report()["status"] == "incomplete"


def test_pid_reuse_is_rejected_and_reparented_known_child_is_retained(fake_proc):
    fake_process(fake_proc, 7, children=[9])
    fake_process(fake_proc, 9, ppid=7)
    observation = sampler()
    observation.sample()
    fake_process(fake_proc, 7, start=11)
    fake_process(fake_proc, 9, ppid=1)
    observation.sample()
    sample = observation.samples[-1]
    assert [p["pid"] for p in sample["processes"]] == [9]
    assert any(e["pid"] == 7 and e["category"] == "pid_reused" for e in sample["errors"])
    assert sample["family_pss_bytes"] is None


def test_discovery_limits_never_become_complete_family_memory(fake_proc):
    fake_process(fake_proc, 7, children=[9, 10])
    fake_process(fake_proc, 9, ppid=7)
    fake_process(fake_proc, 10, ppid=7)
    observation = sampler(max_processes=2)
    observation.sample()
    assert len(observation.known) == 2
    assert observation.report()["status"] == "incomplete"
    assert observation.samples[0]["family_pss_bytes"] is None


def test_permission_denied_remains_unavailable(fake_proc, monkeypatch):
    fake_process(fake_proc, 7)
    read = backend._read

    def restricted(path, *args):
        if path.name == "smaps_rollup":
            raise PermissionError
        return read(path, *args)

    monkeypatch.setattr(backend, "_read", restricted)
    observation = sampler()
    observation.sample()
    sample = observation.samples[0]
    assert sample["errors"][0]["category"] == "permission_denied"
    assert sample["processes"][0]["pss_bytes"] is None


@linux
def test_actual_sibling_observer_sees_secondary_thread_child_and_leaves_exit_to_caller():
    child_source = (
        "import sys; data=bytearray(1048576); print('ready',flush=True); sys.stdin.readline()"
    )
    source = """import subprocess, sys, threading
print('ready', flush=True)
sys.stdin.readline()
finish = threading.Event()
def thread_work():
    child = subprocess.Popen([sys.executable, '-c', CHILD], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    assert child.stdout.readline().strip() == 'ready'
    print(child.pid, flush=True)
    finish.wait(10)
    child.communicate('stop\\n', timeout=3)
worker = threading.Thread(target=thread_work)
worker.start()
sys.stdin.readline()
finish.set()
worker.join(5)
sys.exit(17)
""".replace("CHILD", repr(child_source))
    process = subprocess.Popen(
        [sys.executable, "-c", source], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    try:
        assert process.stdout.readline().strip() == "ready"
        with observe_process_family(process.pid, interval_s=0.01, max_samples=100) as observation:
            observer_pid = observation._worker.pid
            assert Path(f"/proc/{observer_pid}").exists()
            process.stdin.write("go\n")
            process.stdin.flush()
            child_pid = int(process.stdout.readline())
            time.sleep(0.08)
        report = observation.report()
        assert report["observer_exit_code"] == 0
        assert report["observer_cpu_ns"] >= 0
        assert process.poll() is None
        assert any(child_pid in {p["pid"] for p in s["processes"]} for s in report["samples"])
        assert all(
            observer_pid not in {p["pid"] for p in s["processes"]} for s in report["samples"]
        )
        assert all(s["end_ns"] >= s["start_ns"] for s in report["samples"])
        assert not Path(f"/proc/{observer_pid}").exists()
        process.communicate("finish\n", timeout=5)
        assert process.returncode == 17
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)


@linux
def test_body_exception_preserved_and_temporary_observer_retired():
    process = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.stdin.readline()"], stdin=subprocess.PIPE, text=True
    )
    error = RuntimeError("calculation failure")
    try:
        with pytest.raises(RuntimeError) as caught:
            with observe_process_family(process.pid) as observation:
                observer_pid = observation._worker.pid
                temporary = observation._temporary
                raise error
        assert caught.value is error
        assert process.poll() is None
        assert not Path(temporary).exists()
        assert not Path(f"/proc/{observer_pid}").exists()
    finally:
        process.communicate("stop\n", timeout=5)


@linux
def test_self_root_refused_before_launching_an_observer():
    with pytest.raises(ObservationError) as caught:
        with observe_process_family(os.getpid()):
            pass
    assert caught.value.code == "SMONITOR-OBSERVATION-CONFLICT"


@linux
def test_resource_snapshot_exposes_capacity_pressure_and_controls_separately():
    report = linux_resource_snapshot(os.getpid())
    assert report["identity_verified"]
    assert report["affinity_cpus"] == sorted(os.sched_getaffinity(0))
    assert "cpu" in report["host_pressure_raw"]
    assert "MemAvailable" in report["host_memory_bytes"]
    assert isinstance(report["visible_cgroup_v2_ancestors"], list)


def test_unsupported_process_backend_refuses_explicitly(monkeypatch):
    monkeypatch.setattr(backend.sys, "platform", "unsupported")
    with pytest.raises(ObservationError) as caught:
        with observe_process_family(7):
            pass
    assert caught.value.code == "SMONITOR-OBSERVATION-UNSUPPORTED"


@pytest.mark.parametrize(
    "options",
    [
        {"max_samples": 0},
        {"max_samples": 10000, "max_processes": 4096},
        {"interval_s": float("nan")},
        {"max_tasks": True},
    ],
)
def test_process_selection_bounds_are_validated(options):
    with pytest.raises(ObservationError) as caught:
        observe_process_family(7, **options)
    assert caught.value.code == "SMONITOR-OBSERVATION-INVALID"


def test_repeated_failed_reads_retain_the_last_success_of_that_operation(fake_proc):
    fake_process(fake_proc, 7)
    observation = sampler()
    observation.sample()
    (fake_proc / "7" / "smaps_rollup").unlink()
    observation.sample()
    observation.sample()
    assert (
        observation.samples[-1]["errors"][0]["last_success_ns"]
        == observation.samples[-2]["errors"][0]["last_success_ns"]
    )


def test_read_limits_and_operation_categories(fake_proc):
    path = fake_proc / "oversized"
    path.write_text("abcdef")
    with pytest.raises(ValueError):
        backend._read(path, 5)
    assert backend._category(ProcessLookupError()) == "process_lookup"
    assert backend._category(OSError()) == "os_error"
    assert backend._category(ValueError()) == "invalid_read"


def test_non_ascii_process_name_does_not_change_numeric_observation(fake_proc):
    fake_process(fake_proc, 7)
    path = fake_proc / "7" / "stat"
    path.write_bytes(path.read_bytes().replace(b"private name", b"private \xff name"))
    observation = sampler()
    observation.sample()
    assert observation.samples[0]["family_pss_bytes"] == 32768
    assert "private" not in json.dumps(observation.report())


def test_missing_child_and_task_file_are_retained_with_operation_context(fake_proc):
    fake_process(fake_proc, 7, children=[9])
    (fake_proc / "7" / "task" / "1007" / "children").unlink()
    observation = sampler()
    observation.sample()
    errors = observation.samples[0]["errors"]
    assert {(e["pid"], e["operation"]) for e in errors} == {(7, "task_children"), (9, "stat")}
    assert next(e for e in errors if e["operation"] == "task_children")["tid"] == 1007


def test_root_exit_preserves_previously_discovered_descendants(fake_proc):
    import shutil

    fake_process(fake_proc, 7, children=[9])
    fake_process(fake_proc, 9, ppid=7)
    observation = sampler()
    observation.sample()
    shutil.rmtree(fake_proc / "7")
    fake_process(fake_proc, 9, ppid=1)
    observation.sample()
    assert [row["pid"] for row in observation.samples[-1]["processes"]] == [9]
    assert observation.report()["status"] == "incomplete"


def test_parent_changed_before_child_identity_is_never_adopted(fake_proc):
    fake_process(fake_proc, 7, children=[9])
    fake_process(fake_proc, 9, ppid=1)
    observation = sampler()
    observation.sample()
    assert 9 not in observation.known
    assert observation.samples[0]["errors"][0]["category"] == "parent_changed"


@pytest.mark.parametrize("after", ["changed", "missing"])
def test_identity_change_during_memory_read_invalidates_memory(fake_proc, monkeypatch, after):
    fake_process(fake_proc, 7)
    read = backend._read

    def racing(path, *args):
        value = read(path, *args)
        if path.name == "smaps_rollup":
            if after == "changed":
                fake_process(fake_proc, 7, start=11)
            else:
                (fake_proc / "7" / "stat").unlink()
        return value

    monkeypatch.setattr(backend, "_read", racing)
    observation = sampler()
    observation.sample()
    assert observation.samples[0]["processes"][0]["pss_bytes"] is None
    assert not observation.samples[0]["processes"][0]["identity_verified"]


@pytest.mark.parametrize("contents", ["Pss: -1 kB\n", "Pss: 1 B\n", "Rss: 2 kB\n"])
def test_invalid_pss_is_unavailable(fake_proc, contents):
    fake_process(fake_proc, 7)
    (fake_proc / "7" / "smaps_rollup").write_text(contents)
    observation = sampler()
    observation.sample()
    assert observation.samples[0]["family_pss_bytes"] is None
    assert observation.samples[0]["errors"][0]["operation"] == "smaps_rollup"


def test_task_and_child_discovery_bounds_are_reported(fake_proc):
    fake_process(fake_proc, 7, children=range(10, 20))
    observation = sampler(max_processes=2)
    observation.sample()
    assert any(
        e["operation"] == "child_discovery" and e["category"] == "limit"
        for e in observation.samples[0]["errors"]
    )
    observation = sampler(max_tasks=1)
    observation.sample()
    assert any(
        e["operation"] == "task_discovery" and e["category"] == "limit"
        for e in observation.samples[0]["errors"]
    )


def test_error_and_previous_success_metadata_are_bounded(fake_proc):
    fake_process(fake_proc, 7)
    observation = sampler()
    observation.sample()
    sample = observation.samples[0]
    for _ in range(4200):
        observation._error(sample, 7, "probe", "permission_denied")
    assert len(sample["errors"]) == 128
    assert sample["errors_omitted"] == 4072
    for tid in range(4200):
        observation._remember(7, "task_children", tid)
    assert len(observation.last_success) == 4096
    assert observation.report()["success_history_omitted"] > 0


@linux
@pytest.mark.parametrize(
    "limit,reason",
    [({"max_samples": 1}, "sample_limit"), ({"max_duration_s": 0.001}, "duration_limit")],
)
def test_finite_worker_bounds_stop_without_affecting_calculation(limit, reason):
    process = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.stdin.readline()"], stdin=subprocess.PIPE, text=True
    )
    try:
        with observe_process_family(process.pid, **limit) as observation:
            time.sleep(0.03)
        report = observation.report()
        assert report["stop_reason"] == reason
        assert report["status"] == "incomplete"
        assert process.poll() is None
    finally:
        process.communicate("stop\n", timeout=5)


def test_worker_control_loop_and_original_sample_receipt(fake_proc, monkeypatch, capsys):
    import io

    fake_process(fake_proc, 7)
    path = fake_proc / "receipt.json"
    config = {
        "pid": 7,
        "start_ticks": 10,
        "interval_s": 0.1,
        "max_samples": 2,
        "max_processes": 16,
        "max_tasks": 32,
        "max_duration_s": 1,
        "include_host": False,
        "report_path": str(path),
    }
    monkeypatch.setattr(backend.sys, "stdin", io.StringIO(json.dumps(config) + "\nstop\n"))
    monkeypatch.setattr(backend.select, "select", lambda *args: ([sys.stdin], [], []))
    backend._worker_main()
    report = json.loads(path.read_text())
    assert json.loads(capsys.readouterr().out) == {"ready": True, "pid": os.getpid()}
    assert report["stop_reason"] == "caller_stop_or_eof"
    assert report["observer_cpu_ns"] >= 0
    assert len(report["samples"]) == 1
    assert report["samples"][0]["family_pss_bytes"] == 32768


@linux
def test_startup_failure_retires_owned_temp_and_preserves_catalog_error(monkeypatch):
    process = subprocess.Popen(
        [sys.executable, "-c", "import sys; sys.stdin.readline()"], stdin=subprocess.PIPE, text=True
    )
    observation = observe_process_family(process.pid)
    try:

        def unavailable(*args, **kwargs):
            raise OSError

        with monkeypatch.context() as patch:
            patch.setattr(backend.subprocess, "Popen", unavailable)
            with pytest.raises(ObservationError) as caught:
                observation.__enter__()
        assert caught.value.code == "SMONITOR-OBSERVATION-IO"
        assert not observation._temporary.exists()
        assert process.poll() is None
    finally:
        process.communicate("stop\n", timeout=5)


def test_snapshot_unavailable_facts_are_explicit(fake_proc):
    report = linux_resource_snapshot(7) if sys.platform == "linux" else None
    if report is not None:
        assert not report["identity_verified"]
        assert report["host_memory_bytes"] is None
        assert report["status"] == "incomplete"
    with pytest.raises(ObservationError):
        linux_resource_snapshot(0)


def test_process_report_requires_closed_scope():
    with pytest.raises(ObservationError):
        observe_process_family(7).report()


@pytest.mark.parametrize("stop", ["sample_limit", "duration_limit", "host_snapshot"])
def test_worker_finite_window_limits_and_host_receipt(fake_proc, monkeypatch, capsys, stop):
    import io

    fake_process(fake_proc, 7)
    report_path = fake_proc / "report.json"
    config = {
        "pid": 7,
        "start_ticks": 10,
        "interval_s": 0.1,
        "max_samples": 2,
        "max_processes": 16,
        "max_tasks": 32,
        "max_duration_s": 1,
        "include_host": stop == "host_snapshot",
        "report_path": str(report_path),
    }
    monkeypatch.setattr(backend.sys, "stdin", io.StringIO(json.dumps(config) + "\n"))
    clock = [0]
    monkeypatch.setattr(backend.time, "monotonic_ns", lambda: clock[0])

    def wait(*args):
        if stop == "duration_limit":
            clock[0] = 2_000_000_000
        return [], [], []

    monkeypatch.setattr(backend.select, "select", wait)
    monkeypatch.setattr(
        backend, "linux_resource_snapshot", lambda pid: {"pid": pid, "status": "observed"}
    )
    backend._worker_main()
    report = json.loads(report_path.read_text())
    assert report["stop_reason"] == (
        "duration_limit" if stop == "duration_limit" else "sample_limit"
    )
    assert report["status"] == "incomplete"
    assert report["observer_process_cpu_ns"] >= report["observer_cpu_ns"]
    assert (report["resources_at_start"] is not None) == (stop == "host_snapshot")


@linux
def test_visible_cgroup_resource_snapshot_preserves_raw_controls(fake_proc, monkeypatch):
    fake_process(fake_proc, 7)
    (fake_proc / "7" / "cgroup").write_text("0::/\n")
    (fake_proc / "meminfo").write_text("MemAvailable: 100 kB\nSwapFree: 90 kB\nSwapTotal: 100 kB\n")
    pressure = fake_proc / "pressure"
    pressure.mkdir()
    for kind in ("cpu", "memory", "io"):
        (pressure / kind).write_text("some avg10=0.0 total=0\n")
    read = backend._read

    def controls(path, *args):
        if str(path).startswith("/sys/fs/cgroup/"):
            return "max 100000\n" if path.name == "cpu.max" else "max\n"
        return read(path, *args)

    monkeypatch.setattr(backend, "_read", controls)
    monkeypatch.setattr(backend.os, "sched_getaffinity", lambda pid: {1, 2})
    report = linux_resource_snapshot(7)
    assert report["status"] == "observed"
    assert report["host_memory_bytes"]["MemAvailable"] == 102400
    assert report["visible_cgroup_v2_ancestors"][0]["controls"]["cpu.max"] == "max 100000\n"


def test_unretired_observer_preserves_its_owned_directory_until_retry(tmp_path):
    class Worker:
        pid = 123
        returncode = None

        def communicate(self, *args, **kwargs):
            if self.returncode is None:
                raise subprocess.TimeoutExpired("owned observer", 1)

        def terminate(self):
            pass

        def kill(self):
            pass

        def poll(self):
            return self.returncode

    observation = observe_process_family(7)
    observation._temporary = tmp_path / "owned"
    observation._temporary.mkdir()
    observation._config["report_path"] = str(observation._temporary / "report.json")
    observation._worker = Worker()
    observation.stop()
    assert observation.report()["observer_cleanup_pending"]
    assert observation._temporary.exists()
    observation._worker.returncode = -9
    observation.stop()
    assert not observation.report()["observer_cleanup_pending"]
    assert observation.report()["status"] == "incomplete"
    assert not observation._temporary.exists()
