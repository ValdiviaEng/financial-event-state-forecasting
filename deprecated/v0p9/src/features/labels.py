"""Forward excess-return label generation for Stage 3."""

from __future__ import annotations

from datetime import date
from statistics import mean
from typing import Any

import pandas as pd

from event_state_forecasting.data.contracts import APPROVED_HORIZONS, ROW_KEY_FIELDS, TARGET_FAMILY


LABEL_REFERENCE_POLICY = "leave_one_out_equal_weight_approved_universe"
LABEL_RETURN_TYPE = "simple"


class LabelBuildError(ValueError):
    """Raised when labels cannot be built without violating the contract."""


def build_forward_excess_return_labels(panel: pd.DataFrame, close_by_ticker: dict[str, dict[date, float]]) -> pd.DataFrame:
    """Build approved-horizon leave-one-out universe excess-return labels."""

    required = [*ROW_KEY_FIELDS, "dataset_version", "as_of_date", "label_window_start", "label_window_end"]
    missing = [column for column in required if column not in panel.columns]
    if missing:
        raise LabelBuildError(f"panel missing label fields: {missing}")

    horizons = tuple(panel["horizon_id"].drop_duplicates().tolist())
    if set(horizons) != set(APPROVED_HORIZONS):
        raise LabelBuildError("panel horizons do not match approved horizons")

    tickers = sorted(panel["canonical_ticker"].drop_duplicates().tolist())
    rows: list[dict[str, Any]] = []
    for row in panel.to_dict("records"):
        ticker = str(row["canonical_ticker"])
        start = date.fromisoformat(str(row["as_of_date"]))
        end = date.fromisoformat(str(row["label_window_end"]))
        ticker_return = simple_return(close_by_ticker[ticker][start], close_by_ticker[ticker][end])
        peer_returns = [simple_return(close_by_ticker[peer][start], close_by_ticker[peer][end]) for peer in tickers if peer != ticker]
        if not peer_returns:
            raise LabelBuildError("leave-one-out reference requires at least two tickers")
        reference_return = mean(peer_returns)
        rows.append(
            {
                **{field: row[field] for field in ROW_KEY_FIELDS},
                "dataset_version": row["dataset_version"],
                "target_family": TARGET_FAMILY,
                "return_type": LABEL_RETURN_TYPE,
                "reference_policy": LABEL_REFERENCE_POLICY,
                "label_window_start": row["label_window_start"],
                "label_window_end": row["label_window_end"],
                "ticker_forward_simple_return": ticker_return,
                "leave_one_out_universe_reference_return": reference_return,
                "forward_excess_return": ticker_return - reference_return,
                "label_available_flag": True,
            }
        )
    return pd.DataFrame.from_records(rows)


def simple_return(start_close: float, end_close: float) -> float:
    if start_close <= 0 or end_close <= 0:
        raise LabelBuildError("label close values must be positive")
    return (end_close / start_close) - 1.0
