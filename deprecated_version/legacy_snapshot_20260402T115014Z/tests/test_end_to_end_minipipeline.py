from __future__ import annotations

import importlib
import json
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd
from pydantic import SecretStr
import pytest

from src.data.modeling_dataset import ModelingDatasetBuilder
from src.features.event_state import build_daily_event_states
from src.features.news_embeddings import build_article_embedding_cache
from src.models.ablation_runner import build_ablation_summary
from src.models.metric_registry import evaluate_prediction_frame
from src.models.trainer import train_market_baseline_fold, train_multimodal_fold
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


def _torch_available() -> bool:
    try:
        importlib.import_module("torch")
    except ModuleNotFoundError:
        return False
    return True


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
            "labels": {"horizons": [1]},
        },
    )


def _adjusted_rows() -> list[dict]:
    rows = []
    closes = {"AAPL": [1.0, 1.1, 1.2, 1.1, 1.3, 1.4], "MSFT": [1.2, 1.25, 1.3, 1.28, 1.35, 1.4]}
    for ticker, ticker_closes in closes.items():
        for idx, close in enumerate(ticker_closes, start=1):
            rows.append(
                {
                    "date": f"2024-01-0{idx}",
                    "ticker": ticker,
                    "open": close - 0.02,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000 + idx,
                    "source": "twelve_data",
                    "ingest_ts": datetime(2026, 3, 18, tzinfo=UTC),
                    "adjustment_source": "split_events",
                }
            )
    return rows


def _benchmark_rows() -> list[dict]:
    return [
        {"date": f"2024-01-0{idx}", "close": 2.0 + (0.01 * idx)} for idx in range(1, 7)
    ]


def _articles() -> list[dict]:
    return [
        {
            "article_id": "a1",
            "ticker": "AAPL",
            "headline": "Apple launches service",
            "summary": "Recurring revenue expansion",
            "published_ts_utc": datetime(2024, 1, 2, 18, 0, tzinfo=UTC),
            "asof_trade_date": date(2024, 1, 2),
        },
        {
            "article_id": "a2",
            "ticker": "AAPL",
            "headline": "Apple analyst update",
            "summary": "Target price increased",
            "published_ts_utc": datetime(2024, 1, 3, 18, 0, tzinfo=UTC),
            "asof_trade_date": date(2024, 1, 3),
        },
        {
            "article_id": "m1",
            "ticker": "MSFT",
            "headline": "Microsoft guidance raised",
            "summary": "Cloud momentum remains strong",
            "published_ts_utc": datetime(2024, 1, 2, 18, 0, tzinfo=UTC),
            "asof_trade_date": date(2024, 1, 2),
        },
    ]


def _write_run_summary(base_dir: Path, *, run_id: str, model_name: str, metrics_path: Path, panel_path: Path) -> Path:
    summary_path = base_dir / f"{run_id}_summary.json"
    payload = {
        "run_id": run_id,
        "panel_path": str(panel_path.resolve()),
        "horizons": [1],
        "split_count": 1,
        "results": [{"model_name": model_name, "split_id": 0, "metrics_path": str(metrics_path.resolve())}],
    }
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return summary_path


def test_end_to_end_minipipeline_builds_train_evaluate_and_compare(tmp_path: Path) -> None:
    if not _torch_available():
        pytest.skip("PyTorch is required for the end-to-end minipipeline test.")

    settings = _build_test_settings(tmp_path)
    builder = ModelingDatasetBuilder.from_settings(settings)
    articles = _articles()
    cache = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)
    event_states = build_daily_event_states(
        articles,
        cache,
        model_id="hashing",
        lookback_days=2,
        decay_half_life_days=1,
        feature_dates=[date(2024, 1, day) for day in range(1, 7)],
    )
    panel, manifest = builder.build_panel(
        adjusted_price_rows=_adjusted_rows(),
        benchmark_rows=_benchmark_rows(),
        event_state_rows=event_states,
        dataset_version="mini_panel_v1",
        event_state_version="v1",
    )
    result = builder.write_panel_and_manifest(panel=panel, manifest_payload=manifest, dataset_version="mini_panel_v1")

    baseline = train_market_baseline_fold(
        panel=panel,
        train_dates=tuple(date(2024, 1, day) for day in range(1, 4)),
        validation_dates=(date(2024, 1, 4),),
        test_dates=(date(2024, 1, 5),),
        model_name="ridge",
        split_id=0,
        run_dir=tmp_path / "baseline",
        horizons=[1],
        seed=42,
    )
    multimodal = train_multimodal_fold(
        panel=panel,
        train_dates=tuple(date(2024, 1, day) for day in range(1, 4)),
        validation_dates=(date(2024, 1, 4),),
        test_dates=(date(2024, 1, 5),),
        split_id=0,
        run_dir=tmp_path / "multimodal",
        horizons=[1],
        seed=42,
        training_config={
            "device": "cpu",
            "max_epochs": 20,
            "early_stopping_patience": 5,
            "train_batch_size": 4,
            "eval_batch_size": 8,
            "optimizer": "adamw",
            "learning_rate": 0.02,
            "weight_decay": 0.0,
            "loss_name": "mse",
            "num_workers": 0,
            "pin_memory": False,
        },
        model_config={"branches": {"event_state": True, "company_profile": False}},
    )

    baseline_predictions = pd.read_parquet(baseline.predictions_path)
    multimodal_predictions = pd.read_parquet(multimodal.predictions_path)
    labels = panel[["ticker", "date", "y_excess_ret_1"]].copy()
    baseline_eval = evaluate_prediction_frame(baseline_predictions, labels, target_columns=["y_excess_ret_1"])
    multimodal_eval = evaluate_prediction_frame(multimodal_predictions, labels, target_columns=["y_excess_ret_1"])

    baseline_summary = _write_run_summary(tmp_path, run_id="baseline_mini", model_name="ridge", metrics_path=baseline.metrics_path, panel_path=result.panel_path)
    multimodal_summary = _write_run_summary(tmp_path, run_id="multimodal_mini", model_name="multimodal_event_state", metrics_path=multimodal.metrics_path, panel_path=result.panel_path)
    ablation = build_ablation_summary([baseline_summary, multimodal_summary], partition="test", metric_name="rmse")

    assert result.panel_path.exists()
    assert baseline.predictions_path.exists()
    assert multimodal.predictions_path.exists()
    assert not baseline_eval["regression"].empty
    assert not multimodal_eval["regression"].empty
    assert len(ablation) == 2
