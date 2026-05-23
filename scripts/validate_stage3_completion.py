#!/usr/bin/env python3
"""Validate materialized Stage 3 feature and label artifacts."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID, ROW_KEY_FIELDS, TARGET_FAMILY  # noqa: E402
from event_state_forecasting.dataset.row_universe import row_universe_digest  # noqa: E402
from event_state_forecasting.features.labels import LABEL_REFERENCE_POLICY, LABEL_RETURN_TYPE  # noqa: E402


DEFAULT_ARTIFACT_FAMILY_ROOT = PROJECT_ROOT / "data" / "features" / BENCHMARK_FAMILY_ID
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage3_completion_validation_2026-05-15.json"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a materialized Stage 3 feature/label artifact set.")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_FAMILY_ROOT), help="Stage 3 artifact root or family root.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for completion-validation JSON.")
    parser.add_argument("--write", action="store_true", help="Write completion-validation JSON.")
    parser.add_argument("--json", action="store_true", help="Print full validation JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        summary = validate_stage3_completion(resolve_artifact_root(Path(args.artifact_root)))
    except (ValueError, FileNotFoundError) as exc:
        summary = {
            "artifact_type": "stage3_completion_validation",
            "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "status": "failed",
            "error": str(exc),
        }
        print_summary(summary, as_json=args.json)
        return 2

    output_path = resolve_project_path(args.output)
    summary["output_path"] = str(output_path)
    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print_summary(summary, as_json=args.json)
    return 0


def validate_stage3_completion(artifact_root: Path) -> dict[str, Any]:
    manifest_path = artifact_root / "feature_label_manifest.json"
    row_digest_path = artifact_root / "row_universe_digest.json"
    market_path = artifact_root / "market_features.parquet"
    event_path = artifact_root / "event_state_features.parquet"
    labels_path = artifact_root / "labels.parquet"
    aligned_news_path = artifact_root / "aligned_news.parquet"
    required_paths = [manifest_path, row_digest_path, market_path, event_path, labels_path, aligned_news_path]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing Stage 3 artifact(s): {missing}")

    manifest = read_json(manifest_path)
    row_digest_record = read_json(row_digest_path)
    market = pd.read_parquet(market_path)
    event_state = pd.read_parquet(event_path)
    labels = pd.read_parquet(labels_path)
    aligned_news = pd.read_parquet(aligned_news_path)

    expected_digest = row_digest_record.get("stage2_row_universe_digest")
    digests = {
        "market_features": row_universe_digest(market.to_dict("records")),
        "event_state_features": row_universe_digest(event_state.to_dict("records")),
        "labels": row_universe_digest(labels.to_dict("records")),
    }
    if any(value != expected_digest for value in digests.values()):
        raise ValueError(f"row-universe digest mismatch: {digests}; expected {expected_digest}")
    if len(market) != len(event_state) or len(market) != len(labels):
        raise ValueError("Stage 3 artifact row counts do not match")
    if manifest.get("benchmark_claim") is not False:
        raise ValueError("Stage 3 manifest must not make a benchmark claim")
    identity = manifest.get("identity", {})
    if identity.get("feature_artifacts_created") is not True or identity.get("label_artifacts_created") is not True:
        raise ValueError("Stage 3 manifest does not claim feature and label artifacts")
    if set(labels["target_family"].unique()) != {TARGET_FAMILY}:
        raise ValueError("labels target family mismatch")
    if set(labels["return_type"].unique()) != {LABEL_RETURN_TYPE}:
        raise ValueError("labels return type mismatch")
    if set(labels["reference_policy"].unique()) != {LABEL_REFERENCE_POLICY}:
        raise ValueError("labels reference policy mismatch")
    if not labels["label_available_flag"].all():
        raise ValueError("all Stage 3 labels should be available for the Stage 2 clean window")
    embedding_columns = [column for column in event_state.columns if column.startswith("event_state_hash_embedding_")]
    if len(embedding_columns) != 8:
        raise ValueError("event-state embedding dimension mismatch")

    return {
        "artifact_type": "stage3_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed",
        "benchmark_claim": False,
        "artifact_root": str(artifact_root),
        "artifact_version": identity.get("artifact_version"),
        "input_dataset_version": identity.get("input_dataset_version"),
        "row_count": len(labels),
        "row_universe_digest": expected_digest,
        "aligned_news_rows": len(aligned_news),
        "event_state_embedding_dimension": len(embedding_columns),
        "label_reference_policy": LABEL_REFERENCE_POLICY,
        "label_return_type": LABEL_RETURN_TYPE,
        "artifact_paths": [str(path) for path in required_paths],
        "non_claims": manifest.get("non_claims", []),
    }


def resolve_artifact_root(path: Path) -> Path:
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if (path / "feature_label_manifest.json").exists():
        return path
    candidates = sorted((child for child in path.iterdir() if (child / "feature_label_manifest.json").exists()), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"no Stage 3 feature-label manifests found under {path}")
    return candidates[-1]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    if summary.get("status") != "passed":
        print("STAGE3_COMPLETION_VALIDATION FAILED")
        print(f"error: {summary.get('error')}")
        return
    print("STAGE3_COMPLETION_VALIDATION PASSED")
    print(f"artifact_version: {summary['artifact_version']}")
    print(f"row_count: {summary['row_count']}")
    print(f"row_universe_digest: {summary['row_universe_digest']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
