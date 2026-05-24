"""Stage 6 secondary ranking diagnostics."""

from __future__ import annotations

from collections.abc import Mapping
from math import ceil
from typing import Any

import numpy as np
import pandas as pd


TARGET_COLUMN = "forward_excess_return"


class RankingDiagnosticError(ValueError):
    """Raised when ranking diagnostics cannot be computed under the contract."""


def compute_ranking_diagnostics(aligned_predictions: pd.DataFrame, config: Mapping[str, Any]) -> pd.DataFrame:
    """Compute mandatory secondary cross-sectional ranking diagnostics."""

    ranking_config = config["ranking_diagnostics"]
    minimum_cross_section = int(ranking_config["minimum_cross_section"])
    top_bottom_fraction = float(ranking_config["top_bottom_fraction"])
    date_records: list[dict[str, Any]] = []
    group_columns = ["split_role", "fold_id", "horizon_id", "model_id", "model_family", "branch"]
    for keys, group in aligned_predictions.groupby(group_columns, sort=True):
        key_values = dict(zip(group_columns, keys))
        for as_of_date, date_group in group.groupby("as_of_date", sort=True):
            if len(date_group) < minimum_cross_section:
                continue
            date_records.append(
                {
                    **{name: str(value) for name, value in key_values.items()},
                    "as_of_date": str(as_of_date),
                    **_cross_sectional_values(date_group, top_bottom_fraction=top_bottom_fraction),
                }
            )
    if not date_records:
        raise RankingDiagnosticError("no cross-sections satisfied the ranking minimum")
    date_frame = pd.DataFrame.from_records(date_records)

    records: list[dict[str, Any]] = []
    for aggregation_level, group_columns in [
        ("fold", ["split_role", "fold_id", "horizon_id", "model_id", "model_family", "branch"]),
        ("aggregate", ["split_role", "horizon_id", "model_id", "model_family", "branch"]),
    ]:
        for keys, group in date_frame.groupby(group_columns, sort=True):
            key_values = dict(zip(group_columns, keys if isinstance(keys, tuple) else (keys,)))
            if aggregation_level == "aggregate":
                key_values["fold_id"] = "ALL"
            records.append(
                {
                    "aggregation_level": aggregation_level,
                    "split_role": str(key_values["split_role"]),
                    "fold_id": str(key_values["fold_id"]),
                    "horizon_id": str(key_values["horizon_id"]),
                    "model_id": str(key_values["model_id"]),
                    "model_family": str(key_values["model_family"]),
                    "branch": str(key_values["branch"]),
                    "cross_section_count": int(len(group)),
                    "spearman_rank_ic": _safe_mean(group["spearman_rank_ic"]),
                    "kendall_rank_correlation": _safe_mean(group["kendall_rank_correlation"]),
                    "directional_hit_rate": _safe_mean(group["directional_hit_rate"]),
                    "top_minus_bottom_spread": _safe_mean(group["top_minus_bottom_spread"]),
                    "ranking_is_primary": False,
                }
            )
    return pd.DataFrame.from_records(records).sort_values(
        ["aggregation_level", "split_role", "fold_id", "horizon_id", "model_id"]
    ).reset_index(drop=True)


def _cross_sectional_values(group: pd.DataFrame, *, top_bottom_fraction: float) -> dict[str, float | int]:
    predictions = group["prediction"].astype("float64")
    actuals = group[TARGET_COLUMN].astype("float64")
    prediction_rank = predictions.rank(method="average")
    actual_rank = actuals.rank(method="average")
    if prediction_rank.nunique(dropna=True) <= 1 or actual_rank.nunique(dropna=True) <= 1:
        spearman = float("nan")
    else:
        spearman = float(prediction_rank.corr(actual_rank))
    kendall = _kendall_tau_b(predictions.to_numpy(), actuals.to_numpy())
    directional_hit_rate = float(np.mean(np.sign(predictions.to_numpy()) == np.sign(actuals.to_numpy())))
    ordered = group.assign(_prediction=predictions).sort_values("_prediction")
    tail_count = max(1, int(ceil(len(ordered) * top_bottom_fraction)))
    bottom = ordered.head(tail_count)[TARGET_COLUMN].astype("float64").mean()
    top = ordered.tail(tail_count)[TARGET_COLUMN].astype("float64").mean()
    return {
        "row_count": int(len(group)),
        "spearman_rank_ic": spearman,
        "kendall_rank_correlation": kendall,
        "directional_hit_rate": directional_hit_rate,
        "top_minus_bottom_spread": float(top - bottom),
    }


def _kendall_tau_b(x_values: np.ndarray, y_values: np.ndarray) -> float:
    concordant = 0
    discordant = 0
    ties_x = 0
    ties_y = 0
    n = len(x_values)
    for i in range(n - 1):
        dx = x_values[i] - x_values[i + 1 :]
        dy = y_values[i] - y_values[i + 1 :]
        sign_x = np.sign(dx)
        sign_y = np.sign(dy)
        ties_x += int(np.sum(sign_x == 0))
        ties_y += int(np.sum(sign_y == 0))
        products = sign_x * sign_y
        concordant += int(np.sum(products > 0))
        discordant += int(np.sum(products < 0))
    denominator = np.sqrt((concordant + discordant + ties_x) * (concordant + discordant + ties_y))
    if denominator == 0:
        return float("nan")
    return float((concordant - discordant) / denominator)


def _safe_mean(series: pd.Series) -> float:
    values = series.astype("float64").replace([np.inf, -np.inf], np.nan).dropna()
    if values.empty:
        return float("nan")
    return float(values.mean())
