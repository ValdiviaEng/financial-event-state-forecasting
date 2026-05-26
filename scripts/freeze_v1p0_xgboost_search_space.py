from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402
from event_state_forecasting.v1p0.xgboost_search import validate_xgboost_search_config  # noqa: E402


CONFIG_PATH = PROJECT_ROOT / "configs/xgboost_search_v1p0.yaml"
STAGE20_MANIFEST_PATH = PROJECT_ROOT / "data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z/diagnostic_manifest.json"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_AT_UTC = "2026-05-24T07:15:00Z"
SOURCE_ID = "6dff1bd"


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze the v1p0 Stage 21 XGBoost search-space and objective contract.")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--stage20-manifest", type=Path, default=STAGE20_MANIFEST_PATH)
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()

    config = load_json_config(args.config)
    validated = validate_xgboost_search_config(config)
    stage20_manifest = json.loads(args.stage20_manifest.read_text(encoding="utf-8"))
    _validate_stage20_gate(stage20_manifest, validated)

    digest = validated["config_digest_sha256"]
    run_id = f"v1p0__phase1_top50_v1p0__stage21__xgboost_search_freeze__20260524T071500Z__src_{SOURCE_ID}__run_{digest[:8]}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    frozen_config_path = output_root / "frozen_search_space.json"
    stage21_manifest_path = output_root / "search_space_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage21_xgboost_search_space_freeze_report.md"

    frozen_payload = dict(validated)
    frozen_payload["artifact_type"] = "v1p0_stage21_frozen_xgboost_search_space"
    frozen_payload["artifact_id"] = f"xgboost_search_space_v1p0__stage21_20260524T071500Z__digest_{digest[:12]}"
    frozen_payload["search_started"] = False
    frozen_payload["model_fit_started"] = False
    frozen_payload["lockbox_tuning"] = False
    _write_json(frozen_config_path, frozen_payload)

    stage21_manifest = {
        "artifact_type": "v1p0_stage21_search_space_manifest",
        "artifact_id": frozen_payload["artifact_id"],
        "generated_at_utc": GENERATED_AT_UTC,
        "status": "frozen",
        "stage22_allowed": True,
        "config_digest_sha256": digest,
        "config_source_path": _rel(args.config),
        "source_diagnostic_artifact_id": stage20_manifest["artifact_id"],
        "source_metric_digest_sha256": stage20_manifest["metric_digest_sha256"],
        "candidate_model_id": validated["candidate_model_id"],
        "hurdle_model_id": validated["hurdle_model_id"],
        "trial_budget": validated["budgets"],
        "objective": {
            "objective_id": validated["objective"]["objective_id"],
            "direction": validated["objective"]["direction"],
            "horizon_weights": validated["objective"]["horizon_weights"],
            "metric_weights": validated["objective"]["metric_weights"],
            "penalties": validated["objective"]["penalties"],
        },
        "outputs": {
            "frozen_search_space": _rel(frozen_config_path),
            "search_space_manifest": _rel(stage21_manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "lockbox_policy": {
            "lockbox_available_in_source_artifacts": True,
            "lockbox_used_for_search_space_freeze": False,
            "lockbox_allowed_in_stage22_search": False,
            "lockbox_allowed_after_frozen_final_selection": True,
        },
        "non_claims": validated["non_claims"],
    }
    _write_json(stage21_manifest_path, stage21_manifest)

    run_manifest = {
        "run_id": run_id,
        "stage": 21,
        "stage_name": "xgboost_search_space_and_objective_freeze",
        "generated_at_utc": GENERATED_AT_UTC,
        "status": "completed",
        "source_ids": {
            "source_code_id": SOURCE_ID,
            "stage20_diagnostic_artifact_id": stage20_manifest["artifact_id"],
            "stage20_metric_digest_sha256": stage20_manifest["metric_digest_sha256"],
        },
        "command": "source ~/venvs/ai/bin/activate && python scripts/freeze_v1p0_xgboost_search_space.py",
        "outputs": stage21_manifest["outputs"],
        "benchmark_claim": False,
        "search_started": False,
        "model_fit_started": False,
        "lockbox_tuning": False,
    }
    _write_json(run_manifest_path, run_manifest)
    report_path.write_text(_render_report(run_id, stage21_manifest), encoding="utf-8")

    print(json.dumps({"status": "passed", "run_id": run_id, "config_digest_sha256": digest, "output_root": _rel(output_root), "stage22_allowed": True}, sort_keys=True))


def _validate_stage20_gate(stage20_manifest: dict[str, Any], config: dict[str, Any]) -> None:
    if stage20_manifest.get("artifact_id") != config["source_diagnostic_artifact_id"]:
        raise RuntimeError("Stage 20 diagnostic artifact ID does not match search config source")
    gate = stage20_manifest.get("diagnostic_gate", {})
    if not gate.get("proceed_to_stage21_from_development_evidence"):
        raise RuntimeError("Stage 20 gate does not allow Stage 21")
    if gate.get("lockbox_tuning"):
        raise RuntimeError("Stage 20 gate indicates lockbox tuning")


def _render_report(run_id: str, manifest: dict[str, Any]) -> str:
    objective = manifest["objective"]
    budget = manifest["trial_budget"]
    return f"""# Stage 21 XGBoost Search-Space Freeze Report

Status: completed; search space and objective frozen before any Stage 22 search

Updated: 2026-05-24

Run ID: `{run_id}`

## Frozen Contract

| Field | Value |
| --- | --- |
| Candidate model | `{manifest['candidate_model_id']}` |
| Hurdle model | `{manifest['hurdle_model_id']}` |
| Objective | `{objective['objective_id']}` |
| Direction | `{objective['direction']}` |
| Config digest | `{manifest['config_digest_sha256']}` |
| Stage 22 allowed | `{str(manifest['stage22_allowed']).lower()}` |

## Trial Budget

| Phase | Trials |
| --- | ---: |
| Random | {budget['random_trials']} |
| Optuna TPE | {budget['optuna_tpe_trials']} |
| Local refinement | {budget['local_refinement_trials']} |
| Total maximum | {budget['max_total_trials']} |

## Objective Weights

| Horizon | Weight |
| --- | ---: |
| `1d` | {objective['horizon_weights']['1d']} |
| `5d` | {objective['horizon_weights']['5d']} |
| `10d` | {objective['horizon_weights']['10d']} |
| `20d` | {objective['horizon_weights']['20d']} |
| `60d` | {objective['horizon_weights']['60d']} |

RMSE and MAE are each weighted at 0.5. Penalties are frozen for one-sided improvement, train-validation gaps, horizon instability, fold instability, and complexity.

## Lockbox Policy

Stage 22 search must use development train and validation evidence only. Lockbox metrics may not guide search, search-space changes, trial pruning, candidate selection, or local refinement.

## Artifacts

| Artifact | Path |
| --- | --- |
| Frozen search space | `{manifest['outputs']['frozen_search_space']}` |
| Search-space manifest | `{manifest['outputs']['search_space_manifest']}` |
| Run manifest | `{manifest['outputs']['run_manifest']}` |

## Non-Claims

This freeze is not hyperparameter search, not a model fit, not benchmark evidence, not a promotion claim, not Stage 6 reinterpretation, and not lockbox tuning.
"""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    main()
