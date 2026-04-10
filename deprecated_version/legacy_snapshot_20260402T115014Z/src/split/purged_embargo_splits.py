"""Purged and embargoed extensions for walk-forward splits."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from src.split.walk_forward_splits import build_walk_forward_splits


class PurgedSplitError(ValueError):
    """Raised when purge or embargo settings are inconsistent."""


@dataclass(frozen=True, slots=True)
class PurgedWalkForwardSplit:
    """Walk-forward split with purged and embargoed training rows removed."""

    split_id: int
    train_dates: tuple[date, ...]
    validation_dates: tuple[date, ...]
    test_dates: tuple[date, ...]
    train_indices: tuple[int, ...]
    validation_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    removed_train_dates: tuple[date, ...]
    removed_train_indices: tuple[int, ...]
    max_horizon: int
    embargo_days: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "split_id": self.split_id,
            "train_dates": [value.isoformat() for value in self.train_dates],
            "validation_dates": [value.isoformat() for value in self.validation_dates],
            "test_dates": [value.isoformat() for value in self.test_dates],
            "removed_train_dates": [value.isoformat() for value in self.removed_train_dates],
            "max_horizon": self.max_horizon,
            "embargo_days": self.embargo_days,
        }


def purge_and_embargo_train_dates(
    *,
    train_dates: tuple[date, ...],
    holdout_dates: tuple[date, ...],
    ordered_dates: tuple[date, ...],
    max_horizon: int,
    embargo_days: int = 0,
) -> tuple[tuple[date, ...], tuple[date, ...]]:
    """Remove train dates whose label windows overlap holdout dates.

    A train date is purged if `train_position + max_horizon >= first_holdout_position`.
    Any train date that falls inside the explicit embargo window after the final
    holdout date is also removed.
    """

    if max_horizon < 0:
        raise PurgedSplitError("max_horizon must be non-negative.")
    if embargo_days < 0:
        raise PurgedSplitError("embargo_days must be non-negative.")
    if not holdout_dates:
        return train_dates, tuple()

    date_positions = {value: index for index, value in enumerate(ordered_dates)}
    first_holdout_pos = min(date_positions[value] for value in holdout_dates)
    last_holdout_pos = max(date_positions[value] for value in holdout_dates)

    kept: list[date] = []
    removed: list[date] = []
    for train_date in train_dates:
        train_pos = date_positions[train_date]
        overlaps_holdout = train_pos + max_horizon >= first_holdout_pos
        in_embargo_window = first_holdout_pos <= train_pos <= (last_holdout_pos + embargo_days)
        if overlaps_holdout or in_embargo_window:
            removed.append(train_date)
        else:
            kept.append(train_date)
    return tuple(kept), tuple(removed)


def build_purged_walk_forward_splits(
    data: pd.DataFrame,
    *,
    date_col: str = "date",
    train_window: int,
    test_window: int,
    validation_window: int = 0,
    step_size: int | None = None,
    max_splits: int | None = None,
    expanding: bool = True,
    horizons: tuple[int, ...] = (1,),
    embargo_days: int = 0,
) -> list[PurgedWalkForwardSplit]:
    """Build walk-forward splits and purge overlapping train rows by horizon."""

    if not horizons:
        raise PurgedSplitError("At least one horizon is required for purged splits.")
    max_horizon = max(horizons)

    base_splits = build_walk_forward_splits(
        data,
        date_col=date_col,
        train_window=train_window,
        test_window=test_window,
        validation_window=validation_window,
        step_size=step_size,
        max_splits=max_splits,
        expanding=expanding,
    )

    prepared = data.copy()
    prepared[date_col] = pd.to_datetime(prepared[date_col]).dt.date
    ordered_dates = tuple(sorted(prepared[date_col].dropna().unique().tolist()))

    purged_splits: list[PurgedWalkForwardSplit] = []
    for split in base_splits:
        holdout_dates = split.validation_dates + split.test_dates
        purged_train_dates, removed_train_dates = purge_and_embargo_train_dates(
            train_dates=split.train_dates,
            holdout_dates=holdout_dates,
            ordered_dates=ordered_dates,
            max_horizon=max_horizon,
            embargo_days=embargo_days,
        )
        purged_splits.append(
            PurgedWalkForwardSplit(
                split_id=split.split_id,
                train_dates=purged_train_dates,
                validation_dates=split.validation_dates,
                test_dates=split.test_dates,
                train_indices=_row_indices_for_dates(prepared, date_col, purged_train_dates),
                validation_indices=split.validation_indices,
                test_indices=split.test_indices,
                removed_train_dates=removed_train_dates,
                removed_train_indices=_row_indices_for_dates(prepared, date_col, removed_train_dates),
                max_horizon=max_horizon,
                embargo_days=embargo_days,
            )
        )

    return purged_splits


def _row_indices_for_dates(data: pd.DataFrame, date_col: str, dates: tuple[date, ...]) -> tuple[int, ...]:
    if not dates:
        return tuple()
    mask = data[date_col].isin(dates)
    return tuple(int(index) for index in data.index[mask].tolist())
