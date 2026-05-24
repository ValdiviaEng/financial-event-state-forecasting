from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import pytest

from src.features.labels import build_multi_horizon_labels, summarize_label_availability


def _adjusted_rows() -> list[dict]:
    return [
        {
            "date": "2024-01-02",
            "ticker": "AAPL",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 1000,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
            "adjustment_source": "split_events",
        },
        {
            "date": "2024-01-03",
            "ticker": "AAPL",
            "open": 100.0,
            "high": 111.0,
            "low": 99.5,
            "close": 110.0,
            "volume": 1100,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
            "adjustment_source": "split_events",
        },
        {
            "date": "2024-01-04",
            "ticker": "AAPL",
            "open": 110.0,
            "high": 121.0,
            "low": 109.0,
            "close": 120.0,
            "volume": 1200,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
            "adjustment_source": "split_events",
        },
        {
            "date": "2024-01-05",
            "ticker": "AAPL",
            "open": 120.0,
            "high": 121.0,
            "low": 118.0,
            "close": 90.0,
            "volume": 1300,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
            "adjustment_source": "split_events",
        },
    ]


def _benchmark_rows() -> list[dict]:
    return [
        {"date": "2024-01-02", "close": 200.0},
        {"date": "2024-01-03", "close": 202.0},
        {"date": "2024-01-04", "close": 204.0},
        {"date": "2024-01-05", "close": 206.0},
    ]


def test_forward_return_labels_match_expected_horizons() -> None:
    labels = build_multi_horizon_labels(_adjusted_rows(), horizons=(1, 2))

    row0 = labels.iloc[0]
    row1 = labels.iloc[1]
    assert row0["y_ret_1"] == pytest.approx(0.10)
    assert row0["y_ret_2"] == pytest.approx(0.20)
    assert row1["y_ret_1"] == pytest.approx((120.0 / 110.0) - 1.0)


def test_excess_returns_align_to_benchmark() -> None:
    labels = build_multi_horizon_labels(_adjusted_rows(), benchmark_rows=_benchmark_rows(), horizons=(1,))

    expected_stock = (110.0 / 100.0) - 1.0
    expected_benchmark = (202.0 / 200.0) - 1.0
    assert labels.iloc[0]["y_excess_ret_1"] == pytest.approx(expected_stock - expected_benchmark)


def test_missing_horizons_are_left_missing_at_series_end() -> None:
    labels = build_multi_horizon_labels(_adjusted_rows(), horizons=(1, 3))

    assert pd.isna(labels.iloc[-1]["y_ret_1"])
    assert pd.isna(labels.iloc[-2]["y_ret_3"])


def test_direction_and_downside_labels_follow_forward_returns() -> None:
    labels = build_multi_horizon_labels(_adjusted_rows(), horizons=(1,), downside_threshold=0.0)

    assert labels.iloc[0]["y_dir_1"] is True
    assert labels.iloc[2]["y_downside_1"] is True


def test_raw_rows_are_rejected_when_adjusted_contract_is_required() -> None:
    raw_like_rows = [{k: v for k, v in row.items() if k != "adjustment_source"} for row in _adjusted_rows()]

    with pytest.raises(Exception):
        build_multi_horizon_labels(raw_like_rows, horizons=(1,))


def test_label_summary_reports_availability_counts() -> None:
    labels = build_multi_horizon_labels(_adjusted_rows(), horizons=(1, 2))
    summary = summarize_label_availability(labels, horizons=(1, 2))

    assert summary["row_count"] == 4
    assert summary["available_counts"]["y_ret_1"] == 3
