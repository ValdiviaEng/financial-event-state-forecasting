"""As-of-safe market feature construction for Stage 3."""

from __future__ import annotations

import pandas as pd

from event_state_forecasting.data.contracts import ROW_KEY_FIELDS


MARKET_FEATURE_COLUMNS = (
    "market_open",
    "market_high",
    "market_low",
    "market_close",
    "market_volume",
    "market_intraday_return",
    "market_intraday_range_ratio",
)


class MarketFeatureError(ValueError):
    """Raised when market feature inputs violate the Stage 3 contract."""


def build_market_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Build row-aligned market-only features using as-of row values only."""

    required = [*ROW_KEY_FIELDS, "dataset_version", "feature_availability_timestamp", "prediction_timestamp", "market_open", "market_high", "market_low", "market_close", "market_volume"]
    missing = [column for column in required if column not in panel.columns]
    if missing:
        raise MarketFeatureError(f"panel missing market feature fields: {missing}")

    output = panel[[*ROW_KEY_FIELDS, "dataset_version", "feature_availability_timestamp", "prediction_timestamp", "market_open", "market_high", "market_low", "market_close", "market_volume"]].copy()
    output["market_intraday_return"] = (output["market_close"] / output["market_open"]) - 1.0
    output["market_intraday_range_ratio"] = (output["market_high"] - output["market_low"]) / output["market_close"]
    output["market_feature_policy"] = "same_row_as_of_close_only"
    return output
