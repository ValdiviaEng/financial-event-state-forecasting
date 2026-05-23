"""Refine likely truncated Alpha Vantage news windows.

The Stage 1 audit records yearly/current windows that returned the provider
limit. This runner plans quarterly downloads for those windows, validates actual
files on disk, and creates monthly follow-up requests when a quarterly file is
itself truncated.
"""

from __future__ import annotations

import argparse
import calendar
from dataclasses import dataclass
from datetime import UTC, datetime
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from alphavantage_news_bucket_common import (
    AlphaVantageClientError,
    AlphaVantageRateLimitError,
    DEFAULT_LEDGER_JSONL,
    PROJECT_ROOT,
    RAW_ALPHAVANTAGE_DIR,
    RUN_LOG_DIR,
    append_jsonl,
    classify_rate_limit_message,
    fetch_news_sentiment,
    load_api_key,
    load_recent_request_times,
    normalize_ticker_for_alphavantage,
    seconds_until_budget_refresh,
    write_json_atomic,
)


LOGGER = logging.getLogger("alphavantage_news_truncation_refinement")
DEFAULT_STAGE1_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage1_raw_security_coverage_audit_2026-05-12.json"
REFINEMENT_LEDGER_JSONL = RAW_ALPHAVANTAGE_DIR / "news_request_ledger_truncation_refinement.jsonl"
LEGACY_QUARTERLY_LEDGER_JSONL = RAW_ALPHAVANTAGE_DIR / "news_request_ledger_truncation_refinement_quarterly.jsonl"
REFINEMENT_SUMMARY_JSON = RAW_ALPHAVANTAGE_DIR / "daemon_summary_truncation_refinement.json"
LEGACY_QUARTERLY_SUMMARY_JSON = RAW_ALPHAVANTAGE_DIR / "daemon_summary_truncation_refinement_quarterly.json"
REFINEMENT_LOG_PATH = RUN_LOG_DIR / "alphavantage_news_truncation_refinement.log"
USER_AGENT = "EventStateForecastingAlphaVantageTruncationRefinement/1.1"


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
    manifest_path: Path
    sources: list[TruncatedSourceWindow]
    requests: list[RefinementRequest]
    inspections: list[FileInspection]
    pending_requests: list[RefinementRequest]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refine likely truncated Alpha Vantage NEWS_SENTIMENT windows.")
    parser.add_argument("--manifest", default=str(DEFAULT_STAGE1_MANIFEST), help="Stage 1 audit manifest with likely_truncated_window_ids.")
    parser.add_argument("--ticker", action="append", default=[], help="Restrict to a canonical ticker. May be passed more than once.")
    parser.add_argument("--year", action="append", type=int, default=[], help="Restrict to a source year. May be passed more than once.")
    parser.add_argument("--window-id", action="append", default=[], help="Restrict to an exact manifest window ID such as AAPL:2025:1000.")
    parser.add_argument("--exclude-current", action="store_true", help="Skip current-year truncated windows from the manifest.")
    parser.add_argument("--redownload-invalid", action="store_true", help="Replace existing files that fail local JSON/feed validation.")
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
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print full summary JSON to stdout instead of compact text.")
    parser.add_argument(
        "--console-log-level",
        default="INFO",
        help="Console log verbosity (default: INFO, matching the main Alpha Vantage builders).",
    )
    parser.add_argument(
        "--file-log-level",
        default="INFO",
        help="File log verbosity for runs/logs output (default: INFO).",
    )
    parser.add_argument(
        "--log-level",
        default=None,
        help="Legacy option: sets both console and file log level (overrides --console-log-level/--file-log-level).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    if args.log_level:
        console_level = str(args.log_level)
        file_level = str(args.log_level)
    else:
        console_level = str(args.console_log_level)
        file_level = str(args.file_log_level)
    configure_logging(console_level=console_level, file_level=file_level)
    ensure_runtime_directories()

    manifest_path = resolve_project_path(args.manifest)
    plan = build_refinement_plan(manifest_path=manifest_path, args=args, now=datetime.now(UTC))
    summary = build_progress_summary(plan=plan, limit=args.limit, max_calls_per_24h=args.max_calls_per_24h)
    write_summary(summary)
    LOGGER.info(
        "Truncation refinement scan: sources=%s pending=%s quarterly_missing=%s monthly_missing=%s budget_remaining=%s/%s",
        summary["source_truncated_window_count"],
        summary["pending_request_count"],
        summary["quarterly"]["missing_count"],
        summary["monthly"]["missing_count"],
        summary["successful_call_budget_remaining"],
        summary["max_successful_calls_per_24h"],
    )

    if args.plan:
        print_summary(summary, as_json=args.json)
        return 0

    api_key = load_api_key(PROJECT_ROOT / ".env", explicit_api_key=args.api_key)

    while True:
        plan = build_refinement_plan(manifest_path=manifest_path, args=args, now=datetime.now(UTC))
        summary = build_progress_summary(plan=plan, limit=args.limit, max_calls_per_24h=args.max_calls_per_24h)
        write_summary(summary)
        LOGGER.info(
            "Refinement status: pending=%s quarterly_valid=%s monthly_valid=%s budget_remaining=%s/%s",
            summary["pending_request_count"],
            summary["quarterly"]["valid_existing_count"],
            summary["monthly"]["valid_existing_count"],
            summary["successful_call_budget_remaining"],
            summary["max_successful_calls_per_24h"],
        )

        if not plan.pending_requests:
            LOGGER.info("No pending truncation-refinement downloads remain.")
            print_summary(summary, as_json=args.json)
            return 0 if args.once else sleep_and_continue(args.idle_sleep_seconds)

        recent_success_times = combined_recent_request_times(success_only=True)
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
            return 0 if args.once else sleep_and_continue(sleep_seconds)

        request = plan.pending_requests[0]
        LOGGER.info(
            "Attempting %s refinement request: budget=%s pending=%s target=%s %s parent=%s",
            request.interval_kind,
            budget,
            len(plan.pending_requests),
            request.ticker,
            request.period_id,
            request.parent_period_id or request.source_window_id,
        )

        try:
            downloaded = download_and_verify_request(request=request, api_key=api_key, args=args)
            LOGGER.info(
                "Downloaded and verified %s rows for %s %s -> %s",
                downloaded["result_count"],
                request.ticker,
                request.period_id,
                request.raw_path,
            )
            refreshed_plan = build_refinement_plan(manifest_path=manifest_path, args=args, now=datetime.now(UTC))
            refreshed = build_progress_summary(
                plan=refreshed_plan,
                limit=args.limit,
                max_calls_per_24h=args.max_calls_per_24h,
                last_download=downloaded,
            )
            write_summary(refreshed)
            if args.once:
                print_summary(refreshed, as_json=args.json)
                return 0
            time.sleep(max(1.0, float(args.min_spacing_seconds)))
            continue
        except AlphaVantageRateLimitError as exc:
            append_jsonl(REFINEMENT_LEDGER_JSONL, build_error_record(request=request, sort=args.sort, limit=args.limit, error_message=str(exc)))
            sleep_seconds = sleep_seconds_for_rate_limit(str(exc), args)
            LOGGER.warning("Alpha Vantage rate limit for %s %s. Sleeping %.0f seconds.", request.ticker, request.period_id, sleep_seconds)
            if args.once:
                print_summary(summary, as_json=args.json)
                return 0
            time.sleep(sleep_seconds)
            continue
        except AlphaVantageClientError as exc:
            append_jsonl(REFINEMENT_LEDGER_JSONL, build_error_record(request=request, sort=args.sort, limit=args.limit, error_message=str(exc)))
            LOGGER.warning("Alpha Vantage request failed for %s %s: %s", request.ticker, request.period_id, exc)
            if args.once:
                print_summary(summary, as_json=args.json)
                return 0
            time.sleep(max(60.0, float(args.error_sleep_seconds)))
            continue


def configure_logging(*, console_level: str, file_level: str) -> None:
    RUN_LOG_DIR.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger()
    # Let handlers control verbosity; keep root permissive.
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(parse_log_level(console_level, default=logging.WARNING))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(REFINEMENT_LOG_PATH, encoding="utf-8")
    file_handler.setLevel(parse_log_level(file_level, default=logging.INFO))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def parse_log_level(value: str, *, default: int) -> int:
    candidate = str(value).strip().upper()
    return getattr(logging, candidate, default)


def ensure_runtime_directories() -> None:
    for directory in (RAW_ALPHAVANTAGE_DIR, RUN_LOG_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def sleep_and_continue(seconds: float) -> int:
    time.sleep(max(60.0, float(seconds)))
    return 0


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def build_refinement_plan(*, manifest_path: Path, args: argparse.Namespace, now: datetime) -> RefinementPlan:
    sources = load_truncated_sources(
        manifest_path,
        ticker_filter={ticker.upper() for ticker in args.ticker},
        year_filter=set(args.year),
        window_id_filter=set(args.window_id),
        include_current=not args.exclude_current,
    )
    requests = build_all_requests(sources=sources, limit=args.limit, now=now)
    if args.reverse:
        requests.reverse()
    inspections = [inspect_request_file(request, limit=args.limit) for request in requests]
    pending = [
        inspection.request
        for inspection in inspections
        if not inspection.exists or (args.redownload_invalid and inspection.exists and not inspection.valid)
    ]
    return RefinementPlan(manifest_path=manifest_path, sources=sources, requests=requests, inspections=inspections, pending_requests=pending)


def load_truncated_sources(
    manifest_path: Path,
    *,
    ticker_filter: set[str],
    year_filter: set[int],
    window_id_filter: set[str],
    include_current: bool,
) -> list[TruncatedSourceWindow]:
    if not manifest_path.exists():
        raise FileNotFoundError(f"Stage 1 manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_ids = manifest.get("likely_truncated_window_ids", [])
    if not isinstance(raw_ids, list):
        raise ValueError("Expected manifest likely_truncated_window_ids to be a list.")

    sources: list[TruncatedSourceWindow] = []
    for raw_id in raw_ids:
        source = parse_truncated_window_id(str(raw_id))
        if ticker_filter and source.ticker.upper() not in ticker_filter:
            continue
        if year_filter and source.year not in year_filter:
            continue
        if window_id_filter and source.source_window_id not in window_id_filter:
            continue
        if source.is_current_year_window and not include_current:
            continue
        sources.append(source)
    return sources


def parse_truncated_window_id(raw_id: str) -> TruncatedSourceWindow:
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
    source_raw_path = RAW_ALPHAVANTAGE_DIR / ticker / f"news_sentiment__{year}-01-01__{source_file_end}.json"
    return TruncatedSourceWindow(
        ticker=ticker,
        year_label=year_label,
        year=year,
        is_current_year_window=is_current,
        source_feed_count=int(feed_count),
        source_window_id=raw_id,
        source_raw_path=source_raw_path,
    )


def build_all_requests(*, sources: Sequence[TruncatedSourceWindow], limit: int, now: datetime) -> list[RefinementRequest]:
    requests: list[RefinementRequest] = []
    for source in sources:
        for quarterly_request in build_quarterly_requests_for_source(source, now=now):
            requests.append(quarterly_request)
            quarter_inspection = inspect_request_file(quarterly_request, limit=limit)
            if quarter_inspection.valid and quarter_inspection.likely_truncated:
                requests.extend(build_monthly_requests_for_quarter(quarterly_request))
    return requests


def build_quarterly_requests_for_source(source: TruncatedSourceWindow, *, now: datetime) -> list[RefinementRequest]:
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
                raw_path=RAW_ALPHAVANTAGE_DIR / source.ticker / f"news_sentiment__{file_start}__{file_end}.json",
                is_current_partial_window=is_current_partial,
            )
        )
    return requests


def build_monthly_requests_for_quarter(quarter: RefinementRequest) -> list[RefinementRequest]:
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
                    raw_path=RAW_ALPHAVANTAGE_DIR / quarter.ticker / f"news_sentiment__{file_start}__{file_end}.json",
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


def download_and_verify_request(*, request: RefinementRequest, api_key: str, args: argparse.Namespace) -> dict[str, Any]:
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
    append_jsonl(REFINEMENT_LEDGER_JSONL, record)
    return record


def build_progress_summary(
    *,
    plan: RefinementPlan,
    limit: int,
    max_calls_per_24h: int,
    last_download: dict[str, Any] | None = None,
) -> dict[str, Any]:
    recent_attempt_times = combined_recent_request_times(success_only=False)
    recent_success_times = combined_recent_request_times(success_only=True)
    quarterly = [inspection for inspection in plan.inspections if inspection.request.interval_kind == "quarterly"]
    monthly = [inspection for inspection in plan.inspections if inspection.request.interval_kind == "monthly"]
    missing_sources = [source for source in plan.sources if not source.source_raw_path.exists()]
    pending_quarterly = [request for request in plan.pending_requests if request.interval_kind == "quarterly"]
    pending_monthly = [request for request in plan.pending_requests if request.interval_kind == "monthly"]
    summary = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "provider": "alphavantage",
        "endpoint": "NEWS_SENTIMENT",
        "refinement_mode": "quarterly_then_monthly_truncated_window_refinement",
        "source_manifest": str(plan.manifest_path),
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
        "ledger_paths": [str(DEFAULT_LEDGER_JSONL), str(LEGACY_QUARTERLY_LEDGER_JSONL), str(REFINEMENT_LEDGER_JSONL)],
        "summary_paths": [str(LEGACY_QUARTERLY_SUMMARY_JSON), str(REFINEMENT_SUMMARY_JSON)],
        "last_download": last_download,
        "non_claims": [
            "truncation_refinement_raw_downloads_are_not_dataset_readiness",
            "truncation_refinement_raw_downloads_do_not_select_a_clean_window",
            "truncation_refinement_raw_downloads_do_not_create_features_labels_or_benchmark_results",
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


def combined_recent_request_times(*, success_only: bool) -> list[datetime]:
    timestamps: list[datetime] = []
    for ledger_path in (DEFAULT_LEDGER_JSONL, LEGACY_QUARTERLY_LEDGER_JSONL, REFINEMENT_LEDGER_JSONL):
        timestamps.extend(load_recent_request_times(ledger_path, within_hours=24, success_only=success_only))
    timestamps.sort()
    return timestamps


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
            "refinement_mode": "truncated_window_refinement",
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
        "refinement_mode": "truncated_window_refinement",
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
    print("TRUNCATION REFINEMENT SUMMARY")
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

        truncated_by_ticker = item.get("truncated_by_ticker") or {}
        if truncated_by_ticker:
            top = sorted(truncated_by_ticker.items(), key=lambda pair: (-pair[1], pair[0]))[:10]
            preview = ", ".join(f"{ticker}={count}" for ticker, count in top)
            extra = "" if len(truncated_by_ticker) <= 10 else f" (+{len(truncated_by_ticker) - 10} more)"
            print(f"{interval} truncated_by_ticker: {preview}{extra}")
    for label, key in (("truncated quarterly", "truncated_quarterly_files"), ("truncated monthly", "truncated_monthly_files")):
        items = summary.get(key) or []
        if items:
            preview = ", ".join(f"{item['ticker']} {item['period_id']} rows={item['feed_count']}" for item in items[:5])
            extra = "" if len(items) <= 5 else f" (+{len(items) - 5} more)"
            print(f"{label}: {preview}{extra}")
    invalid = summary.get("invalid_existing_files") or []
    if invalid:
        preview = ", ".join(f"{item['ticker']} {item['period_id']} {item['error']}" for item in invalid[:5])
        extra = "" if len(invalid) <= 5 else f" (+{len(invalid) - 5} more)"
        print(f"invalid existing files: {preview}{extra}")
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
    print(f"summary: {summary['summary_paths'][-1]}")
    print("Use --json for full detail.")


def write_summary(summary: dict[str, Any]) -> None:
    write_json_atomic(summary, REFINEMENT_SUMMARY_JSON)
    write_json_atomic(summary, LEGACY_QUARTERLY_SUMMARY_JSON)


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


def format_alpha_time(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M")


def parse_alpha_time(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%dT%H%M").replace(tzinfo=UTC)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
