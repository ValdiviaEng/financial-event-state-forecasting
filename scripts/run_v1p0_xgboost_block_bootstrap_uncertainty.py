from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.xgboost_search import (  # noqa: E402
    build_stage25_paired_loss_table,
    stage25_delta_intervals,
    stage25_generalization_gap_intervals,
    stage25_uncertainty_comparison,
)


STAGE19_ROOT = PROJECT_ROOT / "data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z"
STAGE23_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80"
STAGE24_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_AT_UTC = "2026-05-24T09:05:00Z"
SOURCE_ID = "6dff1bd"
BLOCK_LENGTH = 5
RESAMPLE_COUNT = 1000
SEED = 20260524


def main() -> None:
    parser = argparse.ArgumentParser(description="Run v1p0 Stage 25 block-bootstrap uncertainty evidence for the frozen XGBoost candidate.")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--resample-count", type=int, default=RESAMPLE_COUNT)
    parser.add_argument("--block-length", type=int, default=BLOCK_LENGTH)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    stage23_manifest = json.loads((STAGE23_ROOT / "final_evaluation_manifest.json").read_text(encoding="utf-8"))
    stage24_manifest = json.loads((STAGE24_ROOT / "review_manifest.json").read_text(encoding="utf-8"))
    _validate_sources(stage23_manifest, stage24_manifest)

    run_id = f"v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_{SOURCE_ID}__run_{stage23_manifest['best_config_digest_sha256'][:8]}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    candidate_predictions = pd.read_parquet(STAGE23_ROOT / "saved_predictions.parquet")
    hurdle_predictions = pd.read_parquet(STAGE19_ROOT / "saved_predictions.parquet")
    paired_losses = build_stage25_paired_loss_table(candidate_predictions, hurdle_predictions)
    paired_schema = {
        "paired_loss_rows": int(len(paired_losses)),
        "split_role_counts": {str(k): int(v) for k, v in paired_losses["split_role"].value_counts().sort_index().to_dict().items()},
        "horizon_count": int(paired_losses["horizon_id"].nunique()),
    }

    block_intervals = stage25_delta_intervals(paired_losses, block_length=args.block_length, resample_count=args.resample_count, seed=args.seed, method="moving_block_bootstrap")
    date_clustered_intervals = stage25_delta_intervals(paired_losses, block_length=1, resample_count=args.resample_count, seed=args.seed, method="date_clustered_bootstrap")
    uncertainty_comparison = stage25_uncertainty_comparison(block_intervals, date_clustered_intervals)
    generalization_gaps = stage25_generalization_gap_intervals(paired_losses, block_length=args.block_length, resample_count=args.resample_count, seed=args.seed)
    classification = _classify_uncertainty(block_intervals, generalization_gaps, stage24_manifest["classification"])

    paired_path = output_root / "paired_candidate_hurdle_losses.parquet"
    block_path = output_root / "block_bootstrap_intervals.parquet"
    date_path = output_root / "date_clustered_intervals.parquet"
    comparison_path = output_root / "uncertainty_method_comparison.parquet"
    gaps_path = output_root / "train_oos_generalization_gap_intervals.parquet"
    manifest_path = output_root / "uncertainty_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage25_block_bootstrap_uncertainty_report.md"

    paired_losses.to_parquet(paired_path, index=False)
    block_intervals.to_parquet(block_path, index=False)
    date_clustered_intervals.to_parquet(date_path, index=False)
    uncertainty_comparison.to_parquet(comparison_path, index=False)
    generalization_gaps.to_parquet(gaps_path, index=False)

    outputs = {
        "paired_candidate_hurdle_losses": _rel(paired_path),
        "block_bootstrap_intervals": _rel(block_path),
        "date_clustered_intervals": _rel(date_path),
        "uncertainty_method_comparison": _rel(comparison_path),
        "train_oos_generalization_gap_intervals": _rel(gaps_path),
        "uncertainty_manifest": _rel(manifest_path),
        "run_manifest": _rel(run_manifest_path),
        "report": _rel(report_path),
    }
    manifest = {
        "artifact_type": "v1p0_stage25_block_bootstrap_uncertainty_manifest",
        "artifact_id": f"xgboost_stage25_block_bootstrap_uncertainty__stage24_{stage23_manifest['best_config_digest_sha256'][:12]}__20260524T090500Z",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed",
        "source_stage19_artifact_id": "market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z",
        "source_stage23_artifact_id": stage23_manifest["artifact_id"],
        "source_stage24_artifact_id": stage24_manifest["artifact_id"],
        "bootstrap_config": {
            "block_unit": "as_of_date within split_role and horizon_id",
            "block_method": "moving block bootstrap over contiguous trading-date blocks",
            "block_length_trading_dates": int(args.block_length),
            "date_clustered_comparison_block_length": 1,
            "resample_count": int(args.resample_count),
            "seed": int(args.seed),
            "metrics": ["rmse_delta_candidate_minus_hurdle", "mae_delta_candidate_minus_hurdle"],
            "train_gap_policy": "diagnostic_only_not_claim_evidence",
        },
        "paired_loss_schema": paired_schema,
        "uncertainty_classification": classification,
        "outputs": outputs,
        "benchmark_claim": False,
        "promotion_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_positive_claim_approval", "not_stage6_reinterpretation", "not_trading_signal", "stage39_claim_review_required"],
    }
    _write_json(manifest_path, manifest)
    _write_json(
        run_manifest_path,
        {
            "run_id": run_id,
            "stage": 25,
            "stage_name": "block_bootstrap_uncertainty",
            "generated_at_utc": GENERATED_AT_UTC,
            "status": "completed",
            "command": "source ~/venvs/ai/bin/activate && python scripts/run_v1p0_xgboost_block_bootstrap_uncertainty.py",
            "outputs": outputs,
            "benchmark_claim": False,
            "promotion_claim": False,
            "positive_claim_approved": False,
        },
    )
    report_path.write_text(_render_report(manifest, block_intervals, uncertainty_comparison, generalization_gaps), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "completed",
                "uncertainty_classification": classification["uncertainty_classification"],
                "min_improvement_probability": classification["min_improvement_probability"],
                "diagnostic_overfit_pressure_flag_rate": classification["diagnostic_overfit_pressure_flag_rate"],
                "positive_claim_approved": False,
                "output_root": _rel(output_root),
            },
            sort_keys=True,
        )
    )


