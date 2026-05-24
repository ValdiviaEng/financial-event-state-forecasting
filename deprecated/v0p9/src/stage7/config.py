"""Stage 7 contextual-bandit config validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml


STAGE7_CONFIG_SCHEMA_VERSION = "stage7_contextual_bandit_config_v1"


class Stage7ConfigError(ValueError):
    """Raised when the Stage 7 config violates approved decisions."""


def load_stage7_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise Stage7ConfigError(f"expected mapping in {path}")
    validate_stage7_config(config)
    return config


def validate_stage7_config(config: Mapping[str, Any]) -> None:
    if config.get("artifact_schema_version") != STAGE7_CONFIG_SCHEMA_VERSION:
        raise Stage7ConfigError("Stage 7 config schema version mismatch")
    protocol = _mapping(config, "protocol")
    if protocol.get("development_replay_uses_current_lockbox") is not False:
        raise Stage7ConfigError("Stage 7 development replay must not use the current Stage 6 lockbox")
    if protocol.get("final_execution_training_enabled_by_default") is not False:
        raise Stage7ConfigError("final-execution all-data training must be disabled by default")
    if not isinstance(protocol.get("seed"), int):
        raise Stage7ConfigError("Stage 7 seed must be an integer")

    basket = _mapping(config, "basket_policy")
    if int(basket.get("primary_k", -1)) != 5:
        raise Stage7ConfigError("approved primary basket size is k=5")
    if sorted(int(value) for value in basket.get("diagnostic_k", [])) != [3, 10]:
        raise Stage7ConfigError("approved diagnostic basket sizes are k=3 and k=10")

    epsilon = _mapping(config, "epsilon_policy")
    if abs(float(epsilon.get("primary_epsilon", -1.0)) - 0.05) > 1e-12:
        raise Stage7ConfigError("approved primary epsilon is 0.05")
    diagnostics = sorted(float(value) for value in epsilon.get("diagnostic_epsilon", []))
    if diagnostics != [0.01, 0.1]:
        raise Stage7ConfigError("approved diagnostic epsilons are 0.01 and 0.10")
    if epsilon.get("selection_from_holdout_allowed") is not False:
        raise Stage7ConfigError("epsilon selection from holdout results is forbidden")

    output = _mapping(config, "output_policy")
    if output.get("live_buy_sell_signal_approved") is not False:
        raise Stage7ConfigError("live buy/sell signal output is not approved")

    policies = _mapping(config, "policies")
    if policies.get("abstain_cash_in_scope") is not False:
        raise Stage7ConfigError("abstain/cash is not approved for first Stage 7 bundle")
    if policies.get("cost_adjusted_trading_in_scope") is not False:
        raise Stage7ConfigError("cost-adjusted trading reward is not approved")


def all_k_values(config: Mapping[str, Any]) -> list[int]:
    basket = _mapping(config, "basket_policy")
    values = [int(basket["primary_k"]), *(int(value) for value in basket.get("diagnostic_k", []))]
    return sorted(set(values))


def all_epsilon_values(config: Mapping[str, Any]) -> list[float]:
    epsilon = _mapping(config, "epsilon_policy")
    values = [float(epsilon["primary_epsilon"]), *(float(value) for value in epsilon.get("diagnostic_epsilon", []))]
    return sorted(set(values))


def _mapping(config: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = config.get(key)
    if not isinstance(value, Mapping):
        raise Stage7ConfigError(f"Stage 7 config missing mapping: {key}")
    return value
