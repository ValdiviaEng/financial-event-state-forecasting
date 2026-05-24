"""Stage 6 serious benchmark reporting from saved predictions."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import yaml

from event_state_forecasting.benchmark.artifact_packet import validate_artifact_packet
from event_state_forecasting.evaluation.comparison_summary import (
    build_benchmark_comparability_record,
    build_comparison_summary,
    build_overfitting_diagnostic_report,
)
from event_state_forecasting.evaluation.ranking import compute_ranking_diagnostics
from event_state_forecasting.evaluation.regression import (
    align_predictions_with_labels,
    attach_loss_differences,
    compute_regression_metrics,
    select_market_hurdles,
)
from event_state_forecasting.evaluation.statistical_tests import compute_paired_loss_deltas


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEATURE_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
SPLIT_VERSION = f"{FEATURE_VERSION}__stage4_splits_v1"
STAGE5_VERSION = f"{SPLIT_VERSION}__stage5_models_v1"
STAGE6_VERSION = f"{STAGE5_VERSION}__stage6_reporting_v1"
FEATURE_ROOT = PROJECT_ROOT / "data" / "features" / "phase1_top50" / FEATURE_VERSION
SPLIT_ROOT = PROJECT_ROOT / "data" / "splits" / "phase1_top50" / SPLIT_VERSION
MODEL_ROOT = PROJECT_ROOT / "data" / "models" / "phase1_top50" / STAGE5_VERSION
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "benchmark_runs" / "phase1_top50" / STAGE6_VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Stage 6 serious benchmark reporting from saved predictions.")
    parser.add_argument("--feature-root", type=Path, default=FEATURE_ROOT)
    parser.add_argument("--split-root", type=Path, default=SPLIT_ROOT)
    parser.add_argument("--model-root", type=Path, default=MODEL_ROOT)
    parser.add_argument("--evaluation-config", type=Path, default=PROJECT_ROOT / "configs" / "evaluation.yaml")
    parser.add_argument("--split-config", type=Path, default=PROJECT_ROOT / "configs" / "splits.yaml")
    parser.add_argument("--packet-config", type=Path, default=PROJECT_ROOT / "configs" / "artifact_packet.yaml")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    config = load_yaml_or_json(args.evaluation_config)
    packet_config = load_yaml_or_json(args.packet_config)
    feature_manifest = load_json(args.feature_root / "feature_label_manifest.json")
    split_manifest = load_json(args.split_root / "split_manifest.json")
    stage5_manifest = load_json(args.model_root / "model_manifest.json")
    search_space_summary = load_json(args.model_root / "search_space_summary.json")

    predictions = pd.read_parquet(args.model_root / "saved_predictions.parquet")
    labels = pd.read_parquet(args.feature_root / "labels.parquet")
    aligned = align_predictions_with_labels(predictions, labels)
    prediction_validation = build_prediction_label_validation(aligned, predictions, labels, stage5_manifest)

    metrics = compute_regression_metrics(aligned, config)
    selected_market_hurdles = select_market_hurdles(metrics, config)
    paired = compute_paired_loss_deltas(aligned, selected_market_hurdles, config)
    metrics = attach_loss_differences(metrics, paired)
    ranking = compute_ranking_diagnostics(aligned, config)

    diagnostic_report = build_overfitting_diagnostic_report(
        metrics,
        paired,
        config,
        search_space_summary,
        training_prediction_available=False,
    )
    comparison_summary = build_comparison_summary(
        metrics,
        ranking,
        paired,
        selected_market_hurdles,
        diagnostic_report,
        config,
    )

    resolved_config_path = output_root / "resolved_evaluation_config.json"
    prediction_validation_path = output_root / "prediction_label_validation.json"
    metrics_path = output_root / "metrics.parquet"
    ranking_path = output_root / "ranking_diagnostics.parquet"
    paired_path = output_root / "paired_comparisons.parquet"
    diagnostic_path = output_root / "overfitting_diagnostic_report.json"
    comparison_path = output_root / "comparison_summary.json"
    packet_path = output_root / "serious_packet_validation.json"
    comparability_path = output_root / "benchmark_comparability.json"
    manifest_path = output_root / "evaluation_manifest.json"

    write_json(resolved_config_path, config)
    write_json(prediction_validation_path, prediction_validation)
    metrics.to_parquet(metrics_path, index=False)
    ranking.to_parquet(ranking_path, index=False)
    paired.to_parquet(paired_path, index=False)
    write_json(diagnostic_path, diagnostic_report)
    write_json(comparison_path, comparison_summary)

    packet_validation = validate_artifact_packet(
        build_stage6_member_map(
            feature_manifest=feature_manifest,
            split_manifest=split_manifest,
            split_config=args.split_config,
            packet_config=args.packet_config,
            stage5_manifest=stage5_manifest,
            metrics=metrics_path,
            diagnostic_report=diagnostic_path,
            comparison_summary=comparison_path,
        ),
        packet_config,
        mode="serious_run",
    )
    write_json(packet_path, packet_validation)
    comparability = build_benchmark_comparability_record(packet_validation, diagnostic_report)
    write_json(comparability_path, comparability)

    manifest = build_evaluation_manifest(
        output_root=output_root,
        feature_manifest=feature_manifest,
        split_manifest=split_manifest,
        stage5_manifest=stage5_manifest,
        metrics=metrics,
        ranking=ranking,
        paired=paired,
        selected_market_hurdles=selected_market_hurdles,
        comparison_summary=comparison_summary,
        comparability=comparability,
        packet_validation=packet_validation,
        paths={
            "resolved_evaluation_config": resolved_config_path,
            "prediction_label_validation": prediction_validation_path,
            "metrics": metrics_path,
            "ranking_diagnostics": ranking_path,
            "paired_comparisons": paired_path,
            "overfitting_diagnostic_report": diagnostic_path,
            "comparison_summary": comparison_path,
            "serious_packet_validation": packet_path,
            "benchmark_comparability": comparability_path,
        },
    )
    write_json(manifest_path, manifest)

    print(
        "stage6_serious_benchmark_reporting_built",
        "result_class",
        comparison_summary["result_class"],
        "comparability",
        comparability["comparability_classification"],
        "artifact_root",
        output_root,
    )
    return 0


def build_prediction_label_validation(
    aligned: pd.DataFrame,
    predictions: pd.DataFrame,
    labels: pd.DataFrame,
    stage5_manifest: Mapping[str, Any],
) -> dict[str, Any]:
    role_counts = {str(key): int(value) for key, value in predictions["split_role"].value_counts().sort_index().items()}
    return {
        "artifact_type": "prediction_label_validation",
        "artifact_schema_version": "stage6_reporting_v1",
        "generated_at_utc": now_utc(),
        "status": "passed",
        "saved_prediction_rows": int(len(predictions)),
        "aligned_prediction_label_rows": int(len(aligned)),
        "frozen_label_rows": int(len(labels)),
        "prediction_role_counts": role_counts,
        "model_count": int(predictions["model_id"].nunique()),
        "horizon_count": int(predictions["horizon_id"].nunique()),
        "fold_count": int(predictions["fold_id"].nunique()),
        "dataset_version": str(predictions["dataset_version"].iloc[0]),
        "stage5_artifact_version": stage5_manifest["identity"]["artifact_version"],
        "out_of_sample_roles_only": sorted(role_counts) == ["lockbox", "validation"],
        "lockbox_metrics_policy": "final_reporting_read_once_v1",
    }


def build_stage6_member_map(
    *,
    feature_manifest: Mapping[str, Any],
    split_manifest: Mapping[str, Any],
    split_config: Path,
    packet_config: Path,
    stage5_manifest: Mapping[str, Any],
    metrics: Path,
    diagnostic_report: Path,
    comparison_summary: Path,
) -> dict[str, str]:
    return {
        "dataset_manifest": str(feature_manifest["inputs"]["dataset_manifest"]),
        "feature_label_manifest": str(Path(feature_manifest["artifacts"]["artifact_root"]) / "feature_label_manifest.json"),
        "resolved_split_config": str(split_config),
        "artifact_packet_config": str(packet_config),
        "split_manifest": str(Path(split_manifest["artifacts"]["split_manifest"])),
        "fold_definitions": str(Path(split_manifest["artifacts"]["fold_definitions"])),
        "split_assignments": str(Path(split_manifest["artifacts"]["split_assignments"])),
        "lockbox_record": str(Path(split_manifest["artifacts"]["lockbox_record"])),
        "leakage_validation": str(Path(split_manifest["artifacts"]["leakage_validation"])),
        "preprocessing_fit_manifest": str(Path(stage5_manifest["outputs"]["preprocessing_fit_manifest"])),
        "saved_predictions": str(Path(stage5_manifest["outputs"]["saved_predictions"])),
        "metrics": str(metrics),
        "overfitting_diagnostic_report": str(diagnostic_report),
        "comparison_summary": str(comparison_summary),
    }


def build_evaluation_manifest(
    *,
    output_root: Path,
    feature_manifest: Mapping[str, Any],
    split_manifest: Mapping[str, Any],
    stage5_manifest: Mapping[str, Any],
    metrics: pd.DataFrame,
    ranking: pd.DataFrame,
    paired: pd.DataFrame,
    selected_market_hurdles: Mapping[str, str],
    comparison_summary: Mapping[str, Any],
    comparability: Mapping[str, Any],
    packet_validation: Mapping[str, Any],
    paths: Mapping[str, Path],
) -> dict[str, Any]:
    return {
        "artifact_type": "stage6_serious_benchmark_reporting_manifest",
        "artifact_schema_version": "stage6_reporting_v1",
        "generated_at_utc": now_utc(),
        "stage6_status": "stage6_serious_benchmark_reporting_created",
        "benchmark_claim": packet_validation.get("status") == "passed",
        "identity": {
            "artifact_version": STAGE6_VERSION,
            "artifact_root": str(output_root),
            "input_feature_artifact_version": feature_manifest["identity"]["artifact_version"],
            "input_split_artifact_version": split_manifest["identity"]["artifact_version"],
            "input_stage5_artifact_version": stage5_manifest["identity"]["artifact_version"],
            "row_universe_digest": stage5_manifest["identity"]["row_universe_digest"],
        },
        "counts": {
            "metric_rows": int(len(metrics)),
            "ranking_diagnostic_rows": int(len(ranking)),
            "paired_comparison_rows": int(len(paired)),
            "model_count": int(metrics["model_id"].nunique()),
            "horizon_count": int(metrics["horizon_id"].nunique()),
        },
        "selected_market_hurdles": dict(selected_market_hurdles),
        "result_class": comparison_summary["result_class"],
        "comparability_classification": comparability["comparability_classification"],
        "serious_packet_status": packet_validation.get("status"),
        "outputs": {name: str(path) for name, path in paths.items()},
        "limitations": comparability.get("limitation_reasons", []),
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


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