def _validate_sources(stage23_manifest: dict[str, Any], stage24_manifest: dict[str, Any]) -> None:
    if stage23_manifest.get("status") != "completed":
        raise RuntimeError("Stage 25 requires completed Stage 23 frozen final evaluation")
    if stage24_manifest.get("status") != "completed":
        raise RuntimeError("Stage 25 requires completed Stage 24 overfit review")
    if stage24_manifest.get("classification", {}).get("positive_claim_approved"):
        raise RuntimeError("Stage 25 expects Stage 24 to preserve positive_claim_approved=false")


def _classify_uncertainty(block_intervals: pd.DataFrame, generalization_gaps: pd.DataFrame, stage24_classification: dict[str, Any]) -> dict[str, Any]:
    review_rows = block_intervals[block_intervals["split_role"].isin(["validation", "lockbox"])]
    min_probability = float(review_rows["probability_candidate_improves"].min())
    interval_support_rate = float(review_rows["ci_excludes_zero_in_improvement_direction"].mean())
    lockbox_support_rate = float(review_rows[review_rows["split_role"] == "lockbox"]["ci_excludes_zero_in_improvement_direction"].mean())
    overfit_pressure_rate = float(generalization_gaps["diagnostic_overfit_pressure_flag"].mean()) if not generalization_gaps.empty else 0.0
    if min_probability < 0.5:
        label = "uncertainty_unstable"
        reason = "at least one horizon/metric has less than even bootstrap support for candidate improvement"
    elif overfit_pressure_rate > 0.75:
        label = "supportive_but_high_train_oos_gap_pressure"
        reason = "candidate-vs-hurdle intervals are supportive, but train-to-real-data gap pressure is high"
    elif interval_support_rate >= 0.5 and lockbox_support_rate >= 0.8:
        label = "supportive_nonclaim_uncertainty"
        reason = "moving-block bootstrap evidence supports most candidate-vs-hurdle deltas while preserving claim gates"
    else:
        label = "mixed_nonclaim_uncertainty"
        reason = "bootstrap evidence is directionally useful but not broad enough for positive claim language"
    return {
        "stage24_classification": stage24_classification.get("classification"),
        "uncertainty_classification": label,
        "reason": reason,
        "min_improvement_probability": min_probability,
        "interval_support_rate": interval_support_rate,
        "lockbox_interval_support_rate": lockbox_support_rate,
        "diagnostic_overfit_pressure_flag_rate": overfit_pressure_rate,
        "promotion_review_recommended": bool(stage24_classification.get("promotion_review_recommended")) and label != "uncertainty_unstable",
        "positive_claim_approved": False,
        "required_follow_up": ["Stage 35 full diagnostic battery", "Stage 39 final benchmark claim review"],
    }


