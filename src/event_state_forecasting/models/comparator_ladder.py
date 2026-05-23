"""Stage 5 comparator-ladder roster validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Mapping


STAGE5_MODEL_SCHEMA_VERSION = "stage5_models_v1"
MARKET_ONLY_FAMILIES = {
    "constant_zero",
    "constant_train_mean",
    "ridge",
    "elastic_net",
    "random_forest",
    "hist_gradient_boosting",
    "mlp",
}
EVENT_STATE_FAMILIES = {"simple_gated_fusion"}
APPROVED_MODEL_FAMILIES = MARKET_ONLY_FAMILIES | EVENT_STATE_FAMILIES


class ComparatorLadderError(ValueError):
    """Raised when the Stage 5 comparator roster is invalid."""


@dataclass(frozen=True, slots=True)
class ModelSpec:
    model_id: str
    family: str
    branch: str
    allowed_inputs: tuple[str, ...]
    preprocessing: str
    params: Mapping[str, Any]


def validate_model_config(config: Mapping[str, Any]) -> list[ModelSpec]:
    if config.get("artifact_schema_version") != STAGE5_MODEL_SCHEMA_VERSION:
        raise ComparatorLadderError("model config schema version mismatch")

    ladder = config.get("comparator_ladder")
    if not isinstance(ladder, Mapping):
        raise ComparatorLadderError("model config missing comparator_ladder")
    if not ladder.get("roster_id"):
        raise ComparatorLadderError("comparator roster_id is required")
    if ladder.get("search_policy") != "tiny_fixed_no_hyperparameter_search":
        raise ComparatorLadderError("Stage 5 currently requires the approved tiny fixed search policy")
    if not isinstance(ladder.get("seed"), int):
        raise ComparatorLadderError("integer seed is required")

    models = ladder.get("models")
    if not isinstance(models, list) or not models:
        raise ComparatorLadderError("comparator_ladder.models must be a non-empty list")

    seen: set[str] = set()
    specs: list[ModelSpec] = []
    for raw in models:
        if not isinstance(raw, Mapping):
            raise ComparatorLadderError("each model spec must be a mapping")
        model_id = str(raw.get("model_id", ""))
        family = str(raw.get("family", ""))
        branch = str(raw.get("branch", ""))
        allowed_inputs = tuple(str(value) for value in raw.get("allowed_inputs", []))
        preprocessing = str(raw.get("preprocessing", ""))
        params = raw.get("params", {})

        if not model_id:
            raise ComparatorLadderError("model_id is required")
        if model_id in seen:
            raise ComparatorLadderError(f"duplicate model_id: {model_id}")
        seen.add(model_id)
        if family not in APPROVED_MODEL_FAMILIES:
            raise ComparatorLadderError(f"unapproved model family: {family}")
        if not isinstance(params, Mapping):
            raise ComparatorLadderError(f"params must be a mapping for {model_id}")
        if preprocessing not in {"none", "median_impute", "median_impute_scale"}:
            raise ComparatorLadderError(f"unsupported preprocessing policy for {model_id}: {preprocessing}")

        if family in MARKET_ONLY_FAMILIES:
            if branch != "market_only" or allowed_inputs != ("market_features",):
                raise ComparatorLadderError(f"market-only model has invalid inputs: {model_id}")
        if family in EVENT_STATE_FAMILIES:
            if branch != "event_state" or allowed_inputs != ("market_features", "event_state_features"):
                raise ComparatorLadderError(f"event-state model has invalid inputs: {model_id}")

        specs.append(
            ModelSpec(
                model_id=model_id,
                family=family,
                branch=branch,
                allowed_inputs=allowed_inputs,
                preprocessing=preprocessing,
                params=params,
            )
        )

    if not any(spec.family == "simple_gated_fusion" for spec in specs):
        raise ComparatorLadderError("approved Stage 5 roster must include simple gated fusion")
    return specs


def freeze_comparator_ladder(config: Mapping[str, Any]) -> dict[str, Any]:
    specs = validate_model_config(config)
    ladder = config["comparator_ladder"]
    return {
        "artifact_type": "stage5_comparator_roster_record",
        "artifact_schema_version": STAGE5_MODEL_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "roster_id": ladder["roster_id"],
        "approval_basis": ladder.get("approval_basis"),
        "seed": ladder["seed"],
        "search_policy": ladder["search_policy"],
        "prediction_scope": ladder.get("prediction_scope"),
        "model_count": len(specs),
        "model_ids": [spec.model_id for spec in specs],
        "model_families": {spec.model_id: spec.family for spec in specs},
        "allowed_inputs": {spec.model_id: list(spec.allowed_inputs) for spec in specs},
        "benchmark_claim": False,
    }
