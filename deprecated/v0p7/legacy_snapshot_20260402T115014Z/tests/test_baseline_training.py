from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from src.models.baseline_models import SklearnRegressorWrapper, load_baseline_checkpoint
from src.models.dataloaders import MarketPanelDataset, filter_rows_with_complete_targets, select_market_feature_columns, select_target_columns
from src.models.inference import predict_sklearn_model
from src.models.trainer import train_market_baseline_fold


def _panel() -> pd.DataFrame:
    rows = []
    base_dates = [date(2024, 1, day) for day in range(1, 9)]
    for ticker_index, ticker in enumerate(("AAPL", "MSFT"), start=1):
        for idx, current_date in enumerate(base_dates):
            feature_value = float(idx + ticker_index)
            rows.append(
                {
                    "ticker": ticker,
                    "date": current_date,
                    "split_adjusted_prices_used": True,
                    "dataset_version": "panel_test_v1",
                    "market_feature_version": "v1",
                    "label_version": "v1",
                    "event_state_version": None,
                    "company_feature_version": None,
                    "open": 100.0 + feature_value,
                    "high": 101.0 + feature_value,
                    "low": 99.0 + feature_value,
                    "close": 100.5 + feature_value,
                    "volume": 1000.0 + (10 * feature_value),
                    "daily_return_1": 0.01 * feature_value,
                    "return_1": 0.02 * feature_value,
                    "log_return_1": 0.019 * feature_value,
                    "rolling_volatility_2": 0.005 * feature_value,
                    "momentum_2": 0.03 * feature_value,
                    "volume_ratio_2": 1.0 + (0.01 * feature_value),
                    "volume_surprise_2": 5.0 * feature_value,
                    "y_excess_ret_1": 0.05 * feature_value,
                }
            )
    panel = pd.DataFrame(rows)
    panel.loc[panel["date"] == date(2024, 1, 8), "y_excess_ret_1"] = np.nan
    return panel


def test_market_dataloader_feature_and_target_selection() -> None:
    panel = _panel()
    feature_columns = select_market_feature_columns(panel)
    target_columns = select_target_columns(panel, horizons=[1])
    filtered = filter_rows_with_complete_targets(panel, target_columns=target_columns)
    dataset = MarketPanelDataset(filtered, feature_columns=feature_columns, target_columns=target_columns)

    assert "y_excess_ret_1" in target_columns
    assert "return_1" in feature_columns
    assert "ticker" not in feature_columns
    assert len(dataset) == len(filtered)
    item = dataset[0]
    assert "features" in item and "targets" in item and "row_id" in item


def test_train_market_baseline_fold_writes_artifacts(tmp_path: Path) -> None:
    panel = _panel()
    result = train_market_baseline_fold(
        panel=panel,
        train_dates=tuple(date(2024, 1, day) for day in range(1, 6)),
        validation_dates=(date(2024, 1, 6),),
        test_dates=(date(2024, 1, 7), date(2024, 1, 8)),
        model_name="ridge",
        split_id=0,
        run_dir=tmp_path / "run_ridge",
        horizons=[1],
        seed=123,
    )

    assert result.checkpoint_path.exists()
    assert result.predictions_path.exists()
    assert result.metrics_path.exists()

    predictions = pd.read_parquet(result.predictions_path)
    assert {"ticker", "date", "pred_y_excess_ret_1", "partition"}.issubset(predictions.columns)
    assert set(predictions["partition"]) == {"train", "validation", "test"}


def test_sklearn_checkpoint_round_trip_prediction_export(tmp_path: Path) -> None:
    panel = _panel()
    run_dir = tmp_path / "run_checkpoint"
    result = train_market_baseline_fold(
        panel=panel,
        train_dates=tuple(date(2024, 1, day) for day in range(1, 6)),
        validation_dates=(date(2024, 1, 6),),
        test_dates=(date(2024, 1, 7),),
        model_name="ridge",
        split_id=1,
        run_dir=run_dir,
        horizons=[1],
        seed=123,
    )

    loaded = load_baseline_checkpoint(result.checkpoint_path)
    assert isinstance(loaded, SklearnRegressorWrapper)

    feature_columns = select_market_feature_columns(panel)
    target_columns = select_target_columns(panel, horizons=[1])
    test_df = filter_rows_with_complete_targets(panel[panel["date"] == date(2024, 1, 7)], target_columns=target_columns)
    exported = predict_sklearn_model(
        loaded,
        test_df[feature_columns],
        row_ids=test_df[["ticker", "date"]].to_dict(orient="records"),
        target_columns=target_columns,
        model_name="ridge",
        split_id=1,
        partition="test",
    )
    assert len(exported) == len(test_df)
    assert "pred_y_excess_ret_1" in exported.columns


def test_ridge_training_is_deterministic_for_same_seed(tmp_path: Path) -> None:
    panel = _panel()
    common_kwargs = {
        "panel": panel,
        "train_dates": tuple(date(2024, 1, day) for day in range(1, 6)),
        "validation_dates": (date(2024, 1, 6),),
        "test_dates": (date(2024, 1, 7),),
        "model_name": "ridge",
        "horizons": [1],
        "seed": 123,
    }
    first = train_market_baseline_fold(split_id=2, run_dir=tmp_path / "run_one", **common_kwargs)
    second = train_market_baseline_fold(split_id=2, run_dir=tmp_path / "run_two", **common_kwargs)

    first_predictions = pd.read_parquet(first.predictions_path)
    second_predictions = pd.read_parquet(second.predictions_path)
    merged = first_predictions.merge(
        second_predictions,
        on=["ticker", "date", "partition", "split_id", "model_name"],
        suffixes=("_first", "_second"),
    )
    assert np.allclose(merged["pred_y_excess_ret_1_first"], merged["pred_y_excess_ret_1_second"])
