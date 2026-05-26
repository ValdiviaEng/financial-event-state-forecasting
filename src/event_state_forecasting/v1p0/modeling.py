from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


class V1P0ModelError(ValueError):
    """Raised when v1p0 model inputs violate contract rules."""


@dataclass(slots=True)
class Preprocessor:
    columns: list[str]
    imputer: SimpleImputer
    scaler: StandardScaler | None
    fit_row_count: int

    def transform(self, frame: pd.DataFrame) -> np.ndarray:
        values = self.imputer.transform(frame[self.columns].astype("float64"))
        if self.scaler is not None:
            values = self.scaler.transform(values)
        return values


def fit_preprocessor(train: pd.DataFrame, feature_columns: list[str], policy: str) -> Preprocessor:
    if train.empty or set(train["split_role"].unique()) != {"train"}:
        raise V1P0ModelError("model preprocessing may fit on train rows only")
    imputer = SimpleImputer(strategy="median").fit(train[feature_columns].astype("float64"))
    transformed = imputer.transform(train[feature_columns].astype("float64"))
    scaler = StandardScaler().fit(transformed) if policy == "median_impute_scale" else None
    return Preprocessor(columns=feature_columns, imputer=imputer, scaler=scaler, fit_row_count=len(train))


def run_lag_linear_predictions(frame: pd.DataFrame, feature_columns: list[str], model_config: dict[str, Any]) -> pd.DataFrame:
    required = ["row_key", "fold_id", "split_role", "target", *feature_columns]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise V1P0ModelError(f"training frame missing columns: {missing}")

    records: list[pd.DataFrame] = []
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        score = group[group["split_role"].isin(["validation", "lockbox"])].copy()
        if score.empty:
            continue
        preprocessor = fit_preprocessor(train, feature_columns, model_config["preprocessing"])
        estimator = Ridge(alpha=float(model_config["params"].get("alpha", 1.0))).fit(preprocessor.transform(train), train["target"].astype("float64"))
        score["prediction"] = estimator.predict(preprocessor.transform(score))
        score["model_id"] = model_config["model_id"]
        score["model_family"] = model_config["family"]
        score["branch"] = model_config["branch"]
        score["v1p0_artifact_version"] = "v1p0_smoke_predictions_v1"
        records.append(score)
    if not records:
        raise V1P0ModelError("no validation or lockbox rows available for prediction")
    return pd.concat(records, ignore_index=True)


def run_fixed_xgboost_or_blocker(frame: pd.DataFrame, feature_columns: list[str], model_config: dict[str, Any]) -> pd.DataFrame | dict[str, Any]:
    try:
        from xgboost import XGBRegressor  # type: ignore
    except ModuleNotFoundError:
        return {
            "model_id": model_config["model_id"],
            "status": "blocked_missing_dependency",
            "missing_dependency": "xgboost",
            "message": "Install xgboost before executing market_xgboost_v1_fixed predictions.",
        }

    records: list[pd.DataFrame] = []
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        score = group[group["split_role"].isin(["validation", "lockbox"])].copy()
        if score.empty:
            continue
        preprocessor = fit_preprocessor(train, feature_columns, model_config["preprocessing"])
        estimator = XGBRegressor(**model_config["params"]).fit(preprocessor.transform(train), train["target"].astype("float64"))
        score["prediction"] = estimator.predict(preprocessor.transform(score))
        score["model_id"] = model_config["model_id"]
        score["model_family"] = model_config["family"]
        score["branch"] = model_config["branch"]
        score["v1p0_artifact_version"] = "v1p0_smoke_predictions_v1"
        records.append(score)
    return pd.concat(records, ignore_index=True) if records else pd.DataFrame()


def validate_prediction_schema(predictions: pd.DataFrame, required_columns: list[str]) -> dict[str, int]:
    missing = [column for column in required_columns if column not in predictions.columns]
    if missing:
        raise V1P0ModelError(f"predictions missing columns: {missing}")
    if predictions.duplicated(["row_key", "fold_id", "split_role", "model_id"]).any():
        raise V1P0ModelError("duplicate prediction rows detected")
    return {"prediction_rows": len(predictions), "model_count": int(predictions["model_id"].nunique())}
