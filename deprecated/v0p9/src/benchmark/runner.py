"""Gate-safe Stage 4 benchmark runner checks.

This module does not train models, score predictions, compute metrics, or create
benchmark results. It only verifies that Stage 4 split and packet gates cannot be
bypassed before Stage 5 model work.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Mapping

from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID


def validate_gate_safe_runner(
    *,
    split_manifest: Mapping[str, Any],
    leakage_validation: Mapping[str, Any],
    stage4_packet_validation: Mapping[str, Any],
    serious_packet_validation: Mapping[str, Any],
) -> dict[str, Any]:
    blockers: list[str] = []
    identity = split_manifest.get("identity", {})
    if identity.get("benchmark_family_id") != BENCHMARK_FAMILY_ID:
        blockers.append("benchmark_family_id_drift")
    if leakage_validation.get("status") != "passed":
        blockers.append("leakage_validation_not_passed")
    if stage4_packet_validation.get("status") != "passed":
        blockers.append("stage4_pre_model_packet_incomplete")
    if serious_packet_validation.get("status") == "passed":
        blockers.append("serious_packet_unexpectedly_complete_before_models")

    status = "stage4_runner_gate_passed_no_model_execution" if not blockers else "blocked_stage4_runner_gate"
    return {
        "artifact_type": "stage4_benchmark_runner_gate",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": status,
        "benchmark_claim": False,
        "training_executed": False,
        "predictions_created": False,
        "metrics_computed": False,
        "comparison_summary_created": False,
        "serious_claim_allowed": False,
        "blockers": blockers,
        "stage4_packet_status": stage4_packet_validation.get("status"),
        "serious_packet_status": serious_packet_validation.get("status"),
        "next_stage": "Stage 5 model and comparator execution can start only after consuming these split artifacts.",
    }
