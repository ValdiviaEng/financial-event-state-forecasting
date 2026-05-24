"""Stage 4 final untouched lockbox boundary helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence


class LockboxError(ValueError):
    """Raised when a lockbox boundary cannot be defined safely."""


@dataclass(frozen=True, slots=True)
class LockboxBoundary:
    policy: str
    start_date: str
    end_date: str
    start_index: int
    date_count: int
    total_date_count: int
    access_policy: str

    def to_record(self, *, row_count: int) -> dict[str, Any]:
        return {
            "policy": self.policy,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "start_index": self.start_index,
            "date_count": self.date_count,
            "row_count": row_count,
            "total_date_count": self.total_date_count,
            "access_policy": self.access_policy,
            "forbidden_uses": [
                "hyperparameter_tuning",
                "model_selection",
                "feature_selection",
                "clean_window_selection",
                "provider_policy_selection",
                "metric_selection",
                "threshold_selection",
                "debugging_by_repeated_result_inspection",
            ],
            "allowed_uses": [
                "final_reporting_after_development_freeze",
                "validation_to_lockbox_degradation_report",
                "comparison_summary_from_saved_predictions",
            ],
        }


def define_lockbox_boundary(
    dates: Sequence[str],
    *,
    fraction: float,
    expected_start_date: str | None = None,
    explicit_start_date: str | None = None,
) -> LockboxBoundary:
    unique_dates = sorted(dict.fromkeys(str(value) for value in dates))
    if len(unique_dates) < 2:
        raise LockboxError("at least two dates are required to define a lockbox")

    if explicit_start_date:
        if explicit_start_date not in unique_dates:
            raise LockboxError(f"explicit lockbox start date is not in label dates: {explicit_start_date}")
        start_index = unique_dates.index(explicit_start_date)
        policy = "explicit_final_untouched_start_date"
    else:
        if not 0 < fraction < 1:
            raise LockboxError("lockbox fraction must be between 0 and 1")
        start_index = int(len(unique_dates) * (1 - fraction))
        policy = "final_untouched_fraction_of_stage3_as_of_dates"
    if start_index <= 0 or start_index >= len(unique_dates):
        raise LockboxError("lockbox fraction leaves no development or lockbox dates")
    start_date = unique_dates[start_index]
    if expected_start_date and start_date != expected_start_date:
        raise LockboxError(f"lockbox start date {start_date} does not match expected {expected_start_date}")

    return LockboxBoundary(
        policy=policy,
        start_date=start_date,
        end_date=unique_dates[-1],
        start_index=start_index,
        date_count=len(unique_dates) - start_index,
        total_date_count=len(unique_dates),
        access_policy="reporting_only_after_development_freeze",
    )
