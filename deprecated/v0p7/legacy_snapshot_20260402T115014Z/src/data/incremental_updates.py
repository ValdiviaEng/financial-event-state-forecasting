"""Helpers for planning incremental market-data refreshes."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from collections.abc import Mapping
from typing import Any

from src.utils.io_utils import read_parquet


class IncrementalUpdateError(ValueError):
    """Raised when incremental update planning inputs are invalid."""


@dataclass(frozen=True, slots=True)
class MarketUpdateWindow:
    """One ticker-specific update request window."""

    ticker: str
    start_date: str
    end_date: str
    reason: str
    latest_local_date: date | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "reason": self.reason,
            "latest_local_date": self.latest_local_date.isoformat() if self.latest_local_date else None,
        }


def detect_latest_local_date(rows_or_table: Any) -> date | None:
    """Detect the latest available date from row records or a DataFrame-like object."""

    if rows_or_table is None:
        return None

    if hasattr(rows_or_table, "empty") and getattr(rows_or_table, "empty") is True:
        return None

    if hasattr(rows_or_table, "columns"):
        if "date" not in getattr(rows_or_table, "columns"):
            raise IncrementalUpdateError("Expected tabular input to contain a 'date' column.")
        series = rows_or_table["date"]
        if len(series) == 0:
            return None
        latest = max(_coerce_date(value) for value in series.tolist())
        return latest

    if isinstance(rows_or_table, list):
        if not rows_or_table:
            return None
        latest = max(_coerce_date(row["date"]) for row in rows_or_table)
        return latest

    raise IncrementalUpdateError(
        f"Unsupported input type for latest-date detection: {type(rows_or_table).__name__}"
    )


def read_latest_date_from_price_file(file_path: str | Path) -> date | None:
    """Read a per-ticker price parquet file and return the latest local date."""

    path = Path(file_path)
    if not path.exists():
        return None
    table = read_parquet(path, columns=["date"], backend="pandas")
    return detect_latest_local_date(table)


def determine_incremental_window(
    *,
    latest_local_date: date | None,
    start_date: str | date,
    end_date: str | date,
) -> MarketUpdateWindow | None:
    """Determine the next required update window for one ticker."""

    normalized_start = _coerce_date(start_date)
    normalized_end = _coerce_date(end_date)
    if normalized_end < normalized_start:
        raise IncrementalUpdateError("end_date must be on or after start_date.")

    if latest_local_date is None:
        return MarketUpdateWindow(
            ticker="",
            start_date=normalized_start.isoformat(),
            end_date=normalized_end.isoformat(),
            reason="initial_backfill",
            latest_local_date=None,
        )

    next_start = latest_local_date + timedelta(days=1)
    if next_start > normalized_end:
        return None

    return MarketUpdateWindow(
        ticker="",
        start_date=max(next_start, normalized_start).isoformat(),
        end_date=normalized_end.isoformat(),
        reason="incremental_refresh",
        latest_local_date=latest_local_date,
    )


def build_market_update_plan(
    tickers: list[str] | tuple[str, ...],
    *,
    latest_dates: dict[str, date | None],
    start_date: str | date,
    end_date: str | date,
    max_symbols: int | None = None,
) -> list[MarketUpdateWindow]:
    """Build ticker-specific market update windows in deterministic order."""

    windows: list[MarketUpdateWindow] = []
    for ticker in tickers:
        window = determine_incremental_window(
            latest_local_date=latest_dates.get(ticker),
            start_date=start_date,
            end_date=end_date,
        )
        if window is None:
            continue
        windows.append(
            MarketUpdateWindow(
                ticker=ticker,
                start_date=window.start_date,
                end_date=window.end_date,
                reason=window.reason,
                latest_local_date=window.latest_local_date,
            )
        )

    if max_symbols is not None:
        if max_symbols <= 0:
            raise IncrementalUpdateError("max_symbols must be positive when provided.")
        windows = windows[:max_symbols]

    return windows


def build_repair_window(
    ticker: str,
    *,
    anchor_date: str | date,
    window_days: int,
) -> MarketUpdateWindow:
    """Create a symmetric repair window around an anchor date."""

    if window_days < 0:
        raise IncrementalUpdateError("window_days must be non-negative.")
    anchor = _coerce_date(anchor_date)
    start = anchor - timedelta(days=window_days)
    end = anchor + timedelta(days=window_days)
    return MarketUpdateWindow(
        ticker=ticker,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        reason="repair_window",
        latest_local_date=None,
    )


def latest_dates_by_ticker(price_files: Mapping[str, str | Path]) -> dict[str, date | None]:
    """Return latest local dates keyed by ticker from per-ticker parquet paths."""

    return {ticker: read_latest_date_from_price_file(path) for ticker, path in price_files.items()}


def _coerce_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
