from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    TSMIXER_ARCHITECTURE_VERSION,
    TSMIXER_INVALIDATED_READOUT_POLICY,
    TSMIXER_READOUT_POLICY,
    stable_digest,
)


RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
SOURCE_ID = "6dff1bd"
UPDATED_XGBOOST_ROOT = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__20260528T100000Z__src_6dff1bd__run_40f1c9a0"
UPDATED_TSMIXER_ROOT = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage44__tsmixer_training__20260528T120000Z__src_6dff1bd__run_6817ae4c"
UPDATED_META_ROOT = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage45__market_xgb_tsmixer_meta__20260528T150000Z__src_6dff1bd__run_5a3a14f8"
ENHANCED_TSMIXER_ROOT = RESULT_ROOT / "v1p0__phase1_top50_v1p0__stage42__tsmixer_enhanced_optuna__20260528T040000Z__src_6dff1bd__run_05ccd906"


def updated_tsmixer_algorithm_correction_audit_contract() -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_tsmixer_algorithm_correction_audit_contract",
        "branch_scope": "updated_alpha_vantage_stage43_45",
        "corrected_architecture_version": TSMIXER_ARCHITECTURE_VERSION,
        "corrected_readout_policy": TSMIXER_READOUT_POLICY,
        "invalidated_prior_readout_policy": TSMIXER_INVALIDATED_READOUT_POLICY,
        "no_training_executed": True,
        "tsmixer_retraining_required_before_tsmixer_or_meta_evidence": True,
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": [
            "algorithm_correction_audit_only",
            "no_tsmixer_training_executed",
            "stale_mean_pooling_tsmixer_artifacts_invalidated",
            "stage45_meta_uses_stale_tsmixer_inputs_and_is_not_active_evidence",
            "not_positive_benchmark_claim",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }


def main() -> None:
    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    generated_token = generated_at.strftime("%Y%m%dT%H%M%SZ")
    contract = updated_tsmixer_algorithm_correction_audit_contract()
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_updated_av__stage46__tsmixer_algorithm_correction_audit__{generated_token}__src_{SOURCE_ID}__run_{digest}"
    output_root = RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    manifest_path = output_root / "tsmixer_algorithm_correction_audit_manifest.json"
    report_path = output_root / "stage46_tsmixer_algorithm_correction_audit.md"
    run_manifest_path = output_root / "run_manifest.json"

    affected_artifacts = {
        "updated_xgboost_stage43_unaffected": _artifact_record(UPDATED_XGBOOST_ROOT, invalidated=False),
        "updated_tsmixer_stage44_invalidated_until_rerun": _artifact_record(UPDATED_TSMIXER_ROOT, invalidated=True),
        "updated_meta_stage45_invalidated_until_tsmixer_rerun": _artifact_record(UPDATED_META_ROOT, invalidated=True),
        "historical_enhanced_tsmixer_stage42_invalidated_until_rerun": _artifact_record(ENHANCED_TSMIXER_ROOT, invalidated=True),
    }
    manifest = {
        **contract,
        "artifact_type": "updated_dataset_tsmixer_algorithm_correction_audit_manifest",
        "artifact_id": f"updated_dataset_tsmixer_algorithm_correction_audit__{digest}__{generated_token}",
        "generated_at_utc": generated_at.isoformat().replace("+00:00", "Z"),
        "run_id": run_id,
        "status": "completed_no_training",
        "current_active_model_candidate": "updated_av_xgboost_event_market_optuna_v1",
        "algorithm_correction": {
            "problem": "prior TSMixer implementations mixed over time/features and then used mean pooling over the time axis",
            "correction": "TSMixer now reads out from the flattened ordered time-feature state after mixer blocks",
            "code_paths": [
                "src/event_state_forecasting/v1p0/final_sprint.py",
                "scripts/run_updated_dataset_tsmixer_training.py",
                "scripts/run_v1p0_tsmixer_enhanced_optuna.py",
            ],
        },
        "affected_artifacts": affected_artifacts,
        "required_next_evidence_before_tsmixer_or_meta_use": [
            "rerun Stage 31/44-style fixed multiseed TSMixer with corrected architecture",
            "rerun any TSMixer optimization only after standalone evidence and approval",
            "rerun XGBoost+TSMixer meta only after corrected standalone TSMixer predictions exist",
            "refresh Stage 35-40 diagnostics/claim review after corrected candidate evidence exists",
        ],
        "outputs": {
            "manifest": _rel(manifest_path),
            "report": _rel(report_path),
            "run_manifest": _rel(run_manifest_path),
        },
    }
    _write_json(manifest_path, manifest)
    _write_json(run_manifest_path, {"stage": 46, "stage_name": "tsmixer_algorithm_correction_audit", "status": "completed_no_training", "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_render_report(manifest), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "manifest": manifest["outputs"]["manifest"], "current_active_model_candidate": manifest["current_active_model_candidate"]}, sort_keys=True))


def _artifact_record(path: Path, *, invalidated: bool) -> dict[str, Any]:
    return {
        "path": _rel(path),
        "exists": path.exists(),
        "invalidated_by_algorithm_correction": invalidated,
        "reason": "depends on stale mean-pooled TSMixer architecture" if invalidated else "does not depend on TSMixer architecture",
    }


def _render_report(manifest: dict[str, Any]) -> str:
    lines = [
        "# Stage 46 TSMixer Algorithm Correction Audit",
        "",
        "Status: completed with no TSMixer training executed.",
        "",
        "## Correction",
        "",
        f"Previous readout policy invalidated: `{manifest['invalidated_prior_readout_policy']}`.",
        f"Corrected architecture: `{manifest['corrected_architecture_version']}` with `{manifest['corrected_readout_policy']}` readout.",
        "",
        "## Evidence Boundary",
        "",
        "Stage 44 TSMixer and Stage 45 XGBoost+TSMixer meta evidence are stale until rerun with the corrected TSMixer architecture.",
        "Updated Stage 43 XGBoost evidence is unaffected and remains the active candidate evidence.",
        "",
        "## Required Next Evidence",
        "",
    ]
    lines.extend(f"- {item}" for item in manifest["required_next_evidence_before_tsmixer_or_meta_use"])
    lines.extend([
        "",
        "## Non-Claims",
        "",
        "This audit does not approve a positive benchmark claim, Stage 6 reinterpretation, benchmark-comparability promotion, live forecast, or trading output.",
        "",
    ])
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    main()
