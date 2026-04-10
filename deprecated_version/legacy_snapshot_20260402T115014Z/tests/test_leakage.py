from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from src.features.labels import build_multi_horizon_labels
from src.features.market_features import build_market_features
from src.split.leakage_checks import (
    LeakageCheckError,
    assert_articles_aligned_asof_close,
    assert_no_date_overlap,
    assert_scaler_fit_within_train_window,
)


def _adjusted_rows() -> list[dict]:
    closes = [100.0, 110.0, 105.0, 120.0]
    rows = []
    for index, close in enumerate(closes, start=1):
        rows.append(
            {
                "date": f"2024-01-0{index}",
                "ticker": "AAPL",
                "open": close - 1.0,
                "high": close + 1.0,
                "low": close - 2.0,
                "close": close,
                "volume": 1000 + (index * 10),
                "source": "twelve_data",
                "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
                "adjustment_source": "split_events",
            }
        )
    return rows


def test_market_features_use_only_past_information() -> None:
    features = build_market_features(_adjusted_rows(), return_windows=(1,), volatility_windows=(2,), momentum_windows=(2,), volume_windows=(2,))

    assert pd.isna(features.iloc[0]["return_1"])
    assert features.iloc[1]["return_1"] == pytest.approx(0.10)
    assert features.iloc[2]["return_1"] == pytest.approx((105.0 / 110.0) - 1.0)


def test_labels_use_future_information_and_remain_offset_from_features() -> None:
    features = build_market_features(_adjusted_rows(), return_windows=(1,), volatility_windows=(2,), momentum_windows=(2,), volume_windows=(2,))
    labels = build_multi_horizon_labels(_adjusted_rows(), horizons=(1,))

    assert features.iloc[0]["return_1"] != labels.iloc[0]["y_ret_1"]
    assert labels.iloc[0]["y_ret_1"] == pytest.approx(0.10)
    assert labels.iloc[1]["y_ret_1"] == pytest.approx((105.0 / 110.0) - 1.0)
    assert pd.isna(labels.iloc[-1]["y_ret_1"])


def test_features_reject_unadjusted_rows() -> None:
    raw_like_rows = [{k: v for k, v in row.items() if k != "adjustment_source"} for row in _adjusted_rows()]

    try:
        build_market_features(raw_like_rows, return_windows=(1,), volatility_windows=(2,), momentum_windows=(2,), volume_windows=(2,))
    except Exception:
        assert True
    else:
        raise AssertionError("Expected unadjusted rows to be rejected by market feature builder.")


def test_labels_reject_unadjusted_rows() -> None:
    raw_like_rows = [{k: v for k, v in row.items() if k != "adjustment_source"} for row in _adjusted_rows()]

    try:
        build_multi_horizon_labels(raw_like_rows, horizons=(1,))
    except Exception:
        assert True
    else:
        raise AssertionError("Expected unadjusted rows to be rejected by label builder.")


def test_assert_no_date_overlap_detects_overlap() -> None:
    with pytest.raises(LeakageCheckError, match="Overlapping date detected"):
        assert_no_date_overlap(
            [datetime(2024, 1, 1).date(), datetime(2024, 1, 2).date()],
            [datetime(2024, 1, 2).date(), datetime(2024, 1, 3).date()],
        )


def test_assert_scaler_fit_within_train_window_detects_contamination() -> None:
    with pytest.raises(LeakageCheckError, match="Scaler fit end date extends beyond"):
        assert_scaler_fit_within_train_window(
            scaler_fit_end_date=datetime(2024, 1, 5).date(),
            train_end_date=datetime(2024, 1, 4).date(),
        )


def test_assert_articles_aligned_asof_close_detects_misalignment() -> None:
    bad_articles = [
        {
            "article_id": "1",
            "published_ts_utc": datetime(2024, 1, 2, 22, 0, tzinfo=UTC),
            "asof_trade_date": datetime(2024, 1, 2).date(),
        }
    ]

    with pytest.raises(LeakageCheckError, match="Article alignment mismatch"):
        assert_articles_aligned_asof_close(
            bad_articles,
            market_timezone="America/New_York",
            exchange_calendar="XNYS",
            close_hour=16,
            close_minute=0,
        )
