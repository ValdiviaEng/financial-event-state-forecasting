"""Multi-horizon label construction from adjusted price histories."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from src.data.data_contracts import validate_records


DEFAULT_LABEL_HORIZONS = (1, 5, 20, 60)


def build_multi_horizon_labels(
    adjusted_price_rows: Sequence[dict[str, Any]],
    *,
    benchmark_rows: Sequence[dict[str, Any]] | None = None,
    horizons: Sequence[int] = DEFAULT_LABEL_HORIZONS,
    downside_threshold: float = 0.0,
) -> pd.DataFrame:
    """Build multi-horizon regression and classification labels.

    Labels are built from adjusted price histories and are aligned so that row
    date `t` uses future information from `t + horizon`, never past information.
    """

    validate_records("adjusted_prices_daily", adjusted_price_rows)
    price_df = _prepare_price_frame(adjusted_price_rows)
    benchmark_forward = _prepare_benchmark_forward_returns(benchmark_rows, horizons=horizons)

    label_frames = []
    for ticker, ticker_df in price_df.groupby("ticker", sort=True):
        labels = ticker_df[["ticker", "date"]].copy()
        close = ticker_df["close"].astype(float)

        for horizon in horizons:
            future_close = close.shift(-horizon)
            forward_return = future_close / close - 1.0
            labels[f"y_ret_{horizon}"] = forward_return
            if benchmark_forward is not None:
                labels = labels.merge(
                    benchmark_forward[["date", f"benchmark_forward_return_{horizon}"]],
                    how="left",
                    on="date",
                )
                labels[f"y_excess_ret_{horizon}"] = (
                    labels[f"y_ret_{horizon}"] - labels[f"benchmark_forward_return_{horizon}"]
                )
                labels = labels.drop(columns=[f"benchmark_forward_return_{horizon}"])
            else:
                labels[f"y_excess_ret_{horizon}"] = labels[f"y_ret_{horizon}"]

            labels[f"y_dir_{horizon}"] = labels[f"y_ret_{horizon}"].apply(
                lambda value: None if pd.isna(value) else bool(value > 0.0)
            )
            labels[f"y_downside_{horizon}"] = labels[f"y_ret_{horizon}"].apply(
                lambda value: None if pd.isna(value) else bool(value < downside_threshold)
            )

        label_frames.append(labels)

    return pd.concat(label_frames, ignore_index=True)


def summarize_label_availability(labels: pd.DataFrame, *, horizons: Sequence[int]) -> dict[str, Any]:
    """Return a small summary of label sparsity and availability."""

    summary: dict[str, Any] = {
        "row_count": int(len(labels)),
        "ticker_count": int(labels["ticker"].nunique()) if "ticker" in labels else 0,
        "horizons": list(horizons),
        "available_counts": {},
    }
    for horizon in horizons:
        for prefix in ("y_ret", "y_excess_ret", "y_dir", "y_downside"):
            column = f"{prefix}_{horizon}"
            if column in labels.columns:
                summary["available_counts"][column] = int(labels[column].notna().sum())
    return summary


def _prepare_price_frame(rows: Sequence[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows).copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.date
    frame = frame.sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)
    return frame


def _prepare_benchmark_forward_returns(
    benchmark_rows: Sequence[dict[str, Any]] | None,
    *,
    horizons: Sequence[int],
) -> pd.DataFrame | None:
    if benchmark_rows is None:
        return None

    benchmark_df = pd.DataFrame(benchmark_rows).copy()
    if "date" not in benchmark_df.columns or "close" not in benchmark_df.columns:
        raise ValueError("Benchmark rows must include at least 'date' and 'close'.")
    benchmark_df["date"] = pd.to_datetime(benchmark_df["date"]).dt.date
    benchmark_df = benchmark_df.sort_values("date", kind="stable").reset_index(drop=True)

    close = benchmark_df["close"].astype(float)
    prepared = benchmark_df[["date"]].copy()
    for horizon in horizons:
        future_close = close.shift(-horizon)
        prepared[f"benchmark_forward_return_{horizon}"] = future_close / close - 1.0
    return prepared
