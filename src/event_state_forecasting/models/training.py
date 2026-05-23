"""Stage 5 fold-local preprocessing and training helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


TRAIN_SPLIT_ROLE = "train"
PREPROCESSING_POLICIES = {"none", "median_impute", "median_impute_scale"}


class TrainingContractError(ValueError):
    """Raised when Stage 5 training isolation is violated."""


@dataclass(slots=True)
class FoldPreprocessor:
    feature_columns: tuple[str, ...]
    policy: str
    fit_row_count: int
    imputer: SimpleImputer | None = None
    scaler: StandardScaler | None = None

    def transform(self, frame: pd.DataFrame) -> np.ndarray:
        if self.policy == "none":
            return np.zeros((len(frame), 0), dtype="float64")
        X = frame.loc[:, self.feature_columns].astype("float64").to_numpy()
        if self.imputer is not None:
            X = self.imputer.transform(X)
        if self.scaler is not None:
            X = self.scaler.transform(X)
        return X

    def parameter_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "policy": self.policy,
            "feature_columns": list(self.feature_columns),
            "fit_row_count": self.fit_row_count,
            "imputer_statistics": None,
            "scaler_mean": None,
            "scaler_scale": None,
        }
        if self.imputer is not None:
            payload["imputer_statistics"] = [float(value) for value in self.imputer.statistics_]
        if self.scaler is not None:
            payload["scaler_mean"] = [float(value) for value in self.scaler.mean_]
            payload["scaler_scale"] = [float(value) for value in self.scaler.scale_]
        payload["parameter_digest"] = stable_payload_digest(payload)
        return payload


def validate_training_rows(frame: pd.DataFrame) -> None:
    if frame.empty:
        raise TrainingContractError("training frame is empty")
    if set(frame["split_role"].unique()) != {TRAIN_SPLIT_ROLE}:
        raise TrainingContractError("preprocessing and model fit may use train rows only")
    if "preprocessing_fit_allowed" in frame and not bool(frame["preprocessing_fit_allowed"].all()):
        raise TrainingContractError("all training rows must permit preprocessing fit")


def fit_fold_preprocessor(
    train_frame: pd.DataFrame,
    *,
    feature_columns: Sequence[str],
    policy: str,
) -> FoldPreprocessor:
    if policy not in PREPROCESSING_POLICIES:
        raise TrainingContractError(f"unsupported preprocessing policy: {policy}")
    validate_training_rows(train_frame)
    columns = tuple(feature_columns)
    if policy == "none":
        return FoldPreprocessor(feature_columns=(), policy=policy, fit_row_count=len(train_frame))
    if not columns:
        raise TrainingContractError("learned preprocessing requires feature columns")

    X = train_frame.loc[:, columns].astype("float64").to_numpy()
    imputer = SimpleImputer(strategy="median").fit(X)
    X = imputer.transform(X)
    scaler = StandardScaler().fit(X) if policy == "median_impute_scale" else None
    return FoldPreprocessor(
        feature_columns=columns,
        policy=policy,
        fit_row_count=len(train_frame),
        imputer=imputer,
        scaler=scaler,
    )


def stable_payload_digest(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
