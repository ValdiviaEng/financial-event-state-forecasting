from __future__ import annotations

import os

import pytest

from src.data.sec_edgar_client import SecEdgarClient
from src.utils.config_loader import load_project_settings


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_API_TESTS", "").lower() != "true",
    reason="Set RUN_LIVE_API_TESTS=true to execute live provider tests manually.",
)


def test_live_sec_submissions_metadata_small_request() -> None:
    settings = load_project_settings()
    client = SecEdgarClient.from_settings(settings)
    payload, metadata = client.get_submissions("320193")
    company = client.extract_company_metadata(payload)
    mappings = client.extract_ticker_cik_mappings(payload)

    assert metadata.response_status == 200
    assert company["cik"] == "0000320193"
    assert company["ticker"] == "AAPL"
    assert mappings
    assert mappings[0]["ticker"] == "AAPL"
