import smonitor
from smonitor.core.manager import get_manager


def test_manager_report_includes_redundant_conversion_counters():
    manager = get_manager()
    manager.configure(profile="user", handlers=[])
    manager._redundant_conversions_by_callsite.clear()
    manager._redundant_conversions_recent.clear()

    manager.record_redundant_conversion(
        "pkg.mod:fn:10",
        form_in="pint",
        to_unit=None,
        to_form="pint",
        to_type="quantity",
    )
    manager.record_redundant_conversion(
        "pkg.mod:fn:10",
        form_in="pint",
        to_unit=None,
        to_form="pint",
        to_type="quantity",
    )

    report = manager.report()

    assert report["redundant_conversions_total"] == 2
    assert report["redundant_conversions_by_callsite"]["pkg.mod:fn:10"] == 2
    assert report["top_redundant_conversions"][0]["key"] == "pkg.mod:fn:10"
    assert report["top_redundant_conversions"][0]["count"] == 2
    assert report["redundant_conversions_recent"][-1]["form_in"] == "pint"
