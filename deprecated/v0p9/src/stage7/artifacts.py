"""Stage 7 artifact writing helpers."""

from __future__ import annotations

import json
import math
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


class Stage7ArtifactError(ValueError):
    """Raised when Stage 7 artifact writing is unsafe."""


def write_stage7_artifacts(
    *,
    output_root: Path,
    config: Mapping[str, Any],
    context: pd.DataFrame,
    selections: pd.DataFrame,
    metrics: pd.DataFrame,
    policy_manifest: pd.DataFrame,
    replay_validation: Mapping[str, Any],
    data_update_plan: Mapping[str, Any],
    deprecated_archive_manifest: Mapping[str, Any] | None,
    final_execution_stub: Mapping[str, Any] | None,
    inputs: Mapping[str, str],
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    if output_root.exists():
        if not allow_overwrite:
            raise Stage7ArtifactError(f"Stage 7 output root already exists: {output_root}")
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=False)

    paths = {
        "resolved_stage7_config": output_root / "resolved_stage7_config.json",
        "context_schema": output_root / "context_schema.json",
        "policy_manifest": output_root / "policy_manifest.parquet",
        "policy_selections": output_root / "policy_selections.parquet",
        "policy_metrics": output_root / "policy_metrics.parquet",
        "replay_validation": output_root / "replay_validation.json",
        "data_update_plan": output_root / "data_update_plan.json",
        "stage7_manifest": output_root / "stage7_manifest.json",
    }
    write_json(paths["resolved_stage7_config"], config)
    write_json(paths["context_schema"], build_context_schema(context))
    policy_manifest.to_parquet(paths["policy_manifest"], index=False)
    selections.to_parquet(paths["policy_selections"], index=False)
    metrics.to_parquet(paths["policy_metrics"], index=False)
    write_json(paths["replay_validation"], replay_validation)
    write_json(paths["data_update_plan"], data_update_plan)
    if final_execution_stub is not None:
        paths["final_execution_stub"] = output_root / "final_execution_stub.json"
        write_json(paths["final_execution_stub"], final_execution_stub)

    manifest = build_stage7_manifest(
        output_root=output_root,
        config=config,
        context=context,
        selections=selections,
        metrics=metrics,
        replay_validation=replay_validation,
        data_update_plan=data_update_plan,
        deprecated_archive_manifest=deprecated_archive_manifest,
        final_execution_stub=final_execution_stub,
        inputs=inputs,
        paths=paths,
    )
    write_json(paths["stage7_manifest"], manifest)
    return manifest


def build_context_schema(context: pd.DataFrame) -> dict[str, Any]:
    return {
        "artifact_type": "stage7_context_schema",
        "artifact_schema_version": "stage7_contextual_bandit_v1",
        "generated_at_utc": now_utc(),
        "row_count": int(len(context)),
        "column_count": int(len(context.columns)),
        "columns": list(context.columns),
        "split_roles": sorted(str(value) for value in context["split_role"].drop_duplicates().tolist()) if "split_role" in context else [],
        "benchmark_claim": False,
    }


def build_stage7_manifest(
    *,
    output_root: Path,
    config: Mapping[str, Any],
    context: pd.DataFrame,
    selections: pd.DataFrame,
    metrics: pd.DataFrame,
    replay_validation: Mapping[str, Any],
    data_update_plan: Mapping[str, Any],
    deprecated_archive_manifest: Mapping[str, Any] | None,
    final_execution_stub: Mapping[str, Any] | None,
    inputs: Mapping[str, str],
    paths: Mapping[str, Path],
) -> dict[str, Any]:
    new_holdout_mode = bool(replay_validation.get("new_post_lockbox_holdout_mode"))
    return {
        "artifact_type": "stage7_contextual_bandit_manifest",
        "artifact_schema_version": "stage7_contextual_bandit_v1",
        "generated_at_utc": now_utc(),
        "stage7_status": "stage7_new_post_lockbox_holdout_diagnostics_created" if new_holdout_mode else "stage7_development_replay_diagnostics_created",
        "benchmark_claim": False,
        "bandit_value_claim_allowed": False,
        "identity": {
            "artifact_root": str(output_root),
            "protocol_id": config["protocol"]["protocol_id"],
            "benchmark_family_id": config["protocol"]["benchmark_family_id"],
        },
        "inputs": dict(inputs),
        "outputs": {name: str(path) for name, path in paths.items()},
        "counts": {
            "context_rows": int(len(context)),
            "selection_rows": int(len(selections)),
            "metric_rows": int(len(metrics)),
            "policy_count": int(selections["policy_id"].nunique()) if not selections.empty else 0,
            "horizon_count": int(selections["horizon_id"].nunique()) if not selections.empty else 0,
            "fold_count": int(selections["fold_id"].nunique()) if not selections.empty else 0,
        },
        "protocol_choices": {
            "primary_k": config["basket_policy"]["primary_k"],
            "diagnostic_k": config["basket_policy"]["diagnostic_k"],
            "primary_epsilon": config["epsilon_policy"]["primary_epsilon"],
            "diagnostic_epsilon": config["epsilon_policy"]["diagnostic_epsilon"],
            "row_filter_primary": config["row_filters"]["primary"],
            "row_filter_secondary": config["row_filters"]["secondary"],
        },
        "replay_validation_status": replay_validation.get("status"),
        "data_update_status": data_update_plan.get("status"),
        "deprecated_settings_archive_status": None if deprecated_archive_manifest is None else deprecated_archive_manifest.get("status"),
        "final_execution_status": None if final_execution_stub is None else final_execution_stub.get("status"),
        "non_claims": config.get("non_claims", []),
        "limitations": [
            "new post-lockbox holdout diagnostics use explicit lockbox rows only" if new_holdout_mode else "development replay uses validation artifacts only and excludes the current Stage 6 lockbox",
            "benchmark_claim remains false until final documentation/governance promotion records this artifact as claim-bearing",
            "epsilon-greedy diagnostics are simulated full-information replay diagnostics, not real logged-policy OPE",
            "bottom-k outputs are downside/avoid diagnostics, not live sell recommendations",
        ],
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    return value


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
