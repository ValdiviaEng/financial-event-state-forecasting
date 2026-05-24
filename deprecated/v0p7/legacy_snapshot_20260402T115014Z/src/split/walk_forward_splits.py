"""Walk-forward temporal split generation for panel datasets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


class WalkForwardSplitError(ValueError):
    """Raised when walk-forward split inputs are invalid."""


@dataclass(frozen=True, slots=True)
class WalkForwardSplit:
    """One walk-forward fold over a panel keyed by `date`."""

    split_id: int
    train_dates: tuple[date, ...]
    validation_dates: tuple[date, ...]
    test_dates: tuple[date, ...]
    train_indices: tuple[int, ...]
    validation_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    expanding: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "split_id": self.split_id,
            "train_dates": [value.isoformat() for value in self.train_dates],
            "validation_dates": [value.isoformat() for value in self.validation_dates],
            "test_dates": [value.isoformat() for value in self.test_dates],
            "train_size": len(self.train_indices),
            "validation_size": len(self.validation_indices),
            "test_size": len(self.test_indices),
            "expanding": self.expanding,
        }


def build_walk_forward_splits(
    data: pd.DataFrame,
    *,
    date_col: str = "date",
    train_window: int,
    test_window: int,
    validation_window: int = 0,
    step_size: int | None = None,
    max_splits: int | None = None,
    expanding: bool = True,
) -> list[WalkForwardSplit]:
    """Build expanding or rolling walk-forward splits from a panel DataFrame."""

    if train_window <= 0:
        raise WalkForwardSplitError("train_window must be positive.")
    if test_window <= 0:
        raise WalkForwardSplitError("test_window must be positive.")
    if validation_window < 0:
        raise WalkForwardSplitError("validation_window must be non-negative.")

    prepared = _prepare_frame(data, date_col=date_col)
    unique_dates = sorted(prepared[date_col].dropna().unique().tolist())
    required_dates = train_window + validation_window + test_window
    if len(unique_dates) < required_dates:
        raise WalkForwardSplitError(
            "Not enough unique dates to build one split with the requested windows."
        )

    step = step_size or test_window
    if step <= 0:
        raise WalkForwardSplitError("step_size must be positive when provided.")

    splits: list[WalkForwardSplit] = []
    anchor = train_window
    split_id = 0
    while True:
        train_end = anchor
        validation_start = train_end
        validation_end = validation_start + validation_window
        test_start = validation_end
        test_end = test_start + test_window
        if test_end > len(unique_dates):
            break

        train_start = 0 if expanding else train_end - train_window
        train_dates = tuple(unique_dates[train_start:train_end])
        validation_dates = tuple(unique_dates[validation_start:validation_end])
        test_dates = tuple(unique_dates[test_start:test_end])

        split = WalkForwardSplit(
            split_id=split_id,
            train_dates=train_dates,
            validation_dates=validation_dates,
            test_dates=test_dates,
            train_indices=_row_indices_for_dates(prepared, date_col, train_dates),
            validation_indices=_row_indices_for_dates(prepared, date_col, validation_dates),
            test_indices=_row_indices_for_dates(prepared, date_col, test_dates),
            expanding=expanding,
        )
        splits.append(split)

        split_id += 1
        if max_splits is not None and len(splits) >= max_splits:
            break
        anchor += step

    return splits


def summarize_walk_forward_splits(splits: list[WalkForwardSplit]) -> dict[str, Any]:
    """Return a compact summary of generated walk-forward folds."""

    return {
        "split_count": len(splits),
        "split_ids": [split.split_id for split in splits],
        "train_date_counts": [len(split.train_dates) for split in splits],
        "validation_date_counts": [len(split.validation_dates) for split in splits],
        "test_date_counts": [len(split.test_dates) for split in splits],
    }


def _prepare_frame(data: pd.DataFrame, *, date_col: str) -> pd.DataFrame:
    if date_col not in data.columns:
        raise WalkForwardSplitError(f"Input data must contain date column '{date_col}'.")
    frame = data.copy()
    frame[date_col] = pd.to_datetime(frame[date_col]).dt.date
    return frame.sort_values(date_col, kind="stable").reset_index(drop=True)


def _row_indices_for_dates(data: pd.DataFrame, date_col: str, dates: tuple[date, ...]) -> tuple[int, ...]:
    if not dates:
        return tuple()
    mask = data[date_col].isin(dates)
    return tuple(int(index) for index in data.index[mask].tolist())
