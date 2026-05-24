from __future__ import annotations

import pytest

from src.data.data_contracts import (
    MANIFEST_REQUIRED_FIELDS,
    DataContractError,
    SCHEMA_VERSION,
    get_table_contract,
    list_table_contracts,
    validate_columns,
    validate_manifest,
    validate_records,
)


def test_core_table_contracts_exist() -> None:
    contracts = list_table_contracts()

    expected = {
        "market_data_request_ledger",
        "prices_daily",
        "adjusted_prices_daily",
        "news_articles",
        "split_events",
        "article_embeddings",
        "event_states_daily",
        "company_kb",
        "company_ticker_mappings",
        "company_aliases",
        "labels_multi_horizon",
        "modeling_panel",
    }

    assert expected.issubset(contracts.keys())


def test_prices_daily_contract_has_expected_required_columns() -> None:
    contract = get_table_contract("prices_daily")

    assert contract.key_columns == ("ticker", "date")
    assert contract.required_column_names == (
        "date",
        "ticker",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "ingest_ts",
    )


def test_validate_columns_accepts_required_and_optional_columns() -> None:
    columns = [
        "date",
        "ticker",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "source",
        "ingest_ts",
        "extra_debug_column",
    ]

    validated = validate_columns("prices_daily", columns)

    assert "date" in validated
    assert "extra_debug_column" in validated


def test_validate_columns_rejects_missing_required_columns() -> None:
    incomplete_columns = ["date", "ticker", "open", "high", "low", "close"]

    with pytest.raises(DataContractError, match="missing required columns"):
        validate_columns("prices_daily", incomplete_columns)


def test_validate_records_rejects_missing_required_row_key() -> None:
    bad_rows = [
        {
            "date": "2024-01-01",
            "ticker": "AAPL",
            "open": 99.5,
            "high": 100.5,
            "low": 98.8,
            "close": 100.0,
            "volume": 1000000,
            "source": "twelve_data",
            "ingest_ts": "2024-01-02T00:00:00Z",
        },
        {
            "date": "2024-01-02",
            "ticker": "AAPL",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.5,
            "source": "twelve_data",
            "ingest_ts": "2024-01-03T00:00:00Z",
        }
    ]

    with pytest.raises(DataContractError, match="missing required keys"):
        validate_records("prices_daily", bad_rows)


def test_validate_records_rejects_duplicate_unique_key_in_modeling_panel() -> None:
    duplicate_rows = [
        {
            "ticker": "AAPL",
            "date": "2024-01-02",
            "split_adjusted_prices_used": True,
            "dataset_version": "panel_v1",
        },
        {
            "ticker": "AAPL",
            "date": "2024-01-02",
            "split_adjusted_prices_used": True,
            "dataset_version": "panel_v1",
        },
    ]

    with pytest.raises(DataContractError, match="Duplicate key detected"):
        validate_records("modeling_panel", duplicate_rows)


def test_validate_manifest_requires_expected_fields() -> None:
    manifest = {
        "manifest_version": "1",
        "dataset_name": "pilot_panel",
        "dataset_version": "v0",
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": "2026-03-18T00:00:00Z",
        "source_tables": ["prices_daily", "labels_multi_horizon"],
    }

    validated = validate_manifest(manifest)

    assert set(MANIFEST_REQUIRED_FIELDS).issubset(validated.keys())


def test_validate_manifest_rejects_missing_schema_version() -> None:
    bad_manifest = {
        "manifest_version": "1",
        "dataset_name": "pilot_panel",
        "dataset_version": "v0",
        "created_at_utc": "2026-03-18T00:00:00Z",
        "source_tables": ["prices_daily"],
    }

    with pytest.raises(DataContractError, match="missing required fields"):
        validate_manifest(bad_manifest)


def test_validate_columns_can_reject_unexpected_columns_when_requested() -> None:
    columns = [
        "ticker",
        "split_date",
        "split_factor",
        "source",
        "ingest_ts",
        "unexpected_field",
    ]

    with pytest.raises(DataContractError, match="unexpected columns"):
        validate_columns("split_events", columns, allow_additional_columns=False)
