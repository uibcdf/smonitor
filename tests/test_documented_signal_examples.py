"""Execute the published entry-point examples against the public decorator."""

import re
from pathlib import Path

import pytest

import smonitor

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "document",
    ["README.md", "docs/index.md", "docs/content/showcase/library-integration-contract.md"],
)
def test_documented_signal_definition_and_call(document):
    source = (ROOT / document).read_text(encoding="utf-8")
    examples = [
        block
        for block in re.findall(r"```python\n(.*?)```", source, flags=re.DOTALL)
        if "@smonitor.signal" in block
    ]
    assert examples
    smonitor.configure(event_buffer_size=10)
    namespace = {"__name__": "documented_example"}
    for example in examples:
        exec(compile(example, document, "exec"), namespace)
    if "do_work" in namespace:
        assert namespace["do_work"](3) == 6
    else:
        items = ["one", "two"]
        namespace["select"](items, "all")
    assert smonitor.report()["events_by_code"]
