"""Timezone and trading-calendar helpers used across the project."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
import importlib
from typing import Any
from zoneinfo import ZoneInfo


class CalendarError(ValueError):
    """Raised when calendar or timestamp inputs cannot be normalized safely."""


def normalize_to_utc(
    value: Any,
    *,
    assume_timezone: str = "UTC",
) -> datetime:
    """Normalize common timestamp inputs into a timezone-aware UTC datetime."""

    if isinstance(value, datetime):
        timestamp = value
    elif isinstance(value, (int, float)):
        numeric = int(value)
        if numeric > 10_000_000_000:
            numeric = numeric // 1000
        timestamp = datetime.fromtimestamp(numeric, tz=UTC)
    elif isinstance(value, str):
        normalized = value.strip().replace("Z", "+00:00")
        timestamp = datetime.fromisoformat(normalized)
    else:
        raise CalendarError(f"Unsupported timestamp type: {type(value).__name__}")

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=ZoneInfo(assume_timezone))
    return timestamp.astimezone(UTC)


def market_close_timestamp(
    trading_date: str | date,
    *,
    market_timezone: str,
    close_hour: int,
    close_minute: int,
) -> datetime:
    """Return the UTC timestamp corresponding to the market close on a trading day."""

    session_date = _coerce_date(trading_date)
    local_close = datetime.combine(
        session_date,
        time(hour=close_hour, minute=close_minute),
        tzinfo=ZoneInfo(market_timezone),
    )
    return local_close.astimezone(UTC)


def is_trading_day(trading_date: str | date, *, exchange_calendar: str = "XNYS") -> bool:
    """Return whether a date is a trading session for the configured exchange."""

    session_date = _coerce_date(trading_date)
    calendar = _optional_exchange_calendar(exchange_calendar)
    if calendar is None:
        return session_date.weekday() < 5

    pandas_module = importlib.import_module("pandas")
    return bool(calendar.is_session(pandas_module.Timestamp(session_date)))


def next_trading_day(trading_date: str | date, *, exchange_calendar: str = "XNYS") -> date:
    """Return the next trading day strictly after the provided date."""

    current = _coerce_date(trading_date) + timedelta(days=1)
    while not is_trading_day(current, exchange_calendar=exchange_calendar):
        current += timedelta(days=1)
    return current


def previous_trading_day(trading_date: str | date, *, exchange_calendar: str = "XNYS") -> date:
    """Return the previous trading day strictly before the provided date."""

    current = _coerce_date(trading_date) - timedelta(days=1)
    while not is_trading_day(current, exchange_calendar=exchange_calendar):
        current -= timedelta(days=1)
    return current


def resolve_asof_trade_date(
    published_ts_utc: datetime | str | int | float,
    *,
    market_timezone: str,
    exchange_calendar: str,
    close_hour: int,
    close_minute: int,
) -> date:
    """Assign a published timestamp to the trading date whose features may use it."""

    published_utc = normalize_to_utc(published_ts_utc)
    local_timestamp = published_utc.astimezone(ZoneInfo(market_timezone))
    local_date = local_timestamp.date()

    if not is_trading_day(local_date, exchange_calendar=exchange_calendar):
        return next_trading_day(local_date, exchange_calendar=exchange_calendar)

    close_ts = market_close_timestamp(
        local_date,
        market_timezone=market_timezone,
        close_hour=close_hour,
        close_minute=close_minute,
    )
    if published_utc <= close_ts:
        return local_date
    return next_trading_day(local_date, exchange_calendar=exchange_calendar)


def is_after_market_close(
    published_ts_utc: datetime | str | int | float,
    *,
    market_timezone: str,
    close_hour: int,
    close_minute: int,
) -> bool:
    """Return whether a published timestamp falls after the local market close."""

    published_utc = normalize_to_utc(published_ts_utc)
    local_timestamp = published_utc.astimezone(ZoneInfo(market_timezone))
    local_date = local_timestamp.date()
    close_ts = market_close_timestamp(
        local_date,
        market_timezone=market_timezone,
        close_hour=close_hour,
        close_minute=close_minute,
    )
    return published_utc > close_ts


def _optional_exchange_calendar(exchange_calendar: str) -> Any | None:
    try:
        exchange_calendars = importlib.import_module("exchange_calendars")
    except ModuleNotFoundError:
        return None
    return exchange_calendars.get_calendar(exchange_calendar)


def _coerce_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
