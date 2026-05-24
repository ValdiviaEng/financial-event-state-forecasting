from __future__ import annotations

from datetime import UTC, date, datetime

from src.split.alignment_rules import annotate_article_alignment, annotate_articles_asof_close
from src.utils.time_and_calendars import (
    is_after_market_close,
    market_close_timestamp,
    next_trading_day,
    normalize_to_utc,
    resolve_asof_trade_date,
)


def test_normalize_to_utc_handles_offset_strings_and_unix_seconds() -> None:
    offset_string = normalize_to_utc("2024-01-02T15:30:00-05:00")
    unix_seconds = normalize_to_utc(1704202200)

    assert offset_string.isoformat() == "2024-01-02T20:30:00+00:00"
    assert unix_seconds.tzinfo == UTC


def test_market_close_timestamp_is_built_in_utc() -> None:
    close_ts = market_close_timestamp(
        "2024-01-02",
        market_timezone="America/New_York",
        close_hour=16,
        close_minute=0,
    )

    assert close_ts.isoformat() == "2024-01-02T21:00:00+00:00"


def test_resolve_asof_trade_date_same_day_before_close() -> None:
    asof_date = resolve_asof_trade_date(
        "2024-01-02T20:30:00+00:00",
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    )

    assert asof_date == date(2024, 1, 2)


def test_resolve_asof_trade_date_after_close_rolls_to_next_trading_day() -> None:
    asof_date = resolve_asof_trade_date(
        "2024-01-02T22:00:00+00:00",
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    )

    assert asof_date == date(2024, 1, 3)


def test_friday_after_close_rolls_to_monday() -> None:
    asof_date = resolve_asof_trade_date(
        "2024-01-05T22:30:00+00:00",
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    )

    assert asof_date == date(2024, 1, 8)
    assert next_trading_day("2024-01-05", exchange_calendar="XNYS") == date(2024, 1, 8)


def test_weekend_article_rolls_to_next_trading_day() -> None:
    asof_date = resolve_asof_trade_date(
        "2024-01-06T15:00:00+00:00",
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    )

    assert asof_date == date(2024, 1, 8)


def test_annotate_article_alignment_adds_fields() -> None:
    article = {
        "article_id": "1",
        "ticker": "AAPL",
        "published_ts_utc": datetime(2024, 1, 2, 22, 0, tzinfo=UTC),
    }
    enriched = annotate_article_alignment(
        article,
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    )

    assert enriched["asof_trade_date"] == date(2024, 1, 3)
    assert enriched["after_market_close"] is True
    assert is_after_market_close(
        article["published_ts_utc"],
        market_timezone="America/New_York",
        close_hour=16,
        close_minute=0,
    ) is True


def test_annotate_articles_asof_close_handles_empty_and_missing_timestamp() -> None:
    assert annotate_articles_asof_close(
        [],
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    ) == []

    enriched = annotate_articles_asof_close(
        [{"article_id": "1", "ticker": "AAPL", "published_ts_utc": None}],
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        close_hour=16,
        close_minute=0,
    )

    assert enriched[0]["asof_trade_date"] is None
    assert enriched[0]["after_market_close"] is None
