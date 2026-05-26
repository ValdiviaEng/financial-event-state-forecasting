from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.modeling import fit_preprocessor, validate_prediction_schema  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402


FEATURE_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
STAGE20_ROOT = PROJECT_ROOT / "data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z"
STAGE22_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_AT_UTC = "2026-05-24T08:30:00Z"
SOURCE_ID = "6dff1bd"
MODEL_ID = "market_xgboost_v2_frozen_final"
SPLIT_ARTIFACT_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the v1p0 Stage 23 frozen XGBoost final evaluation exactly once.")
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()

    started = time.perf_counter()
    best_config = json.loads((STAGE22_ROOT / "best_development_candidate_config.json").read_text(encoding="utf-8"))
    search_manifest = json.loads((STAGE22_ROOT / "search_manifest.json").read_text(encoding="utf-8"))
    _validate_frozen_inputs(best_config, search_manifest)
    best_config_digest = _stable_digest(best_config)
    run_id = f"v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_{SOURCE_ID}__run_{best_config_digest[:8]}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    feature_manifest = json.loads((FEATURE_ROOT / "feature_manifest.json").read_text(encoding="utf-8"))
    frame = _load_scoring_frame(feature_manifest)
    predictions, fit_records, preprocessing_records = _run_frozen_model(frame, list(feature_manifest["feature_columns"]), best_config, feature_manifest)
    model_config = load_json_config(PROJECT_ROOT / "configs/models_v1p0.yaml")
    schema_result = validate_prediction_schema(predictions, model_config["saved_prediction_schema"]["required_columns"])

    prediction_path = output_root / "saved_predictions.parquet"
    metrics_path = output_root / "metrics.parquet"
    hurdle_deltas_path = output_root / "hurdle_deltas.parquet"
    fit_path = output_root / "model_fit_manifest.parquet"
    preprocessing_path = output_root / "preprocessing_fit_manifest.parquet"
    predictions.to_parquet(prediction_path, index=False)
    metrics = _compute_metrics(predictions)
    hurdle_deltas = _compute_hurdle_deltas(metrics)
    metrics.to_parquet(metrics_path, index=False)
    hurdle_deltas.to_parquet(hurdle_deltas_path, index=False)
    pd.DataFrame.from_records(fit_records).to_parquet(fit_path, index=False)
    pd.DataFrame.from_records(preprocessing_records).to_parquet(preprocessing_path, index=False)

    manifest_path = output_root / "final_evaluation_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage23_xgboost_frozen_final_report.md"
    prediction_digest = _sha256(prediction_path)
    manifest = {
        "artifact_type": "v1p0_stage23_xgboost_frozen_final_manifest",
        "artifact_id": f"xgboost_stage23_frozen_final__stage22_trial_{best_config['selected_trial_id']}__20260524T083000Z",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed",
        "model_id": MODEL_ID,
        "source_stage22_artifact_id": search_manifest["artifact_id"],
        "source_stage22_best_trial_id": int(best_config["selected_trial_id"]),
        "best_config_digest_sha256": best_config_digest,
        "search_config_digest_sha256": best_config["search_config_digest_sha256"],
        "prediction_digest_sha256": prediction_digest,
        "prediction_role_counts": {str(k): int(v) for k, v in predictions["split_role"].value_counts().sort_index().items()},
        "prediction_row_count": int(len(predictions)),
        "metric_rows": int(len(metrics)),
        "hurdle_delta_rows": int(len(hurdle_deltas)),
        "schema_validation": schema_result,
        "model_fit_count": len(fit_records),
        "preprocessing_fit_count": len(preprocessing_records),
        "outputs": {
            "saved_predictions": _rel(prediction_path),
            "metrics": _rel(metrics_path),
            "hurdle_deltas": _rel(hurdle_deltas_path),
            "model_fit_manifest": _rel(fit_path),
            "preprocessing_fit_manifest": _rel(preprocessing_path),
            "final_evaluation_manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "lockbox_policy": {
            "frozen_before_lockbox_evaluation": True,
            "lockbox_used_for_selection": False,
            "lockbox_metrics_computed_once_for_reporting": True,
        },
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "benchmark_claim": False,
        "promotion_claim": False,
        "non_claims": ["not_promotion_claim", "not_stage6_reinterpretation", "not_trading_signal", "claim_review_pending_stage39"],
    }
    _write_json(manifest_path, manifest)
    run_manifest = {
        "run_id": run_id,
        "stage": 23,
        "stage_name": "xgboost_frozen_final_evaluation",
        "generated_at_utc": GENERATED_AT_UTC,
        "status": "completed",
        "command": "source ~/venvs/ai/bin/activate && python scripts/run_v1p0_xgboost_frozen_final_evaluation.py",
        "outputs": manifest["outputs"],
        "benchmark_claim": False,
        "promotion_claim": False,
        "lockbox_tuning": False,
    }
    _write_json(run_manifest_path, run_manifest)
    report_path.write_text(_render_report(manifest, hurdle_deltas), encoding="utf-8")
    print(json.dumps({"status": "completed", "model_id": MODEL_ID, "prediction_rows": len(predictions), "metric_rows": len(metrics), "hurdle_delta_rows": len(hurdle_deltas), "output_root": _rel(output_root)}, sort_keys=True))


