from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.features import build_market_lag_features  # noqa: E402
from event_state_forecasting.v1p0.registry import validate_feature_registry  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config, validate_version_manifest  # noqa: E402


def test_version_manifest_and_feature_registry_contracts() -> None:
    manifest = validate_version_manifest(load_json_config(PROJECT_ROOT / "configs" / "v1p0_version_manifest.yaml"))
    registry = validate_feature_registry(load_json_config(PROJECT_ROOT / "configs" / "feature_registry_v1p0.yaml"))

    assert manifest["benchmark_family_id"] == "phase1_top50_v1p0"
    assert manifest["manifest_digest"]
    assert registry["registry_digest"]
    dependency_ids = {item["model_id"] for item in registry["model_feature_dependencies"]}
    assert {
        "market_lag_linear_v1",
        "market_xgboost_v1_fixed",
        "market_xgboost_v2_nested_optuna_candidate",
        "market_xgboost_v2_frozen_final",
    }.issubset(dependency_ids)
    assert "event_market_horizon_fusion_v1" in dependency_ids


def test_market_lag_features_shift_before_rolling_without_lookahead() -> None:
    config = load_json_config(PROJECT_ROOT / "configs" / "market_features_v1p0.yaml")
    features = build_market_lag_features(_panel(), config)

    third_day = features[features["as_of_date"] == "2025-01-03"].iloc[0]
    assert third_day["market_close_lag_1"] == pytest.approx(102.0)
    assert third_day["market_close_lag_2"] == pytest.approx(100.0)
    assert third_day["market_close_rolling_3_mean_lag_1"] == pytest.approx((100.0 + 102.0) / 2.0)
    assert third_day["market_close_rolling_3_mean_lag_1"] != pytest.approx(104.0)
    assert third_day["market_return_1d_lag_1"] == pytest.approx(0.02)
    assert third_day["market_return_1d_lag_1"] != pytest.approx(104.0 / 102.0 - 1.0)


def _panel() -> pd.DataFrame:
    rows = []
    closes = [100.0, 102.0, 104.0, 108.0, 109.0]
    for index, close in enumerate(closes, start=1):
        rows.append(
            {
                "benchmark_family_id": "phase1_top50_v1p0",
                "dataset_version": "toy_dataset_v1",
                "canonical_ticker": "AAPL",
                "as_of_date": f"2025-01-0{index}",
                "horizon_id": "1d",
                "market_open": close - 1.0,
                "market_high": close + 2.0,
                "market_low": close - 2.0,
                "market_close": close,
                "market_volume": 1000 + index,
                "benchmark_close": close - 10.0,
            }
        )
    return pd.DataFrame(rows)
