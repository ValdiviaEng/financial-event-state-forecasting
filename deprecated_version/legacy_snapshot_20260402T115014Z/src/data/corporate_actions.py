"""Split-event application and adjusted-price generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from collections.abc import Sequence
from typing import Any

from src.data.split_events_client import SplitEvent


class CorporateActionsError(RuntimeError):
    """Raised when split-adjustment inputs or outputs are invalid."""


@dataclass(frozen=True, slots=True)
class SplitFactorRow:
    """Cumulative split-adjustment factor applicable to one historical row."""

    ticker: str
    date: date
    cumulative_split_factor: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "date": self.date,
            "cumulative_split_factor": self.cumulative_split_factor,
        }


@dataclass(frozen=True, slots=True)
class AdjustedPriceResult:
    """Adjusted prices and diagnostics for one ticker history."""

    adjusted_rows: list[dict[str, Any]]
    diagnostics: dict[str, Any]


def normalize_split_events(
    split_events: Sequence[SplitEvent | dict[str, Any]],
    *,
    ticker: str | None = None,
) -> list[SplitEvent]:
    """Normalize split events into canonical dataclass instances."""

    normalized: list[SplitEvent] = []
    for event in split_events:
        if isinstance(event, SplitEvent):
            split_event = event
        elif isinstance(event, dict):
            try:
                split_event = SplitEvent(
                    ticker=str(event["ticker"]),
                    split_date=_coerce_date(event["split_date"]),
                    split_factor=float(event["split_factor"]),
                    source=str(event.get("source", "unknown")),
                    provider_event_id=_string_or_none(event.get("provider_event_id")),
                    raw_factor_text=_string_or_none(event.get("raw_factor_text")),
                )
            except KeyError as exc:
                raise CorporateActionsError(
                    f"Split-event record is missing required key: {exc.args[0]}"
                ) from exc
        else:
            raise CorporateActionsError(
                f"Unsupported split-event type {type(event).__name__}; expected SplitEvent or mapping."
            )

        if split_event.split_factor <= 0:
            raise CorporateActionsError(
                f"Split factor must be positive, got {split_event.split_factor} for {split_event.ticker}."
            )
        if ticker is not None and split_event.ticker != ticker:
            continue
        normalized.append(split_event)

    return sorted(normalized, key=lambda event: event.split_date)


def compute_cumulative_future_split_factors(
    rows: list[dict[str, Any]],
    split_events: Sequence[SplitEvent | dict[str, Any]],
) -> list[SplitFactorRow]:
    """Compute cumulative future split factors for each historical row.

    The factor for a row at date `t` is the product of all split factors whose
    `split_date` is strictly greater than `t`.
    """

    if not rows:
        return []

    ticker = _extract_single_ticker(rows)
    normalized_rows = sorted((_normalize_price_row(row) for row in rows), key=lambda row: row["date"], reverse=True)
    events = sorted(normalize_split_events(split_events, ticker=ticker), key=lambda event: event.split_date, reverse=True)

    factor_rows: list[SplitFactorRow] = []
    cumulative_factor = 1.0
    event_index = 0

    for row in normalized_rows:
        row_date = row["date"]
        while event_index < len(events) and row_date < events[event_index].split_date:
            cumulative_factor *= events[event_index].split_factor
            event_index += 1

        factor_rows.append(
            SplitFactorRow(
                ticker=ticker,
                date=row_date,
                cumulative_split_factor=cumulative_factor,
            )
        )

    return sorted(factor_rows, key=lambda item: item.date)


def apply_split_adjustments(
    rows: list[dict[str, Any]],
    split_events: Sequence[SplitEvent | dict[str, Any]],
    *,
    adjustment_source: str,
    missing_split_policy: str = "warn_return_raw",
    adjustment_applied_ts: datetime | None = None,
) -> AdjustedPriceResult:
    """Back-adjust OHLCV rows using canonical split events."""

    if not rows:
        return AdjustedPriceResult(adjusted_rows=[], diagnostics={"split_event_count": 0, "issues": []})

    ticker = _extract_single_ticker(rows)
    normalized_rows = sorted((_normalize_price_row(row) for row in rows), key=lambda row: row["date"])
    events = normalize_split_events(split_events, ticker=ticker)
    events, skipped_messages = _filter_events_for_existing_adjustment(normalized_rows, events)

    if not events:
        if missing_split_policy == "error":
            raise CorporateActionsError(
                f"No split events provided for ticker '{ticker}' and missing_split_policy='error'."
            )
        adjusted_rows = [
            _build_adjusted_row(
                row,
                cumulative_split_factor=1.0,
                adjustment_source=f"{adjustment_source}:no_split_events",
                adjustment_applied_ts=adjustment_applied_ts or datetime.now(UTC),
            )
            for row in normalized_rows
        ]
        diagnostics = build_split_adjustment_diagnostics(
            raw_rows=normalized_rows,
            adjusted_rows=adjusted_rows,
            split_events=events,
            adjustment_source=adjustment_source,
            missing_split_policy=missing_split_policy,
            issues=["No split events supplied; rows were returned unadjusted.", *skipped_messages],
        )
        return AdjustedPriceResult(adjusted_rows=adjusted_rows, diagnostics=diagnostics)

    factor_rows = compute_cumulative_future_split_factors(normalized_rows, events)
    factor_map = {item.date: item.cumulative_split_factor for item in factor_rows}
    applied_ts = adjustment_applied_ts or datetime.now(UTC)

    adjusted_rows = [
        _build_adjusted_row(
            row,
            cumulative_split_factor=factor_map[row["date"]],
            adjustment_source=adjustment_source,
            adjustment_applied_ts=applied_ts,
        )
        for row in normalized_rows
    ]
    diagnostics = build_split_adjustment_diagnostics(
        raw_rows=normalized_rows,
        adjusted_rows=adjusted_rows,
        split_events=events,
        adjustment_source=adjustment_source,
        missing_split_policy=missing_split_policy,
        issues=skipped_messages,
    )
    return AdjustedPriceResult(adjusted_rows=adjusted_rows, diagnostics=diagnostics)


def exclude_rows_around_split_dates(
    rows: list[dict[str, Any]],
    split_events: Sequence[SplitEvent | dict[str, Any]],
    *,
    window_days: int,
) -> list[dict[str, Any]]:
    """Exclude rows within a symmetric calendar-day window around each split date."""

    if window_days < 0:
        raise CorporateActionsError("window_days must be non-negative.")

    events = normalize_split_events(split_events)
    excluded_dates: set[date] = set()
    for event in events:
        for offset in range(-window_days, window_days + 1):
            excluded_dates.add(event.split_date + timedelta(days=offset))

    filtered_rows = []
    for row in rows:
        normalized_row = _normalize_price_row(row)
        if normalized_row["date"] in excluded_dates:
            continue
        filtered_rows.append(normalized_row)
    return filtered_rows


def build_split_adjustment_diagnostics(
    *,
    raw_rows: list[dict[str, Any]],
    adjusted_rows: list[dict[str, Any]],
    split_events: list[SplitEvent],
    adjustment_source: str,
    missing_split_policy: str,
    issues: list[str],
) -> dict[str, Any]:
    """Build diagnostics for split-adjustment output validation and auditing."""

    ticker = _extract_single_ticker(raw_rows) if raw_rows else None
    raw_returns = _one_day_close_returns(raw_rows)
    adjusted_returns = _one_day_close_returns(adjusted_rows)

    return {
        "ticker": ticker,
        "adjustment_source": adjustment_source,
        "missing_split_policy": missing_split_policy,
        "split_event_count": len(split_events),
        "split_dates": [event.split_date.isoformat() for event in split_events],
        "max_abs_return_raw": max((abs(value) for value in raw_returns), default=0.0),
        "max_abs_return_adjusted": max((abs(value) for value in adjusted_returns), default=0.0),
        "split_day_checks": _split_day_checks(raw_rows, adjusted_rows, split_events),
        "issues": issues,
    }


def _split_day_checks(
    raw_rows: list[dict[str, Any]],
    adjusted_rows: list[dict[str, Any]],
    split_events: list[SplitEvent],
) -> list[dict[str, Any]]:
    raw_by_date = {_normalize_price_row(row)["date"]: _normalize_price_row(row) for row in raw_rows}
    adjusted_by_date = {_normalize_price_row(row)["date"]: _normalize_price_row(row) for row in adjusted_rows}
    ordered_dates = sorted(raw_by_date)

    checks: list[dict[str, Any]] = []
    for event in split_events:
        prior_dates = [current_date for current_date in ordered_dates if current_date < event.split_date]
        previous_date = prior_dates[-1] if prior_dates else None
        if previous_date is None or event.split_date not in raw_by_date:
            continue
        raw_return = _close_to_close_return(raw_by_date[previous_date], raw_by_date[event.split_date])
        adjusted_return = _close_to_close_return(
            adjusted_by_date[previous_date], adjusted_by_date[event.split_date]
        )
        checks.append(
            {
                "split_date": event.split_date.isoformat(),
                "split_factor": event.split_factor,
                "previous_date": previous_date.isoformat(),
                "raw_close_to_split_return": raw_return,
                "adjusted_close_to_split_return": adjusted_return,
            }
        )
    return checks


def _filter_events_for_existing_adjustment(
    raw_rows: list[dict[str, Any]],
    split_events: list[SplitEvent],
) -> tuple[list[SplitEvent], list[str]]:
    raw_by_date = {_normalize_price_row(row)["date"]: _normalize_price_row(row) for row in raw_rows}
    ordered_dates = sorted(raw_by_date)
    kept: list[SplitEvent] = []
    issues: list[str] = []

    for event in split_events:
        if event.split_date not in raw_by_date:
            kept.append(event)
            continue
        prior_dates = [current_date for current_date in ordered_dates if current_date < event.split_date]
        previous_date = prior_dates[-1] if prior_dates else None
        if previous_date is None:
            kept.append(event)
            continue

        raw_return = _close_to_close_return(raw_by_date[previous_date], raw_by_date[event.split_date])
        if raw_return is None:
            kept.append(event)
            continue

        expected_unadjusted_return = (1.0 / event.split_factor) - 1.0
        error_if_already_adjusted = abs(raw_return)
        error_if_unadjusted = abs(raw_return - expected_unadjusted_return)
        if error_if_already_adjusted < error_if_unadjusted:
            issues.append(
                f"Skipped split event {event.split_date.isoformat()} for {event.ticker} because the raw series already appears split-adjusted in the local window."
            )
            continue
        kept.append(event)

    return kept, issues


def _close_to_close_return(previous_row: dict[str, Any], current_row: dict[str, Any]) -> float | None:
    previous_close = previous_row.get("close")
    current_close = current_row.get("close")
    if previous_close in (None, 0) or current_close is None:
        return None
    return (float(current_close) / float(previous_close)) - 1.0


def _one_day_close_returns(rows: list[dict[str, Any]]) -> list[float]:
    normalized_rows = sorted((_normalize_price_row(row) for row in rows), key=lambda row: row["date"])
    returns: list[float] = []
    for previous_row, current_row in zip(normalized_rows, normalized_rows[1:], strict=False):
        ret = _close_to_close_return(previous_row, current_row)
        if ret is not None:
            returns.append(ret)
    return returns


def _build_adjusted_row(
    row: dict[str, Any],
    *,
    cumulative_split_factor: float,
    adjustment_source: str,
    adjustment_applied_ts: datetime,
) -> dict[str, Any]:
    adjusted = dict(row)
    adjusted["open"] = _adjust_price(row.get("open"), cumulative_split_factor)
    adjusted["high"] = _adjust_price(row.get("high"), cumulative_split_factor)
    adjusted["low"] = _adjust_price(row.get("low"), cumulative_split_factor)
    adjusted["close"] = _adjust_price(row.get("close"), cumulative_split_factor)
    adjusted["volume"] = _adjust_volume(row.get("volume"), cumulative_split_factor)
    adjusted["adjustment_source"] = adjustment_source
    adjusted["cumulative_split_factor"] = cumulative_split_factor
    adjusted["adjustment_applied_ts"] = adjustment_applied_ts
    return adjusted


def _adjust_price(value: Any, cumulative_split_factor: float) -> float | None:
    if value is None:
        return None
    return float(value) / cumulative_split_factor


def _adjust_volume(value: Any, cumulative_split_factor: float) -> int | None:
    if value is None:
        return None
    return int(round(float(value) * cumulative_split_factor))


def _extract_single_ticker(rows: list[dict[str, Any]]) -> str:
    tickers = {str(row.get("ticker")) for row in rows if row.get("ticker") is not None}
    if len(tickers) != 1:
        raise CorporateActionsError(
            f"Expected rows for exactly one ticker, found {sorted(tickers)}."
        )
    return next(iter(tickers))


def _normalize_price_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    normalized["date"] = _coerce_date(normalized["date"])
    return normalized


def _coerce_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if hasattr(value, "date") and not isinstance(value, str):
        return value.date()
    return date.fromisoformat(str(value)[:10])


def _string_or_none(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
