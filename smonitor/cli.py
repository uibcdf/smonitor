from __future__ import annotations

import argparse
import json
from pathlib import Path

import smonitor
from smonitor.bundle import compare_bundles, export_bundle, format_bundle_comparison_markdown
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
    compare_parser = subparsers.add_parser("compare", help="Compare two smonitor bundles")
    compare_parser.add_argument("current")
    compare_parser.add_argument("previous")
    compare_parser.add_argument("--format", choices=["json", "markdown"], default="json")
    pytest_check = subparsers.add_parser(
        "pytest-check", help="Evaluate opt-in diagnostic policy on a receptor artifact"
    )
    pytest_check.add_argument("artifact")
    pytest_check.add_argument("--provider-root", action="append", default=[])
    pytest_check.add_argument("--forbid-code", action="append", default=[])
    pytest_check.add_argument("--baseline")
    pytest_check.add_argument("--require-diagnostics", action="store_true")
    pytest_baseline = subparsers.add_parser(
        "pytest-baseline", help="Write an accepted identity baseline from complete evidence"
    )
    pytest_baseline.add_argument("artifact")
    pytest_baseline.add_argument("--out", required=True)
    pytest_baseline.add_argument("--allow-empty", action="store_true")
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

    if args.command == "compare":
        diff = compare_bundles(args.current, args.previous)
        if args.format == "markdown":
            print(format_bundle_comparison_markdown(diff))
        else:
            print(json.dumps(diff, indent=2))
        return 0

    if args.command in {"pytest-check", "pytest-baseline"}:
        from smonitor.pytest_policy import (
            evaluate_pytest_artifact,
            load_baseline,
            load_provider_codes,
            write_baseline,
        )

        try:
            from pytest_receptor import ArtifactError

            provider_codes = None
            provider_violations = []
            baseline = None
            forbidden_codes = ()
            if args.command == "pytest-check":
                if args.provider_root:
                    provider_codes, provider_violations = load_provider_codes(args.provider_root)
                if args.baseline:
                    baseline = load_baseline(args.baseline)
                forbidden_codes = args.forbid_code
            result = evaluate_pytest_artifact(
                args.artifact,
                known_codes=provider_codes,
                forbidden_codes=forbidden_codes,
                baseline=baseline,
                require_diagnostics=args.require_diagnostics
                if args.command == "pytest-check"
                else False,
            )
            if provider_violations:
                result["violations"].extend(provider_violations)
                result["ok"] = False
            if args.command == "pytest-baseline" and result["pytest_outcome"] != "PASS":
                result["violations"].append({"rule": "pytest_run_not_passed"})
                result["ok"] = False
            if (
                args.command == "pytest-baseline"
                and not result["identities"]
                and not args.allow_empty
            ):
                result["violations"].append({"rule": "empty_baseline_requires_opt_in"})
                result["ok"] = False
            if args.command == "pytest-baseline" and result["ok"]:
                write_baseline(
                    args.out,
                    (
                        (item["code"], item["source"], item["fingerprint"])
                        for item in result["identities"]
                    ),
                )
            print(json.dumps(result, indent=2))
            return 0 if result["ok"] else 1
        except (ArtifactError, OSError, ValueError, ImportError) as exc:
            print(json.dumps({"schema": "smonitor.pytest-policy-result@1", "error": str(exc)}))
            return 2

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
