from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.evaluation.ranking import compute_ranking_diagnostics  # noqa: E402
from event_state_forecasting.evaluation.regression import (  # noqa: E402
    MetricContractError,
    align_predictions_with_labels,
    attach_loss_differences,
    compute_regression_metrics,
    select_market_hurdles,
)
from event_state_forecasting.evaluation.statistical_tests import compute_paired_loss_deltas  # noqa: E402


def test_regression_metrics_use_saved_predictions_and_frozen_labels() -> None:
    aligned = align_predictions_with_labels(_predictions(), _labels())

    metrics = compute_regression_metrics(aligned, _config())

    assert {"rmse", "mae", "r2_oos"}.issubset(metrics.columns)
    assert set(metrics["split_role"]) == {"validation", "lockbox"}
    assert "train" not in set(metrics["split_role"])


def test_metric_contract_rejects_in_sample_prediction_roles() -> None:
    predictions = _predictions()
    predictions.loc[0, "split_role"] = "train"

    with pytest.raises(MetricContractError, match="validation and lockbox"):
        align_predictions_with_labels(predictions, _labels())


def test_strict_market_hurdle_and_loss_delta_are_predeclared() -> None:
    aligned = align_predictions_with_labels(_predictions(), _labels())
    metrics = compute_regression_metrics(aligned, _config())
    selected = select_market_hurdles(metrics, _config())
    paired = compute_paired_loss_deltas(aligned, selected, _config())
    metrics = attach_loss_differences(metrics, paired)

    assert selected == {"1d": "market_ridge"}
    event_row = metrics[
        (metrics["aggregation_level"] == "aggregate")
        & (metrics["split_role"] == "validation")
        & (metrics["model_id"] == "event_state_gated_fusion")
    ].iloc[0]
    assert event_row["baseline_model_id"] == "market_ridge"
    assert event_row["mean_squared_loss_diff"] > 0


def test_ranking_diagnostics_are_secondary() -> None:
    aligned = align_predictions_with_labels(_predictions(cross_section=25), _labels(cross_section=25))

    ranking = compute_ranking_diagnostics(aligned, _config())

    assert "spearman_rank_ic" in ranking.columns
    assert set(ranking["ranking_is_primary"]) == {False}


def _predictions(cross_section: int = 2) -> pd.DataFrame:
    tickers = [f"T{i:02d}" for i in range(cross_section)]
    rows = []
    for split_role in ["validation", "lockbox"]:
        for model_id, prediction_shift, branch in [
            ("market_zero_excess_return", 0.0, "market_only"),
            ("market_ridge", 0.01, "market_only"),
            ("event_state_gated_fusion", 0.011, "event_state"),
        ]:
            for index, ticker in enumerate(tickers):
                rows.append(
                    {
                        "row_key": f"phase1_top50|{ticker}|2025-01-01|1d",
                        "benchmark_family_id": "phase1_top50",
                        "canonical_ticker": ticker,
                        "as_of_date": "2025-01-01",
                        "horizon_id": "1d",
                        "fold_id": "fold_001",
                        "split_role": split_role,
                        "model_id": model_id,
                        "model_family": "ridge" if model_id == "market_ridge" else model_id,
                        "branch": branch,
                        "dataset_version": "dataset_v1",
                        "feature_artifact_version": "features_v1",
                        "split_artifact_version": "splits_v1",
                        "stage5_artifact_version": "stage5_v1",
                        "prediction": prediction_shift + (index * 0.001),
                    }
                )
    return pd.DataFrame(rows)


def _labels(cross_section: int = 2) -> pd.DataFrame:
    tickers = [f"T{i:02d}" for i in range(cross_section)]
    return pd.DataFrame(
        {
            "benchmark_family_id": ["phase1_top50"] * cross_section,
            "canonical_ticker": tickers,
            "as_of_date": ["2025-01-01"] * cross_section,
            "horizon_id": ["1d"] * cross_section,
            "dataset_version": ["dataset_v1"] * cross_section,
            "forward_excess_return": [0.012 + (index * 0.001) for index in range(cross_section)],
            "label_available_flag": [True] * cross_section,
        }
    )


def _config() -> dict:
    return {
        "metric_policy": {
            "r2_baseline_model_id": "market_zero_excess_return",
            "market_hurdle_candidates": ["market_zero_excess_return", "market_ridge"],
            "event_state_model_id": "event_state_gated_fusion",
            "primary_regression_metrics": ["rmse", "mae"],
        },
        "ranking_diagnostics": {
            "minimum_cross_section": 20,
            "top_bottom_fraction": 0.2,
        },
        "paired_comparison_policy": {"policy_id": "loss_delta_summary_no_p_values"},
        "result_classification": {
            "primary_horizons": ["1d"],
            "reported_horizons": ["1d"],
            "robust_positive_min_primary_horizons": 1,
            "conditional_positive_min_primary_horizons": 1,
        },
    }
