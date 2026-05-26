from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.modeling import validate_prediction_schema  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402


def test_stage23_best_config_was_selected_without_lockbox() -> None:
    config_path = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/best_development_candidate_config.json"
    best_config = json.loads(config_path.read_text(encoding="utf-8"))

    assert best_config["model_id"] == "market_xgboost_v2_frozen_final_pending_stage23"
    assert best_config["selection_basis"] == "development_validation_guarded_hurdle_delta_only"
    assert best_config["lockbox_used_for_selection"] is False
    assert best_config["selected_trial_id"] == 211


def test_stage23_frozen_final_saved_prediction_schema_allows_targets_for_metrics() -> None:
    required_columns = load_json_config(PROJECT_ROOT / "configs" / "models_v1p0.yaml")["saved_prediction_schema"]["required_columns"]
    predictions = pd.DataFrame.from_records(
        [
            {
                "row_key": "phase1_top50_v1p0|AAPL|2025-01-01|1d",
                "benchmark_family_id": "phase1_top50_v1p0",
                "canonical_ticker": "AAPL",
                "as_of_date": "2025-01-01",
                "horizon_id": "1d",
                "fold_id": "fold_001",
                "split_role": "lockbox",
                "model_id": "market_xgboost_v2_frozen_final",
                "model_family": "xgboost_regressor",
                "branch": "market_only",
                "dataset_version": "toy_dataset_v1",
                "feature_artifact_version": "toy_features_v1",
                "split_artifact_version": "toy_splits_v1",
                "v1p0_artifact_version": "toy_stage23_v1",
                "prediction": 0.01,
                "target": 0.02,
            }
        ]
    )

    result = validate_prediction_schema(predictions, required_columns)

    assert result == {"prediction_rows": 1, "model_count": 1}
