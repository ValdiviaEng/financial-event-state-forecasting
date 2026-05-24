"""Stage 5 model training and saved-prediction materialization CLI."""

from __future__ import annotations

import argparse
import json
import random
import sys
import warnings
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd
import yaml

from event_state_forecasting.benchmark.artifact_packet import validate_artifact_packet
from event_state_forecasting.models.comparator_ladder import ModelSpec, freeze_comparator_ladder, validate_model_config
from event_state_forecasting.models.gated_fusion import make_gated_fusion_estimator
from event_state_forecasting.models.inference import build_prediction_frame, validate_saved_predictions
from event_state_forecasting.models.market_baselines import make_market_estimator
from event_state_forecasting.models.training import fit_fold_preprocessor, stable_payload_digest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEATURE_ROOT = PROJECT_ROOT / "data" / "features" / "phase1_top50" / "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
SPLIT_ROOT = PROJECT_ROOT / "data" / "splits" / "phase1_top50" / "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
MODEL_SCHEMA_VERSION = "stage5_models_v1"
KEY_COLUMNS = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Materialize Stage 5 model predictions without metrics.")
    parser.add_argument("--feature-root", type=Path, default=FEATURE_ROOT)
    parser.add_argument("--split-root", type=Path, default=SPLIT_ROOT)
    parser.add_argument("--model-config", type=Path, default=PROJECT_ROOT / "configs" / "models.yaml")
    parser.add_argument("--split-config", type=Path, default=PROJECT_ROOT / "configs" / "splits.yaml")
    parser.add_argument("--packet-config", type=Path, default=PROJECT_ROOT / "configs" / "artifact_packet.yaml")
    parser.add_argument("--output-root", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_yaml_or_json(args.model_config)
    specs = validate_model_config(config)
    seed = int(config["comparator_ladder"]["seed"])
    random.seed(seed)
    np.random.seed(seed)

    feature_manifest = load_json(args.feature_root / "feature_label_manifest.json")
    split_manifest = load_json(args.split_root / "split_manifest.json")
    feature_artifact_version = feature_manifest["identity"]["artifact_version"]
    split_artifact_version = split_manifest["identity"]["artifact_version"]
    stage5_artifact_version = f"{split_artifact_version}__stage5_models_v1"
    output_root = args.output_root or PROJECT_ROOT / "data" / "models" / "phase1_top50" / stage5_artifact_version
    params_root = output_root / "preprocessing_params"
    output_root.mkdir(parents=True, exist_ok=True)
    params_root.mkdir(parents=True, exist_ok=True)

    panel = load_training_panel(args.feature_root, args.split_root, config)
    model_ids = [spec.model_id for spec in specs]
    prediction_frames: list[pd.DataFrame] = []
    preprocessing_records: list[dict[str, Any]] = []
    fit_records: list[dict[str, Any]] = []
    diagnostic_records: list[dict[str, Any]] = []

    folds = sorted(panel["fold_id"].unique())
    horizons = sorted(panel["horizon_id"].unique(), key=horizon_sort_key)
    for fold_id in folds:
        for horizon_id in horizons:
            fold_horizon = panel[(panel["fold_id"] == fold_id) & (panel["horizon_id"] == horizon_id)].copy()
            train_rows = fold_horizon[fold_horizon["split_role"] == "train"].sort_values(KEY_COLUMNS)
            prediction_rows = fold_horizon[fold_horizon["split_role"].isin(["validation", "lockbox"])].sort_values(
                ["split_role", *KEY_COLUMNS]
            )
            if train_rows.empty or prediction_rows.empty:
                raise RuntimeError(f"empty train or prediction rows for {fold_id} {horizon_id}")
            y_train = train_rows["forward_excess_return"].astype("float64").to_numpy()

            for spec in specs:
                feature_columns = feature_columns_for_spec(spec, config)
                preprocessor = fit_fold_preprocessor(
                    train_rows,
                    feature_columns=feature_columns,
                    policy=spec.preprocessing,
                )
                X_train = preprocessor.transform(train_rows)
                X_pred = preprocessor.transform(prediction_rows)
                estimator = make_estimator(spec, config, seed=seed)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    estimator.fit(X_train, y_train)
                pred = estimator.predict(X_pred)

                parameter_payload = preprocessor.parameter_payload()
                param_path = params_root / f"{fold_id}__{horizon_id}__{spec.model_id}.json"
                write_json(param_path, parameter_payload)
                warning_messages = [str(item.message) for item in caught]

                prediction_frames.append(
                    build_prediction_frame(
                        prediction_rows,
                        pred,
                        model_id=spec.model_id,
                        model_family=spec.family,
                        branch=spec.branch,
                        feature_artifact_version=feature_artifact_version,
                        split_artifact_version=split_artifact_version,
                        stage5_artifact_version=stage5_artifact_version,
                    )
                )
                preprocessing_records.append(
                    {
                        "fold_id": fold_id,
                        "horizon_id": horizon_id,
                        "model_id": spec.model_id,
                        "preprocessing_policy": spec.preprocessing,
                        "fit_split_role": "train",
                        "fit_row_count": len(train_rows),
                        "preprocessing_fit_allowed_only": True,
                        "feature_count": len(feature_columns),
                        "feature_columns_digest": stable_payload_digest(list(feature_columns)),
                        "parameters_path": str(param_path),
                        "parameter_digest": parameter_payload["parameter_digest"],
                    }
                )
                fit_records.append(
                    {
                        "fold_id": fold_id,
                        "horizon_id": horizon_id,
                        "model_id": spec.model_id,
                        "model_family": spec.family,
                        "branch": spec.branch,
                        "seed": seed,
                        "search_policy": config["comparator_ladder"]["search_policy"],
                        "allowed_inputs": ";".join(spec.allowed_inputs),
                        "train_row_count": len(train_rows),
                        "validation_prediction_row_count": int((prediction_rows["split_role"] == "validation").sum()),
                        "lockbox_prediction_row_count": int((prediction_rows["split_role"] == "lockbox").sum()),
                        "fit_status": "fitted_with_warnings" if warning_messages else "fitted",
                        "warning_count": len(warning_messages),
                        "model_params_digest": stable_payload_digest(dict(spec.params)),
                    }
                )
                diagnostic_records.append(
                    {
                        "fold_id": fold_id,
                        "horizon_id": horizon_id,
                        "model_id": spec.model_id,
                        "fit_status": "fitted_with_warnings" if warning_messages else "fitted",
                        "warning_messages": " | ".join(warning_messages),
                        "train_row_count": len(train_rows),
                        "train_target_mean": float(np.mean(y_train)),
                        "train_target_std": float(np.std(y_train)),
                        "metrics_computed": False,
                        "benchmark_claim": False,
                    }
                )

    predictions = pd.concat(prediction_frames, ignore_index=True)
    validate_saved_predictions(predictions, expected_model_ids=model_ids)
    preprocessing_manifest = pd.DataFrame(preprocessing_records)
    model_fit_manifest = pd.DataFrame(fit_records)
    training_diagnostics = pd.DataFrame(diagnostic_records)

    resolved_config_path = output_root / "resolved_model_config.json"
    roster_path = output_root / "comparator_roster_record.json"
    predictions_path = output_root / "saved_predictions.parquet"
    preprocessing_path = output_root / "preprocessing_fit_manifest.parquet"
    model_fit_path = output_root / "model_fit_manifest.parquet"
    diagnostics_path = output_root / "training_diagnostics.parquet"
    search_path = output_root / "search_space_summary.json"
    serious_packet_path = output_root / "serious_packet_validation.json"
    manifest_path = output_root / "model_manifest.json"

    write_json(resolved_config_path, config)
    write_json(roster_path, freeze_comparator_ladder(config))
    predictions.to_parquet(predictions_path, index=False)
    preprocessing_manifest.to_parquet(preprocessing_path, index=False)
    model_fit_manifest.to_parquet(model_fit_path, index=False)
    training_diagnostics.to_parquet(diagnostics_path, index=False)
    write_json(search_path, build_search_space_summary(config, specs, folds, horizons))

    packet_config = load_yaml_or_json(args.packet_config)
    serious_packet = validate_artifact_packet(
        build_stage5_member_map(
            feature_manifest=feature_manifest,
            split_manifest=split_manifest,
            split_config=args.split_config,
            packet_config=args.packet_config,
            preprocessing_fit_manifest=preprocessing_path,
            saved_predictions=predictions_path,
        ),
        packet_config,
        mode="serious_run",
    )
    write_json(serious_packet_path, serious_packet)

    manifest = build_model_manifest(
        output_root=output_root,
        stage5_artifact_version=stage5_artifact_version,
        feature_manifest=feature_manifest,
        split_manifest=split_manifest,
        config=config,
        predictions=predictions,
        preprocessing_manifest=preprocessing_manifest,
        model_fit_manifest=model_fit_manifest,
        serious_packet=serious_packet,
        paths={
            "resolved_model_config": resolved_config_path,
            "comparator_roster_record": roster_path,
            "saved_predictions": predictions_path,
            "preprocessing_fit_manifest": preprocessing_path,
            "model_fit_manifest": model_fit_path,
            "training_diagnostics": diagnostics_path,
            "search_space_summary": search_path,
            "serious_packet_validation": serious_packet_path,
        },
    )
    write_json(manifest_path, manifest)
    print(
        "stage5_models_predictions_built",
        "model_count",
        len(model_ids),
        "prediction_row_count",
        len(predictions),
        "artifact_root",
        output_root,
    )
    return 0


def load_training_panel(feature_root: Path, split_root: Path, config: Mapping[str, Any]) -> pd.DataFrame:
    market_columns = list(config["feature_sets"]["market_features"])
    event_columns = list(config["feature_sets"]["event_state_features"])
    market = pd.read_parquet(feature_root / "market_features.parquet", columns=[*KEY_COLUMNS, "dataset_version", *market_columns])
    event = pd.read_parquet(feature_root / "event_state_features.parquet", columns=[*KEY_COLUMNS, *event_columns])
    labels = pd.read_parquet(
        feature_root / "labels.parquet",
        columns=[*KEY_COLUMNS, "forward_excess_return", "label_available_flag"],
    )
    assignments = pd.read_parquet(split_root / "split_assignments.parquet")
    features = market.merge(event, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    features = features.merge(labels, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    panel = assignments.merge(features, on=KEY_COLUMNS + ["dataset_version"], how="left", validate="many_to_one")
    if panel["forward_excess_return"].isna().any():
        raise RuntimeError("split assignments failed to align with labels")
    if not bool(panel["label_available_flag"].all()):
        raise RuntimeError("Stage 5 requires label-available rows only")
    return panel


def feature_columns_for_spec(spec: ModelSpec, config: Mapping[str, Any]) -> list[str]:
    market_columns = list(config["feature_sets"]["market_features"])
    if spec.family in {"constant_zero", "constant_train_mean"}:
        return []
    if spec.allowed_inputs == ("market_features",):
        return market_columns
    event_columns = list(config["feature_sets"]["event_state_features"])
    return [*market_columns, *event_columns]


def make_estimator(spec: ModelSpec, config: Mapping[str, Any], *, seed: int):
    if spec.family == "simple_gated_fusion":
        return make_gated_fusion_estimator(
            n_market_features=len(config["feature_sets"]["market_features"]),
            event_feature_columns=config["feature_sets"]["event_state_features"],
            gate_feature_columns=config["feature_sets"]["gated_fusion_gate_features"],
            alpha=float(spec.params.get("alpha", 1.0)),
        )
    return make_market_estimator(spec.family, spec.params, seed=seed)


def build_search_space_summary(
    config: Mapping[str, Any], specs: list[ModelSpec], folds: list[str], horizons: list[str]
) -> dict[str, Any]:
    return {
        "artifact_type": "stage5_search_space_summary",
        "artifact_schema_version": MODEL_SCHEMA_VERSION,
        "generated_at_utc": now_utc(),
        "search_policy": config["comparator_ladder"]["search_policy"],
        "seed": config["comparator_ladder"]["seed"],
        "hyperparameter_search_attempts": 0,
        "fixed_model_count": len(specs),
        "model_ids": [spec.model_id for spec in specs],
        "fold_count": len(folds),
        "horizon_ids": horizons,
        "metrics_computed": False,
        "benchmark_claim": False,
    }


def build_stage5_member_map(
    *,
    feature_manifest: Mapping[str, Any],
    split_manifest: Mapping[str, Any],
    split_config: Path,
    packet_config: Path,
    preprocessing_fit_manifest: Path,
    saved_predictions: Path,
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
        "preprocessing_fit_manifest": str(preprocessing_fit_manifest),
        "saved_predictions": str(saved_predictions),
    }


def build_model_manifest(
    *,
    output_root: Path,
    stage5_artifact_version: str,
    feature_manifest: Mapping[str, Any],
    split_manifest: Mapping[str, Any],
    config: Mapping[str, Any],
    predictions: pd.DataFrame,
    preprocessing_manifest: pd.DataFrame,
    model_fit_manifest: pd.DataFrame,
    serious_packet: Mapping[str, Any],
    paths: Mapping[str, Path],
) -> dict[str, Any]:
    role_counts = {str(key): int(value) for key, value in predictions["split_role"].value_counts().sort_index().items()}
    return {
        "artifact_type": "stage5_model_prediction_manifest",
        "artifact_schema_version": MODEL_SCHEMA_VERSION,
        "generated_at_utc": now_utc(),
        "benchmark_claim": False,
        "identity": {
            "artifact_version": stage5_artifact_version,
            "artifact_root": str(output_root),
            "input_feature_artifact_version": feature_manifest["identity"]["artifact_version"],
            "input_split_artifact_version": split_manifest["identity"]["artifact_version"],
            "row_universe_digest": feature_manifest["row_universe"]["row_universe_digest"],
        },
        "roster": {
            "roster_id": config["comparator_ladder"]["roster_id"],
            "model_count": int(predictions["model_id"].nunique()),
            "model_ids": sorted(str(value) for value in predictions["model_id"].unique()),
            "seed": config["comparator_ladder"]["seed"],
            "search_policy": config["comparator_ladder"]["search_policy"],
        },
        "outputs": {name: str(path) for name, path in paths.items()},
        "counts": {
            "fold_count": int(model_fit_manifest["fold_id"].nunique()),
            "horizon_count": int(model_fit_manifest["horizon_id"].nunique()),
            "model_fit_count": int(len(model_fit_manifest)),
            "preprocessing_fit_count": int(len(preprocessing_manifest)),
            "saved_prediction_row_count": int(len(predictions)),
            "prediction_role_counts": role_counts,
        },
        "stage5_status": "stage5_model_prediction_artifacts_created",
        "serious_packet_status": serious_packet.get("status"),
        "non_claims": [
            "not_metrics",
            "not_overfitting_diagnostic_report",
            "not_comparison_summary",
            "not_benchmark_result",
        ],
        "lockbox_policy": {
            "lockbox_predictions_created": True,
            "lockbox_metrics_computed": False,
            "lockbox_used_for_selection": False,
        },
    }


def horizon_sort_key(value: str) -> int:
    return int(str(value).removesuffix("d"))


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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
