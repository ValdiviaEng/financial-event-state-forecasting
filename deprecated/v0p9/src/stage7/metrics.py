"""Stage 7 two-sided policy diagnostics."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


GROUP_COLUMNS = ["policy_id", "policy_family", "k", "epsilon", "horizon_id", "fold_id", "row_filter_track"]


def compute_stage7_metrics(selections: pd.DataFrame) -> pd.DataFrame:
    """Compute top-k, bottom-k, and spread diagnostics.

    The spread is a research separation diagnostic, not long-short PnL.
    """

    tracks = [
        ("all_rows_primary", selections),
        ("news_days_secondary", selections[selections["stage7_news_day_flag"]]),
    ]
    rows: list[dict[str, object]] = []
    for track_name, track_frame in tracks:
        if track_frame.empty:
            continue
        working = track_frame.copy()
        working["row_filter_track"] = track_name
        for keys, group in working.groupby(GROUP_COLUMNS, dropna=False, sort=True):
            rows.append(summarize_group(dict(zip(GROUP_COLUMNS, keys, strict=True)), group))
    metrics = pd.DataFrame(rows)
    if metrics.empty:
        return metrics
    aggregate = aggregate_metrics(metrics)
    return pd.concat([metrics, aggregate], ignore_index=True)


def summarize_group(keys: dict[str, object], group: pd.DataFrame) -> dict[str, object]:
    top = group[group["selection_side"] == "top"]
    bottom = group[group["selection_side"] == "bottom"]
    top_mean = safe_mean(top["forward_excess_return"])
    bottom_mean = safe_mean(bottom["forward_excess_return"])
    return {
        **keys,
        "aggregation_level": "fold",
        "selection_rows": int(len(group)),
        "top_selection_rows": int(len(top)),
        "bottom_selection_rows": int(len(bottom)),
        "top_k_mean_forward_excess_return": top_mean,
        "bottom_k_mean_forward_excess_return": bottom_mean,
        "top_minus_bottom_forward_excess_return_spread": none_if_nan(top_mean - bottom_mean),
        "top_positive_rate": safe_rate(top["forward_excess_return"] > 0),
        "bottom_negative_rate": safe_rate(bottom["forward_excess_return"] < 0),
        "exploration_row_rate": safe_rate(group["exploration_used"].astype(bool)),
        "trading_signal_approved": False,
        "spread_is_trading_pnl": False,
        "benchmark_claim": False,
    }


def aggregate_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = [column for column in GROUP_COLUMNS if column != "fold_id"]
    for keys, group in metrics.groupby(group_cols, dropna=False, sort=True):
        weights = group["selection_rows"].astype("float64")
        row: dict[str, object] = dict(zip(group_cols, keys, strict=True))
        row["fold_id"] = "aggregate"
        row["aggregation_level"] = "aggregate"
        row["selection_rows"] = int(group["selection_rows"].sum())
        row["top_selection_rows"] = int(group["top_selection_rows"].sum())
        row["bottom_selection_rows"] = int(group["bottom_selection_rows"].sum())
        for column in [
            "top_k_mean_forward_excess_return",
            "bottom_k_mean_forward_excess_return",
            "top_minus_bottom_forward_excess_return_spread",
            "top_positive_rate",
            "bottom_negative_rate",
            "exploration_row_rate",
        ]:
            row[column] = weighted_mean(group[column], weights)
        row["trading_signal_approved"] = False
        row["spread_is_trading_pnl"] = False
        row["benchmark_claim"] = False
        rows.append(row)
    return pd.DataFrame(rows)


def safe_mean(values: Iterable[float]) -> float:
    series = pd.Series(values, dtype="float64")
    return none_if_nan(float(series.mean()))


def safe_rate(mask: Iterable[bool]) -> float:
    series = pd.Series(mask, dtype="bool")
    if series.empty:
        return float("nan")
    return float(series.mean())


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    valid = values.notna() & weights.notna() & (weights > 0)
    if not bool(valid.any()):
        return float("nan")
    return none_if_nan(float(np.average(values[valid].astype("float64"), weights=weights[valid].astype("float64"))))


def none_if_nan(value: float) -> float:
    return float("nan") if pd.isna(value) else float(value)
