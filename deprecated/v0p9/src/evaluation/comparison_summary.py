"""Stage 6 overfitting diagnostics, comparability, and result summary."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

import pandas as pd


ALLOWED_RESULT_CLASSES = {"robust_positive", "conditional_positive", "clean_null"}
ALLOWED_COMPARABILITY = {"comparable", "limitation_bearing", "invalidated", "not_comparable"}


class ComparisonSummaryError(ValueError):
    """Raised when Stage 6 summary inputs are incomplete."""


def build_overfitting_diagnostic_report(
    metrics: pd.DataFrame,
    paired_comparisons: pd.DataFrame,
    config: Mapping[str, Any],
    search_space_summary: Mapping[str, Any],
    training_prediction_available: bool,
) -> dict[str, Any]:
    """Build the mandatory Option B diagnostic report."""

    event_model_id = str(config["metric_policy"]["event_state_model_id"])
    primary_horizons = list(config["result_classification"]["primary_horizons"])
    aggregate = metrics[metrics["aggregation_level"] == "aggregate"].copy()
    validation = aggregate[aggregate["split_role"] == "validation"]
    lockbox = aggregate[aggregate["split_role"] == "lockbox"]
    if validation.empty or lockbox.empty:
        raise ComparisonSummaryError("validation and lockbox aggregate metrics are required")

    return {
        "artifact_type": "overfitting_diagnostic_report",
        "artifact_schema_version": "stage6_reporting_v1",
        "generated_at_utc": now_utc(),
        "train_validation_gap": _train_validation_gap(training_prediction_available),
        "fold_dispersion": _fold_dispersion(metrics),
        "positive_fold_rates": _positive_fold_rates(paired_comparisons, event_model_id=event_model_id, primary_horizons=primary_horizons),
        "positive_horizon_rates": _positive_horizon_rates(paired_comparisons, event_model_id=event_model_id, primary_horizons=primary_horizons),
        "validation_to_lockbox_degradation": _validation_to_lockbox_degradation(aggregate, event_model_id=event_model_id),
        "paired_comparison_policy": config["paired_comparison_policy"],
        "multiple_comparison_note": _multiple_comparison_note(config, search_space_summary),
        "search_space_summary": dict(search_space_summary),
        "diagnostic_status": "complete_with_explicit_train_gap_blocker" if not training_prediction_available else "complete",
    }


def build_comparison_summary(
    metrics: pd.DataFrame,
    ranking_diagnostics: pd.DataFrame,
    paired_comparisons: pd.DataFrame,
    selected_market_hurdles: Mapping[str, str],
    diagnostic_report: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the evidence-backed result-class summary."""

    event_model_id = str(config["metric_policy"]["event_state_model_id"])
    primary_horizons = list(config["result_classification"]["primary_horizons"])
    robust_min = int(config["result_classification"]["robust_positive_min_primary_horizons"])
    conditional_min = int(config["result_classification"]["conditional_positive_min_primary_horizons"])

    horizon_table = _event_horizon_table(paired_comparisons, event_model_id=event_model_id)
    validation_primary = [row for row in horizon_table if row["split_role"] == "validation" and row["horizon_id"] in primary_horizons]
    lockbox_primary = [row for row in horizon_table if row["split_role"] == "lockbox" and row["horizon_id"] in primary_horizons]
    validation_positive = sum(1 for row in validation_primary if row["improves_on_both_primary_losses"])
    lockbox_positive = sum(1 for row in lockbox_primary if row["improves_on_both_primary_losses"])

    if validation_positive >= robust_min and lockbox_positive >= robust_min:
        result_class = "robust_positive"
        result_reason = "event_state_improved_on_required_short_horizon_primary_metrics_in_validation_and_lockbox"
    elif validation_positive >= conditional_min or lockbox_positive >= conditional_min:
        result_class = "conditional_positive"
        result_reason = "event_state_showed_partial_short_horizon_improvement_but_not_the_robust_threshold"
    else:
        result_class = "clean_null"
        result_reason = "event_state_did_not_clear_the_predeclared_short_horizon_primary_hurdle"

    return {
        "artifact_type": "comparison_summary",
        "artifact_schema_version": "stage6_reporting_v1",
        "generated_at_utc": now_utc(),
        "result_class": result_class,
        "result_reason": result_reason,
        "classification_policy": dict(config["result_classification"]),
        "event_state_model_id": event_model_id,
        "selected_market_hurdles": dict(selected_market_hurdles),
        "primary_horizon_counts": {
            "validation_positive_horizons": validation_positive,
            "lockbox_positive_horizons": lockbox_positive,
            "required_for_robust_positive": robust_min,
            "required_for_conditional_positive": conditional_min,
        },
        "event_state_horizon_table": horizon_table,
        "topline_regression_metrics": _topline_metrics(metrics, event_model_id=event_model_id, selected_market_hurdles=selected_market_hurdles),
        "topline_ranking_diagnostics": _topline_ranking(ranking_diagnostics, event_model_id=event_model_id),
        "diagnostic_status": diagnostic_report.get("diagnostic_status"),
        "non_claims": ["not_trading_profitability", "not_provider_level_article_completeness", "not_sentiment_string_ablation"],
    }


