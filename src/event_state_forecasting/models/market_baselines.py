"""Stage 5 sklearn market-baseline factories."""

from __future__ import annotations

from typing import Any, Mapping

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.neural_network import MLPRegressor


class ConstantZeroRegressor:
    """Predicts zero forward excess return for every row."""

    def fit(self, X: np.ndarray, y: np.ndarray) -> "ConstantZeroRegressor":
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.zeros(X.shape[0], dtype="float64")


class TrainMeanRegressor:
    """Predicts the training-fold target mean for every row."""

    def fit(self, X: np.ndarray, y: np.ndarray) -> "TrainMeanRegressor":
        self.n_features_in_ = X.shape[1]
        self.mean_ = float(np.mean(y))
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        return np.full(X.shape[0], self.mean_, dtype="float64")


def make_market_estimator(family: str, params: Mapping[str, Any], *, seed: int):
    if family == "constant_zero":
        return ConstantZeroRegressor()
    if family == "constant_train_mean":
        return TrainMeanRegressor()
    if family == "ridge":
        return Ridge(alpha=float(params.get("alpha", 1.0)))
    if family == "elastic_net":
        return ElasticNet(
            alpha=float(params.get("alpha", 0.0001)),
            l1_ratio=float(params.get("l1_ratio", 0.15)),
            max_iter=int(params.get("max_iter", 5000)),
            random_state=seed,
        )
    if family == "random_forest":
        return RandomForestRegressor(
            n_estimators=int(params.get("n_estimators", 32)),
            max_depth=int(params.get("max_depth", 6)),
            min_samples_leaf=int(params.get("min_samples_leaf", 20)),
            n_jobs=int(params.get("n_jobs", 1)),
            random_state=seed,
        )
    if family == "hist_gradient_boosting":
        return HistGradientBoostingRegressor(
            max_iter=int(params.get("max_iter", 60)),
            learning_rate=float(params.get("learning_rate", 0.05)),
            max_leaf_nodes=int(params.get("max_leaf_nodes", 15)),
            l2_regularization=float(params.get("l2_regularization", 0.01)),
            random_state=seed,
        )
    if family == "mlp":
        hidden = tuple(int(value) for value in params.get("hidden_layer_sizes", [16]))
        return MLPRegressor(
            hidden_layer_sizes=hidden,
            alpha=float(params.get("alpha", 0.0001)),
            learning_rate_init=float(params.get("learning_rate_init", 0.001)),
            max_iter=int(params.get("max_iter", 80)),
            random_state=seed,
            early_stopping=False,
        )
    raise ValueError(f"unsupported market estimator family: {family}")
