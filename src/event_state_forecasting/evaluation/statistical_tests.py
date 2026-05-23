"""Stage 6 paired loss-delta diagnostics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd


PAIR_KEY_COLUMNS = ["row_key", "fold_id", "split_role", "horizon_id"]


class PairedComparisonError(ValueError):
    """Raised when paired saved predictions cannot be compared."""


def compute_paired_loss_deltas(
    aligned_predictions: pd.DataFrame,
    selected_market_hurdles: Mapping[str, str],
    config: Mapping[str, Any],
) -> pd.DataFrame:
    """Compare every model against the frozen market hurdle on identical rows."""

    records: list[dict[str, Any]] = []
    model_metadata = aligned_predictions.loc[:, ["model_id", "model_family", "branch"]].drop_duplicates()
    for horizon_id, baseline_model_id in selected_market_hurdles.items():
        horizon = aligned_predictions[aligned_predictions["horizon_id"] == horizon_id]
        baseline = horizon[horizon["model_id"] == baseline_model_id].loc[
            :, [*PAIR_KEY_COLUMNS, "squared_error", "absolute_error"]
        ].rename(columns={"squared_error": "baseline_squared_error", "absolute_error": "baseline_absolute_error"})
        if baseline.empty:
            raise PairedComparisonError(f"missing baseline predictions for {horizon_id} {baseline_model_id}")
        for model_id in sorted(horizon["model_id"].unique()):
            model = horizon[horizon["model_id"] == model_id]
            metadata = model_metadata[model_metadata["model_id"] == model_id].iloc[0]
            paired = model.merge(baseline, on=PAIR_KEY_COLUMNS, how="inner", validate="one_to_one")
            if len(paired) != len(model):
                raise PairedComparisonError(f"unpaired rows for {horizon_id} {model_id}")
            paired["squared_loss_diff"] = paired["baseline_squared_error"] - paired["squared_error"]
            paired["absolute_loss_diff"] = paired["baseline_absolute_error"] - paired["absolute_error"]
            for aggregation_level, group_columns in [
                ("fold", ["split_role", "fold_id"]),
                ("aggregate", ["split_role"]),
            ]:
                for keys, group in paired.groupby(group_columns, sort=True):
                    key_values = dict(zip(group_columns, keys if isinstance(keys, tuple) else (keys,)))
                    if aggregation_level == "aggregate":
                        key_values["fold_id"] = "ALL"
                    records.append(
                        {
                            "aggregation_level": aggregation_level,
                            "split_role": str(key_values["split_role"]),
                            "fold_id": str(key_values["fold_id"]),
                            "horizon_id": str(horizon_id),
                            "baseline_model_id": str(baseline_model_id),
                            "model_id": str(model_id),
                            "model_family": str(metadata["model_family"]),
                            "branch": str(metadata["branch"]),
                            "paired_policy": str(config["paired_comparison_policy"]["policy_id"]),
                            **_delta_stats(group),
                        }
                    )
    return pd.DataFrame.from_records(records).sort_values(
        ["aggregation_level", "split_role", "fold_id", "horizon_id", "model_id"]
    ).reset_index(drop=True)


def _delta_stats(group: pd.DataFrame) -> dict[str, float | int | bool]:
    squared = group["squared_loss_diff"].astype("float64").to_numpy()
    absolute = group["absolute_loss_diff"].astype("float64").to_numpy()
    return {
        "row_count": int(len(group)),
        "mean_squared_loss_diff": float(np.mean(squared)),
        "squared_loss_diff_standard_error": _standard_error(squared),
        "squared_loss_positive_row_rate": float(np.mean(squared > 0.0)),
        "mean_absolute_loss_diff": float(np.mean(absolute)),
        "absolute_loss_diff_standard_error": _standard_error(absolute),
        "absolute_loss_positive_row_rate": float(np.mean(absolute > 0.0)),
        "p_value_reported": False,
    }


def _standard_error(values: np.ndarray) -> float:
    if len(values) <= 1:
        return 0.0
    return float(np.std(values, ddof=1) / np.sqrt(len(values)))
