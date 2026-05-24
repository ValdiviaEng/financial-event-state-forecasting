"""Stage 7 final-execution pipeline stubs and safeguards."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping


def build_final_execution_stub(output_root: Path, config: Mapping[str, Any]) -> dict[str, Any]:
    """Return a non-training final-execution manifest.

    The user requested no all-data final-execution training/output for this
    Stage 7C run. This stub records the approved future path without producing
    live-use candidates.
    """

    return {
        "artifact_type": "stage7_final_execution_stub",
        "artifact_schema_version": "stage7_contextual_bandit_v1",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "stub_created_no_all_data_training_output",
        "artifact_root": str(output_root),
        "final_execution_training_ran": False,
        "live_use_candidate_output_created": False,
        "benchmark_evidence": False,
        "transferred_frozen_choices": {
            "primary_k": config["basket_policy"]["primary_k"],
            "diagnostic_k": config["basket_policy"]["diagnostic_k"],
            "primary_epsilon": config["epsilon_policy"]["primary_epsilon"],
            "diagnostic_epsilon": config["epsilon_policy"]["diagnostic_epsilon"],
            "context_mode": config["context"]["mode"],
        },
        "non_claims": [
            "not_all_data_training_output",
            "not_benchmark_evidence",
            "not_live_buy_sell_signal",
            "not_trading_profitability",
        ],
    }
