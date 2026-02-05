from pathlib import Path

from smonitor.catalog import write_catalog

root = Path(__file__).resolve().parents[1]
write_catalog(root, Path(__file__).parent)
