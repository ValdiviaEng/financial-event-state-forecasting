"""Regression loss helpers for baseline and later neural models."""

from __future__ import annotations

from typing import Any

import numpy as np


class LossFunctionError(ValueError):
    """Raised when an unsupported loss configuration is requested."""


def compute_regression_loss(
    predictions: Any,
    targets: Any,
    *,
    loss_name: str = "mse",
    horizon_weights: list[float] | tuple[float, ...] | None = None,
) -> float:
    """Compute a weighted regression loss using NumPy arrays."""

    pred = np.asarray(predictions, dtype=float)
    true = np.asarray(targets, dtype=float)
    if pred.shape != true.shape:
        raise LossFunctionError(
            f"Predictions and targets must have the same shape, got {pred.shape} and {true.shape}."
        )

    if pred.ndim == 1:
        pred = pred.reshape(-1, 1)
        true = true.reshape(-1, 1)

    per_target = _per_target_loss(pred, true, loss_name=loss_name)
    weights = _normalize_horizon_weights(per_target.shape[0], horizon_weights)
    return float(np.dot(per_target, weights))


def compute_torch_regression_loss(
    predictions: Any,
    targets: Any,
    *,
    loss_name: str = "mse",
    horizon_weights: list[float] | tuple[float, ...] | None = None,
) -> Any:
    """Compute a weighted regression loss for torch tensors.

    This import path is lazy so the repository can remain usable when PyTorch is
    not installed.
    """

    import importlib

    try:
        torch = importlib.import_module("torch")
    except ModuleNotFoundError as exc:
        raise LossFunctionError("PyTorch is required for torch-based regression loss.") from exc

    pred = predictions
    true = targets
    if pred.shape != true.shape:
        raise LossFunctionError(
            f"Predictions and targets must have the same shape, got {pred.shape} and {true.shape}."
        )

    if pred.ndim == 1:
        pred = pred.unsqueeze(-1)
        true = true.unsqueeze(-1)

    if loss_name == "mse":
        per_example = (pred - true) ** 2
    elif loss_name == "mae":
        per_example = torch.abs(pred - true)
    elif loss_name == "huber":
        delta = 1.0
        error = torch.abs(pred - true)
        quadratic = torch.minimum(error, torch.tensor(delta, device=pred.device))
        linear = error - quadratic
        per_example = 0.5 * quadratic**2 + delta * linear
    else:
        raise LossFunctionError(f"Unsupported loss_name '{loss_name}'.")

    per_target = per_example.mean(dim=0)
    weights = torch.tensor(
        _normalize_horizon_weights(int(per_target.shape[0]), horizon_weights),
        dtype=per_target.dtype,
        device=per_target.device,
    )
    return torch.dot(per_target, weights)


def _per_target_loss(pred: np.ndarray, true: np.ndarray, *, loss_name: str) -> np.ndarray:
    if loss_name == "mse":
        return np.mean((pred - true) ** 2, axis=0)
    if loss_name == "mae":
        return np.mean(np.abs(pred - true), axis=0)
    if loss_name == "huber":
        error = np.abs(pred - true)
        quadratic = np.minimum(error, 1.0)
        linear = error - quadratic
        return np.mean(0.5 * quadratic**2 + linear, axis=0)
    raise LossFunctionError(f"Unsupported loss_name '{loss_name}'.")


def _normalize_horizon_weights(target_count: int, horizon_weights: list[float] | tuple[float, ...] | None) -> np.ndarray:
    if horizon_weights is None:
        return np.full(target_count, 1.0 / target_count)
    weights = np.asarray(horizon_weights, dtype=float)
    if len(weights) != target_count:
        raise LossFunctionError(
            f"Expected {target_count} horizon weights, got {len(weights)}."
        )
    if np.any(weights < 0):
        raise LossFunctionError("Horizon weights must be non-negative.")
    if float(weights.sum()) == 0.0:
        raise LossFunctionError("At least one horizon weight must be positive.")
    return weights / weights.sum()