def _render_report(manifest: dict[str, Any], block_intervals: pd.DataFrame, comparison: pd.DataFrame, gaps: pd.DataFrame) -> str:
    classification = manifest["uncertainty_classification"]
    by_split = block_intervals.groupby(["split_role", "metric"], sort=True).agg(
        min_probability=("probability_candidate_improves", "min"),
        mean_probability=("probability_candidate_improves", "mean"),
        support_rate=("ci_excludes_zero_in_improvement_direction", "mean"),
    )
    split_lines = "\n".join(
        f"| `{split}` | `{metric}` | {row.min_probability} | {row.mean_probability} | {row.support_rate} |"
        for (split, metric), row in by_split.iterrows()
    )
    gap_summary = gaps.groupby(["oos_split_role", "metric"], sort=True).agg(
        mean_ratio=("observed_oos_to_train_ratio", "mean"),
        pressure_rate=("diagnostic_overfit_pressure_flag", "mean"),
        mean_probability_oos_worse=("probability_oos_worse_than_train", "mean"),
    )
    gap_lines = "\n".join(
        f"| `{split}` | `{metric}` | {row.mean_ratio} | {row.pressure_rate} | {row.mean_probability_oos_worse} |"
        for (split, metric), row in gap_summary.iterrows()
    )
    comparison_summary = comparison.groupby("metric", sort=True).agg(mean_width_ratio=("ci_width_ratio_block_to_date_clustered", "mean"), sign_consistency_rate=("sign_consistent", "mean"))
    comparison_lines = "\n".join(f"| `{metric}` | {row.mean_width_ratio} | {row.sign_consistency_rate} |" for metric, row in comparison_summary.iterrows())
    config = manifest["bootstrap_config"]
    return f"""# Stage 25 Block-Bootstrap Uncertainty Evidence

Status: completed; uncertainty evidence recorded without positive claim approval

Updated: 2026-05-24

Run ID: `{manifest['run_id']}`

## Method

| Field | Value |
| --- | --- |
| Block unit | {config['block_unit']} |
| Block method | {config['block_method']} |
| Block length | {config['block_length_trading_dates']} trading dates |
| Resamples | {config['resample_count']} |
| Seed | {config['seed']} |
| Train-gap policy | {config['train_gap_policy']} |

## Classification

| Field | Value |
| --- | --- |
| Stage 24 classification | `{classification['stage24_classification']}` |
| Uncertainty classification | `{classification['uncertainty_classification']}` |
| Promotion review recommended | `{str(classification['promotion_review_recommended']).lower()}` |
| Positive claim approved | `false` |
| Reason | {classification['reason']} |

## Candidate-Vs-Hurdle Bootstrap Summary

| Split | Metric | Min improvement probability | Mean improvement probability | CI-support rate |
| --- | --- | ---: | ---: | ---: |
{split_lines}

## Train-To-Real-Data Gap Diagnostics

These are diagnostic-only overfit-pressure checks and are not claim evidence.

| OOS split | Metric | Mean OOS/train ratio | Pressure flag rate | Mean probability OOS worse |
| --- | --- | ---: | ---: | ---: |
{gap_lines}

## Method Comparison

| Metric | Mean block/date CI-width ratio | Sign consistency rate |
| --- | ---: | ---: |
{comparison_lines}

## Non-Claims

This packet strengthens uncertainty and overfit-pressure evidence, but it does not approve positive claims, Stage 6 reinterpretation, trading signals, or benchmark-comparability promotion. Stage 39 remains the claim-language gate.
"""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    main()
