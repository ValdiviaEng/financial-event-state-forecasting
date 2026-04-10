"""CLI entry point for building a frozen S&P 500 universe snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from src.data.universe_builder import (
    DEFAULT_PILOT_TICKERS,
    SP500_WIKIPEDIA_URL,
    build_and_save_sp500_universe_snapshot,
)
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and save a frozen S&P 500 universe snapshot.")
    parser.add_argument("--output-dir", default=None, help="Directory for universe snapshots. Defaults to data/raw/universe")
    parser.add_argument("--source-url", default=SP500_WIKIPEDIA_URL)
    parser.add_argument("--snapshot-date", default=None, help="Override snapshot date label (YYYY-MM-DD).")
    parser.add_argument("--no-pilot", action="store_true", help="Do not write pilot10.csv")
    parser.add_argument(
        "--pilot-tickers",
        default=",".join(DEFAULT_PILOT_TICKERS),
        help="Comma-separated pilot ticker list for pilot10.csv output.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--log-level", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)

    output_dir = Path(args.output_dir) if args.output_dir else settings.project_paths.data_raw_dir / "universe"
    pilot_tickers = tuple(item.strip().upper() for item in args.pilot_tickers.split(",") if item.strip())

    result = build_and_save_sp500_universe_snapshot(
        output_dir,
        source_url=args.source_url,
        snapshot_date=args.snapshot_date,
        timeout_seconds=args.timeout_seconds,
        include_pilot_subset=not args.no_pilot,
        pilot_tickers=pilot_tickers,
    )
    payload = result.as_dict()
    logger.info("Built S&P 500 universe snapshot with %s rows.", payload["row_count"])
    print(json.dumps(_to_jsonable(payload), indent=2, sort_keys=True))
    return 0


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
