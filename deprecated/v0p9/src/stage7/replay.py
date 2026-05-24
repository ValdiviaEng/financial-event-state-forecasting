"""Stage 7 development replay runner."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from event_state_forecasting.stage7.config import all_epsilon_values, all_k_values
from event_state_forecasting.stage7.context import CURRENT_STAGE6_LOCKBOX_END, CURRENT_STAGE6_LOCKBOX_START, prediction_column
from event_state_forecasting.stage7.metrics import compute_stage7_metrics
from event_state_forecasting.stage7.policies import deterministic_rng, select_top_bottom


def run_development_replay(context: pd.DataFrame, config: Mapping[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Run the approved development-only Stage 7 replay.

    This is full-information simulated replay using frozen labels. It is not a
    real logged-policy IPW/DR evaluation and does not create a trading signal.
    """

    seed = int(config["protocol"]["seed"])
    primary_score = prediction_column(str(config["context"]["primary_supervised_score_model_id"]))
    market_score = prediction_column(str(config["context"]["market_only_score_model_id"]))
    k_values = all_k_values(config)
    epsilon_values = all_epsilon_values(config)
    policy_records = build_policy_records(epsilon_values)

    selected_frames: list[pd.DataFrame] = []
    group_columns = ["fold_id", "horizon_id", "as_of_date"]
    for policy in policy_records:
        for k in k_values:
            for keys, group in context.groupby(group_columns, sort=True):
                fold_id, horizon_id, as_of_date = keys
                score_column = market_score if policy["policy_id"] == "market_only_ranker" else primary_score
                force_random = policy["policy_family"] == "random_baseline"
                selected = select_top_bottom(
                    group,
                    k=k,
                    score_column=score_column,
                    policy_id=policy["policy_id"],
                    policy_family=policy["policy_family"],
                    epsilon=policy["epsilon"],
                    rng=deterministic_rng(seed, policy["policy_id"], k, fold_id, horizon_id, as_of_date),
                    force_random=force_random,
                )
                selected_frames.append(selected)

    selections = pd.concat(selected_frames, ignore_index=True) if selected_frames else context.iloc[0:0].copy()
    metrics = compute_stage7_metrics(selections)
    policy_manifest = pd.DataFrame(policy_records)
    return selections, metrics, policy_manifest


def build_policy_records(epsilon_values: list[float]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = [
        {
            "policy_id": "random_top_bottom",
            "policy_family": "random_baseline",
            "epsilon": None,
            "adaptive": False,
            "baseline": True,
        },
        {
            "policy_id": "market_only_ranker",
            "policy_family": "market_only_baseline",
            "epsilon": None,
            "adaptive": False,
            "baseline": True,
        },
        {
            "policy_id": "stage5_predictions_only_supervised",
            "policy_family": "predictions_only_supervised_baseline",
            "epsilon": None,
            "adaptive": False,
            "baseline": True,
        },
        {
            "policy_id": "combined_supervised",
            "policy_family": "combined_context_supervised_baseline",
            "epsilon": None,
            "adaptive": False,
            "baseline": True,
        },
        {
            "policy_id": "static_validation_selected_rule",
            "policy_family": "static_rule_baseline",
            "epsilon": None,
            "adaptive": False,
            "baseline": True,
        },
    ]
    for epsilon in epsilon_values:
        suffix = epsilon_suffix(epsilon)
        records.append(
            {
                "policy_id": f"epsilon_random_{suffix}",
                "policy_family": "epsilon_random_baseline",
                "epsilon": epsilon,
                "adaptive": False,
                "baseline": True,
            }
        )
        records.append(
            {
                "policy_id": f"epsilon_greedy_{suffix}",
                "policy_family": "epsilon_greedy_policy",
                "epsilon": epsilon,
                "adaptive": True,
                "baseline": False,
            }
        )
    return records


def epsilon_suffix(value: float) -> str:
    return f"{value:.2f}".replace(".", "p")


def build_replay_validation(
    context: pd.DataFrame,
    selections: pd.DataFrame,
    metrics: pd.DataFrame,
    *,
    allow_new_post_lockbox_holdout: bool = False,
) -> dict[str, Any]:
    blockers: list[str] = []
    if context.empty:
        blockers.append("empty_context")
    if selections.empty:
        blockers.append("empty_policy_outputs")
    if metrics.empty:
        blockers.append("empty_metrics")
    split_roles = set(context.get("split_role", []))
    current_lockbox_row_count = count_current_stage6_lockbox_rows(context)
    if current_lockbox_row_count:
        blockers.append("current_stage6_lockbox_used_in_stage7_context")
    if "lockbox" in split_roles and not allow_new_post_lockbox_holdout:
        blockers.append("lockbox_role_used_without_new_post_lockbox_holdout_mode")
    if bool(selections.get("trading_signal_approved", pd.Series(dtype=bool)).any()):
        blockers.append("trading_signal_unexpectedly_approved")
    if bool(metrics.get("spread_is_trading_pnl", pd.Series(dtype=bool)).any()):
        blockers.append("spread_marked_as_trading_pnl")
    return {
        "artifact_type": "stage7_replay_validation",
        "artifact_schema_version": "stage7_contextual_bandit_v1",
        "status": "passed" if not blockers else "failed",
        "context_rows": int(len(context)),
        "selection_rows": int(len(selections)),
        "metric_rows": int(len(metrics)),
        "split_roles": sorted(str(value) for value in context.get("split_role", pd.Series(dtype=str)).drop_duplicates().tolist()),
        "lockbox_used_for_design": "lockbox" in split_roles and not allow_new_post_lockbox_holdout,
        "new_post_lockbox_holdout_mode": bool(allow_new_post_lockbox_holdout),
        "current_stage6_lockbox_row_count": current_lockbox_row_count,
        "benchmark_claim": False,
        "blockers": blockers,
    }


def count_current_stage6_lockbox_rows(context: pd.DataFrame) -> int:
    if "as_of_date" not in context.columns:
        return 0
    dates = pd.to_datetime(context["as_of_date"]).dt.date.astype(str)
    mask = (dates >= CURRENT_STAGE6_LOCKBOX_START) & (dates <= CURRENT_STAGE6_LOCKBOX_END)
    return int(mask.sum())
