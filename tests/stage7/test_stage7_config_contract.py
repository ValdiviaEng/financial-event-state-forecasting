from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.stage7.config import Stage7ConfigError, all_epsilon_values, all_k_values, validate_stage7_config  # noqa: E402


def test_stage7_config_enforces_approved_k_and_epsilon() -> None:
    config = _config()

    validate_stage7_config(config)

    assert all_k_values(config) == [3, 5, 10]
    assert all_epsilon_values(config) == [0.01, 0.05, 0.1]


def test_stage7_config_rejects_current_lockbox_design_replay() -> None:
    config = _config()
    config["protocol"]["development_replay_uses_current_lockbox"] = True

    with pytest.raises(Stage7ConfigError, match="current Stage 6 lockbox"):
        validate_stage7_config(config)


def _config() -> dict:
    return {
        "artifact_schema_version": "stage7_contextual_bandit_config_v1",
        "protocol": {"seed": 1729, "development_replay_uses_current_lockbox": False, "final_execution_training_enabled_by_default": False},
        "basket_policy": {"primary_k": 5, "diagnostic_k": [3, 10]},
        "epsilon_policy": {"primary_epsilon": 0.05, "diagnostic_epsilon": [0.01, 0.1], "selection_from_holdout_allowed": False},
        "output_policy": {"live_buy_sell_signal_approved": False},
        "policies": {"abstain_cash_in_scope": False, "cost_adjusted_trading_in_scope": False},
    }
