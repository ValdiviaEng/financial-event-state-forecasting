"""CLI orchestration for Stage 4 split and packet-gate artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys
from typing import Any

import pandas as pd

from event_state_forecasting.benchmark.artifact_packet import build_stage4_member_map, validate_artifact_packet
from event_state_forecasting.benchmark.runner import validate_gate_safe_runner
from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID
from event_state_forecasting.split.leakage_checks import validate_no_leakage
from event_state_forecasting.split.purged_embargo import SplitBuildError, build_purged_embargoed_folds


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_STAGE3_ROOT = PROJECT_ROOT / "data" / "features" / BENCHMARK_FAMILY_ID
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "splits" / BENCHMARK_FAMILY_ID
DEFAULT_SPLITS_CONFIG = PROJECT_ROOT / "configs" / "splits.yaml"
DEFAULT_PACKET_CONFIG = PROJECT_ROOT / "configs" / "artifact_packet.yaml"


class Stage4BuildError(ValueError):
    """Raised when Stage 4 artifacts cannot be built safely."""


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Stage 4 split, lockbox, leakage, and packet-gate artifacts.")
    parser.add_argument("--stage3-root", default=str(DEFAULT_STAGE3_ROOT), help="Stage 3 artifact root or family root.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Stage 4 split artifact family output root.")
    parser.add_argument("--splits-config", default=str(DEFAULT_SPLITS_CONFIG), help="Active Stage 4 split config.")
    parser.add_argument("--artifact-packet-config", default=str(DEFAULT_PACKET_CONFIG), help="Active artifact-packet config.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Replace an existing Stage 4 artifact root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable build summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        outputs = run_stage4_build(
            stage3_root=Path(args.stage3_root),
            output_root=Path(args.output_root),
            splits_config_path=Path(args.splits_config),
            artifact_packet_config_path=Path(args.artifact_packet_config),
            allow_overwrite=args.allow_overwrite,
        )
    except (Stage4BuildError, SplitBuildError, FileNotFoundError, ValueError) as exc:
        print(f"STAGE4_SPLIT_PACKET_BUILD_FAILED: {exc}", file=sys.stderr)
        return 2

    summary = {
        "status": "stage4_splits_packet_built",
        "benchmark_claim": False,
        "artifact_version": outputs["artifact_version"],
        "artifact_root": outputs["artifact_root"],
        "fold_count": outputs["fold_count"],
        "lockbox_start_date": outputs["lockbox_start_date"],
        "assignment_row_count": outputs["assignment_row_count"],
        "split_manifest": outputs["split_manifest"],
        "leakage_validation": outputs["leakage_validation"],
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("STAGE4 SPLIT PACKET BUILD")
        print("status: stage4_splits_packet_built")
        print("benchmark_claim: false")
        print(f"artifact_version: {outputs['artifact_version']}")
        print(f"fold_count: {outputs['fold_count']}")
        print(f"lockbox_start_date: {outputs['lockbox_start_date']}")
        print(f"assignment_row_count: {outputs['assignment_row_count']}")
        print(f"artifact_root: {outputs['artifact_root']}")
    return 0


def run_stage4_build(
    *,
    stage3_root: Path,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    splits_config_path: Path = DEFAULT_SPLITS_CONFIG,
    artifact_packet_config_path: Path = DEFAULT_PACKET_CONFIG,
    allow_overwrite: bool = False,
) -> dict[str, Any]:
    stage3_root = resolve_stage3_root(stage3_root)
    if not output_root.is_absolute():
        output_root = PROJECT_ROOT / output_root
    splits_config_path = resolve_project_path(splits_config_path)
    artifact_packet_config_path = resolve_project_path(artifact_packet_config_path)

    feature_manifest_path = stage3_root / "feature_label_manifest.json"
    labels_path = stage3_root / "labels.parquet"
    feature_manifest = read_json(feature_manifest_path)
    splits_config = read_json(splits_config_path)
    packet_config = read_json(artifact_packet_config_path)
    labels = pd.read_parquet(labels_path)

    input_artifact_version = feature_manifest["identity"]["artifact_version"]
    row_digest = feature_manifest["row_universe"]["row_universe_digest"]
    artifact_version = f"{input_artifact_version}__stage4_splits_v1"
    artifact_root = output_root / artifact_version
    if artifact_root.exists():
        if not allow_overwrite:
            raise Stage4BuildError(f"Stage 4 output already exists: {artifact_root}")
        shutil.rmtree(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=False)

    split_artifacts = build_purged_embargoed_folds(
        labels,
        split_config=splits_config,
        artifact_version=artifact_version,
        input_artifact_version=input_artifact_version,
        row_universe_digest=row_digest,
    )

    fold_definitions_path = artifact_root / "fold_definitions.parquet"
    split_assignments_path = artifact_root / "split_assignments.parquet"
    split_manifest_path = artifact_root / "split_manifest.json"
    lockbox_record_path = artifact_root / "lockbox_record.json"
    leakage_validation_path = artifact_root / "leakage_validation.json"
    artifact_packet_validation_path = artifact_root / "artifact_packet_validation.json"
    runner_gate_path = artifact_root / "benchmark_runner_gate.json"

    split_artifacts.fold_definitions.to_parquet(fold_definitions_path, index=False, engine="pyarrow")
    split_artifacts.assignments.to_parquet(split_assignments_path, index=False, engine="pyarrow")
    split_artifacts.manifest["artifacts"] = {
        "artifact_root": str(artifact_root),
        "fold_definitions": str(fold_definitions_path),
        "split_assignments": str(split_assignments_path),
        "split_manifest": str(split_manifest_path),
        "lockbox_record": str(lockbox_record_path),
        "leakage_validation": str(leakage_validation_path),
        "artifact_packet_validation": str(artifact_packet_validation_path),
        "benchmark_runner_gate": str(runner_gate_path),
    }
    write_json(lockbox_record_path, split_artifacts.lockbox_record)
    write_json(split_manifest_path, split_artifacts.manifest)

    leakage_validation = validate_no_leakage(split_artifacts.assignments, split_artifacts.fold_definitions, split_artifacts.lockbox_record)
    if leakage_validation["status"] != "passed":
        write_json(leakage_validation_path, leakage_validation)
        raise Stage4BuildError(f"Stage 4 leakage validation failed: {leakage_validation['violations']}")
    write_json(leakage_validation_path, leakage_validation)

    dataset_manifest = Path(feature_manifest["inputs"]["dataset_manifest"])
    members = build_stage4_member_map(
        dataset_manifest=dataset_manifest,
        feature_label_manifest=feature_manifest_path,
        split_config=splits_config_path,
        artifact_packet_config=artifact_packet_config_path,
        split_manifest=split_manifest_path,
        fold_definitions=fold_definitions_path,
        split_assignments=split_assignments_path,
        lockbox_record=lockbox_record_path,
        leakage_validation=leakage_validation_path,
    )
    stage4_packet_validation = validate_artifact_packet(members, packet_config, mode="stage4_pre_model")
    serious_packet_validation = validate_artifact_packet(members, packet_config, mode="serious_run")
    packet_record = {
        "artifact_type": "stage4_artifact_packet_validation_bundle",
        "benchmark_claim": False,
        "stage4_pre_model_packet": stage4_packet_validation,
        "serious_run_packet": serious_packet_validation,
    }
    write_json(artifact_packet_validation_path, packet_record)

    runner_gate = validate_gate_safe_runner(
        split_manifest=split_artifacts.manifest,
        leakage_validation=leakage_validation,
        stage4_packet_validation=stage4_packet_validation,
        serious_packet_validation=serious_packet_validation,
    )
    write_json(runner_gate_path, runner_gate)

    return {
        "artifact_version": artifact_version,
        "artifact_root": str(artifact_root),
        "fold_count": int(len(split_artifacts.fold_definitions)),
        "lockbox_start_date": split_artifacts.lockbox_record["start_date"],
        "assignment_row_count": int(len(split_artifacts.assignments)),
        "split_manifest": str(split_manifest_path),
        "leakage_validation": str(leakage_validation_path),
    }


def resolve_stage3_root(path: Path) -> Path:
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if (path / "feature_label_manifest.json").exists():
        return path
    candidates = sorted((child for child in path.iterdir() if (child / "feature_label_manifest.json").exists()), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FileNotFoundError(f"no Stage 3 feature-label manifests found under {path}")
    return candidates[-1]


def resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise Stage4BuildError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
