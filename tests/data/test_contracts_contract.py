from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.data.contracts import (  # noqa: E402
    APPROVED_HORIZONS,
    BENCHMARK_FAMILY_ID,
    NEWS_ALIGNMENT_STATUS,
    PENDING_SPLIT_ROLE,
    TARGET_FAMILY,
    ContractError,
    validate_manifest,
    validate_panel_records,
)


def test_validate_panel_records_accepts_required_stage2_schema() -> None:
    records = [_record("AAPL", horizon) for horizon in APPROVED_HORIZONS]

    summary = validate_panel_records(records)

    assert summary.row_count == len(APPROVED_HORIZONS)
    assert summary.duplicate_key_count == 0
    assert summary.horizon_counts == {horizon: 1 for horizon in APPROVED_HORIZONS}


def test_validate_panel_records_fails_on_missing_required_field() -> None:
    record = _record("AAPL", "1d")
    record.pop("feature_availability_timestamp")

    with pytest.raises(ContractError, match="missing required fields"):
        validate_panel_records([record])


def test_validate_panel_records_fails_on_duplicate_row_key() -> None:
    record = _record("AAPL", "1d")

    with pytest.raises(ContractError, match="duplicate row keys"):
        validate_panel_records([record, dict(record)])


def test_validate_manifest_protects_scope_values() -> None:
    manifest = _manifest()
    validate_manifest(manifest)

    manifest["protected_scope"]["horizons"] = ["1d"]
    with pytest.raises(ContractError, match="horizons"):
        validate_manifest(manifest)


def _record(ticker: str, horizon: str) -> dict[str, object]:
    return {
        "benchmark_family_id": BENCHMARK_FAMILY_ID,
        "dataset_version": "test_dataset_version",
        "canonical_ticker": ticker,
        "as_of_date": "2024-04-01",
        "prediction_timestamp": "2024-04-01T16:00:00-04:00",
        "horizon_id": horizon,
        "feature_availability_timestamp": "2024-04-01T16:00:00-04:00",
        "label_window_start": "2024-04-02",
        "label_window_end": "2024-04-03",
        "row_status": "active_stage2_row",
        "exclusion_reason": "",
        "split_role": PENDING_SPLIT_ROLE,
        "fold_id": PENDING_SPLIT_ROLE,
        "lockbox_flag": False,
        "purge_flag": False,
        "embargo_flag": False,
        "split_exclusion_reason": "pending_stage4_split_construction",
        "preprocessing_fit_allowed": False,
        "market_data_available_flag": True,
        "news_provider_window_status": "canonical_file_present",
        "aligned_news_count": 0,
        "no_news_flag": True,
        "empty_event_state_flag": True,
        "provider_empty_feed_flag": False,
        "provider_truncation_risk_flag": False,
        "news_alignment_status": NEWS_ALIGNMENT_STATUS,
    }


def _manifest() -> dict[str, object]:
    return {
        "identity": {"dataset_version": "test", "benchmark_claim": False},
        "protected_scope": {
            "benchmark_family_id": BENCHMARK_FAMILY_ID,
            "horizons": list(APPROVED_HORIZONS),
            "target_family": TARGET_FAMILY,
        },
        "sources": {},
        "coverage": {},
        "clean_window": {},
        "rows_and_labels": {},
        "availability": {},
        "separation": {},
        "hashes": {},
        "limitations": [],
        "non_claims": [],
    }
