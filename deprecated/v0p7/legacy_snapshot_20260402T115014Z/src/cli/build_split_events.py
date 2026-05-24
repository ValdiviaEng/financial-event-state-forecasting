"""CLI entry point for building split-event tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

from src.data.split_events_pipeline import SplitEventsPipeline
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build split-event tables for a universe or ticker list.")
    parser.add_argument("--tickers", default=None, help="Comma-separated explicit ticker list.")
    parser.add_argument("--universe-file", default=None, help="Universe CSV containing a ticker column.")
    parser.add_argument("--preferred-provider", default="auto", choices=["auto", "twelve_data", "yfinance"])
    parser.add_argument("--run-label", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--log-level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)

    tickers = _resolve_tickers(args)
    if not tickers:
        parser.error("Provide either --tickers or --universe-file with a non-empty ticker list.")

    pipeline = SplitEventsPipeline.from_settings(settings)
    summary = pipeline.build(tickers, preferred_provider=args.preferred_provider, run_label=args.run_label)
    logger.info("Built split events for %s requested tickers.", len(tickers))
    print(json.dumps(_to_jsonable(summary), indent=2, sort_keys=True))
    return 0


def _resolve_tickers(args: argparse.Namespace) -> list[str]:
    if args.tickers:
        return [item.strip().upper() for item in args.tickers.split(",") if item.strip()]
    if args.universe_file:
        frame = pd.read_csv(Path(args.universe_file))
        if "ticker" not in frame.columns:
            raise SystemExit("Universe file must contain a 'ticker' column.")
        return frame["ticker"].astype(str).tolist()
    return []


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
