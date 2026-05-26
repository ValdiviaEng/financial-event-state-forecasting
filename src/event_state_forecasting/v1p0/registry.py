from __future__ import annotations

from typing import Any

from event_state_forecasting.v1p0.versioning import V1P0ContractError, stable_digest


def validate_feature_registry(registry: dict[str, Any]) -> dict[str, Any]:
    if registry.get("implementation_version") != "v1p0":
        raise V1P0ContractError("feature registry must be v1p0")
    features = registry.get("features")
    dependencies = registry.get("model_feature_dependencies")
    if not isinstance(features, list) or not features:
        raise V1P0ContractError("feature registry must contain features")
    if not isinstance(dependencies, list) or not dependencies:
        raise V1P0ContractError("feature registry must contain model dependencies")
    feature_ids = [str(feature.get("feature_family_id", "")) for feature in features]
    if len(feature_ids) != len(set(feature_ids)):
        raise V1P0ContractError("feature_family_id values must be unique")
    feature_id_set = set(feature_ids)
    model_ids = [str(item.get("model_id", "")) for item in dependencies]
    if len(model_ids) != len(set(model_ids)):
        raise V1P0ContractError("model_id dependencies must be unique")
    for dependency in dependencies:
        if str(dependency.get("feature_family_id", "")) not in feature_id_set:
            raise V1P0ContractError("model dependency references unknown feature family")
    result = dict(registry)
    result["registry_digest"] = stable_digest(registry)
    return result
