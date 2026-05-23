from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.data.contracts import APPROVED_HORIZONS  # noqa: E402
from event_state_forecasting.features.labels import LABEL_REFERENCE_POLICY, build_forward_excess_return_labels  # noqa: E402


def test_labels_use_simple_leave_one_out_universe_excess_returns() -> None:
    panel = pd.DataFrame([_row(ticker, horizon) for ticker in ("AAA", "BBB", "CCC") for horizon in APPROVED_HORIZONS])
    close_by_ticker = {
        "AAA": {date(2024, 4, 1): 100.0, date(2024, 4, 2): 110.0},
        "BBB": {date(2024, 4, 1): 100.0, date(2024, 4, 2): 120.0},
        "CCC": {date(2024, 4, 1): 100.0, date(2024, 4, 2): 130.0},
    }

    labels = build_forward_excess_return_labels(panel, close_by_ticker)

    aaa = labels[(labels["canonical_ticker"] == "AAA") & (labels["horizon_id"] == "1d")].iloc[0]
    assert aaa["reference_policy"] == LABEL_REFERENCE_POLICY
    assert aaa["ticker_forward_simple_return"] == pytest.approx(0.10)
    assert aaa["leave_one_out_universe_reference_return"] == pytest.approx(0.25)
    assert aaa["forward_excess_return"] == pytest.approx(-0.15)


def _row(ticker: str, horizon: str) -> dict[str, object]:
    return {
        "benchmark_family_id": "phase1_top50",
        "dataset_version": "test",
        "canonical_ticker": ticker,
        "as_of_date": "2024-04-01",
        "horizon_id": horizon,
        "label_window_start": "2024-04-02",
        "label_window_end": "2024-04-02",
    }
