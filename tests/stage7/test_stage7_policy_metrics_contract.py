from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.stage7.metrics import compute_stage7_metrics  # noqa: E402
from event_state_forecasting.stage7.policies import select_top_bottom  # noqa: E402
from event_state_forecasting.stage7.replay import build_replay_validation  # noqa: E402


def test_stage7_policy_selects_two_sided_top_and_bottom_without_trading_signal() -> None:
    selected = select_top_bottom(
        _candidate_frame(),
        k=2,
        score_column="score",
        policy_id="combined_supervised",
        policy_family="combined_context_supervised_baseline",
        epsilon=None,
        rng=np.random.default_rng(1729),
    )

    assert set(selected["selection_side"]) == {"top", "bottom"}
    assert len(selected) == 4
    assert bool(selected["trading_signal_approved"].any()) is False
    assert selected[selected["selection_side"] == "top"].iloc[0]["canonical_ticker"] == "T04"
    assert selected[selected["selection_side"] == "bottom"].iloc[0]["canonical_ticker"] == "T00"


def test_stage7_metrics_report_top_bottom_and_spread_as_non_trading_diagnostic() -> None:
    selected = select_top_bottom(
        _candidate_frame(),
        k=2,
        score_column="score",
        policy_id="combined_supervised",
        policy_family="combined_context_supervised_baseline",
        epsilon=None,
        rng=np.random.default_rng(1729),
    )

    metrics = compute_stage7_metrics(selected)

    aggregate = metrics[(metrics["aggregation_level"] == "aggregate") & (metrics["row_filter_track"] == "all_rows_primary")].iloc[0]
    assert aggregate["top_k_mean_forward_excess_return"] > aggregate["bottom_k_mean_forward_excess_return"]
    assert aggregate["top_minus_bottom_forward_excess_return_spread"] > 0
    assert aggregate["trading_signal_approved"] == False  # noqa: E712
    assert aggregate["spread_is_trading_pnl"] == False  # noqa: E712


def test_stage7_validation_allows_explicit_new_post_lockbox_holdout() -> None:
    context = _candidate_frame()
    context["split_role"] = "lockbox"
    context["as_of_date"] = "2026-02-17"
    selections = select_top_bottom(
        context,
        k=2,
        score_column="score",
        policy_id="combined_supervised",
        policy_family="combined_context_supervised_baseline",
        epsilon=None,
        rng=np.random.default_rng(1729),
    )
    metrics = compute_stage7_metrics(selections)

    validation = build_replay_validation(context, selections, metrics, allow_new_post_lockbox_holdout=True)

    assert validation["status"] == "passed"
    assert validation["new_post_lockbox_holdout_mode"] is True
    assert validation["current_stage6_lockbox_row_count"] == 0


def _candidate_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "fold_id": ["fold_001"] * 5,
            "horizon_id": ["1d"] * 5,
            "as_of_date": ["2025-01-01"] * 5,
            "canonical_ticker": [f"T{i:02d}" for i in range(5)],
            "score": [0.1, 0.2, 0.3, 0.4, 0.5],
            "forward_excess_return": [-0.02, -0.01, 0.0, 0.01, 0.02],
            "stage7_news_day_flag": [True, False, False, True, True],
            "split_role": ["validation"] * 5,
        }
    )
