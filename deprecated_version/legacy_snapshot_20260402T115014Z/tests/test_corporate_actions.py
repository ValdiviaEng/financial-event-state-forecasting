from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import cast

import pandas as pd
from pydantic import SecretStr
import pytest

from src.data.corporate_actions import (
    CorporateActionsError,
    apply_split_adjustments,
    compute_cumulative_future_split_factors,
    exclude_rows_around_split_dates,
)
from src.data.price_pipeline import MarketPricePipeline
from src.data.split_events_client import SplitEvent
from src.data.twelve_data_client import TwelveDataClient
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


def _sample_split_rows() -> list[dict]:
    return [
        {
            "date": "2020-08-28",
            "ticker": "AAPL",
            "open": 500.0,
            "high": 505.0,
            "low": 495.0,
            "close": 500.0,
            "volume": 100,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
        },
        {
            "date": "2020-08-31",
            "ticker": "AAPL",
            "open": 125.0,
            "high": 128.0,
            "low": 124.0,
            "close": 126.0,
            "volume": 450,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
        },
        {
            "date": "2022-08-24",
            "ticker": "AAPL",
            "open": 300.0,
            "high": 302.0,
            "low": 298.0,
            "close": 300.0,
            "volume": 150,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
        },
        {
            "date": "2022-08-25",
            "ticker": "AAPL",
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.0,
            "volume": 500,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
        },
    ]


def _sample_split_events() -> list[SplitEvent]:
    return [
        SplitEvent(ticker="AAPL", split_date=datetime(2020, 8, 31).date(), split_factor=4.0, source="test"),
        SplitEvent(ticker="AAPL", split_date=datetime(2022, 8, 25).date(), split_factor=3.0, source="test"),
    ]


def _build_test_settings(tmp_path: Path) -> ResolvedSettings:
    environment = EnvironmentSettings(
        twelve_data_api_key=SecretStr("test-twelve-key"),
        finnhub_api_key=SecretStr("test-finnhub-key"),
        sec_user_agent="Test User test@example.com EventStateForecasting",
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        data_raw_dir=tmp_path / "data" / "raw",
        data_interim_dir=tmp_path / "data" / "interim",
        data_final_dir=tmp_path / "data" / "final",
        data_embeddings_dir=tmp_path / "data" / "embeddings",
        data_kb_dir=tmp_path / "data" / "kb",
        data_manifests_dir=tmp_path / "data" / "manifests",
        artifacts_dir=tmp_path / "artifacts",
        checkpoints_dir=tmp_path / "artifacts" / "checkpoints",
        figures_dir=tmp_path / "artifacts" / "figures",
        tables_dir=tmp_path / "artifacts" / "tables",
        runs_dir=tmp_path / "runs",
        reports_dir=tmp_path / "reports",
        notebooks_dir=tmp_path / "notebooks",
        logs_dir=tmp_path / "runs" / "logs",
    )
    paths = build_project_paths(tmp_path)
    paths.ensure_base_directories()
    return ResolvedSettings(
        environment=environment,
        project_paths=paths,
        config_dir=tmp_path / "configs",
        env_file=None,
        configs={
            "project": {"runtime": {"create_base_directories_on_load": True}},
            "data_sources": {"market_data": {}},
            "dataset_build": {"outputs": {"raw_market_subdir": "twelvedata"}},
        },
    )


def test_compute_cumulative_future_split_factors_handles_multiple_splits() -> None:
    factors = compute_cumulative_future_split_factors(_sample_split_rows(), _sample_split_events())
    factor_map = {item.date.isoformat(): item.cumulative_split_factor for item in factors}

    assert factor_map["2020-08-28"] == pytest.approx(12.0)
    assert factor_map["2020-08-31"] == pytest.approx(3.0)
    assert factor_map["2022-08-24"] == pytest.approx(3.0)
    assert factor_map["2022-08-25"] == pytest.approx(1.0)


