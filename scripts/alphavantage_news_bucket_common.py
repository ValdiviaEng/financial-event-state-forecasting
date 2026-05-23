"""Shared standalone runner core for hardcoded Alpha Vantage ticker buckets.

The wrappers in this directory provide the hardcoded ticker lists and fallback
API key values. This module keeps the runtime behavior consistent across all
bucket scripts while remaining standard-library only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


LOGGER = logging.getLogger("alphavantage_news_bucket")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = PROJECT_ROOT / "deprecated_version" / "legacy_snapshot_20260402T115014Z"
RAW_UNIVERSE_DIR = PROJECT_ROOT / "data" / "raw" / "universe"
RAW_ALPHAVANTAGE_DIR = PROJECT_ROOT / "data" / "raw" / "alphavantage"
RUN_LOG_DIR = PROJECT_ROOT / "runs" / "logs"
DEFAULT_LEDGER_JSONL = RAW_ALPHAVANTAGE_DIR / "news_request_ledger.jsonl"


class AlphaVantageClientError(RuntimeError):
    pass


class AlphaVantageRateLimitError(AlphaVantageClientError):
    pass


@dataclass(frozen=True, slots=True)
class YearWindow:
    year: int
    time_from: str
    time_to: str
    file_start: str
    file_end: str
    is_current_year: bool


@dataclass(frozen=True, slots=True)
class BucketConfig:
    script_description: str
    bucket_label: str
    bucket_slug: str
    ticker_range_label: str
    base_tickers: tuple[str, ...]
    fallback_api_key: str = ""
    expanded_tickers: tuple[str, ...] = ()
    user_agent: str = "EventStateForecastingAlphaVantageBucket/1.0"


def main_for_bucket(config: BucketConfig, argv: list[str] | None = None) -> int:
    args = build_argument_parser(config).parse_args(argv)
    active_tickers, universe_source = resolve_active_tickers(config, args)

    configure_logging(log_level=args.log_level, log_path=log_path_for(config.bucket_slug, args.reverse, args.include_expanded, args.expanded_only))
    ensure_runtime_directories()
    if not args.skip_seed_migration:
        migrate_seed_data()

    if args.start_year > args.end_year:
        raise ValueError("start-year must be <= end-year")

    windows = build_year_windows(start_year=args.start_year, end_year=args.end_year)
    ensure_current_year_aliases(raw_provider_dir=RAW_ALPHAVANTAGE_DIR, current_year=args.end_year)

    if args.migrate_only:
        pending = build_pending_requests(tickers=active_tickers, windows=windows)
        summary = build_progress_summary(
            bucket_label=config.bucket_label,
            bucket_slug=config.bucket_slug,
            universe_source=universe_source,
            tickers=active_tickers,
            windows=windows,
            pending_requests=pending,
            limit=args.limit,
            max_calls_per_24h=args.max_calls_per_24h,
            reverse=args.reverse,
            include_expanded=args.include_expanded,
            expanded_only=args.expanded_only,
            expanded_count=len(config.expanded_tickers),
        )
        write_json_atomic(summary, summary_path_for(config.bucket_slug, args.reverse, args.include_expanded, args.expanded_only))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if args.plan:
        pending = build_pending_requests(tickers=active_tickers, windows=windows)
        summary = build_progress_summary(
            bucket_label=config.bucket_label,
            bucket_slug=config.bucket_slug,
            universe_source=universe_source,
            tickers=active_tickers,
            windows=windows,
            pending_requests=pending,
            limit=args.limit,
            max_calls_per_24h=args.max_calls_per_24h,
            reverse=args.reverse,
            include_expanded=args.include_expanded,
            expanded_only=args.expanded_only,
            expanded_count=len(config.expanded_tickers),
        )
        write_json_atomic(summary, summary_path_for(config.bucket_slug, args.reverse, args.include_expanded, args.expanded_only))
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    api_key = load_api_key(PROJECT_ROOT / ".env", explicit_api_key=args.api_key, fallback_api_key=config.fallback_api_key)

    while True:
        pending = build_pending_requests(tickers=active_tickers, windows=windows)
        summary = build_progress_summary(
            bucket_label=config.bucket_label,
            bucket_slug=config.bucket_slug,
            universe_source=universe_source,
            tickers=active_tickers,
            windows=windows,
            pending_requests=pending,
            limit=args.limit,
            max_calls_per_24h=args.max_calls_per_24h,
            reverse=args.reverse,
            include_expanded=args.include_expanded,
            expanded_only=args.expanded_only,
            expanded_count=len(config.expanded_tickers),
        )
        write_json_atomic(summary, summary_path_for(config.bucket_slug, args.reverse, args.include_expanded, args.expanded_only))

        if not pending:
            LOGGER.info("No pending Alpha Vantage windows remain for %s", universe_source)
            if args.once:
                print(json.dumps(summary, indent=2, sort_keys=True))
                return 0
            time.sleep(max(60.0, float(args.idle_sleep_seconds)))
            continue

        recent_success_times = load_recent_success_times(DEFAULT_LEDGER_JSONL, within_hours=24)
        budget = args.max_calls_per_24h - len(recent_success_times)
        if budget <= 0:
            sleep_seconds = seconds_until_budget_refresh(recent_success_times)
            LOGGER.info(
                "Rolling 24h successful-call budget exhausted (%s/%s). Sleeping %.0f seconds.",
                len(recent_success_times),
                args.max_calls_per_24h,
                sleep_seconds,
            )
            if args.once:
                print(json.dumps(summary, indent=2, sort_keys=True))
                return 0
            time.sleep(max(60.0, sleep_seconds))
            continue

        item = pending[0]
        request_ticker = normalize_ticker_for_alphavantage(item["ticker"])
        LOGGER.info(
            "Attempting next Alpha Vantage request: success-budget remaining=%s, pending=%s, scope=%s, reverse=%s, target=%s (request=%s) %s",
            budget,
            len(pending),
            universe_source,
            args.reverse,
            item["ticker"],
            request_ticker,
            item["year"],
        )
        raw_path = Path(item["raw_path"])
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            payload, metadata = fetch_news_sentiment(
                api_key=api_key,
                symbol=request_ticker,
                time_from=item["time_from"],
                time_to=item["time_to"],
                limit=args.limit,
                sort=args.sort,
                timeout_seconds=args.request_timeout_seconds,
                user_agent=config.user_agent,
            )
            write_json_atomic(payload, raw_path)
            append_jsonl(
                DEFAULT_LEDGER_JSONL,
                {
                    **metadata,
                    "ticker": item["ticker"],
                    "request_ticker": request_ticker,
                    "raw_path": str(raw_path),
                    "success": True,
                    "likely_truncated": len(payload.get("feed", [])) >= args.limit,
                },
            )
            LOGGER.info(
                "Downloaded %s feed rows for %s window %s -> %s",
                len(payload.get("feed", [])),
                item["ticker"],
                item["time_from"],
                item["time_to"],
            )
            if args.once:
                refreshed_pending = build_pending_requests(tickers=active_tickers, windows=windows)
                refreshed = build_progress_summary(
                    bucket_label=config.bucket_label,
                    bucket_slug=config.bucket_slug,
                    universe_source=universe_source,
                    tickers=active_tickers,
                    windows=windows,
                    pending_requests=refreshed_pending,
                    limit=args.limit,
                    max_calls_per_24h=args.max_calls_per_24h,
                    reverse=args.reverse,
                    include_expanded=args.include_expanded,
                    expanded_only=args.expanded_only,
                    expanded_count=len(config.expanded_tickers),
                )
                write_json_atomic(refreshed, summary_path_for(config.bucket_slug, args.reverse, args.include_expanded, args.expanded_only))
                print(json.dumps(refreshed, indent=2, sort_keys=True))
                return 0
            time.sleep(max(1.0, float(args.min_spacing_seconds)))
            continue
        except AlphaVantageRateLimitError as exc:
            append_jsonl(
                DEFAULT_LEDGER_JSONL,
                build_error_record(item=item, request_ticker=request_ticker, sort=args.sort, limit=args.limit, raw_path=raw_path, error_message=str(exc)),
            )
            rate_limit_kind = classify_rate_limit_message(str(exc))
            if rate_limit_kind == "daily":
                sleep_seconds = max(60.0, float(args.daily_limit_sleep_seconds))
                LOGGER.warning(
                    "Alpha Vantage signaled a daily limit for %s (request=%s) %s. Sleeping %.0f seconds.",
                    item["ticker"],
                    request_ticker,
                    item["year"],
                    sleep_seconds,
                )
            else:
                sleep_seconds = max(60.0, float(args.rate_limit_sleep_seconds))
                LOGGER.warning(
                    "Alpha Vantage signaled a burst/rate limit for %s (request=%s) %s. Sleeping %.0f seconds.",
                    item["ticker"],
                    request_ticker,
                    item["year"],
                    sleep_seconds,
                )
            if args.once:
                return 0
            time.sleep(sleep_seconds)
            continue
        except AlphaVantageClientError as exc:
            append_jsonl(
                DEFAULT_LEDGER_JSONL,
                build_error_record(item=item, request_ticker=request_ticker, sort=args.sort, limit=args.limit, raw_path=raw_path, error_message=str(exc)),
            )
            LOGGER.warning(
                "Alpha Vantage request failed for %s (request=%s) (%s -> %s): %s",
                item["ticker"],
                request_ticker,
                item["time_from"],
                item["time_to"],
                exc,
            )
            if args.once:
                return 0
            time.sleep(max(60.0, float(args.error_sleep_seconds)))
            continue


def build_argument_parser(config: BucketConfig) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=config.script_description)
    parser.add_argument("--start-year", type=int, default=2010)
    parser.add_argument("--end-year", type=int, default=datetime.now(UTC).year)
    parser.add_argument("--max-calls-per-24h", type=int, default=25)
    parser.add_argument("--min-spacing-seconds", type=float, default=20.0)
    parser.add_argument("--idle-sleep-seconds", type=float, default=1800.0)
    parser.add_argument("--rate-limit-sleep-seconds", type=float, default=120.0)
    parser.add_argument("--daily-limit-sleep-seconds", type=float, default=86460.0)
    parser.add_argument("--error-sleep-seconds", type=float, default=900.0)
    parser.add_argument("--request-timeout-seconds", type=int, default=60)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--sort", default="LATEST")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--reverse", action="store_true")
    if config.expanded_tickers:
        parser.add_argument("--include-expanded", action="store_true")
        parser.add_argument("--expanded-only", action="store_true")
    else:
        parser.set_defaults(include_expanded=False, expanded_only=False)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--migrate-only", action="store_true")
    parser.add_argument("--skip-seed-migration", action="store_true")
    parser.add_argument("--log-level", default="INFO")
    return parser


def resolve_active_tickers(config: BucketConfig, args: argparse.Namespace) -> tuple[list[str], str]:
    base = list(config.base_tickers)
    if not config.expanded_tickers:
        if args.reverse:
            base.reverse()
        return base, config.bucket_label

    expanded = list(config.expanded_tickers)
    if args.expanded_only:
        active = expanded
        source = f"{config.bucket_label}+expanded_only"
    elif args.include_expanded:
        active = base + expanded
        source = f"{config.bucket_label}+expanded"
    else:
        active = base
        source = config.bucket_label
    if args.reverse:
        active.reverse()
    return active, source


def configure_logging(*, log_level: str, log_path: Path) -> None:
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def ensure_runtime_directories() -> None:
    for directory in (RAW_UNIVERSE_DIR, RAW_ALPHAVANTAGE_DIR, RUN_LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def migrate_seed_data() -> None:
    if not ARCHIVE_ROOT.exists():
        LOGGER.info("No archived snapshot found at %s; skipping seed migration.", ARCHIVE_ROOT)
        return
    copy_seed_tree(source_dir=ARCHIVE_ROOT / "data" / "raw" / "universe", destination_dir=RAW_UNIVERSE_DIR)
    copy_seed_tree(source_dir=ARCHIVE_ROOT / "data" / "raw" / "alphavantage", destination_dir=RAW_ALPHAVANTAGE_DIR)
    ensure_current_year_aliases(raw_provider_dir=RAW_ALPHAVANTAGE_DIR, current_year=datetime.now(UTC).year)


def copy_seed_tree(*, source_dir: Path, destination_dir: Path) -> None:
    if not source_dir.exists():
        return
    for source_path in source_dir.rglob("*"):
        relative = source_path.relative_to(source_dir)
        destination_path = destination_dir / relative
        if source_path.is_dir():
            destination_path.mkdir(parents=True, exist_ok=True)
            continue
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        if destination_path.exists():
            continue
        shutil.copy2(source_path, destination_path)


def ensure_current_year_aliases(*, raw_provider_dir: Path, current_year: int) -> None:
    if not raw_provider_dir.exists():
        return
    prefix = f"news_sentiment__{current_year}-01-01__"
    alias_name = f"news_sentiment__{current_year}-01-01__current.json"
    for ticker_dir in raw_provider_dir.iterdir():
        if not ticker_dir.is_dir():
            continue
        alias_path = ticker_dir / alias_name
        if alias_path.exists():
            continue
        candidates = sorted(path for path in ticker_dir.glob(f"{prefix}*.json") if path.name != alias_name)
        if not candidates:
            continue
        shutil.copy2(candidates[-1], alias_path)


def load_api_key(env_path: Path, *, explicit_api_key: str | None = None, fallback_api_key: str = "") -> str:
    if explicit_api_key and explicit_api_key.strip():
        return explicit_api_key.strip()
    if "ALPHAVANTAGE_API_KEY" not in os.environ and env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY", "").strip() or fallback_api_key.strip()
    if not api_key:
        raise RuntimeError("Missing ALPHAVANTAGE_API_KEY. Set --api-key, .env, environment variable, or FALLBACK_API_KEY.")
    return api_key


def build_year_windows(*, start_year: int, end_year: int) -> list[YearWindow]:
    now = datetime.now(UTC)
    windows: list[YearWindow] = []
    for year in range(end_year, start_year - 1, -1):
        time_from = f"{year}0101T0000"
        if year == now.year:
            time_to = now.strftime("%Y%m%dT%H%M")
            file_end = "current"
            is_current_year = True
        else:
            time_to = f"{year}1231T2359"
            file_end = f"{year}-12-31"
            is_current_year = False
        windows.append(YearWindow(year, time_from, time_to, f"{year}-01-01", file_end, is_current_year))
    return windows


def raw_news_path(*, ticker: str, window: YearWindow) -> Path:
    return RAW_ALPHAVANTAGE_DIR / ticker / f"news_sentiment__{window.file_start}__{window.file_end}.json"


def build_pending_requests(*, tickers: Sequence[str], windows: list[YearWindow]) -> list[dict[str, Any]]:
    planned_requests: list[dict[str, Any]] = []
    for ticker in tickers:
        for window in windows:
            raw_path = raw_news_path(ticker=ticker, window=window)
            if raw_path.exists():
                continue
            planned_requests.append(
                {
                    "ticker": ticker,
                    "year": window.year,
                    "time_from": window.time_from,
                    "time_to": window.time_to,
                    "raw_path": str(raw_path),
                    "is_current_year": window.is_current_year,
                }
            )
    return planned_requests


def build_progress_summary(
    *,
    bucket_label: str,
    bucket_slug: str,
    universe_source: str,
    tickers: Sequence[str],
    windows: list[YearWindow],
    pending_requests: list[dict[str, Any]],
    limit: int,
    max_calls_per_24h: int,
    reverse: bool,
    include_expanded: bool,
    expanded_only: bool,
    expanded_count: int,
) -> dict[str, Any]:
    recent_attempt_times = load_recent_request_times(DEFAULT_LEDGER_JSONL, within_hours=24)
    recent_success_times = load_recent_success_times(DEFAULT_LEDGER_JSONL, within_hours=24)
    return {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "bucket_label": bucket_label,
        "bucket_slug": bucket_slug,
        "universe_source": universe_source,
        "reverse": reverse,
        "include_expanded": include_expanded,
        "expanded_only": expanded_only,
        "expanded_ticker_count": expanded_count,
        "ticker_count": len(tickers),
        "start_year": windows[-1].year if windows else None,
        "end_year": windows[0].year if windows else None,
        "limit": limit,
        "planned_request_count_total": len(tickers) * len(windows),
        "completed_request_count": len(tickers) * len(windows) - len(pending_requests),
        "pending_request_count": len(pending_requests),
        "max_successful_calls_per_24h": max_calls_per_24h,
        "successful_calls_logged_in_last_24h": len(recent_success_times),
        "attempts_logged_in_last_24h": len(recent_attempt_times),
        "next_pending_requests_preview": pending_requests[:10],
    }


def load_recent_request_times(ledger_path: Path, *, within_hours: int, success_only: bool = False) -> list[datetime]:
    if not ledger_path.exists():
        return []
    cutoff = datetime.now(UTC) - timedelta(hours=within_hours)
    timestamps: list[datetime] = []
    with ledger_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            raw_time = record.get("requested_at_utc")
            if not isinstance(raw_time, str):
                continue
            if success_only and record.get("success") is not True:
                continue
            try:
                timestamp = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            except ValueError:
                continue
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
            timestamp = timestamp.astimezone(UTC)
            if timestamp >= cutoff:
                timestamps.append(timestamp)
    timestamps.sort()
    return timestamps


def load_recent_success_times(ledger_path: Path, *, within_hours: int) -> list[datetime]:
    return load_recent_request_times(ledger_path, within_hours=within_hours, success_only=True)


def seconds_until_budget_refresh(recent_call_times: list[datetime]) -> float:
    if not recent_call_times:
        return 0.0
    oldest = recent_call_times[0]
    eligible = oldest + timedelta(hours=24, minutes=1)
    return max(0.0, (eligible - datetime.now(UTC)).total_seconds())


def fetch_news_sentiment(
    *,
    api_key: str,
    symbol: str,
    time_from: str,
    time_to: str,
    limit: int,
    sort: str,
    timeout_seconds: int,
    user_agent: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": symbol,
        "time_from": time_from,
        "time_to": time_to,
        "sort": sort,
        "limit": limit,
        "apikey": api_key,
    }
    query_url = f"https://www.alphavantage.co/query?{urlencode(params)}"
    request = Request(query_url, headers={"User-Agent": user_agent})
    requested_at = datetime.now(UTC)
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
            response_status = response.status
            response_headers = dict(response.headers.items())
            response_url = response.geturl()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise AlphaVantageClientError(f"HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise AlphaVantageClientError(f"Network error: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise AlphaVantageClientError(f"Invalid JSON response: {exc}") from exc

    if not isinstance(payload, dict):
        raise AlphaVantageClientError("Expected Alpha Vantage NEWS_SENTIMENT payload to be a JSON object.")
    if payload.get("Note"):
        raise AlphaVantageRateLimitError(str(payload["Note"]))
    if payload.get("Information"):
        info_message = str(payload["Information"])
        if is_rate_limit_message(info_message):
            raise AlphaVantageRateLimitError(info_message)
        raise AlphaVantageClientError(info_message)
    if payload.get("Error Message"):
        raise AlphaVantageClientError(str(payload["Error Message"]))
    feed = payload.get("feed", [])
    if not isinstance(feed, list):
        raise AlphaVantageClientError("Expected Alpha Vantage 'feed' field to be a list.")

    metadata = {
        "request_id": f"NEWS_SENTIMENT:{symbol}:{requested_at.isoformat()}",
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "ticker": symbol,
        "request_ticker": symbol,
        "requested_at_utc": requested_at.isoformat(),
        "time_from": time_from,
        "time_to": time_to,
        "sort": sort,
        "limit": limit,
        "result_count": len(feed),
        "response_status": response_status,
        "request_url": response_url,
        "response_headers": response_headers,
    }
    return payload, metadata


def build_error_record(*, item: dict[str, Any], request_ticker: str, sort: str, limit: int, raw_path: Path, error_message: str) -> dict[str, Any]:
    return {
        "request_id": f"NEWS_SENTIMENT:{item['ticker']}:{datetime.now(UTC).isoformat()}",
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "ticker": item["ticker"],
        "request_ticker": request_ticker,
        "requested_at_utc": datetime.now(UTC).isoformat(),
        "time_from": item["time_from"],
        "time_to": item["time_to"],
        "sort": sort,
        "limit": limit,
        "raw_path": str(raw_path),
        "success": False,
        "result_count": None,
        "response_status": None,
        "request_url": None,
        "error_message": error_message,
        "likely_truncated": None,
    }


def append_jsonl(file_path: Path, record: dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def write_json_atomic(payload: Any, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(file_path)


def summary_path_for(bucket_slug: str, reverse: bool, include_expanded: bool, expanded_only: bool) -> Path:
    mode = "reverse" if reverse else "forward"
    suffix = "expanded_only" if expanded_only else "with_expanded" if include_expanded else "base_only"
    return RAW_ALPHAVANTAGE_DIR / f"daemon_summary_{bucket_slug}_{mode}_{suffix}.json"


def log_path_for(bucket_slug: str, reverse: bool, include_expanded: bool, expanded_only: bool) -> Path:
    mode = "reverse" if reverse else "forward"
    suffix = "expanded_only" if expanded_only else "with_expanded" if include_expanded else "base_only"
    return RUN_LOG_DIR / f"alphavantage_news_{bucket_slug}_{mode}_{suffix}.log"


def classify_rate_limit_message(message: str) -> str:
    lowered = message.lower()
    burst_markers = (
        "1 request per second",
        "spreading out your free api requests more sparingly",
        "per-second burst limit",
    )
    daily_markers = (
        "25 requests per day",
        "requests per day",
        "standard api rate limit is 25 requests per day",
    )
    if any(marker in lowered for marker in burst_markers):
        return "burst"
    if any(marker in lowered for marker in daily_markers):
        return "daily"
    return "other"


def is_rate_limit_message(message: str) -> bool:
    return classify_rate_limit_message(message) in {"daily", "burst"}


def normalize_ticker_for_alphavantage(ticker: str) -> str:
    return ticker.replace(".", "-")
