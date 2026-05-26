from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.xgboost_search import (  # noqa: E402
    V1P0XGBoostSearchError,
    select_best_stage22_trial,
    validate_stage22_prediction_schema,
    validate_stage22_trial_ledger_schema,
)


def test_stage22_trial_ledger_schema_allows_completed_and_failed_trials() -> None:
    ledger = pd.DataFrame.from_records(
        [
            _ledger_row(1, "completed", -0.001, ""),
            _ledger_row(2, "failed", float("nan"), "synthetic failure"),
        ]
    )

    result = validate_stage22_trial_ledger_schema(ledger)

    assert result == {"trial_count": 2, "completed_trial_count": 1, "failed_trial_count": 1}


def test_stage22_best_trial_selection_uses_development_objective_only() -> None:
    ledger = pd.DataFrame.from_records(
        [
            _ledger_row(1, "completed", 0.002, ""),
            _ledger_row(2, "completed", -0.003, ""),
            _ledger_row(3, "completed", -0.001, ""),
        ]
    )

    best = select_best_stage22_trial(ledger)

    assert best["trial_id"] == 2
    assert best["objective_value"] == pytest.approx(-0.003)
    assert best["lockbox_rows_used"] == 0


def test_stage22_prediction_schema_rejects_lockbox_rows() -> None:
    predictions = pd.DataFrame.from_records(
        [
            {"trial_id": 1, "fold_id": "fold_001", "horizon_id": "1d", "split_role": "validation", "row_key": "rk1", "prediction": 0.1, "target": 0.2},
            {"trial_id": 1, "fold_id": "fold_001", "horizon_id": "1d", "split_role": "lockbox", "row_key": "rk2", "prediction": 0.1, "target": 0.2},
        ]
    )

    with pytest.raises(V1P0XGBoostSearchError, match="validation-only"):
        validate_stage22_prediction_schema(predictions)


def _ledger_row(trial_id: int, status: str, objective_value: float, failure_reason: str) -> dict:
    return {
        "trial_id": trial_id,
        "phase_id": "phase1_random",
        "status": status,
        "objective_value": objective_value,
        "base_hurdle_delta": objective_value,
        "total_penalty": 0.0,
        "lockbox_rows_used": 0,
        "params_json": json.dumps({"max_depth": 3}, sort_keys=True),
        "failure_reason": failure_reason,
    }