def test_apply_split_adjustments_divides_prices_and_multiplies_volume() -> None:
    result = apply_split_adjustments(
        _sample_split_rows(),
        _sample_split_events(),
        adjustment_source="external_split_events",
    )
    adjusted_by_date = {row["date"].isoformat(): row for row in result.adjusted_rows}

    assert adjusted_by_date["2020-08-28"]["close"] == pytest.approx(500.0 / 12.0)
    assert adjusted_by_date["2020-08-28"]["volume"] == 1200
    assert adjusted_by_date["2020-08-31"]["close"] == pytest.approx(126.0 / 3.0)
    assert adjusted_by_date["2022-08-25"]["close"] == pytest.approx(100.0)


def test_split_day_jump_is_reduced_after_adjustment() -> None:
    result = apply_split_adjustments(
        _sample_split_rows(),
        _sample_split_events(),
        adjustment_source="external_split_events",
    )

    diagnostics = result.diagnostics
    split_day_checks = {item["split_date"]: item for item in diagnostics["split_day_checks"]}
    assert abs(split_day_checks["2020-08-31"]["adjusted_close_to_split_return"]) < abs(
        split_day_checks["2020-08-31"]["raw_close_to_split_return"]
    )
    assert abs(split_day_checks["2022-08-25"]["adjusted_close_to_split_return"]) < abs(
        split_day_checks["2022-08-25"]["raw_close_to_split_return"]
    )


def test_split_event_is_skipped_when_raw_window_already_appears_adjusted() -> None:
    rows = [
        {
            "date": "2024-06-07",
            "ticker": "NVDA",
            "open": 120.0,
            "high": 121.0,
            "low": 119.0,
            "close": 120.888,
            "volume": 100,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
        },
        {
            "date": "2024-06-10",
            "ticker": "NVDA",
            "open": 121.0,
            "high": 122.0,
            "low": 120.0,
            "close": 121.790,
            "volume": 110,
            "source": "twelve_data",
            "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
        },
    ]
    split_events = [SplitEvent(ticker="NVDA", split_date=datetime(2024, 6, 10).date(), split_factor=10.0, source="test")]

    result = apply_split_adjustments(rows, split_events, adjustment_source="test_source")
    adjusted_by_date = {row["date"].isoformat(): row for row in result.adjusted_rows}

    assert adjusted_by_date["2024-06-07"]["close"] == pytest.approx(120.888)
    assert any("already appears split-adjusted" in issue for issue in result.diagnostics["issues"])


def test_missing_split_policy_warn_return_raw_keeps_rows_unadjusted() -> None:
    result = apply_split_adjustments(
        _sample_split_rows()[:2],
        [],
        adjustment_source="missing_source",
        missing_split_policy="warn_return_raw",
    )

    adjusted_by_date = {row["date"].isoformat(): row for row in result.adjusted_rows}
    assert adjusted_by_date["2020-08-28"]["close"] == pytest.approx(500.0)
    assert result.diagnostics["issues"]


def test_missing_split_policy_error_raises() -> None:
    with pytest.raises(CorporateActionsError, match="No split events provided"):
        apply_split_adjustments(
            _sample_split_rows()[:2],
            [],
            adjustment_source="missing_source",
            missing_split_policy="error",
        )


def test_exclude_rows_around_split_dates_filters_window() -> None:
    filtered = exclude_rows_around_split_dates(
        _sample_split_rows(),
        _sample_split_events()[:1],
        window_days=1,
    )
    filtered_dates = [row["date"].isoformat() for row in filtered]

    assert "2020-08-31" not in filtered_dates
    assert "2020-08-28" in filtered_dates


def test_price_pipeline_build_adjusted_prices_for_ticker_writes_outputs(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    raw_rows = _sample_split_rows()
    raw_path = settings.project_paths.data_interim_dir / "prices_daily" / "AAPL.parquet"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(raw_rows).to_parquet(raw_path, index=False)

    pipeline = MarketPricePipeline(settings=settings, client=cast(TwelveDataClient, object()))
    summary = pipeline.build_adjusted_prices_for_ticker(
        "AAPL",
        split_events=_sample_split_events(),
        adjustment_source="external_split_events",
    )

    adjusted_path = Path(summary["adjusted_price_path"])
    report_path = Path(summary["adjustment_report_path"])
    assert adjusted_path.exists()
    assert report_path.exists()

    adjusted_rows = pd.read_parquet(adjusted_path)
    assert "adjustment_source" in adjusted_rows.columns
    assert "cumulative_split_factor" in adjusted_rows.columns
