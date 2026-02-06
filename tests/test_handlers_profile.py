from pathlib import Path

from smonitor.handlers.file import FileHandler


def test_file_handler_dev_includes_hint_and_chain(tmp_path: Path):
    path = tmp_path / "out.log"
    handler = FileHandler(str(path), mode="w")
    handler.handle(
        {
            "timestamp": "t",
            "level": "WARNING",
            "source": "s",
            "message": "m",
            "code": "C1",
            "context": {"chain": ["a", "b"]},
            "extra": {"hint": "h"},
        },
        profile="dev",
    )
    text = path.read_text(encoding="utf-8").strip()
    assert "Hint: h" in text
    assert "a -> b" in text
