"""Standalone Alpha Vantage NEWS_SENTIMENT truncation-refinement downloader.

This file is intentionally self-contained: copy just this script to another
machine, provide an Alpha Vantage API key, and run it with standard-library
Python. It embeds the Stage 1 likely-truncated top-50 window list and refines
those windows at quarterly granularity first, then at monthly granularity for
any quarter that still returns the provider limit.
"""

from __future__ import annotations

import argparse
import calendar
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


LOGGER = logging.getLogger("alphavantage_news_truncation_refinement_standalone")
USER_AGENT = "EventStateForecastingAlphaVantageTruncationRefinementStandalone/1.0"
DEFAULT_LIMIT = 1000
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_OUTPUT_ROOT = SCRIPT_PATH.parent.parent if SCRIPT_PATH.parent.name == "scripts" else SCRIPT_PATH.parent

EMBEDDED_LIKELY_TRUNCATED_WINDOW_IDS: tuple[str, ...] = (
    "NVDA:2024:1000",
    "NVDA:2025:1000",
    "NVDA:2026_current:1000",
    "AAPL:2025:1000",
    "AAPL:2026_current:1000",
    "MSFT:2021:1000",
    "MSFT:2022:1000",
    "MSFT:2024:1000",
    "MSFT:2025:1000",
    "MSFT:2026_current:1000",
    "AMZN:2021:1000",
    "AMZN:2022:1000",
    "AMZN:2025:1000",
    "AMZN:2026_current:1000",
    "GOOGL:2025:1000",
    "GOOGL:2026_current:1000",
    "GOOG:2025:1000",
    "GOOG:2026_current:1000",
    "AVGO:2025:1000",
    "AVGO:2026_current:1000",
    "META:2025:1000",
    "META:2026_current:1000",
    "TSLA:2025:1000",
    "TSLA:2026_current:1000",
    "WMT:2025:1000",
    "WMT:2026_current:1000",
    "LLY:2025:1000",
    "LLY:2026_current:1000",
    "JPM:2021:1000",
    "JPM:2022:1000",
    "JPM:2025:1000",
    "JPM:2026_current:1000",
    "XOM:2025:1000",
    "XOM:2026_current:1000",
    "V:2025:1000",
    "V:2026_current:1000",
    "JNJ:2025:1000",
    "JNJ:2026_current:1000",
    "MU:2025:1000",
    "MU:2026_current:1000",
    "COST:2025:1000",
    "COST:2026_current:1000",
    "MA:2026_current:1000",
    "NFLX:2025:1000",
    "NFLX:2026_current:1000",
    "ORCL:2025:1000",
    "ORCL:2026_current:1000",
    "AMD:2025:1000",
    "AMD:2026_current:1000",
    "CVX:2025:1000",
    "CVX:2026_current:1000",
    "BAC:2025:1000",
    "BAC:2026_current:1000",
    "ABBV:2026_current:1000",
    "CAT:2025:1000",
    "CAT:2026_current:1000",
    "PG:2025:1000",
    "PG:2026_current:1000",
    "HD:2025:1000",
    "HD:2026_current:1000",
    "KO:2025:1000",
    "KO:2026_current:1000",
    "CSCO:2025:1000",
    "CSCO:2026_current:1000",
    "GE:2025:1000",
    "GE:2026_current:1000",
    "LRCX:2026_current:1000",
    "AMAT:2025:1000",
    "AMAT:2026_current:1000",
    "PLTR:2025:1000",
    "PLTR:2026_current:1000",
    "INTC:2025:1000",
    "INTC:2026_current:1000",
    "MRK:2025:1000",
    "MRK:2026_current:1000",
    "MS:2025:1000",
    "MS:2026_current:1000",
    "UNH:2025:1000",
    "UNH:2026_current:1000",
    "RTX:2025:1000",
    "RTX:2026_current:1000",
    "GS:2025:1000",
    "GS:2026_current:1000",
    "WFC:2025:1000",
    "WFC:2026_current:1000",
    "IBM:2025:1000",
    "IBM:2026_current:1000",
    "MCD:2025:1000",
    "MCD:2026_current:1000",
    "AXP:2025:1000",
    "C:2025:1000",
    "C:2026_current:1000",
)


class AlphaVantageClientError(RuntimeError):
    pass


