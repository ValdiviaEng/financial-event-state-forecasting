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

from event_state_forecasting.v1p0.modeling import fit_preprocessor  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402
from event_state_forecasting.v1p0.xgboost_search import (  # noqa: E402
    compute_guarded_hurdle_objective,
    select_best_stage22_trial,
    validate_stage22_prediction_schema,
    validate_stage22_trial_ledger_schema,
    validate_xgboost_search_config,
)


FEATURE_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
STAGE20_ROOT = PROJECT_ROOT / "data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z"
STAGE21_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage21__xgboost_search_freeze__20260524T071500Z__src_6dff1bd__run_2a802f16"
CONFIG_PATH = PROJECT_ROOT / "configs/xgboost_search_v1p0.yaml"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_AT_UTC = "2026-05-24T07:30:00Z"
SOURCE_ID = "6dff1bd"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the v1p0 Stage 22 XGBoost development-only nested search.")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--max-trials", type=int, default=None, help="Optional non-default cap for shakedown runs. Omit for the frozen full budget.")
    args = parser.parse_args()

    started = time.perf_counter()
    config = validate_xgboost_search_config(load_json_config(args.config))
    stage21_manifest = json.loads((STAGE21_ROOT / "search_space_manifest.json").read_text(encoding="utf-8"))
    if stage21_manifest["config_digest_sha256"] != config["config_digest_sha256"]:
        raise RuntimeError("Stage 21 manifest digest does not match current search config")
    if not stage21_manifest["stage22_allowed"]:
        raise RuntimeError("Stage 21 manifest does not allow Stage 22")

    run_id = f"v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_{SOURCE_ID}__run_{config['config_digest_sha256'][:8]}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    prediction_root = output_root / "trial_predictions"
    prediction_root.mkdir(exist_ok=True)
    ledger_path = output_root / "trial_ledger.ndjson"
    fold_metrics_path = output_root / "trial_fold_metrics.ndjson"
    prediction_index_path = output_root / "trial_prediction_index.ndjson"

    feature_manifest = json.loads((FEATURE_ROOT / "feature_manifest.json").read_text(encoding="utf-8"))
    frame = _load_development_frame(feature_manifest)
    bundles = _prepare_fold_horizon_bundles(frame, list(feature_manifest["feature_columns"]))
    hurdle_metrics = _load_hurdle_metrics(config["hurdle_model_id"])
    frozen_trial_count = int(config["budgets"]["max_total_trials"])
    requested_trial_count = min(frozen_trial_count, args.max_trials) if args.max_trials is not None else frozen_trial_count

    completed_trial_ids = _completed_trial_ids(ledger_path)
    rng = np.random.default_rng(1729)
    trial_id = 1
    for _ in range(int(config["budgets"]["random_trials"])):
        if trial_id > requested_trial_count:
            break
        trial = {"trial_id": trial_id, "phase_id": "phase1_random", "sampler": "random", "seed": 1729 + trial_id, "params": _sample_random_params(config, rng)}
        _execute_and_record_trial(trial, completed_trial_ids, bundles, hurdle_metrics, config, prediction_root, ledger_path, fold_metrics_path, prediction_index_path)
        trial_id += 1

    sampler = optuna.samplers.TPESampler(seed=1730, n_startup_trials=25, multivariate=True)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    for _ in range(int(config["budgets"]["optuna_tpe_trials"])):
        if trial_id > requested_trial_count:
            break
        optuna_trial = study.ask()
        params = _suggest_optuna_params(optuna_trial, config)
        trial = {"trial_id": trial_id, "phase_id": "phase2_optuna_tpe", "sampler": "optuna_tpe", "seed": 1730 + trial_id, "params": params}
        ledger_record = _execute_and_record_trial(trial, completed_trial_ids, bundles, hurdle_metrics, config, prediction_root, ledger_path, fold_metrics_path, prediction_index_path)
        if ledger_record is not None and ledger_record["status"] == "completed":
            study.tell(optuna_trial, float(ledger_record["objective_value"]))
        else:
            study.tell(optuna_trial, state=optuna.trial.TrialState.FAIL)
        trial_id += 1

    local_rng = np.random.default_rng(1731)
    current_ledger = _read_jsonl_frame(ledger_path)
    has_completed_trial = (not current_ledger.empty) and bool((current_ledger["status"] == "completed").any())
    best_params = json.loads(select_best_stage22_trial(current_ledger)["params_json"]) if has_completed_trial else _sample_random_params(config, local_rng)
    for _ in range(int(config["budgets"]["local_refinement_trials"])):
        if trial_id > requested_trial_count:
            break
        trial = {"trial_id": trial_id, "phase_id": "phase3_local_refinement", "sampler": "local_refinement", "seed": 1731 + trial_id, "params": _sample_local_params(config, best_params, local_rng)}
        _execute_and_record_trial(trial, completed_trial_ids, bundles, hurdle_metrics, config, prediction_root, ledger_path, fold_metrics_path, prediction_index_path)
        trial_id += 1

    ledger = _read_jsonl_frame(ledger_path)
    fold_metrics = _read_jsonl_frame(fold_metrics_path)
    prediction_index = _read_jsonl_frame(prediction_index_path)
    schema_result = validate_stage22_trial_ledger_schema(ledger)
    best = select_best_stage22_trial(ledger)
    overfit_frontier = _build_overfit_frontier(ledger)

    ledger_parquet = output_root / "trial_ledger.parquet"
    fold_metrics_parquet = output_root / "trial_fold_metrics.parquet"
    prediction_index_parquet = output_root / "trial_prediction_index.parquet"
    overfit_frontier_parquet = output_root / "overfit_frontier.parquet"
    ledger.to_parquet(ledger_parquet, index=False)
    fold_metrics.to_parquet(fold_metrics_parquet, index=False)
    prediction_index.to_parquet(prediction_index_parquet, index=False)
    overfit_frontier.to_parquet(overfit_frontier_parquet, index=False)

    best_config_path = output_root / "best_development_candidate_config.json"
    best_config = _best_candidate_config(best, config)
    _write_json(best_config_path, best_config)

    manifest_path = output_root / "search_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage22_xgboost_search_report.md"
    manifest = {
        "artifact_type": "v1p0_stage22_xgboost_search_manifest",
        "artifact_id": f"xgboost_stage22_search__stage21_{config['config_digest_sha256'][:12]}__20260524T073000Z",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed" if schema_result["completed_trial_count"] == requested_trial_count else "partial",
        "source_stage21_artifact_id": stage21_manifest["artifact_id"],
        "search_config_digest_sha256": config["config_digest_sha256"],
        "candidate_model_id": config["candidate_model_id"],
        "hurdle_model_id": config["hurdle_model_id"],
        "requested_trial_count": requested_trial_count,
        "trial_schema": schema_result,
        "best_development_trial": {k: best[k] for k in ["trial_id", "phase_id", "objective_value", "base_hurdle_delta", "total_penalty", "params_json"]},
        "outputs": {
            "trial_ledger_ndjson": _rel(ledger_path),
            "trial_ledger_parquet": _rel(ledger_parquet),
            "trial_fold_metrics_ndjson": _rel(fold_metrics_path),
            "trial_fold_metrics_parquet": _rel(fold_metrics_parquet),
            "trial_prediction_index_ndjson": _rel(prediction_index_path),
            "trial_prediction_index_parquet": _rel(prediction_index_parquet),
            "trial_prediction_root": _rel(prediction_root),
            "overfit_frontier": _rel(overfit_frontier_parquet),
            "best_development_candidate_config": _rel(best_config_path),
            "search_manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "lockbox_policy": {
            "lockbox_predictions_loaded": False,
            "lockbox_metrics_loaded_for_selection": False,
            "lockbox_used_for_search": False,
            "lockbox_used_for_candidate_selection": False,
        },
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "benchmark_claim": False,
        "promotion_claim": False,
        "non_claims": ["not_final_evaluation", "not_lockbox_result", "not_promotion_claim", "not_stage6_reinterpretation", "not_trading_signal"],
    }
    _write_json(manifest_path, manifest)
    run_manifest = {
        "run_id": run_id,
        "stage": 22,
        "stage_name": "xgboost_nested_random_and_optuna_search",
        "generated_at_utc": GENERATED_AT_UTC,
        "status": manifest["status"],
        "command": "source ~/venvs/ai/bin/activate && python scripts/run_v1p0_xgboost_nested_search.py",
        "outputs": manifest["outputs"],
        "benchmark_claim": False,
        "lockbox_tuning": False,
    }
    _write_json(run_manifest_path, run_manifest)
    report_path.write_text(_render_report(manifest), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "trial_count": schema_result["trial_count"], "completed_trial_count": schema_result["completed_trial_count"], "best_trial_id": int(best["trial_id"]), "best_objective_value": float(best["objective_value"]), "output_root": _rel(output_root)}, sort_keys=True))


