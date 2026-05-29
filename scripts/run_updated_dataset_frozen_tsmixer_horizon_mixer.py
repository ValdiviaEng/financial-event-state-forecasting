from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import optuna
import pandas as pd
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    HORIZON_WEIGHTS,
    ROW_KEY,
    compute_pairwise_deltas,
    sha256_file,
    stable_digest,
)


RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
UPDATED_XGBOOST_ROOT = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__20260528T100000Z__src_6dff1bd__run_40f1c9a0"
FROZEN_TSMIXER_ROOT = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage44__tsmixer_training__20260528T120000Z__src_6dff1bd__run_6817ae4c"
STALE_STAGE45_ROOT = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage45__market_xgb_tsmixer_meta__20260528T150000Z__src_6dff1bd__run_5a3a14f8"

SOURCE_ID = "6dff1bd"
DEFAULT_TRIAL_COUNT = 800
DEFAULT_PREFLIGHT_TRIALS = 25
MODEL_ID = "updated_av_xgb_frozen_tsmixer_horizon_mixer_v1"
UPDATED_XGBOOST_MODEL_ID = "updated_av_xgboost_event_market_optuna_v1"
FROZEN_TSMIXER_MODEL_ID = "updated_av_tsmixer_event_market_optuna_v1_seed_mean"
BASE_FEATURE_COLUMNS = ["xgboost_prediction", "tsmixer_prediction"]
HORIZON_ORDER = tuple(HORIZON_WEIGHTS.keys())
MIXER_MODES = ("xgboost_only", "tsmixer_only", "convex_blend", "ridge", "elastic_net")


def frozen_tsmixer_horizon_mixer_contract(trial_count: int = DEFAULT_TRIAL_COUNT) -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_frozen_tsmixer_horizon_mixer_contract",
        "model_id": MODEL_ID,
        "xgboost_model_id": UPDATED_XGBOOST_MODEL_ID,
        "frozen_tsmixer_model_id": FROZEN_TSMIXER_MODEL_ID,
        "trial_count": int(trial_count),
        "minimum_required_trials": 800,
        "model_family": "horizon_specific_frozen_base_mixer",
        "base_features": BASE_FEATURE_COLUMNS,
        "base_model_policy": {
            "xgboost": "stage43_updated_xgboost_current_valid_evidence",
            "tsmixer": "current_frozen_stage44_best_trial_diagnostic_input_only",
            "tsmixer_direct_tuning_allowed": False,
            "tsmixer_retraining_allowed": False,
            "tsmixer_architecture_status": "stale_mean_pooling_readout_not_corrected",
            "owner_override": "2026-05-29_use_current_best_tsmixer_no_direct_tuning",
        },
        "meta_training_policy": {
            "per_fold_horizon_model": True,
            "training_split": "train_only",
            "selection_split": "validation",
            "lockbox_rows_used_for_tuning": 0,
            "final_lockbox_evaluation": "post_selection_only",
            "can_select_xgboost_only_per_horizon": True,
            "can_select_tsmixer_weight_by_horizon": True,
        },
        "search_space": {
            "mode_by_horizon": {"type": "categorical", "choices": list(MIXER_MODES), "horizons": list(HORIZON_ORDER)},
            "blend_tsmixer_weight_by_horizon": {"type": "float", "low": 0.0, "high": 1.0, "horizons": list(HORIZON_ORDER)},
            "alpha_by_horizon": {"type": "log_float", "low": 1e-6, "high": 10.0, "horizons": list(HORIZON_ORDER)},
            "l1_ratio_by_horizon": {"type": "float", "low": 0.05, "high": 0.95, "horizons": list(HORIZON_ORDER)},
            "fit_intercept_by_horizon": {"type": "categorical", "choices": [True, False], "horizons": list(HORIZON_ORDER)},
            "positive_coefficients_by_horizon": {"type": "categorical", "choices": [False, True], "horizons": list(HORIZON_ORDER)},
        },
        "selection_objective": {
            "name": "validation_weighted_delta_vs_updated_xgboost_with_xgboost_only_floor",
            "baseline_model_id": UPDATED_XGBOOST_MODEL_ID,
            "horizon_weights": HORIZON_WEIGHTS,
            "metric_weights": {"rmse": 0.5, "mae": 0.5},
            "lower_is_better": True,
            "lockbox_policy": "no_lockbox_rows_or_metrics_used_for_trial_selection",
        },
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": [
            "frozen_current_tsmixer_diagnostic_input_only",
            "no_tsmixer_training_or_tuning_executed",
            "development_tuning_uses_train_validation_only",
            "lockbox_not_used_for_tuning_or_selection",
            "final_lockbox_evaluation_is_post_selection_evidence",
            "not_positive_benchmark_claim",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Tune a horizon-specific mixer over Stage 43 XGBoost and the current frozen Stage 44 TSMixer predictions without TSMixer retraining.")
    parser.add_argument("--xgboost-predictions", type=Path, default=STALE_STAGE45_ROOT / "xgboost_best_all_split_predictions.parquet")
    parser.add_argument("--xgboost-metrics", type=Path, default=STALE_STAGE45_ROOT / "xgboost_best_all_split_metrics.parquet")
    parser.add_argument("--frozen-tsmixer-root", type=Path, default=FROZEN_TSMIXER_ROOT)
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--preflight-trials", type=int, default=DEFAULT_PREFLIGHT_TRIALS)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()
    if args.trial_count < DEFAULT_TRIAL_COUNT:
        raise RuntimeError("final frozen-TSMixer horizon mixer requires at least 800 meta/mixer trials")

    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    generated_token = generated_at.strftime("%Y%m%dT%H%M%SZ")
    contract = frozen_tsmixer_horizon_mixer_contract(args.trial_count)
    contract["generated_at_utc"] = generated_at.isoformat().replace("+00:00", "Z")
    contract["xgboost_predictions"] = _rel(args.xgboost_predictions.resolve())
    contract["xgboost_metrics"] = _rel(args.xgboost_metrics.resolve())
    contract["frozen_tsmixer_root"] = _rel(args.frozen_tsmixer_root.resolve())
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_updated_av__stage48__frozen_tsmixer_horizon_mixer__{generated_token}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root.resolve() if args.output_root else RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)
    _write_json(output_root / "frozen_tsmixer_horizon_mixer_contract.json", contract)

    prep_started = time.perf_counter()
    xgboost_predictions = pd.read_parquet(args.xgboost_predictions)
    xgboost_metrics = pd.read_parquet(args.xgboost_metrics)
    tsmixer_predictions, tsmixer_metrics, tsmixer_evidence = _load_frozen_tsmixer(args.frozen_tsmixer_root)
    meta_frame = _build_meta_frame(xgboost_predictions, tsmixer_predictions)
    prep_seconds = time.perf_counter() - prep_started

    if args.preflight_only:
        preflight = _run_preflight(meta_frame, xgboost_metrics, contract, int(args.preflight_trials), prep_seconds)
        preflight_path = output_root / "preflight_timing_summary.json"
        _write_json(preflight_path, preflight)
        print(json.dumps({"status": "preflight_completed", "preflight": preflight, "preflight_summary": _rel(preflight_path)}, sort_keys=True))
        return

    result = _run_full_mixer_tuning(output_root, meta_frame, xgboost_metrics, tsmixer_metrics, tsmixer_evidence, contract, generated_at, run_id)
    print(json.dumps({"status": result["status"], "trial_count_completed": result["trial_count_completed"], "best_trial_number": result["best_trial"]["trial_number"], "manifest": result["manifest"]}, sort_keys=True))


