#!/usr/bin/env python3
"""Validate Stage 7 contextual-bandit development replay artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGE5_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1"
STAGE7_VERSION = f"{STAGE5_VERSION}__stage7_contextual_bandit_v1"
DEFAULT_STAGE7_ROOT = PROJECT_ROOT / "data" / "stage7_contextual_bandit" / "phase1_top50" / STAGE7_VERSION
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage7_completion_validation_2026-05-22.json"
REQUIRED_METRIC_COLUMNS = {
    "policy_id",
    "policy_family",
    "k",
    "horizon_id",
    "fold_id",
    "row_filter_track",
    "top_k_mean_forward_excess_return",
    "bottom_k_mean_forward_excess_return",
    "top_minus_bottom_forward_excess_return_spread",
    "trading_signal_approved",
    "spread_is_trading_pnl",
    "benchmark_claim",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 7 completion artifacts.")
    parser.add_argument("--stage7-root", type=Path, default=DEFAULT_STAGE7_ROOT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = validate_stage7(args.stage7_root)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "passed":
        print("STAGE7_COMPLETION_VALIDATION FAILED")
        for blocker in result["blockers"]:
            print(f"- {blocker}")
        return 1
    print("STAGE7_COMPLETION_VALIDATION PASSED")
    print("metric_rows:", result["metric_rows"])
    print("selection_rows:", result["selection_rows"])
    return 0


def validate_stage7(stage7_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    required_files = {
        "stage7_manifest": stage7_root / "stage7_manifest.json",
        "resolved_stage7_config": stage7_root / "resolved_stage7_config.json",
        "context_schema": stage7_root / "context_schema.json",
        "policy_manifest": stage7_root / "policy_manifest.parquet",
        "policy_selections": stage7_root / "policy_selections.parquet",
        "policy_metrics": stage7_root / "policy_metrics.parquet",
        "replay_validation": stage7_root / "replay_validation.json",
        "data_update_plan": stage7_root / "data_update_plan.json",
    }
    for name, path in required_files.items():
        if not path.exists():
            blockers.append(f"missing_{name}")

    manifest: dict[str, Any] = {}
    replay_validation: dict[str, Any] = {}
    data_update_plan: dict[str, Any] = {}
    metric_rows = 0
    selection_rows = 0
    policy_count = 0
    if not blockers:
        manifest = load_json(required_files["stage7_manifest"])
        replay_validation = load_json(required_files["replay_validation"])
        data_update_plan = load_json(required_files["data_update_plan"])
        metrics = pd.read_parquet(required_files["policy_metrics"])
        selections = pd.read_parquet(required_files["policy_selections"])
        policy_manifest = pd.read_parquet(required_files["policy_manifest"])
        metric_rows = int(len(metrics))
        selection_rows = int(len(selections))
        policy_count = int(policy_manifest["policy_id"].nunique()) if "policy_id" in policy_manifest else 0

        if manifest.get("artifact_schema_version") != "stage7_contextual_bandit_v1":
            blockers.append("manifest_schema_mismatch")
        allowed_stage7_statuses = {
            "stage7_development_replay_diagnostics_created",
            "stage7_new_post_lockbox_holdout_diagnostics_created",
        }
        if manifest.get("stage7_status") not in allowed_stage7_statuses:
            blockers.append("stage7_status_not_created")
        if manifest.get("benchmark_claim") is not False:
            blockers.append("stage7_manifest_unexpected_benchmark_claim")
        if replay_validation.get("status") != "passed":
            blockers.append("replay_validation_not_passed")
        if replay_validation.get("lockbox_used_for_design") is not False:
            blockers.append("lockbox_used_for_design")
        allowed_data_update_statuses = {
            "planned_not_materialized",
            "raw_ohlcv_updated_new_holdout_not_materialized",
            "raw_ohlcv_updated_new_post_lockbox_holdout_materialized_diagnostics_only",
        }
        if data_update_plan.get("status") not in allowed_data_update_statuses:
            blockers.append("unexpected_data_update_status")
        missing_metric_columns = REQUIRED_METRIC_COLUMNS - set(metrics.columns)
        if missing_metric_columns:
            blockers.append(f"metrics_missing_columns:{sorted(missing_metric_columns)}")
        if metric_rows == 0 or selection_rows == 0:
            blockers.append("empty_stage7_artifacts")
        if bool(metrics["trading_signal_approved"].any()) or bool(selections["trading_signal_approved"].any()):
            blockers.append("trading_signal_unexpectedly_approved")
        if bool(metrics["spread_is_trading_pnl"].any()):
            blockers.append("spread_marked_as_trading_pnl")
        if "lockbox" in set(selections.get("split_role", [])) and replay_validation.get("new_post_lockbox_holdout_mode") is not True:
            blockers.append("lockbox_rows_in_policy_outputs")

    return {
        "artifact_type": "stage7_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed" if not blockers else "failed",
        "stage7_root": str(stage7_root),
        "benchmark_claim": False,
        "metric_rows": metric_rows,
        "selection_rows": selection_rows,
        "policy_count": policy_count,
        "replay_validation_status": replay_validation.get("status"),
        "data_update_status": data_update_plan.get("status"),
        "blockers": blockers,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"expected object in {path}")
    return data


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
