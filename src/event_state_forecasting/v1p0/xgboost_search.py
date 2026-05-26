from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

import numpy as np
import pandas as pd


class V1P0XGBoostSearchError(ValueError):
    """Raised when the v1p0 XGBoost search contract is malformed."""


REQUIRED_HORIZONS = ("1d", "5d", "10d", "20d", "60d")
OBJECTIVE_METRICS = ("rmse", "mae")
STAGE22_TRIAL_LEDGER_REQUIRED_COLUMNS = {
    "trial_id",
    "phase_id",
    "status",
    "objective_value",
    "base_hurdle_delta",
    "total_penalty",
    "lockbox_rows_used",
    "params_json",
    "failure_reason",
}
STAGE24_FRONTIER_REQUIRED_COLUMNS = {
    "trial_id",
    "phase_id",
    "objective_value",
    "n_estimators",
    "max_depth",
    "train_rmse_mean",
    "validation_rmse_mean",
    "validation_to_train_rmse_ratio",
}
STAGE25_PAIRED_LOSS_REQUIRED_COLUMNS = {
    "row_key",
    "canonical_ticker",
    "as_of_date",
    "horizon_id",
    "fold_id",
    "split_role",
    "target",
    "candidate_prediction",
    "hurdle_prediction",
    "candidate_squared_error",
    "hurdle_squared_error",
    "squared_error_delta_candidate_minus_hurdle",
    "candidate_absolute_error",
    "hurdle_absolute_error",
    "absolute_error_delta_candidate_minus_hurdle",
}


def canonical_search_digest(config: dict[str, Any]) -> str:
    encoded = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return sha256(encoded).hexdigest()


