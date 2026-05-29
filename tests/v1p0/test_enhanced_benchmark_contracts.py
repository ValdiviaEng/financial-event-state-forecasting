from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = PROJECT_ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_enhanced_xgboost_contract_requires_800_and_bigger_models() -> None:
    module = _load_script("run_v1p0_xgboost_enhanced_optuna.py")
    contract = module.enhanced_xgboost_search_contract()

    assert contract["trial_count"] >= 800
    assert contract["minimum_required_trials"] == 800
    assert contract["baseline_model_id"] == "market_xgboost_v2_frozen_final"
    assert contract["search_space"]["n_estimators"]["high"] >= 2400
    assert contract["search_space"]["max_depth"]["high"] >= 10
    assert "grow_policy" in contract["search_space"]
    assert contract["objective"]["lockbox_rows_used_for_optimization"] == 0


def test_enhanced_tsmixer_contract_requires_800_and_bigger_models() -> None:
    module = _load_script("run_v1p0_tsmixer_enhanced_optuna.py")
    contract = module.enhanced_tsmixer_search_contract()

    assert contract["architecture"]["version"] == "tsmixer_pure_pytorch_flatten_readout_v2"
    assert contract["architecture"]["readout_policy"] == "flatten_time_feature_state"
    assert contract["trial_count"] >= 800
    assert contract["minimum_required_trials"] == 800
    assert contract["baseline_model_id"] == "market_xgboost_v2_frozen_final"
    assert max(contract["search_space"]["hidden_feature"]["choices"]) >= 384
    assert max(contract["search_space"]["mixer_blocks"]["choices"]) >= 4
    assert set(contract["search_space"]["window_length"]["choices"]) == {20, 60}
    assert contract["lockbox_rows_used_for_optimization"] == 0


def test_updated_dataset_tsmixer_contract_is_complete_and_nonselective_lockbox() -> None:
    module = _load_script("run_updated_dataset_tsmixer_training.py")
    contract = module.updated_tsmixer_training_contract()

    assert contract["architecture"]["version"] == "tsmixer_pure_pytorch_flatten_readout_v2"
    assert contract["architecture"]["readout_policy"] == "flatten_time_feature_state"
    assert contract["trial_count"] >= 800
    assert contract["minimum_required_trials"] == 800
    assert contract["feature_scope"] == "updated_alpha_vantage_market_plus_event_state_sequences"
    assert contract["fixed_multiseed_benchmark"]["seed_count"] >= 5
    assert contract["tuning"]["seed_count"] >= 2
    assert set(contract["search_space"]["window_length"]["choices"]) == {20, 60}
    assert max(contract["search_space"]["hidden_feature"]["choices"]) >= 384
    assert max(contract["search_space"]["mixer_blocks"]["choices"]) >= 4
    assert contract["lockbox_rows_used_for_tuning"] == 0
    assert contract["selection_objective"]["lockbox_policy"] == "no_lockbox_rows_or_metrics_used_for_trial_selection"
    assert "lockbox_not_used_for_tuning_or_selection" in contract["non_claims"]


def test_updated_market_meta_ensemble_contract_freezes_partial_tsmixer() -> None:
    module = _load_script("run_updated_dataset_market_meta_ensemble.py")
    contract = module.updated_market_meta_ensemble_contract()

    assert contract["trial_count"] >= 800
    assert contract["minimum_required_trials"] == 800
    assert contract["model_id"] == "updated_av_market_xgb_tsmixer_horizon_meta_v1"
    assert contract["model_family"] == "horizon_specific_regularized_meta_combiner"
    assert contract["base_features"] == ["xgboost_prediction", "tsmixer_prediction"]
    assert contract["base_model_policy"]["tsmixer_previous_stale_partial_tuning_trial_count"] == 401
    assert contract["base_model_policy"]["tsmixer_current_corrected_artifacts_required"] is True
    assert contract["base_model_policy"]["tsmixer_required_architecture_version"] == "tsmixer_pure_pytorch_flatten_readout_v2"
    assert contract["meta_training_policy"]["training_split"] == "train_only"
    assert contract["meta_training_policy"]["selection_split"] == "validation"
    assert contract["meta_training_policy"]["lockbox_rows_used_for_tuning"] == 0
    assert "stale_tsmixer_mean_pooling_artifacts_not_reused" in contract["non_claims"]


def test_updated_dataset_tsmixer_readout_uses_full_mixed_state() -> None:
    import torch

    module = _load_script("run_updated_dataset_tsmixer_training.py")
    model = module._UpdatedTSMixer(
        window_length=4,
        feature_count=3,
        config={
            "mixer_blocks": 1,
            "hidden_time": 2,
            "hidden_feature": 5,
            "head_hidden": 0,
            "dropout": 0.0,
        },
    )

    output = model(torch.zeros((7, 4, 3), dtype=torch.float32))

    assert output.shape == (7, 1)
    assert model.readout_policy == "flatten_time_feature_state"
    assert model.head[0].normalized_shape == (12,)
    assert model.head[1].in_features == 12


def test_tsmixer_algorithm_correction_audit_invalidates_stale_meta() -> None:
    module = _load_script("write_updated_dataset_tsmixer_algorithm_correction_audit.py")
    contract = module.updated_tsmixer_algorithm_correction_audit_contract()

    assert contract["corrected_architecture_version"] == "tsmixer_pure_pytorch_flatten_readout_v2"
    assert contract["invalidated_prior_readout_policy"] == "mean_time_pooling_readout_v1"
    assert contract["no_training_executed"] is True
    assert contract["tsmixer_retraining_required_before_tsmixer_or_meta_evidence"] is True
    assert "stage45_meta_uses_stale_tsmixer_inputs_and_is_not_active_evidence" in contract["non_claims"]
