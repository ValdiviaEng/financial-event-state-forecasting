"""CLI entry point for building adjusted prices from split events."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

from src.data.price_pipeline import MarketPricePipeline
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build split-adjusted price history for a universe or ticker list.")
    parser.add_argument("--tickers", default=None, help="Comma-separated explicit ticker list.")
    parser.add_argument("--universe-file", default=None, help="Universe CSV containing a ticker column.")
    parser.add_argument("--split-events-path", default="data/interim/split_events/split_events.parquet")
    parser.add_argument("--adjustment-source", default="split_events")
    parser.add_argument("--missing-split-policy", default="warn_return_raw", choices=["warn_return_raw", "error"])
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

    split_events_df = pd.read_parquet(Path(args.split_events_path))
    by_ticker = {
        ticker: split_events_df[split_events_df["ticker"].astype(str) == ticker].to_dict(orient="records")
        for ticker in tickers
    }
    pipeline = MarketPricePipeline.from_settings(settings)
    results: list[dict[str, Any]] = []
    for ticker in tickers:
        result = pipeline.build_adjusted_prices_for_ticker(
            ticker,
            split_events=by_ticker.get(ticker, []),
            adjustment_source=args.adjustment_source,
            missing_split_policy=args.missing_split_policy,
        )
        results.append(result)
    logger.info("Built adjusted prices for %s tickers.", len(results))
    print(json.dumps(_to_jsonable({"results": results}), indent=2, sort_keys=True))
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