def _execute_and_record_trial(
    trial: dict[str, Any],
    completed_trial_ids: set[int],
    bundles: list[dict[str, Any]],
    hurdle_metrics: pd.DataFrame,
    config: dict[str, Any],
    prediction_root: Path,
    ledger_path: Path,
    fold_metrics_path: Path,
    prediction_index_path: Path,
) -> dict[str, Any] | None:
    if int(trial["trial_id"]) in completed_trial_ids:
        return None
    record = _execute_trial(trial, bundles, hurdle_metrics, config, prediction_root)
    _append_jsonl(ledger_path, record["ledger"])
    completed_trial_ids.add(int(trial["trial_id"]))
    for row in record["fold_metrics"]:
        _append_jsonl(fold_metrics_path, row)
    if record["prediction_index"] is not None:
        _append_jsonl(prediction_index_path, record["prediction_index"])
    print(json.dumps({"trial_id": int(trial["trial_id"]), "phase_id": trial["phase_id"], "status": record["ledger"]["status"], "objective_value": record["ledger"]["objective_value"]}, sort_keys=True), flush=True)
    return record["ledger"]


def _execute_trial(trial: dict[str, Any], bundles: list[dict[str, Any]], hurdle_metrics: pd.DataFrame, config: dict[str, Any], prediction_root: Path) -> dict[str, Any]:
    started = time.perf_counter()
    from xgboost import XGBRegressor

    fold_metrics: list[dict[str, Any]] = []
    validation_predictions: list[pd.DataFrame] = []
    training_seconds = 0.0
    inference_seconds = 0.0
    try:
        resolved_params = _resolved_xgboost_params(config, trial["params"], int(trial["seed"]))
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
            fold_metrics.append(_metric_row(trial, bundle, "train", train_pred, bundle["y_train"], fit_seconds, predict_seconds))
            fold_metrics.append(_metric_row(trial, bundle, "validation", validation_pred, bundle["y_validation"], fit_seconds, predict_seconds))
            validation_frame = bundle["validation_meta"].copy()
            validation_frame.insert(0, "trial_id", int(trial["trial_id"]))
            validation_frame["model_id"] = config["candidate_model_id"]
            validation_frame["prediction"] = validation_pred.astype("float64")
            validation_frame["target"] = bundle["y_validation"]
            validation_predictions.append(validation_frame)
        candidate_metrics = pd.DataFrame.from_records(fold_metrics)
        objective_input = pd.concat([candidate_metrics[["split_role", "fold_id", "horizon_id", "model_id", "rmse", "mae"]], hurdle_metrics], ignore_index=True)
        objective = compute_guarded_hurdle_objective(objective_input, config, trial_params=trial["params"])
        predictions = pd.concat(validation_predictions, ignore_index=True)
        validate_stage22_prediction_schema(predictions)
        prediction_path = prediction_root / f"trial_{int(trial['trial_id']):04d}_validation_predictions.parquet"
        predictions.to_parquet(prediction_path, index=False)
        ledger = _ledger_record(trial, objective, training_seconds, inference_seconds, time.perf_counter() - started, _rel(prediction_path), "completed", "")
        return {"ledger": ledger, "fold_metrics": fold_metrics, "prediction_index": {"trial_id": int(trial["trial_id"]), "prediction_path": _rel(prediction_path), "row_count": int(len(predictions))}}
    except Exception as exc:  # noqa: BLE001 - failed trials must be recorded, not hidden.
        ledger = _ledger_record(trial, None, training_seconds, inference_seconds, time.perf_counter() - started, "", "failed", repr(exc))
        return {"ledger": ledger, "fold_metrics": fold_metrics, "prediction_index": None}