def build_benchmark_comparability_record(
    packet_validation: Mapping[str, Any],
    diagnostic_report: Mapping[str, Any],
) -> dict[str, Any]:
    """Classify benchmark comparability after Stage 6 packet validation."""

    invalidating_reasons: list[str] = []
    limitation_reasons = [
        "alphavantage_provider_level_article_completeness_not_claimed",
        "active_split_adjustment_method_not_selected_but_stage2_uses_derived_manifest_only",
    ]
    if packet_validation.get("status") != "passed":
        invalidating_reasons.append("serious_run_packet_incomplete")
    if diagnostic_report.get("train_validation_gap", {}).get("status") == "blocked_missing_train_predictions":
        limitation_reasons.append("train_validation_gap_blocked_because_stage5_saved_no_train_predictions")

    status = "invalidated" if invalidating_reasons else "limitation_bearing" if limitation_reasons else "comparable"
    return {
        "artifact_type": "benchmark_comparability_classification",
        "artifact_schema_version": "stage6_reporting_v1",
        "generated_at_utc": now_utc(),
        "comparability_classification": status,
        "invalidating_reasons": invalidating_reasons,
        "limitation_reasons": limitation_reasons,
        "protected_scope_changed": False,
        "metric_policy_changed_after_results": False,
        "lockbox_used_for_tuning": False,
    }


def _train_validation_gap(training_prediction_available: bool) -> dict[str, Any]:
    if training_prediction_available:
        return {"status": "available", "note": "train predictions available for explicit gap computation"}
    return {
        "status": "blocked_missing_train_predictions",
        "reason": "Stage 5 intentionally saved out-of-sample validation and lockbox predictions only; no in-sample train predictions or train losses were materialized.",
        "handling": "explicitly_blocked_not_invented",
    }


def _fold_dispersion(metrics: pd.DataFrame) -> list[dict[str, Any]]:
    fold_metrics = metrics[(metrics["aggregation_level"] == "fold") & (metrics["split_role"] == "validation")].copy()
    records: list[dict[str, Any]] = []
    for keys, group in fold_metrics.groupby(["model_id", "horizon_id"], sort=True):
        model_id, horizon_id = keys
        records.append(
            {
                "model_id": str(model_id),
                "horizon_id": str(horizon_id),
                "fold_count": int(len(group)),
                "rmse_mean": float(group["rmse"].mean()),
                "rmse_std": _std(group["rmse"]),
                "mae_mean": float(group["mae"].mean()),
                "mae_std": _std(group["mae"]),
                "r2_oos_mean": float(group["r2_oos"].mean()),
                "r2_oos_std": _std(group["r2_oos"]),
                "mean_squared_loss_diff_mean": float(group["mean_squared_loss_diff"].mean()),
                "mean_absolute_loss_diff_mean": float(group["mean_absolute_loss_diff"].mean()),
            }
        )
    return records


def _positive_fold_rates(paired: pd.DataFrame, *, event_model_id: str, primary_horizons: list[str]) -> dict[str, Any]:
    fold = paired[(paired["aggregation_level"] == "fold") & (paired["model_id"] == event_model_id)].copy()
    fold["improves_on_both_primary_losses"] = (fold["mean_squared_loss_diff"] > 0.0) & (fold["mean_absolute_loss_diff"] > 0.0)
    records: list[dict[str, Any]] = []
    for keys, group in fold.groupby(["split_role", "horizon_id"], sort=True):
        split_role, horizon_id = keys
        records.append(
            {
                "split_role": str(split_role),
                "horizon_id": str(horizon_id),
                "is_primary_horizon": str(horizon_id) in primary_horizons,
                "fold_count": int(len(group)),
                "positive_fold_rate": float(group["improves_on_both_primary_losses"].mean()),
            }
        )
    return {"records": records}


def _positive_horizon_rates(paired: pd.DataFrame, *, event_model_id: str, primary_horizons: list[str]) -> dict[str, Any]:
    aggregate = paired[(paired["aggregation_level"] == "aggregate") & (paired["model_id"] == event_model_id)].copy()
    aggregate["improves_on_both_primary_losses"] = (aggregate["mean_squared_loss_diff"] > 0.0) & (aggregate["mean_absolute_loss_diff"] > 0.0)
    records: list[dict[str, Any]] = []
    for split_role, group in aggregate.groupby("split_role", sort=True):
        primary = group[group["horizon_id"].isin(primary_horizons)]
        records.append(
            {
                "split_role": str(split_role),
                "all_horizon_positive_rate": float(group["improves_on_both_primary_losses"].mean()),
                "primary_horizon_positive_rate": float(primary["improves_on_both_primary_losses"].mean()) if len(primary) else 0.0,
                "primary_horizon_count": int(len(primary)),
                "all_horizon_count": int(len(group)),
            }
        )
    return {"records": records}


