from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.xgboost_search import classify_stage24_candidate, validate_stage24_frontier_schema  # noqa: E402


def test_stage24_frontier_schema_requires_complexity_and_gap_columns() -> None:
    frontier = pd.DataFrame.from_records(
        [
            {
                "trial_id": 1,
                "phase_id": "phase2_optuna_tpe",
                "objective_value": 0.001,
                "n_estimators": 100,
                "max_depth": 3,
                "train_rmse_mean": 0.05,
                "validation_rmse_mean": 0.06,
                "validation_to_train_rmse_ratio": 1.2,
            }
        ]
    )

    assert validate_stage24_frontier_schema(frontier) == {"frontier_rows": 1, "trial_count": 1}


def test_stage24_candidate_classification_is_conservative() -> None:
    blocked = classify_stage24_candidate(1.0, 1.0, 0.0, lockbox_used_for_selection=True)
    weak = classify_stage24_candidate(0.4, 0.9, 0.0, lockbox_used_for_selection=False)
    reportable = classify_stage24_candidate(0.58, 0.95, 0.33, lockbox_used_for_selection=False)

    assert blocked["classification"] == "blocked"
    assert weak["classification"] == "exploratory_only"
    assert reportable == {
        "classification": "lockbox_reported_candidate",
        "promotion_review_recommended": True,
        "reason": "candidate cleared conservative validation/lockbox rate floors without lockbox selection",
    }
