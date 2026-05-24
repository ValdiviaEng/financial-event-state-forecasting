"""Download Alpha Vantage NEWS_SENTIMENT history for an explicit universe file."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

from dotenv import load_dotenv
import pandas as pd

from src.data.alphavantage_backfill_utils import (
    classify_planned_call,
    load_ledger_frame,
    minmax_time_published,
    write_classification_logs,
)
from src.data.alphavantage_client import AlphaVantageClient, AlphaVantageClientError, AlphaVantageRateLimitError
from src.data.universe_builder import load_universe_snapshot
from src.utils.io_utils import read_parquet, read_json, write_json, write_parquet
from src.utils.logging_setup import configure_logging
from src.utils.paths import build_project_paths, find_project_root


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Backfill Alpha Vantage news for an explicit ticker universe.")
    parser.add_argument("--universe-file", required=True)
    parser.add_argument("--years-back", type=int, default=10)
    parser.add_argument("--max-calls", type=int, default=25)
    parser.add_argument("--sleep-seconds", type=float, default=15.0)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--sort", default="LATEST")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--force-redownload", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    logger = configure_logging(log_level=args.log_level)
    project_root = find_project_root()
    load_dotenv(project_root / ".env", override=False)

    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ALPHAVANTAGE_API_KEY in legacy snapshot .env")

    snapshot = load_universe_snapshot(args.universe_file, treat_as_latest_snapshot=False)
    tickers = list(snapshot.tickers)

    paths = build_project_paths(project_root)
    paths.ensure_base_directories()
    raw_provider_dir = paths.raw_provider_dir("alphavantage")
    ledger_path = raw_provider_dir / "news_request_ledger.parquet"
    ledger_frame = load_ledger_frame(ledger_path)
    scope_name = Path(args.universe_file).stem

    client = AlphaVantageClient(api_key=api_key.strip())
    windows = yearly_windows(years_back=args.years_back)

    calls_made = 0
    sleep_seconds = float(args.sleep_seconds)
    ledger_records: list[dict[str, Any]] = []
    ticker_summaries: list[dict[str, Any]] = []
    call_classifications: list[dict[str, Any]] = []
    stop_reason = "completed_requested_universe"

    for ticker in tickers:
        ticker_dir = raw_provider_dir / ticker
        ticker_dir.mkdir(parents=True, exist_ok=True)
        ticker_rows = 0
        ticker_calls = 0
        ticker_oldest = None
        ticker_newest = None
        ticker_files: list[str] = []

        for start_dt, end_dt in windows:
            raw_path = ticker_dir / f"news_sentiment__{start_dt.date().isoformat()}__{end_dt.date().isoformat()}.json"
            time_from = start_dt.strftime("%Y%m%dT0000")
            time_to = end_dt.strftime("%Y%m%dT2359")

            classification = classify_planned_call(
                raw_path=raw_path,
                ledger_frame=ledger_frame,
                ticker=ticker,
                time_from=time_from,
                time_to=time_to,
                sort=args.sort,
                limit=args.limit,
            )
            if not args.force_redownload and classification["status"].startswith("already_done"):
                call_classifications.append(classification)
                ticker_rows += int(classification["rows_returned"] or 0)
                ticker_files.append(str(raw_path))
                oldest = classification.get("oldest_time_published")
                newest = classification.get("newest_time_published")
                if oldest is not None and (ticker_oldest is None or oldest < ticker_oldest):
                    ticker_oldest = oldest
                if newest is not None and (ticker_newest is None or newest > ticker_newest):
                    ticker_newest = newest
                logger.info(
                    "Skipping already downloaded call for %s window %s->%s classified as %s",
                    ticker,
                    start_dt.date(),
                    end_dt.date(),
                    classification["status"],
                )
                continue

            if calls_made >= args.max_calls:
                stop_reason = "max_calls_reached"
                break

            try:
                payload, metadata = client.get_news_sentiment(
                    symbol=ticker,
                    time_from=time_from,
                    time_to=time_to,
                    limit=args.limit,
                    sort=args.sort,
                )
                write_json(payload, raw_path)
                ledger_records.append(metadata.as_ledger_record(raw_path=str(raw_path)))
                feed = payload.get("feed", [])
                ticker_rows += len(feed)
                ticker_calls += 1
                calls_made += 1
                ticker_files.append(str(raw_path))
                oldest, newest = minmax_time_published(feed)
                if oldest is not None and (ticker_oldest is None or oldest < ticker_oldest):
                    ticker_oldest = oldest
                if newest is not None and (ticker_newest is None or newest > ticker_newest):
                    ticker_newest = newest
                call_classifications.append(
                    {
                        "ticker": ticker,
                        "time_from": time_from,
                        "time_to": time_to,
                        "raw_path": str(raw_path),
                        "status": "downloaded_truncated" if len(feed) >= args.limit else "downloaded_complete",
                        "rows_returned": len(feed),
                        "oldest_time_published": oldest,
                        "newest_time_published": newest,
                        "likely_truncated": len(feed) >= args.limit,
                        "ledger_match_count": 0,
                    }
                )
                logger.info(
                    "Downloaded %s rows for %s window %s->%s",
                    len(feed),
                    ticker,
                    start_dt.date(),
                    end_dt.date(),
                )
            except AlphaVantageRateLimitError as exc:
                stop_reason = "alphavantage_rate_or_daily_limit"
                ledger_records.append(
                    {
                        "request_id": f"NEWS_SENTIMENT:{ticker}:{datetime.now(UTC).isoformat()}",
                        "provider": "alphavantage",
                        "endpoint": "NEWS_SENTIMENT",
                        "ticker": ticker,
                        "requested_at_utc": datetime.now(UTC),
                        "response_status": None,
                        "success": False,
                        "raw_path": str(raw_path),
                        "time_from": time_from,
                        "time_to": time_to,
                        "sort": args.sort,
                        "limit": args.limit,
                        "result_count": None,
                        "request_url": None,
                        "error_message": str(exc),
                    }
                )
                call_classifications.append(
                    {
                        "ticker": ticker,
                        "time_from": time_from,
                        "time_to": time_to,
                        "raw_path": str(raw_path),
                        "status": "rate_limited",
                        "rows_returned": None,
                        "oldest_time_published": None,
                        "newest_time_published": None,
                        "likely_truncated": None,
                        "ledger_match_count": 0,
                        "error_message": str(exc),
                    }
                )
                logger.warning("Alpha Vantage stopped on rate/daily limit while processing %s", ticker)
                break
            except AlphaVantageClientError as exc:
                stop_reason = f"request_failed:{ticker}:{exc.__class__.__name__}"
                ledger_records.append(
                    {
                        "request_id": f"NEWS_SENTIMENT:{ticker}:{datetime.now(UTC).isoformat()}",
                        "provider": "alphavantage",
                        "endpoint": "NEWS_SENTIMENT",
                        "ticker": ticker,
                        "requested_at_utc": datetime.now(UTC),
                        "response_status": None,
                        "success": False,
                        "raw_path": str(raw_path),
                        "time_from": time_from,
                        "time_to": time_to,
                        "sort": args.sort,
                        "limit": args.limit,
                        "result_count": None,
                        "request_url": None,
                        "error_message": str(exc),
                    }
                )
                call_classifications.append(
                    {
                        "ticker": ticker,
                        "time_from": time_from,
                        "time_to": time_to,
                        "raw_path": str(raw_path),
                        "status": "request_failed",
                        "rows_returned": None,
                        "oldest_time_published": None,
                        "newest_time_published": None,
                        "likely_truncated": None,
                        "ledger_match_count": 0,
                        "error_message": str(exc),
                    }
                )
                logger.warning("Alpha Vantage request failed for %s: %s", ticker, exc)
                break

            if calls_made < args.max_calls:
                time.sleep(sleep_seconds)

        ticker_summaries.append(
            {
                "ticker": ticker,
                "calls_made_for_ticker": ticker_calls,
                "rows_returned_for_ticker": ticker_rows,
                "oldest_time_published_seen": ticker_oldest,
                "newest_time_published_seen": ticker_newest,
                "raw_files": ticker_files,
            }
        )

        if stop_reason in {"max_calls_reached", "alphavantage_rate_or_daily_limit"} or stop_reason.startswith("request_failed:"):
            break

    append_ledger(ledger_path=ledger_path, new_records=ledger_records)
    status_log_path, truncated_log_path = write_classification_logs(
        raw_provider_dir=raw_provider_dir,
        scope_name=scope_name,
        classifications=call_classifications,
    )
    summary = {
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "universe_file": str(Path(args.universe_file).resolve()),
        "tickers_requested": tickers,
        "years_back": args.years_back,
        "calls_made": calls_made,
        "max_calls": args.max_calls,
        "stop_reason": stop_reason,
        "status_log_path": str(status_log_path),
        "truncated_log_path": str(truncated_log_path),
        "ticker_summaries": ticker_summaries,
    }
    print(json.dumps(to_jsonable(summary), indent=2, sort_keys=True))
    return 0


def yearly_windows(*, years_back: int) -> list[tuple[datetime, datetime]]:
    now = datetime.now(UTC)
    current_year = now.year
    start_year = max(current_year - years_back + 1, 2010)
    windows: list[tuple[datetime, datetime]] = []
    for year in range(current_year, start_year - 1, -1):
        start_dt = datetime(year, 1, 1, tzinfo=UTC)
        if year == current_year:
            end_dt = now
        else:
            end_dt = datetime(year, 12, 31, 23, 59, 59, tzinfo=UTC)
        windows.append((start_dt, end_dt))
    return windows


def append_ledger(*, ledger_path: Path, new_records: list[dict[str, Any]]) -> None:
    if not new_records:
        return
    existing = pd.DataFrame()
    if ledger_path.exists():
        existing = read_parquet(ledger_path, backend="pandas")
    merged = pd.concat([existing, pd.DataFrame(new_records)], ignore_index=True)
    write_parquet(merged, ledger_path, index=False)


def to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
