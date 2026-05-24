from __future__ import annotations

import importlib
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from src.models.ablation_runner import ensure_run_summaries_comparable
from src.models.trainer import train_market_baseline_fold, train_multimodal_fold
from src.split.leakage_checks import assert_no_future_profile_effective_dates


def _torch_available() -> bool:
    try:
        importlib.import_module("torch")
    except ModuleNotFoundError:
        return False
    return True


def _panel() -> pd.DataFrame:
    rows = []
    dates = [date(2024, 1, day) for day in range(1, 9)]
    for ticker_idx, ticker in enumerate(("AAPL", "MSFT"), start=1):
        for idx, current_date in enumerate(dates):
            market_signal = 0.1 * (idx + ticker_idx)
            event_signal = 0.2 * ((idx % 3) + 1)
            target = 0.6 * market_signal + 0.8 * event_signal - 0.3 * (0.01 * idx)
            rows.append(
                {
                    "ticker": ticker,
                    "date": current_date,
                    "split_adjusted_prices_used": True,
                    "dataset_version": "research_panel_v1",
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
                    "state_vector": [event_signal, event_signal / 2.0],
                    "news_count": 1 + (idx % 3),
                    "density": 0.5 + (0.1 * (idx % 2)),
                    "novelty": 0.02 * idx,
                    "conflict": 0.01 * idx,
                    "lookback_days": 3,
                    "decay_half_life_days": 2,
                    "y_excess_ret_1": target,
                }
            )
    panel = pd.DataFrame(rows)
    panel.loc[panel["date"] == date(2024, 1, 8), "y_excess_ret_1"] = float("nan")
    return panel


def test_baseline_and_multimodal_training_use_same_row_universe_for_same_fold(tmp_path: Path) -> None:
    if not _torch_available():
        pytest.skip("PyTorch is required for the multimodal research-integrity test.")

    panel = _panel()
    train_dates = tuple(date(2024, 1, day) for day in range(1, 5))
    validation_dates = (date(2024, 1, 5),)
    test_dates = (date(2024, 1, 6),)

    baseline = train_market_baseline_fold(
        panel=panel,
        train_dates=train_dates,
        validation_dates=validation_dates,
        test_dates=test_dates,
        model_name="ridge",
        split_id=0,
        run_dir=tmp_path / "baseline",
        horizons=[1],
        seed=42,
    )
    multimodal = train_multimodal_fold(
        panel=panel,
        train_dates=train_dates,
        validation_dates=validation_dates,
        test_dates=test_dates,
        split_id=0,
        run_dir=tmp_path / "multimodal",
        horizons=[1],
        seed=42,
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

    baseline_predictions = pd.read_parquet(baseline.predictions_path)
    multimodal_predictions = pd.read_parquet(multimodal.predictions_path)
    baseline_ids = set(tuple(row) for row in baseline_predictions[["ticker", "date", "partition"]].to_numpy())
    multimodal_ids = set(tuple(row) for row in multimodal_predictions[["ticker", "date", "partition"]].to_numpy())
    assert baseline_ids == multimodal_ids


def test_run_summaries_are_only_comparable_when_panel_and_horizons_match(tmp_path: Path) -> None:
    summary_a = {
        "run_id": "a",
        "panel_path": str((tmp_path / "panel_a.parquet").resolve()),
        "horizons": [1],
        "split_count": 1,
        "results": [],
    }
    summary_b = {
        "run_id": "b",
        "panel_path": str((tmp_path / "panel_a.parquet").resolve()),
        "horizons": [1],
        "split_count": 1,
        "results": [],
    }
    ensure_run_summaries_comparable([summary_a, summary_b])

    summary_c = dict(summary_b, panel_path=str((tmp_path / "panel_b.parquet").resolve()))
    with pytest.raises(Exception):
        ensure_run_summaries_comparable([summary_a, summary_c])


def test_future_profile_effective_dates_are_rejected() -> None:
    with pytest.raises(Exception):
        assert_no_future_profile_effective_dates(
            [{"date": date(2024, 1, 2), "effective_date": date(2024, 1, 3)}]
        )
