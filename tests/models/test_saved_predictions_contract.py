from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.models.inference import (  # noqa: E402
    SavedPredictionSchemaError,
    build_prediction_frame,
    validate_saved_predictions,
)


def test_saved_prediction_schema_accepts_validation_and_lockbox_rows() -> None:
    rows = _rows()
    predictions = build_prediction_frame(
        rows,
        np.array([0.1, -0.1]),
        model_id="market_ridge",
        model_family="ridge",
        branch="market_only",
        feature_artifact_version="features_v1",
        split_artifact_version="splits_v1",
        stage5_artifact_version="models_v1",
    )

    validate_saved_predictions(predictions, expected_model_ids=["market_ridge"])

    assert set(predictions["split_role"]) == {"validation", "lockbox"}
    assert predictions["row_key"].notna().all()


def test_saved_prediction_schema_rejects_train_predictions() -> None:
    rows = _rows()
    rows.loc[0, "split_role"] = "train"
    predictions = build_prediction_frame(
        rows,
        np.array([0.1, -0.1]),
        model_id="market_ridge",
        model_family="ridge",
        branch="market_only",
        feature_artifact_version="features_v1",
        split_artifact_version="splits_v1",
        stage5_artifact_version="models_v1",
    )

    with pytest.raises(SavedPredictionSchemaError, match="forbidden split roles"):
        validate_saved_predictions(predictions, expected_model_ids=["market_ridge"])


def test_saved_prediction_schema_rejects_duplicates() -> None:
    rows = _rows()
    rows.loc[1, "canonical_ticker"] = "AAPL"
    rows.loc[1, "as_of_date"] = "2025-01-01"
    rows.loc[1, "split_role"] = "validation"
    predictions = build_prediction_frame(
        rows,
        np.array([0.1, -0.1]),
        model_id="market_ridge",
        model_family="ridge",
        branch="market_only",
        feature_artifact_version="features_v1",
        split_artifact_version="splits_v1",
        stage5_artifact_version="models_v1",
    )

    with pytest.raises(SavedPredictionSchemaError, match="duplicate"):
        validate_saved_predictions(predictions, expected_model_ids=["market_ridge"])


def _rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "benchmark_family_id": ["phase1_top50", "phase1_top50"],
            "canonical_ticker": ["AAPL", "MSFT"],
            "as_of_date": ["2025-01-01", "2025-10-01"],
            "horizon_id": ["1d", "1d"],
            "fold_id": ["fold_001", "fold_001"],
            "split_role": ["validation", "lockbox"],
            "dataset_version": ["dataset_v1", "dataset_v1"],
        }
    )
