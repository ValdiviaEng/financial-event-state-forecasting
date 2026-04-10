"""Single source of truth for news-to-market temporal alignment."""

from __future__ import annotations

from typing import Any

from src.utils.time_and_calendars import is_after_market_close, resolve_asof_trade_date


def assign_article_asof_trade_date(
    published_ts_utc: Any,
    *,
    market_timezone: str,
    exchange_calendar: str,
    close_hour: int,
    close_minute: int,
):
    """Map one article timestamp to the trading date allowed to use it."""

    return resolve_asof_trade_date(
        published_ts_utc,
        market_timezone=market_timezone,
        exchange_calendar=exchange_calendar,
        close_hour=close_hour,
        close_minute=close_minute,
    )


def annotate_article_alignment(
    article: dict[str, Any],
    *,
    market_timezone: str,
    exchange_calendar: str,
    close_hour: int,
    close_minute: int,
) -> dict[str, Any]:
    """Return an article copy with as-of trade-date alignment metadata."""

    enriched = dict(article)
    published_ts_utc = article.get("published_ts_utc")
    if published_ts_utc is None:
        enriched["asof_trade_date"] = None
        enriched["after_market_close"] = None
        return enriched

    enriched["asof_trade_date"] = assign_article_asof_trade_date(
        published_ts_utc,
        market_timezone=market_timezone,
        exchange_calendar=exchange_calendar,
        close_hour=close_hour,
        close_minute=close_minute,
    )
    enriched["after_market_close"] = is_after_market_close(
        published_ts_utc,
        market_timezone=market_timezone,
        close_hour=close_hour,
        close_minute=close_minute,
    )
    return enriched


def annotate_articles_asof_close(
    articles: list[dict[str, Any]],
    *,
    market_timezone: str,
    exchange_calendar: str,
    close_hour: int,
    close_minute: int,
) -> list[dict[str, Any]]:
    """Annotate a list of articles with as-of-close alignment fields."""

    return [
        annotate_article_alignment(
            article,
            market_timezone=market_timezone,
            exchange_calendar=exchange_calendar,
            close_hour=close_hour,
            close_minute=close_minute,
        )
        for article in articles
    ]