def _load_frozen_tsmixer(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    predictions_path = root / "best_tsmixer_predictions.parquet"
    metrics_path = root / "best_tsmixer_metrics.parquet"
    fit_path = root / "best_tsmixer_fit_manifest.parquet"
    ledger_path = root / "trial_ledger.ndjson"
    if not predictions_path.exists() or not metrics_path.exists():
        raise RuntimeError(f"missing frozen TSMixer predictions/metrics under {root}")
    predictions = pd.read_parquet(predictions_path)
    metrics = pd.read_parquet(metrics_path)
    fit_columns = list(pd.read_parquet(fit_path).columns) if fit_path.exists() else []
    completed = _read_jsonl_frame(ledger_path)
    completed = completed[completed.get("status", pd.Series(dtype=str)) == "completed"].copy() if not completed.empty else pd.DataFrame()
    best_trial = None
    if not completed.empty:
        best_trial = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()
    evidence = {
        "root": _rel(root.resolve()),
        "predictions": _rel(predictions_path.resolve()),
        "metrics": _rel(metrics_path.resolve()),
        "fit_manifest": _rel(fit_path.resolve()) if fit_path.exists() else None,
        "trial_ledger": _rel(ledger_path.resolve()) if ledger_path.exists() else None,
        "trial_count_completed": int(len(completed)),
        "best_trial_number": None if best_trial is None else int(best_trial["trial_number"]),
        "best_objective_value": None if best_trial is None else float(best_trial["objective_value"]),
        "architecture_status": "stale_mean_pooling_readout_not_corrected",
        "fit_manifest_has_corrected_architecture_columns": "architecture_version" in fit_columns and "readout_policy" in fit_columns,
        "direct_tsmixer_tuning_executed_in_this_stage": False,
    }
    return predictions[predictions["model_id"] == FROZEN_TSMIXER_MODEL_ID].copy(), metrics[metrics["model_id"] == FROZEN_TSMIXER_MODEL_ID].copy(), evidence


def _build_meta_frame(xgboost_predictions: pd.DataFrame, tsmixer_predictions: pd.DataFrame) -> pd.DataFrame:
    keys = ["row_key", *ROW_KEY, "fold_id", "split_role", "target"]
    xgb = xgboost_predictions[xgboost_predictions["model_id"] == UPDATED_XGBOOST_MODEL_ID][keys + ["prediction"]].rename(columns={"prediction": "xgboost_prediction"})
    tsm = tsmixer_predictions[keys + ["prediction"]].rename(columns={"prediction": "tsmixer_prediction"})
    frame = xgb.merge(tsm, on=keys, how="inner", validate="one_to_one")
    if set(frame["split_role"].unique()) != {"train", "validation", "lockbox"}:
        raise RuntimeError(f"meta frame split roles incomplete: {sorted(frame['split_role'].unique())}")
    return frame


def _run_preflight(meta_frame: pd.DataFrame, xgboost_metrics: pd.DataFrame, contract: dict[str, Any], preflight_trials: int, prep_seconds: float) -> dict[str, Any]:
    sampler = optuna.samplers.TPESampler(seed=2026054801, n_startup_trials=min(10, int(preflight_trials)), multivariate=True)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    durations: list[float] = []

    def objective(trial: optuna.Trial) -> float:
        started = time.perf_counter()
        config = _suggest_mixer_config(trial)
        _, metrics, _ = _fit_mixer_config(meta_frame, config, int(trial.number), split_roles=("train", "validation"), save_predictions=False)
        summary = _summarize_trial(metrics, xgboost_metrics)
        durations.append(time.perf_counter() - started)
        return float(summary["objective_value"])

    study.enqueue_trial(_xgboost_only_params())
    study.optimize(objective, n_trials=int(preflight_trials), show_progress_bar=False)
    median_seconds = float(np.median(durations)) if durations else float("inf")
    estimate_seconds = median_seconds * int(contract["trial_count"])
    return {
        "status": "completed",
        "preflight_trials": int(preflight_trials),
        "trial_count_for_full_run": int(contract["trial_count"]),
        "base_prediction_preparation_seconds": round(float(prep_seconds), 3),
        "median_seconds_per_mixer_trial": round(median_seconds, 6),
        "estimated_full_mixer_tuning_seconds": round(float(estimate_seconds), 3),
        "estimated_full_mixer_tuning_minutes": round(float(estimate_seconds) / 60.0, 3),
        "under_one_hour": bool(estimate_seconds < 3600.0),
        "best_preflight_value": float(study.best_value),
        "lockbox_rows_used_for_tuning": 0,
        "tsmixer_training_or_tuning_executed": False,
    }


def _run_full_mixer_tuning(output_root: Path, meta_frame: pd.DataFrame, xgboost_metrics: pd.DataFrame, tsmixer_metrics: pd.DataFrame, tsmixer_evidence: dict[str, Any], contract: dict[str, Any], generated_at: datetime, run_id: str) -> dict[str, Any]:
    ledger_jsonl_path = output_root / "mixer_trial_ledger.ndjson"
    metrics_jsonl_path = output_root / "mixer_trial_fold_metrics.ndjson"
    coefficients_jsonl_path = output_root / "mixer_trial_coefficients.ndjson"
    storage_path = output_root / "optuna_study.sqlite3"
    sampler = optuna.samplers.TPESampler(seed=2026054801, n_startup_trials=80, multivariate=True)
    study = optuna.create_study(study_name="updated_av_frozen_tsmixer_horizon_mixer_800", direction="minimize", sampler=sampler, storage=f"sqlite:///{storage_path}", load_if_exists=True)
    if not ledger_jsonl_path.exists():
        for params in _seed_trials():
            study.enqueue_trial(params)
    completed_ids = _completed_trial_ids(ledger_jsonl_path)

    def objective(trial: optuna.Trial) -> float:
        trial_number = int(trial.number)
        if trial_number in completed_ids:
            prior = _read_trial_record(ledger_jsonl_path, trial_number)
            if prior and prior.get("status") == "completed":
                return float(prior["objective_value"])
        config = _suggest_mixer_config(trial)
        started = time.perf_counter()
        try:
            _, metrics, coefficients = _fit_mixer_config(meta_frame, config, trial_number, split_roles=("train", "validation"), save_predictions=False)
            summary = _summarize_trial(metrics, xgboost_metrics)
            ledger = {"trial_number": trial_number, "status": "completed", "runtime_seconds": round(time.perf_counter() - started, 6), "params_json": json.dumps(config, sort_keys=True), **summary}
        except Exception as exc:  # noqa: BLE001 - failed trials are recorded evidence.
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
        raise RuntimeError("frozen-TSMixer horizon mixer produced no completed trials")
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()
    best_config = json.loads(str(best["params_json"]))
    final_predictions, final_metrics, final_coefficients = _fit_mixer_config(meta_frame, best_config, int(best["trial_number"]), split_roles=("train", "validation", "lockbox"), save_predictions=True)
    comparison_summary, horizon_deltas, model_summary = _build_comparison_outputs(final_metrics, xgboost_metrics, tsmixer_metrics)

    ledger_path = output_root / "mixer_trial_ledger.parquet"
    metrics_path = output_root / "mixer_trial_fold_metrics.parquet"
    coefficients_path = output_root / "mixer_trial_coefficients.parquet"
    final_predictions_path = output_root / "best_mixer_predictions.parquet"
    final_metrics_path = output_root / "best_mixer_metrics.parquet"
    final_coefficients_path = output_root / "best_mixer_coefficients.parquet"
    horizon_deltas_path = output_root / "horizon_metric_deltas.parquet"
    model_summary_path = output_root / "model_split_summary.parquet"
    comparison_json_path = output_root / "comparison_summary.json"
    report_md_path = output_root / "stage48_frozen_tsmixer_horizon_mixer_report.md"
    report_html_path = output_root / "stage48_frozen_tsmixer_horizon_mixer_report.html"
    manifest_path = output_root / "frozen_tsmixer_horizon_mixer_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    weighted_delta_svg_path = output_root / "weighted_delta_by_split.svg"
    horizon_delta_svg_path = output_root / "lockbox_horizon_delta_vs_xgboost.svg"
    weight_svg_path = output_root / "mixer_weights_by_horizon.svg"

    ledger.to_parquet(ledger_path, index=False)
    _read_jsonl_frame(metrics_jsonl_path).to_parquet(metrics_path, index=False)
    _read_jsonl_frame(coefficients_jsonl_path).to_parquet(coefficients_path, index=False)
    final_predictions.to_parquet(final_predictions_path, index=False)
    final_metrics.to_parquet(final_metrics_path, index=False)
    final_coefficients.to_parquet(final_coefficients_path, index=False)
    horizon_deltas.to_parquet(horizon_deltas_path, index=False)
    model_summary.to_parquet(model_summary_path, index=False)
    _write_json(comparison_json_path, comparison_summary)
    weighted_delta_svg_path.write_text(_weighted_delta_svg(comparison_summary), encoding="utf-8")
    horizon_delta_svg_path.write_text(_horizon_delta_svg(horizon_deltas), encoding="utf-8")
    weight_svg_path.write_text(_weight_svg(final_coefficients), encoding="utf-8")

    manifest = {
        "artifact_type": "updated_dataset_frozen_tsmixer_horizon_mixer_manifest",
        "artifact_id": f"updated_dataset_frozen_tsmixer_horizon_mixer__{sha256_file(ledger_path)[:12]}__{generated_at.strftime('%Y%m%dT%H%M%SZ')}",
        "generated_at_utc": generated_at.isoformat().replace("+00:00", "Z"),
        "run_id": run_id,
        "status": "completed" if int((ledger["status"] == "completed").sum()) >= int(contract["trial_count"]) else "partial",
        "model_id": MODEL_ID,
        "xgboost_model_id": UPDATED_XGBOOST_MODEL_ID,
        "frozen_tsmixer_model_id": FROZEN_TSMIXER_MODEL_ID,
        "frozen_tsmixer_evidence": tsmixer_evidence,
        "trial_count_requested": int(contract["trial_count"]),
        "trial_count_completed": int((ledger["status"] == "completed").sum()),
        "trial_count_failed": int((ledger["status"] == "failed").sum()),
        "best_trial": {**best, "params": best_config},
        "comparison_summary": comparison_summary,
        "lockbox_rows_used_for_tuning": 0,
        "tsmixer_training_or_tuning_executed": False,
        "outputs": {
            "contract": _rel(output_root / "frozen_tsmixer_horizon_mixer_contract.json"),
            "trial_ledger_ndjson": _rel(ledger_jsonl_path),
            "trial_ledger": _rel(ledger_path),
            "trial_fold_metrics_ndjson": _rel(metrics_jsonl_path),
            "trial_fold_metrics": _rel(metrics_path),
            "trial_coefficients_ndjson": _rel(coefficients_jsonl_path),
            "trial_coefficients": _rel(coefficients_path),
            "best_mixer_predictions": _rel(final_predictions_path),
            "best_mixer_metrics": _rel(final_metrics_path),
            "best_mixer_coefficients": _rel(final_coefficients_path),
            "horizon_metric_deltas": _rel(horizon_deltas_path),
            "model_split_summary": _rel(model_summary_path),
            "comparison_json": _rel(comparison_json_path),
            "weighted_delta_by_split_svg": _rel(weighted_delta_svg_path),
            "lockbox_horizon_delta_vs_xgboost_svg": _rel(horizon_delta_svg_path),
            "mixer_weights_by_horizon_svg": _rel(weight_svg_path),
            "report_markdown": _rel(report_md_path),
            "report_html": _rel(report_html_path),
            "optuna_storage": _rel(storage_path),
            "manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
        },
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": contract["non_claims"],
    }
    _write_json(manifest_path, manifest)
    _write_json(run_manifest_path, {"stage": 48, "stage_name": "frozen_tsmixer_horizon_mixer", "status": manifest["status"], "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_md_path.write_text(_render_markdown_report(manifest, horizon_deltas, model_summary), encoding="utf-8")
    report_html_path.write_text(_render_html_report(manifest, horizon_deltas, model_summary), encoding="utf-8")
    return {"status": manifest["status"], "trial_count_completed": manifest["trial_count_completed"], "best_trial": manifest["best_trial"], "manifest": manifest["outputs"]["manifest"]}


def _suggest_mixer_config(trial: optuna.Trial) -> dict[str, Any]:
    config = {"mode_by_horizon": {}, "blend_tsmixer_weight_by_horizon": {}, "alpha_by_horizon": {}, "l1_ratio_by_horizon": {}, "fit_intercept_by_horizon": {}, "positive_coefficients_by_horizon": {}}
    for horizon_id in HORIZON_ORDER:
        config["mode_by_horizon"][horizon_id] = trial.suggest_categorical(f"mode_{horizon_id}", list(MIXER_MODES))
        config["blend_tsmixer_weight_by_horizon"][horizon_id] = float(trial.suggest_float(f"blend_tsmixer_weight_{horizon_id}", 0.0, 1.0))
        config["alpha_by_horizon"][horizon_id] = float(trial.suggest_float(f"alpha_{horizon_id}", 1e-6, 10.0, log=True))
        config["l1_ratio_by_horizon"][horizon_id] = float(trial.suggest_float(f"l1_ratio_{horizon_id}", 0.05, 0.95))
        config["fit_intercept_by_horizon"][horizon_id] = bool(trial.suggest_categorical(f"fit_intercept_{horizon_id}", [True, False]))
        config["positive_coefficients_by_horizon"][horizon_id] = bool(trial.suggest_categorical(f"positive_coefficients_{horizon_id}", [False, True]))
    return config


def _fit_mixer_config(meta_frame: pd.DataFrame, config: dict[str, Any], trial_number: int, *, split_roles: tuple[str, ...], save_predictions: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, Any]] = []
    coefficient_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    for (fold_id, horizon_id), group in meta_frame.groupby(["fold_id", "horizon_id"], sort=True):
        mode = str(config["mode_by_horizon"][horizon_id])
        train = group[group["split_role"] == "train"].copy()
        if train.empty:
            continue
        fit_started = time.perf_counter()
        estimator: Any | None = None
        scaler: StandardScaler | None = None
        raw_xgb_weight = 1.0
        raw_tsmixer_weight = 0.0
        raw_intercept = 0.0
        if mode == "xgboost_only":
            pass
        elif mode == "tsmixer_only":
            raw_xgb_weight = 0.0
            raw_tsmixer_weight = 1.0
        elif mode == "convex_blend":
            raw_tsmixer_weight = float(config["blend_tsmixer_weight_by_horizon"][horizon_id])
            raw_xgb_weight = 1.0 - raw_tsmixer_weight
        else:
            scaler = StandardScaler().fit(train[BASE_FEATURE_COLUMNS].astype("float64"))
            x_train = scaler.transform(train[BASE_FEATURE_COLUMNS].astype("float64"))
            y_train = train["target"].astype("float64").to_numpy()
            alpha = float(config["alpha_by_horizon"][horizon_id])
            if mode == "ridge":
                estimator = Ridge(alpha=alpha, fit_intercept=bool(config["fit_intercept_by_horizon"][horizon_id]), positive=bool(config["positive_coefficients_by_horizon"][horizon_id]))
            elif mode == "elastic_net":
                estimator = ElasticNet(alpha=alpha, l1_ratio=float(config["l1_ratio_by_horizon"][horizon_id]), fit_intercept=bool(config["fit_intercept_by_horizon"][horizon_id]), positive=bool(config["positive_coefficients_by_horizon"][horizon_id]), max_iter=10000, random_state=2026054801)
            else:
                raise RuntimeError(f"unsupported mixer mode: {mode}")
            estimator.fit(x_train, y_train)
            raw_coefficients, raw_intercept = _raw_coefficients(estimator, scaler)
            raw_xgb_weight = float(raw_coefficients[0])
            raw_tsmixer_weight = float(raw_coefficients[1])
        coefficient_rows.append({
            "trial_number": int(trial_number),
            "model_id": MODEL_ID,
            "fold_id": fold_id,
            "horizon_id": horizon_id,
            "mode": mode,
            "raw_intercept": float(raw_intercept),
            "raw_xgboost_weight": float(raw_xgb_weight),
            "raw_tsmixer_weight": float(raw_tsmixer_weight),
            "alpha": float(config["alpha_by_horizon"][horizon_id]),
            "l1_ratio": float(config["l1_ratio_by_horizon"][horizon_id]),
            "fit_intercept": bool(config["fit_intercept_by_horizon"][horizon_id]),
            "positive_coefficients": bool(config["positive_coefficients_by_horizon"][horizon_id]),
            "train_rows": int(len(train)),
            "training_seconds": round(time.perf_counter() - fit_started, 6),
            "lockbox_rows_used_for_tuning": 0,
        })
        for split_role in split_roles:
            split = group[group["split_role"] == split_role].copy()
            if split.empty:
                continue
            prediction = _predict_split(split, mode, raw_xgb_weight, raw_tsmixer_weight, raw_intercept, estimator, scaler)
            metric_rows.append(_metric_row(trial_number, split_role, fold_id, horizon_id, MODEL_ID, split["target"].to_numpy(dtype="float64"), prediction))
            if save_predictions:
                output = split[["row_key", *ROW_KEY, "fold_id", "split_role", "target", *BASE_FEATURE_COLUMNS]].copy()
                output["trial_number"] = int(trial_number)
                output["model_id"] = MODEL_ID
                output["prediction"] = prediction
                output["mixer_mode"] = mode
                output["raw_xgboost_weight"] = float(raw_xgb_weight)
                output["raw_tsmixer_weight"] = float(raw_tsmixer_weight)
                prediction_frames.append(output)
    predictions = pd.concat(prediction_frames, ignore_index=True) if prediction_frames else pd.DataFrame()
    return predictions, pd.DataFrame.from_records(metric_rows), pd.DataFrame.from_records(coefficient_rows)


def _predict_split(split: pd.DataFrame, mode: str, xgb_weight: float, tsmixer_weight: float, intercept: float, estimator: Any | None, scaler: StandardScaler | None) -> np.ndarray:
    if mode in {"xgboost_only", "tsmixer_only", "convex_blend"}:
        return (float(intercept) + float(xgb_weight) * split["xgboost_prediction"].astype("float64") + float(tsmixer_weight) * split["tsmixer_prediction"].astype("float64")).to_numpy(dtype="float64")
    if estimator is None or scaler is None:
        raise RuntimeError("linear mixer missing estimator/scaler")
    return estimator.predict(scaler.transform(split[BASE_FEATURE_COLUMNS].astype("float64"))).astype("float64")


def _raw_coefficients(estimator: Any, scaler: StandardScaler) -> tuple[np.ndarray, float]:
    scale = scaler.scale_.astype("float64")
    mean = scaler.mean_.astype("float64")
    coef = np.asarray(estimator.coef_, dtype="float64") / scale
    intercept = float(getattr(estimator, "intercept_", 0.0)) - float(np.dot(coef, mean))
    return coef, intercept


def _summarize_trial(metrics: pd.DataFrame, xgboost_metrics: pd.DataFrame) -> dict[str, Any]:
    deltas = compute_pairwise_deltas(pd.concat([metrics, xgboost_metrics], ignore_index=True, sort=False), UPDATED_XGBOOST_MODEL_ID, [MODEL_ID])
    validation = deltas[deltas["split_role"] == "validation"].copy()
    train = deltas[deltas["split_role"] == "train"].copy()
    validation_weighted_delta = _weighted_delta(validation)
    train_weighted_delta = _weighted_delta(train)
    validation_rate = float(validation["both_metrics_improve"].mean()) if not validation.empty else 0.0
    train_rate = float(train["both_metrics_improve"].mean()) if not train.empty else 0.0
    objective_value = validation_weighted_delta + max(0.0, validation_weighted_delta) * 0.10
    return {
        "objective_value": float(objective_value),
        "validation_weighted_delta_vs_updated_xgboost": float(validation_weighted_delta),
        "train_weighted_delta_vs_updated_xgboost": float(train_weighted_delta),
        "validation_both_metric_improvement_rate_vs_updated_xgboost": validation_rate,
        "train_both_metric_improvement_rate_vs_updated_xgboost": train_rate,
        "lockbox_rows_used_for_tuning": 0,
    }


def _build_comparison_outputs(mixer_metrics: pd.DataFrame, xgboost_metrics: pd.DataFrame, tsmixer_metrics: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    comparisons = []
    horizon_frames = []
    for baseline_id, baseline_metrics in [(UPDATED_XGBOOST_MODEL_ID, xgboost_metrics), (FROZEN_TSMIXER_MODEL_ID, tsmixer_metrics)]:
        deltas = compute_pairwise_deltas(pd.concat([mixer_metrics, baseline_metrics], ignore_index=True, sort=False), baseline_id, [MODEL_ID])
        comparisons.append({"baseline_model_id": baseline_id, "candidate_model_id": MODEL_ID, "split_summaries": _split_delta_summary(deltas), "metric_summary": _comparison_metric_summary(mixer_metrics, baseline_metrics, baseline_id)})
        horizon = deltas.copy()
        horizon["baseline_model_id"] = baseline_id
        horizon_frames.append(horizon)
    summary = {"artifact_type": "updated_dataset_frozen_tsmixer_horizon_mixer_comparison_summary", "candidate_model_id": MODEL_ID, "comparisons": comparisons, "lockbox_used_for_tuning": False, "tsmixer_training_or_tuning_executed": False, "benchmark_claim": False, "positive_claim_approved": False}
    model_summary = pd.DataFrame.from_records([row for comparison in comparisons for row in comparison["metric_summary"]])
    return summary, pd.concat(horizon_frames, ignore_index=True), model_summary


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
    error = prediction.astype("float64") - target.astype("float64")
    denominator = float(np.sum(target.astype("float64") ** 2))
    return {"trial_number": int(trial_number), "split_role": split_role, "fold_id": fold_id, "horizon_id": horizon_id, "model_id": model_id, "row_count": int(len(target)), "rmse": float(np.sqrt(np.mean(error**2))), "mae": float(np.mean(np.abs(error))), "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - float(np.sum(error**2)) / denominator, "lockbox_rows_used_for_tuning": 0}


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


def _seed_trials() -> list[dict[str, Any]]:
    trials = [_xgboost_only_params(), _tsmixer_only_params()]
    for weight in [0.10, 0.25, 0.50, 0.75]:
        trials.append(_convex_params({h: weight for h in HORIZON_ORDER}))
    trials.append(_convex_params({"1d": 0.0, "5d": 0.0, "10d": 0.0, "20d": 0.25, "60d": 0.75}))
    return trials


def _xgboost_only_params() -> dict[str, Any]:
    return _mode_params("xgboost_only")


def _tsmixer_only_params() -> dict[str, Any]:
    return _mode_params("tsmixer_only")


def _mode_params(mode: str) -> dict[str, Any]:
    params: dict[str, Any] = {}
    for horizon_id in HORIZON_ORDER:
        params[f"mode_{horizon_id}"] = mode
        params[f"blend_tsmixer_weight_{horizon_id}"] = 0.0 if mode == "xgboost_only" else 1.0
        params[f"alpha_{horizon_id}"] = 0.01
        params[f"l1_ratio_{horizon_id}"] = 0.5
        params[f"fit_intercept_{horizon_id}"] = True
        params[f"positive_coefficients_{horizon_id}"] = False
    return params


def _convex_params(weights: dict[str, float]) -> dict[str, Any]:
    params = _mode_params("convex_blend")
    for horizon_id, weight in weights.items():
        params[f"blend_tsmixer_weight_{horizon_id}"] = float(weight)
    return params


def _weighted_delta_svg(summary: dict[str, Any]) -> str:
    rows = []
    for comparison in summary["comparisons"]:
        baseline = comparison["baseline_model_id"]
        for split in ["validation", "lockbox"]:
            value = float(comparison["split_summaries"][split]["weighted_delta_candidate_minus_baseline"])
            rows.append((f"{split} vs {baseline}", value))
    return _bar_svg("Weighted Delta Candidate Minus Baseline", rows, lower_is_better=True)


def _horizon_delta_svg(horizon_deltas: pd.DataFrame) -> str:
    rows = []
    split = horizon_deltas[(horizon_deltas["split_role"] == "lockbox") & (horizon_deltas["baseline_model_id"] == UPDATED_XGBOOST_MODEL_ID)]
    for horizon_id in HORIZON_ORDER:
        group = split[split["horizon_id"] == horizon_id]
        if group.empty:
            continue
        value = float((0.5 * group["rmse_delta_candidate_minus_baseline"] + 0.5 * group["mae_delta_candidate_minus_baseline"]).mean())
        rows.append((horizon_id, value))
    return _bar_svg("Lockbox Horizon Delta Vs XGBoost", rows, lower_is_better=True)


def _weight_svg(coefficients: pd.DataFrame) -> str:
    rows = []
    for horizon_id in HORIZON_ORDER:
        group = coefficients[coefficients["horizon_id"] == horizon_id]
        if group.empty:
            continue
        rows.append((f"{horizon_id} TSMixer", float(group["raw_tsmixer_weight"].mean())))
    return _bar_svg("Average Selected Raw TSMixer Weight", rows, lower_is_better=False)


def _bar_svg(title: str, rows: list[tuple[str, float]], *, lower_is_better: bool) -> str:
    width = 920
    row_height = 30
    height = 80 + row_height * max(1, len(rows))
    max_abs = max([abs(value) for _, value in rows] + [1e-9])
    zero_x = 460
    scale = 360 / max_abs
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="20" y="28" font-family="Arial" font-size="18" font-weight="700">{_escape(title)}</text>', f'<line x1="{zero_x}" y1="50" x2="{zero_x}" y2="{height - 20}" stroke="#555" stroke-width="1"/>']
    for index, (label, value) in enumerate(rows):
        y = 62 + index * row_height
        color = "#2f855a" if (value < 0 if lower_is_better else value > 0) else "#c53030"
        bar_width = abs(value) * scale
        x = zero_x if value >= 0 else zero_x - bar_width
        parts.append(f'<text x="20" y="{y + 14}" font-family="Arial" font-size="12">{_escape(label)}</text>')
        parts.append(f'<rect x="{x:.2f}" y="{y}" width="{bar_width:.2f}" height="18" fill="{color}" opacity="0.85"/>')
        parts.append(f'<text x="{zero_x + 380}" y="{y + 14}" font-family="Arial" font-size="12">{value:.8f}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _render_markdown_report(manifest: dict[str, Any], horizon_deltas: pd.DataFrame, model_summary: pd.DataFrame) -> str:
    comparison = manifest["comparison_summary"]["comparisons"][0]
    lines = ["# Stage 48 Frozen TSMixer Horizon Mixer", "", f"Status: `{manifest['status']}`", "", "## Key Result", "", f"Best trial: `{manifest['best_trial'].get('trial_number')}`", f"Validation weighted delta vs XGBoost: `{comparison['split_summaries']['validation']['weighted_delta_candidate_minus_baseline']}`", f"Lockbox weighted delta vs XGBoost: `{comparison['split_summaries']['lockbox']['weighted_delta_candidate_minus_baseline']}`", f"Lockbox both-metric improvement rate vs XGBoost: `{comparison['split_summaries']['lockbox']['both_metric_improvement_rate']}`", "", "## Evidence Boundary", "", "TSMixer was not retrained or tuned in this stage. The frozen current Stage 44 TSMixer artifact is used as a diagnostic base input under explicit owner override.", "", "## Outputs", ""]
    for key in ["best_mixer_predictions", "best_mixer_metrics", "best_mixer_coefficients", "horizon_metric_deltas", "model_split_summary", "weighted_delta_by_split_svg", "lockbox_horizon_delta_vs_xgboost_svg", "mixer_weights_by_horizon_svg"]:
        lines.append(f"- `{key}`: `{manifest['outputs'][key]}`")
    lines.extend(["", "## Non-Claims", "", "No positive benchmark claim, benchmark-comparability promotion, Stage 6 reinterpretation, live forecast, or trading output is approved.", ""])
    return "\n".join(lines)


def _render_html_report(manifest: dict[str, Any], horizon_deltas: pd.DataFrame, model_summary: pd.DataFrame) -> str:
    md = _render_markdown_report(manifest, horizon_deltas, model_summary)
    weighted_svg = Path(PROJECT_ROOT / manifest["outputs"]["weighted_delta_by_split_svg"]).read_text(encoding="utf-8")
    horizon_svg = Path(PROJECT_ROOT / manifest["outputs"]["lockbox_horizon_delta_vs_xgboost_svg"]).read_text(encoding="utf-8")
    weight_svg = Path(PROJECT_ROOT / manifest["outputs"]["mixer_weights_by_horizon_svg"]).read_text(encoding="utf-8")
    table = model_summary.to_html(index=False, escape=True)
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Stage 48 Frozen TSMixer Horizon Mixer</title><style>body{{font-family:Arial,sans-serif;margin:32px;line-height:1.45}} pre{{white-space:pre-wrap;background:#f7fafc;padding:16px}} table{{border-collapse:collapse;font-size:12px}} td,th{{border:1px solid #ddd;padding:4px 6px}}</style></head>
<body>
<h1>Stage 48 Frozen TSMixer Horizon Mixer</h1>
<p><strong>Status:</strong> {_escape(str(manifest['status']))}</p>
<p><strong>Evidence boundary:</strong> TSMixer was not retrained or tuned in this stage. Outputs are historical diagnostics, not trading advice or a positive benchmark claim.</p>
{weighted_svg}
{horizon_svg}
{weight_svg}
<h2>Model Split Summary</h2>
{table}
<h2>Markdown Source</h2>
<pre>{_escape(md)}</pre>
</body></html>"""


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


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
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                yield json.loads(stripped)


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
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if not isinstance(value, (dict, list, tuple, str, bytes)):
        try:
            if pd.isna(value):
                return None
        except TypeError:
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
