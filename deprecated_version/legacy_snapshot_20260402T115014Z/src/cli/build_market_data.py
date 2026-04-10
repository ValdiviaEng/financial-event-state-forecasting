"""CLI entry point for market-data ingestion and normalization."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from src.data.price_pipeline import MarketPricePipeline
from src.data.universe_builder import load_universe_snapshot
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build raw and interim market data from Twelve Data.")
    parser.add_argument("--start-date", dest="start_date", default=None)
    parser.add_argument("--end-date", dest="end_date", default=None)
    parser.add_argument("--max-symbols", dest="max_symbols", type=int, default=None)
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--run-label", dest="run_label", default=None)
    parser.add_argument(
        "--tickers",
        dest="tickers",
        default=None,
        help="Comma-separated explicit ticker override, e.g. AAPL,MSFT,BRK.B",
    )
    parser.add_argument("--universe-file", dest="universe_file", default=None)
    parser.add_argument("--pilot-file", dest="pilot_file", default=None)
    parser.add_argument("--log-level", dest="log_level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)

    tickers = resolve_tickers(settings=settings, args=args)
    dataset_build_config = settings.get_config("dataset_build")
    dates_config = dataset_build_config.get("dates", {})

    start_date = args.start_date or dates_config.get("start_date") or settings.environment.market_start_date
    end_date = args.end_date or dates_config.get("end_date") or settings.environment.market_end_date
    if end_date is None:
        parser.error("An end date must be provided via config or CLI for market-data builds.")

    max_symbols = args.max_symbols or dataset_build_config.get("incremental_updates", {}).get("max_symbols_per_run")

    pipeline = MarketPricePipeline.from_settings(settings)
    summary = pipeline.run(
        tickers=tickers,
        start_date=str(start_date),
        end_date=str(end_date),
        max_symbols=max_symbols,
        force_refresh=args.force_refresh,
        dry_run=args.dry_run,
        run_label=args.run_label,
    )

    logger.info("Market-data build completed for %s planned updates.", len(summary.get("planned_updates", [])))
    print(json.dumps(_to_jsonable(summary), indent=2, sort_keys=True))
    return 0


def resolve_tickers(settings, args: argparse.Namespace) -> list[str]:
    if args.tickers:
        return [ticker.strip().upper() for ticker in args.tickers.split(",") if ticker.strip()]

    dataset_build_config = settings.get_config("dataset_build")
    universe_config = dataset_build_config.get("universe", {})

    active_mode = universe_config.get("active_mode", "pilot")
    if args.universe_file:
        universe_file = Path(args.universe_file)
    elif args.pilot_file:
        universe_file = Path(args.pilot_file)
    elif active_mode == "pilot":
        universe_file = Path(universe_config.get("pilot_file", universe_config.get("active_file")))
    else:
        universe_file = Path(universe_config.get("active_file", universe_config.get("source_file")))

    snapshot = load_universe_snapshot(universe_file)
    return list(snapshot.tickers)


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
