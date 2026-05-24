from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import requests

from src.data.finnhub_client import FinnhubClient
from src.data.sec_edgar_client import SecEdgarClient
from src.data.split_events_client import SplitEventsClient
from src.data.twelve_data_client import TwelveDataClient
from src.data.universe_builder import (
    UniverseBuilderError,
    build_pilot_subset,
    load_universe_snapshot,
    normalize_ticker,
)


class _FakeResponse:
    def __init__(self, payload, *, status_code: int = 200, url: str = "https://example.test/api", headers=None):
        self._payload = payload
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}

    def json(self):
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP error {self.status_code}")


class _FakeSession:
    def __init__(self, response: _FakeResponse):
        self.response = response

    def get(self, *args, **kwargs):
        return self.response


def test_dot_ticker_normalization_is_preserved_across_components() -> None:
    assert normalize_ticker(" brk.b ") == "BRK.B"
    assert TwelveDataClient.normalize_symbol(" brk.b ") == "BRK.B"
    assert FinnhubClient.normalize_symbol(" bf.b ") == "BF.B"
    assert SplitEventsClient.normalize_symbol(" brk.b ") == "BRK.B"


def test_load_universe_snapshot_and_build_pilot_subset(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "universe.csv"
    snapshot_path.write_text(
        "ticker,name\nAAPL,Apple\nBRK.B,Berkshire Hathaway\nMSFT,Microsoft\n",
        encoding="utf-8",
    )

    snapshot = load_universe_snapshot(snapshot_path, source_name="test_snapshot")
    pilot = build_pilot_subset(snapshot, ["BRK.B", "AAPL"])

    assert snapshot.row_count == 3
    assert snapshot.tickers == ("AAPL", "BRK.B", "MSFT")
    assert pilot.tickers == ("BRK.B", "AAPL")
    assert any("survivorship bias" in warning.lower() for warning in snapshot.warnings)


def test_load_universe_snapshot_rejects_duplicate_tickers_after_normalization(tmp_path: Path) -> None:
    snapshot_path = tmp_path / "bad_universe.csv"
    snapshot_path.write_text(
        "ticker,name\nAAPL,Apple\naapl,Apple duplicate\n",
        encoding="utf-8",
    )

    with pytest.raises(UniverseBuilderError, match="duplicate tickers"):
        load_universe_snapshot(snapshot_path)


def test_twelve_data_client_parses_empty_time_series_payload() -> None:
    client = TwelveDataClient(api_key="test-key")

    rows = client.parse_time_series({"meta": {"symbol": "AAPL"}, "values": []}, symbol="AAPL")

    assert rows == []
    assert client.is_empty_time_series_payload({"values": []}) is True


def test_twelve_data_client_surfaces_provider_errors_readably() -> None:
    client = TwelveDataClient(
        api_key="test-key",
        session=cast(requests.Session, _FakeSession(_FakeResponse({"status": "error", "message": "bad symbol"}))),
    )

    with pytest.raises(RuntimeError, match="bad symbol"):
        client.get_time_series("AAPL")


def test_finnhub_chunking_and_news_normalization() -> None:
    client = FinnhubClient(api_key="test-key")

    chunks = client.iter_date_chunks("2024-01-01", "2024-01-05", chunk_days=2)
    assert chunks == [
        ("2024-01-01", "2024-01-02"),
        ("2024-01-03", "2024-01-04"),
        ("2024-01-05", "2024-01-05"),
    ]

    articles = client.normalize_company_news(
        [
            {
                "id": 123,
                "datetime": 1704153600,
                "headline": " Sample headline ",
                "summary": "",
                "source": "Reuters",
                "url": "https://example.com/story?id=1#fragment",
                "image": None,
                "category": "company",
                "related": "AAPL",
            }
        ],
        symbol="AAPL",
    )

    assert articles[0]["ticker"] == "AAPL"
    assert articles[0]["article_id"] == "123"
    assert articles[0]["summary"] is None
    assert articles[0]["url"] == "https://example.com/story?id=1"
    assert articles[0]["published_date_utc"].isoformat() == "2024-01-02"


def test_finnhub_client_handles_empty_company_news_response() -> None:
    client = FinnhubClient(
        api_key="test-key",
        session=cast(requests.Session, _FakeSession(_FakeResponse([], status_code=200))),
    )

    payload, metadata = client.get_company_news("BRK.B", "2024-01-01", "2024-01-02")

    assert payload == []
    assert metadata.symbol == "BRK.B"
    assert metadata.response_status == 200


def test_sec_edgar_extracts_company_metadata_and_mappings() -> None:
    client = SecEdgarClient(user_agent="Name email@example.com Project")
    payload = {
        "cik": "320193",
        "tickers": ["AAPL"],
        "exchanges": ["Nasdaq"],
        "name": "Apple Inc.",
        "formerNames": [{"name": "Apple Computer, Inc.", "from": "1977-01-03", "to": "2007-01-09"}],
        "addresses": {
            "business": {
                "street1": "One Apple Park Way",
                "city": "Cupertino",
                "stateOrCountry": "CA",
                "zipCode": "95014",
            }
        },
    }

    metadata = client.extract_company_metadata(payload)
    mappings = client.extract_ticker_cik_mappings(payload)

    assert metadata["cik"] == "0000320193"
    assert metadata["ticker"] == "AAPL"
    assert metadata["former_names"][0]["name"] == "Apple Computer, Inc."
    assert metadata["business_address"]["city"] == "Cupertino"
    assert mappings == [{"ticker": "AAPL", "cik": "0000320193", "exchange": "Nasdaq", "source": "sec_edgar"}]


def test_split_events_client_normalizes_ratios_and_dates() -> None:
    client = SplitEventsClient(provider_name="external_or_upgrade_path")
    events = client.normalize_events(
        [
            {"executionDate": "2020-08-31", "ratio": "4:1", "id": "event-1"},
            {"executionDate": "2022-08-25", "numerator": 3, "denominator": 1, "event_id": "event-2"},
        ],
        symbol="AAPL",
        source_name="fallback_provider",
    )

    assert [event.split_factor for event in events] == [4.0, 3.0]
    assert events[0].ticker == "AAPL"
    assert events[0].provider_event_id == "event-1"
    client.validate_known_split_dates(events, ["2020-08-31", "2022-08-25"])
