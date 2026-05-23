from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.benchmark.runner import validate_gate_safe_runner  # noqa: E402


def test_gate_safe_runner_does_not_train_or_claim_benchmark_results() -> None:
    result = validate_gate_safe_runner(
        split_manifest={"identity": {"benchmark_family_id": "phase1_top50"}},
        leakage_validation={"status": "passed"},
        stage4_packet_validation={"status": "passed"},
        serious_packet_validation={"status": "blocked_missing_required_members"},
    )

    assert result["status"] == "stage4_runner_gate_passed_no_model_execution"
    assert result["training_executed"] is False
    assert result["predictions_created"] is False
    assert result["metrics_computed"] is False
    assert result["benchmark_claim"] is False
    assert result["serious_claim_allowed"] is False


def test_gate_safe_runner_blocks_benchmark_family_drift() -> None:
    result = validate_gate_safe_runner(
        split_manifest={"identity": {"benchmark_family_id": "different_family"}},
        leakage_validation={"status": "passed"},
        stage4_packet_validation={"status": "passed"},
        serious_packet_validation={"status": "blocked_missing_required_members"},
    )

    assert result["status"] == "blocked_stage4_runner_gate"
    assert "benchmark_family_id_drift" in result["blockers"]
