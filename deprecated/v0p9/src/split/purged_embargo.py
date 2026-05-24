"""Stage 4 purged-plus-embargoed walk-forward split construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from event_state_forecasting.data.contracts import APPROVED_HORIZONS, BENCHMARK_FAMILY_ID, HORIZON_TRADING_STEPS, ROW_KEY_FIELDS
from event_state_forecasting.split.lockbox import define_lockbox_boundary


SPLIT_SCHEMA_VERSION = "stage4_splits_v1"
SPLIT_PROTOCOL = "purged_embargoed_walk_forward_with_final_untouched_lockbox"
APPROVED_SPLIT_ROLES = {"train", "validation", "purged", "embargoed", "lockbox", "excluded"}


class SplitBuildError(ValueError):
    """Raised when Stage 4 splits cannot be built safely."""


@dataclass(frozen=True, slots=True)
class SplitArtifacts:
    assignments: pd.DataFrame
    fold_definitions: pd.DataFrame
    lockbox_record: dict[str, Any]
    manifest: dict[str, Any]


def build_purged_embargoed_folds(
    labels: pd.DataFrame,
    *,
    split_config: dict[str, Any],
    artifact_version: str,
    input_artifact_version: str,
    row_universe_digest: str,
) -> SplitArtifacts:
    validate_split_config(split_config)
    labels = normalize_labels(labels)
    unique_dates = sorted(labels["as_of_date"].drop_duplicates().tolist())
    lockbox_config = split_config["lockbox"]
    explicit_start_date = None
    if lockbox_config.get("policy") == "explicit_post_stage6_lockbox_holdout_start_date":
        explicit_start_date = str(lockbox_config.get("start_date") or "")
    lockbox = define_lockbox_boundary(
        unique_dates,
        fraction=float(lockbox_config["fraction"]),
        expected_start_date=lockbox_config.get("expected_start_date"),
        explicit_start_date=explicit_start_date,
    )
    development_dates = [value for value in unique_dates if value < lockbox.start_date]
    fold_config = split_config["fold_schedule"]
    initial_train_dates = int(fold_config["initial_training_date_count"])
    validation_dates = int(fold_config["validation_date_count"])
    purge_embargo_dates = int(split_config["purge_embargo"]["trading_date_count"])

    folds = build_fold_definitions(
        development_dates,
        initial_train_dates=initial_train_dates,
        validation_dates=validation_dates,
        purge_embargo_dates=purge_embargo_dates,
        lockbox_start_date=lockbox.start_date,
        lockbox_end_date=lockbox.end_date,
    )
    if not folds:
        raise SplitBuildError("split config creates no complete development folds")

    assignment_frames = [assign_fold_roles(labels, fold, lockbox.start_date) for fold in folds]
    assignments = pd.concat(assignment_frames, ignore_index=True)
    fold_definitions = pd.DataFrame(folds)
    lockbox_row_count = int((labels["as_of_date"] >= lockbox.start_date).sum())
    lockbox_record = lockbox.to_record(row_count=lockbox_row_count)
    lockbox_record.update(
        {
            "artifact_type": "stage4_lockbox_record",
            "benchmark_family_id": BENCHMARK_FAMILY_ID,
            "input_artifact_version": input_artifact_version,
            "row_universe_digest": row_universe_digest,
            "benchmark_claim": False,
        }
    )

    for fold in folds:
        fold_rows = assignments[assignments["fold_id"] == fold["fold_id"]]
        fold["row_counts_by_role"] = dict(sorted(fold_rows["split_role"].value_counts().to_dict().items()))
        fold["row_counts_by_role_and_horizon"] = role_horizon_counts(fold_rows)

    fold_definitions = pd.DataFrame(folds)
    manifest = build_split_manifest(
        artifact_version=artifact_version,
        input_artifact_version=input_artifact_version,
        row_universe_digest=row_universe_digest,
        split_config=split_config,
        labels=labels,
        assignments=assignments,
        folds=folds,
        lockbox_record=lockbox_record,
    )
    return SplitArtifacts(
        assignments=assignments,
        fold_definitions=fold_definitions,
        lockbox_record=lockbox_record,
        manifest=manifest,
    )


def validate_split_config(config: dict[str, Any]) -> None:
    if config.get("artifact_schema_version") != SPLIT_SCHEMA_VERSION:
        raise SplitBuildError("split config schema version mismatch")
    if config.get("split_protocol") != SPLIT_PROTOCOL:
        raise SplitBuildError("split protocol mismatch")
    if tuple(config.get("horizons", ())) != APPROVED_HORIZONS:
        raise SplitBuildError("split config horizons do not match approved horizons")

    fold_config = config.get("fold_schedule", {})
    if fold_config.get("training_window") != "expanding":
        raise SplitBuildError("Stage 4 currently supports expanding training windows only")
    if fold_config.get("cadence") != "monthly":
        raise SplitBuildError("Stage 4 approved cadence is monthly")
    if int(fold_config.get("initial_training_date_count", 0)) <= 0:
        raise SplitBuildError("initial training date count must be positive")
    if int(fold_config.get("validation_date_count", 0)) <= 0:
        raise SplitBuildError("validation date count must be positive")

    expected_gap = max(HORIZON_TRADING_STEPS.values())
    purge_config = config.get("purge_embargo", {})
    if purge_config.get("policy") != "maximum_approved_label_horizon":
        raise SplitBuildError("purge/embargo policy must use maximum approved label horizon")
    if int(purge_config.get("trading_date_count", 0)) != expected_gap:
        raise SplitBuildError(f"purge/embargo trading-date count must be {expected_gap}")

    lockbox_config = config.get("lockbox", {})
    lockbox_policy = lockbox_config.get("policy", "final_fraction_of_stage3_as_of_dates")
    if lockbox_policy not in {"final_fraction_of_stage3_as_of_dates", "explicit_post_stage6_lockbox_holdout_start_date"}:
        raise SplitBuildError("unsupported lockbox policy")
    if lockbox_policy == "explicit_post_stage6_lockbox_holdout_start_date" and not lockbox_config.get("start_date"):
        raise SplitBuildError("explicit lockbox policy requires start_date")


def normalize_labels(labels: pd.DataFrame) -> pd.DataFrame:
    required = set(ROW_KEY_FIELDS) | {"dataset_version", "label_window_start", "label_window_end", "label_available_flag"}
    missing = sorted(required - set(labels.columns))
    if missing:
        raise SplitBuildError(f"labels are missing required split fields: {missing}")
    if labels.empty:
        raise SplitBuildError("labels must not be empty")
    frame = labels.copy()
    for column in ["as_of_date", "label_window_start", "label_window_end"]:
        frame[column] = frame[column].astype(str)
    if set(frame["benchmark_family_id"].unique()) != {BENCHMARK_FAMILY_ID}:
        raise SplitBuildError("labels benchmark family drift detected")
    if tuple(sorted(frame["horizon_id"].unique(), key=lambda value: APPROVED_HORIZONS.index(value))) != APPROVED_HORIZONS:
        raise SplitBuildError("labels horizon set does not match approved horizons")
    if not frame["label_available_flag"].all():
        raise SplitBuildError("all rows must have labels before Stage 4 split construction")
    return frame.sort_values(list(ROW_KEY_FIELDS)).reset_index(drop=True)


def build_fold_definitions(
    development_dates: list[str],
    *,
    initial_train_dates: int,
    validation_dates: int,
    purge_embargo_dates: int,
    lockbox_start_date: str,
    lockbox_end_date: str,
) -> list[dict[str, Any]]:
    start_index = initial_train_dates + purge_embargo_dates
    folds: list[dict[str, Any]] = []
    fold_number = 1
    while start_index + validation_dates <= len(development_dates):
        validation_start_index = start_index
        validation_end_index = start_index + validation_dates - 1
        embargo_start_index = validation_start_index - purge_embargo_dates
        train_end_index = embargo_start_index - 1
        if train_end_index < 0:
            raise SplitBuildError("fold config leaves no training dates before purge/embargo")
        folds.append(
            {
                "fold_id": f"fold_{fold_number:03d}",
                "fold_number": fold_number,
                "train_start_date": development_dates[0],
                "train_end_date": development_dates[train_end_index],
                "purge_embargo_start_date": development_dates[embargo_start_index],
                "purge_embargo_end_date": development_dates[validation_start_index - 1],
                "validation_start_date": development_dates[validation_start_index],
                "validation_end_date": development_dates[validation_end_index],
                "validation_date_count": validation_dates,
                "purge_embargo_date_count": purge_embargo_dates,
                "lockbox_start_date": lockbox_start_date,
                "lockbox_end_date": lockbox_end_date,
                "partial_window_policy": "drop_incomplete_final_development_window",
            }
        )
        fold_number += 1
        start_index += validation_dates
    return folds


def assign_fold_roles(labels: pd.DataFrame, fold: dict[str, Any], lockbox_start_date: str) -> pd.DataFrame:
    frame = labels[list(ROW_KEY_FIELDS) + ["dataset_version", "label_window_start", "label_window_end"]].copy()
    as_of = frame["as_of_date"]
    validation_mask = as_of.between(fold["validation_start_date"], fold["validation_end_date"])
    lockbox_mask = as_of >= lockbox_start_date
    embargo_mask = as_of.between(fold["purge_embargo_start_date"], fold["purge_embargo_end_date"])
    purge_mask = (as_of < fold["validation_start_date"]) & (frame["label_window_end"] >= fold["validation_start_date"])
    train_mask = (as_of <= fold["train_end_date"]) & ~purge_mask & ~embargo_mask
    future_development_mask = (as_of > fold["validation_end_date"]) & (as_of < lockbox_start_date)

    frame.insert(0, "fold_id", fold["fold_id"])
    frame["split_role"] = "excluded"
    frame.loc[train_mask, "split_role"] = "train"
    frame.loc[embargo_mask, "split_role"] = "embargoed"
    frame.loc[purge_mask, "split_role"] = "purged"
    frame.loc[validation_mask, "split_role"] = "validation"
    frame.loc[future_development_mask, "split_role"] = "excluded"
    frame.loc[lockbox_mask, "split_role"] = "lockbox"

    frame["lockbox_flag"] = lockbox_mask
    frame["purge_flag"] = purge_mask
    frame["embargo_flag"] = embargo_mask
    frame["preprocessing_fit_allowed"] = frame["split_role"] == "train"
    frame["split_exclusion_reason"] = ""
    frame.loc[frame["split_role"] == "purged", "split_exclusion_reason"] = "label_window_overlaps_validation_window"
    frame.loc[(frame["split_role"] == "purged") & embargo_mask, "split_exclusion_reason"] = (
        "label_window_overlaps_validation_window_and_embargo_window"
    )
    frame.loc[frame["split_role"] == "embargoed", "split_exclusion_reason"] = "embargo_window_before_validation"
    frame.loc[frame["split_role"] == "lockbox", "split_exclusion_reason"] = "final_untouched_lockbox"
    frame.loc[future_development_mask, "split_exclusion_reason"] = "future_development_period_for_fold"
    return frame


def role_horizon_counts(frame: pd.DataFrame) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    grouped = frame.groupby(["split_role", "horizon_id"]).size()
    for (role, horizon), count in grouped.items():
        counts.setdefault(str(role), {})[str(horizon)] = int(count)
    return counts


def build_split_manifest(
    *,
    artifact_version: str,
    input_artifact_version: str,
    row_universe_digest: str,
    split_config: dict[str, Any],
    labels: pd.DataFrame,
    assignments: pd.DataFrame,
    folds: list[dict[str, Any]],
    lockbox_record: dict[str, Any],
) -> dict[str, Any]:
    role_counts = dict(sorted(assignments["split_role"].value_counts().to_dict().items()))
    development_dates = sorted(value for value in labels["as_of_date"].drop_duplicates().tolist() if value < lockbox_record["start_date"])
    assigned_validation_dates = sorted(assignments.loc[assignments["split_role"] == "validation", "as_of_date"].drop_duplicates().tolist())
    leftover_dates = sorted(set(development_dates) - set(assigned_validation_dates) - {value for fold in folds for value in dates_between(development_dates, fold["train_start_date"], fold["train_end_date"])} - {value for fold in folds for value in dates_between(development_dates, fold["purge_embargo_start_date"], fold["purge_embargo_end_date"])})
    return {
        "artifact_type": "stage4_split_manifest",
        "artifact_schema_version": SPLIT_SCHEMA_VERSION,
        "benchmark_claim": False,
        "identity": {
            "artifact_version": artifact_version,
            "input_stage3_artifact_version": input_artifact_version,
            "benchmark_family_id": BENCHMARK_FAMILY_ID,
            "row_universe_digest": row_universe_digest,
        },
        "split_protocol": {
            "name": SPLIT_PROTOCOL,
            "training_window": split_config["fold_schedule"]["training_window"],
            "cadence": split_config["fold_schedule"]["cadence"],
            "validation_date_count": int(split_config["fold_schedule"]["validation_date_count"]),
            "initial_training_date_count": int(split_config["fold_schedule"]["initial_training_date_count"]),
            "purge_embargo_policy": split_config["purge_embargo"]["policy"],
            "purge_embargo_trading_date_count": int(split_config["purge_embargo"]["trading_date_count"]),
            "random_shuffle_allowed": False,
        },
        "row_universe": {
            "row_key_fields": list(ROW_KEY_FIELDS),
            "input_row_count": int(len(labels)),
            "assignment_row_count": int(len(assignments)),
            "fold_count": len(folds),
            "approved_horizons": list(APPROVED_HORIZONS),
        },
        "clean_window": {
            "as_of_start_date": labels["as_of_date"].min(),
            "as_of_end_date": labels["as_of_date"].max(),
            "as_of_date_count": int(labels["as_of_date"].nunique()),
            "label_window_end_max": labels["label_window_end"].max(),
        },
        "lockbox": lockbox_record,
        "folds": folds,
        "assignment_role_counts": {key: int(value) for key, value in role_counts.items()},
        "excluded_development_dates_not_scored": leftover_dates,
        "limitations": [
            "Stage 4 creates split, leakage, runner-gate, and artifact-packet evidence only.",
            "No model, prediction, metric, comparison summary, or benchmark result is created.",
            "Alpha Vantage provider-level article completeness remains limitation-flagged from upstream artifacts.",
        ],
        "non_claims": [
            "not_models",
            "not_predictions",
            "not_metrics",
            "not_comparison_summary",
            "not_benchmark_result",
            "not_provider_level_article_completeness",
        ],
    }


def dates_between(dates: list[str], start: str, end: str) -> list[str]:
    return [value for value in dates if start <= value <= end]
