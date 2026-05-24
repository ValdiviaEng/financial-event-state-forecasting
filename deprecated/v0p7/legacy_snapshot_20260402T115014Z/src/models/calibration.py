"""Optional probability calibration helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class ReliabilityBin:
    """Reliability curve bin summary."""

    lower: float
    upper: float
    mean_probability: float
    empirical_frequency: float
    count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "lower": self.lower,
            "upper": self.upper,
            "mean_probability": self.mean_probability,
            "empirical_frequency": self.empirical_frequency,
            "count": self.count,
        }


def fit_binary_calibrator(y_true: Any, y_prob: Any, *, method: str = "isotonic") -> Any:
    """Fit a post-hoc binary calibrator from validation data only."""

    sklearn_isotonic = __import__("sklearn.isotonic", fromlist=["IsotonicRegression"])
    sklearn_linear = __import__("sklearn.linear_model", fromlist=["LogisticRegression"])

    true = np.asarray(y_true, dtype=float).reshape(-1)
    prob = np.asarray(y_prob, dtype=float).reshape(-1)
    mask = ~(np.isnan(true) | np.isnan(prob))
    true = true[mask]
    prob = prob[mask]

    if method == "isotonic":
        model = sklearn_isotonic.IsotonicRegression(out_of_bounds="clip")
        model.fit(prob, true)
        return {"method": method, "model": model}
    if method == "logistic":
        model = sklearn_linear.LogisticRegression(max_iter=1000)
        model.fit(prob.reshape(-1, 1), true.astype(int))
        return {"method": method, "model": model}
    raise ValueError(f"Unsupported calibration method '{method}'.")


def apply_binary_calibrator(calibrator: Any, y_prob: Any) -> np.ndarray:
    """Apply a fitted binary calibrator to probability scores."""

    probs = np.asarray(y_prob, dtype=float).reshape(-1)
    method = calibrator["method"]
    model = calibrator["model"]
    if method == "isotonic":
        return np.asarray(model.predict(probs), dtype=float)
    if method == "logistic":
        return np.asarray(model.predict_proba(probs.reshape(-1, 1))[:, 1], dtype=float)
    raise ValueError(f"Unsupported calibrator method '{method}'.")


def reliability_curve(y_true: Any, y_prob: Any, *, n_bins: int = 10) -> list[dict[str, Any]]:
    """Build reliability-curve bins from probabilities and binary outcomes."""

    true = np.asarray(y_true, dtype=float).reshape(-1)
    prob = np.asarray(y_prob, dtype=float).reshape(-1)
    mask = ~(np.isnan(true) | np.isnan(prob))
    true = true[mask]
    prob = prob[mask]

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    rows: list[dict[str, Any]] = []
    for lower, upper in zip(bins[:-1], bins[1:], strict=False):
        if upper == 1.0:
            bucket = (prob >= lower) & (prob <= upper)
        else:
            bucket = (prob >= lower) & (prob < upper)
        count = int(bucket.sum())
        if count == 0:
            rows.append(ReliabilityBin(lower, upper, np.nan, np.nan, 0).as_dict())
            continue
        rows.append(
            ReliabilityBin(
                lower=float(lower),
                upper=float(upper),
                mean_probability=float(prob[bucket].mean()),
                empirical_frequency=float(true[bucket].mean()),
                count=count,
            ).as_dict()
        )
    return rows


def expected_calibration_error(y_true: Any, y_prob: Any, *, n_bins: int = 10) -> float:
    """Compute expected calibration error from reliability bins."""

    bins = reliability_curve(y_true, y_prob, n_bins=n_bins)
    total = sum(row["count"] for row in bins)
    if total == 0:
        return np.nan
    ece = 0.0
    for row in bins:
        if row["count"] == 0:
            continue
        gap = abs(row["mean_probability"] - row["empirical_frequency"])
        ece += (row["count"] / total) * gap
    return float(ece)
