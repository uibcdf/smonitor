import smonitor


def test_profiling_timeline_and_module():
    smonitor.configure(profile="user", profiling=True, profiling_buffer_size=10)

    @smonitor.signal
    def foo():
        return 1

    foo()
    report = smonitor.report()
    assert report["timings"]
    assert report["timeline"]
    assert report["timings_by_module"]


def test_profiling_hooks():
    def hook():
        return {"gpu": "test"}

    smonitor.configure(profile="user", profiling=True, profiling_hooks=[hook])
    smonitor.emit("INFO", "x")
    report = smonitor.report()
    assert report["profiling_meta"]["gpu"] == "test"
