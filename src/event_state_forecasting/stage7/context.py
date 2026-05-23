"""Stage 7 context assembly from frozen Stage 3/4/5 artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

import pandas as pd


KEY_COLUMNS = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
CURRENT_STAGE6_LOCKBOX_START = "2025-09-30"
CURRENT_STAGE6_LOCKBOX_END = "2026-02-13"


class Stage7ContextError(ValueError):
    """Raised when Stage 7 context assembly would violate protocol."""


def load_stage7_context(
    *,
    feature_root: Path,
    split_root: Path,
    model_root: Path,
    model_config: Mapping[str, Any],
    stage7_config: Mapping[str, Any],
    split_roles: Sequence[str] = ("validation",),
    smoke_date_limit: int | None = None,
) -> pd.DataFrame:
    """Load row-level Stage 7 decision context for development replay.

    Stage 7 benchmark design uses development validation folds only. Current
    Stage 6 lockbox rows are rejected unless a future, explicit non-design
    diagnostic mode is added.
    """

    roles = tuple(str(role) for role in split_roles)
    allow_new_holdout = bool(stage7_config["protocol"].get("post_lockbox_holdout_evaluation_allowed"))
    if "lockbox" in roles and not allow_new_holdout:
        raise Stage7ContextError("lockbox rows require explicit Stage 7 post-lockbox holdout approval")

    market_columns = list(model_config["feature_sets"]["market_features"])
    event_columns = list(model_config["feature_sets"]["event_state_features"])
    prediction_model_ids = list(stage7_config["context"]["required_prediction_model_ids"])

    market = pd.read_parquet(feature_root / "market_features.parquet", columns=[*KEY_COLUMNS, "dataset_version", *market_columns])
    event = pd.read_parquet(feature_root / "event_state_features.parquet", columns=[*KEY_COLUMNS, *event_columns])
    labels = pd.read_parquet(
        feature_root / "labels.parquet",
        columns=[*KEY_COLUMNS, "forward_excess_return", "label_available_flag"],
    )
    assignments = pd.read_parquet(split_root / "split_assignments.parquet")
    predictions = pd.read_parquet(model_root / "saved_predictions.parquet")

    assignments = assignments[assignments["split_role"].isin(roles)].copy()
    if assignments.empty:
        raise Stage7ContextError(f"no split rows for roles: {roles}")
    if "lockbox" not in roles:
        assignments = drop_current_stage6_lockbox_rows(assignments)
        if assignments.empty:
            raise Stage7ContextError("no split rows remain after excluding the current Stage 6 lockbox")
    validate_no_current_lockbox_design_rows(assignments)

    features = market.merge(event, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    features = features.merge(labels, on=KEY_COLUMNS, how="inner", validate="one_to_one")
    panel = assignments.merge(features, on=[*KEY_COLUMNS, "dataset_version"], how="left", validate="many_to_one")
    if panel["forward_excess_return"].isna().any():
        raise Stage7ContextError("split assignments failed to align with Stage 3 labels")
    if not bool(panel["label_available_flag"].all()):
        raise Stage7ContextError("Stage 7 replay requires label-available rows")

    prediction_context = build_prediction_context(predictions, prediction_model_ids, roles=roles)
    panel = panel.merge(
        prediction_context,
        on=[*KEY_COLUMNS, "fold_id", "split_role", "dataset_version"],
        how="left",
        validate="one_to_one",
    )
    required_prediction_columns = [prediction_column(model_id) for model_id in prediction_model_ids]
    missing_predictions = panel[required_prediction_columns].isna().any(axis=1)
    if bool(missing_predictions.any()):
        raise Stage7ContextError("Stage 7 context has missing fold-safe Stage 5 predictions")

    news_column = str(stage7_config["row_filters"]["news_day_column"])
    panel["stage7_news_day_flag"] = panel[news_column].fillna(0).astype("float64") > 0.0
    panel["stage7_context_mode"] = stage7_config["context"]["mode"]
    panel["stage7_current_lockbox_excluded"] = True

    if smoke_date_limit is not None:
        panel = limit_dates_per_fold_horizon(panel, smoke_date_limit)
    return panel.sort_values(["fold_id", "horizon_id", "as_of_date", "canonical_ticker"]).reset_index(drop=True)


def build_prediction_context(predictions: pd.DataFrame, model_ids: Sequence[str], *, roles: Sequence[str]) -> pd.DataFrame:
    required = {"benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id", "fold_id", "split_role", "dataset_version", "model_id", "prediction"}
    missing = required - set(predictions.columns)
    if missing:
        raise Stage7ContextError(f"saved predictions missing columns: {sorted(missing)}")
    frame = predictions[predictions["split_role"].isin(roles) & predictions["model_id"].isin(model_ids)].copy()
    if frame.empty:
        raise Stage7ContextError("no saved predictions for Stage 7 context")
    pivot = frame.pivot_table(
        index=[*KEY_COLUMNS, "fold_id", "split_role", "dataset_version"],
        columns="model_id",
        values="prediction",
        aggfunc="first",
    ).reset_index()
    pivot.columns = [prediction_column(value) if value in model_ids else str(value) for value in pivot.columns]
    return pivot


def prediction_column(model_id: str) -> str:
    return f"stage5_prediction__{model_id}"


def validate_no_current_lockbox_design_rows(frame: pd.DataFrame) -> None:
    if "as_of_date" not in frame.columns:
        raise Stage7ContextError("frame missing as_of_date")
    in_lockbox = current_stage6_lockbox_mask(frame)
    if bool(in_lockbox.any()):
        raise Stage7ContextError("current Stage 6 lockbox rows cannot be used for Stage 7 design replay")


def drop_current_stage6_lockbox_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if "as_of_date" not in frame.columns:
        raise Stage7ContextError("frame missing as_of_date")
    return frame.loc[~current_stage6_lockbox_mask(frame)].copy()


def current_stage6_lockbox_mask(frame: pd.DataFrame) -> pd.Series:
    dates = pd.to_datetime(frame["as_of_date"]).dt.date.astype(str)
    return (dates >= CURRENT_STAGE6_LOCKBOX_START) & (dates <= CURRENT_STAGE6_LOCKBOX_END)


def limit_dates_per_fold_horizon(frame: pd.DataFrame, limit: int) -> pd.DataFrame:
    if limit <= 0:
        raise Stage7ContextError("smoke_date_limit must be positive")
    kept = []
    for _, group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        dates = sorted(group["as_of_date"].drop_duplicates().astype(str).tolist())[:limit]
        kept.append(group[group["as_of_date"].astype(str).isin(dates)])
    return pd.concat(kept, ignore_index=True) if kept else frame.iloc[0:0].copy()
