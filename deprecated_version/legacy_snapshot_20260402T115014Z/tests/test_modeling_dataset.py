from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from pydantic import SecretStr
import pytest

from src.data.modeling_dataset import ModelingDatasetBuilder, ModelingDatasetError
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


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
            "features": {
                "market_features": {
                    "return_windows": [1],
                    "volatility_windows": [2],
                    "momentum_windows": [2],
                    "volume_windows": [2],
                }
            },
            "labels": {"horizons": [1, 2]},
        },
    )


def _adjusted_rows() -> list[dict]:
    closes = [100.0, 110.0, 120.0, 90.0]
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
                "volume": 1000 + index,
                "source": "twelve_data",
                "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
                "adjustment_source": "split_events",
            }
        )
    return rows


def _benchmark_rows() -> list[dict]:
    return [
        {"date": "2024-01-01", "close": 200.0},
        {"date": "2024-01-02", "close": 201.0},
        {"date": "2024-01-03", "close": 202.0},
        {"date": "2024-01-04", "close": 203.0},
    ]


def _event_state_rows() -> list[dict]:
    return [
        {
            "ticker": "AAPL",
            "date": "2024-01-01",
            "state_vector": [0.1, 0.2],
            "news_count": 1,
            "lookback_days": 2,
            "decay_half_life_days": 1,
            "density": 0.5,
            "conflict": 0.0,
            "novelty": 0.0,
        },
        {
            "ticker": "AAPL",
            "date": "2024-01-02",
            "state_vector": [0.2, 0.3],
            "news_count": 2,
            "lookback_days": 2,
            "decay_half_life_days": 1,
            "density": 1.0,
            "conflict": 0.1,
            "novelty": 0.2,
        },
    ]


def _company_feature_rows() -> list[dict]:
    return [{"ticker": "AAPL", "sector": "Technology", "exchange": "Nasdaq"}]


def test_modeling_dataset_builder_assembles_unique_panel_and_manifest(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    builder = ModelingDatasetBuilder.from_settings(settings)

    panel, manifest = builder.build_panel(
        adjusted_price_rows=_adjusted_rows(),
        benchmark_rows=_benchmark_rows(),
        event_state_rows=_event_state_rows(),
        company_feature_rows=_company_feature_rows(),
        dataset_version="panel_test_v1",
    )

    assert len(panel) == 4
    assert panel.duplicated(subset=["ticker", "date"]).sum() == 0
    assert panel["split_adjusted_prices_used"].all()
    assert "state_vector" in panel.columns
    assert "sector" in panel.columns
    assert "return_1" in panel.columns
    assert "y_ret_1" in panel.columns
    assert manifest["dataset_name"] == "modeling_panel"
    assert manifest["summary"]["row_count"] == 4


def test_modeling_dataset_builder_writes_panel_and_manifest(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    builder = ModelingDatasetBuilder.from_settings(settings)

    panel, manifest = builder.build_panel(
        adjusted_price_rows=_adjusted_rows(),
        benchmark_rows=_benchmark_rows(),
        event_state_rows=_event_state_rows(),
        dataset_version="panel_test_v2",
    )
    result = builder.write_panel_and_manifest(panel=panel, manifest_payload=manifest, dataset_version="panel_test_v2")

    assert result.panel_path.exists()
    assert result.manifest_path.exists()
    saved_panel = pd.read_parquet(result.panel_path)
    assert len(saved_panel) == 4


def test_modeling_dataset_builder_rejects_duplicate_optional_merge_rows(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    builder = ModelingDatasetBuilder.from_settings(settings)
    duplicate_event_states = _event_state_rows() + [_event_state_rows()[0]]

    with pytest.raises(ModelingDatasetError, match="duplicate rows"):
        builder.build_panel(
            adjusted_price_rows=_adjusted_rows(),
            benchmark_rows=_benchmark_rows(),
            event_state_rows=duplicate_event_states,
            dataset_version="panel_bad_v1",
        )
