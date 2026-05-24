from __future__ import annotations

import os

import pytest

from src.data.finnhub_client import FinnhubClient
from src.utils.config_loader import load_project_settings


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_API_TESTS", "").lower() != "true",
    reason="Set RUN_LIVE_API_TESTS=true to execute live provider tests manually.",
)


def test_live_finnhub_company_news_small_request() -> None:
    settings = load_project_settings()
    client = FinnhubClient.from_settings(settings)
    payload, metadata = client.get_company_news("AAPL", "2024-01-02", "2024-01-05")

    assert metadata.response_status == 200
    assert isinstance(payload, list)

    if not payload:
        pytest.skip("Finnhub returned no articles for the selected small historical window.")

    articles = client.normalize_company_news(payload, symbol="AAPL")
    assert articles
    assert articles[0]["ticker"] == "AAPL"
    assert {"article_id", "published_ts_utc", "headline", "source", "provider"}.issubset(articles[0].keys())
