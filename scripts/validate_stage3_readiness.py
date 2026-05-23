#!/usr/bin/env python3
"""Validate Stage 3 feature/label implementation readiness.

This gate rechecks Stage 3 after Stage 2 materialization. It does not create
features, labels, executable feature tests, active configs, splits, models, or
benchmark results.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_FAMILY_ROOT = PROJECT_ROOT / "data" / "datasets" / "phase1_top50"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage3_feature_label_pipeline_readiness_2026-05-14.json"

APPROVED_HORIZONS = ["1d", "5d", "10d", "20d", "60d"]
FEATURE_TEST_PATHS = [
    PROJECT_ROOT / "tests" / "features" / "test_market_features_contract.py",
    PROJECT_ROOT / "tests" / "features" / "test_news_alignment_contract.py",
    PROJECT_ROOT / "tests" / "features" / "test_event_state_contract.py",
    PROJECT_ROOT / "tests" / "features" / "test_no_news_state_contract.py",
    PROJECT_ROOT / "tests" / "features" / "test_labels_contract.py",
]
FEATURE_SOURCE_PATHS = [
    PROJECT_ROOT / "src" / "event_state_forecasting" / "cli" / "build_features_and_labels.py",
    PROJECT_ROOT / "src" / "event_state_forecasting" / "features" / "embeddings.py",
    PROJECT_ROOT / "src" / "event_state_forecasting" / "features" / "market.py",
    PROJECT_ROOT / "src" / "event_state_forecasting" / "features" / "news_alignment.py",
    PROJECT_ROOT / "src" / "event_state_forecasting" / "features" / "event_state.py",
    PROJECT_ROOT / "src" / "event_state_forecasting" / "features" / "no_news_state.py",
    PROJECT_ROOT / "src" / "event_state_forecasting" / "features" / "labels.py",
]
CONFIG_PATHS = [
    PROJECT_ROOT / "configs" / "features.yaml",
    PROJECT_ROOT / "configs" / "labels.yaml",
]


@dataclass(frozen=True, slots=True)
class ReadinessCheck:
    name: str
    required_for_implementation: bool
    ready: bool
    blocking: bool
    evidence: list[str]
    details: dict[str, Any]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 3 readiness without building feature/label artifacts.")
    parser.add_argument("--dataset-root", default=str(DEFAULT_DATASET_FAMILY_ROOT), help="Stage 2 dataset version root or family root.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for machine-readable Stage 3 readiness JSON.")
    parser.add_argument("--write", action="store_true", help="Write readiness JSON to --output.")
    parser.add_argument("--json", action="store_true", help="Print full readiness JSON instead of compact text.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless Stage 3 implementation preconditions are ready.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    dataset_root = find_dataset_root(Path(args.dataset_root))
    summary = build_summary(dataset_root)
    output_path = resolve_project_path(args.output)
    summary["output_path"] = str(output_path)

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print_summary(summary, as_json=args.json)
    if args.strict and summary["status"] != "ready_for_stage3_implementation":
        return 2
    return 0


def build_summary(dataset_root: Path | None) -> dict[str, Any]:
    manifest_path = dataset_root / "dataset_manifest.json" if dataset_root else None
    row_digest_path = dataset_root / "row_universe_digest.json" if dataset_root else None
    clean_window_path = dataset_root / "clean_window_decision.json" if dataset_root else None
    panel_path = dataset_root / "benchmark_panel.parquet" if dataset_root else None

    manifest = read_json_if_exists(manifest_path)
    row_digest = read_json_if_exists(row_digest_path)
    clean_window = read_json_if_exists(clean_window_path)

    checks = [
        check_stage2_dataset_artifacts(dataset_root, manifest_path, row_digest_path, clean_window_path, panel_path, manifest, clean_window),
        check_stage2_row_universe(manifest, row_digest),
        check_stage2_provider_flags(manifest),
        check_feature_label_tests(),
        check_feature_source_implementation(),
        check_active_feature_label_configs(),
        check_label_reference_contract(manifest),
        check_event_state_contract(),
    ]
    blockers = [item.name for item in checks if item.required_for_implementation and item.blocking]
    stage2_ready = all(item.ready for item in checks if item.name in {"stage2_dataset_artifacts", "stage2_row_universe_identity"})

    if not stage2_ready:
        status = "blocked_missing_stage2_prerequisites"
    elif blockers:
        status = "blocked_stage3_implementation_preconditions_not_met"
    else:
        status = "ready_for_stage3_implementation"

    return {
        "artifact_type": "stage3_feature_label_pipeline_readiness",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": status,
        "benchmark_claim": False,
        "stage2_dataset_ready": stage2_ready,
        "stage3_implementation_ready": status == "ready_for_stage3_implementation",
        "feature_artifacts_created": False,
        "label_artifacts_created": False,
        "split_artifacts_created": False,
        "model_artifacts_created": False,
        "stage4_ready": False,
        "dataset_root": None if dataset_root is None else str(dataset_root),
        "dataset_version": nested_get(manifest, ["identity", "dataset_version"]),
        "row_count": nested_get(manifest, ["coverage", "row_count"]),
        "row_universe_digest": nested_get(manifest, ["hashes", "row_universe_digest"]),
        "clean_window": nested_get(manifest, ["clean_window"]),
        "implementation_blockers": blockers,
        "readiness_checks": [asdict(item) for item in checks],
        "required_future_executable_tests": [path.relative_to(PROJECT_ROOT).as_posix() for path in FEATURE_TEST_PATHS],
        "non_claims": [
            "not_market_feature_artifacts",
            "not_event_state_feature_artifacts",
            "not_label_artifacts",
            "not_splits_models_predictions_metrics_benchmark_runner_or_benchmark_result",
        ],
    }


def check_stage2_dataset_artifacts(
    dataset_root: Path | None,
    manifest_path: Path | None,
    row_digest_path: Path | None,
    clean_window_path: Path | None,
    panel_path: Path | None,
    manifest: dict[str, Any] | None,
    clean_window: dict[str, Any] | None,
) -> ReadinessCheck:
    paths = [path for path in [manifest_path, row_digest_path, clean_window_path, panel_path] if path is not None]
    missing = [str(path) for path in paths if not path.exists()]
    ready = (
        dataset_root is not None
        and not missing
        and nested_get(manifest, ["identity", "materialized_dataset_created"]) is True
        and nested_get(manifest, ["identity", "stage2_completion_status"]) == "materialized_stage2_dataset_complete"
        and nested_get(manifest, ["identity", "benchmark_claim"]) is False
        and nested_get(clean_window, ["status"]) == "selected_for_stage2_materialized_dataset"
    )
    return ReadinessCheck(
        name="stage2_dataset_artifacts",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(path) for path in paths],
        details={
            "dataset_root": None if dataset_root is None else str(dataset_root),
            "missing_paths": missing,
            "stage2_completion_status": nested_get(manifest, ["identity", "stage2_completion_status"]),
            "materialized_dataset_created": nested_get(manifest, ["identity", "materialized_dataset_created"]),
            "benchmark_claim": nested_get(manifest, ["identity", "benchmark_claim"]),
            "clean_window_status": nested_get(clean_window, ["status"]),
        },
    )


def check_stage2_row_universe(manifest: dict[str, Any] | None, row_digest: dict[str, Any] | None) -> ReadinessCheck:
    manifest_horizons = nested_get(manifest, ["protected_scope", "horizons"])
    digest_horizons = sorted((nested_get(row_digest, ["horizon_counts"]) or {}).keys(), key=horizon_sort_key)
    ready = (
        nested_get(manifest, ["coverage", "row_count"]) == nested_get(row_digest, ["row_count"])
        and nested_get(manifest, ["hashes", "row_universe_digest"]) == nested_get(row_digest, ["row_universe_digest"])
        and nested_get(row_digest, ["branch_row_universe_equal"]) is True
        and manifest_horizons == APPROVED_HORIZONS
        and digest_horizons == APPROVED_HORIZONS
    )
    return ReadinessCheck(
        name="stage2_row_universe_identity",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=[],
        details={
            "manifest_row_count": nested_get(manifest, ["coverage", "row_count"]),
            "digest_row_count": nested_get(row_digest, ["row_count"]),
            "manifest_row_universe_digest": nested_get(manifest, ["hashes", "row_universe_digest"]),
            "digest_row_universe_digest": nested_get(row_digest, ["row_universe_digest"]),
            "branch_row_universe_equal": nested_get(row_digest, ["branch_row_universe_equal"]),
            "approved_horizons": APPROVED_HORIZONS,
            "manifest_horizons": manifest_horizons,
            "digest_horizons": digest_horizons,
        },
    )


def check_stage2_provider_flags(manifest: dict[str, Any] | None) -> ReadinessCheck:
    availability = nested_get(manifest, ["availability"]) or {}
    ready = all(
        key in availability
        for key in [
            "rows_with_news_count",
            "no_news_row_count",
            "provider_empty_feed_row_count",
            "provider_truncation_risk_row_count",
        ]
    )
    return ReadinessCheck(
        name="stage2_no_news_and_provider_flags",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=[],
        details={
            "rows_with_news_count": availability.get("rows_with_news_count"),
            "no_news_row_count": availability.get("no_news_row_count"),
            "provider_empty_feed_row_count": availability.get("provider_empty_feed_row_count"),
            "provider_truncation_risk_row_count": availability.get("provider_truncation_risk_row_count"),
            "provider_level_article_completeness_claim": False,
        },
    )


def check_feature_label_tests() -> ReadinessCheck:
    statuses = {path.relative_to(PROJECT_ROOT).as_posix(): python_file_status(path) for path in FEATURE_TEST_PATHS}
    ready = all(status == "executable" for status in statuses.values())
    return ReadinessCheck(
        name="executable_stage3_feature_label_tests",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(path) for path in FEATURE_TEST_PATHS],
        details={"file_statuses": statuses},
    )


def check_feature_source_implementation() -> ReadinessCheck:
    statuses = {path.relative_to(PROJECT_ROOT).as_posix(): python_file_status(path) for path in FEATURE_SOURCE_PATHS}
    ready = all(status == "executable" for status in statuses.values())
    return ReadinessCheck(
        name="feature_label_source_implementation",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(path) for path in FEATURE_SOURCE_PATHS],
        details={"file_statuses": statuses},
    )


def check_active_feature_label_configs() -> ReadinessCheck:
    statuses = {path.relative_to(PROJECT_ROOT).as_posix(): text_file_status(path) for path in CONFIG_PATHS}
    active_configs = [path for path, status in statuses.items() if status == "active_content"]
    ready = len(active_configs) == len(CONFIG_PATHS)
    return ReadinessCheck(
        name="active_feature_label_configs_and_contracts",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(path) for path in CONFIG_PATHS],
        details={
            "file_statuses": statuses,
            "status": "active_configs_present" if ready else "missing_or_comment_only_configs",
            "required_resolution": "freeze executable Stage 3 feature, alignment, no-news, event-state, and label contracts before implementation",
        },
    )


def check_label_reference_contract(manifest: dict[str, Any] | None) -> ReadinessCheck:
    labels_config = read_json_if_exists(PROJECT_ROOT / "configs" / "labels.yaml") or {}
    support_ticker = nested_get(manifest, ["coverage", "support_ticker"])
    ready = (
        labels_config.get("target_family") == "forward_excess_returns"
        and labels_config.get("return_type") == "simple"
        and labels_config.get("reference_policy") == "leave_one_out_equal_weight_approved_universe"
        and labels_config.get("formula") == "ticker_forward_simple_return_minus_leave_one_out_equal_weight_universe_forward_simple_return"
    )
    return ReadinessCheck(
        name="label_reference_formula_contract",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=["configs/labels.yaml", "data/datasets/phase1_top50/*/dataset_manifest.json"],
        details={
            "stage2_support_ticker": support_ticker,
            "selected_reference_policy": labels_config.get("reference_policy"),
            "selected_return_type": labels_config.get("return_type"),
            "status": "frozen_in_active_labels_config" if ready else "blocked_label_contract_not_frozen",
            "required_resolution": "freeze close-to-close return formula, benchmark reference handling, endpoint-null policy, and label artifact schema in executable tests/contracts",
        },
    )


def check_event_state_contract() -> ReadinessCheck:
    features_config = read_json_if_exists(PROJECT_ROOT / "configs" / "features.yaml") or {}
    embeddings = features_config.get("embeddings", {}) if isinstance(features_config.get("embeddings"), dict) else {}
    event_state = features_config.get("event_state", {}) if isinstance(features_config.get("event_state"), dict) else {}
    scalars = event_state.get("scalar_enrichments", []) if isinstance(event_state.get("scalar_enrichments"), list) else []
    required_scalars = {
        "stage3_aligned_news_count",
        "no_news_flag",
        "empty_event_state_flag",
        "provider_empty_feed_flag",
        "provider_truncation_risk_flag",
        "minutes_since_latest_aligned_article",
    }
    ready = (
        embeddings.get("model_id") == "deterministic_hash_embedding_v1"
        and embeddings.get("dimension") == 8
        and embeddings.get("pooling_policy") == "mean"
        and required_scalars.issubset(set(scalars))
        and event_state.get("empty_vector_policy") == "zero_vector"
    )
    return ReadinessCheck(
        name="event_state_embedding_and_scalar_contract",
        required_for_implementation=True,
        ready=ready,
        blocking=not ready,
        evidence=["configs/features.yaml", "src/event_state_forecasting/features/event_state.py"],
        details={
            "embedding_model_id": embeddings.get("model_id"),
            "embedding_dimension": embeddings.get("dimension"),
            "pooling_policy": embeddings.get("pooling_policy"),
            "scalar_enrichments": scalars,
            "status": "frozen_in_active_features_config" if ready else "blocked_embedding_model_pooling_policy_and_scalar_enrichment_set_not_frozen",
            "required_resolution": "freeze embedding model id, text normalization, pooling policy, scalar enrichment roster, no-news encoding, and manifest metadata in executable tests/contracts",
        },
    )


def find_dataset_root(path: Path) -> Path | None:
    resolved = resolve_project_path(str(path))
    if (resolved / "dataset_manifest.json").exists():
        return resolved
    if not resolved.exists():
        return None
    candidates = sorted((child for child in resolved.iterdir() if (child / "dataset_manifest.json").exists()), key=lambda item: item.stat().st_mtime)
    if not candidates:
        return None
    return candidates[-1]


def read_json_if_exists(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        return None
    return value


def python_file_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    return "executable" if has_non_comment_content(path) else "comment_only"


def text_file_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    return "active_content" if has_non_comment_content(path) else "comment_only"


def has_non_comment_content(path: Path) -> bool:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return True
    return False


def nested_get(value: dict[str, Any] | None, keys: list[str]) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def horizon_sort_key(value: str) -> int:
    return int(value[:-1]) if value.endswith("d") and value[:-1].isdigit() else 10_000


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print("STAGE3 READINESS")
    print(f"status: {summary['status']}")
    print(f"stage2_dataset_ready: {summary['stage2_dataset_ready']}")
    print(f"stage3_implementation_ready: {summary['stage3_implementation_ready']}")
    for item in summary["readiness_checks"]:
        mark = "ready" if item["ready"] else "blocked" if item["blocking"] else "not_ready"
        print(f"{item['name']}: {mark}")
    if summary["implementation_blockers"]:
        print("blocking_preconditions: " + ", ".join(summary["implementation_blockers"]))
    print(f"output: {summary['output_path']}")


if __name__ == "__main__":
    raise SystemExit(main())
