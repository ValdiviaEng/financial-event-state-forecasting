#!/usr/bin/env python3
"""Validate materialized Stage 4 split and packet-gate artifacts."""

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

from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID, ROW_KEY_FIELDS  # noqa: E402
from event_state_forecasting.split.leakage_checks import validate_no_leakage  # noqa: E402


DEFAULT_ARTIFACT_FAMILY_ROOT = PROJECT_ROOT / "data" / "splits" / BENCHMARK_FAMILY_ID
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage4_completion_validation_2026-05-15.json"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate a materialized Stage 4 split artifact set.")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_FAMILY_ROOT), help="Stage 4 artifact root or family root.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for completion-validation JSON.")
    parser.add_argument("--write", action="store_true", help="Write completion-validation JSON.")
    parser.add_argument("--json", action="store_true", help="Print full validation JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        summary = validate_stage4_completion(resolve_artifact_root(Path(args.artifact_root)))
    except (ValueError, FileNotFoundError) as exc:
        summary = {
            "artifact_type": "stage4_completion_validation",
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


def validate_stage4_completion(artifact_root: Path) -> dict[str, Any]:
    paths = {
        "split_manifest": artifact_root / "split_manifest.json",
        "fold_definitions": artifact_root / "fold_definitions.parquet",
        "split_assignments": artifact_root / "split_assignments.parquet",
        "lockbox_record": artifact_root / "lockbox_record.json",
        "leakage_validation": artifact_root / "leakage_validation.json",
        "artifact_packet_validation": artifact_root / "artifact_packet_validation.json",
        "benchmark_runner_gate": artifact_root / "benchmark_runner_gate.json",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing Stage 4 artifact(s): {missing}")

    manifest = read_json(paths["split_manifest"])
    lockbox = read_json(paths["lockbox_record"])
    leakage = read_json(paths["leakage_validation"])
    packet = read_json(paths["artifact_packet_validation"])
    runner = read_json(paths["benchmark_runner_gate"])
    folds = pd.read_parquet(paths["fold_definitions"])
    assignments = pd.read_parquet(paths["split_assignments"])

    identity = manifest.get("identity", {})
    if identity.get("benchmark_family_id") != BENCHMARK_FAMILY_ID:
        raise ValueError("Stage 4 split manifest benchmark family mismatch")
    if manifest.get("benchmark_claim") is not False:
        raise ValueError("Stage 4 split manifest must not make a benchmark claim")
    if lockbox.get("benchmark_claim") is not False:
        raise ValueError("lockbox record must not make a benchmark claim")
    if leakage.get("status") != "passed":
        raise ValueError("stored Stage 4 leakage validation did not pass")
    recomputed_leakage = validate_no_leakage(assignments, folds, lockbox)
    if recomputed_leakage.get("status") != "passed":
        raise ValueError(f"recomputed leakage validation failed: {recomputed_leakage.get('violations')}")

    stage4_packet = packet.get("stage4_pre_model_packet", {})
    serious_packet = packet.get("serious_run_packet", {})
    if stage4_packet.get("status") != "passed":
        raise ValueError("Stage 4 pre-model artifact packet did not pass")
    if serious_packet.get("status") != "blocked_missing_required_members":
        raise ValueError("serious-run packet should remain blocked until model artifacts exist")
    if runner.get("status") != "stage4_runner_gate_passed_no_model_execution":
        raise ValueError("Stage 4 runner gate did not pass safely")
    if runner.get("training_executed") or runner.get("predictions_created") or runner.get("metrics_computed"):
        raise ValueError("Stage 4 runner gate must not train, predict, or compute metrics")

    duplicate_assignments = int(assignments.duplicated(["fold_id", *ROW_KEY_FIELDS]).sum())
    if duplicate_assignments:
        raise ValueError(f"duplicate split assignments detected: {duplicate_assignments}")
    expected_assignment_rows = int(manifest["row_universe"]["input_row_count"] * manifest["row_universe"]["fold_count"])
    if len(assignments) != expected_assignment_rows:
        raise ValueError("split assignment row count does not equal input rows times folds")

    return {
        "artifact_type": "stage4_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed",
        "benchmark_claim": False,
        "artifact_root": str(artifact_root),
        "artifact_version": identity.get("artifact_version"),
        "input_stage3_artifact_version": identity.get("input_stage3_artifact_version"),
        "row_universe_digest": identity.get("row_universe_digest"),
        "fold_count": int(len(folds)),
        "assignment_row_count": int(len(assignments)),
        "lockbox_start_date": lockbox["start_date"],
        "lockbox_end_date": lockbox["end_date"],
        "lockbox_date_count": int(lockbox["date_count"]),
        "stage4_packet_status": stage4_packet.get("status"),
        "serious_packet_status": serious_packet.get("status"),
        "runner_gate_status": runner.get("status"),
        "artifact_paths": {name: str(path) for name, path in paths.items()},
        "non_claims": manifest.get("non_claims", []),
    }


def resolve_artifact_root(path: Path) -> Path:
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if (path / "split_manifest.json").exists():
        return path
    candidates = sorted((child for child in path.iterdir() if (child / "split_manifest.json").exists()), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"no Stage 4 split manifests found under {path}")
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
        print("STAGE4_COMPLETION_VALIDATION FAILED")
        print(f"error: {summary.get('error')}")
        return
    print("STAGE4_COMPLETION_VALIDATION PASSED")
    print(f"artifact_version: {summary['artifact_version']}")
    print(f"fold_count: {summary['fold_count']}")
    print(f"lockbox_start_date: {summary['lockbox_start_date']}")
    print(f"assignment_row_count: {summary['assignment_row_count']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
