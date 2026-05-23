"""Stage 4 artifact-packet validation gates."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping


ARTIFACT_PACKET_SCHEMA_VERSION = "stage4_artifact_packet_v1"


class ArtifactPacketError(ValueError):
    """Raised when artifact-packet config is invalid."""


def validate_artifact_packet(
    members: Mapping[str, str | Path | None],
    packet_config: Mapping[str, Any],
    *,
    mode: str,
) -> dict[str, Any]:
    validate_packet_config(packet_config)
    required_key = "stage4_pre_model_required_members" if mode == "stage4_pre_model" else "serious_run_required_members"
    if required_key not in packet_config:
        raise ArtifactPacketError(f"packet config missing required member list: {required_key}")
    required_members = [str(value) for value in packet_config[required_key]]
    missing_members: list[str] = []
    missing_paths: list[str] = []
    present_members: dict[str, str] = {}
    for member in required_members:
        value = members.get(member)
        if value is None or str(value) == "":
            missing_members.append(member)
            continue
        path = Path(value)
        if not path.exists():
            missing_paths.append(member)
            continue
        present_members[member] = str(path)

    status = "passed" if not missing_members and not missing_paths else "blocked_missing_required_members"
    return {
        "artifact_type": "artifact_packet_validation",
        "artifact_schema_version": ARTIFACT_PACKET_SCHEMA_VERSION,
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "mode": mode,
        "status": status,
        "benchmark_claim": False,
        "required_members": required_members,
        "present_members": present_members,
        "missing_members": missing_members,
        "missing_paths": missing_paths,
        "serious_claim_allowed": status == "passed" and mode == "serious_run",
    }


def validate_packet_config(packet_config: Mapping[str, Any]) -> None:
    if packet_config.get("artifact_schema_version") != ARTIFACT_PACKET_SCHEMA_VERSION:
        raise ArtifactPacketError("artifact packet config schema version mismatch")
    if packet_config.get("claim_policy", {}).get("benchmark_claim_requires_full_serious_packet") is not True:
        raise ArtifactPacketError("artifact packet config must require the full serious-run packet for claims")


def build_stage4_member_map(
    *,
    dataset_manifest: Path,
    feature_label_manifest: Path,
    split_config: Path,
    artifact_packet_config: Path,
    split_manifest: Path,
    fold_definitions: Path,
    split_assignments: Path,
    lockbox_record: Path,
    leakage_validation: Path,
) -> dict[str, str]:
    return {
        "dataset_manifest": str(dataset_manifest),
        "feature_label_manifest": str(feature_label_manifest),
        "resolved_split_config": str(split_config),
        "artifact_packet_config": str(artifact_packet_config),
        "split_manifest": str(split_manifest),
        "fold_definitions": str(fold_definitions),
        "split_assignments": str(split_assignments),
        "lockbox_record": str(lockbox_record),
        "leakage_validation": str(leakage_validation),
    }
