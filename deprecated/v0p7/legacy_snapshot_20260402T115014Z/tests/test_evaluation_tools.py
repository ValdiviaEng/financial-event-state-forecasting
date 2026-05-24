from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.models.calibration import apply_binary_calibrator, expected_calibration_error, fit_binary_calibrator, reliability_curve
from src.models.metric_registry import classification_metrics, evaluate_prediction_frame, ranking_metrics, regression_metrics
from src.models.statistical_tests import bootstrap_confidence_interval, compare_prediction_errors, diebold_mariano_test


def test_regression_metrics_are_exact_for_identical_predictions() -> None:
    y_true = np.array([0.1, 0.2, -0.1, 0.0])
    metrics = regression_metrics(y_true, y_true)

    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["r2"] == 1.0
    assert metrics["pearson"] == 1.0
    assert metrics["spearman"] == 1.0


def test_classification_metrics_and_calibration_helpers_work() -> None:
    y_true = np.array([0, 0, 1, 1], dtype=float)
    y_prob = np.array([0.1, 0.2, 0.8, 0.9], dtype=float)
    metrics = classification_metrics(y_true, y_prob)
    assert metrics["auc"] == 1.0
    assert metrics["brier"] >= 0.0

    bins = reliability_curve(y_true, y_prob, n_bins=2)
    assert len(bins) == 2
    ece = expected_calibration_error(y_true, y_prob, n_bins=2)
    assert ece >= 0.0

    calibrator = fit_binary_calibrator(y_true, y_prob, method="isotonic")
    calibrated = apply_binary_calibrator(calibrator, y_prob)
    assert np.all((calibrated >= 0.0) & (calibrated <= 1.0))


def test_ranking_metrics_are_cross_sectional_by_date() -> None:
    frame = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
            "pred": [0.9, 0.1, 0.8, 0.2],
            "target": [1.0, 0.0, 0.9, 0.1],
        }
    )
    metrics = ranking_metrics(frame, prediction_column="pred", target_column="target")
    assert metrics["daily_ic_mean"] == pytest.approx(1.0)
    assert len(metrics["daily_rows"]) == 2


def test_statistical_tests_return_zero_difference_for_identical_errors() -> None:
    losses = np.array([0.1, 0.2, 0.3, 0.4])
    dm = diebold_mariano_test(losses, losses, horizon=1)
    assert dm["mean_loss_diff"] == 0.0
    assert dm["p_value"] == 1.0

    ci = bootstrap_confidence_interval(losses, n_bootstrap=200, random_state=7)
    assert ci["lower"] <= ci["estimate"] <= ci["upper"]

    comparison = compare_prediction_errors(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]))
    assert comparison["mean_loss_diff"] == 0.0


def test_evaluate_prediction_frame_builds_machine_readable_tables() -> None:
    labels = pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT", "AAPL", "MSFT"],
            "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
            "y_excess_ret_1": [0.1, 0.0, 0.2, 0.1],
        }
    )
    predictions = pd.DataFrame(
        {
            "ticker": ["AAPL", "MSFT", "AAPL", "MSFT"],
            "date": ["2024-01-01", "2024-01-01", "2024-01-02", "2024-01-02"],
            "pred_y_excess_ret_1": [0.11, -0.01, 0.19, 0.09],
            "model_name": ["ridge"] * 4,
            "split_id": [0] * 4,
            "partition": ["test"] * 4,
        }
    )
    evaluation = evaluate_prediction_frame(predictions, labels, target_columns=["y_excess_ret_1"])
    assert not evaluation["regression"].empty
    assert not evaluation["ranking"].empty
