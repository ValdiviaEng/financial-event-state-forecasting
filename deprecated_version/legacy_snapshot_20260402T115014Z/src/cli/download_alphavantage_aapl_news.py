"""Download Alpha Vantage NEWS_SENTIMENT history for AAPL into the legacy raw layer."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

import pandas as pd
from dotenv import load_dotenv

from src.data.alphavantage_backfill_utils import (
    classify_planned_call,
    load_ledger_frame,
    minmax_time_published,
    write_classification_logs,
)
from src.data.alphavantage_client import AlphaVantageClient, AlphaVantageRateLimitError
from src.utils.io_utils import read_parquet, write_json, write_parquet
from src.utils.logging_setup import configure_logging
from src.utils.paths import build_project_paths, find_project_root


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Download Alpha Vantage AAPL news history.")
    parser.add_argument("--ticker", default="AAPL")
    parser.add_argument("--max-calls", type=int, default=25)
    parser.add_argument("--years-back", type=int, default=20)
    parser.add_argument("--sleep-seconds", type=float, default=15.0)
    parser.add_argument("--limit", type=int, default=1000)
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

    paths = build_project_paths(project_root)
    paths.ensure_base_directories()

    raw_provider_dir = paths.raw_provider_dir("alphavantage")
    ticker_dir = raw_provider_dir / args.ticker.upper()
    ticker_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = raw_provider_dir / "news_request_ledger.parquet"
    ledger_frame = load_ledger_frame(ledger_path)
    scope_name = args.ticker.upper()

    client = AlphaVantageClient(api_key=api_key.strip())
    windows = yearly_windows(years_back=args.years_back)
    calls_made = 0
    sleep_seconds = float(args.sleep_seconds)
    ledger_records: list[dict[str, Any]] = []
    window_summaries: list[dict[str, Any]] = []
    call_classifications: list[dict[str, Any]] = []
    stop_reason = "completed_requested_windows"

    for start_dt, end_dt in windows:
        time_from = start_dt.strftime("%Y%m%dT0000")
        time_to = end_dt.strftime("%Y%m%dT2359")
        raw_path = ticker_dir / f"news_sentiment__{start_dt.date().isoformat()}__{end_dt.date().isoformat()}.json"

        classification = classify_planned_call(
            raw_path=raw_path,
            ledger_frame=ledger_frame,
            ticker=args.ticker.upper(),
            time_from=time_from,
            time_to=time_to,
            sort="LATEST",
            limit=args.limit,
        )
        if not args.force_redownload and classification["status"].startswith("already_done"):
            call_classifications.append(classification)
            window_summaries.append(
                {
                    "start_date": start_dt.date().isoformat(),
                    "end_date": end_dt.date().isoformat(),
                    "rows_returned": classification["rows_returned"],
                    "oldest_time_published": classification["oldest_time_published"],
                    "newest_time_published": classification["newest_time_published"],
                    "raw_path": str(raw_path),
                    "likely_truncated": classification["likely_truncated"],
                    "classification": classification["status"],
                }
            )
            logger.info(
                "Skipping already downloaded call for %s window %s->%s classified as %s",
                args.ticker.upper(),
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
                symbol=args.ticker,
                time_from=time_from,
                time_to=time_to,
                limit=args.limit,
                sort="LATEST",
            )
            write_json(payload, raw_path)
            ledger_records.append(metadata.as_ledger_record(raw_path=str(raw_path)))

            feed = payload.get("feed", [])
            oldest = min((item.get("time_published") for item in feed if item.get("time_published")), default=None)
            newest = max((item.get("time_published") for item in feed if item.get("time_published")), default=None)
            window_summaries.append(
                {
                    "start_date": start_dt.date().isoformat(),
                    "end_date": end_dt.date().isoformat(),
                    "rows_returned": len(feed),
                    "oldest_time_published": oldest,
                    "newest_time_published": newest,
                    "raw_path": str(raw_path),
                    "likely_truncated": len(feed) >= args.limit,
                    "classification": "downloaded_truncated" if len(feed) >= args.limit else "downloaded_complete",
                }
            )
            call_classifications.append(
                {
                    "ticker": args.ticker.upper(),
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
            calls_made += 1
            logger.info(
                "Downloaded %s rows for %s window %s to %s",
                len(feed),
                args.ticker.upper(),
                f"{start_dt.date()}->{end_dt.date()}",
                raw_path,
            )
        except AlphaVantageRateLimitError as exc:
            stop_reason = "alphavantage_rate_or_daily_limit"
            ledger_records.append(
                {
                    "request_id": f"NEWS_SENTIMENT:{args.ticker.upper()}:{datetime.now(UTC).isoformat()}",
                    "provider": "alphavantage",
                    "endpoint": "NEWS_SENTIMENT",
                    "ticker": args.ticker.upper(),
                    "requested_at_utc": datetime.now(UTC),
                    "response_status": None,
                    "success": False,
                    "raw_path": str(raw_path),
                    "time_from": time_from,
                    "time_to": time_to,
                    "sort": "LATEST",
                    "limit": args.limit,
                    "result_count": None,
                        "request_url": None,
                        "error_message": str(exc),
                    }
                )
            call_classifications.append(
                {
                    "ticker": args.ticker.upper(),
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
            logger.warning("Stopped on Alpha Vantage limit signal: %s", exc)
            break
        except Exception as exc:  # noqa: BLE001
            stop_reason = f"request_failed:{exc.__class__.__name__}"
            ledger_records.append(
                {
                    "request_id": f"NEWS_SENTIMENT:{args.ticker.upper()}:{datetime.now(UTC).isoformat()}",
                    "provider": "alphavantage",
                    "endpoint": "NEWS_SENTIMENT",
                    "ticker": args.ticker.upper(),
                    "requested_at_utc": datetime.now(UTC),
                    "response_status": None,
                    "success": False,
                    "raw_path": str(raw_path),
                    "time_from": time_from,
                    "time_to": time_to,
                    "sort": "LATEST",
                    "limit": args.limit,
                    "result_count": None,
                        "request_url": None,
                        "error_message": repr(exc),
                    }
                )
            call_classifications.append(
                {
                    "ticker": args.ticker.upper(),
                    "time_from": time_from,
                    "time_to": time_to,
                    "raw_path": str(raw_path),
                    "status": "request_failed",
                    "rows_returned": None,
                    "oldest_time_published": None,
                    "newest_time_published": None,
                    "likely_truncated": None,
                    "ledger_match_count": 0,
                    "error_message": repr(exc),
                }
            )
            logger.exception("Alpha Vantage request failed for %s window %s->%s", args.ticker.upper(), start_dt, end_dt)
            break

        if calls_made < args.max_calls:
            time.sleep(sleep_seconds)

    append_ledger(ledger_path=ledger_path, new_records=ledger_records)
    status_log_path, truncated_log_path = write_classification_logs(
        raw_provider_dir=raw_provider_dir,
        scope_name=scope_name,
        classifications=call_classifications,
    )
    summary = build_summary(ticker_dir=ticker_dir, ticker=args.ticker.upper(), calls_made=calls_made, max_calls=args.max_calls, stop_reason=stop_reason, windows=window_summaries)
    summary["status_log_path"] = str(status_log_path)
    summary["truncated_log_path"] = str(truncated_log_path)
    print(json.dumps(to_jsonable(summary), indent=2, sort_keys=True))
    return 0


def yearly_windows(*, years_back: int) -> list[tuple[datetime, datetime]]:
    now = datetime.now(UTC)
    current_year = now.year
    start_year = max(current_year - years_back + 1, 2000)
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


def build_summary(*, ticker_dir: Path, ticker: str, calls_made: int, max_calls: int, stop_reason: str, windows: list[dict[str, Any]]) -> dict[str, Any]:
    all_paths = sorted(str(path) for path in ticker_dir.glob("*.json"))
    total_rows = sum(item["rows_returned"] for item in windows)
    nonempty_windows = [item for item in windows if item["rows_returned"] > 0]
    oldest = None
    newest = None
    if nonempty_windows:
        oldest = min((item["oldest_time_published"] for item in nonempty_windows if item["oldest_time_published"]), default=None)
        newest = max((item["newest_time_published"] for item in nonempty_windows if item["newest_time_published"]), default=None)
    return {
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "ticker": ticker,
        "calls_made": calls_made,
        "max_calls": max_calls,
        "stop_reason": stop_reason,
        "total_rows_returned": total_rows,
        "oldest_time_published_seen": oldest,
        "newest_time_published_seen": newest,
        "raw_files": all_paths,
        "window_summaries": windows,
    }


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
