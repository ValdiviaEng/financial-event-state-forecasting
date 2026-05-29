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
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from sklearn.impute import SimpleImputer


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


UPDATED_STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1"
UPDATED_STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
PREVIOUS_XGBOOST_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"

ROW_KEY = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
GENERATED_TOKEN = "20260528T100000Z"
GENERATED_AT_UTC = "2026-05-28T10:00:00Z"
SOURCE_ID = "6dff1bd"
DEFAULT_TRIAL_COUNT = 800
MODEL_ID = "updated_av_xgboost_event_market_optuna_v1"
PREVIOUS_MODEL_ID = "market_xgboost_v2_frozen_final"
DIVERSITY_CHECK_HORIZONS = ("1d", "5d", "10d")
MIN_PREDICTION_RANGE = 1e-8


def updated_xgboost_search_contract(trial_count: int = DEFAULT_TRIAL_COUNT) -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_xgboost_optuna_search_contract",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": MODEL_ID,
        "previous_model_id": PREVIOUS_MODEL_ID,
        "trial_count": int(trial_count),
        "minimum_required_trials": 800,
        "feature_scope": "updated_alpha_vantage_market_plus_event_state",
        "selection_split_roles": ["train", "validation"],
        "final_evaluation_split_roles": ["train", "validation", "lockbox"],
        "lockbox_rows_used_for_tuning": 0,
        "optuna": {
            "direction": "minimize",
            "sampler": "TPESampler",
            "sampler_seed": 2026052803,
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
            "n_estimators": {"type": "int", "low": 100, "high": 1600, "step": 50},
            "max_depth": {"type": "int", "low": 2, "high": 8, "step": 1},
            "learning_rate": {"type": "float", "low": 0.003, "high": 0.20, "log": True},
            "subsample": {"type": "float", "low": 0.50, "high": 1.0, "log": False},
            "colsample_bytree": {"type": "float", "low": 0.50, "high": 1.0, "log": False},
            "colsample_bylevel": {"type": "float", "low": 0.50, "high": 1.0, "log": False},
            "min_child_weight": {"type": "float", "low": 0.5, "high": 80.0, "log": True},
            "gamma": {"type": "float", "low": 1e-12, "high": 1e-3, "log": True},
            "reg_alpha": {"type": "float", "low": 1e-12, "high": 1e-3, "log": True},
            "reg_lambda": {"type": "float", "low": 1e-3, "high": 200.0, "log": True},
            "max_delta_step": {"type": "int", "low": 0, "high": 5, "step": 1},
            "max_bin": {"type": "categorical", "choices": [128, 256, 512]},
            "grow_policy": {"type": "categorical", "choices": ["depthwise", "lossguide"]},
            "max_leaves": {"type": "categorical", "choices": [0, 16, 32, 64, 128]},
        },
        "objective": {
            "name": "validation_weighted_delta_vs_previous_xgboost_with_overfit_penalty",
            "baseline_model_id": PREVIOUS_MODEL_ID,
            "horizon_weights": HORIZON_WEIGHTS,
            "metric_weights": {"rmse": 0.5, "mae": 0.5},
            "lower_is_better": True,
        },
        "non_claims": [
            "development_tuning_uses_train_validation_only",
            "lockbox_not_used_for_tuning_or_selection",
            "comparison_is_post_selection_evidence",
            "not_positive_benchmark_claim",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
        "prediction_diversity_gate": {
            "split_role": "validation",
            "horizons": list(DIVERSITY_CHECK_HORIZONS),
            "minimum_prediction_range_per_fold": MIN_PREDICTION_RANGE,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune XGBoost on the updated Alpha Vantage dataset and compare against the previous frozen XGBoost model.")
    parser.add_argument("--stage3-root", type=Path, default=UPDATED_STAGE3_ROOT)
    parser.add_argument("--stage4-root", type=Path, default=UPDATED_STAGE4_ROOT)
    parser.add_argument("--previous-xgboost-root", type=Path, default=PREVIOUS_XGBOOST_ROOT)
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()
    if args.trial_count < 800:
        raise RuntimeError("updated-dataset XGBoost tuning requires at least 800 trials")

    stage3_root = args.stage3_root.resolve()
    stage4_root = args.stage4_root.resolve()
    previous_root = args.previous_xgboost_root.resolve()
    contract = updated_xgboost_search_contract(args.trial_count)
    contract["updated_stage3_root"] = _rel(stage3_root)
    contract["updated_stage4_root"] = _rel(stage4_root)
    contract["previous_xgboost_root"] = _rel(previous_root)
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__{GENERATED_TOKEN}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root.resolve() if args.output_root else RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    prediction_root = output_root / "trial_predictions"
    prediction_root.mkdir(exist_ok=True)

    search_space_path = output_root / "search_space_manifest.json"
    ledger_jsonl_path = output_root / "trial_ledger.ndjson"
    fold_metrics_jsonl_path = output_root / "trial_fold_metrics.ndjson"
    prediction_index_jsonl_path = output_root / "trial_prediction_index.ndjson"
    storage_path = output_root / "optuna_study.sqlite3"
    _write_json(search_space_path, contract)

    started = time.perf_counter()
    frame, feature_columns, feature_summary = _load_updated_frame(stage3_root, stage4_root)
    previous_metrics = _load_previous_metrics(previous_root)
    bundles = _prepare_bundles(frame, feature_columns)
    completed_trial_ids = _completed_trial_ids(ledger_jsonl_path)

    sampler = optuna.samplers.TPESampler(
        seed=int(contract["optuna"]["sampler_seed"]),
        n_startup_trials=int(contract["optuna"]["n_startup_trials"]),
        multivariate=bool(contract["optuna"].get("multivariate", False)),
    )
    study = optuna.create_study(
        study_name="updated_av_xgboost_event_market_800",
        direction="minimize",
        sampler=sampler,
        storage=f"sqlite:///{storage_path}",
        load_if_exists=True,
    )

    def objective(trial: optuna.Trial) -> float:
        trial_number = int(trial.number)
        if trial_number in completed_trial_ids:
            prior = _read_trial_record(ledger_jsonl_path, trial_number)
            if prior and prior.get("status") == "completed":
                return float(prior["objective_value"])
        params = _suggest_params(trial, contract)
        record = _execute_trial(trial_number, params, bundles, previous_metrics, contract, save_predictions=False, prediction_root=prediction_root)
        _append_jsonl(ledger_jsonl_path, record["ledger"])
        completed_trial_ids.add(trial_number)
        for row in record["fold_metrics"]:
            _append_jsonl(fold_metrics_jsonl_path, row)
        if record["prediction_index"] is not None:
            _append_jsonl(prediction_index_jsonl_path, record["prediction_index"])
        print(json.dumps({"trial_number": trial_number, "status": record["ledger"]["status"], "objective_value": record["ledger"].get("objective_value")}, sort_keys=True), flush=True)
        return float(record["ledger"].get("objective_value", 1e9) or 1e9)

    remaining = max(0, int(args.trial_count) - len(completed_trial_ids))
    if remaining:
        study.optimize(objective, n_trials=remaining, show_progress_bar=False)

    ledger = _read_jsonl_frame(ledger_jsonl_path)
    if ledger.empty or not (ledger["status"] == "completed").any():
        raise RuntimeError("updated-dataset XGBoost tuning produced no completed trials")
    completed = ledger[ledger["status"] == "completed"].copy()
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()
    best_params = json.loads(str(best["params_json"]))
    best_eval = _execute_trial(int(best["trial_number"]), best_params, bundles, previous_metrics, contract, save_predictions=True, prediction_root=output_root)
    best_predictions = best_eval["predictions"]
    best_metrics = pd.DataFrame.from_records(best_eval["fold_metrics"])
    comparison_deltas = compute_pairwise_deltas(pd.concat([best_metrics, previous_metrics], ignore_index=True, sort=False), PREVIOUS_MODEL_ID, [MODEL_ID])
    comparison_summary = _comparison_summary(comparison_deltas, best_metrics, previous_metrics, best, feature_summary, contract)

    fold_metrics = _read_jsonl_frame(fold_metrics_jsonl_path)
    prediction_index = _read_jsonl_frame(prediction_index_jsonl_path)
    overfit_frontier = _build_overfit_frontier(ledger)

    ledger_parquet = output_root / "trial_ledger.parquet"
    fold_metrics_parquet = output_root / "trial_fold_metrics.parquet"
    prediction_index_parquet = output_root / "trial_prediction_index.parquet"
    overfit_frontier_path = output_root / "overfit_frontier.parquet"
    best_config_path = output_root / "best_development_candidate_config.json"
    best_predictions_path = output_root / "best_model_predictions.parquet"
    best_metrics_path = output_root / "best_model_metrics.parquet"
    comparison_deltas_path = output_root / "comparison_vs_previous_xgboost.parquet"
    comparison_json_path = output_root / "comparison_vs_previous_xgboost.json"
    comparison_md_path = output_root / "comparison_vs_previous_xgboost.md"
    manifest_path = output_root / "updated_dataset_xgboost_tuning_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage43_updated_dataset_xgboost_tuning_report.md"

    ledger.to_parquet(ledger_parquet, index=False)
    fold_metrics.to_parquet(fold_metrics_parquet, index=False)
    prediction_index.to_parquet(prediction_index_parquet, index=False)
    overfit_frontier.to_parquet(overfit_frontier_path, index=False)
    best_predictions.to_parquet(best_predictions_path, index=False)
    best_metrics.to_parquet(best_metrics_path, index=False)
    comparison_deltas.to_parquet(comparison_deltas_path, index=False)
    best_config = _best_candidate_config(best, best_params, contract, feature_columns)
    _write_json(best_config_path, best_config)
    _write_json(comparison_json_path, comparison_summary)
    comparison_md_path.write_text(_render_comparison_markdown(comparison_summary), encoding="utf-8")

    manifest = {
        "artifact_type": "updated_dataset_xgboost_tuning_manifest",
        "artifact_id": f"updated_dataset_xgboost_tuning__{sha256_file(ledger_parquet)[:12]}__{GENERATED_TOKEN}",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed" if int((ledger["status"] == "completed").sum()) >= int(args.trial_count) else "partial",
        "model_id": MODEL_ID,
        "previous_model_id": PREVIOUS_MODEL_ID,
        "updated_stage3_root": _rel(stage3_root),
        "updated_stage4_root": _rel(stage4_root),
        "trial_count_requested": int(args.trial_count),
        "trial_count_completed": int((ledger["status"] == "completed").sum()),
        "trial_count_failed": int((ledger["status"] == "failed").sum()),
        "feature_summary": feature_summary,
        "best_development_trial": _json_safe(best),
        "comparison_summary": comparison_summary,
        "lockbox_rows_used_for_tuning": 0,
        "outputs": {
            "search_space_manifest": _rel(search_space_path),
            "trial_ledger_ndjson": _rel(ledger_jsonl_path),
            "trial_ledger": _rel(ledger_parquet),
            "trial_fold_metrics_ndjson": _rel(fold_metrics_jsonl_path),
            "trial_fold_metrics": _rel(fold_metrics_parquet),
            "trial_prediction_index_ndjson": _rel(prediction_index_jsonl_path),
            "trial_prediction_index": _rel(prediction_index_parquet),
            "overfit_frontier": _rel(overfit_frontier_path),
            "best_development_candidate_config": _rel(best_config_path),
            "best_model_predictions": _rel(best_predictions_path),
            "best_model_metrics": _rel(best_metrics_path),
            "comparison_deltas": _rel(comparison_deltas_path),
            "comparison_json": _rel(comparison_json_path),
            "comparison_markdown": _rel(comparison_md_path),
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
    _write_json(run_manifest_path, {"stage": 43, "stage_name": "updated_dataset_xgboost_tuning", "status": manifest["status"], "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_render_report(manifest), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "trial_count_completed": manifest["trial_count_completed"], "best_trial_number": int(best["trial_number"]), "comparison_json": manifest["outputs"]["comparison_json"], "manifest": manifest["outputs"]["manifest"]}, sort_keys=True))


def _load_updated_frame(stage3_root: Path, stage4_root: Path) -> tuple[pd.DataFrame, list[str], dict[str, Any]]:
    market = pd.read_parquet(stage3_root / "market_features.parquet")
    event = pd.read_parquet(stage3_root / "event_state_features.parquet")
    labels = pd.read_parquet(stage3_root / "labels.parquet", columns=[*ROW_KEY, "forward_excess_return"])
    splits = pd.read_parquet(stage4_root / "split_assignments.parquet", columns=["fold_id", *ROW_KEY, "split_role", "lockbox_flag"])
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
    market_columns = _numeric_feature_columns(market, ROW_KEY)
    event_columns = _numeric_feature_columns(event, ROW_KEY)
    event = event[[*ROW_KEY, *event_columns]].copy()
    market = market[[*ROW_KEY, *market_columns]].copy()
    frame = splits.merge(market, on=ROW_KEY, how="inner", validate="many_to_one").merge(event, on=ROW_KEY, how="inner", validate="many_to_one").merge(labels, on=ROW_KEY, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target"})
    frame["row_key"] = frame[ROW_KEY].astype(str).agg("|".join, axis=1)
    feature_columns = market_columns + event_columns
    summary = {
        "feature_count": len(feature_columns),
        "market_feature_count": len(market_columns),
        "event_state_feature_count": len(event_columns),
        "row_count": int(len(frame)),
        "split_role_counts": {str(k): int(v) for k, v in frame["split_role"].value_counts().items()},
        "feature_columns": feature_columns,
    }
    return frame, feature_columns, summary


def _numeric_feature_columns(frame: pd.DataFrame, key_columns: list[str]) -> list[str]:
    excluded = set(key_columns) | {"dataset_version", "feature_availability_timestamp", "prediction_timestamp"}
    columns = []
    for column in frame.columns:
        if column in excluded:
            continue
        if is_numeric_dtype(frame[column]) or is_bool_dtype(frame[column]):
            columns.append(column)
    return columns


def _load_previous_metrics(previous_root: Path) -> pd.DataFrame:
    metrics = pd.read_parquet(previous_root / "metrics.parquet")
    return metrics[metrics["model_id"] == PREVIOUS_MODEL_ID][["split_role", "fold_id", "horizon_id", "model_id", "row_count", "rmse", "mae", "r2_oos_zero_baseline"]].copy()


def _prepare_bundles(frame: pd.DataFrame, feature_columns: list[str]) -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    meta_columns = ["row_key", *ROW_KEY, "fold_id", "split_role", "target"]
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        validation = group[group["split_role"] == "validation"].copy()
        lockbox = group[group["split_role"] == "lockbox"].copy()
        if train.empty or validation.empty:
            continue
        imputer = SimpleImputer(strategy="median")
        x_train = imputer.fit_transform(train[feature_columns].astype("float64"))
        bundles.append(
            {
                "fold_id": fold_id,
                "horizon_id": horizon_id,
                "x_train": x_train,
                "y_train": train["target"].astype("float64").to_numpy(),
                "x_validation": imputer.transform(validation[feature_columns].astype("float64")),
                "y_validation": validation["target"].astype("float64").to_numpy(),
                "validation_meta": validation[meta_columns].reset_index(drop=True),
                "x_lockbox": imputer.transform(lockbox[feature_columns].astype("float64")) if not lockbox.empty else np.empty((0, len(feature_columns))),
                "y_lockbox": lockbox["target"].astype("float64").to_numpy(),
                "lockbox_meta": lockbox[meta_columns].reset_index(drop=True),
            }
        )
    return bundles


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


def _execute_trial(trial_number: int, params: dict[str, Any], bundles: list[dict[str, Any]], previous_metrics: pd.DataFrame, contract: dict[str, Any], *, save_predictions: bool, prediction_root: Path) -> dict[str, Any]:
    from xgboost import XGBRegressor

    started = time.perf_counter()
    fold_metrics: list[dict[str, Any]] = []
    predictions: list[pd.DataFrame] = []
    diversity_violations: list[dict[str, Any]] = []
    training_seconds = 0.0
    inference_seconds = 0.0
    try:
        resolved_params = _resolved_params(contract, params, seed=2026052803 + int(trial_number))
        for bundle in bundles:
            fit_started = time.perf_counter()
            estimator = XGBRegressor(**resolved_params)
            estimator.fit(bundle["x_train"], bundle["y_train"])
            fit_seconds = time.perf_counter() - fit_started
            predict_started = time.perf_counter()
            train_pred = estimator.predict(bundle["x_train"])
            validation_pred = estimator.predict(bundle["x_validation"])
            lockbox_pred = estimator.predict(bundle["x_lockbox"]) if save_predictions and len(bundle["x_lockbox"]) else np.array([], dtype="float64")
            if bundle["horizon_id"] in DIVERSITY_CHECK_HORIZONS:
                prediction_range = float(np.max(validation_pred) - np.min(validation_pred)) if len(validation_pred) else 0.0
                if prediction_range < MIN_PREDICTION_RANGE:
                    diversity_violations.append({"fold_id": bundle["fold_id"], "horizon_id": bundle["horizon_id"], "prediction_range": prediction_range})
            predict_seconds = time.perf_counter() - predict_started
            training_seconds += fit_seconds
            inference_seconds += predict_seconds
            fold_metrics.append(_metric_row(trial_number, bundle, "train", train_pred, bundle["y_train"], fit_seconds, predict_seconds))
            fold_metrics.append(_metric_row(trial_number, bundle, "validation", validation_pred, bundle["y_validation"], fit_seconds, predict_seconds))
            if len(lockbox_pred):
                fold_metrics.append(_metric_row(trial_number, bundle, "lockbox", lockbox_pred, bundle["y_lockbox"], fit_seconds, predict_seconds))
            if save_predictions:
                predictions.append(_prediction_frame(bundle["validation_meta"], trial_number, validation_pred))
                if len(lockbox_pred):
                    predictions.append(_prediction_frame(bundle["lockbox_meta"], trial_number, lockbox_pred))
        candidate_metrics = pd.DataFrame.from_records(fold_metrics)
        summary = _summarize_trial(candidate_metrics, previous_metrics, params, contract, diversity_violations)
        prediction_index = None
        if save_predictions:
            all_predictions = pd.concat(predictions, ignore_index=True)
            prediction_path = prediction_root / "best_model_predictions.parquet"
            all_predictions.to_parquet(prediction_path, index=False)
            prediction_index = {"trial_number": int(trial_number), "prediction_path": _rel(prediction_path), "row_count": int(len(all_predictions))}
        else:
            all_predictions = pd.DataFrame()
        ledger = _ledger_record(trial_number, params, summary, training_seconds, inference_seconds, time.perf_counter() - started, "completed", "")
        return {"ledger": ledger, "fold_metrics": fold_metrics, "prediction_index": prediction_index, "predictions": all_predictions}
    except Exception as exc:  # noqa: BLE001 - failed trials must be captured.
        ledger = _ledger_record(trial_number, params, None, training_seconds, inference_seconds, time.perf_counter() - started, "failed", repr(exc))
        return {"ledger": ledger, "fold_metrics": fold_metrics, "prediction_index": None, "predictions": pd.DataFrame()}


def _resolved_params(contract: dict[str, Any], params: dict[str, Any], seed: int) -> dict[str, Any]:
    resolved = dict(contract["fixed_xgboost_params"])
    resolved.update(params)
    resolved["random_state"] = int(seed)
    return resolved


def _metric_row(trial_number: int, bundle: dict[str, Any], split_role: str, prediction: np.ndarray, target: np.ndarray, training_seconds: float, inference_seconds: float) -> dict[str, Any]:
    error = prediction.astype("float64") - target.astype("float64")
    denominator = float(np.sum(target.astype("float64") ** 2))
    sse = float(np.sum(error**2))
    return {
        "trial_number": int(trial_number),
        "split_role": split_role,
        "fold_id": bundle["fold_id"],
        "horizon_id": bundle["horizon_id"],
        "model_id": MODEL_ID,
        "row_count": int(len(target)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator),
        "training_time_seconds": round(training_seconds, 6),
        "inference_time_seconds": round(inference_seconds, 6),
    }


def _prediction_frame(meta: pd.DataFrame, trial_number: int, prediction: np.ndarray) -> pd.DataFrame:
    output = meta.copy()
    output["trial_number"] = int(trial_number)
    output["model_id"] = MODEL_ID
    output["prediction"] = prediction.astype("float64")
    return output


def _summarize_trial(candidate_metrics: pd.DataFrame, previous_metrics: pd.DataFrame, params: dict[str, Any], contract: dict[str, Any], diversity_violations: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    combined = pd.concat([candidate_metrics, previous_metrics], ignore_index=True, sort=False)
    deltas = compute_pairwise_deltas(combined, PREVIOUS_MODEL_ID, [MODEL_ID])
    validation = deltas[deltas["split_role"] == "validation"].copy()
    train = deltas[deltas["split_role"] == "train"].copy()
    validation_weighted = _weighted_delta(validation)
    train_weighted = _weighted_delta(train)
    validation_rate = float(validation["both_metrics_improve"].mean()) if not validation.empty else 0.0
    train_rate = float(train["both_metrics_improve"].mean()) if not train.empty else 0.0
    gap_penalty = max(0.0, validation_weighted - train_weighted) * 0.10 if np.isfinite(train_weighted) else 0.0
    low_support_penalty = max(0.0, 0.50 - validation_rate) * 0.001
    complexity_penalty = _complexity_proxy(params, contract) * 0.0005
    diversity_penalty = 1.0 if diversity_violations else 0.0
    objective_value = validation_weighted + gap_penalty + low_support_penalty + complexity_penalty + diversity_penalty
    return {
        "objective_value": float(objective_value),
        "validation_weighted_delta_vs_previous": float(validation_weighted),
        "train_weighted_delta_vs_previous": float(train_weighted),
        "validation_both_metric_improvement_rate_vs_previous": validation_rate,
        "train_both_metric_improvement_rate_vs_previous": train_rate,
        "gap_penalty": float(gap_penalty),
        "low_support_penalty": float(low_support_penalty),
        "complexity_penalty": float(complexity_penalty),
        "prediction_diversity_penalty": float(diversity_penalty),
        "prediction_diversity_violation_count": 0 if diversity_violations is None else int(len(diversity_violations)),
        "lockbox_rows_used_for_tuning": 0,
    }


def _weighted_delta(deltas: pd.DataFrame) -> float:
    if deltas.empty:
        return float("inf")
    working = deltas.copy()
    working["horizon_weight"] = working["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    working["weighted_delta"] = 0.5 * working["rmse_delta_candidate_minus_baseline"] * working["horizon_weight"] + 0.5 * working["mae_delta_candidate_minus_baseline"] * working["horizon_weight"]
    return float(working.groupby("horizon_id", sort=True)["weighted_delta"].mean().sum())


def _complexity_proxy(params: dict[str, Any], contract: dict[str, Any]) -> float:
    space = contract["search_space"]
    n_score = (float(params["n_estimators"]) - float(space["n_estimators"]["low"])) / (float(space["n_estimators"]["high"]) - float(space["n_estimators"]["low"]))
    depth_score = (float(params["max_depth"]) - float(space["max_depth"]["low"])) / (float(space["max_depth"]["high"]) - float(space["max_depth"]["low"]))
    leaf_score = min(float(params.get("max_leaves", 0)) / 128.0, 1.0)
    return float(0.45 * n_score + 0.35 * depth_score + 0.20 * leaf_score)


def _ledger_record(trial_number: int, params: dict[str, Any], summary: dict[str, Any] | None, training_seconds: float, inference_seconds: float, total_seconds: float, status: str, failure_reason: str) -> dict[str, Any]:
    return {
        "trial_number": int(trial_number),
        "status": status,
        "objective_value": None if summary is None else float(summary["objective_value"]),
        "validation_weighted_delta_vs_previous": None if summary is None else float(summary["validation_weighted_delta_vs_previous"]),
        "train_weighted_delta_vs_previous": None if summary is None else float(summary["train_weighted_delta_vs_previous"]),
        "validation_both_metric_improvement_rate_vs_previous": None if summary is None else float(summary["validation_both_metric_improvement_rate_vs_previous"]),
        "train_both_metric_improvement_rate_vs_previous": None if summary is None else float(summary["train_both_metric_improvement_rate_vs_previous"]),
        "gap_penalty": 0.0 if summary is None else float(summary["gap_penalty"]),
        "low_support_penalty": 0.0 if summary is None else float(summary["low_support_penalty"]),
        "complexity_penalty": 0.0 if summary is None else float(summary["complexity_penalty"]),
        "prediction_diversity_penalty": 0.0 if summary is None else float(summary.get("prediction_diversity_penalty", 0.0)),
        "prediction_diversity_violation_count": 0 if summary is None else int(summary.get("prediction_diversity_violation_count", 0)),
        "lockbox_rows_used_for_tuning": 0,
        "training_time_seconds": round(training_seconds, 6),
        "inference_time_seconds": round(inference_seconds, 6),
        "total_time_seconds": round(total_seconds, 6),
        "params_json": json.dumps(params, sort_keys=True),
        "failure_reason": failure_reason,
    }


def _build_overfit_frontier(ledger: pd.DataFrame) -> pd.DataFrame:
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        return pd.DataFrame()
    completed["generalization_gap"] = completed["validation_weighted_delta_vs_previous"].astype("float64") - completed["train_weighted_delta_vs_previous"].astype("float64")
    completed["overfit_frontier_flag"] = completed["generalization_gap"] > completed["generalization_gap"].median()
    columns = ["trial_number", "objective_value", "validation_weighted_delta_vs_previous", "train_weighted_delta_vs_previous", "generalization_gap", "complexity_penalty", "overfit_frontier_flag", "params_json"]
    if "prediction_diversity_violation_count" in completed.columns:
        columns.insert(-1, "prediction_diversity_violation_count")
    return completed[columns]


def _best_candidate_config(best: dict[str, Any], params: dict[str, Any], contract: dict[str, Any], feature_columns: list[str]) -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_xgboost_best_development_candidate_config",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": MODEL_ID,
        "previous_model_id": PREVIOUS_MODEL_ID,
        "selected_trial_number": int(best["trial_number"]),
        "selection_basis": "updated_dataset_development_validation_only",
        "objective_value": float(best["objective_value"]),
        "params": params,
        "resolved_xgboost_params": _resolved_params(contract, params, seed=2026052803 + int(best["trial_number"])),
        "feature_columns": feature_columns,
        "lockbox_used_for_selection": False,
        "benchmark_claim": False,
        "positive_claim_approved": False,
    }


def _comparison_summary(deltas: pd.DataFrame, best_metrics: pd.DataFrame, previous_metrics: pd.DataFrame, best: dict[str, Any], feature_summary: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    split_summaries: dict[str, Any] = {}
    for split_role in ["validation", "lockbox"]:
        split = deltas[deltas["split_role"] == split_role].copy()
        split_summaries[split_role] = {
            "weighted_delta_candidate_minus_previous": _weighted_delta(split),
            "both_metric_improvement_rate": float(split["both_metrics_improve"].mean()) if not split.empty else 0.0,
            "comparison_rows": int(len(split)),
            "rmse_delta_mean": float(split["rmse_delta_candidate_minus_baseline"].mean()) if not split.empty else None,
            "mae_delta_mean": float(split["mae_delta_candidate_minus_baseline"].mean()) if not split.empty else None,
        }
    metric_summary = _metric_summary(best_metrics, previous_metrics)
    result_class = "lockbox_improved_nonclaim" if split_summaries["lockbox"]["weighted_delta_candidate_minus_previous"] < 0 and split_summaries["lockbox"]["both_metric_improvement_rate"] >= 0.5 else "not_lockbox_improved_or_mixed"
    return {
        "artifact_type": "updated_dataset_xgboost_vs_previous_comparison",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": MODEL_ID,
        "previous_model_id": PREVIOUS_MODEL_ID,
        "selected_trial_number": int(best["trial_number"]),
        "selection_split": "validation",
        "lockbox_used_for_tuning": False,
        "feature_summary": feature_summary,
        "split_summaries": split_summaries,
        "metric_summary": metric_summary,
        "result_class": result_class,
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": contract["non_claims"],
    }


def _metric_summary(best_metrics: pd.DataFrame, previous_metrics: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for split_role in ["validation", "lockbox"]:
        for model_id, source in [(MODEL_ID, best_metrics), (PREVIOUS_MODEL_ID, previous_metrics)]:
            split = source[(source["split_role"] == split_role) & (source["model_id"] == model_id)]
            rows.append({
                "split_role": split_role,
                "model_id": model_id,
                "metric_rows": int(len(split)),
                "rmse_mean": float(split["rmse"].mean()) if not split.empty else None,
                "mae_mean": float(split["mae"].mean()) if not split.empty else None,
                "r2_oos_zero_baseline_mean": float(split["r2_oos_zero_baseline"].mean()) if not split.empty else None,
            })
    return rows


def _render_comparison_markdown(summary: dict[str, Any]) -> str:
    validation = summary["split_summaries"]["validation"]
    lockbox = summary["split_summaries"]["lockbox"]
    return f"""# Updated Dataset XGBoost vs Previous XGBoost

Result class: `{summary['result_class']}`

Selected trial: `{summary['selected_trial_number']}`

Feature count: {summary['feature_summary']['feature_count']} ({summary['feature_summary']['market_feature_count']} market, {summary['feature_summary']['event_state_feature_count']} event-state)

## Validation

Weighted delta candidate minus previous: {validation['weighted_delta_candidate_minus_previous']}

Both-metric improvement rate: {validation['both_metric_improvement_rate']}

## Lockbox

Weighted delta candidate minus previous: {lockbox['weighted_delta_candidate_minus_previous']}

Both-metric improvement rate: {lockbox['both_metric_improvement_rate']}

## Non-Claims

Lockbox was not used for tuning or selection. This comparison does not approve positive benchmark language, Stage 6 reinterpretation, or trading output.
"""


def _render_report(manifest: dict[str, Any]) -> str:
    comparison = manifest["comparison_summary"]
    validation = comparison["split_summaries"]["validation"]
    lockbox = comparison["split_summaries"]["lockbox"]
    return f"""# Stage 43 Updated Dataset XGBoost Tuning

Status: {manifest['status']}

Trials requested: {manifest['trial_count_requested']}

Trials completed: {manifest['trial_count_completed']}

Best development trial: `{manifest['best_development_trial'].get('trial_number')}`

Validation weighted delta vs previous XGBoost: {validation['weighted_delta_candidate_minus_previous']}

Validation both-metric improvement rate vs previous XGBoost: {validation['both_metric_improvement_rate']}

Lockbox weighted delta vs previous XGBoost: {lockbox['weighted_delta_candidate_minus_previous']}

Lockbox both-metric improvement rate vs previous XGBoost: {lockbox['both_metric_improvement_rate']}

Result class: `{comparison['result_class']}`

Non-claims: tuning used train/validation only; lockbox was post-selection comparison evidence only; no positive benchmark claim or trading signal is approved.
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
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if not isinstance(value, (dict, list, tuple)) and pd.isna(value):
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
