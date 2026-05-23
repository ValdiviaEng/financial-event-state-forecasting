#!/usr/bin/env python3
"""Validate Stage 6 serious benchmark reporting artifacts."""

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
STAGE6_ARTIFACT_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1"
DEFAULT_STAGE6_ROOT = PROJECT_ROOT / "data" / "benchmark_runs" / "phase1_top50" / STAGE6_ARTIFACT_VERSION
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage6_completion_validation_2026-05-21.json"
REQUIRED_METRIC_COLUMNS = {
    "aggregation_level",
    "split_role",
    "fold_id",
    "horizon_id",
    "model_id",
    "rmse",
    "mae",
    "r2_oos",
    "mean_squared_loss_diff",
    "mean_absolute_loss_diff",
}
ALLOWED_RESULT_CLASSES = {"robust_positive", "conditional_positive", "clean_null"}
ALLOWED_COMPARABILITY = {"comparable", "limitation_bearing", "invalidated", "not_comparable"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 6 completion artifacts.")
    parser.add_argument("--stage6-root", type=Path, default=DEFAULT_STAGE6_ROOT)
    parser.add_argument("--evaluation-config", type=Path, default=PROJECT_ROOT / "configs" / "evaluation.yaml")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_stage6(args.stage6_root, args.evaluation_config)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "passed":
        print("STAGE6_COMPLETION_VALIDATION FAILED")
        for blocker in result["blockers"]:
            print(f"- {blocker}")
        return 1
    print("STAGE6_COMPLETION_VALIDATION PASSED")
    print("result_class:", result["result_class"])
    print("comparability:", result["comparability_classification"])
    return 0


def validate_stage6(stage6_root: Path, evaluation_config: Path) -> dict[str, Any]:
    blockers: list[str] = []
    config = load_yaml_or_json(evaluation_config)
    required_files = {
        "evaluation_manifest": stage6_root / "evaluation_manifest.json",
        "resolved_evaluation_config": stage6_root / "resolved_evaluation_config.json",
        "prediction_label_validation": stage6_root / "prediction_label_validation.json",
        "metrics": stage6_root / "metrics.parquet",
        "ranking_diagnostics": stage6_root / "ranking_diagnostics.parquet",
        "paired_comparisons": stage6_root / "paired_comparisons.parquet",
        "overfitting_diagnostic_report": stage6_root / "overfitting_diagnostic_report.json",
        "comparison_summary": stage6_root / "comparison_summary.json",
        "serious_packet_validation": stage6_root / "serious_packet_validation.json",
        "benchmark_comparability": stage6_root / "benchmark_comparability.json",
    }
    for name, path in required_files.items():
        if not path.exists():
            blockers.append(f"missing_{name}")

    manifest: dict[str, Any] = {}
    comparison: dict[str, Any] = {}
    comparability: dict[str, Any] = {}
    packet: dict[str, Any] = {}
    validation: dict[str, Any] = {}
    metric_rows = 0
    ranking_rows = 0
    paired_rows = 0
    if not blockers:
        manifest = load_json(required_files["evaluation_manifest"])
        comparison = load_json(required_files["comparison_summary"])
        comparability = load_json(required_files["benchmark_comparability"])
        packet = load_json(required_files["serious_packet_validation"])
        validation = load_json(required_files["prediction_label_validation"])
        diagnostics = load_json(required_files["overfitting_diagnostic_report"])
        metrics = pd.read_parquet(required_files["metrics"])
        ranking = pd.read_parquet(required_files["ranking_diagnostics"])
        paired = pd.read_parquet(required_files["paired_comparisons"])
        metric_rows = len(metrics)
        ranking_rows = len(ranking)
        paired_rows = len(paired)

        if manifest.get("artifact_schema_version") != "stage6_reporting_v1":
            blockers.append("manifest_schema_mismatch")
        if manifest.get("stage6_status") != "stage6_serious_benchmark_reporting_created":
            blockers.append("stage6_status_not_created")
        if packet.get("status") != "passed" or packet.get("serious_claim_allowed") is not True:
            blockers.append("serious_packet_not_passed")
        if comparison.get("result_class") not in ALLOWED_RESULT_CLASSES:
            blockers.append("result_class_invalid")
        if comparability.get("comparability_classification") not in ALLOWED_COMPARABILITY:
            blockers.append("comparability_classification_invalid")
        if validation.get("status") != "passed" or validation.get("out_of_sample_roles_only") is not True:
            blockers.append("prediction_label_validation_not_passed")
        missing_metric_columns = REQUIRED_METRIC_COLUMNS - set(metrics.columns)
        if missing_metric_columns:
            blockers.append(f"metrics_missing_columns:{sorted(missing_metric_columns)}")
        if metric_rows == 0 or ranking_rows == 0 or paired_rows == 0:
            blockers.append("empty_stage6_metric_artifacts")
        if set(config["result_classification"]["primary_horizons"]) != set(comparison["classification_policy"]["primary_horizons"]):
            blockers.append("classification_policy_drift")
        if diagnostics.get("diagnostic_status") not in {"complete", "complete_with_explicit_train_gap_blocker"}:
            blockers.append("diagnostic_status_invalid")
        missing_packet_members = packet.get("missing_members", []) or packet.get("missing_paths", [])
        if missing_packet_members:
            blockers.append("serious_packet_has_missing_members")

    status = "passed" if not blockers else "failed"
    return {
        "artifact_type": "stage6_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": status,
        "stage6_root": str(stage6_root),
        "benchmark_claim": status == "passed",
        "result_class": comparison.get("result_class"),
        "comparability_classification": comparability.get("comparability_classification"),
        "serious_packet_status": packet.get("status"),
        "metric_rows": metric_rows,
        "ranking_diagnostic_rows": ranking_rows,
        "paired_comparison_rows": paired_rows,
        "manifest_stage6_status": manifest.get("stage6_status"),
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
