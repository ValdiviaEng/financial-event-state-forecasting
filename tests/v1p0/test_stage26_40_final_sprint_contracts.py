from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    TSMIXER_ARCHITECTURE_VERSION,
    TSMIXER_READOUT_POLICY,
    _CompactTSMixer,
    _build_sequence_tensors,
    compute_pairwise_deltas,
    deterministic_projection_matrix,
    normalize_article_text,
    sha256_text,
    stage32_search_space_contract,
    stable_digest,
    xgboost_only_allowed_language,
    xgboost_only_branch_status_records,
)


def test_stage26_text_normalization_and_hash_are_deterministic() -> None:
    text = normalize_article_text("  Stocks   rallied ", " Pound\n gained. ")

    assert text == "Stocks rallied\n\nPound gained."
    assert sha256_text(text) == sha256_text(normalize_article_text("Stocks rallied", "Pound gained."))


def test_stage28_projection_matrix_is_deterministic() -> None:
    first = deterministic_projection_matrix(5, output_dim=3, seed=123)
    second = deterministic_projection_matrix(5, output_dim=3, seed=123)

    assert first.shape == (5, 3)
    assert (first == second).all()


def test_stage29_pairwise_deltas_use_candidate_minus_baseline() -> None:
    metrics = pd.DataFrame(
        [
            {"split_role": "validation", "fold_id": "fold_001", "horizon_id": "1d", "model_id": "baseline", "rmse": 0.20, "mae": 0.10},
            {"split_role": "validation", "fold_id": "fold_001", "horizon_id": "1d", "model_id": "candidate", "rmse": 0.15, "mae": 0.09},
        ]
    )

    deltas = compute_pairwise_deltas(metrics, "baseline", ["candidate"])

    assert float(deltas.loc[0, "rmse_delta_candidate_minus_baseline"]) < 0.0
    assert bool(deltas.loc[0, "both_metrics_improve"])


def test_stable_digest_is_order_independent() -> None:
    assert stable_digest({"a": 1, "b": 2}) == stable_digest({"b": 2, "a": 1})


def test_stage18_sequence_tensor_builder_left_pads_and_masks() -> None:
    base = pd.DataFrame(
        [
            {"canonical_ticker": "AAA", "as_of_date": "2024-01-01", "sequence_base_index": 0, "f1": 1.0, "f2": np.nan},
            {"canonical_ticker": "AAA", "as_of_date": "2024-01-02", "sequence_base_index": 1, "f1": 2.0, "f2": 3.0},
        ]
    )

    values, mask = _build_sequence_tensors(base, ["f1", "f2"], window_length=3)

    assert values.shape == (2, 3, 2)
    assert values[0, -1, 0] == 1.0
    assert values[0, -1, 1] == 0.0
    assert bool(mask[0, -1, 0])
    assert not bool(mask[0, -1, 1])
    assert values[1, -2:, 0].tolist() == [1.0, 2.0]


def test_stage31_compact_tsmixer_forward_shape() -> None:
    import torch

    model = _CompactTSMixer(window_length=4, feature_count=3, hidden_time=2, hidden_feature=5)
    output = model(torch.zeros((7, 4, 3), dtype=torch.float32))

    assert output.shape == (7, 1)
    assert model.architecture_version == TSMIXER_ARCHITECTURE_VERSION
    assert model.readout_policy == TSMIXER_READOUT_POLICY
    assert model.head[0].normalized_shape == (12,)
    assert model.head[1].in_features == 12


def test_stage32_search_contract_is_train_validation_only() -> None:
    contract = stage32_search_space_contract(trial_count=60, seeds=(1, 2), epochs=8)

    assert contract["search_policy"] == "user_override_heavy_optuna_after_negative_stage31_recommendation"
    assert contract["trial_count"] == 60
    assert contract["seed_count"] == 2
    assert contract["architecture"]["version"] == TSMIXER_ARCHITECTURE_VERSION
    assert contract["architecture"]["readout_policy"] == TSMIXER_READOUT_POLICY
    assert contract["split_roles_for_optimization"] == ["train", "validation"]
    assert contract["lockbox_rows_used_for_optimization"] == 0
    assert contract["freeze_gate"]["positive_claim_approved"] is False
    assert contract["search_space"]["hidden_time"]["choices"] == [16, 32, 48, 64]


def test_xgboost_only_branch_status_closes_tsmixer_and_fusion() -> None:
    records = {record["component_id"]: record for record in xgboost_only_branch_status_records()}

    assert records["market_xgboost_v2_frozen_final"]["active_xgboost_only_candidate"] is True
    assert records["market_tsmixer_v1_tuned_best_trial_41"]["classification"] == "tuned_candidate_rejected_from_development_only"
    assert records["market_xgb_tsmixer_horizon_meta_v1"]["current_branch_status"] == "cancelled_current_branch"
    assert records["event_market_horizon_fusion_v1"]["current_branch_status"] == "cancelled_current_branch_historical_exploratory"
    assert all(record["positive_claim_approved"] is False for record in records.values())


def test_xgboost_only_allowed_language_preserves_nonclaims() -> None:
    language = xgboost_only_allowed_language()

    assert "XGBoost-only" in language
    assert "positive benchmark-improvement language" in language
    assert "remain unapproved" in language
    assert "fusion diagnostics" not in language
