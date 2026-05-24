"""Helpers for Alpha Vantage backfill classification and logging."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.io_utils import read_json, read_parquet, write_json


def load_ledger_frame(ledger_path: Path) -> pd.DataFrame:
    if not ledger_path.exists():
        return pd.DataFrame()
    return read_parquet(ledger_path, backend="pandas")


def minmax_time_published(feed: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    times = [item.get("time_published") for item in feed if item.get("time_published")]
    if not times:
        return None, None
    return min(times), max(times)


def classify_planned_call(
    *,
    raw_path: Path,
    ledger_frame: pd.DataFrame,
    ticker: str,
    time_from: str,
    time_to: str,
    sort: str,
    limit: int,
) -> dict[str, Any]:
    if raw_path.exists():
        payload = read_json(raw_path)
        feed = payload.get("feed", []) if isinstance(payload, dict) else []
        oldest, newest = minmax_time_published(feed)
        likely_truncated = len(feed) >= limit
        return {
            "ticker": ticker,
            "time_from": time_from,
            "time_to": time_to,
            "raw_path": str(raw_path),
            "status": "already_done_truncated" if likely_truncated else "already_done_complete",
            "rows_returned": len(feed),
            "oldest_time_published": oldest,
            "newest_time_published": newest,
            "likely_truncated": likely_truncated,
            "ledger_match_count": count_matching_ledger_rows(
                ledger_frame=ledger_frame,
                ticker=ticker,
                time_from=time_from,
                time_to=time_to,
                sort=sort,
                limit=limit,
            ),
        }

    match_count = count_matching_ledger_rows(
        ledger_frame=ledger_frame,
        ticker=ticker,
        time_from=time_from,
        time_to=time_to,
        sort=sort,
        limit=limit,
    )
    return {
        "ticker": ticker,
        "time_from": time_from,
        "time_to": time_to,
        "raw_path": str(raw_path),
        "status": "pending",
        "rows_returned": None,
        "oldest_time_published": None,
        "newest_time_published": None,
        "likely_truncated": None,
        "ledger_match_count": match_count,
    }


def count_matching_ledger_rows(
    *,
    ledger_frame: pd.DataFrame,
    ticker: str,
    time_from: str,
    time_to: str,
    sort: str,
    limit: int,
) -> int:
    if ledger_frame.empty:
        return 0
    frame = ledger_frame.copy()
    for column in ["provider", "endpoint", "ticker", "time_from", "time_to", "sort", "limit"]:
        if column not in frame.columns:
            return 0
    mask = (
        (frame["provider"].astype(str) == "alphavantage")
        & (frame["endpoint"].astype(str) == "NEWS_SENTIMENT")
        & (frame["ticker"].astype(str) == ticker)
        & (frame["time_from"].astype(str) == time_from)
        & (frame["time_to"].astype(str) == time_to)
        & (frame["sort"].astype(str) == sort)
        & (frame["limit"].astype(str) == str(limit))
    )
    return int(mask.sum())


def write_classification_logs(
    *,
    raw_provider_dir: Path,
    scope_name: str,
    classifications: list[dict[str, Any]],
) -> tuple[Path, Path]:
    generated_at = datetime.now(UTC).isoformat()
    status_payload = {
        "provider": "alphavantage",
        "generated_at_utc": generated_at,
        "scope_name": scope_name,
        "total_classified_calls": len(classifications),
        "status_counts": build_status_counts(classifications),
        "classifications": classifications,
    }
    truncated = [
        classification
        for classification in classifications
        if classification.get("status") in {"already_done_truncated", "downloaded_truncated"}
    ]
    truncated_payload = {
        "provider": "alphavantage",
        "generated_at_utc": generated_at,
        "scope_name": scope_name,
        "truncated_call_count": len(truncated),
        "truncated_calls": truncated,
    }
    status_path = raw_provider_dir / f"call_status__{scope_name}.json"
    truncated_path = raw_provider_dir / f"truncated_calls__{scope_name}.json"
    write_json(status_payload, status_path)
    write_json(truncated_payload, truncated_path)
    return status_path, truncated_path


def build_status_counts(classifications: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in classifications:
        status = str(item.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts
