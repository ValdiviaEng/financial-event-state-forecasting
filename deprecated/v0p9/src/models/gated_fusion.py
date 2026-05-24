"""Simple Stage 5 gated-fusion regressor."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sklearn.linear_model import Ridge


class SimpleGatedFusionRegressor:
    """Combines market and event-state branches with a train-fold combiner.

    The estimator is intentionally small and deterministic. It fits separate
    ridge branches for market and event-state features, then fits a ridge
    combiner on branch predictions plus approved event-state gate features.
    """

    def __init__(self, *, n_market_features: int, gate_feature_indices: Sequence[int], alpha: float = 1.0):
        self.n_market_features = int(n_market_features)
        self.gate_feature_indices = tuple(int(value) for value in gate_feature_indices)
        self.alpha = float(alpha)

    def fit(self, X: np.ndarray, y: np.ndarray) -> "SimpleGatedFusionRegressor":
        self._validate_shape(X)
        market_X = X[:, : self.n_market_features]
        event_X = X[:, self.n_market_features :]
        self.market_model_ = Ridge(alpha=self.alpha).fit(market_X, y)
        self.event_model_ = Ridge(alpha=self.alpha).fit(event_X, y)
        self.combiner_model_ = Ridge(alpha=self.alpha).fit(self._combiner_matrix(X), y)
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._validate_shape(X)
        return self.combiner_model_.predict(self._combiner_matrix(X))

    def _validate_shape(self, X: np.ndarray) -> None:
        if X.ndim != 2:
            raise ValueError("fusion input must be a 2D array")
        if self.n_market_features <= 0:
            raise ValueError("n_market_features must be positive")
        if X.shape[1] <= self.n_market_features:
            raise ValueError("fusion input must include event-state features")
        event_feature_count = X.shape[1] - self.n_market_features
        bad_indices = [idx for idx in self.gate_feature_indices if idx < 0 or idx >= event_feature_count]
        if bad_indices:
            raise ValueError(f"gate feature indices out of range: {bad_indices}")

    def _combiner_matrix(self, X: np.ndarray) -> np.ndarray:
        market_X = X[:, : self.n_market_features]
        event_X = X[:, self.n_market_features :]
        market_pred = self.market_model_.predict(market_X).reshape(-1, 1)
        event_pred = self.event_model_.predict(event_X).reshape(-1, 1)
        gate_X = event_X[:, self.gate_feature_indices] if self.gate_feature_indices else np.empty((X.shape[0], 0))
        interactions = event_pred * gate_X if gate_X.size else np.empty((X.shape[0], 0))
        return np.hstack([market_pred, event_pred, gate_X, interactions])


def make_gated_fusion_estimator(
    *,
    n_market_features: int,
    event_feature_columns: Sequence[str],
    gate_feature_columns: Sequence[str],
    alpha: float,
) -> SimpleGatedFusionRegressor:
    gate_indices = [event_feature_columns.index(column) for column in gate_feature_columns]
    return SimpleGatedFusionRegressor(
        n_market_features=n_market_features,
        gate_feature_indices=gate_indices,
        alpha=alpha,
    )