def _validate_frozen_inputs(best_config: dict[str, Any], search_manifest: dict[str, Any]) -> None:
    if search_manifest.get("status") != "completed":
        raise RuntimeError("Stage 22 search manifest must be completed before Stage 23")
    if best_config.get("lockbox_used_for_selection"):
        raise RuntimeError("frozen final config cannot be selected with lockbox evidence")
    if search_manifest.get("lockbox_policy", {}).get("lockbox_used_for_candidate_selection"):
        raise RuntimeError("Stage 22 manifest reports lockbox candidate selection")
    if best_config.get("selection_basis") != "development_validation_guarded_hurdle_delta_only":
        raise RuntimeError("Stage 23 requires a development-selected frozen candidate")


def _load_scoring_frame(feature_manifest: dict[str, Any]) -> pd.DataFrame:
    row_key = list(feature_manifest["row_key"])
    features = pd.read_parquet(PROJECT_ROOT / feature_manifest["outputs"]["market_lag_features"])
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*row_key, "forward_excess_return"])
    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet", columns=["fold_id", *row_key, "split_role", "lockbox_flag", "preprocessing_fit_allowed"])
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
    frame = splits.merge(features, on=row_key, how="inner", validate="many_to_one").merge(labels, on=row_key, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target"})
    frame["row_key"] = frame[row_key].astype(str).agg("|".join, axis=1)
    frame["feature_artifact_version"] = feature_manifest["artifact_id"]
    frame["split_artifact_version"] = SPLIT_ARTIFACT_VERSION
    frame["v1p0_artifact_version"] = "xgboost_stage23_frozen_final_v1"
    return frame


def _run_frozen_model(frame: pd.DataFrame, feature_columns: list[str], best_config: dict[str, Any], feature_manifest: dict[str, Any]) -> tuple[pd.DataFrame, list[dict[str, Any]], list[dict[str, Any]]]:
    from xgboost import XGBRegressor

    records: list[pd.DataFrame] = []
    fit_records: list[dict[str, Any]] = []
    preprocessing_records: list[dict[str, Any]] = []
    params = dict(best_config["resolved_xgboost_params"])
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        score = group[group["split_role"].isin(["train", "validation", "lockbox"])].copy()
        if train.empty or score.empty:
            continue
        fit_started = time.perf_counter()
        preprocessor = fit_preprocessor(train, feature_columns, "median_impute")
        estimator = XGBRegressor(**params)
        estimator.fit(preprocessor.transform(train), train["target"].astype("float64"))
        training_time = time.perf_counter() - fit_started
        infer_started = time.perf_counter()
        prediction = estimator.predict(preprocessor.transform(score))
        inference_time = time.perf_counter() - infer_started
        output = score[["row_key", "benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id", "fold_id", "split_role", "dataset_version", "feature_artifact_version", "split_artifact_version", "v1p0_artifact_version", "target"]].copy()
        output["model_id"] = MODEL_ID
        output["model_family"] = "xgboost_regressor"
        output["branch"] = "market_only"
        output["prediction"] = prediction
        records.append(output)
        fit_records.append({"model_id": MODEL_ID, "model_family": "xgboost_regressor", "fold_id": fold_id, "horizon_id": horizon_id, "train_rows": int(len(train)), "score_rows": int(len(score)), "training_time_seconds": round(training_time, 6), "inference_time_seconds": round(inference_time, 6), "params_json": json.dumps(params, sort_keys=True), "selected_stage22_trial_id": int(best_config["selected_trial_id"])})
        preprocessing_records.append({"model_id": MODEL_ID, "fold_id": fold_id, "horizon_id": horizon_id, "policy": "median_impute", "feature_count": len(feature_columns), "fit_row_count": preprocessor.fit_row_count, "feature_artifact_id": feature_manifest["artifact_id"]})
    return pd.concat(records, ignore_index=True), fit_records, preprocessing_records


def _compute_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    working = predictions.copy()
    working["error"] = working["prediction"].astype("float64") - working["target"].astype("float64")
    working["squared_error"] = working["error"] ** 2
    working["absolute_error"] = working["error"].abs()
    rows: list[dict[str, Any]] = []
    for keys, group in working.groupby(["split_role", "fold_id", "horizon_id", "model_id"], sort=True):
        split_role, fold_id, horizon_id, model_id = keys
        target = group["target"].astype("float64")
        denominator = float(np.sum(target**2))
        sse = float(group["squared_error"].sum())
        rows.append({"split_role": split_role, "fold_id": fold_id, "horizon_id": horizon_id, "model_id": model_id, "row_count": int(len(group)), "target_mean": float(target.mean()), "prediction_mean": float(group["prediction"].mean()), "mse": float(group["squared_error"].mean()), "rmse": float(np.sqrt(group["squared_error"].mean())), "mae": float(group["absolute_error"].mean()), "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator)})
    return pd.DataFrame.from_records(rows)


def _compute_hurdle_deltas(metrics: pd.DataFrame) -> pd.DataFrame:
    hurdle = pd.read_parquet(STAGE20_ROOT / "metrics.parquet", columns=["split_role", "fold_id", "horizon_id", "model_id", "rmse", "mae"])
    hurdle = hurdle[hurdle["model_id"] == "market_xgboost_v1_fixed"].copy()
    candidate = metrics[["split_role", "fold_id", "horizon_id", "model_id", "rmse", "mae"]].copy()
    paired = candidate.merge(hurdle, on=["split_role", "fold_id", "horizon_id"], suffixes=("_candidate", "_hurdle"), validate="one_to_one")
    paired["rmse_delta_candidate_minus_hurdle"] = paired["rmse_candidate"] - paired["rmse_hurdle"]
    paired["mae_delta_candidate_minus_hurdle"] = paired["mae_candidate"] - paired["mae_hurdle"]
    paired["both_metrics_improve"] = (paired["rmse_delta_candidate_minus_hurdle"] < 0.0) & (paired["mae_delta_candidate_minus_hurdle"] < 0.0)
    return paired


def _render_report(manifest: dict[str, Any], hurdle_deltas: pd.DataFrame) -> str:
    lockbox = hurdle_deltas[hurdle_deltas["split_role"] == "lockbox"]
    validation = hurdle_deltas[hurdle_deltas["split_role"] == "validation"]
    return f"""# Stage 23 XGBoost Frozen Final Evaluation Report

Status: completed; final evaluation artifacts recorded without promotion claim

Updated: 2026-05-24

Run ID: `{manifest['run_id']}`

## Output

| Field | Value |
| --- | --- |
| Model ID | `{manifest['model_id']}` |
| Source Stage 22 trial | `{manifest['source_stage22_best_trial_id']}` |
| Prediction rows | {manifest['prediction_row_count']} |
| Metric rows | {manifest['metric_rows']} |
| Hurdle-delta rows | {manifest['hurdle_delta_rows']} |
| Prediction digest | `{manifest['prediction_digest_sha256']}` |

## Hurdle-Delta Diagnostics

| Split | Both-metric improvement rate vs fixed XGBoost hurdle |
| --- | ---: |
| Validation | {float(validation['both_metrics_improve'].mean()) if not validation.empty else 'nan'} |
| Lockbox | {float(lockbox['both_metrics_improve'].mean()) if not lockbox.empty else 'nan'} |

## Lockbox Policy

The candidate config was selected before lockbox evaluation. Lockbox metrics are computed once for frozen reporting only and were not used for search or selection.

## Artifacts

| Artifact | Path |
| --- | --- |
| Saved predictions | `{manifest['outputs']['saved_predictions']}` |
| Metrics | `{manifest['outputs']['metrics']}` |
| Hurdle deltas | `{manifest['outputs']['hurdle_deltas']}` |
| Manifest | `{manifest['outputs']['final_evaluation_manifest']}` |

## Non-Claims

These final-evaluation artifacts alone do not authorize a positive conclusion, promotion claim, Stage 6 reinterpretation, trading signal, or benchmark-comparability promotion. Stage 24 and Stage 39 remain required for overfit and claim review.
"""


def _stable_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    main()
