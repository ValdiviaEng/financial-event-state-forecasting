from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import SecretStr

from src.data.data_contracts import validate_manifest, validate_records
from src.data.modeling_dataset import ModelingDatasetBuilder
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
    return [
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
        for index, close in enumerate(closes, start=1)
    ]


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
    return [{"ticker": "AAPL", "company_quality_score": 0.9, "company_exchange_rank": 1.0}]


def test_final_panel_manifest_tracks_actual_branches_and_rows(tmp_path: Path) -> None:
    builder = ModelingDatasetBuilder.from_settings(_build_test_settings(tmp_path))
    panel, manifest = builder.build_panel(
        adjusted_price_rows=_adjusted_rows(),
        benchmark_rows=_benchmark_rows(),
        event_state_rows=_event_state_rows(),
        company_feature_rows=_company_feature_rows(),
        dataset_version="integrity_panel_v1",
        event_state_version="es_v1",
        company_feature_version="kb_v1",
    )

    validate_records("modeling_panel", panel.to_dict(orient="records"))
    validate_manifest(manifest)

    assert manifest["dataset_name"] == "modeling_panel"
    assert set(manifest["source_tables"]) >= {"adjusted_prices_daily", "labels_multi_horizon", "event_states_daily", "company_kb"}
    assert panel["split_adjusted_prices_used"].all()
    assert panel["event_state_version"].dropna().nunique() == 1
    assert panel["company_feature_version"].dropna().nunique() == 1


def test_company_features_merge_without_creating_duplicate_panel_rows(tmp_path: Path) -> None:
    builder = ModelingDatasetBuilder.from_settings(_build_test_settings(tmp_path))
    panel, _ = builder.build_panel(
        adjusted_price_rows=_adjusted_rows(),
        benchmark_rows=_benchmark_rows(),
        company_feature_rows=_company_feature_rows(),
        dataset_version="integrity_panel_v2",
    )

    assert panel.duplicated(subset=["ticker", "date"]).sum() == 0
    assert "company_quality_score" in panel.columns
    assert "company_exchange_rank" in panel.columns