class AlphaVantageRateLimitError(AlphaVantageClientError):
    pass


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    output_root: Path
    raw_dir: Path
    run_log_dir: Path
    ledger_jsonl: Path
    summary_json: Path
    log_path: Path


@dataclass(frozen=True, slots=True)
class TruncatedSourceWindow:
    ticker: str
    year_label: str
    year: int
    is_current_year_window: bool
    source_feed_count: int
    source_window_id: str
    source_raw_path: Path


@dataclass(frozen=True, slots=True)
class RefinementRequest:
    interval_kind: str
    ticker: str
    request_ticker: str
    source_window_id: str
    source_raw_path: Path
    year: int
    period_id: str
    parent_period_id: str | None
    time_from: str
    time_to: str
    file_start: str
    file_end: str
    raw_path: Path
    is_current_partial_window: bool


@dataclass(frozen=True, slots=True)
class FileInspection:
    request: RefinementRequest
    exists: bool
    valid: bool
    feed_count: int | None
    likely_truncated: bool
    error: str | None


@dataclass(frozen=True, slots=True)
class RefinementPlan:
    source_label: str
    order: str
    sources: list[TruncatedSourceWindow]
    requests: list[RefinementRequest]
    inspections: list[FileInspection]
    pending_requests: list[RefinementRequest]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Standalone Alpha Vantage truncation-refinement downloader.",
        epilog=(
            "Examples: python run_alphavantage_news_truncation_refinement_standalone.py --plan; "
            "python run_alphavantage_news_truncation_refinement_standalone.py --order reverse --once --api-key YOUR_KEY"
        ),
    )
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root for data/ and runs/ outputs. Defaults to repo root when run from scripts/, otherwise the script directory.",
    )
    parser.add_argument(
        "--manifest",
        default=None,
        help="Optional Stage 1 audit manifest. If omitted, the embedded truncated-window list is used.",
    )
    parser.add_argument("--ticker", action="append", default=[], help="Restrict to a canonical ticker. May be passed more than once.")
    parser.add_argument("--year", action="append", type=int, default=[], help="Restrict to a source year. May be passed more than once.")
    parser.add_argument("--window-id", action="append", default=[], help="Restrict to an exact source window ID such as MSFT:2022:1000.")
    parser.add_argument("--exclude-current", action="store_true", help="Skip 2026_current-style source windows.")
    parser.add_argument("--redownload-invalid", action="store_true", help="Replace existing files that fail local JSON/feed validation.")
    parser.add_argument("--max-calls-per-24h", type=int, default=25, help="Local successful-call budget guard. Default: 25.")
    parser.add_argument("--min-spacing-seconds", type=float, default=20.0, help="Minimum delay after a successful download in continuous mode.")
    parser.add_argument("--rate-limit-sleep-seconds", type=float, default=120.0)
    parser.add_argument("--daily-limit-sleep-seconds", type=float, default=86460.0)
    parser.add_argument("--error-sleep-seconds", type=float, default=900.0)
    parser.add_argument("--request-timeout-seconds", type=int, default=60)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Alpha Vantage response limit used for truncation detection. Default: 1000.")
    parser.add_argument("--sort", default="LATEST")
    parser.add_argument("--api-key", default=None, help="Alpha Vantage API key. Can also use ALPHAVANTAGE_API_KEY or .env.")
    parser.add_argument("--order", choices=("forward", "reverse"), default="forward", help="Execution order. Use reverse for last-entry-to-first execution.")
    parser.add_argument("--reverse", action="store_true", help="Alias for --order reverse.")
    parser.add_argument("--once", action="store_true", help="Attempt at most one pending download, then exit.")
    parser.add_argument("--plan", action="store_true", help="Print/write the current plan without downloading.")
    parser.add_argument("--json", action="store_true", help="Print full summary JSON instead of compact text.")
    parser.add_argument("--log-level", default="INFO")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    paths = build_runtime_paths(args.output_root)
    configure_logging(log_level=args.log_level, log_path=paths.log_path)
    ensure_runtime_directories(paths)

    while True:
        plan = build_refinement_plan(paths=paths, args=args, now=datetime.now(UTC))
        summary = build_progress_summary(paths=paths, plan=plan, limit=args.limit, max_calls_per_24h=args.max_calls_per_24h)
        write_json_atomic(summary, paths.summary_json)
        LOGGER.info(
            "Refinement scan: source=%s sources=%s pending=%s order=%s budget_remaining=%s/%s",
            summary["source_label"],
            summary["source_truncated_window_count"],
            summary["pending_request_count"],
            summary["order"],
            summary["successful_call_budget_remaining"],
            summary["max_successful_calls_per_24h"],
        )

        if args.plan:
            print_summary(summary, as_json=args.json)
            return 0

        if not plan.pending_requests:
            LOGGER.info("No pending truncation-refinement downloads remain.")
            print_summary(summary, as_json=args.json)
            return 0

        recent_success_times = load_recent_request_times(paths.ledger_jsonl, within_hours=24, success_only=True)
        budget = args.max_calls_per_24h - len(recent_success_times)
        if budget <= 0:
            sleep_seconds = seconds_until_budget_refresh(recent_success_times)
            LOGGER.info(
                "Rolling 24h successful-call budget exhausted (%s/%s). Sleeping %.0f seconds.",
                len(recent_success_times),
                args.max_calls_per_24h,
                sleep_seconds,
            )
            print_summary(summary, as_json=args.json)
            if args.once:
                return 0
            time.sleep(max(60.0, sleep_seconds))
            continue

        api_key = load_api_key(output_root=paths.output_root, explicit_api_key=args.api_key)
        request = plan.pending_requests[0]
        LOGGER.info(
            "Attempting %s request: budget=%s pending=%s order=%s target=%s %s parent=%s",
            request.interval_kind,
            budget,
            len(plan.pending_requests),
            effective_order(args),
            request.ticker,
            request.period_id,
            request.parent_period_id or request.source_window_id,
        )

        try:
            downloaded = download_and_verify_request(request=request, paths=paths, api_key=api_key, args=args)
            LOGGER.info(
                "Downloaded and verified %s rows for %s %s -> %s",
                downloaded["result_count"],
                request.ticker,
                request.period_id,
                request.raw_path,
            )
            refreshed_plan = build_refinement_plan(paths=paths, args=args, now=datetime.now(UTC))
            refreshed = build_progress_summary(
                paths=paths,
                plan=refreshed_plan,
                limit=args.limit,
                max_calls_per_24h=args.max_calls_per_24h,
                last_download=downloaded,
            )
            write_json_atomic(refreshed, paths.summary_json)
            if args.once:
                print_summary(refreshed, as_json=args.json)
                return 0
            time.sleep(max(1.0, float(args.min_spacing_seconds)))
        except AlphaVantageRateLimitError as exc:
            append_jsonl(paths.ledger_jsonl, build_error_record(request=request, sort=args.sort, limit=args.limit, error_message=str(exc)))
            sleep_seconds = sleep_seconds_for_rate_limit(str(exc), args)
            LOGGER.warning("Alpha Vantage rate limit for %s %s. Sleeping %.0f seconds.", request.ticker, request.period_id, sleep_seconds)
            if args.once:
                print_summary(summary, as_json=args.json)
                return 0
            time.sleep(sleep_seconds)
        except AlphaVantageClientError as exc:
            append_jsonl(paths.ledger_jsonl, build_error_record(request=request, sort=args.sort, limit=args.limit, error_message=str(exc)))
            LOGGER.warning("Alpha Vantage request failed for %s %s: %s", request.ticker, request.period_id, exc)
            if args.once:
                print_summary(summary, as_json=args.json)
                return 0
            time.sleep(max(60.0, float(args.error_sleep_seconds)))


