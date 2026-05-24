"""Run Stage 7 contextual-bandit development replay diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

from event_state_forecasting.stage7.artifacts import Stage7ArtifactError, write_stage7_artifacts
from event_state_forecasting.stage7.config import load_stage7_config
from event_state_forecasting.stage7.context import load_stage7_context
from event_state_forecasting.stage7.data_update import archive_deprecated_settings, build_stage7_data_update_plan
from event_state_forecasting.stage7.final_execution import build_final_execution_stub
from event_state_forecasting.stage7.replay import build_replay_validation, run_development_replay


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEATURE_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
SPLIT_VERSION = f"{FEATURE_VERSION}__stage4_splits_v1"
STAGE5_VERSION = f"{SPLIT_VERSION}__stage5_models_v1"
STAGE7_VERSION = f"{STAGE5_VERSION}__stage7_contextual_bandit_v1"
FEATURE_ROOT = PROJECT_ROOT / "data" / "features" / "phase1_top50" / FEATURE_VERSION
SPLIT_ROOT = PROJECT_ROOT / "data" / "splits" / "phase1_top50" / SPLIT_VERSION
MODEL_ROOT = PROJECT_ROOT / "data" / "models" / "phase1_top50" / STAGE5_VERSION
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "stage7_contextual_bandit" / "phase1_top50" / STAGE7_VERSION


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Stage 7 contextual-bandit development replay diagnostics.")
    parser.add_argument("--feature-root", type=Path, default=FEATURE_ROOT)
    parser.add_argument("--split-root", type=Path, default=SPLIT_ROOT)
    parser.add_argument("--model-root", type=Path, default=MODEL_ROOT)
    parser.add_argument("--model-config", type=Path, default=PROJECT_ROOT / "configs" / "models.yaml")
    parser.add_argument("--stage7-config", type=Path, default=PROJECT_ROOT / "configs" / "stage7_contextual_bandit.yaml")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--split-roles", default="validation", help="Comma-separated split roles to evaluate; default excludes lockbox.")
    parser.add_argument("--smoke-date-limit", type=int, default=None, help="Limit dates per fold/horizon for functionality tests.")
    parser.add_argument("--archive-deprecated-settings", action="store_true")
    parser.add_argument("--write-final-execution-stub", action="store_true", default=True)
    parser.add_argument("--target-data-update-end-date", default=None)
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        config = load_stage7_config(args.stage7_config)
        model_config = load_yaml_or_json(args.model_config)
        split_roles = parse_split_roles(args.split_roles)
        context = load_stage7_context(
            feature_root=args.feature_root,
            split_root=args.split_root,
            model_root=args.model_root,
            model_config=model_config,
            stage7_config=config,
            split_roles=split_roles,
            smoke_date_limit=args.smoke_date_limit,
        )
        selections, metrics, policy_manifest = run_development_replay(context, config)
        allow_new_holdout = set(split_roles) == {"lockbox"} and bool(config["protocol"].get("post_lockbox_holdout_evaluation_allowed"))
        replay_validation = build_replay_validation(
            context,
            selections,
            metrics,
            allow_new_post_lockbox_holdout=allow_new_holdout,
        )
        data_update_plan = build_stage7_data_update_plan(
            PROJECT_ROOT,
            config,
            target_end_date=args.target_data_update_end_date,
            new_holdout_materialized=allow_new_holdout,
        )
        archive_manifest = None
        if args.archive_deprecated_settings:
            archive_manifest = archive_deprecated_settings(PROJECT_ROOT, Path(data_update_plan["deprecated_settings_archive"]))
        final_stub = build_final_execution_stub(args.output_root / "final_execution_stub", config) if args.write_final_execution_stub else None
        manifest = write_stage7_artifacts(
            output_root=args.output_root,
            config=config,
            context=context,
            selections=selections,
            metrics=metrics,
            policy_manifest=policy_manifest,
            replay_validation=replay_validation,
            data_update_plan=data_update_plan,
            deprecated_archive_manifest=archive_manifest,
            final_execution_stub=final_stub,
            inputs={
                "feature_root": str(args.feature_root),
                "split_root": str(args.split_root),
                "model_root": str(args.model_root),
                "model_config": str(args.model_config),
                "stage7_config": str(args.stage7_config),
                "split_roles": ",".join(split_roles),
            },
            allow_overwrite=args.allow_overwrite,
        )
    except (Stage7ArtifactError, ValueError, RuntimeError) as exc:
        print(f"STAGE7_CONTEXTUAL_BANDIT_FAILED: {exc}", file=sys.stderr)
        return 2

    summary = {
        "status": manifest["stage7_status"],
        "benchmark_claim": manifest["benchmark_claim"],
        "artifact_root": str(args.output_root),
        "context_rows": manifest["counts"]["context_rows"],
        "selection_rows": manifest["counts"]["selection_rows"],
        "metric_rows": manifest["counts"]["metric_rows"],
        "replay_validation_status": manifest["replay_validation_status"],
        "data_update_status": manifest["data_update_status"],
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("STAGE7 CONTEXTUAL BANDIT")
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise RuntimeError(f"expected mapping in {path}")
    return data


def parse_split_roles(value: str) -> tuple[str, ...]:
    roles = tuple(role.strip() for role in value.split(",") if role.strip())
    if not roles:
        raise RuntimeError("at least one split role is required")
    allowed = {"validation", "lockbox"}
    unsupported = sorted(set(roles) - allowed)
    if unsupported:
        raise RuntimeError(f"unsupported Stage 7 split roles: {unsupported}")
    return roles


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
