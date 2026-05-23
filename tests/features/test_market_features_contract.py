from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.features.market import build_market_features  # noqa: E402


def test_market_features_use_same_row_as_of_values() -> None:
    panel = pd.DataFrame(
        [
            {
                "benchmark_family_id": "phase1_top50",
                "dataset_version": "test",
                "canonical_ticker": "AAPL",
                "as_of_date": "2024-04-01",
                "horizon_id": "1d",
                "prediction_timestamp": "2024-04-01T16:00:00-04:00",
                "feature_availability_timestamp": "2024-04-01T16:00:00-04:00",
                "market_open": 100.0,
                "market_high": 110.0,
                "market_low": 95.0,
                "market_close": 105.0,
                "market_volume": 1000,
            }
        ]
    )

    features = build_market_features(panel)

    assert features.loc[0, "market_intraday_return"] == pytest.approx(0.05)
    assert features.loc[0, "market_intraday_range_ratio"] == pytest.approx((110.0 - 95.0) / 105.0)
    assert features.loc[0, "feature_availability_timestamp"] == "2024-04-01T16:00:00-04:00"
