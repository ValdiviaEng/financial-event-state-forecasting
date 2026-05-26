from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.features import build_market_lag_features, validate_feature_label_split_compatibility  # noqa: E402
from event_state_forecasting.v1p0.modeling import run_fixed_xgboost_or_blocker, run_lag_linear_predictions, validate_prediction_schema  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402


def test_feature_builder_compatibility_and_lag_linear_prediction_schema() -> None:
    feature_config = load_json_config(PROJECT_ROOT / "configs" / "market_features_v1p0.yaml")
    model_config = load_json_config(PROJECT_ROOT / "configs" / "models_v1p0.yaml")
    frame = _training_frame(feature_config)
    row_key = feature_config["row_key"]

    compatibility = validate_feature_label_split_compatibility(
        frame[row_key].drop_duplicates().copy(),
        frame[row_key].drop_duplicates().copy(),
        frame[row_key].drop_duplicates().copy(),
        row_key,
    )
    predictions = run_lag_linear_predictions(frame, _feature_columns(frame), model_config["models"][0])
    schema_result = validate_prediction_schema(predictions, model_config["saved_prediction_schema"]["required_columns"])

    assert compatibility["joined_rows"] == len(frame)
    assert schema_result["prediction_rows"] == 2
    assert set(predictions["split_role"]) == {"validation", "lockbox"}
    assert set(predictions["model_id"]) == {"market_lag_linear_v1"}


def test_fixed_xgboost_records_dependency_blocker_when_missing() -> None:
    feature_config = load_json_config(PROJECT_ROOT / "configs" / "market_features_v1p0.yaml")
    model_config = load_json_config(PROJECT_ROOT / "configs" / "models_v1p0.yaml")
    frame = _training_frame(feature_config)

    result = run_fixed_xgboost_or_blocker(frame, _feature_columns(frame), model_config["models"][1])

    if isinstance(result, dict):
        assert result["status"] == "blocked_missing_dependency"
        assert result["missing_dependency"] == "xgboost"
    else:
        assert set(result["model_id"]) == {"market_xgboost_v1_fixed"}
        schema_result = validate_prediction_schema(result, model_config["saved_prediction_schema"]["required_columns"])
        assert schema_result["prediction_rows"] == 2


def _training_frame(feature_config: dict) -> pd.DataFrame:
    rows = []
    closes = [100.0, 101.0, 103.0, 106.0, 110.0, 111.0, 113.0, 114.0]
    roles = ["train", "train", "train", "train", "train", "train", "validation", "lockbox"]
    for index, (close, role) in enumerate(zip(closes, roles), start=1):
        rows.append(
            {
                "row_key": f"phase1_top50_v1p0|AAPL|2025-01-0{index}|1d",
                "benchmark_family_id": "phase1_top50_v1p0",
                "canonical_ticker": "AAPL",
                "as_of_date": f"2025-01-0{index}",
                "horizon_id": "1d",
                "fold_id": "fold_001",
                "split_role": role,
                "dataset_version": "toy_dataset_v1",
                "feature_artifact_version": "market_lag_features_v1p0_smoke",
                "split_artifact_version": "toy_splits_v1",
                "market_open": close - 1.0,
                "market_high": close + 2.0,
                "market_low": close - 2.0,
                "market_close": close,
                "market_volume": 1000 + index,
                "benchmark_close": close - 10.0,
                "target": 0.001 * index,
            }
        )
    base = pd.DataFrame(rows)
    features = build_market_lag_features(base, feature_config)
    return base.merge(features, on=[*feature_config["row_key"], "dataset_version"], how="left")


def _feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if "_lag_" in column or "_rolling_" in column]