def _load_development_frame(feature_manifest: dict[str, Any]) -> pd.DataFrame:
    row_key = list(feature_manifest["row_key"])
    features = pd.read_parquet(PROJECT_ROOT / feature_manifest["outputs"]["market_lag_features"])
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*row_key, "forward_excess_return"])
    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet", columns=["fold_id", *row_key, "split_role", "lockbox_flag", "preprocessing_fit_allowed"])
    splits = splits[splits["split_role"].isin(["train", "validation"])].copy()
    if bool(splits["lockbox_flag"].any()):
        raise RuntimeError("Stage 22 development frame unexpectedly contains lockbox rows")
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


def _load_hurdle_metrics(hurdle_model_id: str) -> pd.DataFrame:
    metrics = pd.read_parquet(STAGE20_ROOT / "metrics.parquet", columns=["split_role", "fold_id", "horizon_id", "model_id", "rmse", "mae"])
    return metrics[(metrics["model_id"] == hurdle_model_id) & (metrics["split_role"].isin(["train", "validation"]))].copy()


def _metric_row(trial: dict[str, Any], bundle: dict[str, Any], split_role: str, prediction: np.ndarray, target: np.ndarray, training_seconds: float, inference_seconds: float) -> dict[str, Any]:
    error = prediction.astype("float64") - target.astype("float64")
    return {
        "trial_id": int(trial["trial_id"]),
        "phase_id": trial["phase_id"],
        "split_role": split_role,
        "fold_id": bundle["fold_id"],
        "horizon_id": bundle["horizon_id"],
        "model_id": "market_xgboost_v2_nested_optuna_candidate",
        "row_count": int(len(target)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "training_time_seconds": round(training_seconds, 6),
        "inference_time_seconds": round(inference_seconds, 6),
    }


def _ledger_record(trial: dict[str, Any], objective: dict[str, Any] | None, training_seconds: float, inference_seconds: float, total_seconds: float, prediction_path: str, status: str, failure_reason: str) -> dict[str, Any]:
    penalties = objective["penalties"] if objective else {}
    return {
        "trial_id": int(trial["trial_id"]),
        "phase_id": trial["phase_id"],
        "sampler": trial["sampler"],
        "seed": int(trial["seed"]),
        "status": status,
        "objective_value": None if objective is None else float(objective["objective_value"]),
        "base_hurdle_delta": None if objective is None else float(objective["base_hurdle_delta"]),
        "total_penalty": None if objective is None else float(objective["total_penalty"]),
        "penalty_one_sided_improvement": float(penalties.get("one_sided_improvement", 0.0)),
        "penalty_train_validation_gap": float(penalties.get("train_validation_gap", 0.0)),
        "penalty_horizon_instability": float(penalties.get("horizon_instability", 0.0)),
        "penalty_fold_instability": float(penalties.get("fold_instability", 0.0)),
        "penalty_complexity": float(penalties.get("complexity", 0.0)),
        "validation_pair_count": 0 if objective is None else int(objective["validation_pair_count"]),
        "lockbox_rows_used": 0,
        "training_time_seconds": round(training_seconds, 6),
        "inference_time_seconds": round(inference_seconds, 6),
        "total_time_seconds": round(total_seconds, 6),
        "prediction_path": prediction_path,
        "params_json": json.dumps(trial["params"], sort_keys=True),
        "failure_reason": failure_reason,
    }


def _sample_random_params(config: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name, spec in config["search_space"].items():
        params[name] = _sample_spec(spec, rng)
    return params


def _sample_local_params(config: dict[str, Any], base: dict[str, Any], rng: np.random.Generator) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name, spec in config["search_space"].items():
        low = float(spec["low"])
        high = float(spec["high"])
        center = float(base[name])
        radius = 0.15 * (high - low)
        if spec["type"] == "int":
            step = int(spec.get("step", 1))
            value = int(round(np.clip(rng.normal(center, radius / 2.0), low, high) / step) * step)
            params[name] = int(np.clip(value, int(low), int(high)))
        elif spec.get("log"):
            log_low = np.log(low)
            log_high = np.log(high)
            log_center = np.log(max(center, low))
            value = float(np.exp(np.clip(rng.normal(log_center, 0.15 * (log_high - log_low) / 2.0), log_low, log_high)))
            params[name] = value
        else:
            params[name] = float(np.clip(rng.normal(center, radius / 2.0), low, high))
    return params


def _sample_spec(spec: dict[str, Any], rng: np.random.Generator) -> int | float:
    low = float(spec["low"])
    high = float(spec["high"])
    if spec["type"] == "int":
        step = int(spec.get("step", 1))
        values = np.arange(int(low), int(high) + step, step)
        return int(rng.choice(values))
    if spec.get("log"):
        return float(np.exp(rng.uniform(np.log(low), np.log(high))))
    return float(rng.uniform(low, high))


def _suggest_optuna_params(trial: optuna.Trial, config: dict[str, Any]) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for name, spec in config["search_space"].items():
        if spec["type"] == "int":
            params[name] = trial.suggest_int(name, int(spec["low"]), int(spec["high"]), step=int(spec.get("step", 1)))
        else:
            params[name] = trial.suggest_float(name, float(spec["low"]), float(spec["high"]), log=bool(spec.get("log", False)))
    return params


def _resolved_xgboost_params(config: dict[str, Any], params: dict[str, Any], seed: int) -> dict[str, Any]:
    fixed = dict(config["fixed_xgboost_params"])
    fixed.pop("random_state_policy", None)
    fixed.update(params)
    fixed["random_state"] = seed
    fixed["verbosity"] = 0
    return fixed


def _complexity_proxy(params: dict[str, Any], config: dict[str, Any]) -> float:
    space = config["search_space"]
    n_score = (float(params["n_estimators"]) - float(space["n_estimators"]["low"])) / (float(space["n_estimators"]["high"]) - float(space["n_estimators"]["low"]))
    depth_score = (float(params["max_depth"]) - float(space["max_depth"]["low"])) / (float(space["max_depth"]["high"]) - float(space["max_depth"]["low"]))
    return 0.5 * n_score + 0.5 * depth_score


def _build_overfit_frontier(ledger: pd.DataFrame) -> pd.DataFrame:
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        return pd.DataFrame()
    completed["overfit_penalty_total"] = completed["penalty_train_validation_gap"].astype("float64") + completed["penalty_horizon_instability"].astype("float64") + completed["penalty_fold_instability"].astype("float64")
    completed["overfit_frontier_flag"] = completed["overfit_penalty_total"] > completed["overfit_penalty_total"].median()
    return completed[["trial_id", "phase_id", "objective_value", "base_hurdle_delta", "total_penalty", "overfit_penalty_total", "overfit_frontier_flag"]]


def _best_candidate_config(best: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    params = json.loads(best["params_json"])
    return {
        "artifact_type": "v1p0_stage22_best_development_candidate_config",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": "market_xgboost_v2_frozen_final_pending_stage23",
        "source_candidate_model_id": config["candidate_model_id"],
        "selected_trial_id": int(best["trial_id"]),
        "selected_phase_id": best["phase_id"],
        "selection_basis": "development_validation_guarded_hurdle_delta_only",
        "objective_value": float(best["objective_value"]),
        "search_config_digest_sha256": config["config_digest_sha256"],
        "params": params,
        "resolved_xgboost_params": _resolved_xgboost_params(config, params, int(best["seed"])),
        "lockbox_used_for_selection": False,
        "benchmark_claim": False,
        "non_claims": ["not_final_evaluation", "not_lockbox_result", "not_promotion_claim"],
    }


def _render_report(manifest: dict[str, Any]) -> str:
    best = manifest["best_development_trial"]
    return f"""# Stage 22 XGBoost Development Search Report

Status: {manifest['status']}; development-only search evidence

Updated: 2026-05-24

Run ID: `{manifest['run_id']}`

## Search Result

| Field | Value |
| --- | --- |
| Requested trials | {manifest['requested_trial_count']} |
| Completed trials | {manifest['trial_schema']['completed_trial_count']} |
| Failed trials | {manifest['trial_schema']['failed_trial_count']} |
| Best development trial | {best['trial_id']} |
| Best objective value | {best['objective_value']} |
| Base hurdle delta | {best['base_hurdle_delta']} |
| Total penalty | {best['total_penalty']} |

## Lockbox Policy

No lockbox rows, predictions, or metrics were used for search, local refinement, or candidate selection. Stage 23 owns frozen final evaluation.

## Artifacts

| Artifact | Path |
| --- | --- |
| Trial ledger | `{manifest['outputs']['trial_ledger_parquet']}` |
| Fold metrics | `{manifest['outputs']['trial_fold_metrics_parquet']}` |
| Prediction index | `{manifest['outputs']['trial_prediction_index_parquet']}` |
| Trial predictions | `{manifest['outputs']['trial_prediction_root']}` |
| Overfit frontier | `{manifest['outputs']['overfit_frontier']}` |
| Best development config | `{manifest['outputs']['best_development_candidate_config']}` |

## Non-Claims

The best development-search score is not a final benchmark improvement claim, not a lockbox result, not a promotion claim, not Stage 6 reinterpretation, and not a trading signal.
"""


def _completed_trial_ids(ledger_path: Path) -> set[int]:
    if not ledger_path.exists():
        return set()
    return {int(row["trial_id"]) for row in _iter_jsonl(ledger_path) if row.get("status") in {"completed", "failed"}}


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
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


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
