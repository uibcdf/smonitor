"""Exercise real optional Rich APIs at the reviewed provider floors (#55)."""

import pytest

from smonitor.handlers.console import RichConsoleHandler


@pytest.mark.parametrize("profile", ["user", "dev", "qa", "agent"])
def test_real_rich_renders_diagnostic_and_hint(profile):
    pytest.importorskip("rich")
    handler = RichConsoleHandler()
    with handler._console.capture() as capture:
        handler.handle(
            {
                "level": "WARNING",
                "message": "Controlled warning",
                "code": "TEST-W001",
                "source": "test.provider",
                "extra": {"hint": "Review the input"},
            },
            profile=profile,
        )
    assert "Controlled warning" in capture.get()
    if profile != "agent":
        assert "Review the input" in capture.get()
