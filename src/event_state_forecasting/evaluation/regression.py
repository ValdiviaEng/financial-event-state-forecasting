"""Stage 6 primary regression metric computation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd


KEY_COLUMNS = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
PREDICTION_ID_COLUMNS = ["row_key", "fold_id", "split_role", "model_id"]
TARGET_COLUMN = "forward_excess_return"
METRIC_GROUP_COLUMNS = ["aggregation_level", "split_role", "fold_id", "horizon_id", "model_id", "model_family", "branch"]


class MetricContractError(ValueError):
    """Raised when saved predictions and labels cannot support Stage 6 metrics."""


def align_predictions_with_labels(predictions: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    """Join saved out-of-sample predictions to frozen labels under row-key discipline."""

    required_predictions = {
        "row_key",
        "benchmark_family_id",
        "canonical_ticker",
        "as_of_date",
        "horizon_id",
        "fold_id",
        "split_role",
        "model_id",
        "model_family",
        "branch",
        "dataset_version",
        "prediction",
    }
    required_labels = {*KEY_COLUMNS, "dataset_version", TARGET_COLUMN, "label_available_flag"}
    missing_predictions = required_predictions - set(predictions.columns)
    missing_labels = required_labels - set(labels.columns)
    if missing_predictions:
        raise MetricContractError(f"predictions missing columns: {sorted(missing_predictions)}")
    if missing_labels:
        raise MetricContractError(f"labels missing columns: {sorted(missing_labels)}")
    if set(predictions["split_role"].unique()) - {"validation", "lockbox"}:
        raise MetricContractError("Stage 6 metrics may only consume validation and lockbox predictions")
    if predictions.duplicated(PREDICTION_ID_COLUMNS).any():
        raise MetricContractError("duplicate prediction rows detected")

    label_subset = labels.loc[:, [*KEY_COLUMNS, "dataset_version", TARGET_COLUMN, "label_available_flag"]].copy()
    if label_subset.duplicated([*KEY_COLUMNS, "dataset_version"]).any():
        raise MetricContractError("frozen labels contain duplicate row keys")
    if not bool(label_subset["label_available_flag"].all()):
        raise MetricContractError("Stage 6 requires frozen available labels")

    aligned = predictions.merge(
        label_subset,
        on=[*KEY_COLUMNS, "dataset_version"],
        how="left",
        validate="many_to_one",
    )
    if aligned[TARGET_COLUMN].isna().any():
        raise MetricContractError("saved predictions failed to align with frozen labels")
    aligned["prediction_error"] = aligned["prediction"].astype("float64") - aligned[TARGET_COLUMN].astype("float64")
    aligned["squared_error"] = aligned["prediction_error"] ** 2
    aligned["absolute_error"] = aligned["prediction_error"].abs()
    return aligned


def compute_regression_metrics(aligned_predictions: pd.DataFrame, config: Mapping[str, Any]) -> pd.DataFrame:
    """Compute RMSE, MAE, and zero-baseline out-of-sample R2."""

    metric_policy = config["metric_policy"]
    r2_baseline_model_id = str(metric_policy["r2_baseline_model_id"])
    records: list[dict[str, Any]] = []
    for aggregation_level, group_columns in [
        ("fold", ["split_role", "fold_id", "horizon_id", "model_id", "model_family", "branch"]),
        ("aggregate", ["split_role", "horizon_id", "model_id", "model_family", "branch"]),
    ]:
        for keys, group in aligned_predictions.groupby(group_columns, sort=True):
            key_values = dict(zip(group_columns, keys if isinstance(keys, tuple) else (keys,)))
            if aggregation_level == "aggregate":
                key_values["fold_id"] = "ALL"
            records.append(
                {
                    "aggregation_level": aggregation_level,
                    "split_role": str(key_values["split_role"]),
                    "fold_id": str(key_values["fold_id"]),
                    "horizon_id": str(key_values["horizon_id"]),
                    "model_id": str(key_values["model_id"]),
                    "model_family": str(key_values["model_family"]),
                    "branch": str(key_values["branch"]),
                    **_metric_values(group, r2_baseline_model_id=r2_baseline_model_id),
                }
            )
    return pd.DataFrame.from_records(records).sort_values(METRIC_GROUP_COLUMNS).reset_index(drop=True)


def select_market_hurdles(metrics: pd.DataFrame, config: Mapping[str, Any]) -> dict[str, str]:
    """Select the strict market-only hurdle per horizon using the frozen rule."""

    candidates = set(str(value) for value in config["metric_policy"]["market_hurdle_candidates"])
    validation = metrics[
        (metrics["aggregation_level"] == "aggregate")
        & (metrics["split_role"] == "validation")
        & (metrics["branch"] == "market_only")
        & (metrics["model_id"].isin(candidates))
    ].copy()
    if validation.empty:
        raise MetricContractError("no validation market-only metrics available for hurdle selection")
    selected: dict[str, str] = {}
    for horizon_id, group in validation.groupby("horizon_id", sort=True):
        ranked = group.sort_values(["rmse", "mae", "model_id"], ascending=[True, True, True])
        selected[str(horizon_id)] = str(ranked.iloc[0]["model_id"])
    return selected


def attach_loss_differences(metrics: pd.DataFrame, paired_comparisons: pd.DataFrame) -> pd.DataFrame:
    """Attach predeclared mean loss differences versus the selected market hurdle."""

    delta_columns = [
        "aggregation_level",
        "split_role",
        "fold_id",
        "horizon_id",
        "model_id",
        "baseline_model_id",
        "mean_squared_loss_diff",
        "mean_absolute_loss_diff",
    ]
    merged = metrics.merge(
        paired_comparisons.loc[:, delta_columns],
        on=["aggregation_level", "split_role", "fold_id", "horizon_id", "model_id"],
        how="left",
        validate="one_to_one",
    )
    if merged["mean_squared_loss_diff"].isna().any() or merged["mean_absolute_loss_diff"].isna().any():
        raise MetricContractError("loss-difference attachment left missing metric rows")
    return merged.sort_values(METRIC_GROUP_COLUMNS).reset_index(drop=True)


def _metric_values(group: pd.DataFrame, *, r2_baseline_model_id: str) -> dict[str, float | int | str]:
    actual = group[TARGET_COLUMN].astype("float64").to_numpy()
    squared_error = group["squared_error"].astype("float64").to_numpy()
    absolute_error = group["absolute_error"].astype("float64").to_numpy()
    denominator = float(np.sum(actual**2))
    sum_squared_error = float(np.sum(squared_error))
    r2_oos = float("nan") if denominator == 0.0 else 1.0 - (sum_squared_error / denominator)
    return {
        "row_count": int(len(group)),
        "target_mean": float(np.mean(actual)),
        "prediction_mean": float(group["prediction"].astype("float64").mean()),
        "mean_squared_error": float(np.mean(squared_error)),
        "rmse": float(np.sqrt(np.mean(squared_error))),
        "mae": float(np.mean(absolute_error)),
        "r2_oos": r2_oos,
        "r2_baseline_model_id": r2_baseline_model_id,
    }
