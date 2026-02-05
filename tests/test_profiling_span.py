import smonitor
from smonitor.profiling import span


def test_span_records_timeline():
    smonitor.configure(profile="user", profiling=True, profiling_buffer_size=10)
    with span("block", detail="x"):
        pass
    report = smonitor.report()
    assert any(item.get("span") for item in report["timeline"])
