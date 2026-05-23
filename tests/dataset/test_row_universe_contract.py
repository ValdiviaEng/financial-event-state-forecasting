from __future__ import annotations

import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID, ContractError  # noqa: E402
from event_state_forecasting.dataset.row_universe import compare_row_universes, row_universe_digest, sorted_row_keys  # noqa: E402


def test_row_universe_digest_is_order_stable() -> None:
    records = [_row("AAPL", "2024-04-01", "1d"), _row("MSFT", "2024-04-02", "5d")]

    assert row_universe_digest(records) == row_universe_digest(list(reversed(records)))


def test_sorted_row_keys_fails_on_duplicate_keys() -> None:
    record = _row("AAPL", "2024-04-01", "1d")

    with pytest.raises(ContractError, match="duplicate keys"):
        sorted_row_keys([record, dict(record)])


def test_compare_row_universes_reports_missing_and_extra_rows() -> None:
    reference = [_row("AAPL", "2024-04-01", "1d"), _row("MSFT", "2024-04-01", "1d")]
    candidate = [_row("AAPL", "2024-04-01", "1d"), _row("NVDA", "2024-04-01", "1d")]

    comparison = compare_row_universes(reference, candidate)

    assert comparison["equal"] is False
    assert comparison["missing_count"] == 1
    assert comparison["extra_count"] == 1


def _row(ticker: str, as_of_date: str, horizon_id: str) -> dict[str, str]:
    return {
        "benchmark_family_id": BENCHMARK_FAMILY_ID,
        "canonical_ticker": ticker,
        "as_of_date": as_of_date,
        "horizon_id": horizon_id,
    }
