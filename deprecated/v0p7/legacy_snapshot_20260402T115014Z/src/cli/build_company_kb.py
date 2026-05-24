"""CLI entry point for SEC company knowledge-base ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from src.data.company_kb_pipeline import CompanyKbPipeline
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build SEC company knowledge-base tables.")
    parser.add_argument(
        "--ciks",
        dest="ciks",
        default=None,
        help="Comma-separated CIK list, e.g. 320193,789019",
    )
    parser.add_argument(
        "--cik-file",
        dest="cik_file",
        default=None,
        help="Path to a text file containing one CIK per line.",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--run-label", dest="run_label", default=None)
    parser.add_argument("--log-level", dest="log_level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)

    ciks = resolve_ciks(args)
    if not ciks:
        parser.error("At least one CIK must be supplied via --ciks or --cik-file.")

    pipeline = CompanyKbPipeline.from_settings(settings)
    summary = pipeline.build_from_ciks(ciks, run_label=args.run_label, dry_run=args.dry_run)

    logger.info("Company KB build completed for %s requested CIKs.", len(summary.get("requested_ciks", [])))
    print(json.dumps(_to_jsonable(summary), indent=2, sort_keys=True))
    return 0


def resolve_ciks(args: argparse.Namespace) -> list[str]:
    ciks: list[str] = []
    if args.ciks:
        ciks.extend(value.strip() for value in args.ciks.split(",") if value.strip())

    if args.cik_file:
        path = Path(args.cik_file)
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped:
                ciks.append(stripped)

    seen: set[str] = set()
    unique_ciks: list[str] = []
    for cik in ciks:
        if cik not in seen:
            seen.add(cik)
            unique_ciks.append(cik)
    return unique_ciks


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
