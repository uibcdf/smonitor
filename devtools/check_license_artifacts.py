"""Verify actual MIT notice bytes and SPDX metadata, including an sdist rebuild."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from email.parser import BytesParser
from pathlib import Path


def check_metadata(payload: bytes) -> None:
    metadata = BytesParser().parsebytes(payload)
    if metadata.get("License-Expression") != "MIT" or metadata.get_all("License-File") != [
        "LICENSE"
    ]:
        raise ValueError("distribution must declare the MIT expression and LICENSE file")


def check_wheel(path: Path, notice: bytes) -> None:
    with zipfile.ZipFile(path) as archive:
        (metadata_path,) = [
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        ]
        check_metadata(archive.read(metadata_path))
        license_path = metadata_path.rsplit("/", 1)[0] + "/licenses/LICENSE"
        if archive.read(license_path) != notice:
            raise ValueError("wheel license notice differs from the repository")


def check_distributions(dist: Path, notice_path: Path) -> dict:
    (sdist,) = dist.glob("smonitor-*.tar.gz")
    (wheel,) = dist.glob("smonitor-*.whl")
    notice = notice_path.read_bytes()
    check_wheel(wheel, notice)
    with tempfile.TemporaryDirectory(prefix="smonitor-license-") as temporary:
        root = Path(temporary)
        with tarfile.open(sdist) as archive:
            (member,) = [
                item
                for item in archive.getmembers()
                if item.name.count("/") == 1 and item.name.endswith("/LICENSE")
            ]
            if archive.extractfile(member).read() != notice:
                raise ValueError("sdist license notice differs from the repository")
            package_info = member.name.rsplit("/", 1)[0] + "/PKG-INFO"
            check_metadata(archive.extractfile(package_info).read())
            archive.extractall(root / "source", filter="data")
        (source,) = (root / "source").iterdir()
        command = [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(root / "rebuilt"),
            str(source),
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode:
            sys.stderr.buffer.write(result.stdout)
            result.check_returncode()
        (rebuilt,) = (root / "rebuilt").glob("*.whl")
        check_wheel(rebuilt, notice)
        return {
            "notice_sha256": hashlib.sha256(notice).hexdigest(),
            "sdist_sha256": hashlib.sha256(sdist.read_bytes()).hexdigest(),
            "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "rebuilt_wheel_sha256": hashlib.sha256(rebuilt.read_bytes()).hexdigest(),
            "license_expression": "MIT",
            "license_file": "LICENSE",
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--notice", type=Path, default=Path("LICENSE"))
    args = parser.parse_args()
    print(json.dumps(check_distributions(args.dist_dir, args.notice), indent=2))
