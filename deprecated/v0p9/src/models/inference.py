"""Stage 5 saved-prediction schema helpers."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd


PREDICTION_SCHEMA_VERSION = "stage5_saved_predictions_v1"
ROW_KEY_COLUMNS = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
REQUIRED_PREDICTION_COLUMNS = [
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
    "feature_artifact_version",
    "split_artifact_version",
    "stage5_artifact_version",
    "prediction",
]
ALLOWED_PREDICTION_ROLES = {"validation", "lockbox"}


class SavedPredictionSchemaError(ValueError):
    """Raised when saved predictions violate the Stage 5 schema."""


def make_row_key(frame: pd.DataFrame) -> pd.Series:
    return frame[ROW_KEY_COLUMNS].astype(str).agg("|".join, axis=1)


def build_prediction_frame(
    rows: pd.DataFrame,
    predictions: np.ndarray,
    *,
    model_id: str,
    model_family: str,
    branch: str,
    feature_artifact_version: str,
    split_artifact_version: str,
    stage5_artifact_version: str,
) -> pd.DataFrame:
    if len(rows) != len(predictions):
        raise SavedPredictionSchemaError("prediction length does not match row count")
    output = rows.loc[
        :,
        [
            "benchmark_family_id",
            "canonical_ticker",
            "as_of_date",
            "horizon_id",
            "fold_id",
            "split_role",
            "dataset_version",
        ],
    ].copy()
    output.insert(0, "row_key", make_row_key(output))
    output["model_id"] = model_id
    output["model_family"] = model_family
    output["branch"] = branch
    output["feature_artifact_version"] = feature_artifact_version
    output["split_artifact_version"] = split_artifact_version
    output["stage5_artifact_version"] = stage5_artifact_version
    output["prediction"] = np.asarray(predictions, dtype="float64")
    return output.loc[:, REQUIRED_PREDICTION_COLUMNS]


def validate_saved_predictions(
    predictions: pd.DataFrame,
    *,
    expected_model_ids: Iterable[str] | None = None,
) -> None:
    missing = [column for column in REQUIRED_PREDICTION_COLUMNS if column not in predictions.columns]
    if missing:
        raise SavedPredictionSchemaError(f"missing prediction columns: {missing}")
    roles = set(predictions["split_role"].unique())
    if roles - ALLOWED_PREDICTION_ROLES:
        raise SavedPredictionSchemaError(f"predictions include forbidden split roles: {sorted(roles - ALLOWED_PREDICTION_ROLES)}")
    if predictions["prediction"].isna().any():
        raise SavedPredictionSchemaError("predictions contain null values")
    if not np.isfinite(predictions["prediction"].to_numpy(dtype="float64")).all():
        raise SavedPredictionSchemaError("predictions contain non-finite values")
    duplicate_subset = ["row_key", "fold_id", "model_id", "split_role"]
    if predictions.duplicated(duplicate_subset).any():
        raise SavedPredictionSchemaError("duplicate saved predictions detected")
    if expected_model_ids is not None:
        observed = set(str(value) for value in predictions["model_id"].unique())
        expected = set(str(value) for value in expected_model_ids)
        if observed != expected:
            raise SavedPredictionSchemaError(f"model id mismatch: observed={sorted(observed)} expected={sorted(expected)}")
