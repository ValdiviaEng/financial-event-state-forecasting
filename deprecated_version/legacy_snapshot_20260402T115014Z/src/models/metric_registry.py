"""Metric helpers for regression, classification, ranking, and evaluation tables."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def regression_metrics(y_true: Any, y_pred: Any) -> dict[str, float]:
    """Compute core regression metrics with explicit NaN filtering."""

    true, pred = _paired_numeric_arrays(y_true, y_pred)
    if true.size == 0:
        return {"mae": np.nan, "rmse": np.nan, "r2": np.nan, "pearson": np.nan, "spearman": np.nan}

    mae = float(np.mean(np.abs(pred - true)))
    rmse = float(np.sqrt(np.mean((pred - true) ** 2)))
    r2 = _safe_r2(true, pred)
    pearson = _safe_correlation(true, pred, method="pearson")
    spearman = _safe_correlation(true, pred, method="spearman")
    return {"mae": mae, "rmse": rmse, "r2": r2, "pearson": pearson, "spearman": spearman}


def classification_metrics(y_true: Any, y_score: Any, *, threshold: float = 0.5) -> dict[str, float]:
    """Compute core binary classification metrics from probabilities or scores."""

    sklearn_metrics = __import__("sklearn.metrics", fromlist=["metrics"])
    true, score = _paired_numeric_arrays(y_true, y_score)
    if true.size == 0:
        return {"auc": np.nan, "pr_auc": np.nan, "brier": np.nan, "accuracy": np.nan}

    true_bool = true.astype(int)
    auc = float(sklearn_metrics.roc_auc_score(true_bool, score)) if len(np.unique(true_bool)) > 1 else np.nan
    pr_auc = (
        float(sklearn_metrics.average_precision_score(true_bool, score))
        if len(np.unique(true_bool)) > 1
        else np.nan
    )
    brier = float(sklearn_metrics.brier_score_loss(true_bool, score))
    predictions = (score >= threshold).astype(int)
    accuracy = float(sklearn_metrics.accuracy_score(true_bool, predictions))
    return {"auc": auc, "pr_auc": pr_auc, "brier": brier, "accuracy": accuracy}


def ranking_metrics(
    frame: pd.DataFrame,
    *,
    prediction_column: str,
    target_column: str,
    date_column: str = "date",
) -> dict[str, Any]:
    """Compute daily cross-sectional ranking metrics."""

    required = {prediction_column, target_column, date_column}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Ranking metric input is missing required columns: {', '.join(missing)}")

    daily_rows: list[dict[str, Any]] = []
    for current_date, date_frame in frame.groupby(date_column, sort=True):
        subset = date_frame[[prediction_column, target_column]].dropna()
        if len(subset) < 2:
            continue
        daily_ic = _spearman_correlation(
            np.asarray(subset[prediction_column], dtype=float),
            np.asarray(subset[target_column], dtype=float),
        )
        if pd.isna(daily_ic):
            continue
        daily_rows.append({"date": current_date, "daily_ic": float(daily_ic), "row_count": int(len(subset))})

    if not daily_rows:
        return {"daily_ic_mean": np.nan, "icir": np.nan, "daily_rows": []}

    daily_ic_values = np.asarray([row["daily_ic"] for row in daily_rows], dtype=float)
    mean_ic = float(np.mean(daily_ic_values))
    std_ic = float(np.std(daily_ic_values))
    icir = float(mean_ic / std_ic) if std_ic > 0 else np.nan
    return {"daily_ic_mean": mean_ic, "icir": icir, "daily_rows": daily_rows}


def evaluate_prediction_frame(
    predictions: pd.DataFrame,
    labels: pd.DataFrame,
    *,
    target_columns: list[str],
    id_columns: tuple[str, ...] = ("ticker", "date"),
) -> dict[str, pd.DataFrame]:
    """Evaluate stored predictions against a label frame.

    Returns machine-readable regression and ranking metric tables.
    """

    joined = predictions.merge(labels[list(id_columns) + target_columns], how="left", on=list(id_columns))
    regression_rows: list[dict[str, Any]] = []
    ranking_rows: list[dict[str, Any]] = []

    group_columns = [column for column in ("model_name", "split_id", "partition") if column in joined.columns]
    grouped = joined.groupby(group_columns, dropna=False, sort=True) if group_columns else [((), joined)]

    for group_key, group_frame in grouped:
        group_metadata = _group_metadata(group_columns, group_key)
        for target_column in target_columns:
            prediction_column = f"pred_{target_column}"
            if prediction_column not in group_frame.columns:
                continue
            metrics = regression_metrics(group_frame[target_column], group_frame[prediction_column])
            regression_rows.append({**group_metadata, "target": target_column, **metrics})

            ranking = ranking_metrics(
                group_frame,
                prediction_column=prediction_column,
                target_column=target_column,
                date_column="date",
            )
            ranking_rows.append(
                {
                    **group_metadata,
                    "target": target_column,
                    "daily_ic_mean": ranking["daily_ic_mean"],
                    "icir": ranking["icir"],
                    "evaluated_dates": len(ranking["daily_rows"]),
                }
            )

    return {
        "regression": pd.DataFrame(regression_rows),
        "ranking": pd.DataFrame(ranking_rows),
        "joined": joined,
    }


def _paired_numeric_arrays(y_true: Any, y_pred: Any) -> tuple[np.ndarray, np.ndarray]:
    true = np.asarray(y_true, dtype=float).reshape(-1)
    pred = np.asarray(y_pred, dtype=float).reshape(-1)
    if true.shape != pred.shape:
        raise ValueError(f"Metric inputs must have the same shape, got {true.shape} and {pred.shape}.")
    mask = ~(np.isnan(true) | np.isnan(pred))
    return true[mask], pred[mask]


def _safe_r2(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    sklearn_metrics = __import__("sklearn.metrics", fromlist=["metrics"])
    if y_true.size < 2:
        return np.nan
    return float(sklearn_metrics.r2_score(y_true, y_pred))


def _safe_correlation(y_true: np.ndarray, y_pred: np.ndarray, *, method: str) -> float:
    if y_true.size < 2:
        return np.nan
    if method == "pearson":
        std_true = float(np.std(y_true))
        std_pred = float(np.std(y_pred))
        if std_true == 0.0 or std_pred == 0.0:
            return np.nan
        return float(np.corrcoef(y_true, y_pred)[0, 1])
    if method == "spearman":
        return _spearman_correlation(y_true, y_pred)
    raise ValueError(f"Unsupported correlation method '{method}'.")


def _spearman_correlation(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    true_ranks = pd.Series(y_true).rank(method="average").to_numpy(dtype=float)
    pred_ranks = pd.Series(y_pred).rank(method="average").to_numpy(dtype=float)
    std_true = float(np.std(true_ranks))
    std_pred = float(np.std(pred_ranks))
    if std_true == 0.0 or std_pred == 0.0:
        return np.nan
    return float(np.corrcoef(true_ranks, pred_ranks)[0, 1])


def _group_metadata(group_columns: list[str], group_key: Any) -> dict[str, Any]:
    if not group_columns:
        return {}
    if len(group_columns) == 1:
        return {group_columns[0]: group_key}
    return {column: value for column, value in zip(group_columns, group_key, strict=False)}
