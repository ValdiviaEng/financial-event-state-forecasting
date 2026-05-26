from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


class V1P0EvaluationError(ValueError):
    """Raised when v1p0 evaluation inputs are malformed."""


def compute_diagnostics(predictions: pd.DataFrame) -> pd.DataFrame:
    if "target" not in predictions.columns or "prediction" not in predictions.columns:
        raise V1P0EvaluationError("predictions must include target and prediction")
    frame = predictions.copy()
    frame["error"] = frame["prediction"].astype("float64") - frame["target"].astype("float64")
    frame["squared_error"] = frame["error"] ** 2
    frame["absolute_error"] = frame["error"].abs()
    records: list[dict[str, Any]] = []
    for keys, group in frame.groupby(["split_role", "fold_id", "horizon_id", "model_id"], sort=True):
        split_role, fold_id, horizon_id, model_id = keys
        target = group["target"].astype("float64").to_numpy()
        denominator = float(np.sum(target**2))
        sse = float(group["squared_error"].sum())
        records.append(
            {
                "split_role": split_role,
                "fold_id": fold_id,
                "horizon_id": horizon_id,
                "model_id": model_id,
                "row_count": int(len(group)),
                "rmse": float(np.sqrt(group["squared_error"].mean())),
                "mae": float(group["absolute_error"].mean()),
                "r2_oos": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator),
            }
        )
    return pd.DataFrame.from_records(records)


def attach_strata(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["news_stratum"] = np.where(output.get("no_news_flag", False).astype(bool), "no_news", "news_rich")
    output["truncation_stratum"] = np.where(output.get("provider_truncation_risk_flag", False).astype(bool), "truncation_risk", "no_truncation_flag")
    count = output.get("article_count", pd.Series([0] * len(output), index=output.index)).astype("int64")
    output["article_count_stratum"] = pd.cut(count, bins=[-1, 0, 2, np.inf], labels=["articles_0", "articles_1_2", "articles_3_plus"])
    return output


def compute_stratified_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    frame = attach_strata(predictions)
    frame["absolute_error"] = (frame["prediction"].astype("float64") - frame["target"].astype("float64")).abs()
    records = []
    for stratum_column in ["news_stratum", "truncation_stratum", "article_count_stratum"]:
        for keys, group in frame.groupby(["model_id", "horizon_id", stratum_column], sort=True, observed=True):
            model_id, horizon_id, stratum_value = keys
            records.append(
                {
                    "model_id": model_id,
                    "horizon_id": horizon_id,
                    "stratum_type": stratum_column,
                    "stratum_value": str(stratum_value),
                    "row_count": int(len(group)),
                    "mae": float(group["absolute_error"].mean()),
                    "provider_completeness_claim": False,
                }
            )
    return pd.DataFrame.from_records(records)


def compute_date_clustered_ci(predictions: pd.DataFrame, confidence_level: float = 0.95) -> pd.DataFrame:
    frame = predictions.copy()
    frame["absolute_error"] = (frame["prediction"].astype("float64") - frame["target"].astype("float64")).abs()
    z_value = 1.96 if confidence_level == 0.95 else 1.96
    records = []
    for keys, group in frame.groupby(["model_id", "horizon_id"], sort=True):
        model_id, horizon_id = keys
        by_date = group.groupby("as_of_date", sort=True)["absolute_error"].mean()
        mean = float(by_date.mean())
        if len(by_date) < 2:
            lower = upper = mean
        else:
            half_width = float(z_value * by_date.std(ddof=1) / np.sqrt(len(by_date)))
            lower = mean - half_width
            upper = mean + half_width
        records.append({"model_id": model_id, "horizon_id": horizon_id, "metric": "mae", "cluster_count": int(len(by_date)), "mean": mean, "ci_lower": lower, "ci_upper": upper, "method": "date_clustered_normal_ci"})
    return pd.DataFrame.from_records(records)
