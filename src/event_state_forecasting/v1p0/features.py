from __future__ import annotations

from typing import Any

import pandas as pd


class V1P0FeatureError(ValueError):
    """Raised when v1p0 feature inputs violate contract rules."""


def build_market_lag_features(panel: pd.DataFrame, config: dict[str, Any]) -> pd.DataFrame:
    row_key = list(config["row_key"])
    source_columns = list(config["source_columns"])
    required = [*row_key, "dataset_version", "market_open", "market_close", "market_volume"]
    if config.get("production_feature_set"):
        required.extend(["market_high", "market_low", "benchmark_close"])
    missing = [column for column in required if column not in panel.columns]
    if missing:
        raise V1P0FeatureError(f"market panel missing columns: {missing}")

    frame = panel.copy()
    frame["as_of_date"] = pd.to_datetime(frame["as_of_date"])
    if "market_intraday_return" not in frame.columns:
        frame["market_intraday_return"] = (frame["market_close"] / frame["market_open"]) - 1.0

    base_columns = ["canonical_ticker", "as_of_date", *source_columns]
    if config.get("production_feature_set"):
        base_columns.extend(["market_high", "market_low", "benchmark_close"])
    base = (
        frame[base_columns]
        .drop_duplicates(["canonical_ticker", "as_of_date"])
        .sort_values(["canonical_ticker", "as_of_date"])
        .reset_index(drop=True)
    )
    feature_columns: list[str] = []
    grouped = base.groupby("canonical_ticker", sort=False)
    for column in source_columns:
        for lag in config["lag_periods"]:
            name = f"{column}_lag_{int(lag)}"
            base[name] = grouped[column].shift(int(lag))
            feature_columns.append(name)
        shifted = grouped[column].shift(1)
        for window in config["rolling_windows"]:
            window = int(window)
            mean_name = f"{column}_rolling_{window}_mean_lag_1"
            std_name = f"{column}_rolling_{window}_std_lag_1"
            base[mean_name] = shifted.groupby(base["canonical_ticker"], sort=False).rolling(
                window=window,
                min_periods=int(config["rolling_min_periods"]),
            ).mean().reset_index(level=0, drop=True)
            base[std_name] = shifted.groupby(base["canonical_ticker"], sort=False).rolling(
                window=window,
                min_periods=int(config["rolling_min_periods"]),
            ).std(ddof=0).reset_index(level=0, drop=True)
            feature_columns.extend([mean_name, std_name])

    production = config.get("production_feature_set") or {}
    if production:
        min_periods = production.get("min_periods_by_family", {})
        base["_daily_return"] = grouped["market_close"].pct_change()
        shifted_close = grouped["market_close"].shift(1)
        shifted_volume = grouped["market_volume"].shift(1)
        shifted_daily_return = grouped["_daily_return"].shift(1)
        shifted_range = ((base["market_high"] - base["market_low"]) / base["market_close"]).groupby(base["canonical_ticker"], sort=False).shift(1)

        return_columns: dict[int, str] = {}
        for window in production.get("return_windows", []):
            window = int(window)
            name = f"market_return_{window}d_lag_1"
            base[name] = (shifted_close / grouped["market_close"].shift(window + 1)) - 1.0
            return_columns[window] = name
            feature_columns.append(name)

        for window in production.get("volatility_windows", []):
            window = int(window)
            name = f"market_realized_volatility_{window}d_lag_1"
            base[name] = shifted_daily_return.groupby(base["canonical_ticker"], sort=False).rolling(
                window=window,
                min_periods=int(min_periods.get("volatility", 2)),
            ).std(ddof=0).reset_index(level=0, drop=True)
            feature_columns.append(name)

        for window in production.get("volume_ratio_windows", []):
            window = int(window)
            rolling_volume = shifted_volume.groupby(base["canonical_ticker"], sort=False).rolling(
                window=window,
                min_periods=int(min_periods.get("volume_ratio", 2)),
            ).mean().reset_index(level=0, drop=True)
            name = f"market_volume_ratio_{window}d_lag_1"
            base[name] = shifted_volume / rolling_volume
            feature_columns.append(name)

        for window in production.get("high_low_range_windows", []):
            window = int(window)
            name = f"market_high_low_range_{window}d_mean_lag_1"
            base[name] = shifted_range.groupby(base["canonical_ticker"], sort=False).rolling(
                window=window,
                min_periods=int(min_periods.get("high_low_range", 2)),
            ).mean().reset_index(level=0, drop=True)
            feature_columns.append(name)

        for window in production.get("drawdown_windows", []):
            window = int(window)
            rolling_max = shifted_close.groupby(base["canonical_ticker"], sort=False).rolling(
                window=window,
                min_periods=int(min_periods.get("drawdown", 2)),
            ).max().reset_index(level=0, drop=True)
            name = f"market_drawdown_{window}d_lag_1"
            base[name] = (shifted_close / rolling_max) - 1.0
            feature_columns.append(name)

        benchmark = (
            base[["as_of_date", "benchmark_close"]]
            .drop_duplicates("as_of_date")
            .sort_values("as_of_date")
            .reset_index(drop=True)
        )
        shifted_benchmark_close = benchmark["benchmark_close"].shift(1)
        for window in production.get("market_relative_return_windows", []):
            window = int(window)
            benchmark_name = f"_benchmark_return_{window}d_lag_1"
            benchmark[benchmark_name] = (shifted_benchmark_close / benchmark["benchmark_close"].shift(window + 1)) - 1.0
            base = base.merge(benchmark[["as_of_date", benchmark_name]], on="as_of_date", how="left", validate="many_to_one")
            return_name = return_columns.get(window)
            if return_name is None:
                return_name = f"market_return_{window}d_lag_1"
                base[return_name] = (shifted_close / grouped["market_close"].shift(window + 1)) - 1.0
                feature_columns.append(return_name)
            name = f"market_relative_return_{window}d_lag_1"
            base[name] = base[return_name] - base[benchmark_name]
            feature_columns.append(name)

    metadata_columns = [
        "dataset_version",
        "clean_window_id",
        "label_window_start",
        "label_window_end",
        "no_news_flag",
        "empty_event_state_flag",
        "provider_empty_feed_flag",
        "provider_truncation_risk_flag",
        "aligned_news_count",
    ]
    metadata_columns = [column for column in metadata_columns if column in frame.columns]
    output = frame[[*row_key, *metadata_columns]].merge(
        base[["canonical_ticker", "as_of_date", *feature_columns]],
        on=["canonical_ticker", "as_of_date"],
        how="left",
        validate="many_to_one",
    )
    output["as_of_date"] = output["as_of_date"].dt.strftime("%Y-%m-%d")
    output["feature_family_id"] = str(config["feature_family_id"])
    output["feature_policy"] = str(config["lookahead_policy"])
    if production:
        output["feature_schema_version"] = str(production["feature_schema_version"])
    return output


def validate_feature_label_split_compatibility(features: pd.DataFrame, labels: pd.DataFrame, splits: pd.DataFrame, row_key: list[str]) -> dict[str, int]:
    for name, frame in {"features": features, "labels": labels, "splits": splits}.items():
        missing = [column for column in row_key if column not in frame.columns]
        if missing:
            raise V1P0FeatureError(f"{name} missing row-key columns: {missing}")
        if frame.duplicated(row_key).any():
            raise V1P0FeatureError(f"{name} contains duplicate row keys")
    joined = features[row_key].merge(labels[row_key], on=row_key, how="inner").merge(splits[row_key], on=row_key, how="inner")
    if len(joined) != len(features):
        raise V1P0FeatureError("features failed to align one-to-one with labels and splits")
    return {"feature_rows": len(features), "label_rows": len(labels), "split_rows": len(splits), "joined_rows": len(joined)}
