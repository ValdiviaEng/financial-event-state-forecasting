from __future__ import annotations

from datetime import date

import pandas as pd

from src.split.leakage_checks import assert_purged_split_respected, assert_walk_forward_chronology
from src.split.purged_embargo_splits import build_purged_walk_forward_splits, purge_and_embargo_train_dates
from src.split.walk_forward_splits import build_walk_forward_splits, summarize_walk_forward_splits


def _panel_frame() -> pd.DataFrame:
    rows = []
    for ticker in ("AAPL", "MSFT"):
        for day in range(1, 11):
            rows.append({"ticker": ticker, "date": f"2024-01-{day:02d}"})
    return pd.DataFrame(rows)


def test_build_walk_forward_splits_is_chronological_and_non_overlapping() -> None:
    frame = _panel_frame()
    splits = build_walk_forward_splits(
        frame,
        train_window=4,
        validation_window=1,
        test_window=2,
        step_size=2,
        max_splits=2,
        expanding=True,
    )

    assert len(splits) == 2
    first = splits[0]
    assert first.train_dates == (
        date(2024, 1, 1),
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
    )
    assert first.validation_dates == (date(2024, 1, 5),)
    assert first.test_dates == (date(2024, 1, 6), date(2024, 1, 7))
    assert_walk_forward_chronology(first)

    second = splits[1]
    assert second.train_dates[-1] == date(2024, 1, 6)
    assert second.test_dates == (date(2024, 1, 8), date(2024, 1, 9))
    assert_walk_forward_chronology(second)


def test_walk_forward_split_generation_is_reproducible() -> None:
    frame = _panel_frame()
    first_run = build_walk_forward_splits(frame, train_window=4, validation_window=0, test_window=2)
    second_run = build_walk_forward_splits(frame, train_window=4, validation_window=0, test_window=2)

    assert [split.as_dict() for split in first_run] == [split.as_dict() for split in second_run]
    summary = summarize_walk_forward_splits(first_run)
    assert summary["split_count"] == len(first_run)


def test_purge_and_embargo_train_dates_remove_overlapping_and_embargoed_dates() -> None:
    ordered_dates = tuple(date(2024, 1, day) for day in range(1, 11))
    train_dates = (date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 8))
    holdout_dates = (date(2024, 1, 5), date(2024, 1, 6))

    kept, removed = purge_and_embargo_train_dates(
        train_dates=train_dates,
        holdout_dates=holdout_dates,
        ordered_dates=ordered_dates,
        max_horizon=2,
        embargo_days=2,
    )

    assert kept == (date(2024, 1, 2),)
    assert removed == (date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 8))


def test_build_purged_walk_forward_splits_applies_horizon_aware_purge() -> None:
    frame = _panel_frame()
    splits = build_purged_walk_forward_splits(
        frame,
        train_window=4,
        validation_window=1,
        test_window=2,
        step_size=2,
        max_splits=1,
        horizons=(2,),
        embargo_days=0,
    )

    assert len(splits) == 1
    split = splits[0]
    assert split.train_dates == (date(2024, 1, 1), date(2024, 1, 2))
    assert split.removed_train_dates == (date(2024, 1, 3), date(2024, 1, 4))
    ordered_dates = tuple(date(2024, 1, day) for day in range(1, 11))
    assert_purged_split_respected(split, ordered_dates=ordered_dates)
