from smonitor.docs_utils import render_codes_table, render_signals_table


def test_render_codes_table():
    codes = {"X": {"title": "T", "user_message": "U"}}
    out = render_codes_table(codes)
    assert "X" in out and "T" in out and "U" in out


def test_render_signals_table():
    signals = {"mod.fn": {"warnings": ["W"], "errors": ["E"], "extra_required": ["x"]}}
    out = render_signals_table(signals)
    assert "mod.fn" in out and "W" in out and "E" in out and "x" in out
