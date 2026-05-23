from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.models.training import (  # noqa: E402
    TrainingContractError,
    fit_fold_preprocessor,
)


def test_fold_preprocessor_fits_on_train_rows_only() -> None:
    frame = pd.DataFrame(
        {
            "split_role": ["train", "train", "train"],
            "preprocessing_fit_allowed": [True, True, True],
            "x1": [1.0, None, 3.0],
            "x2": [2.0, 4.0, 6.0],
        }
    )

    preprocessor = fit_fold_preprocessor(frame, feature_columns=["x1", "x2"], policy="median_impute_scale")
    transformed = preprocessor.transform(frame)
    payload = preprocessor.parameter_payload()

    assert transformed.shape == (3, 2)
    assert payload["fit_row_count"] == 3
    assert payload["parameter_digest"]


def test_fold_preprocessor_rejects_validation_rows() -> None:
    frame = pd.DataFrame(
        {
            "split_role": ["train", "validation"],
            "preprocessing_fit_allowed": [True, False],
            "x1": [1.0, 2.0],
        }
    )

    with pytest.raises(TrainingContractError, match="train rows only"):
        fit_fold_preprocessor(frame, feature_columns=["x1"], policy="median_impute")


def test_fold_preprocessor_rejects_fit_disallowed_train_rows() -> None:
    frame = pd.DataFrame(
        {
            "split_role": ["train", "train"],
            "preprocessing_fit_allowed": [True, False],
            "x1": [1.0, 2.0],
        }
    )

    with pytest.raises(TrainingContractError, match="permit preprocessing fit"):
        fit_fold_preprocessor(frame, feature_columns=["x1"], policy="median_impute")
