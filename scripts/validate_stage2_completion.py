#!/usr/bin/env python3
"""Validate materialized Stage 2 benchmark dataset artifacts."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = PROJECT_ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from _v0p9_package_alias import install_v0p9_event_state_package  # noqa: E402

install_v0p9_event_state_package(PROJECT_ROOT)

from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID, ContractError, validate_manifest, validate_panel_records  # noqa: E402
from event_state_forecasting.dataset.row_universe import row_universe_digest  # noqa: E402


DEFAULT_DATASET_FAMILY_ROOT = PROJECT_ROOT / "data" / "datasets" / BENCHMARK_FAMILY_ID
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage2_completion_validation_2026-05-14.json"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a materialized Stage 2 dataset artifact set.")
    parser.add_argument("--dataset-root", default=str(DEFAULT_DATASET_FAMILY_ROOT), help="Dataset version root or family root.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for completion-validation JSON.")
    parser.add_argument("--write", action="store_true", help="Write completion-validation JSON.")
    parser.add_argument("--json", action="store_true", help="Print full validation JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        summary = validate_stage2_completion(resolve_dataset_root(Path(args.dataset_root)))
    except (ContractError, ValueError, FileNotFoundError) as exc:
        summary = {
            "artifact_type": "stage2_completion_validation",
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


def validate_stage2_completion(dataset_root: Path) -> dict[str, Any]:
    manifest_path = dataset_root / "dataset_manifest.json"
    row_digest_path = dataset_root / "row_universe_digest.json"
    clean_window_path = dataset_root / "clean_window_decision.json"
    cvx_patch_path = dataset_root / "cvx_derived_ohlc_patch_manifest.json"
    panel_path = dataset_root / "benchmark_panel.parquet"
    required_paths = [manifest_path, row_digest_path, clean_window_path, cvx_patch_path, panel_path]
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing Stage 2 artifact(s): {missing}")

    manifest = read_json(manifest_path)
    row_digest_record = read_json(row_digest_path)
    clean_window = read_json(clean_window_path)
    cvx_patch = read_json(cvx_patch_path)
    validate_manifest(manifest)
    if manifest.get("identity", {}).get("stage2_completion_status") != "materialized_stage2_dataset_complete":
        raise ValueError("manifest does not claim Stage 2 materialized completion status")
    if manifest.get("identity", {}).get("benchmark_claim") is not False:
        raise ValueError("Stage 2 manifest must not make a benchmark claim")

    frame = pd.read_parquet(panel_path)
    records = frame.to_dict("records")
    panel_summary = validate_panel_records(records)
    if any(row.get("canonical_ticker") == "SPY" for row in records):
        raise ValueError("SPY support ticker must not be present as a dataset row")
    digest = row_universe_digest(records)
    expected_digest = row_digest_record.get("row_universe_digest")
    if digest != expected_digest:
        raise ValueError("row-universe digest mismatch")
    manifest_digest = manifest.get("hashes", {}).get("row_universe_digest")
    if digest != manifest_digest:
        raise ValueError("manifest row-universe digest mismatch")
    if panel_summary.row_count != manifest.get("coverage", {}).get("row_count"):
        raise ValueError("manifest row count does not match panel")
    if clean_window.get("status") != "selected_for_stage2_materialized_dataset":
        raise ValueError("clean-window record is not selected for Stage 2 materialized dataset")
    if cvx_patch.get("raw_files_mutated") is not False:
        raise ValueError("CVX patch manifest must prove raw files were not mutated")

    return {
        "artifact_type": "stage2_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed",
        "benchmark_claim": False,
        "dataset_root": str(dataset_root),
        "dataset_version": manifest.get("identity", {}).get("dataset_version"),
        "row_count": panel_summary.row_count,
        "horizon_counts": panel_summary.horizon_counts,
        "row_universe_digest": digest,
        "artifact_paths": [str(path) for path in required_paths],
        "non_claims": manifest.get("non_claims", []),
    }


def resolve_dataset_root(path: Path) -> Path:
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if (path / "dataset_manifest.json").exists():
        return path
    candidates = sorted((child for child in path.iterdir() if (child / "dataset_manifest.json").exists()), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"no Stage 2 dataset manifests found under {path}")
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
        print("STAGE2_COMPLETION_VALIDATION FAILED")
        print(f"error: {summary.get('error')}")
        return
    print("STAGE2_COMPLETION_VALIDATION PASSED")
    print(f"dataset_version: {summary['dataset_version']}")
    print(f"row_count: {summary['row_count']}")
    print(f"row_universe_digest: {summary['row_universe_digest']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
