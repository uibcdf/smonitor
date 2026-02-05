from __future__ import annotations

import argparse
import json
from pathlib import Path

import smonitor
from smonitor.config import load_project_config, validate_config


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="smonitor")
    parser.add_argument("--profile", default=None)
    parser.add_argument("--level", default=None)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--config-path", default=None)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.validate_config:
        base = Path(args.config_path) if args.config_path else Path.cwd()
        cfg = load_project_config(base)
        if not cfg:
            print("No _smonitor.py found")
            return 1
        errors = validate_config(cfg)
        if errors:
            print("Invalid _smonitor.py:")
            for err in errors:
                print(f"- {err}")
            return 2
        print(json.dumps(cfg, indent=2, default=str))
        return 0

    smonitor.configure(profile=args.profile, level=args.level)
    if args.report:
        print(json.dumps(smonitor.report(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
