from pathlib import Path

from smonitor.handlers.file import FileHandler


def test_file_handler_agent_format(tmp_path: Path):
    path = tmp_path / "agent.log"
    handler = FileHandler(str(path), mode="w")
    handler.handle(
        {
            "timestamp": "t",
            "level": "ERROR",
            "source": "pkg.mod",
            "message": "boom",
            "code": "E-1",
        },
        profile="agent",
    )
    text = path.read_text(encoding="utf-8").strip()
    assert "code=E-1 level=ERROR source=pkg.mod message=boom" in text


def test_file_handler_fallback_profile_branch(tmp_path: Path):
    path = tmp_path / "fallback.log"
    handler = FileHandler(str(path), mode="w")
    handler.handle(
        {"timestamp": "t", "level": "INFO", "source": "s", "message": "m", "code": "C1"},
        profile="custom",
    )
    text = path.read_text(encoding="utf-8").strip()
    assert text.endswith("[C1] INFO s | m")
