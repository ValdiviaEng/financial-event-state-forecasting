#!/usr/bin/env python3
"""Validate Stage 5 model and saved-prediction artifact completion."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGE5_ARTIFACT_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1"
DEFAULT_MODEL_ROOT = PROJECT_ROOT / "data" / "models" / "phase1_top50" / STAGE5_ARTIFACT_VERSION
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage5_completion_validation_2026-05-21.json"
REQUIRED_PREDICTION_COLUMNS = {
    "row_key",
    "benchmark_family_id",
    "canonical_ticker",
    "as_of_date",
    "horizon_id",
    "fold_id",
    "split_role",
    "model_id",
    "model_family",
    "branch",
    "dataset_version",
    "feature_artifact_version",
    "split_artifact_version",
    "stage5_artifact_version",
    "prediction",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 5 completion artifacts.")
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--model-config", type=Path, default=PROJECT_ROOT / "configs" / "models.yaml")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_stage5(args.model_root, args.model_config)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "passed":
        print("STAGE5_COMPLETION_VALIDATION FAILED")
        for blocker in result["blockers"]:
            print(f"- {blocker}")
        return 1
    print("STAGE5_COMPLETION_VALIDATION PASSED")
    return 0


def validate_stage5(model_root: Path, model_config: Path) -> dict[str, Any]:
    blockers: list[str] = []
    config = load_yaml_or_json(model_config)
    model_ids = [item["model_id"] for item in config["comparator_ladder"]["models"]]
    expected_fit_count = len(model_ids) * 9 * 5
    expected_prediction_rows = len(model_ids) * (47250 + 213750)
    required_files = {
        "model_manifest": model_root / "model_manifest.json",
        "resolved_model_config": model_root / "resolved_model_config.json",
        "comparator_roster_record": model_root / "comparator_roster_record.json",
        "saved_predictions": model_root / "saved_predictions.parquet",
        "preprocessing_fit_manifest": model_root / "preprocessing_fit_manifest.parquet",
        "model_fit_manifest": model_root / "model_fit_manifest.parquet",
        "training_diagnostics": model_root / "training_diagnostics.parquet",
        "search_space_summary": model_root / "search_space_summary.json",
        "serious_packet_validation": model_root / "serious_packet_validation.json",
    }
    for name, path in required_files.items():
        if not path.exists():
            blockers.append(f"missing_{name}")

    manifest: dict[str, Any] = {}
    serious_packet: dict[str, Any] = {}
    if not blockers:
        manifest = load_json(required_files["model_manifest"])
        serious_packet = load_json(required_files["serious_packet_validation"])
        if manifest.get("artifact_schema_version") != "stage5_models_v1":
            blockers.append("manifest_schema_mismatch")
        if manifest.get("benchmark_claim") is not False:
            blockers.append("stage5_manifest_must_not_claim_benchmark")
        if manifest.get("stage5_status") != "stage5_model_prediction_artifacts_created":
            blockers.append("stage5_status_not_created")
        if serious_packet.get("status") != "blocked_missing_required_members":
            blockers.append("serious_packet_should_remain_blocked_without_metrics")
        missing_serious = set(serious_packet.get("missing_members", []))
        if not {"metrics", "overfitting_diagnostic_report", "comparison_summary"}.issubset(missing_serious):
            blockers.append("serious_packet_missing_expected_stage6_blockers")

        predictions = pd.read_parquet(required_files["saved_predictions"])
        preprocessing = pd.read_parquet(required_files["preprocessing_fit_manifest"])
        model_fits = pd.read_parquet(required_files["model_fit_manifest"])
        diagnostics = pd.read_parquet(required_files["training_diagnostics"])
        missing_columns = REQUIRED_PREDICTION_COLUMNS - set(predictions.columns)
        if missing_columns:
            blockers.append(f"saved_predictions_missing_columns:{sorted(missing_columns)}")
        if len(predictions) != expected_prediction_rows:
            blockers.append(f"saved_prediction_row_count_mismatch:{len(predictions)}")
        if set(predictions["split_role"].unique()) != {"validation", "lockbox"}:
            blockers.append("saved_predictions_role_mismatch")
        if predictions["prediction"].isna().any():
            blockers.append("saved_predictions_have_nulls")
        if predictions.duplicated(["row_key", "fold_id", "model_id", "split_role"]).any():
            blockers.append("saved_predictions_have_duplicates")
        if set(predictions["model_id"].unique()) != set(model_ids):
            blockers.append("saved_predictions_model_ids_mismatch")
        if len(preprocessing) != expected_fit_count:
            blockers.append(f"preprocessing_fit_count_mismatch:{len(preprocessing)}")
        if not bool(preprocessing["preprocessing_fit_allowed_only"].all()):
            blockers.append("preprocessing_fit_not_train_only")
        if len(model_fits) != expected_fit_count:
            blockers.append(f"model_fit_count_mismatch:{len(model_fits)}")
        if len(diagnostics) != expected_fit_count:
            blockers.append(f"training_diagnostic_count_mismatch:{len(diagnostics)}")
        if bool(diagnostics["metrics_computed"].any()):
            blockers.append("training_diagnostics_should_not_compute_metrics")

    status = "passed" if not blockers else "failed"
    return {
        "artifact_type": "stage5_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": status,
        "model_root": str(model_root),
        "model_count": len(model_ids),
        "expected_fit_count": expected_fit_count,
        "expected_prediction_rows": expected_prediction_rows,
        "manifest_stage5_status": manifest.get("stage5_status"),
        "serious_packet_status": serious_packet.get("status"),
        "benchmark_claim": False,
        "blockers": blockers,
    }


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"expected mapping in {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"expected object in {path}")
    return data


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
