from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import optuna
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    HORIZON_WEIGHTS,
    compute_pairwise_deltas,
    sha256_file,
    stable_digest,
)
from event_state_forecasting.v1p0.modeling import fit_preprocessor  # noqa: E402


FEATURE_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
STAGE23_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_TOKEN = "20260528T030000Z"
GENERATED_AT_UTC = "2026-05-28T03:00:00Z"
SOURCE_ID = "6dff1bd"
CANDIDATE_MODEL_ID = "market_xgboost_v3_enhanced_optuna_800"
BASELINE_MODEL_ID = "market_xgboost_v2_frozen_final"
DEFAULT_TRIAL_COUNT = 800


def enhanced_xgboost_search_contract(trial_count: int = DEFAULT_TRIAL_COUNT) -> dict[str, Any]:
    return {
        "artifact_type": "v1p0_enhanced_xgboost_optuna_search_contract",
        "generated_at_utc": GENERATED_AT_UTC,
        "candidate_model_id": CANDIDATE_MODEL_ID,
        "baseline_model_id": BASELINE_MODEL_ID,
        "trial_count": int(trial_count),
        "minimum_required_trials": 800,
        "optuna": {
            "direction": "minimize",
            "sampler": "TPESampler",
            "sampler_seed": 2026052801,
            "n_startup_trials": 80,
            "multivariate": True,
        },
        "fixed_xgboost_params": {
            "objective": "reg:squarederror",
            "eval_metric": "rmse",
            "tree_method": "hist",
            "n_jobs": 1,
            "verbosity": 0,
        },
        "search_space": {
            "n_estimators": {"type": "int", "low": 200, "high": 2400, "step": 100},
            "max_depth": {"type": "int", "low": 2, "high": 10, "step": 1},
            "learning_rate": {"type": "float", "low": 0.002, "high": 0.20, "log": True},
            "subsample": {"type": "float", "low": 0.45, "high": 1.0, "log": False},
            "colsample_bytree": {"type": "float", "low": 0.45, "high": 1.0, "log": False},
            "colsample_bylevel": {"type": "float", "low": 0.45, "high": 1.0, "log": False},
            "colsample_bynode": {"type": "float", "low": 0.45, "high": 1.0, "log": False},
            "min_child_weight": {"type": "float", "low": 0.5, "high": 100.0, "log": True},
            "gamma": {"type": "float", "low": 0.0, "high": 20.0, "log": False},
            "reg_alpha": {"type": "float", "low": 1e-8, "high": 20.0, "log": True},
            "reg_lambda": {"type": "float", "low": 1e-3, "high": 200.0, "log": True},
            "max_delta_step": {"type": "int", "low": 0, "high": 5, "step": 1},
            "max_bin": {"type": "categorical", "choices": [128, 256, 512, 1024]},
            "grow_policy": {"type": "categorical", "choices": ["depthwise", "lossguide"]},
            "max_leaves": {"type": "categorical", "choices": [0, 16, 32, 64, 128, 256]},
        },
        "objective": {
            "name": "development_validation_weighted_delta_vs_current_xgboost_with_gap_and_complexity_penalty",
            "baseline_model_id": BASELINE_MODEL_ID,
            "horizon_weights": HORIZON_WEIGHTS,
            "metric_weights": {"rmse": 0.5, "mae": 0.5},
            "split_roles_for_optimization": ["train", "validation"],
            "lockbox_rows_used_for_optimization": 0,
        },
        "non_claims": [
            "development_only_enhanced_search",
            "not_lockbox_selection",
            "not_positive_benchmark_claim",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run enhanced 800+ trial v1p0 XGBoost Optuna search.")
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()
    if args.trial_count < 800:
        raise RuntimeError("enhanced XGBoost search requires at least 800 trials")

    contract = enhanced_xgboost_search_contract(args.trial_count)
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_v1p0__stage41__xgboost_enhanced_optuna__{GENERATED_TOKEN}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    search_space_path = output_root / "search_space_manifest.json"
    ledger_jsonl_path = output_root / "trial_ledger.ndjson"
    fold_metrics_jsonl_path = output_root / "trial_fold_metrics.ndjson"
    prediction_index_jsonl_path = output_root / "trial_prediction_index.ndjson"
    prediction_root = output_root / "trial_predictions"
    prediction_root.mkdir(exist_ok=True)
    storage_path = output_root / "optuna_study.sqlite3"

    _write_json(search_space_path, contract)
    feature_manifest = json.loads((FEATURE_ROOT / "feature_manifest.json").read_text(encoding="utf-8"))
    frame = _load_development_frame(feature_manifest)
    bundles = _prepare_fold_horizon_bundles(frame, list(feature_manifest["feature_columns"]))
    baseline_metrics = _load_baseline_metrics()
    completed_trial_ids = _completed_trial_ids(ledger_jsonl_path)

    sampler = optuna.samplers.TPESampler(
        seed=int(contract["optuna"]["sampler_seed"]),
        n_startup_trials=int(contract["optuna"]["n_startup_trials"]),
        multivariate=bool(contract["optuna"]["multivariate"]),
    )
    study = optuna.create_study(
        study_name="v1p0_xgboost_enhanced_800",
        direction="minimize",
        sampler=sampler,
        storage=f"sqlite:///{storage_path}",
        load_if_exists=True,
    )

    started = time.perf_counter()

    def objective(trial: optuna.Trial) -> float:
        trial_id = int(trial.number)
        if trial_id in completed_trial_ids:
            prior = _read_trial_record(ledger_jsonl_path, trial_id)
            if prior and prior.get("status") == "completed":
                return float(prior["objective_value"])
        params = _suggest_params(trial, contract)
        record = _execute_trial(trial_id, params, bundles, baseline_metrics, contract, prediction_root)
        _append_jsonl(ledger_jsonl_path, record["ledger"])
        completed_trial_ids.add(trial_id)
        for row in record["fold_metrics"]:
            _append_jsonl(fold_metrics_jsonl_path, row)
        if record["prediction_index"] is not None:
            _append_jsonl(prediction_index_jsonl_path, record["prediction_index"])
        print(json.dumps({"model_family": "xgboost", "trial_number": trial_id, "status": record["ledger"]["status"], "objective_value": record["ledger"]["objective_value"]}, sort_keys=True), flush=True)
        return float(record["ledger"]["objective_value"] if record["ledger"]["objective_value"] is not None else 1e9)

    remaining = max(0, int(args.trial_count) - len(completed_trial_ids))
    if remaining:
        study.optimize(objective, n_trials=remaining, show_progress_bar=False)

    ledger = _read_jsonl_frame(ledger_jsonl_path)
    fold_metrics = _read_jsonl_frame(fold_metrics_jsonl_path)
    prediction_index = _read_jsonl_frame(prediction_index_jsonl_path)
    completed = ledger[ledger["status"] == "completed"].copy() if not ledger.empty else pd.DataFrame()
    if completed.empty:
        raise RuntimeError("enhanced XGBoost search produced no completed trials")
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()

    ledger_parquet = output_root / "trial_ledger.parquet"
    fold_metrics_parquet = output_root / "trial_fold_metrics.parquet"
    prediction_index_parquet = output_root / "trial_prediction_index.parquet"
    overfit_frontier_path = output_root / "overfit_frontier.parquet"
    best_config_path = output_root / "best_development_candidate_config.json"
    manifest_path = output_root / "xgboost_enhanced_optuna_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage41_xgboost_enhanced_optuna_report.md"

    ledger.to_parquet(ledger_parquet, index=False)
    fold_metrics.to_parquet(fold_metrics_parquet, index=False)
    prediction_index.to_parquet(prediction_index_parquet, index=False)
    _build_overfit_frontier(ledger).to_parquet(overfit_frontier_path, index=False)
    best_config = _best_candidate_config(best, contract)
    _write_json(best_config_path, best_config)

    manifest = {
        "artifact_type": "v1p0_stage41_xgboost_enhanced_optuna_manifest",
        "artifact_id": f"stage41_xgboost_enhanced_optuna__{sha256_file(ledger_parquet)[:12]}__{GENERATED_TOKEN}",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed" if int((ledger["status"] == "completed").sum()) >= int(args.trial_count) else "partial",
        "candidate_model_id": CANDIDATE_MODEL_ID,
        "baseline_model_id": BASELINE_MODEL_ID,
        "trial_count_requested": int(args.trial_count),
        "trial_count_completed": int((ledger["status"] == "completed").sum()),
        "trial_count_failed": int((ledger["status"] == "failed").sum()),
        "best_development_trial": _json_safe(best),
        "lockbox_rows_used_for_optimization": 0,
        "outputs": {
            "search_space_manifest": _rel(search_space_path),
            "trial_ledger_ndjson": _rel(ledger_jsonl_path),
            "trial_ledger": _rel(ledger_parquet),
            "trial_fold_metrics_ndjson": _rel(fold_metrics_jsonl_path),
            "trial_fold_metrics": _rel(fold_metrics_parquet),
            "trial_prediction_index_ndjson": _rel(prediction_index_jsonl_path),
            "trial_prediction_index": _rel(prediction_index_parquet),
            "trial_prediction_root": _rel(prediction_root),
            "overfit_frontier": _rel(overfit_frontier_path),
            "best_development_candidate_config": _rel(best_config_path),
            "optuna_storage": _rel(storage_path),
            "manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": contract["non_claims"],
    }
    _write_json(manifest_path, manifest)
    _write_json(run_manifest_path, {"stage": 41, "stage_name": "xgboost_enhanced_optuna", "status": manifest["status"], "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_render_report(manifest), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "trial_count_completed": manifest["trial_count_completed"], "best_trial_number": int(best["trial_number"]), "best_objective_value": float(best["objective_value"]), "manifest": manifest["outputs"]["manifest"]}, sort_keys=True))


def _load_development_frame(feature_manifest: dict[str, Any]) -> pd.DataFrame:
    row_key = list(feature_manifest["row_key"])
    features = pd.read_parquet(PROJECT_ROOT / feature_manifest["outputs"]["market_lag_features"])
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*row_key, "forward_excess_return"])
    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet", columns=["fold_id", *row_key, "split_role", "lockbox_flag"])
    splits = splits[splits["split_role"].isin(["train", "validation"])].copy()
    if bool(splits["lockbox_flag"].any()):
        raise RuntimeError("enhanced XGBoost development frame unexpectedly contains lockbox rows")
    frame = splits.merge(features, on=row_key, how="inner", validate="many_to_one").merge(labels, on=row_key, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target"})
    frame["row_key"] = frame[row_key].astype(str).agg("|".join, axis=1)
    return frame


def _prepare_fold_horizon_bundles(frame: pd.DataFrame, feature_columns: list[str]) -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    meta_columns = ["row_key", "benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id", "fold_id", "split_role"]
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        validation = group[group["split_role"] == "validation"].copy()
        if train.empty or validation.empty:
            continue
        preprocessor = fit_preprocessor(train, feature_columns, "median_impute")
        bundles.append(
            {
                "fold_id": fold_id,
                "horizon_id": horizon_id,
                "x_train": preprocessor.transform(train),
                "y_train": train["target"].astype("float64").to_numpy(),
                "x_validation": preprocessor.transform(validation),
                "y_validation": validation["target"].astype("float64").to_numpy(),
                "validation_meta": validation[meta_columns].reset_index(drop=True),
            }
        )
    return bundles


def _load_baseline_metrics() -> pd.DataFrame:
    metrics = pd.read_parquet(STAGE23_ROOT / "metrics.parquet", columns=["split_role", "fold_id", "horizon_id", "model_id", "rmse", "mae"])
    return metrics[(metrics["model_id"] == BASELINE_MODEL_ID) & (metrics["split_role"].isin(["train", "validation"]))].copy()


def _suggest_params(trial: optuna.Trial, contract: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name, spec in contract["search_space"].items():
        if spec["type"] == "int":
            params[name] = trial.suggest_int(name, int(spec["low"]), int(spec["high"]), step=int(spec.get("step", 1)))
        elif spec["type"] == "float":
            params[name] = trial.suggest_float(name, float(spec["low"]), float(spec["high"]), log=bool(spec.get("log", False)))
        elif spec["type"] == "categorical":
            params[name] = trial.suggest_categorical(name, list(spec["choices"]))
        else:
            raise RuntimeError(f"unsupported search-space type for {name}: {spec['type']}")
    return params


def _execute_trial(trial_number: int, params: dict[str, Any], bundles: list[dict[str, Any]], baseline_metrics: pd.DataFrame, contract: dict[str, Any], prediction_root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    from xgboost import XGBRegressor

    fold_metrics: list[dict[str, Any]] = []
    validation_predictions: list[pd.DataFrame] = []
    training_seconds = 0.0
    inference_seconds = 0.0
    try:
        resolved_params = _resolved_xgboost_params(contract, params, seed=2026052801 + trial_number)
        for bundle in bundles:
            fit_started = time.perf_counter()
            estimator = XGBRegressor(**resolved_params)
            estimator.fit(bundle["x_train"], bundle["y_train"])
            fit_seconds = time.perf_counter() - fit_started
            predict_started = time.perf_counter()
            train_pred = estimator.predict(bundle["x_train"])
            validation_pred = estimator.predict(bundle["x_validation"])
            predict_seconds = time.perf_counter() - predict_started
            training_seconds += fit_seconds
            inference_seconds += predict_seconds
            fold_metrics.append(_metric_row(trial_number, bundle, "train", train_pred, bundle["y_train"], fit_seconds, predict_seconds))
            fold_metrics.append(_metric_row(trial_number, bundle, "validation", validation_pred, bundle["y_validation"], fit_seconds, predict_seconds))
            validation_frame = bundle["validation_meta"].copy()
            validation_frame.insert(0, "trial_number", int(trial_number))
            validation_frame["model_id"] = CANDIDATE_MODEL_ID
            validation_frame["prediction"] = validation_pred.astype("float64")
            validation_frame["target"] = bundle["y_validation"]
            validation_predictions.append(validation_frame)
        candidate_metrics = pd.DataFrame.from_records(fold_metrics)
        summary = _summarize_trial(trial_number, candidate_metrics, baseline_metrics, params, contract)
        predictions = pd.concat(validation_predictions, ignore_index=True)
        prediction_path = prediction_root / f"trial_{trial_number:04d}_validation_predictions.parquet"
        predictions.to_parquet(prediction_path, index=False)
        ledger = _ledger_record(trial_number, params, summary, training_seconds, inference_seconds, time.perf_counter() - started, _rel(prediction_path), "completed", "")
        return {"ledger": ledger, "fold_metrics": fold_metrics, "prediction_index": {"trial_number": int(trial_number), "prediction_path": _rel(prediction_path), "row_count": int(len(predictions))}}
    except Exception as exc:  # noqa: BLE001 - failed trials are evidence and must be logged.
        ledger = _ledger_record(trial_number, params, None, training_seconds, inference_seconds, time.perf_counter() - started, "", "failed", repr(exc))
        return {"ledger": ledger, "fold_metrics": fold_metrics, "prediction_index": None}


def _metric_row(trial_number: int, bundle: dict[str, Any], split_role: str, prediction: np.ndarray, target: np.ndarray, training_seconds: float, inference_seconds: float) -> dict[str, Any]:
    error = prediction.astype("float64") - target.astype("float64")
    denominator = float(np.sum(target.astype("float64") ** 2))
    sse = float(np.sum(error**2))
    return {
        "trial_number": int(trial_number),
        "split_role": split_role,
        "fold_id": bundle["fold_id"],
        "horizon_id": bundle["horizon_id"],
        "model_id": CANDIDATE_MODEL_ID,
        "row_count": int(len(target)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator),
        "training_time_seconds": round(training_seconds, 6),
        "inference_time_seconds": round(inference_seconds, 6),
    }


def _summarize_trial(trial_number: int, metrics: pd.DataFrame, baseline_metrics: pd.DataFrame, params: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    deltas = compute_pairwise_deltas(pd.concat([metrics, baseline_metrics], ignore_index=True, sort=False), BASELINE_MODEL_ID, [CANDIDATE_MODEL_ID])
    deltas["horizon_weight"] = deltas["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    deltas["weighted_delta"] = 0.5 * deltas["rmse_delta_candidate_minus_baseline"] * deltas["horizon_weight"] + 0.5 * deltas["mae_delta_candidate_minus_baseline"] * deltas["horizon_weight"]
    validation = deltas[deltas["split_role"] == "validation"].copy()
    train = deltas[deltas["split_role"] == "train"].copy()
    validation_weighted = _weighted_horizon_mean(validation)
    train_weighted = _weighted_horizon_mean(train)
    validation_rate = float(validation["both_metrics_improve"].mean()) if not validation.empty else 0.0
    train_rate = float(train["both_metrics_improve"].mean()) if not train.empty else 0.0
    gap_penalty = max(0.0, validation_weighted - train_weighted) * 0.10 if np.isfinite(train_weighted) else 0.0
    low_support_penalty = max(0.0, 0.50 - validation_rate) * 0.001
    complexity_penalty = _complexity_proxy(params, contract) * 0.0005
    objective_value = validation_weighted + gap_penalty + low_support_penalty + complexity_penalty
    return {
        "trial_number": int(trial_number),
        "objective_value": float(objective_value),
        "validation_weighted_delta_vs_xgboost_final": float(validation_weighted),
        "train_weighted_delta_vs_xgboost_final": float(train_weighted),
        "validation_both_metric_improvement_rate_vs_xgboost_final": validation_rate,
        "train_both_metric_improvement_rate_vs_xgboost_final": train_rate,
        "gap_penalty": float(gap_penalty),
        "low_support_penalty": float(low_support_penalty),
        "complexity_penalty": float(complexity_penalty),
        "lockbox_rows_used_for_optimization": 0,
    }


def _weighted_horizon_mean(deltas: pd.DataFrame) -> float:
    if deltas.empty:
        return float("inf")
    horizon_means = deltas.groupby("horizon_id", sort=True)["weighted_delta"].mean()
    return float(horizon_means.sum())


def _complexity_proxy(params: dict[str, Any], contract: dict[str, Any]) -> float:
    space = contract["search_space"]
    n_score = (float(params["n_estimators"]) - float(space["n_estimators"]["low"])) / (float(space["n_estimators"]["high"]) - float(space["n_estimators"]["low"]))
    depth_score = (float(params["max_depth"]) - float(space["max_depth"]["low"])) / (float(space["max_depth"]["high"]) - float(space["max_depth"]["low"]))
    leaves = float(params.get("max_leaves", 0))
    leaf_score = min(leaves / 256.0, 1.0)
    return float(0.45 * n_score + 0.35 * depth_score + 0.20 * leaf_score)


def _resolved_xgboost_params(contract: dict[str, Any], params: dict[str, Any], seed: int) -> dict[str, Any]:
    resolved = dict(contract["fixed_xgboost_params"])
    resolved.update(params)
    resolved["random_state"] = int(seed)
    return resolved


def _ledger_record(trial_number: int, params: dict[str, Any], summary: dict[str, Any] | None, training_seconds: float, inference_seconds: float, total_seconds: float, prediction_path: str, status: str, failure_reason: str) -> dict[str, Any]:
    return {
        "trial_number": int(trial_number),
        "status": status,
        "objective_value": None if summary is None else float(summary["objective_value"]),
        "validation_weighted_delta_vs_xgboost_final": None if summary is None else float(summary["validation_weighted_delta_vs_xgboost_final"]),
        "train_weighted_delta_vs_xgboost_final": None if summary is None else float(summary["train_weighted_delta_vs_xgboost_final"]),
        "validation_both_metric_improvement_rate_vs_xgboost_final": None if summary is None else float(summary["validation_both_metric_improvement_rate_vs_xgboost_final"]),
        "train_both_metric_improvement_rate_vs_xgboost_final": None if summary is None else float(summary["train_both_metric_improvement_rate_vs_xgboost_final"]),
        "gap_penalty": 0.0 if summary is None else float(summary["gap_penalty"]),
        "low_support_penalty": 0.0 if summary is None else float(summary["low_support_penalty"]),
        "complexity_penalty": 0.0 if summary is None else float(summary["complexity_penalty"]),
        "lockbox_rows_used_for_optimization": 0,
        "training_time_seconds": round(training_seconds, 6),
        "inference_time_seconds": round(inference_seconds, 6),
        "total_time_seconds": round(total_seconds, 6),
        "prediction_path": prediction_path,
        "params_json": json.dumps(params, sort_keys=True),
        "failure_reason": failure_reason,
    }


def _build_overfit_frontier(ledger: pd.DataFrame) -> pd.DataFrame:
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        return pd.DataFrame()
    completed["generalization_gap"] = completed["validation_weighted_delta_vs_xgboost_final"].astype("float64") - completed["train_weighted_delta_vs_xgboost_final"].astype("float64")
    completed["overfit_frontier_flag"] = completed["generalization_gap"] > completed["generalization_gap"].median()
    return completed[["trial_number", "objective_value", "validation_weighted_delta_vs_xgboost_final", "train_weighted_delta_vs_xgboost_final", "generalization_gap", "complexity_penalty", "overfit_frontier_flag", "params_json"]]


def _best_candidate_config(best: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    params = json.loads(str(best["params_json"]))
    return {
        "artifact_type": "v1p0_stage41_xgboost_enhanced_best_development_candidate_config",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": CANDIDATE_MODEL_ID,
        "baseline_model_id": BASELINE_MODEL_ID,
        "selected_trial_number": int(best["trial_number"]),
        "selection_basis": "development_validation_guarded_objective_only",
        "objective_value": float(best["objective_value"]),
        "params": params,
        "resolved_xgboost_params": _resolved_xgboost_params(contract, params, seed=2026052801 + int(best["trial_number"])),
        "lockbox_used_for_selection": False,
        "benchmark_claim": False,
        "positive_claim_approved": False,
    }


def _render_report(manifest: dict[str, Any]) -> str:
    best = manifest["best_development_trial"]
    return f"""# Stage 41 XGBoost Enhanced Optuna Search

Status: {manifest['status']}; enhanced development-only search evidence

Trials requested: {manifest['trial_count_requested']}

Trials completed: {manifest['trial_count_completed']}

Best trial: `{best.get('trial_number')}`

Best objective value: {best.get('objective_value')}

Validation weighted delta vs current XGBoost final: {best.get('validation_weighted_delta_vs_xgboost_final')}

Validation both-metric improvement rate vs current XGBoost final: {best.get('validation_both_metric_improvement_rate_vs_xgboost_final')}

Lockbox rows used for optimization: {manifest['lockbox_rows_used_for_optimization']}

Non-claims: this enhanced Optuna run is not a positive benchmark claim, not lockbox selection, not Stage 6 reinterpretation, and not a trading signal.
"""


def _completed_trial_ids(ledger_path: Path) -> set[int]:
    if not ledger_path.exists():
        return set()
    return {int(row["trial_number"]) for row in _iter_jsonl(ledger_path) if row.get("status") in {"completed", "failed"}}


def _read_trial_record(ledger_path: Path, trial_number: int) -> dict[str, Any] | None:
    if not ledger_path.exists():
        return None
    for row in _iter_jsonl(ledger_path):
        if int(row.get("trial_number", -1)) == int(trial_number):
            return row
    return None


def _read_jsonl_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.DataFrame.from_records(list(_iter_jsonl(path)))


def _iter_jsonl(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(payload), sort_keys=True) + "\n")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if pd.isna(value) if not isinstance(value, (dict, list, tuple)) else False:
        return None
    return value


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    main()
