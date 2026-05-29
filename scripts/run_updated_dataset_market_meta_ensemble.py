from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import optuna
import pandas as pd
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    HORIZON_WEIGHTS,
    ROW_KEY,
    TSMIXER_ARCHITECTURE_VERSION,
    TSMIXER_READOUT_POLICY,
    _train_gaps,
    compute_pairwise_deltas,
    sha256_file,
    stable_digest,
)


UPDATED_STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1"
UPDATED_STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
UPDATED_XGBOOST_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__20260528T100000Z__src_6dff1bd__run_40f1c9a0"
UPDATED_TSMIXER_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage44__tsmixer_training__20260528T120000Z__src_6dff1bd__run_6817ae4c"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"

GENERATED_TOKEN = "20260528T150000Z"
GENERATED_AT_UTC = "2026-05-28T15:00:00Z"
SOURCE_ID = "6dff1bd"
DEFAULT_TRIAL_COUNT = 800
DEFAULT_PREFLIGHT_TRIALS = 25
MODEL_ID = "updated_av_market_xgb_tsmixer_horizon_meta_v1"
UPDATED_XGBOOST_MODEL_ID = "updated_av_xgboost_event_market_optuna_v1"
UPDATED_TSMIXER_MODEL_ID = "updated_av_tsmixer_event_market_optuna_v1_seed_mean"
BASE_FEATURE_COLUMNS = ["xgboost_prediction", "tsmixer_prediction"]


def updated_market_meta_ensemble_contract(trial_count: int = DEFAULT_TRIAL_COUNT) -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_market_xgb_tsmixer_horizon_meta_contract",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": MODEL_ID,
        "xgboost_model_id": UPDATED_XGBOOST_MODEL_ID,
        "tsmixer_model_id": UPDATED_TSMIXER_MODEL_ID,
        "trial_count": int(trial_count),
        "minimum_required_trials": 800,
        "model_family": "horizon_specific_regularized_meta_combiner",
        "base_features": BASE_FEATURE_COLUMNS,
        "base_model_policy": {
            "xgboost": "recompute frozen selected config for train_validation_lockbox row-level predictions",
            "tsmixer": "requires corrected TSMixer architecture artifacts; do not reuse stale mean-pooling predictions",
            "tsmixer_required_architecture_version": TSMIXER_ARCHITECTURE_VERSION,
            "tsmixer_required_readout_policy": TSMIXER_READOUT_POLICY,
            "tsmixer_previous_stale_partial_tuning_trial_count": 401,
            "tsmixer_current_corrected_artifacts_required": True,
        },
        "meta_training_policy": {
            "per_fold_horizon_model": True,
            "training_split": "train_only",
            "selection_split": "validation",
            "lockbox_rows_used_for_tuning": 0,
            "standardize_base_predictions_fold_locally": True,
            "final_lockbox_evaluation": "post_selection_only",
        },
        "optuna": {
            "direction": "minimize",
            "sampler": "TPESampler",
            "sampler_seed": 2026052805,
            "n_startup_trials": 80,
            "multivariate": True,
        },
        "search_space": {
            "estimator": {"type": "categorical", "choices": ["ridge", "elastic_net"]},
            "fit_intercept": {"type": "categorical", "choices": [True, False]},
            "positive_coefficients": {"type": "categorical", "choices": [False, True]},
            "l1_ratio": {"type": "float", "low": 0.05, "high": 0.95, "log": False},
            "alpha_by_horizon": {"type": "log_float", "low": 1e-6, "high": 10.0, "horizons": list(HORIZON_WEIGHTS)},
        },
        "selection_objective": {
            "name": "validation_weighted_delta_vs_updated_xgboost_with_overfit_penalty",
            "baseline_model_id": UPDATED_XGBOOST_MODEL_ID,
            "horizon_weights": HORIZON_WEIGHTS,
            "metric_weights": {"rmse": 0.5, "mae": 0.5},
            "lower_is_better": True,
        },
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": [
            "development_tuning_uses_train_validation_only",
            "lockbox_not_used_for_tuning_or_selection",
            "stale_tsmixer_mean_pooling_artifacts_not_reused",
            "final_lockbox_evaluation_is_post_selection_evidence",
            "not_positive_benchmark_claim",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run updated-dataset XGBoost+TSMixer horizon-specific meta-combiner.")
    parser.add_argument("--stage3-root", type=Path, default=UPDATED_STAGE3_ROOT)
    parser.add_argument("--stage4-root", type=Path, default=UPDATED_STAGE4_ROOT)
    parser.add_argument("--updated-xgboost-root", type=Path, default=UPDATED_XGBOOST_ROOT)
    parser.add_argument("--updated-tsmixer-root", type=Path, default=UPDATED_TSMIXER_ROOT)
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--preflight-trials", type=int, default=DEFAULT_PREFLIGHT_TRIALS)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()
    if args.trial_count < 800:
        raise RuntimeError("market meta-ensemble requires at least 800 trials for the final run")
    stage3_root = args.stage3_root.resolve()
    stage4_root = args.stage4_root.resolve()
    updated_xgboost_root = args.updated_xgboost_root.resolve()
    updated_tsmixer_root = args.updated_tsmixer_root.resolve()
    contract = updated_market_meta_ensemble_contract(args.trial_count)
    contract["updated_stage3_root"] = _rel(stage3_root)
    contract["updated_stage4_root"] = _rel(stage4_root)
    contract["updated_xgboost_root"] = _rel(updated_xgboost_root)
    contract["updated_tsmixer_root"] = _rel(updated_tsmixer_root)
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_updated_av__stage45__market_xgb_tsmixer_meta__{GENERATED_TOKEN}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root.resolve() if args.output_root else RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    _write_json(output_root / "market_meta_ensemble_contract.json", contract)

    prep_started = time.perf_counter()
    xgboost_predictions, xgboost_metrics = _load_or_build_xgboost_predictions(output_root, stage3_root, stage4_root, updated_xgboost_root)
    tsmixer_predictions, tsmixer_metrics, tsmixer_selection = _load_or_build_tsmixer_predictions(updated_tsmixer_root, stage3_root, stage4_root)
    meta_frame = _build_meta_frame(xgboost_predictions, tsmixer_predictions)
    prep_seconds = time.perf_counter() - prep_started

    if args.preflight_only:
        preflight = _run_preflight(meta_frame, xgboost_metrics, tsmixer_metrics, contract, int(args.preflight_trials), prep_seconds)
        preflight_path = output_root / "preflight_timing_summary.json"
        _write_json(preflight_path, preflight)
        print(json.dumps({"status": "preflight_completed", "preflight": preflight, "preflight_summary": _rel(preflight_path)}, sort_keys=True))
        return

    result = _run_full_meta_tuning(output_root, meta_frame, xgboost_metrics, tsmixer_metrics, tsmixer_selection, contract)
    print(json.dumps({"status": result["status"], "trial_count_completed": result["trial_count_completed"], "best_trial_number": result["best_trial"]["trial_number"], "manifest": result["manifest"]}, sort_keys=True))


