"""Statistical-comparison helpers for forecast evaluation."""

from __future__ import annotations

from math import erf, sqrt
from typing import Any

import numpy as np


def bootstrap_confidence_interval(
    values: Any,
    *,
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    random_state: int = 42,
    statistic: str = "mean",
) -> dict[str, float]:
    """Compute a percentile bootstrap confidence interval."""

    array = np.asarray(values, dtype=float).reshape(-1)
    array = array[~np.isnan(array)]
    if array.size == 0:
        return {"estimate": np.nan, "lower": np.nan, "upper": np.nan}

    rng = np.random.default_rng(random_state)
    samples = []
    for _ in range(n_bootstrap):
        bootstrap_sample = rng.choice(array, size=array.size, replace=True)
        samples.append(_statistic(bootstrap_sample, statistic=statistic))
    alpha = (1.0 - confidence) / 2.0
    return {
        "estimate": float(_statistic(array, statistic=statistic)),
        "lower": float(np.quantile(samples, alpha)),
        "upper": float(np.quantile(samples, 1.0 - alpha)),
    }


def paired_bootstrap_mean_difference(
    values_a: Any,
    values_b: Any,
    *,
    confidence: float = 0.95,
    n_bootstrap: int = 1000,
    random_state: int = 42,
) -> dict[str, float]:
    """Compute a paired bootstrap CI for the mean difference `a - b`."""

    a = np.asarray(values_a, dtype=float).reshape(-1)
    b = np.asarray(values_b, dtype=float).reshape(-1)
    if a.shape != b.shape:
        raise ValueError(f"Paired bootstrap inputs must have the same shape, got {a.shape} and {b.shape}.")
    mask = ~(np.isnan(a) | np.isnan(b))
    diff = a[mask] - b[mask]
    return bootstrap_confidence_interval(
        diff,
        confidence=confidence,
        n_bootstrap=n_bootstrap,
        random_state=random_state,
        statistic="mean",
    )


def diebold_mariano_test(loss_a: Any, loss_b: Any, *, horizon: int = 1) -> dict[str, float]:
    """Compute a simple Diebold-Mariano-style predictive accuracy comparison.

    Returns the loss differential `loss_a - loss_b`, so a positive mean suggests
    model B has lower loss than model A.
    """

    a = np.asarray(loss_a, dtype=float).reshape(-1)
    b = np.asarray(loss_b, dtype=float).reshape(-1)
    if a.shape != b.shape:
        raise ValueError(f"Diebold-Mariano inputs must have the same shape, got {a.shape} and {b.shape}.")
    mask = ~(np.isnan(a) | np.isnan(b))
    d = a[mask] - b[mask]
    if d.size < 2:
        return {"mean_loss_diff": np.nan, "statistic": np.nan, "p_value": np.nan}

    mean_d = float(np.mean(d))
    variance = _newey_west_variance(d, horizon=max(1, horizon))
    if variance <= 0:
        statistic = 0.0 if mean_d == 0 else float("inf")
        p_value = 1.0 if mean_d == 0 else 0.0
    else:
        statistic = float(mean_d / np.sqrt(variance / len(d)))
        p_value = float(2.0 * (1.0 - _normal_cdf(abs(statistic))))
    return {"mean_loss_diff": mean_d, "statistic": statistic, "p_value": p_value}


def compare_prediction_errors(
    y_true: Any,
    pred_a: Any,
    pred_b: Any,
    *,
    loss_name: str = "mse",
    horizon: int = 1,
) -> dict[str, float]:
    """Compare two prediction arrays through paired loss differentials."""

    true = np.asarray(y_true, dtype=float).reshape(-1)
    a = np.asarray(pred_a, dtype=float).reshape(-1)
    b = np.asarray(pred_b, dtype=float).reshape(-1)
    if not (true.shape == a.shape == b.shape):
        raise ValueError("Prediction comparison inputs must share the same shape.")
    loss_a = _loss_vector(true, a, loss_name=loss_name)
    loss_b = _loss_vector(true, b, loss_name=loss_name)
    dm = diebold_mariano_test(loss_a, loss_b, horizon=horizon)
    bootstrap = paired_bootstrap_mean_difference(loss_a, loss_b)
    return {
        "mean_loss_diff": dm["mean_loss_diff"],
        "dm_statistic": dm["statistic"],
        "dm_p_value": dm["p_value"],
        "bootstrap_lower": bootstrap["lower"],
        "bootstrap_upper": bootstrap["upper"],
    }


def _loss_vector(y_true: np.ndarray, y_pred: np.ndarray, *, loss_name: str) -> np.ndarray:
    if loss_name == "mse":
        return (y_pred - y_true) ** 2
    if loss_name == "mae":
        return np.abs(y_pred - y_true)
    raise ValueError(f"Unsupported loss_name '{loss_name}'.")


def _statistic(values: np.ndarray, *, statistic: str) -> float:
    if statistic == "mean":
        return float(np.mean(values))
    if statistic == "median":
        return float(np.median(values))
    raise ValueError(f"Unsupported statistic '{statistic}'.")


def _newey_west_variance(differential: np.ndarray, *, horizon: int) -> float:
    centered = differential - np.mean(differential)
    gamma0 = np.mean(centered * centered)
    variance = gamma0
    max_lag = min(horizon - 1, len(centered) - 1)
    for lag in range(1, max_lag + 1):
        cov = np.mean(centered[lag:] * centered[:-lag])
        weight = 1.0 - (lag / horizon)
        variance += 2.0 * weight * cov
    return float(variance)


def _normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + erf(value / sqrt(2.0)))