def build_runtime_paths(output_root_value: str) -> RuntimePaths:
    output_root = Path(output_root_value).expanduser().resolve()
    raw_dir = output_root / "data" / "raw" / "alphavantage"
    run_log_dir = output_root / "runs" / "logs"
    return RuntimePaths(
        output_root=output_root,
        raw_dir=raw_dir,
        run_log_dir=run_log_dir,
        ledger_jsonl=raw_dir / "news_request_ledger_truncation_refinement_standalone.jsonl",
        summary_json=raw_dir / "daemon_summary_truncation_refinement_standalone.json",
        log_path=run_log_dir / "alphavantage_news_truncation_refinement_standalone.log",
    )


def configure_logging(*, log_level: str, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()
    logger.setLevel(parse_log_level(log_level, default=logging.INFO))
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_log_level(value: str, *, default: int) -> int:
    candidate = str(value).strip().upper()
    return getattr(logging, candidate, default)


def ensure_runtime_directories(paths: RuntimePaths) -> None:
    paths.raw_dir.mkdir(parents=True, exist_ok=True)
    paths.run_log_dir.mkdir(parents=True, exist_ok=True)


def effective_order(args: argparse.Namespace) -> str:
    return "reverse" if args.reverse or args.order == "reverse" else "forward"


def build_refinement_plan(*, paths: RuntimePaths, args: argparse.Namespace, now: datetime) -> RefinementPlan:
    sources, source_label = load_truncated_sources(
        paths=paths,
        manifest_value=args.manifest,
        ticker_filter={ticker.upper() for ticker in args.ticker},
        year_filter=set(args.year),
        window_id_filter=set(args.window_id),
        include_current=not args.exclude_current,
    )
    requests = build_all_requests(paths=paths, sources=sources, limit=args.limit, now=now)
    order = effective_order(args)
    if order == "reverse":
        requests.reverse()
    inspections = [inspect_request_file(request, limit=args.limit) for request in requests]
    pending = [
        inspection.request
        for inspection in inspections
        if not inspection.exists or (args.redownload_invalid and inspection.exists and not inspection.valid)
    ]
    return RefinementPlan(source_label=source_label, order=order, sources=sources, requests=requests, inspections=inspections, pending_requests=pending)


def load_truncated_sources(
    *,
    paths: RuntimePaths,
    manifest_value: str | None,
    ticker_filter: set[str],
    year_filter: set[int],
    window_id_filter: set[str],
    include_current: bool,
) -> tuple[list[TruncatedSourceWindow], str]:
    raw_ids: Sequence[str]
    if manifest_value:
        manifest_path = Path(manifest_value).expanduser()
        if not manifest_path.is_absolute():
            manifest_path = (Path.cwd() / manifest_path).resolve()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_ids = manifest.get("likely_truncated_window_ids", [])
        if not isinstance(manifest_ids, list):
            raise ValueError("Expected manifest likely_truncated_window_ids to be a list.")
        raw_ids = [str(item) for item in manifest_ids]
        source_label = str(manifest_path)
    else:
        raw_ids = EMBEDDED_LIKELY_TRUNCATED_WINDOW_IDS
        source_label = "embedded_stage1_likely_truncated_top50_windows"

    sources: list[TruncatedSourceWindow] = []
    for raw_id in raw_ids:
        source = parse_truncated_window_id(str(raw_id), paths=paths)
        if ticker_filter and source.ticker.upper() not in ticker_filter:
            continue
        if year_filter and source.year not in year_filter:
            continue
        if window_id_filter and source.source_window_id not in window_id_filter:
            continue
        if source.is_current_year_window and not include_current:
            continue
        sources.append(source)
    return sources, source_label


def parse_truncated_window_id(raw_id: str, *, paths: RuntimePaths) -> TruncatedSourceWindow:
    parts = raw_id.split(":")
    if len(parts) != 3:
        raise ValueError(f"Invalid truncated window ID: {raw_id!r}")
    ticker, year_label, feed_count = parts
    if year_label.endswith("_current"):
        year = int(year_label.removesuffix("_current"))
        is_current = True
        source_file_end = "current"
    else:
        year = int(year_label)
        is_current = False
        source_file_end = f"{year}-12-31"
    source_raw_path = paths.raw_dir / ticker / f"news_sentiment__{year}-01-01__{source_file_end}.json"
    return TruncatedSourceWindow(
        ticker=ticker,
        year_label=year_label,
        year=year,
        is_current_year_window=is_current,
        source_feed_count=int(feed_count),
        source_window_id=raw_id,
        source_raw_path=source_raw_path,
    )


def build_all_requests(*, paths: RuntimePaths, sources: Sequence[TruncatedSourceWindow], limit: int, now: datetime) -> list[RefinementRequest]:
    requests: list[RefinementRequest] = []
    for source in sources:
        for quarterly_request in build_quarterly_requests_for_source(source, paths=paths, now=now):
            requests.append(quarterly_request)
            quarter_inspection = inspect_request_file(quarterly_request, limit=limit)
            if quarter_inspection.valid and quarter_inspection.likely_truncated:
                requests.extend(build_monthly_requests_for_quarter(quarterly_request, paths=paths))
    return requests


def build_quarterly_requests_for_source(source: TruncatedSourceWindow, *, paths: RuntimePaths, now: datetime) -> list[RefinementRequest]:
    requests: list[RefinementRequest] = []
    for quarter_index, start_month in enumerate((1, 4, 7, 10), start=1):
        start = datetime(source.year, start_month, 1, 0, 0, tzinfo=UTC)
        end_month = start_month + 2
        end_day = calendar.monthrange(source.year, end_month)[1]
        quarter_end = datetime(source.year, end_month, end_day, 23, 59, tzinfo=UTC)

        is_active_current_source = source.is_current_year_window and source.year == now.year
        if is_active_current_source:
            if start > now:
                continue
            end = min(quarter_end, now)
        else:
            end = quarter_end
        if end < start:
            continue

        is_current_partial = is_active_current_source and end < quarter_end
        file_start = start.strftime("%Y-%m-%d")
        file_end = "current" if is_current_partial else end.strftime("%Y-%m-%d")
        requests.append(
            RefinementRequest(
                interval_kind="quarterly",
                ticker=source.ticker,
                request_ticker=normalize_ticker_for_alphavantage(source.ticker),
                source_window_id=source.source_window_id,
                source_raw_path=source.source_raw_path,
                year=source.year,
                period_id=f"{source.year}Q{quarter_index}",
                parent_period_id=None,
                time_from=format_alpha_time(start),
                time_to=format_alpha_time(end),
                file_start=file_start,
                file_end=file_end,
                raw_path=paths.raw_dir / source.ticker / f"news_sentiment__{file_start}__{file_end}.json",
                is_current_partial_window=is_current_partial,
            )
        )
    return requests


def build_monthly_requests_for_quarter(quarter: RefinementRequest, *, paths: RuntimePaths) -> list[RefinementRequest]:
    start = parse_alpha_time(quarter.time_from)
    end = parse_alpha_time(quarter.time_to)
    requests: list[RefinementRequest] = []
    month = start.month
    while month <= end.month:
        month_start = datetime(start.year, month, 1, 0, 0, tzinfo=UTC)
        month_end_day = calendar.monthrange(start.year, month)[1]
        month_end = datetime(start.year, month, month_end_day, 23, 59, tzinfo=UTC)
        period_start = max(month_start, start)
        period_end = min(month_end, end)
        if period_end >= period_start:
            is_current_partial = quarter.is_current_partial_window and period_end == end and period_end < month_end
            file_start = period_start.strftime("%Y-%m-%d")
            file_end = "current" if is_current_partial else period_end.strftime("%Y-%m-%d")
            requests.append(
                RefinementRequest(
                    interval_kind="monthly",
                    ticker=quarter.ticker,
                    request_ticker=quarter.request_ticker,
                    source_window_id=quarter.source_window_id,
                    source_raw_path=quarter.source_raw_path,
                    year=quarter.year,
                    period_id=f"{quarter.year}-{month:02d}",
                    parent_period_id=quarter.period_id,
                    time_from=format_alpha_time(period_start),
                    time_to=format_alpha_time(period_end),
                    file_start=file_start,
                    file_end=file_end,
                    raw_path=paths.raw_dir / quarter.ticker / f"news_sentiment__{file_start}__{file_end}.json",
                    is_current_partial_window=is_current_partial,
                )
            )
        month += 1
    return requests


def inspect_request_file(request: RefinementRequest, *, limit: int) -> FileInspection:
    if not request.raw_path.exists():
        return FileInspection(request=request, exists=False, valid=False, feed_count=None, likely_truncated=False, error="missing")
    try:
        payload = json.loads(request.raw_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return FileInspection(request=request, exists=True, valid=False, feed_count=None, likely_truncated=False, error=str(exc))
    if not isinstance(payload, dict):
        return FileInspection(request=request, exists=True, valid=False, feed_count=None, likely_truncated=False, error="payload_not_object")
    if payload.get("Note") or payload.get("Information") or payload.get("Error Message"):
        return FileInspection(request=request, exists=True, valid=False, feed_count=None, likely_truncated=False, error="provider_message_payload")
    feed = payload.get("feed")
    if not isinstance(feed, list):
        return FileInspection(request=request, exists=True, valid=False, feed_count=None, likely_truncated=False, error="feed_not_list")
    return FileInspection(request=request, exists=True, valid=True, feed_count=len(feed), likely_truncated=len(feed) >= limit, error=None)


def download_and_verify_request(*, request: RefinementRequest, paths: RuntimePaths, api_key: str, args: argparse.Namespace) -> dict[str, Any]:
    payload, metadata = fetch_news_sentiment(
        api_key=api_key,
        symbol=request.request_ticker,
        time_from=request.time_from,
        time_to=request.time_to,
        limit=args.limit,
        sort=args.sort,
        timeout_seconds=args.request_timeout_seconds,
        user_agent=USER_AGENT,
    )
    write_json_atomic(payload, request.raw_path)
    inspection = inspect_request_file(request, limit=args.limit)
    if not inspection.valid:
        raise AlphaVantageClientError(f"Downloaded file failed verification: {inspection.error}")
    record = build_success_record(metadata=metadata, inspection=inspection, limit=args.limit)
    append_jsonl(paths.ledger_jsonl, record)
    return record


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


def build_progress_summary(
    *,
    paths: RuntimePaths,
    plan: RefinementPlan,
    limit: int,
    max_calls_per_24h: int,
    last_download: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recent_attempt_times = load_recent_request_times(paths.ledger_jsonl, within_hours=24, success_only=False)
    recent_success_times = load_recent_request_times(paths.ledger_jsonl, within_hours=24, success_only=True)
    quarterly = [inspection for inspection in plan.inspections if inspection.request.interval_kind == "quarterly"]
    monthly = [inspection for inspection in plan.inspections if inspection.request.interval_kind == "monthly"]
    pending_quarterly = [request for request in plan.pending_requests if request.interval_kind == "quarterly"]
    pending_monthly = [request for request in plan.pending_requests if request.interval_kind == "monthly"]
    missing_sources = [source for source in plan.sources if not source.source_raw_path.exists()]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "script_name": SCRIPT_PATH.name,
        "source_label": plan.source_label,
        "order": plan.order,
        "refinement_mode": "standalone_quarterly_then_monthly_truncated_window_refinement",
        "output_root": str(paths.output_root),
        "raw_dir": str(paths.raw_dir),
        "source_truncated_window_count": len(plan.sources),
        "source_missing_raw_file_count": len(missing_sources),
        "limit": limit,
        "max_successful_calls_per_24h": max_calls_per_24h,
        "successful_calls_logged_in_last_24h": len(recent_success_times),
        "attempts_logged_in_last_24h": len(recent_attempt_times),
        "successful_call_budget_remaining": max(0, max_calls_per_24h - len(recent_success_times)),
        "planned_request_count_total": len(plan.requests),
        "pending_request_count": len(plan.pending_requests),
        "quarterly": interval_summary(quarterly, pending_quarterly),
        "monthly": interval_summary(monthly, pending_monthly),
        "source_missing_raw_files": [source_to_summary(source) for source in missing_sources[:50]],
        "truncated_quarterly_files": [inspection_to_summary(item) for item in quarterly if item.valid and item.likely_truncated][:50],
        "truncated_monthly_files": [inspection_to_summary(item) for item in monthly if item.valid and item.likely_truncated][:50],
        "invalid_existing_files": [inspection_to_summary(item) for item in plan.inspections if item.exists and not item.valid][:50],
        "next_pending_requests_preview": [request_to_summary(request) for request in plan.pending_requests[:10]],
        "ledger_path": str(paths.ledger_jsonl),
        "summary_path": str(paths.summary_json),
        "log_path": str(paths.log_path),
        "last_download": last_download,
        "non_claims": [
            "standalone_truncation_refinement_raw_downloads_are_not_dataset_readiness",
            "standalone_truncation_refinement_raw_downloads_do_not_select_a_clean_window",
            "standalone_truncation_refinement_raw_downloads_do_not_create_features_labels_or_benchmark_results",
        ],
    }
    summary["completed_request_count"] = summary["quarterly"]["valid_existing_count"] + summary["monthly"]["valid_existing_count"]
    summary["blocked_invalid_existing_count"] = summary["quarterly"]["invalid_existing_count"] + summary["monthly"]["invalid_existing_count"]
    return summary


def interval_summary(inspections: Sequence[FileInspection], pending: Sequence[RefinementRequest]) -> dict[str, Any]:
    valid_existing = [item for item in inspections if item.exists and item.valid]
    invalid_existing = [item for item in inspections if item.exists and not item.valid]
    truncated = [item for item in valid_existing if item.likely_truncated]
    missing = [item for item in inspections if not item.exists]
    return {
        "planned_request_count": len(inspections),
        "valid_existing_count": len(valid_existing),
        "missing_count": len(missing),
        "invalid_existing_count": len(invalid_existing),
        "truncated_existing_count": len(truncated),
        "pending_download_count": len(pending),
        "verified_feed_rows": sum(item.feed_count or 0 for item in valid_existing),
        "missing_by_ticker": count_by_ticker(item.request for item in missing),
        "truncated_by_ticker": count_by_ticker(item.request for item in truncated),
        "pending_by_ticker": count_by_ticker(pending),
    }


def count_by_ticker(requests: Sequence[RefinementRequest]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for request in requests:
        counts[request.ticker] = counts.get(request.ticker, 0) + 1
    return dict(sorted(counts.items()))


def source_to_summary(source: TruncatedSourceWindow) -> dict[str, Any]:
    return {
        "ticker": source.ticker,
        "year_label": source.year_label,
        "source_window_id": source.source_window_id,
        "source_feed_count": source.source_feed_count,
        "source_raw_path": str(source.source_raw_path),
        "source_raw_exists": source.source_raw_path.exists(),
    }


def request_to_summary(request: RefinementRequest) -> dict[str, Any]:
    return {
        "interval_kind": request.interval_kind,
        "ticker": request.ticker,
        "request_ticker": request.request_ticker,
        "source_window_id": request.source_window_id,
        "period_id": request.period_id,
        "parent_period_id": request.parent_period_id,
        "time_from": request.time_from,
        "time_to": request.time_to,
        "raw_path": str(request.raw_path),
        "is_current_partial_window": request.is_current_partial_window,
    }


def inspection_to_summary(inspection: FileInspection) -> dict[str, Any]:
    payload = request_to_summary(inspection.request)
    payload.update(
        {
            "exists": inspection.exists,
            "valid": inspection.valid,
            "feed_count": inspection.feed_count,
            "likely_truncated": inspection.likely_truncated,
            "error": inspection.error,
        }
    )
    return payload


def build_success_record(*, metadata: dict[str, Any], inspection: FileInspection, limit: int) -> dict[str, Any]:
    request = inspection.request
    safe_metadata = dict(metadata)
    if isinstance(safe_metadata.get("request_url"), str):
        safe_metadata["request_url"] = redact_api_key_in_url(safe_metadata["request_url"])
        safe_metadata["request_url_redacted"] = True
    safe_metadata.update(
        {
            "ticker": request.ticker,
            "request_ticker": request.request_ticker,
            "raw_path": str(request.raw_path),
            "success": True,
            "result_count": inspection.feed_count,
            "likely_truncated": bool(inspection.feed_count is not None and inspection.feed_count >= limit),
            "refinement_mode": "standalone_truncated_window_refinement",
            "interval_kind": request.interval_kind,
            "source_window_id": request.source_window_id,
            "source_raw_path": str(request.source_raw_path),
            "period_id": request.period_id,
            "parent_period_id": request.parent_period_id,
            "file_start": request.file_start,
            "file_end": request.file_end,
            "is_current_partial_window": request.is_current_partial_window,
            "local_verification": "passed",
        }
    )
    return safe_metadata


def build_error_record(*, request: RefinementRequest, sort: str, limit: int, error_message: str) -> dict[str, Any]:
    return {
        "request_id": f"NEWS_SENTIMENT:{request.ticker}:{request.period_id}:{datetime.now(UTC).isoformat()}",
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "ticker": request.ticker,
        "request_ticker": request.request_ticker,
        "requested_at_utc": datetime.now(UTC).isoformat(),
        "time_from": request.time_from,
        "time_to": request.time_to,
        "sort": sort,
        "limit": limit,
        "raw_path": str(request.raw_path),
        "success": False,
        "result_count": None,
        "response_status": None,
        "request_url": None,
        "error_message": error_message,
        "likely_truncated": None,
        "refinement_mode": "standalone_truncated_window_refinement",
        "interval_kind": request.interval_kind,
        "source_window_id": request.source_window_id,
        "source_raw_path": str(request.source_raw_path),
        "period_id": request.period_id,
        "parent_period_id": request.parent_period_id,
    }


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    last = summary.get("last_download") or {}
    if last:
        print(
            "downloaded "
            f"{last.get('ticker')} {last.get('interval_kind')} {last.get('period_id')} "
            f"rows={last.get('result_count')} truncated={last.get('likely_truncated')}"
        )
    print("STANDALONE TRUNCATION REFINEMENT SUMMARY")
    print(f"source: {summary['source_label']}")
    print(f"order: {summary['order']} output_root: {summary['output_root']}")
    print(f"source windows: {summary['source_truncated_window_count']} missing_sources: {summary['source_missing_raw_file_count']}")
    for interval in ("quarterly", "monthly"):
        item = summary[interval]
        print(
            f"{interval}: planned={item['planned_request_count']} "
            f"valid={item['valid_existing_count']} missing={item['missing_count']} "
            f"invalid={item['invalid_existing_count']} truncated={item['truncated_existing_count']} "
            f"pending={item['pending_download_count']}"
        )
        pending_by_ticker = item.get("pending_by_ticker") or {}
        if pending_by_ticker:
            top = sorted(pending_by_ticker.items(), key=lambda pair: (-pair[1], pair[0]))[:10]
            preview = ", ".join(f"{ticker}={count}" for ticker, count in top)
            extra = "" if len(pending_by_ticker) <= 10 else f" (+{len(pending_by_ticker) - 10} more)"
            print(f"{interval} pending_by_ticker: {preview}{extra}")
    print(
        f"successes_last_24h: {summary['successful_calls_logged_in_last_24h']} "
        f"attempts_last_24h: {summary['attempts_logged_in_last_24h']} "
        f"budget_remaining: {summary['successful_call_budget_remaining']}/{summary['max_successful_calls_per_24h']}"
    )
    preview = summary.get("next_pending_requests_preview") or []
    if preview:
        next_item = preview[0]
        print(
            "next: "
            f"{next_item['ticker']} {next_item['interval_kind']} {next_item['period_id']} "
            f"{next_item['time_from']}->{next_item['time_to']}"
        )
    print(f"summary: {summary['summary_path']}")
    print("Use --json for full detail.")


def load_api_key(*, output_root: Path, explicit_api_key: str | None) -> str:
    if explicit_api_key and explicit_api_key.strip():
        return explicit_api_key.strip()
    for env_name in ("ALPHAVANTAGE_API_KEY", "ALPHA_VANTAGE_API_KEY"):
        if os.environ.get(env_name, "").strip():
            return os.environ[env_name].strip()
    for env_path in (output_root / ".env", Path.cwd() / ".env", SCRIPT_PATH.with_name(".env")):
        if not env_path.exists():
            continue
        values = parse_env_file(env_path)
        for env_name in ("ALPHAVANTAGE_API_KEY", "ALPHA_VANTAGE_API_KEY"):
            if values.get(env_name, "").strip():
                return values[env_name].strip()
    raise RuntimeError("Missing Alpha Vantage API key. Use --api-key, ALPHAVANTAGE_API_KEY, ALPHA_VANTAGE_API_KEY, or .env.")


def parse_env_file(env_path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


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


def seconds_until_budget_refresh(recent_call_times: list[datetime]) -> float:
    if not recent_call_times:
        return 0.0
    oldest = recent_call_times[0]
    eligible = oldest + timedelta(hours=24, minutes=1)
    return max(0.0, (eligible - datetime.now(UTC)).total_seconds())


def append_jsonl(file_path: Path, record: dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def write_json_atomic(payload: Any, file_path: Path) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(file_path.suffix + ".tmp")
    temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(file_path)


def redact_api_key_in_url(url: str) -> str:
    parsed = urlsplit(url)
    pairs = parse_qsl(parsed.query, keep_blank_values=True)
    redacted_pairs = [(key, "<redacted>" if key.lower() == "apikey" else value) for key, value in pairs]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(redacted_pairs), parsed.fragment))


def sleep_seconds_for_rate_limit(message: str, args: argparse.Namespace) -> float:
    rate_limit_kind = classify_rate_limit_message(message)
    if rate_limit_kind == "daily":
        return max(60.0, float(args.daily_limit_sleep_seconds))
    return max(60.0, float(args.rate_limit_sleep_seconds))


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


def format_alpha_time(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M")


def parse_alpha_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%dT%H%M").replace(tzinfo=UTC)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
