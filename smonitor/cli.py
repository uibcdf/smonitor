from __future__ import annotations

import argparse
import json
from pathlib import Path

import smonitor
from smonitor.bundle import export_bundle
from smonitor.config import load_project_config, validate_project_config


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="smonitor")
    subparsers = parser.add_subparsers(dest="command")
    export_parser = subparsers.add_parser("export", help="Export a local smonitor bundle")
    export_parser.add_argument("--out", default="smonitor_bundle")
    export_parser.add_argument("--max-events", type=int, default=None)
    export_parser.add_argument("--since", default=None, help="ISO timestamp (filter events)")
    export_parser.add_argument("--no-events", action="store_true")
    export_parser.add_argument(
        "--append-events",
        action="store_true",
        help="Append to events.jsonl",
    )
    export_parser.add_argument("--drop-extra", action="store_true")
    export_parser.add_argument("--drop-context", action="store_true")
    export_parser.add_argument(
        "--redact",
        action="append",
        default=[],
        help="Redact dotted fields (e.g. extra.password)",
    )
    export_parser.add_argument("--force", action="store_true")
    export_parser.add_argument("--config-path", default=None)
    export_parser.add_argument("--profile", default=None)
    export_parser.add_argument("--level", default=None)
    parser.add_argument("--profile", default=None)
    parser.add_argument("--level", default=None)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--validate-config", action="store_true")
    parser.add_argument("--config-path", default=None)
    parser.add_argument("--check", action="store_true", help="Validate config and simulate event")
    parser.add_argument("--check-level", default="INFO")
    parser.add_argument("--check-code", default=None)
    parser.add_argument("--check-source", default="smonitor.cli")
    parser.add_argument("--check-event", default=None, help="JSON event override for check")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "export":
        base = Path(args.config_path) if args.config_path else Path.cwd()
        cfg = load_project_config(base)
        errors = validate_project_config(cfg)
        if errors:
            print("Invalid _smonitor.py:")
            for err in errors:
                print(f"- {err}")
            return 2
        smonitor.configure(profile=args.profile, level=args.level, handlers=[])
        out_path = export_bundle(
            args.out,
            include_events=not args.no_events,
            max_events=args.max_events,
            since=args.since,
            drop_extra=args.drop_extra,
            drop_context=args.drop_context,
            redact_fields=args.redact,
            force=args.force,
            append_events=args.append_events,
            config_base=base,
        )
        print(str(out_path))
        return 0

    base = Path(args.config_path) if args.config_path else Path.cwd()
    if args.validate_config:
        cfg = load_project_config(base)
        if not cfg:
            print("No _smonitor.py found")
            return 1
        errors = validate_project_config(cfg)
        if errors:
            print("Invalid _smonitor.py:")
            for err in errors:
                print(f"- {err}")
            return 2
        print(json.dumps(cfg, indent=2, default=str))
        return 0

    if args.check:
        cfg = load_project_config(base)
        errors = validate_project_config(cfg)
        if errors:
            print("Invalid _smonitor.py:")
            for err in errors:
                print(f"- {err}")
            return 2
        smonitor.configure(profile=args.profile, level=args.level)
        if args.check_event:
            event = json.loads(args.check_event)
            smonitor.emit(
                event.get("level", "INFO"),
                event.get("message", "smonitor check event"),
                source=event.get("source", args.check_source),
                code=event.get("code", args.check_code),
                extra=event.get("extra"),
                category=event.get("category"),
                tags=event.get("tags"),
            )
        else:
            smonitor.emit(
                args.check_level,
                "smonitor check event",
                source=args.check_source,
                code=args.check_code,
            )
        print("OK")
        return 0

    smonitor.configure(profile=args.profile, level=args.level)
    if args.report:
        print(json.dumps(smonitor.report(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
