from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.benchmark.artifact_packet import validate_artifact_packet  # noqa: E402


def test_stage4_artifact_packet_passes_when_required_members_exist(tmp_path: Path) -> None:
    config = _packet_config()
    members = _members(tmp_path, config["stage4_pre_model_required_members"])

    result = validate_artifact_packet(members, config, mode="stage4_pre_model")

    assert result["status"] == "passed"
    assert result["benchmark_claim"] is False
    assert result["serious_claim_allowed"] is False


def test_artifact_packet_fails_closed_when_member_is_missing(tmp_path: Path) -> None:
    config = _packet_config()
    members = _members(tmp_path, config["stage4_pre_model_required_members"])
    members.pop("split_manifest")

    result = validate_artifact_packet(members, config, mode="stage4_pre_model")

    assert result["status"] == "blocked_missing_required_members"
    assert "split_manifest" in result["missing_members"]


def test_serious_packet_blocks_until_model_artifacts_exist(tmp_path: Path) -> None:
    config = _packet_config()
    members = _members(tmp_path, config["stage4_pre_model_required_members"])

    result = validate_artifact_packet(members, config, mode="serious_run")

    assert result["status"] == "blocked_missing_required_members"
    assert "saved_predictions" in result["missing_members"]
    assert result["serious_claim_allowed"] is False


def _packet_config() -> dict[str, object]:
    return {
        "artifact_schema_version": "stage4_artifact_packet_v1",
        "stage4_pre_model_required_members": [
            "dataset_manifest",
            "feature_label_manifest",
            "resolved_split_config",
            "artifact_packet_config",
            "split_manifest",
        ],
        "serious_run_required_members": [
            "dataset_manifest",
            "feature_label_manifest",
            "resolved_split_config",
            "artifact_packet_config",
            "split_manifest",
            "saved_predictions",
            "metrics",
        ],
        "claim_policy": {"benchmark_claim_requires_full_serious_packet": True},
    }


def _members(tmp_path: Path, names: list[str]) -> dict[str, str]:
    members = {}
    for name in names:
        path = tmp_path / f"{name}.json"
        path.write_text("{}\n", encoding="utf-8")
        members[name] = str(path)
    return members
