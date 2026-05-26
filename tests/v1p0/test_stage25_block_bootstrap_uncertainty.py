from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.xgboost_search import (  # noqa: E402
    build_stage25_paired_loss_table,
    moving_block_resample_indices,
    stage25_delta_intervals,
    stage25_generalization_gap_intervals,
    validate_stage25_paired_loss_schema,
)


def test_stage25_paired_loss_table_schema_and_loss_deltas() -> None:
    candidate, hurdle = _toy_predictions(candidate_validation_error=0.05, hurdle_validation_error=0.10)

    paired = build_stage25_paired_loss_table(candidate, hurdle)

    schema = validate_stage25_paired_loss_schema(paired)
    assert schema["paired_loss_rows"] == len(paired)
    assert set(schema["split_roles"]) == {"lockbox", "train", "validation"}
    validation = paired[paired["split_role"] == "validation"]
    assert validation["absolute_error_delta_candidate_minus_hurdle"].mean() < 0.0
    assert validation["squared_error_delta_candidate_minus_hurdle"].mean() < 0.0


def test_stage25_moving_block_bootstrap_is_deterministic_and_ordered() -> None:
    candidate, hurdle = _toy_predictions(candidate_validation_error=0.05, hurdle_validation_error=0.10)
    paired = build_stage25_paired_loss_table(candidate, hurdle)

    first_indices = moving_block_resample_indices(n_blocks=5, block_length=2, resample_count=4, seed=123)
    second_indices = moving_block_resample_indices(n_blocks=5, block_length=2, resample_count=4, seed=123)
    first = stage25_delta_intervals(paired, block_length=2, resample_count=50, seed=123, split_roles=("validation",), method="moving_block_bootstrap")
    second = stage25_delta_intervals(paired, block_length=2, resample_count=50, seed=123, split_roles=("validation",), method="moving_block_bootstrap")

    assert (first_indices == second_indices).all()
    assert first.to_dict("records") == second.to_dict("records")
    assert (first["ci_low"] <= first["ci_high"]).all()
    assert (first["probability_candidate_improves"] >= 0.9).all()


def test_stage25_generalization_gap_flags_train_to_oos_degradation() -> None:
    candidate, hurdle = _toy_predictions(candidate_validation_error=0.30, hurdle_validation_error=0.32, candidate_train_error=0.05)
    paired = build_stage25_paired_loss_table(candidate, hurdle)

    gaps = stage25_generalization_gap_intervals(paired, block_length=2, resample_count=50, seed=456, oos_roles=("validation",))

    assert not gaps.empty
    assert (gaps["observed_oos_minus_train"] > 0.0).all()
    assert (gaps["observed_oos_to_train_ratio"] > 1.25).all()
    assert gaps["diagnostic_overfit_pressure_flag"].any()


def _toy_predictions(candidate_validation_error: float, hurdle_validation_error: float, candidate_train_error: float = 0.03) -> tuple[pd.DataFrame, pd.DataFrame]:
    candidate_rows: list[dict[str, object]] = []
    hurdle_rows: list[dict[str, object]] = []
    split_errors = {
        "train": (candidate_train_error, 0.09),
        "validation": (candidate_validation_error, hurdle_validation_error),
        "lockbox": (candidate_validation_error * 1.1, hurdle_validation_error * 1.1),
    }
    for split_role, (candidate_error, hurdle_error) in split_errors.items():
        for day in range(1, 6):
            for ticker in ("AAA", "BBB"):
                row_key = f"toy|{ticker}|2025-01-{day:02d}|1d"
                base = {
                    "row_key": row_key,
                    "benchmark_family_id": "phase1_top50_v1p0",
                    "canonical_ticker": ticker,
                    "as_of_date": f"2025-01-{day:02d}",
                    "horizon_id": "1d",
                    "fold_id": "fold_001",
                    "split_role": split_role,
                    "dataset_version": "toy_dataset_v1",
                    "feature_artifact_version": "toy_features_v1",
                    "split_artifact_version": "toy_splits_v1",
                    "v1p0_artifact_version": "toy_stage25_v1",
                }
                target = 1.0
                candidate_rows.append({**base, "target": target, "model_id": "market_xgboost_v2_frozen_final", "model_family": "xgboost_regressor", "branch": "market_only", "prediction": target - candidate_error})
                hurdle_rows.append({**base, "model_id": "market_xgboost_v1_fixed", "model_family": "xgboost_regressor", "branch": "market_only", "prediction": target - hurdle_error})
    return pd.DataFrame.from_records(candidate_rows), pd.DataFrame.from_records(hurdle_rows)
