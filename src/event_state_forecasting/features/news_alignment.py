"""As-of-close Alpha Vantage news alignment for Stage 3."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("America/New_York")
MARKET_CLOSE_TIME = time(16, 0, 0)


class NewsAlignmentError(ValueError):
    """Raised when news records cannot be aligned safely."""


@dataclass(frozen=True, slots=True)
class AlignedNewsRecord:
    article_id: str
    ticker: str
    published_timestamp: str
    aligned_as_of_date: str
    roll_forward_reason: str
    title: str
    summary: str
    url: str
    text_hash: str


def align_news_as_of_close(
    records: list[dict[str, str]],
    trading_dates: list[date],
    *,
    market_close_time: time = MARKET_CLOSE_TIME,
    timezone: ZoneInfo = MARKET_TIMEZONE,
) -> tuple[list[AlignedNewsRecord], dict[str, int]]:
    """Assign raw article records to prediction dates without rolling backward."""

    if not trading_dates:
        raise NewsAlignmentError("trading_dates must not be empty")
    sorted_dates = sorted(set(trading_dates))
    trading_set = set(sorted_dates)
    aligned: list[AlignedNewsRecord] = []
    skipped_after_window = 0
    skipped_missing_timestamp = 0

    for record in records:
        raw_time = record.get("time_published", "")
        if not raw_time:
            skipped_missing_timestamp += 1
            continue
        published = parse_alpha_time_published(raw_time, timezone=timezone)
        assigned_date, reason = assign_prediction_date(published, sorted_dates, trading_set, market_close_time)
        if assigned_date is None:
            skipped_after_window += 1
            continue
        aligned.append(
            AlignedNewsRecord(
                article_id=record["article_id"],
                ticker=record["ticker"],
                published_timestamp=published.isoformat(),
                aligned_as_of_date=assigned_date.isoformat(),
                roll_forward_reason=reason,
                title=record.get("title", ""),
                summary=record.get("summary", ""),
                url=record.get("url", ""),
                text_hash=record.get("text_hash", ""),
            )
        )

    return aligned, {
        "input_record_count": len(records),
        "aligned_record_count": len(aligned),
        "skipped_after_window_count": skipped_after_window,
        "skipped_missing_timestamp_count": skipped_missing_timestamp,
    }


def assign_prediction_date(
    published: datetime,
    trading_dates: list[date],
    trading_set: set[date],
    market_close_time: time = MARKET_CLOSE_TIME,
) -> tuple[date | None, str]:
    local_date = published.date()
    if local_date in trading_set and published.timetz().replace(tzinfo=None) <= market_close_time:
        return local_date, "same_trading_day_at_or_before_close"
    if local_date in trading_set:
        return next_trading_date_after(local_date, trading_dates), "after_close_roll_forward"
    return next_trading_date_on_or_after(local_date, trading_dates), "non_trading_day_roll_forward"


def next_trading_date_after(value: date, trading_dates: list[date]) -> date | None:
    for trading_date in trading_dates:
        if trading_date > value:
            return trading_date
    return None


def next_trading_date_on_or_after(value: date, trading_dates: list[date]) -> date | None:
    for trading_date in trading_dates:
        if trading_date >= value:
            return trading_date
    return None


def parse_alpha_time_published(value: str, *, timezone: ZoneInfo = MARKET_TIMEZONE) -> datetime:
    try:
        parsed = datetime.strptime(value, "%Y%m%dT%H%M%S")
    except ValueError as exc:
        raise NewsAlignmentError(f"invalid Alpha Vantage time_published value: {value}") from exc
    return parsed.replace(tzinfo=timezone)
