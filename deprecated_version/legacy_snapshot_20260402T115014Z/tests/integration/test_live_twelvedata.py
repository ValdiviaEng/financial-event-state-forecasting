from __future__ import annotations

import os

import pytest

from src.data.twelve_data_client import TwelveDataClient
from src.utils.config_loader import load_project_settings


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_API_TESTS", "").lower() != "true",
    reason="Set RUN_LIVE_API_TESTS=true to execute live provider tests manually.",
)


def test_live_twelvedata_time_series_small_request() -> None:
    settings = load_project_settings()
    client = TwelveDataClient.from_settings(settings)
    payload, metadata = client.get_time_series("AAPL", outputsize=5)
    rows = client.parse_time_series(payload, symbol="AAPL")

    assert metadata.response_status == 200
    assert rows
    assert rows[0]["ticker"] == "AAPL"
    assert {"date", "open", "high", "low", "close", "source"}.issubset(rows[0].keys())


def test_live_twelvedata_dot_ticker_small_request() -> None:
    settings = load_project_settings()
    client = TwelveDataClient.from_settings(settings)
    payload, metadata = client.get_time_series("BRK.B", outputsize=5)
    rows = client.parse_time_series(payload, symbol="BRK.B")

    assert metadata.response_status == 200
    assert rows
    assert all(row["ticker"] == "BRK.B" for row in rows)
