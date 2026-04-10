from __future__ import annotations

import importlib
import json
from datetime import date
from pathlib import Path

import pandas as pd

from src.models.dataloaders import (
    MultimodalPanelDataset,
    create_multimodal_dataloader,
    select_event_state_scalar_columns,
    select_market_feature_columns,
    select_target_columns,
)
from src.models.inference import load_model_checkpoint
from src.models.multimodal_models import build_multimodal_regressor
from src.models.trainer import train_multimodal_fold


def _torch():
    return importlib.import_module("torch")


def _panel() -> pd.DataFrame:
    rows = []
    dates = [date(2024, 1, day) for day in range(1, 9)]
    for ticker_idx, ticker in enumerate(("AAPL", "MSFT"), start=1):
        for idx, current_date in enumerate(dates):
            market_signal = 0.1 * (idx + ticker_idx)
            event_signal = 0.2 * ((idx % 3) + 1)
            state_vector = [event_signal, event_signal / 2.0]
            conflict = 0.01 * idx
            density = 0.5 + (0.1 * (idx % 2))
            target = 0.6 * market_signal + 0.8 * event_signal - 0.3 * conflict
            rows.append(
                {
                    "ticker": ticker,
                    "date": current_date,
                    "split_adjusted_prices_used": True,
                    "dataset_version": "panel_multimodal_v1",
                    "market_feature_version": "v1",
                    "label_version": "v1",
                    "event_state_version": "v1",
                    "company_feature_version": None,
                    "open": 1.0 + market_signal,
                    "high": 1.1 + market_signal,
                    "low": 0.9 + market_signal,
                    "close": 1.05 + market_signal,
                    "volume": 1.0 + market_signal,
                    "daily_return_1": market_signal,
                    "return_1": market_signal,
                    "log_return_1": market_signal * 0.95,
                    "rolling_volatility_2": 0.01 + market_signal * 0.1,
                    "momentum_2": market_signal * 1.1,
                    "volume_ratio_2": 1.0 + market_signal,
                    "volume_surprise_2": 5.0 * market_signal,
                    "state_vector": state_vector,
                    "news_count": 1 + (idx % 3),
                    "density": density,
                    "novelty": 0.02 * idx,
                    "conflict": conflict,
                    "lookback_days": 3,
                    "decay_half_life_days": 2,
                    "y_excess_ret_1": target,
                }
            )
    return pd.DataFrame(rows)


def test_multimodal_forward_pass_shape() -> None:
    panel = _panel()
    market_columns = select_market_feature_columns(panel)
    target_columns = select_target_columns(panel, horizons=[1])
    event_scalar_columns = select_event_state_scalar_columns(panel)
    dataset = MultimodalPanelDataset(
        panel,
        market_feature_columns=market_columns,
        target_columns=target_columns,
        event_scalar_columns=event_scalar_columns,
        event_vector_column="state_vector",
    )

    model = build_multimodal_regressor(
        market_input_dim=len(market_columns),
        event_state_input_dim=int(dataset.event_state_features.shape[1]),
        output_dim=len(target_columns),
        market_hidden_dim=16,
        event_hidden_dim=8,
        fusion_hidden_dim=16,
        use_event_state=True,
    )

    torch = _torch()
    outputs = model(
        torch.tensor(dataset.market_features[:3], dtype=torch.float32),
        event_state_features=torch.tensor(dataset.event_state_features[:3], dtype=torch.float32),
        event_state_mask=torch.tensor(dataset.event_state_mask[:3], dtype=torch.float32),
    )
    assert tuple(outputs.shape) == (3, 1)


def test_multimodal_dataloader_batch_schema() -> None:
    panel = _panel()
    market_columns = select_market_feature_columns(panel)
    target_columns = select_target_columns(panel, horizons=[1])
    event_scalar_columns = select_event_state_scalar_columns(panel)
    dataset = MultimodalPanelDataset(
        panel,
        market_feature_columns=market_columns,
        target_columns=target_columns,
        event_scalar_columns=event_scalar_columns,
        event_vector_column="state_vector",
    )
    dataloader = create_multimodal_dataloader(dataset, batch_size=4, shuffle=False)
    batch = next(iter(dataloader))

    assert hasattr(batch, "market_features")
    assert hasattr(batch, "event_state_features")
    assert hasattr(batch, "event_state_mask")
    assert hasattr(batch, "targets")
    assert hasattr(batch, "row_ids")
    assert tuple(batch.market_features.shape) == (4, len(market_columns))
    assert batch.event_state_features is not None
    assert batch.event_state_mask is not None


def test_multimodal_training_can_overfit_tiny_subset(tmp_path: Path) -> None:
    panel = _panel()
    result = train_multimodal_fold(
        panel=panel,
        train_dates=tuple(date(2024, 1, day) for day in range(1, 5)),
        validation_dates=tuple(date(2024, 1, day) for day in range(1, 5)),
        test_dates=(date(2024, 1, 5),),
        split_id=0,
        run_dir=tmp_path / "multimodal_run",
        horizons=[1],
        seed=123,
        training_config={
            "device": "cpu",
            "max_epochs": 120,
            "early_stopping_patience": 30,
            "train_batch_size": 4,
            "eval_batch_size": 8,
            "optimizer": "adamw",
            "learning_rate": 0.05,
            "weight_decay": 0.0,
            "loss_name": "mse",
            "num_workers": 0,
            "pin_memory": False,
        },
        model_config={
            "branches": {"event_state": True, "company_profile": False},
            "market_hidden_dim": 16,
            "event_hidden_dim": 8,
            "fusion_hidden_dim": 16,
            "dropout": 0.0,
        },
    )

    metrics = json.loads(result.metrics_path.read_text(encoding="utf-8"))
    train_metrics = metrics["metrics"]["train"]["y_excess_ret_1"]
    assert train_metrics["rmse"] < 0.02
    assert result.checkpoint_path.exists()
    assert result.predictions_path.exists()


def test_multimodal_prediction_export_matches_baseline_schema(tmp_path: Path) -> None:
    panel = _panel()
    result = train_multimodal_fold(
        panel=panel,
        train_dates=tuple(date(2024, 1, day) for day in range(1, 5)),
        validation_dates=(date(2024, 1, 5),),
        test_dates=(date(2024, 1, 6),),
        split_id=1,
        run_dir=tmp_path / "multimodal_schema",
        horizons=[1],
        seed=123,
        training_config={
            "device": "cpu",
            "max_epochs": 10,
            "early_stopping_patience": 5,
            "train_batch_size": 4,
            "eval_batch_size": 8,
            "optimizer": "adamw",
            "learning_rate": 0.01,
            "weight_decay": 0.0,
            "loss_name": "mse",
            "num_workers": 0,
            "pin_memory": False,
        },
        model_config={"branches": {"event_state": True, "company_profile": False}},
    )
    predictions = pd.read_parquet(result.predictions_path)

    assert {"ticker", "date", "pred_y_excess_ret_1", "partition", "model_name", "split_id"}.issubset(predictions.columns)
    assert set(predictions["partition"]).issubset({"train", "validation", "test"})

    checkpoint = load_model_checkpoint(result.checkpoint_path, model_name="multimodal_event_state")
    assert "state_dict" in checkpoint
