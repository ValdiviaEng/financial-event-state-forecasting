from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402
from event_state_forecasting.v1p0.xgboost_search import (  # noqa: E402
    canonical_search_digest,
    compute_guarded_hurdle_objective,
    validate_xgboost_search_config,
)


def test_stage21_search_config_is_frozen_and_forbids_lockbox() -> None:
    config = _config()
    validated = validate_xgboost_search_config(config)

    assert validated["candidate_model_id"] == "market_xgboost_v2_nested_optuna_candidate"
    assert validated["hurdle_model_id"] == "market_xgboost_v1_fixed"
    assert validated["objective"]["horizon_weights"] == {"1d": 0.30, "5d": 0.25, "10d": 0.20, "20d": 0.15, "60d": 0.10}
    assert validated["objective"]["metric_weights"] == {"rmse": 0.50, "mae": 0.50}
    assert "lockbox" not in validated["allowed_tuning_split_roles"]
    assert "lockbox" in validated["forbidden_tuning_split_roles"]
    assert validated["budgets"]["max_total_trials"] == 400
    assert len(validated["config_digest_sha256"]) == 64


def test_guarded_objective_is_deterministic_and_ignores_lockbox_rows() -> None:
    config = _config()
    metrics = _metrics(candidate_rmse_delta=-0.002, candidate_mae_delta=-0.001)

    objective = compute_guarded_hurdle_objective(metrics, config)
    changed_lockbox = metrics.copy()
    changed_lockbox.loc[changed_lockbox["split_role"] == "lockbox", ["rmse", "mae"]] = 999.0
    objective_after_lockbox_change = compute_guarded_hurdle_objective(changed_lockbox, config)

    assert objective["objective_value"] == objective_after_lockbox_change["objective_value"]
    assert objective["lockbox_rows_used"] == 0
    assert objective["base_hurdle_delta"] < 0.0
    assert objective["penalties"]["one_sided_improvement"] == 0.0


def test_guarded_objective_penalizes_one_sided_metric_gains() -> None:
    config = _config()
    metrics = _metrics(candidate_rmse_delta=-0.002, candidate_mae_delta=0.002)

    objective = compute_guarded_hurdle_objective(metrics, config)

    assert objective["penalties"]["one_sided_improvement"] > 0.0
    assert objective["objective_value"] > objective["base_hurdle_delta"]


def test_search_config_digest_is_order_stable() -> None:
    config = _config()
    copied = json.loads(json.dumps(config, sort_keys=True))

    assert canonical_search_digest(config) == canonical_search_digest(copied)


def _config() -> dict:
    return load_json_config(PROJECT_ROOT / "configs" / "xgboost_search_v1p0.yaml")


def _metrics(candidate_rmse_delta: float, candidate_mae_delta: float) -> pd.DataFrame:
    rows = []
    horizons = ["1d", "5d", "10d", "20d", "60d"]
    for fold_index, fold_id in enumerate(["fold_001", "fold_002"], start=1):
        for horizon_index, horizon_id in enumerate(horizons, start=1):
            hurdle_rmse = 0.030 + 0.001 * horizon_index + 0.0001 * fold_index
            hurdle_mae = 0.020 + 0.001 * horizon_index + 0.0001 * fold_index
            candidate_rmse = hurdle_rmse + candidate_rmse_delta
            candidate_mae = hurdle_mae + candidate_mae_delta
            rows.extend(
                [
                    {"split_role": "train", "fold_id": fold_id, "horizon_id": horizon_id, "model_id": "market_xgboost_v2_nested_optuna_candidate", "rmse": candidate_rmse * 0.90, "mae": candidate_mae * 0.90},
                    {"split_role": "train", "fold_id": fold_id, "horizon_id": horizon_id, "model_id": "market_xgboost_v1_fixed", "rmse": hurdle_rmse * 0.90, "mae": hurdle_mae * 0.90},
                    {"split_role": "validation", "fold_id": fold_id, "horizon_id": horizon_id, "model_id": "market_xgboost_v2_nested_optuna_candidate", "rmse": candidate_rmse, "mae": candidate_mae},
                    {"split_role": "validation", "fold_id": fold_id, "horizon_id": horizon_id, "model_id": "market_xgboost_v1_fixed", "rmse": hurdle_rmse, "mae": hurdle_mae},
                    {"split_role": "lockbox", "fold_id": fold_id, "horizon_id": horizon_id, "model_id": "market_xgboost_v2_nested_optuna_candidate", "rmse": 1.0, "mae": 1.0},
                    {"split_role": "lockbox", "fold_id": fold_id, "horizon_id": horizon_id, "model_id": "market_xgboost_v1_fixed", "rmse": 1.0, "mae": 1.0},
                ]
            )
    return pd.DataFrame.from_records(rows)