def _validation_to_lockbox_degradation(metrics: pd.DataFrame, *, event_model_id: str) -> list[dict[str, Any]]:
    aggregate = metrics[(metrics["aggregation_level"] == "aggregate") & (metrics["model_id"] == event_model_id)].copy()
    validation = aggregate[aggregate["split_role"] == "validation"].set_index("horizon_id")
    lockbox = aggregate[aggregate["split_role"] == "lockbox"].set_index("horizon_id")
    records: list[dict[str, Any]] = []
    for horizon_id in sorted(set(validation.index) & set(lockbox.index), key=lambda value: int(str(value).removesuffix("d"))):
        records.append(
            {
                "model_id": event_model_id,
                "horizon_id": str(horizon_id),
                "rmse_validation": float(validation.loc[horizon_id, "rmse"]),
                "rmse_lockbox": float(lockbox.loc[horizon_id, "rmse"]),
                "rmse_lockbox_minus_validation": float(lockbox.loc[horizon_id, "rmse"] - validation.loc[horizon_id, "rmse"]),
                "mae_validation": float(validation.loc[horizon_id, "mae"]),
                "mae_lockbox": float(lockbox.loc[horizon_id, "mae"]),
                "mae_lockbox_minus_validation": float(lockbox.loc[horizon_id, "mae"] - validation.loc[horizon_id, "mae"]),
            }
        )
    return records


def _multiple_comparison_note(config: Mapping[str, Any], search_space_summary: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "models_considered": int(search_space_summary.get("fixed_model_count", 0)),
        "horizons_considered": list(config["result_classification"]["reported_horizons"]),
        "primary_horizons_for_result_class": list(config["result_classification"]["primary_horizons"]),
        "primary_regression_metrics": list(config["metric_policy"]["primary_regression_metrics"]),
        "ranking_diagnostics_are_secondary": True,
        "hyperparameter_search_attempts": int(search_space_summary.get("hyperparameter_search_attempts", 0)),
        "note": "All five approved horizons and all frozen Stage 5 model IDs are reported; the result class uses the predeclared short-horizon primary subset before result inspection.",
    }


def _event_horizon_table(paired: pd.DataFrame, *, event_model_id: str) -> list[dict[str, Any]]:
    aggregate = paired[(paired["aggregation_level"] == "aggregate") & (paired["model_id"] == event_model_id)].copy()
    records: list[dict[str, Any]] = []
    for row in aggregate.sort_values(["split_role", "horizon_id"]).to_dict("records"):
        records.append(
            {
                "split_role": str(row["split_role"]),
                "horizon_id": str(row["horizon_id"]),
                "baseline_model_id": str(row["baseline_model_id"]),
                "mean_squared_loss_diff": float(row["mean_squared_loss_diff"]),
                "mean_absolute_loss_diff": float(row["mean_absolute_loss_diff"]),
                "improves_on_both_primary_losses": bool(row["mean_squared_loss_diff"] > 0.0 and row["mean_absolute_loss_diff"] > 0.0),
            }
        )
    return records


def _topline_metrics(metrics: pd.DataFrame, *, event_model_id: str, selected_market_hurdles: Mapping[str, str]) -> list[dict[str, Any]]:
    aggregate = metrics[metrics["aggregation_level"] == "aggregate"].copy()
    rows: list[dict[str, Any]] = []
    for split_role in ["validation", "lockbox"]:
        for horizon_id, baseline_model_id in selected_market_hurdles.items():
            subset = aggregate[(aggregate["split_role"] == split_role) & (aggregate["horizon_id"] == horizon_id)]
            for model_id in [baseline_model_id, event_model_id]:
                row = subset[subset["model_id"] == model_id].iloc[0]
                rows.append(
                    {
                        "split_role": split_role,
                        "horizon_id": str(horizon_id),
                        "model_id": str(model_id),
                        "rmse": float(row["rmse"]),
                        "mae": float(row["mae"]),
                        "r2_oos": float(row["r2_oos"]),
                        "mean_squared_loss_diff": float(row["mean_squared_loss_diff"]),
                        "mean_absolute_loss_diff": float(row["mean_absolute_loss_diff"]),
                    }
                )
    return rows


def _topline_ranking(ranking: pd.DataFrame, *, event_model_id: str) -> list[dict[str, Any]]:
    aggregate = ranking[(ranking["aggregation_level"] == "aggregate") & (ranking["model_id"] == event_model_id)].copy()
    columns = ["split_role", "horizon_id", "spearman_rank_ic", "kendall_rank_correlation", "directional_hit_rate", "top_minus_bottom_spread"]
    return [
        {
            "split_role": str(row["split_role"]),
            "horizon_id": str(row["horizon_id"]),
            "spearman_rank_ic": float(row["spearman_rank_ic"]),
            "kendall_rank_correlation": float(row["kendall_rank_correlation"]),
            "directional_hit_rate": float(row["directional_hit_rate"]),
            "top_minus_bottom_spread": float(row["top_minus_bottom_spread"]),
        }
        for row in aggregate.loc[:, columns].sort_values(["split_role", "horizon_id"]).to_dict("records")
    ]


def _std(series: pd.Series) -> float:
    if len(series) <= 1:
        return 0.0
    return float(series.astype("float64").std(ddof=1))


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