def _load_or_build_xgboost_predictions(output_root: Path, stage3_root: Path, stage4_root: Path, xgboost_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    prediction_path = output_root / "xgboost_best_all_split_predictions.parquet"
    metrics_path = output_root / "xgboost_best_all_split_metrics.parquet"
    if prediction_path.exists() and metrics_path.exists():
        return pd.read_parquet(prediction_path), pd.read_parquet(metrics_path)
    from xgboost import XGBRegressor
    from scripts.run_updated_dataset_xgboost_tuning import _load_updated_frame, _prepare_bundles

    best_config = json.loads((xgboost_root / "best_development_candidate_config.json").read_text(encoding="utf-8"))
    frame, feature_columns, _ = _load_updated_frame(stage3_root, stage4_root)
    bundles = _prepare_bundles(frame, feature_columns)
    params = dict(best_config["resolved_xgboost_params"])
    records: list[pd.DataFrame] = []
    metric_rows: list[dict[str, Any]] = []
    trial_number = int(best_config["selected_trial_number"])
    for bundle in bundles:
        estimator = XGBRegressor(**params)
        estimator.fit(bundle["x_train"], bundle["y_train"])
        for split_role, x_key, y_key, meta_key in [
            ("train", "x_train", "y_train", None),
            ("validation", "x_validation", "y_validation", "validation_meta"),
            ("lockbox", "x_lockbox", "y_lockbox", "lockbox_meta"),
        ]:
            x_values = bundle[x_key]
            y_values = bundle[y_key]
            if len(y_values) == 0:
                continue
            prediction = estimator.predict(x_values)
            if meta_key is None:
                meta = _meta_for_train_split(frame, bundle["fold_id"], bundle["horizon_id"])
            else:
                meta = bundle[meta_key]
            output = meta.copy()
            output["trial_number"] = trial_number
            output["model_id"] = UPDATED_XGBOOST_MODEL_ID
            output["prediction"] = prediction.astype("float64")
            records.append(output)
            metric_rows.append(_metric_row(-1, split_role, bundle["fold_id"], bundle["horizon_id"], UPDATED_XGBOOST_MODEL_ID, y_values, prediction))
    predictions = pd.concat(records, ignore_index=True)
    metrics = pd.DataFrame.from_records(metric_rows)
    predictions.to_parquet(prediction_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    return predictions, metrics


def _meta_for_train_split(frame: pd.DataFrame, fold_id: str, horizon_id: str) -> pd.DataFrame:
    meta_columns = ["row_key", *ROW_KEY, "fold_id", "split_role", "target"]
    train = frame[(frame["fold_id"] == fold_id) & (frame["horizon_id"] == horizon_id) & (frame["split_role"] == "train")].copy()
    return train[meta_columns].reset_index(drop=True)


def _load_or_build_tsmixer_predictions(tsmixer_root: Path, stage3_root: Path, stage4_root: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    best_trial = _best_partial_tsmixer_trial(tsmixer_root)
    module = _load_tsmixer_module()
    contract = json.loads((tsmixer_root / "tsmixer_training_contract.json").read_text(encoding="utf-8"))
    sequence_manifest = json.loads((tsmixer_root / "sequence_windows" / "sequence_window_manifest.json").read_text(encoding="utf-8"))
    cache = module._SequenceFrameCache(sequence_manifest, stage3_root, stage4_root)
    final = module._run_or_load_final_evaluation(tsmixer_root, cache, best_trial, contract)
    predictions = pd.read_parquet(tsmixer_root / "best_tsmixer_predictions.parquet")
    metrics = final["metrics"] if isinstance(final.get("metrics"), pd.DataFrame) else pd.read_parquet(tsmixer_root / "best_tsmixer_metrics.parquet")
    return predictions[predictions["model_id"] == UPDATED_TSMIXER_MODEL_ID].copy(), metrics[metrics["model_id"] == UPDATED_TSMIXER_MODEL_ID].copy(), best_trial


def _best_partial_tsmixer_trial(tsmixer_root: Path) -> dict[str, Any]:
    ledger = _read_jsonl_frame(tsmixer_root / "trial_ledger.ndjson")
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        raise RuntimeError("no completed TSMixer tuning trials found to freeze")
    if "architecture_version" not in completed.columns or "readout_policy" not in completed.columns:
        raise RuntimeError("completed TSMixer trials predate the corrected readout; Stage 45 meta evidence must not reuse them")
    stale = completed[(completed["architecture_version"] != TSMIXER_ARCHITECTURE_VERSION) | (completed["readout_policy"] != TSMIXER_READOUT_POLICY)]
    if not stale.empty:
        raise RuntimeError("completed TSMixer trials use a stale architecture; Stage 45 meta evidence must not reuse them")
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()
    best["params"] = json.loads(str(best["params_json"]))
    best["frozen_from_partial_optuna"] = True
    best["trial_count_completed_at_freeze"] = int(len(completed))
    best["trial_count_requested_at_freeze"] = 800
    best["freeze_reason"] = "user_defined_best_available_tsmixer_after_partial_401_trial_run"
    return best


def _load_tsmixer_module() -> Any:
    path = PROJECT_ROOT / "scripts" / "run_updated_dataset_tsmixer_training.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load TSMixer runner module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_meta_frame(xgboost_predictions: pd.DataFrame, tsmixer_predictions: pd.DataFrame) -> pd.DataFrame:
    keys = ["row_key", *ROW_KEY, "fold_id", "split_role", "target"]
    xgb = xgboost_predictions[keys + ["prediction"]].rename(columns={"prediction": "xgboost_prediction"})
    tsm = tsmixer_predictions[keys + ["prediction"]].rename(columns={"prediction": "tsmixer_prediction"})
    frame = xgb.merge(tsm, on=keys, how="inner", validate="one_to_one")
    expected_roles = {"train", "validation", "lockbox"}
    if set(frame["split_role"].unique()) != expected_roles:
        raise RuntimeError(f"meta frame split roles incomplete: {sorted(frame['split_role'].unique())}")
    return frame


def _run_preflight(meta_frame: pd.DataFrame, xgboost_metrics: pd.DataFrame, tsmixer_metrics: pd.DataFrame, contract: dict[str, Any], preflight_trials: int, prep_seconds: float) -> dict[str, Any]:
    sampler = optuna.samplers.TPESampler(seed=int(contract["optuna"]["sampler_seed"]), n_startup_trials=min(int(contract["optuna"]["n_startup_trials"]), int(preflight_trials)), multivariate=bool(contract["optuna"].get("multivariate", False)))
    study = optuna.create_study(direction="minimize", sampler=sampler)
    durations: list[float] = []

    def objective(trial: optuna.Trial) -> float:
        started = time.perf_counter()
        config = _suggest_meta_config(trial)
        _, metrics, _ = _fit_meta_config(meta_frame, config, int(trial.number), split_roles=("train", "validation"), save_predictions=False)
        summary = _summarize_meta_trial(metrics, xgboost_metrics, config)
        durations.append(time.perf_counter() - started)
        return float(summary["objective_value"])

    study.optimize(objective, n_trials=int(preflight_trials), show_progress_bar=False)
    median_seconds = float(np.median(durations)) if durations else float("inf")
    mean_seconds = float(np.mean(durations)) if durations else float("inf")
    estimate_seconds = median_seconds * int(contract["trial_count"])
    return {
        "status": "completed",
        "preflight_trials": int(preflight_trials),
        "trial_count_for_full_run": int(contract["trial_count"]),
        "base_prediction_preparation_seconds": round(float(prep_seconds), 3),
        "median_seconds_per_meta_trial": round(median_seconds, 6),
        "mean_seconds_per_meta_trial": round(mean_seconds, 6),
        "estimated_full_meta_tuning_seconds": round(float(estimate_seconds), 3),
        "estimated_full_meta_tuning_minutes": round(float(estimate_seconds) / 60.0, 3),
        "under_one_hour": bool(estimate_seconds < 3600.0),
        "best_preflight_value": float(study.best_value),
        "lockbox_rows_used_for_tuning": 0,
        "tsmixer_tuning_trials_added": 0,
        "tsmixer_model_frozen_from_partial_trial": True,
    }


def _run_full_meta_tuning(output_root: Path, meta_frame: pd.DataFrame, xgboost_metrics: pd.DataFrame, tsmixer_metrics: pd.DataFrame, tsmixer_selection: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    ledger_jsonl_path = output_root / "meta_trial_ledger.ndjson"
    metrics_jsonl_path = output_root / "meta_trial_fold_metrics.ndjson"
    coefficients_jsonl_path = output_root / "meta_trial_coefficients.ndjson"
    storage_path = output_root / "optuna_study.sqlite3"
    sampler = optuna.samplers.TPESampler(seed=int(contract["optuna"]["sampler_seed"]), n_startup_trials=int(contract["optuna"]["n_startup_trials"]), multivariate=bool(contract["optuna"].get("multivariate", False)))
    study = optuna.create_study(study_name="updated_av_market_xgb_tsmixer_horizon_meta_800", direction="minimize", sampler=sampler, storage=f"sqlite:///{storage_path}", load_if_exists=True)
    completed_ids = _completed_trial_ids(ledger_jsonl_path)

    def objective(trial: optuna.Trial) -> float:
        trial_number = int(trial.number)
        if trial_number in completed_ids:
            prior = _read_trial_record(ledger_jsonl_path, trial_number)
            if prior and prior.get("status") == "completed":
                return float(prior["objective_value"])
        config = _suggest_meta_config(trial)
        started = time.perf_counter()
        try:
            _, metrics, coefficients = _fit_meta_config(meta_frame, config, trial_number, split_roles=("train", "validation"), save_predictions=False)
            summary = _summarize_meta_trial(metrics, xgboost_metrics, config)
            ledger = {"trial_number": trial_number, "status": "completed", "runtime_seconds": round(time.perf_counter() - started, 6), "params_json": json.dumps(config, sort_keys=True), **summary}
        except Exception as exc:  # noqa: BLE001 - failures are recorded evidence.
            metrics = pd.DataFrame()
            coefficients = pd.DataFrame()
            ledger = {"trial_number": trial_number, "status": "failed", "runtime_seconds": round(time.perf_counter() - started, 6), "params_json": json.dumps(config, sort_keys=True), "objective_value": 1e9, "failure_reason": repr(exc), "lockbox_rows_used_for_tuning": 0}
        _append_jsonl(ledger_jsonl_path, ledger)
        completed_ids.add(trial_number)
        for row in metrics.to_dict("records"):
            _append_jsonl(metrics_jsonl_path, row)
        for row in coefficients.to_dict("records"):
            _append_jsonl(coefficients_jsonl_path, row)
        print(json.dumps({"trial_number": trial_number, "status": ledger["status"], "objective_value": ledger.get("objective_value")}, sort_keys=True), flush=True)
        return float(ledger.get("objective_value", 1e9) or 1e9)

    remaining = max(0, int(contract["trial_count"]) - len(completed_ids))
    if remaining:
        study.optimize(objective, n_trials=remaining, show_progress_bar=False)

    ledger = _read_jsonl_frame(ledger_jsonl_path)
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        raise RuntimeError("meta-ensemble tuning produced no completed trials")
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()
    best_config = json.loads(str(best["params_json"]))
    final_predictions, final_metrics, final_coefficients = _fit_meta_config(meta_frame, best_config, int(best["trial_number"]), split_roles=("train", "validation", "lockbox"), save_predictions=True)
    comparison_summary = _build_comparison_summary(final_metrics, xgboost_metrics, tsmixer_metrics)

    ledger_path = output_root / "meta_trial_ledger.parquet"
    metrics_path = output_root / "meta_trial_fold_metrics.parquet"
    coefficients_path = output_root / "meta_trial_coefficients.parquet"
    final_predictions_path = output_root / "best_meta_predictions.parquet"
    final_metrics_path = output_root / "best_meta_metrics.parquet"
    final_coefficients_path = output_root / "best_meta_coefficients.parquet"
    comparison_json_path = output_root / "comparison_summary.json"
    comparison_md_path = output_root / "comparison_summary.md"
    manifest_path = output_root / "updated_dataset_market_meta_ensemble_manifest.json"
    report_path = output_root / "stage45_updated_dataset_market_meta_ensemble_report.md"
    run_manifest_path = output_root / "run_manifest.json"

    ledger.to_parquet(ledger_path, index=False)
    _read_jsonl_frame(metrics_jsonl_path).to_parquet(metrics_path, index=False)
    _read_jsonl_frame(coefficients_jsonl_path).to_parquet(coefficients_path, index=False)
    final_predictions.to_parquet(final_predictions_path, index=False)
    final_metrics.to_parquet(final_metrics_path, index=False)
    final_coefficients.to_parquet(final_coefficients_path, index=False)
    _write_json(comparison_json_path, comparison_summary)
    comparison_md_path.write_text(_render_comparison_markdown(comparison_summary), encoding="utf-8")

    manifest = {
        "artifact_type": "updated_dataset_market_xgb_tsmixer_horizon_meta_manifest",
        "artifact_id": f"updated_dataset_market_meta_ensemble__{sha256_file(ledger_path)[:12]}__{GENERATED_TOKEN}",
        "generated_at_utc": GENERATED_AT_UTC,
        "status": "completed" if int((ledger["status"] == "completed").sum()) >= int(contract["trial_count"]) else "partial",
        "model_id": MODEL_ID,
        "xgboost_model_id": UPDATED_XGBOOST_MODEL_ID,
        "tsmixer_model_id": UPDATED_TSMIXER_MODEL_ID,
        "tsmixer_selection": tsmixer_selection,
        "trial_count_requested": int(contract["trial_count"]),
        "trial_count_completed": int((ledger["status"] == "completed").sum()),
        "trial_count_failed": int((ledger["status"] == "failed").sum()),
        "best_trial": {**best, "params": best_config},
        "comparison_summary": comparison_summary,
        "lockbox_rows_used_for_tuning": 0,
        "outputs": {
            "contract": _rel(output_root / "market_meta_ensemble_contract.json"),
            "trial_ledger_ndjson": _rel(ledger_jsonl_path),
            "trial_ledger": _rel(ledger_path),
            "trial_fold_metrics_ndjson": _rel(metrics_jsonl_path),
            "trial_fold_metrics": _rel(metrics_path),
            "trial_coefficients_ndjson": _rel(coefficients_jsonl_path),
            "trial_coefficients": _rel(coefficients_path),
            "best_meta_predictions": _rel(final_predictions_path),
            "best_meta_metrics": _rel(final_metrics_path),
            "best_meta_coefficients": _rel(final_coefficients_path),
            "comparison_json": _rel(comparison_json_path),
            "comparison_markdown": _rel(comparison_md_path),
            "optuna_storage": _rel(storage_path),
            "manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": contract["non_claims"],
    }
    _write_json(manifest_path, manifest)
    _write_json(run_manifest_path, {"stage": 45, "stage_name": "updated_dataset_market_xgb_tsmixer_horizon_meta", "status": manifest["status"], "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_render_report(manifest), encoding="utf-8")
    return {"status": manifest["status"], "trial_count_completed": manifest["trial_count_completed"], "best_trial": manifest["best_trial"], "manifest": manifest["outputs"]["manifest"]}


def _suggest_meta_config(trial: optuna.Trial) -> dict[str, Any]:
    config = {
        "estimator": trial.suggest_categorical("estimator", ["ridge", "elastic_net"]),
        "fit_intercept": bool(trial.suggest_categorical("fit_intercept", [True, False])),
        "positive_coefficients": bool(trial.suggest_categorical("positive_coefficients", [False, True])),
        "l1_ratio": float(trial.suggest_float("l1_ratio", 0.05, 0.95)),
        "alpha_by_horizon": {},
    }
    for horizon_id in HORIZON_WEIGHTS:
        config["alpha_by_horizon"][horizon_id] = float(trial.suggest_float(f"alpha_{horizon_id}", 1e-6, 10.0, log=True))
    return config


def _fit_meta_config(meta_frame: pd.DataFrame, config: dict[str, Any], trial_number: int, *, split_roles: tuple[str, ...], save_predictions: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, Any]] = []
    coefficient_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    for (fold_id, horizon_id), group in meta_frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        if train.empty:
            continue
        alpha = float(config["alpha_by_horizon"][horizon_id])
        scaler = StandardScaler().fit(train[BASE_FEATURE_COLUMNS].astype("float64"))
        x_train = scaler.transform(train[BASE_FEATURE_COLUMNS].astype("float64"))
        y_train = train["target"].astype("float64").to_numpy()
        if config["estimator"] == "ridge":
            estimator = Ridge(alpha=alpha, fit_intercept=bool(config["fit_intercept"]), positive=bool(config["positive_coefficients"]))
        else:
            estimator = ElasticNet(alpha=alpha, l1_ratio=float(config["l1_ratio"]), fit_intercept=bool(config["fit_intercept"]), positive=bool(config["positive_coefficients"]), max_iter=10000, random_state=2026052805)
        started = time.perf_counter()
        estimator.fit(x_train, y_train)
        fit_seconds = time.perf_counter() - started
        raw_coefficients, raw_intercept = _raw_coefficients(estimator, scaler)
        coefficient_rows.append({
            "trial_number": int(trial_number),
            "model_id": MODEL_ID,
            "fold_id": fold_id,
            "horizon_id": horizon_id,
            "estimator": str(config["estimator"]),
            "alpha": alpha,
            "l1_ratio": float(config["l1_ratio"]),
            "fit_intercept": bool(config["fit_intercept"]),
            "positive_coefficients": bool(config["positive_coefficients"]),
            "raw_intercept": float(raw_intercept),
            "raw_xgboost_weight": float(raw_coefficients[0]),
            "raw_tsmixer_weight": float(raw_coefficients[1]),
            "standardized_xgboost_weight": float(estimator.coef_[0]),
            "standardized_tsmixer_weight": float(estimator.coef_[1]),
            "train_rows": int(len(train)),
            "training_seconds": round(fit_seconds, 6),
            "lockbox_rows_used_for_tuning": 0,
        })
        for split_role in split_roles:
            split = group[group["split_role"] == split_role].copy()
            if split.empty:
                continue
            x_split = scaler.transform(split[BASE_FEATURE_COLUMNS].astype("float64"))
            prediction = estimator.predict(x_split).astype("float64")
            metric_rows.append(_metric_row(trial_number, split_role, fold_id, horizon_id, MODEL_ID, split["target"].to_numpy(dtype="float64"), prediction))
            if save_predictions:
                output = split[["row_key", *ROW_KEY, "fold_id", "split_role", "target", *BASE_FEATURE_COLUMNS]].copy()
                output["trial_number"] = int(trial_number)
                output["model_id"] = MODEL_ID
                output["prediction"] = prediction
                prediction_frames.append(output)
    predictions = pd.concat(prediction_frames, ignore_index=True) if prediction_frames else pd.DataFrame()
    return predictions, pd.DataFrame.from_records(metric_rows), pd.DataFrame.from_records(coefficient_rows)


def _raw_coefficients(estimator: Any, scaler: StandardScaler) -> tuple[np.ndarray, float]:
    scale = scaler.scale_.astype("float64")
    mean = scaler.mean_.astype("float64")
    coef = np.asarray(estimator.coef_, dtype="float64") / scale
    intercept = float(getattr(estimator, "intercept_", 0.0)) - float(np.dot(coef, mean))
    return coef, intercept


def _summarize_meta_trial(metrics: pd.DataFrame, xgboost_metrics: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    deltas = compute_pairwise_deltas(pd.concat([metrics, xgboost_metrics], ignore_index=True, sort=False), UPDATED_XGBOOST_MODEL_ID, [MODEL_ID])
    validation = deltas[deltas["split_role"] == "validation"].copy()
    train = deltas[deltas["split_role"] == "train"].copy()
    validation_weighted_delta = _weighted_delta(validation)
    train_weighted_delta = _weighted_delta(train)
    validation_rate = float(validation["both_metrics_improve"].mean()) if not validation.empty else 0.0
    train_rate = float(train["both_metrics_improve"].mean()) if not train.empty else 0.0
    gaps = _train_gaps(metrics)
    gap_rate = float(gaps["gap_flag"].mean()) if not gaps.empty else 0.0
    gap_penalty = max(0.0, gap_rate - 0.50) * 0.001
    degradation_penalty = max(0.0, validation_weighted_delta) * 0.10
    objective_value = validation_weighted_delta + gap_penalty + degradation_penalty
    return {
        "objective_value": float(objective_value),
        "validation_weighted_delta_vs_updated_xgboost": float(validation_weighted_delta),
        "train_weighted_delta_vs_updated_xgboost": float(train_weighted_delta),
        "validation_both_metric_improvement_rate_vs_updated_xgboost": validation_rate,
        "train_both_metric_improvement_rate_vs_updated_xgboost": train_rate,
        "train_validation_gap_flag_rate": gap_rate,
        "gap_penalty": float(gap_penalty),
        "degradation_penalty": float(degradation_penalty),
        "lockbox_rows_used_for_tuning": 0,
    }


def _build_comparison_summary(meta_metrics: pd.DataFrame, xgboost_metrics: pd.DataFrame, tsmixer_metrics: pd.DataFrame) -> dict[str, Any]:
    comparisons = []
    for baseline_id, baseline_metrics in [(UPDATED_XGBOOST_MODEL_ID, xgboost_metrics), (UPDATED_TSMIXER_MODEL_ID, tsmixer_metrics)]:
        deltas = compute_pairwise_deltas(pd.concat([meta_metrics, baseline_metrics], ignore_index=True, sort=False), baseline_id, [MODEL_ID])
        comparisons.append({"baseline_model_id": baseline_id, "candidate_model_id": MODEL_ID, "split_summaries": _split_delta_summary(deltas), "metric_summary": _comparison_metric_summary(meta_metrics, baseline_metrics, baseline_id)})
    return {"artifact_type": "updated_dataset_market_meta_ensemble_comparison_summary", "generated_at_utc": GENERATED_AT_UTC, "candidate_model_id": MODEL_ID, "comparisons": comparisons, "lockbox_used_for_tuning": False, "benchmark_claim": False, "positive_claim_approved": False}


def _split_delta_summary(deltas: pd.DataFrame) -> dict[str, Any]:
    summary = {}
    for split_role in ["train", "validation", "lockbox"]:
        split = deltas[deltas["split_role"] == split_role].copy()
        summary[split_role] = {"comparison_rows": int(len(split)), "weighted_delta_candidate_minus_baseline": _weighted_delta(split), "both_metric_improvement_rate": float(split["both_metrics_improve"].mean()) if not split.empty else 0.0, "rmse_delta_mean": float(split["rmse_delta_candidate_minus_baseline"].mean()) if not split.empty else None, "mae_delta_mean": float(split["mae_delta_candidate_minus_baseline"].mean()) if not split.empty else None}
    return summary


def _comparison_metric_summary(candidate: pd.DataFrame, baseline: pd.DataFrame, baseline_id: str) -> list[dict[str, Any]]:
    rows = []
    for split_role in ["train", "validation", "lockbox"]:
        for model_id, source in [(MODEL_ID, candidate), (baseline_id, baseline)]:
            split = source[(source["split_role"] == split_role) & (source["model_id"] == model_id)]
            rows.append({"split_role": split_role, "model_id": model_id, "metric_rows": int(len(split)), "weighted_error": _weighted_error(split), "rmse_mean": float(split["rmse"].mean()) if not split.empty else None, "mae_mean": float(split["mae"].mean()) if not split.empty else None, "r2_oos_zero_baseline_mean": float(split["r2_oos_zero_baseline"].mean()) if not split.empty else None})
    return rows


def _metric_row(trial_number: int, split_role: str, fold_id: str, horizon_id: str, model_id: str, target: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    target = target.astype("float64", copy=False)
    prediction = prediction.astype("float64", copy=False)
    error = prediction - target
    denominator = float(np.sum(target**2))
    sse = float(np.sum(error**2))
    return {"trial_number": int(trial_number), "split_role": split_role, "fold_id": fold_id, "horizon_id": horizon_id, "model_id": model_id, "row_count": int(len(target)), "rmse": float(np.sqrt(np.mean(error**2))), "mae": float(np.mean(np.abs(error))), "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator), "lockbox_rows_used_for_tuning": 0}


def _weighted_delta(deltas: pd.DataFrame) -> float:
    if deltas.empty:
        return float("inf")
    working = deltas.copy()
    working["horizon_weight"] = working["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    working["weighted_delta"] = working["horizon_weight"] * (0.5 * working["rmse_delta_candidate_minus_baseline"] + 0.5 * working["mae_delta_candidate_minus_baseline"])
    return float(working.groupby("horizon_id", sort=True)["weighted_delta"].mean().sum())


def _weighted_error(metrics: pd.DataFrame) -> float | None:
    if metrics.empty:
        return None
    working = metrics.copy()
    working["horizon_weight"] = working["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    working["weighted_error"] = working["horizon_weight"] * (0.5 * working["rmse"].astype("float64") + 0.5 * working["mae"].astype("float64"))
    return float(working.groupby("horizon_id", sort=True)["weighted_error"].mean().sum())


def _render_comparison_markdown(summary: dict[str, Any]) -> str:
    lines = ["# Updated Dataset Market XGB + TSMixer Horizon Meta", "", f"Candidate model: `{summary['candidate_model_id']}`", "", "Lockbox was not used for tuning or selection."]
    for comparison in summary["comparisons"]:
        lines.extend(["", f"## Versus `{comparison['baseline_model_id']}`"])
        for split_role in ["validation", "lockbox"]:
            split = comparison["split_summaries"][split_role]
            lines.extend(["", f"{split_role.title()} weighted delta candidate minus baseline: {split['weighted_delta_candidate_minus_baseline']}", f"{split_role.title()} both-metric improvement rate: {split['both_metric_improvement_rate']}"])
    lines.extend(["", "Non-claims: not positive benchmark language, not Stage 6 reinterpretation, and not trading output.", ""])
    return "\n".join(lines)


def _render_report(manifest: dict[str, Any]) -> str:
    comparison = manifest["comparison_summary"]["comparisons"][0]
    validation = comparison["split_summaries"]["validation"]
    lockbox = comparison["split_summaries"]["lockbox"]
    return f"""# Stage 45 Updated Dataset Market XGB + TSMixer Horizon Meta

Status: {manifest['status']}

Trials requested: {manifest['trial_count_requested']}

Trials completed: {manifest['trial_count_completed']}

Best meta trial: `{manifest['best_trial'].get('trial_number')}`

Validation weighted delta vs updated XGBoost: {validation['weighted_delta_candidate_minus_baseline']}

Validation both-metric improvement rate vs updated XGBoost: {validation['both_metric_improvement_rate']}

Lockbox weighted delta vs updated XGBoost: {lockbox['weighted_delta_candidate_minus_baseline']}

Lockbox both-metric improvement rate vs updated XGBoost: {lockbox['both_metric_improvement_rate']}

Lockbox rows used for tuning: {manifest['lockbox_rows_used_for_tuning']}

TSMixer policy: corrected-architecture TSMixer artifacts are required; stale mean-pooling TSMixer predictions must not feed this meta-combiner.

Non-claims: no positive benchmark claim, Stage 6 reinterpretation, benchmark-comparability promotion, or trading output is approved.
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
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if value is None:
        return None
    try:
        if not isinstance(value, (str, bytes)) and pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    main()