def validate_xgboost_search_config(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("schema_version") != "xgboost_search_v1p0_v1":
        raise V1P0XGBoostSearchError("search config must declare schema_version=xgboost_search_v1p0_v1")
    if config.get("implementation_version") != "v1p0":
        raise V1P0XGBoostSearchError("search config must declare implementation_version=v1p0")
    if config.get("candidate_model_id") != "market_xgboost_v2_nested_optuna_candidate":
        raise V1P0XGBoostSearchError("unexpected Stage 21 candidate model ID")
    if config.get("hurdle_model_id") != "market_xgboost_v1_fixed":
        raise V1P0XGBoostSearchError("Stage 21 hurdle model must be the fixed XGBoost baseline")

    allowed_roles = set(config.get("allowed_tuning_split_roles", []))
    forbidden_roles = set(config.get("forbidden_tuning_split_roles", []))
    if "lockbox" in allowed_roles or "lockbox" not in forbidden_roles:
        raise V1P0XGBoostSearchError("lockbox must be forbidden during search")

    objective = config.get("objective", {})
    if objective.get("selection_split_role") != "validation":
        raise V1P0XGBoostSearchError("objective selection role must be validation")
    if "lockbox" not in set(objective.get("forbidden_split_roles", [])):
        raise V1P0XGBoostSearchError("objective must explicitly forbid lockbox")

    _validate_weights(objective.get("horizon_weights", {}), REQUIRED_HORIZONS, "horizon_weights")
    _validate_weights(objective.get("metric_weights", {}), OBJECTIVE_METRICS, "metric_weights")

    budgets = config.get("budgets", {})
    phased_total = int(budgets.get("random_trials", 0)) + int(budgets.get("optuna_tpe_trials", 0)) + int(budgets.get("local_refinement_trials", 0))
    if phased_total != int(budgets.get("max_total_trials", -1)):
        raise V1P0XGBoostSearchError("trial budgets must sum to max_total_trials")
    if phased_total <= 0:
        raise V1P0XGBoostSearchError("trial budget must be positive")

    search_space = config.get("search_space", {})
    required_params = {"n_estimators", "max_depth", "learning_rate", "subsample", "colsample_bytree", "min_child_weight", "gamma", "reg_alpha", "reg_lambda"}
    if set(search_space) != required_params:
        raise V1P0XGBoostSearchError("search space parameters do not match the frozen Stage 21 set")
    for name, spec in search_space.items():
        _validate_param_spec(name, spec)

    result = dict(config)
    result["config_digest_sha256"] = canonical_search_digest(config)
    return result


def compute_guarded_hurdle_objective(
    metrics: pd.DataFrame,
    config: dict[str, Any],
    candidate_model_id: str | None = None,
    hurdle_model_id: str | None = None,
    trial_params: dict[str, float | int] | None = None,
) -> dict[str, Any]:
    validated = validate_xgboost_search_config(config)
    objective = validated["objective"]
    candidate_id = candidate_model_id or validated["candidate_model_id"]
    hurdle_id = hurdle_model_id or validated["hurdle_model_id"]
    selection_role = objective["selection_split_role"]
    train_role = objective["train_gap_split_role"]

    required_columns = {"split_role", "fold_id", "horizon_id", "model_id", *OBJECTIVE_METRICS}
    missing = required_columns.difference(metrics.columns)
    if missing:
        raise V1P0XGBoostSearchError(f"metrics missing required columns: {sorted(missing)}")

    working = metrics[metrics["split_role"].isin([selection_role, train_role])].copy()
    validation_pairs = _paired_validation_metrics(working, candidate_id, hurdle_id, selection_role)
    for metric in OBJECTIVE_METRICS:
        if not np.isfinite(validation_pairs[f"{metric}_candidate"]).all() or not np.isfinite(validation_pairs[f"{metric}_hurdle"]).all():
            raise V1P0XGBoostSearchError("objective metrics must be finite")
        validation_pairs[f"{metric}_delta"] = validation_pairs[f"{metric}_candidate"] - validation_pairs[f"{metric}_hurdle"]

    metric_weights = objective["metric_weights"]
    horizon_weights = objective["horizon_weights"]
    validation_pairs["composite_delta"] = sum(float(metric_weights[metric]) * validation_pairs[f"{metric}_delta"] for metric in OBJECTIVE_METRICS)
    horizon_delta = validation_pairs.groupby("horizon_id", sort=True)["composite_delta"].mean()
    missing_horizons = set(REQUIRED_HORIZONS).difference(horizon_delta.index)
    if missing_horizons:
        raise V1P0XGBoostSearchError(f"objective missing horizons: {sorted(missing_horizons)}")

    base_objective = _weighted_mean(horizon_delta.to_dict(), horizon_weights)
    penalties = _objective_penalties(validation_pairs, working, objective, candidate_id, train_role, selection_role, trial_params or {})
    total_penalty = float(sum(penalties.values()))
    total_objective = float(base_objective + total_penalty)
    return {
        "objective_id": objective["objective_id"],
        "direction": objective["direction"],
        "candidate_model_id": candidate_id,
        "hurdle_model_id": hurdle_id,
        "selection_split_role": selection_role,
        "lockbox_rows_used": 0,
        "validation_pair_count": int(len(validation_pairs)),
        "base_hurdle_delta": float(base_objective),
        "penalties": penalties,
        "total_penalty": total_penalty,
        "objective_value": total_objective,
        "horizon_composite_deltas": {str(k): float(v) for k, v in horizon_delta.to_dict().items()},
        "config_digest_sha256": validated["config_digest_sha256"],
    }


def validate_stage22_trial_ledger_schema(ledger: pd.DataFrame) -> dict[str, Any]:
    missing = STAGE22_TRIAL_LEDGER_REQUIRED_COLUMNS.difference(ledger.columns)
    if missing:
        raise V1P0XGBoostSearchError(f"trial ledger missing required columns: {sorted(missing)}")
    allowed_statuses = {"completed", "failed"}
    statuses = set(ledger["status"].astype(str))
    if not statuses.issubset(allowed_statuses):
        raise V1P0XGBoostSearchError(f"trial ledger has unsupported statuses: {sorted(statuses - allowed_statuses)}")
    if not (ledger["lockbox_rows_used"].fillna(0).astype("int64") == 0).all():
        raise V1P0XGBoostSearchError("Stage 22 trial ledger must not record lockbox usage")
    completed = ledger[ledger["status"] == "completed"]
    if not np.isfinite(completed["objective_value"].astype("float64")).all():
        raise V1P0XGBoostSearchError("completed Stage 22 trials must have finite objective values")
    failed = ledger[ledger["status"] == "failed"]
    if not failed.empty and failed["failure_reason"].fillna("").eq("").any():
        raise V1P0XGBoostSearchError("failed Stage 22 trials must record failure_reason")
    return {"trial_count": int(len(ledger)), "completed_trial_count": int(len(completed)), "failed_trial_count": int(len(failed))}


def validate_stage22_prediction_schema(predictions: pd.DataFrame) -> dict[str, Any]:
    required = {"trial_id", "fold_id", "horizon_id", "split_role", "row_key", "prediction", "target"}
    missing = required.difference(predictions.columns)
    if missing:
        raise V1P0XGBoostSearchError(f"trial predictions missing required columns: {sorted(missing)}")
    split_roles = set(predictions["split_role"].astype(str))
    if split_roles != {"validation"}:
        raise V1P0XGBoostSearchError("Stage 22 saved trial predictions must be validation-only")
    if not np.isfinite(predictions[["prediction", "target"]].astype("float64").to_numpy()).all():
        raise V1P0XGBoostSearchError("Stage 22 saved trial predictions must be finite")
    return {"prediction_rows": int(len(predictions)), "trial_count": int(predictions["trial_id"].nunique())}


def select_best_stage22_trial(ledger: pd.DataFrame) -> dict[str, Any]:
    validate_stage22_trial_ledger_schema(ledger)
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        raise V1P0XGBoostSearchError("cannot select best trial from an empty completed ledger")
    completed["objective_value"] = completed["objective_value"].astype("float64")
    completed = completed.sort_values(["objective_value", "trial_id"], ascending=[True, True])
    best = completed.iloc[0].to_dict()
    best["trial_id"] = int(best["trial_id"])
    best["objective_value"] = float(best["objective_value"])
    return best


def validate_stage24_frontier_schema(frontier: pd.DataFrame) -> dict[str, Any]:
    missing = STAGE24_FRONTIER_REQUIRED_COLUMNS.difference(frontier.columns)
    if missing:
        raise V1P0XGBoostSearchError(f"overfit frontier missing required columns: {sorted(missing)}")
    if frontier.empty:
        raise V1P0XGBoostSearchError("overfit frontier must contain at least one trial")
    if not np.isfinite(frontier["objective_value"].astype("float64")).all():
        raise V1P0XGBoostSearchError("overfit frontier objective values must be finite")
    return {"frontier_rows": int(len(frontier)), "trial_count": int(frontier["trial_id"].nunique())}


def classify_stage24_candidate(validation_both_metric_rate: float, lockbox_both_metric_rate: float, train_validation_gap_flag_rate: float, lockbox_used_for_selection: bool) -> dict[str, Any]:
    if lockbox_used_for_selection:
        return {"classification": "blocked", "promotion_review_recommended": False, "reason": "lockbox was used for selection"}
    if validation_both_metric_rate < 0.5 or lockbox_both_metric_rate < 0.5:
        return {"classification": "exploratory_only", "promotion_review_recommended": False, "reason": "candidate does not clear both-metric rate floor on validation and lockbox"}
    if train_validation_gap_flag_rate > 0.5:
        return {"classification": "development_candidate", "promotion_review_recommended": False, "reason": "train-validation gap flags are too frequent for lockbox-reported status"}
    return {"classification": "lockbox_reported_candidate", "promotion_review_recommended": True, "reason": "candidate cleared conservative validation/lockbox rate floors without lockbox selection"}


def build_stage25_paired_loss_table(
    candidate_predictions: pd.DataFrame,
    hurdle_predictions: pd.DataFrame,
    candidate_model_id: str = "market_xgboost_v2_frozen_final",
    hurdle_model_id: str = "market_xgboost_v1_fixed",
) -> pd.DataFrame:
    candidate_required = {"row_key", "canonical_ticker", "as_of_date", "horizon_id", "fold_id", "split_role", "target", "model_id", "prediction"}
    hurdle_required = {"row_key", "horizon_id", "fold_id", "split_role", "model_id", "prediction"}
    _require_columns(candidate_predictions, candidate_required, "candidate predictions")
    _require_columns(hurdle_predictions, hurdle_required, "hurdle predictions")

    candidate = candidate_predictions[candidate_predictions["model_id"] == candidate_model_id].copy()
    hurdle = hurdle_predictions[hurdle_predictions["model_id"] == hurdle_model_id].copy()
    if candidate.empty or hurdle.empty:
        raise V1P0XGBoostSearchError("Stage 25 requires non-empty candidate and hurdle prediction rows")

    join_keys = ["row_key", "fold_id", "horizon_id", "split_role"]
    candidate_cols = join_keys + ["canonical_ticker", "as_of_date", "target", "prediction"]
    hurdle_cols = join_keys + ["prediction"]
    paired = candidate[candidate_cols].merge(hurdle[hurdle_cols], on=join_keys, suffixes=("_candidate", "_hurdle"), validate="one_to_one")
    if paired.empty:
        raise V1P0XGBoostSearchError("Stage 25 found no paired candidate/hurdle prediction rows")

    paired = paired.rename(columns={"prediction_candidate": "candidate_prediction", "prediction_hurdle": "hurdle_prediction"})
    paired["target"] = paired["target"].astype("float64")
    paired["candidate_prediction"] = paired["candidate_prediction"].astype("float64")
    paired["hurdle_prediction"] = paired["hurdle_prediction"].astype("float64")
    paired["candidate_squared_error"] = np.square(paired["candidate_prediction"] - paired["target"])
    paired["hurdle_squared_error"] = np.square(paired["hurdle_prediction"] - paired["target"])
    paired["squared_error_delta_candidate_minus_hurdle"] = paired["candidate_squared_error"] - paired["hurdle_squared_error"]
    paired["candidate_absolute_error"] = np.abs(paired["candidate_prediction"] - paired["target"])
    paired["hurdle_absolute_error"] = np.abs(paired["hurdle_prediction"] - paired["target"])
    paired["absolute_error_delta_candidate_minus_hurdle"] = paired["candidate_absolute_error"] - paired["hurdle_absolute_error"]
    paired["candidate_model_id"] = candidate_model_id
    paired["hurdle_model_id"] = hurdle_model_id
    paired = paired[
        [
            "row_key",
            "canonical_ticker",
            "as_of_date",
            "horizon_id",
            "fold_id",
            "split_role",
            "target",
            "candidate_model_id",
            "hurdle_model_id",
            "candidate_prediction",
            "hurdle_prediction",
            "candidate_squared_error",
            "hurdle_squared_error",
            "squared_error_delta_candidate_minus_hurdle",
            "candidate_absolute_error",
            "hurdle_absolute_error",
            "absolute_error_delta_candidate_minus_hurdle",
        ]
    ].sort_values(["split_role", "horizon_id", "fold_id", "as_of_date", "canonical_ticker"], kind="mergesort")
    validate_stage25_paired_loss_schema(paired)
    return paired.reset_index(drop=True)


def validate_stage25_paired_loss_schema(paired_losses: pd.DataFrame) -> dict[str, Any]:
    _require_columns(paired_losses, STAGE25_PAIRED_LOSS_REQUIRED_COLUMNS, "Stage 25 paired loss table")
    if paired_losses.empty:
        raise V1P0XGBoostSearchError("Stage 25 paired loss table must not be empty")
    numeric_columns = [
        "target",
        "candidate_prediction",
        "hurdle_prediction",
        "candidate_squared_error",
        "hurdle_squared_error",
        "squared_error_delta_candidate_minus_hurdle",
        "candidate_absolute_error",
        "hurdle_absolute_error",
        "absolute_error_delta_candidate_minus_hurdle",
    ]
    if not np.isfinite(paired_losses[numeric_columns].astype("float64").to_numpy()).all():
        raise V1P0XGBoostSearchError("Stage 25 paired loss numeric columns must be finite")
    duplicate_keys = paired_losses.duplicated(["row_key", "fold_id", "horizon_id", "split_role"])
    if duplicate_keys.any():
        raise V1P0XGBoostSearchError("Stage 25 paired loss rows must be unique by row/fold/horizon/split")
    return {
        "paired_loss_rows": int(len(paired_losses)),
        "split_roles": sorted(paired_losses["split_role"].astype(str).unique().tolist()),
        "horizons": sorted(paired_losses["horizon_id"].astype(str).unique().tolist()),
    }


def moving_block_resample_indices(n_blocks: int, block_length: int, resample_count: int, seed: int) -> np.ndarray:
    if n_blocks <= 0:
        raise V1P0XGBoostSearchError("moving block bootstrap requires at least one block")
    if block_length <= 0 or resample_count <= 0:
        raise V1P0XGBoostSearchError("block_length and resample_count must be positive")
    effective_length = min(int(block_length), int(n_blocks))
    starts = np.arange(0, n_blocks - effective_length + 1, dtype="int64")
    blocks_per_sample = int(np.ceil(n_blocks / effective_length))
    rng = np.random.default_rng(seed)
    result = np.empty((int(resample_count), int(n_blocks)), dtype="int64")
    for i in range(int(resample_count)):
        sampled_starts = rng.choice(starts, size=blocks_per_sample, replace=True)
        sampled = np.concatenate([np.arange(start, start + effective_length, dtype="int64") for start in sampled_starts])[:n_blocks]
        result[i] = sampled
    return result


def stage25_delta_intervals(
    paired_losses: pd.DataFrame,
    block_length: int,
    resample_count: int,
    seed: int,
    split_roles: tuple[str, ...] = ("validation", "lockbox"),
    method: str = "moving_block_bootstrap",
) -> pd.DataFrame:
    validate_stage25_paired_loss_schema(paired_losses)
    rows: list[dict[str, Any]] = []
    for split_role in split_roles:
        for horizon_id in REQUIRED_HORIZONS:
            blocks = _stage25_loss_blocks(paired_losses, split_role, horizon_id)
            if blocks.empty:
                continue
            indices = moving_block_resample_indices(len(blocks), block_length, resample_count, _stable_seed(seed, method, split_role, horizon_id))
            for metric in ("rmse", "mae"):
                observed_candidate = _stage25_metric(blocks, metric, "candidate")
                observed_hurdle = _stage25_metric(blocks, metric, "hurdle")
                observed_delta = observed_candidate - observed_hurdle
                distribution = np.array([_stage25_metric(blocks.iloc[indexer], metric, "candidate") - _stage25_metric(blocks.iloc[indexer], metric, "hurdle") for indexer in indices], dtype="float64")
                ci_low, ci_high = np.quantile(distribution, [0.025, 0.975])
                rows.append(
                    {
                        "method": method,
                        "split_role": split_role,
                        "horizon_id": horizon_id,
                        "metric": metric,
                        "observed_candidate": float(observed_candidate),
                        "observed_hurdle": float(observed_hurdle),
                        "observed_delta_candidate_minus_hurdle": float(observed_delta),
                        "ci_low": float(ci_low),
                        "ci_high": float(ci_high),
                        "ci_width": float(ci_high - ci_low),
                        "probability_candidate_improves": float(np.mean(distribution < 0.0)),
                        "ci_excludes_zero_in_improvement_direction": bool(ci_high < 0.0),
                        "resample_count": int(resample_count),
                        "block_length": int(block_length),
                        "effective_block_length": int(min(block_length, len(blocks))),
                        "date_block_count": int(len(blocks)),
                        "row_count": int(blocks["row_count"].sum()),
                        "seed": int(seed),
                    }
                )
    return pd.DataFrame.from_records(rows)


def stage25_uncertainty_comparison(block_intervals: pd.DataFrame, date_clustered_intervals: pd.DataFrame) -> pd.DataFrame:
    keys = ["split_role", "horizon_id", "metric"]
    merged = block_intervals.merge(date_clustered_intervals, on=keys, suffixes=("_block", "_date_clustered"), validate="one_to_one")
    merged["ci_width_ratio_block_to_date_clustered"] = merged["ci_width_block"] / merged["ci_width_date_clustered"].replace(0.0, np.nan)
    merged["improvement_probability_delta_block_minus_date_clustered"] = merged["probability_candidate_improves_block"] - merged["probability_candidate_improves_date_clustered"]
    merged["sign_consistent"] = np.sign(merged["observed_delta_candidate_minus_hurdle_block"]) == np.sign(merged["observed_delta_candidate_minus_hurdle_date_clustered"])
    return merged[
        keys
        + [
            "observed_delta_candidate_minus_hurdle_block",
            "ci_width_block",
            "ci_width_date_clustered",
            "ci_width_ratio_block_to_date_clustered",
            "probability_candidate_improves_block",
            "probability_candidate_improves_date_clustered",
            "improvement_probability_delta_block_minus_date_clustered",
            "ci_excludes_zero_in_improvement_direction_block",
            "ci_excludes_zero_in_improvement_direction_date_clustered",
            "sign_consistent",
        ]
    ]


def stage25_generalization_gap_intervals(
    paired_losses: pd.DataFrame,
    block_length: int,
    resample_count: int,
    seed: int,
    oos_roles: tuple[str, ...] = ("validation", "lockbox"),
) -> pd.DataFrame:
    validate_stage25_paired_loss_schema(paired_losses)
    rows: list[dict[str, Any]] = []
    for horizon_id in REQUIRED_HORIZONS:
        train_blocks = _stage25_loss_blocks(paired_losses, "train", horizon_id)
        if train_blocks.empty:
            continue
        train_indices = moving_block_resample_indices(len(train_blocks), block_length, resample_count, _stable_seed(seed, "train", horizon_id))
        for oos_role in oos_roles:
            oos_blocks = _stage25_loss_blocks(paired_losses, oos_role, horizon_id)
            if oos_blocks.empty:
                continue
            oos_indices = moving_block_resample_indices(len(oos_blocks), block_length, resample_count, _stable_seed(seed, oos_role, horizon_id))
            for metric in ("rmse", "mae"):
                observed_train = _stage25_metric(train_blocks, metric, "candidate")
                observed_oos = _stage25_metric(oos_blocks, metric, "candidate")
                train_distribution = np.array([_stage25_metric(train_blocks.iloc[indexer], metric, "candidate") for indexer in train_indices], dtype="float64")
                oos_distribution = np.array([_stage25_metric(oos_blocks.iloc[indexer], metric, "candidate") for indexer in oos_indices], dtype="float64")
                gap_distribution = oos_distribution - train_distribution
                ratio_distribution = oos_distribution / np.maximum(train_distribution, 1.0e-12)
                gap_low, gap_high = np.quantile(gap_distribution, [0.025, 0.975])
                ratio_low, ratio_high = np.quantile(ratio_distribution, [0.025, 0.975])
                observed_gap = observed_oos - observed_train
                observed_ratio = observed_oos / max(observed_train, 1.0e-12)
                rows.append(
                    {
                        "method": "moving_block_bootstrap_train_oos_gap",
                        "horizon_id": horizon_id,
                        "metric": metric,
                        "train_split_role": "train",
                        "oos_split_role": oos_role,
                        "observed_train_candidate": float(observed_train),
                        "observed_oos_candidate": float(observed_oos),
                        "observed_oos_minus_train": float(observed_gap),
                        "gap_ci_low": float(gap_low),
                        "gap_ci_high": float(gap_high),
                        "observed_oos_to_train_ratio": float(observed_ratio),
                        "ratio_ci_low": float(ratio_low),
                        "ratio_ci_high": float(ratio_high),
                        "probability_oos_worse_than_train": float(np.mean(gap_distribution > 0.0)),
                        "diagnostic_overfit_pressure_flag": bool(observed_ratio > 1.25 and gap_low > 0.0),
                        "resample_count": int(resample_count),
                        "block_length": int(block_length),
                        "train_date_block_count": int(len(train_blocks)),
                        "oos_date_block_count": int(len(oos_blocks)),
                    }
                )
    return pd.DataFrame.from_records(rows)


def _require_columns(frame: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required.difference(frame.columns)
    if missing:
        raise V1P0XGBoostSearchError(f"{name} missing required columns: {sorted(missing)}")


def _stable_seed(seed: int, *parts: Any) -> int:
    encoded = "|".join([str(seed), *(str(part) for part in parts)]).encode("utf-8")
    return int.from_bytes(sha256(encoded).digest()[:4], "big", signed=False)


def _stage25_loss_blocks(paired_losses: pd.DataFrame, split_role: str, horizon_id: str) -> pd.DataFrame:
    subset = paired_losses[(paired_losses["split_role"] == split_role) & (paired_losses["horizon_id"] == horizon_id)].copy()
    if subset.empty:
        return pd.DataFrame()
    subset["as_of_date"] = pd.to_datetime(subset["as_of_date"])
    blocks = (
        subset.groupby("as_of_date", sort=True)
        .agg(
            candidate_squared_error_sum=("candidate_squared_error", "sum"),
            hurdle_squared_error_sum=("hurdle_squared_error", "sum"),
            candidate_absolute_error_sum=("candidate_absolute_error", "sum"),
            hurdle_absolute_error_sum=("hurdle_absolute_error", "sum"),
            row_count=("row_key", "count"),
        )
        .reset_index()
    )
    return blocks.sort_values("as_of_date", kind="mergesort").reset_index(drop=True)


def _stage25_metric(blocks: pd.DataFrame, metric: str, model_role: str) -> float:
    row_count = float(blocks["row_count"].sum())
    if row_count <= 0.0:
        raise V1P0XGBoostSearchError("Stage 25 bootstrap block has no rows")
    if model_role not in {"candidate", "hurdle"}:
        raise V1P0XGBoostSearchError("model_role must be candidate or hurdle")
    if metric == "rmse":
        return float(np.sqrt(float(blocks[f"{model_role}_squared_error_sum"].sum()) / row_count))
    if metric == "mae":
        return float(float(blocks[f"{model_role}_absolute_error_sum"].sum()) / row_count)
    raise V1P0XGBoostSearchError(f"unsupported Stage 25 metric: {metric}")


def _validate_weights(weights: dict[str, Any], required_keys: tuple[str, ...], field_name: str) -> None:
    if set(weights) != set(required_keys):
        raise V1P0XGBoostSearchError(f"{field_name} keys must be {list(required_keys)}")
    total = sum(float(weights[key]) for key in required_keys)
    if not np.isclose(total, 1.0):
        raise V1P0XGBoostSearchError(f"{field_name} must sum to 1.0")
    if any(float(weights[key]) <= 0.0 for key in required_keys):
        raise V1P0XGBoostSearchError(f"{field_name} values must be positive")


def _validate_param_spec(name: str, spec: dict[str, Any]) -> None:
    if spec.get("type") not in {"int", "float"}:
        raise V1P0XGBoostSearchError(f"unsupported search-space type for {name}")
    low = float(spec.get("low"))
    high = float(spec.get("high"))
    if low >= high:
        raise V1P0XGBoostSearchError(f"search-space low must be lower than high for {name}")
    if spec.get("log") and low <= 0.0:
        raise V1P0XGBoostSearchError(f"log search-space low must be positive for {name}")
    if spec.get("type") == "int" and int(spec.get("step", 1)) <= 0:
        raise V1P0XGBoostSearchError(f"integer search-space step must be positive for {name}")


def _paired_validation_metrics(metrics: pd.DataFrame, candidate_id: str, hurdle_id: str, selection_role: str) -> pd.DataFrame:
    validation = metrics[metrics["split_role"] == selection_role]
    candidate = validation[validation["model_id"] == candidate_id]
    hurdle = validation[validation["model_id"] == hurdle_id]
    paired = candidate.merge(hurdle, on=["fold_id", "horizon_id"], suffixes=("_candidate", "_hurdle"), validate="one_to_one")
    if paired.empty:
        raise V1P0XGBoostSearchError("objective has no paired candidate/hurdle validation metrics")
    return paired


def _objective_penalties(
    validation_pairs: pd.DataFrame,
    metrics: pd.DataFrame,
    objective: dict[str, Any],
    candidate_id: str,
    train_role: str,
    selection_role: str,
    trial_params: dict[str, float | int],
) -> dict[str, float]:
    penalty_config = objective["penalties"]
    horizon_weights = objective["horizon_weights"]

    one_sided = (validation_pairs["rmse_delta"] < 0.0) != (validation_pairs["mae_delta"] < 0.0)
    validation_pairs = validation_pairs.assign(one_sided_improvement=one_sided)
    one_sided_rate = validation_pairs.groupby("horizon_id", sort=True)["one_sided_improvement"].mean().to_dict()
    one_sided_penalty = float(penalty_config["one_sided_improvement"]["weight"]) * _weighted_mean(one_sided_rate, horizon_weights)

    gap_penalty = _train_validation_gap_penalty(metrics, candidate_id, train_role, selection_role, objective)
    horizon_instability_penalty = float(penalty_config["horizon_instability"]["weight"]) * float(validation_pairs.groupby("horizon_id", sort=True)["composite_delta"].mean().std(ddof=0))
    fold_instability_penalty = float(penalty_config["fold_instability"]["weight"]) * float(validation_pairs["composite_delta"].std(ddof=0))
    complexity_penalty = _complexity_penalty(trial_params, penalty_config["complexity"])
    return {
        "one_sided_improvement": one_sided_penalty,
        "train_validation_gap": gap_penalty,
        "horizon_instability": horizon_instability_penalty,
        "fold_instability": fold_instability_penalty,
        "complexity": complexity_penalty,
    }


def _train_validation_gap_penalty(metrics: pd.DataFrame, candidate_id: str, train_role: str, selection_role: str, objective: dict[str, Any]) -> float:
    candidate = metrics[metrics["model_id"] == candidate_id]
    train = candidate[candidate["split_role"] == train_role]
    validation = candidate[candidate["split_role"] == selection_role]
    if train.empty or validation.empty:
        return 0.0
    paired = validation.merge(train, on=["fold_id", "horizon_id"], suffixes=("_validation", "_train"), validate="one_to_one")
    if paired.empty:
        return 0.0
    threshold = float(objective["penalties"]["train_validation_gap"]["validation_to_train_ratio_threshold"])
    metric_weights = objective["metric_weights"]
    horizon_weights = objective["horizon_weights"]
    epsilon = 1.0e-12
    rows: list[dict[str, float | str]] = []
    for _, row in paired.iterrows():
        excess = 0.0
        for metric in OBJECTIVE_METRICS:
            ratio = float(row[f"{metric}_validation"]) / max(float(row[f"{metric}_train"]), epsilon)
            excess += float(metric_weights[metric]) * max(0.0, (ratio - threshold) / threshold)
        rows.append({"horizon_id": str(row["horizon_id"]), "excess": excess})
    by_horizon = pd.DataFrame.from_records(rows).groupby("horizon_id", sort=True)["excess"].mean().to_dict()
    return float(objective["penalties"]["train_validation_gap"]["weight"]) * _weighted_mean(by_horizon, horizon_weights)


def _complexity_penalty(trial_params: dict[str, float | int], penalty_config: dict[str, Any]) -> float:
    if not trial_params:
        return 0.0
    n_estimators_reference = float(penalty_config["n_estimators_reference"])
    max_depth_reference = float(penalty_config["max_depth_reference"])
    n_estimators_component = float(trial_params.get("n_estimators", 0.0)) / n_estimators_reference
    max_depth_component = float(trial_params.get("max_depth", 0.0)) / max_depth_reference
    normalized_complexity = max(0.0, 0.5 * n_estimators_component + 0.5 * max_depth_component)
    return float(penalty_config["weight"]) * normalized_complexity


def _weighted_mean(values: dict[str, Any], weights: dict[str, Any]) -> float:
    return float(sum(float(weights[horizon]) * float(values.get(horizon, 0.0)) for horizon in REQUIRED_HORIZONS))
