from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.models.comparator_ladder import (  # noqa: E402
    ComparatorLadderError,
    freeze_comparator_ladder,
    validate_model_config,
)


def test_comparator_ladder_freezes_approved_roster() -> None:
    config = _model_config()

    specs = validate_model_config(config)
    record = freeze_comparator_ladder(config)

    assert [spec.model_id for spec in specs] == ["market_ridge", "event_state_gated_fusion"]
    assert record["roster_id"] == "test_roster"
    assert record["benchmark_claim"] is False
    assert record["allowed_inputs"]["market_ridge"] == ["market_features"]
    assert record["allowed_inputs"]["event_state_gated_fusion"] == ["market_features", "event_state_features"]


def test_comparator_ladder_rejects_market_model_with_event_state_inputs() -> None:
    config = _model_config()
    config["comparator_ladder"]["models"][0]["allowed_inputs"] = ["market_features", "event_state_features"]

    with pytest.raises(ComparatorLadderError, match="market-only model has invalid inputs"):
        validate_model_config(config)


def test_comparator_ladder_rejects_unapproved_family() -> None:
    config = _model_config()
    config["comparator_ladder"]["models"][0]["family"] = "graph_moe"

    with pytest.raises(ComparatorLadderError, match="unapproved model family"):
        validate_model_config(config)


def _model_config() -> dict[str, object]:
    return {
        "artifact_schema_version": "stage5_models_v1",
        "comparator_ladder": {
            "roster_id": "test_roster",
            "seed": 1729,
            "search_policy": "tiny_fixed_no_hyperparameter_search",
            "prediction_scope": "development_validation_plus_lockbox_no_metrics",
            "models": [
                {
                    "model_id": "market_ridge",
                    "family": "ridge",
                    "branch": "market_only",
                    "allowed_inputs": ["market_features"],
                    "preprocessing": "median_impute_scale",
                    "params": {"alpha": 1.0},
                },
                {
                    "model_id": "event_state_gated_fusion",
                    "family": "simple_gated_fusion",
                    "branch": "event_state",
                    "allowed_inputs": ["market_features", "event_state_features"],
                    "preprocessing": "median_impute_scale",
                    "params": {"alpha": 1.0},
                },
            ],
        },
    }
