from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.features.event_state import build_event_state_features  # noqa: E402
from event_state_forecasting.features.news_alignment import AlignedNewsRecord  # noqa: E402


def test_event_state_preserves_rows_and_marks_no_news() -> None:
    panel = pd.DataFrame([_row("AAPL", "2024-04-01"), _row("MSFT", "2024-04-01")])
    aligned = [
        AlignedNewsRecord(
            article_id="a1",
            ticker="AAPL",
            published_timestamp="2024-04-01T12:00:00-04:00",
            aligned_as_of_date="2024-04-01",
            roll_forward_reason="same_trading_day_at_or_before_close",
            title="Apple news",
            summary="summary",
            url="https://example.test/a1",
            text_hash="hash",
        )
    ]

    features = build_event_state_features(panel, aligned, embedding_dimension=8)

    assert len(features) == len(panel)
    aapl = features[features["canonical_ticker"] == "AAPL"].iloc[0]
    msft = features[features["canonical_ticker"] == "MSFT"].iloc[0]
    assert aapl["stage3_aligned_news_count"] == 1
    assert bool(aapl["no_news_flag"]) is False
    assert msft["stage3_aligned_news_count"] == 0
    assert bool(msft["no_news_flag"]) is True
    assert msft["event_state_hash_embedding_00"] == 0.0


def _row(ticker: str, as_of_date: str) -> dict[str, object]:
    return {
        "benchmark_family_id": "phase1_top50",
        "dataset_version": "test",
        "canonical_ticker": ticker,
        "as_of_date": as_of_date,
        "horizon_id": "1d",
        "prediction_timestamp": f"{as_of_date}T16:00:00-04:00",
        "feature_availability_timestamp": f"{as_of_date}T16:00:00-04:00",
        "provider_empty_feed_flag": False,
        "provider_truncation_risk_flag": False,
    }
