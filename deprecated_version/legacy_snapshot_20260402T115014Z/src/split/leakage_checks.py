"""Reusable leakage diagnostics for temporal financial experiments."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from typing import Any

from src.split.alignment_rules import assign_article_asof_trade_date
from src.split.purged_embargo_splits import PurgedWalkForwardSplit


class LeakageCheckError(RuntimeError):
    """Raised when a leakage guardrail is violated."""


def assert_no_date_overlap(*date_groups: Sequence[date]) -> None:
    """Assert that date groups are pairwise disjoint."""

    seen: set[date] = set()
    for group in date_groups:
        for value in group:
            if value in seen:
                raise LeakageCheckError(f"Overlapping date detected across split groups: {value.isoformat()}")
            seen.add(value)


def assert_walk_forward_chronology(split: PurgedWalkForwardSplit | Any) -> None:
    """Assert that train, validation, and test dates are strictly chronological."""

    if split.train_dates and split.validation_dates:
        if max(split.train_dates) >= min(split.validation_dates):
            raise LeakageCheckError("Train dates must end before validation dates begin.")
    holdout_dates = split.validation_dates or split.test_dates
    if split.train_dates and holdout_dates:
        if max(split.train_dates) >= min(holdout_dates):
            raise LeakageCheckError("Train dates must end before holdout dates begin.")
    if split.validation_dates and split.test_dates:
        if max(split.validation_dates) >= min(split.test_dates):
            raise LeakageCheckError("Validation dates must end before test dates begin.")
    assert_no_date_overlap(split.train_dates, split.validation_dates, split.test_dates)


def assert_purged_split_respected(
    split: PurgedWalkForwardSplit,
    *,
    ordered_dates: Sequence[date],
) -> None:
    """Assert that purged splits respect the configured max horizon and embargo."""

    date_positions = {value: index for index, value in enumerate(ordered_dates)}
    holdout_dates = split.validation_dates + split.test_dates
    if not holdout_dates:
        return

    first_holdout_pos = min(date_positions[value] for value in holdout_dates)
    last_holdout_pos = max(date_positions[value] for value in holdout_dates)
    for train_date in split.train_dates:
        train_pos = date_positions[train_date]
        if train_pos + split.max_horizon >= first_holdout_pos:
            raise LeakageCheckError(
                f"Train date {train_date.isoformat()} was not purged despite overlapping the holdout horizon."
            )
        if first_holdout_pos <= train_pos <= last_holdout_pos + split.embargo_days:
            raise LeakageCheckError(
                f"Train date {train_date.isoformat()} was not embargoed correctly."
            )


def assert_articles_aligned_asof_close(
    articles: Sequence[dict[str, Any]],
    *,
    market_timezone: str,
    exchange_calendar: str,
    close_hour: int,
    close_minute: int,
) -> None:
    """Assert that stored `asof_trade_date` values match the alignment rules."""

    for article in articles:
        published_ts_utc = article.get("published_ts_utc")
        stored_trade_date = article.get("asof_trade_date")
        if published_ts_utc is None or stored_trade_date is None:
            continue
        expected_trade_date = assign_article_asof_trade_date(
            published_ts_utc,
            market_timezone=market_timezone,
            exchange_calendar=exchange_calendar,
            close_hour=close_hour,
            close_minute=close_minute,
        )
        if expected_trade_date != stored_trade_date:
            raise LeakageCheckError(
                "Article alignment mismatch detected for article_id="
                f"{article.get('article_id')}: expected {expected_trade_date.isoformat()} got {stored_trade_date.isoformat()}"
            )


def assert_scaler_fit_within_train_window(*, scaler_fit_end_date: date, train_end_date: date) -> None:
    """Assert that a scaler or normalizer was fit only on training data."""

    if scaler_fit_end_date > train_end_date:
        raise LeakageCheckError(
            "Scaler fit end date extends beyond the allowed train window, indicating train/test contamination."
        )


def assert_no_future_profile_effective_dates(
    profile_rows: Sequence[dict[str, Any]],
    *,
    feature_date_field: str = "date",
    effective_date_field: str = "effective_date",
) -> None:
    """Assert that time-varying profile rows do not come from the future."""

    for row in profile_rows:
        feature_date = row.get(feature_date_field)
        effective_date = row.get(effective_date_field)
        if feature_date is None or effective_date is None:
            continue
        if effective_date > feature_date:
            raise LeakageCheckError(
                f"Profile row uses future effective date {effective_date} for feature date {feature_date}."
            )
