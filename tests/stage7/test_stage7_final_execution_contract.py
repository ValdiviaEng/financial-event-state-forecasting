from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.stage7.final_execution import build_final_execution_stub  # noqa: E402


def test_final_execution_stub_does_not_train_or_create_live_outputs() -> None:
    stub = build_final_execution_stub(Path("data/stage7_final_execution/phase1_top50/test"), _config())

    assert stub["final_execution_training_ran"] is False
    assert stub["live_use_candidate_output_created"] is False
    assert stub["benchmark_evidence"] is False
    assert "not_live_buy_sell_signal" in stub["non_claims"]


def _config() -> dict:
    return {
        "basket_policy": {"primary_k": 5, "diagnostic_k": [3, 10]},
        "epsilon_policy": {"primary_epsilon": 0.05, "diagnostic_epsilon": [0.01, 0.1]},
        "context": {"mode": "combined_stage3_features_plus_stage5_predictions"},
    }
