from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.xgboost_search import classify_stage24_candidate, validate_stage24_frontier_schema  # noqa: E402


STAGE22_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16"
STAGE23_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_AT_UTC = "2026-05-24T08:45:00Z"
SOURCE_ID = "6dff1bd"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the v1p0 Stage 24 XGBoost overfit frontier and promotion review.")
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()

    stage22_manifest = json.loads((STAGE22_ROOT / "search_manifest.json").read_text(encoding="utf-8"))
    stage23_manifest = json.loads((STAGE23_ROOT / "final_evaluation_manifest.json").read_text(encoding="utf-8"))
    _validate_sources(stage22_manifest, stage23_manifest)

    run_id = f"v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_{SOURCE_ID}__run_{stage23_manifest['best_config_digest_sha256'][:8]}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    frontier = _build_frontier()
    frontier_schema = validate_stage24_frontier_schema(frontier)
    split_summary = _build_split_summary()
    horizon_review = _build_horizon_review()
    classification = _classify_candidate(stage23_manifest, split_summary)

    frontier_path = output_root / "overfit_frontier_summary.parquet"
    split_summary_path = output_root / "selected_candidate_split_summary.parquet"
    horizon_review_path = output_root / "candidate_horizon_review.parquet"
    classification_path = output_root / "candidate_classification.json"
    manifest_path = output_root / "review_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage24_xgboost_overfit_promotion_review.md"
    frontier.to_parquet(frontier_path, index=False)
    split_summary.to_parquet(split_summary_path, index=False)
    horizon_review.to_parquet(horizon_review_path, index=False)
    _write_json(classification_path, classification)

    manifest = {
        "artifact_type": "v1p0_stage24_xgboost_overfit_review_manifest",
        "artifact_id": f"xgboost_stage24_overfit_review__stage23_{stage23_manifest['best_config_digest_sha256'][:12]}__20260524T084500Z",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed",
        "source_stage22_artifact_id": stage22_manifest["artifact_id"],
        "source_stage23_artifact_id": stage23_manifest["artifact_id"],
        "frontier_schema": frontier_schema,
        "classification": classification,
        "outputs": {
            "overfit_frontier_summary": _rel(frontier_path),
            "selected_candidate_split_summary": _rel(split_summary_path),
            "candidate_horizon_review": _rel(horizon_review_path),
            "candidate_classification": _rel(classification_path),
            "review_manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "benchmark_claim": False,
        "promotion_claim": False,
        "non_claims": ["not_positive_claim_approval", "not_stage6_reinterpretation", "not_trading_signal", "stage39_claim_review_required"],
    }
    _write_json(manifest_path, manifest)
    run_manifest = {
        "run_id": run_id,
        "stage": 24,
        "stage_name": "xgboost_overfit_frontier_and_promotion_review",
        "generated_at_utc": GENERATED_AT_UTC,
        "status": "completed",
        "command": "source ~/venvs/ai/bin/activate && python scripts/run_v1p0_xgboost_overfit_promotion_review.py",
        "outputs": manifest["outputs"],
        "benchmark_claim": False,
        "promotion_claim": False,
    }
    _write_json(run_manifest_path, run_manifest)
    report_path.write_text(_render_report(manifest, split_summary, horizon_review), encoding="utf-8")
    print(json.dumps({"status": "completed", "classification": classification["classification"], "promotion_review_recommended": classification["promotion_review_recommended"], "frontier_rows": len(frontier), "output_root": _rel(output_root)}, sort_keys=True))


def _validate_sources(stage22_manifest: dict[str, Any], stage23_manifest: dict[str, Any]) -> None:
    if stage22_manifest.get("status") != "completed":
        raise RuntimeError("Stage 24 requires completed Stage 22 search")
    if stage23_manifest.get("status") != "completed":
        raise RuntimeError("Stage 24 requires completed Stage 23 frozen final evaluation")
    if stage22_manifest.get("lockbox_policy", {}).get("lockbox_used_for_candidate_selection"):
        raise RuntimeError("Stage 22 reports lockbox candidate selection")
    if stage23_manifest.get("lockbox_policy", {}).get("lockbox_used_for_selection"):
        raise RuntimeError("Stage 23 reports lockbox selection")


def _build_frontier() -> pd.DataFrame:
    ledger = pd.read_parquet(STAGE22_ROOT / "trial_ledger.parquet")
    metrics = pd.read_parquet(STAGE22_ROOT / "trial_fold_metrics.parquet")
    aggregate = metrics.groupby(["trial_id", "split_role"], sort=True).agg(rmse_mean=("rmse", "mean"), mae_mean=("mae", "mean")).reset_index()
    pivot = aggregate.pivot(index="trial_id", columns="split_role", values=["rmse_mean", "mae_mean"])
    pivot.columns = [f"{role}_{metric.replace('_mean', '')}_mean" for metric, role in pivot.columns]
    pivot = pivot.reset_index()
    rows: list[dict[str, Any]] = []
    for record in ledger.to_dict("records"):
        params = json.loads(record["params_json"])
        rows.append({"trial_id": int(record["trial_id"]), "n_estimators": int(params["n_estimators"]), "max_depth": int(params["max_depth"]), "learning_rate": float(params["learning_rate"]), "subsample": float(params["subsample"]), "colsample_bytree": float(params["colsample_bytree"])})
    params = pd.DataFrame.from_records(rows)
    frontier = ledger.merge(params, on="trial_id", validate="one_to_one").merge(pivot, on="trial_id", validate="one_to_one")
    frontier["validation_to_train_rmse_ratio"] = frontier["validation_rmse_mean"] / frontier["train_rmse_mean"]
    frontier["validation_to_train_mae_ratio"] = frontier["validation_mae_mean"] / frontier["train_mae_mean"]
    frontier["complexity_score"] = frontier["n_estimators"] * frontier["max_depth"]
    frontier["classic_overfit_flag"] = (frontier["validation_to_train_rmse_ratio"] > 1.25) | (frontier["validation_to_train_mae_ratio"] > 1.25)
    return frontier


def _build_split_summary() -> pd.DataFrame:
    metrics = pd.read_parquet(STAGE23_ROOT / "metrics.parquet")
    deltas = pd.read_parquet(STAGE23_ROOT / "hurdle_deltas.parquet")
    gap_rows: list[dict[str, Any]] = []
    for (fold_id, horizon_id), group in metrics.groupby(["fold_id", "horizon_id"], sort=True):
        by_role = group.set_index("split_role")
        if "train" not in by_role.index or "validation" not in by_role.index:
            continue
        for metric in ["rmse", "mae"]:
            train = float(by_role.loc["train", metric])
            validation = float(by_role.loc["validation", metric])
            gap_rows.append({"fold_id": fold_id, "horizon_id": horizon_id, "metric": metric, "gap_flag": bool(validation > train * 1.25), "validation_to_train_ratio": validation / train if train else float("inf")})
    gaps = pd.DataFrame.from_records(gap_rows)
    summary = metrics.groupby("split_role", sort=True).agg(rmse_mean=("rmse", "mean"), mae_mean=("mae", "mean"), row_count=("row_count", "sum")).reset_index()
    rates = deltas.groupby("split_role", sort=True).agg(both_metric_improvement_rate=("both_metrics_improve", "mean"), rmse_delta_mean=("rmse_delta_candidate_minus_hurdle", "mean"), mae_delta_mean=("mae_delta_candidate_minus_hurdle", "mean")).reset_index()
    summary = summary.merge(rates, on="split_role", how="left", validate="one_to_one")
    summary["train_validation_gap_flag_rate"] = float(gaps["gap_flag"].mean()) if not gaps.empty else 0.0
    summary["train_validation_gap_ratio_mean"] = float(gaps["validation_to_train_ratio"].mean()) if not gaps.empty else 0.0
    return summary


def _build_horizon_review() -> pd.DataFrame:
    deltas = pd.read_parquet(STAGE23_ROOT / "hurdle_deltas.parquet")
    return deltas.groupby(["split_role", "horizon_id"], sort=True).agg(fold_count=("fold_id", "nunique"), rmse_delta_mean=("rmse_delta_candidate_minus_hurdle", "mean"), mae_delta_mean=("mae_delta_candidate_minus_hurdle", "mean"), both_metric_improvement_rate=("both_metrics_improve", "mean")).reset_index()


def _classify_candidate(stage23_manifest: dict[str, Any], split_summary: pd.DataFrame) -> dict[str, Any]:
    by_split = split_summary.set_index("split_role")
    validation_rate = float(by_split.loc["validation", "both_metric_improvement_rate"])
    lockbox_rate = float(by_split.loc["lockbox", "both_metric_improvement_rate"])
    gap_rate = float(by_split.loc["validation", "train_validation_gap_flag_rate"])
    classification = classify_stage24_candidate(validation_rate, lockbox_rate, gap_rate, bool(stage23_manifest["lockbox_policy"]["lockbox_used_for_selection"]))
    classification.update(
        {
            "validation_both_metric_improvement_rate": validation_rate,
            "lockbox_both_metric_improvement_rate": lockbox_rate,
            "train_validation_gap_flag_rate": gap_rate,
            "positive_claim_approved": False,
            "required_follow_up": ["Stage 25 uncertainty/block-bootstrap evidence", "Stage 35 full diagnostic battery", "Stage 39 final benchmark claim review"],
        }
    )
    return classification


def _render_report(manifest: dict[str, Any], split_summary: pd.DataFrame, horizon_review: pd.DataFrame) -> str:
    classification = manifest["classification"]
    by_split = split_summary.set_index("split_role")
    horizon_lockbox = horizon_review[horizon_review["split_role"] == "lockbox"]
    horizon_lines = "\n".join(
        f"| `{row.horizon_id}` | {row.rmse_delta_mean} | {row.mae_delta_mean} | {row.both_metric_improvement_rate} |"
        for row in horizon_lockbox.itertuples(index=False)
    )
    return f"""# Stage 24 XGBoost Overfit Frontier And Promotion Review

Status: completed; conservative classification recorded without claim approval

Updated: 2026-05-24

Run ID: `{manifest['run_id']}`

## Classification

| Field | Value |
| --- | --- |
| Candidate classification | `{classification['classification']}` |
| Promotion review recommended | `{str(classification['promotion_review_recommended']).lower()}` |
| Positive claim approved | `false` |
| Reason | {classification['reason']} |

## Split Summary

| Split | Both-metric improvement rate | Mean RMSE delta | Mean MAE delta |
| --- | ---: | ---: | ---: |
| Validation | {by_split.loc['validation', 'both_metric_improvement_rate']} | {by_split.loc['validation', 'rmse_delta_mean']} | {by_split.loc['validation', 'mae_delta_mean']} |
| Lockbox | {by_split.loc['lockbox', 'both_metric_improvement_rate']} | {by_split.loc['lockbox', 'rmse_delta_mean']} | {by_split.loc['lockbox', 'mae_delta_mean']} |

Train-validation gap flag rate is {classification['train_validation_gap_flag_rate']}.

## Lockbox Horizon Review

| Horizon | Mean RMSE delta | Mean MAE delta | Both-metric improvement rate |
| --- | ---: | ---: | ---: |
{horizon_lines}

## Non-Claims

This review may recommend later promotion review, but it does not approve positive claims, Stage 6 reinterpretation, trading signals, or benchmark-comparability promotion. Stage 39 remains the claim-language gate.
"""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    main()
