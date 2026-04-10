"""Leakage-safe end-of-day market feature builders."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd

from src.data.data_contracts import validate_records


DEFAULT_RETURN_WINDOWS = (1, 5, 20)
DEFAULT_VOLATILITY_WINDOWS = (5, 20)
DEFAULT_MOMENTUM_WINDOWS = (5, 20, 60)
DEFAULT_VOLUME_WINDOWS = (5, 20)


def build_market_features(
    adjusted_price_rows: Sequence[dict[str, Any]],
    *,
    benchmark_rows: Sequence[dict[str, Any]] | None = None,
    return_windows: Sequence[int] = DEFAULT_RETURN_WINDOWS,
    volatility_windows: Sequence[int] = DEFAULT_VOLATILITY_WINDOWS,
    momentum_windows: Sequence[int] = DEFAULT_MOMENTUM_WINDOWS,
    volume_windows: Sequence[int] = DEFAULT_VOLUME_WINDOWS,
) -> pd.DataFrame:
    """Build conservative market features from adjusted OHLCV rows.

    The function validates inputs against the `adjusted_prices_daily` contract,
    sorts rows by `(ticker, date)`, and only uses information available up to the
    feature date itself.
    """

    validate_records("adjusted_prices_daily", adjusted_price_rows)
    price_df = _prepare_price_frame(adjusted_price_rows)

    feature_frames = []
    for ticker, ticker_df in price_df.groupby("ticker", sort=True):
        ticker_features = ticker_df[["ticker", "date"]].copy()
        close = ticker_df["close"].astype(float)
        open_ = ticker_df["open"].astype(float)
        high = ticker_df["high"].astype(float)
        low = ticker_df["low"].astype(float)
        volume = ticker_df["volume"].astype(float)

        daily_return = close.pct_change(1)
        ticker_features["daily_return_1"] = daily_return
        ticker_features["intraday_range_pct"] = (high - low) / close.replace(0, np.nan)
        ticker_features["open_close_return"] = (close - open_) / open_.replace(0, np.nan)

        for window in return_windows:
            ticker_features[f"return_{window}"] = close.pct_change(window)
            ticker_features[f"log_return_{window}"] = np.log(close / close.shift(window))

        for window in volatility_windows:
            ticker_features[f"rolling_volatility_{window}"] = daily_return.rolling(window).std()

        for window in momentum_windows:
            ticker_features[f"momentum_{window}"] = close / close.shift(window) - 1.0

        for window in volume_windows:
            rolling_volume = volume.rolling(window).mean()
            ticker_features[f"volume_ratio_{window}"] = volume / rolling_volume.replace(0, np.nan)
            ticker_features[f"volume_surprise_{window}"] = volume - rolling_volume

        feature_frames.append(ticker_features)

    features = pd.concat(feature_frames, ignore_index=True)

    if benchmark_rows:
        features = _merge_benchmark_relative_features(
            features,
            benchmark_rows=benchmark_rows,
            return_windows=return_windows,
        )

    return features


def summarize_market_feature_coverage(features: pd.DataFrame) -> dict[str, Any]:
    """Return a small summary describing market-feature coverage and sparsity."""

    feature_columns = [column for column in features.columns if column not in {"ticker", "date"}]
    non_null_counts = {column: int(features[column].notna().sum()) for column in feature_columns}
    return {
        "row_count": int(len(features)),
        "ticker_count": int(features["ticker"].nunique()) if "ticker" in features else 0,
        "feature_columns": feature_columns,
        "non_null_counts": non_null_counts,
    }


def _prepare_price_frame(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows).copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.date
    frame = frame.sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)
    return frame


def _prepare_benchmark_frame(
    benchmark_rows: Sequence[dict[str, Any]],
    *,
    return_windows: Sequence[int],
) -> pd.DataFrame:
    benchmark_df = pd.DataFrame(benchmark_rows).copy()
    if "date" not in benchmark_df.columns or "close" not in benchmark_df.columns:
        raise ValueError("Benchmark rows must include at least 'date' and 'close'.")

    benchmark_df["date"] = pd.to_datetime(benchmark_df["date"]).dt.date
    benchmark_df = benchmark_df.sort_values("date", kind="stable").reset_index(drop=True)
    close = benchmark_df["close"].astype(float)

    prepared = benchmark_df[["date"]].copy()
    for window in return_windows:
        prepared[f"benchmark_return_{window}"] = close.pct_change(window)
    return prepared


def _merge_benchmark_relative_features(
    feature_df: pd.DataFrame,
    *,
    benchmark_rows: Sequence[dict[str, Any]],
    return_windows: Sequence[int],
) -> pd.DataFrame:
    benchmark_df = _prepare_benchmark_frame(benchmark_rows, return_windows=return_windows)
    merged = feature_df.merge(benchmark_df, how="left", on="date")
    for window in return_windows:
        feature_column = f"return_{window}"
        benchmark_column = f"benchmark_return_{window}"
        merged[f"benchmark_relative_return_{window}"] = merged[feature_column] - merged[benchmark_column]
    return merged
