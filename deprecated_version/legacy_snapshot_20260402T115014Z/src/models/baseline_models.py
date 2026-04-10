"""Market-only baseline model factories and lightweight wrappers."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Any

import joblib
import numpy as np


SUPPORTED_BASELINE_MODELS = ("ridge", "elastic_net", "market_mlp")


class BaselineModelError(RuntimeError):
    """Raised when a baseline model cannot be constructed or loaded."""


@dataclass
class SklearnRegressorWrapper:
    """Uniform interface for sklearn-based multi-output regressors."""

    model_name: str
    estimator: Any

    def fit(self, features: np.ndarray, targets: np.ndarray) -> "SklearnRegressorWrapper":
        self.estimator.fit(features, targets)
        return self

    def predict(self, features: np.ndarray) -> np.ndarray:
        predictions = self.estimator.predict(features)
        predictions = np.asarray(predictions, dtype=float)
        if predictions.ndim == 1:
            predictions = predictions.reshape(-1, 1)
        return predictions

    def save(self, file_path: str | Path) -> Path:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model_name": self.model_name, "estimator": self.estimator}, path)
        return path

    @classmethod
    def load(cls, file_path: str | Path) -> "SklearnRegressorWrapper":
        payload = joblib.load(file_path)
        return cls(model_name=payload["model_name"], estimator=payload["estimator"])


def list_supported_baseline_models() -> tuple[str, ...]:
    """Return the supported baseline model names."""

    return SUPPORTED_BASELINE_MODELS


def build_baseline_model(
    model_name: str,
    *,
    input_dim: int | None = None,
    output_dim: int | None = None,
    alpha: float = 1.0,
    l1_ratio: float = 0.5,
    hidden_dims: tuple[int, ...] = (64, 32),
    dropout: float = 0.0,
) -> Any:
    """Build a baseline model by name.

    Returns either a `SklearnRegressorWrapper` or a torch `nn.Module` for the
    market-only MLP path.
    """

    normalized_name = model_name.strip().lower()
    if normalized_name == "ridge":
        return _build_ridge(alpha=alpha)
    if normalized_name == "elastic_net":
        return _build_elastic_net(alpha=alpha, l1_ratio=l1_ratio)
    if normalized_name == "market_mlp":
        if input_dim is None or output_dim is None:
            raise BaselineModelError("market_mlp requires both input_dim and output_dim.")
        return build_market_mlp(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
            dropout=dropout,
        )
    known = ", ".join(SUPPORTED_BASELINE_MODELS)
    raise BaselineModelError(f"Unsupported baseline model '{model_name}'. Known models: {known}")


def build_market_mlp(
    *,
    input_dim: int,
    output_dim: int,
    hidden_dims: tuple[int, ...] = (64, 32),
    dropout: float = 0.0,
) -> Any:
    """Build a simple market-only PyTorch MLP.

    This import path is lazy so the repository can remain usable without Torch
    installed until neural training is actually needed.
    """

    try:
        torch = importlib.import_module("torch")
    except ModuleNotFoundError as exc:
        raise BaselineModelError(
            "market_mlp requires PyTorch, which is not installed in the current environment."
        ) from exc

    nn = torch.nn
    layers: list[Any] = []
    previous_dim = input_dim
    for hidden_dim in hidden_dims:
        layers.append(nn.Linear(previous_dim, hidden_dim))
        layers.append(nn.ReLU())
        if dropout > 0:
            layers.append(nn.Dropout(dropout))
        previous_dim = hidden_dim
    layers.append(nn.Linear(previous_dim, output_dim))
    return nn.Sequential(*layers)


def is_torch_available() -> bool:
    """Return whether PyTorch is importable in the current environment."""

    try:
        importlib.import_module("torch")
    except ModuleNotFoundError:
        return False
    return True


def load_baseline_checkpoint(file_path: str | Path) -> Any:
    """Load a saved sklearn baseline checkpoint."""

    return SklearnRegressorWrapper.load(file_path)


def _build_ridge(*, alpha: float) -> SklearnRegressorWrapper:
    sklearn_impute = importlib.import_module("sklearn.impute")
    sklearn_pipeline = importlib.import_module("sklearn.pipeline")
    sklearn_preprocessing = importlib.import_module("sklearn.preprocessing")
    sklearn_linear_model = importlib.import_module("sklearn.linear_model")

    estimator = sklearn_pipeline.Pipeline(
        steps=[
            ("imputer", sklearn_impute.SimpleImputer(strategy="median")),
            ("scaler", sklearn_preprocessing.StandardScaler()),
            ("model", sklearn_linear_model.Ridge(alpha=alpha, random_state=42)),
        ]
    )
    return SklearnRegressorWrapper(model_name="ridge", estimator=estimator)


def _build_elastic_net(*, alpha: float, l1_ratio: float) -> SklearnRegressorWrapper:
    sklearn_impute = importlib.import_module("sklearn.impute")
    sklearn_pipeline = importlib.import_module("sklearn.pipeline")
    sklearn_preprocessing = importlib.import_module("sklearn.preprocessing")
    sklearn_linear_model = importlib.import_module("sklearn.linear_model")
    sklearn_multioutput = importlib.import_module("sklearn.multioutput")

    base_estimator = sklearn_linear_model.ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
    estimator = sklearn_pipeline.Pipeline(
        steps=[
            ("imputer", sklearn_impute.SimpleImputer(strategy="median")),
            ("scaler", sklearn_preprocessing.StandardScaler()),
            ("model", sklearn_multioutput.MultiOutputRegressor(base_estimator)),
        ]
    )
    return SklearnRegressorWrapper(model_name="elastic_net", estimator=estimator)
