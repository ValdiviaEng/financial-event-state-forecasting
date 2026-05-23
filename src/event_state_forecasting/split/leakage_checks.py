"""Stage 4 leakage checks for split artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pandas as pd

from event_state_forecasting.data.contracts import ROW_KEY_FIELDS
from event_state_forecasting.split.purged_embargo import APPROVED_SPLIT_ROLES


def validate_no_leakage(assignments: pd.DataFrame, fold_definitions: pd.DataFrame, lockbox_record: dict[str, Any]) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    required = set(ROW_KEY_FIELDS) | {
        "fold_id",
        "split_role",
        "as_of_date",
        "label_window_end",
        "lockbox_flag",
        "purge_flag",
        "embargo_flag",
        "preprocessing_fit_allowed",
    }
    missing = sorted(required - set(assignments.columns))
    if missing:
        violations.append({"check": "required_assignment_fields", "details": {"missing": missing}})
    unknown_roles = sorted(set(assignments.get("split_role", [])) - APPROVED_SPLIT_ROLES)
    if unknown_roles:
        violations.append({"check": "approved_split_roles", "details": {"unknown_roles": unknown_roles}})

    if not missing:
        duplicate_count = int(assignments.duplicated(["fold_id", *ROW_KEY_FIELDS]).sum())
        if duplicate_count:
            violations.append({"check": "single_role_per_row_per_fold", "details": {"duplicate_count": duplicate_count}})
        fit_misuse = assignments[assignments["preprocessing_fit_allowed"] != (assignments["split_role"] == "train")]
        if len(fit_misuse):
            violations.append({"check": "preprocessing_fit_train_only", "details": {"row_count": int(len(fit_misuse))}})
        lockbox_misuse = assignments[(assignments["as_of_date"] >= lockbox_record["start_date"]) & (assignments["split_role"] != "lockbox")]
        if len(lockbox_misuse):
            violations.append({"check": "lockbox_isolation", "details": {"row_count": int(len(lockbox_misuse))}})
        non_lockbox_flagged = assignments[(assignments["as_of_date"] < lockbox_record["start_date"]) & assignments["lockbox_flag"]]
        if len(non_lockbox_flagged):
            violations.append({"check": "lockbox_flag_scope", "details": {"row_count": int(len(non_lockbox_flagged))}})

    for fold in fold_definitions.to_dict("records"):
        fold_id = fold["fold_id"]
        fold_rows = assignments[assignments["fold_id"] == fold_id]
        train_rows = fold_rows[fold_rows["split_role"] == "train"]
        validation_rows = fold_rows[fold_rows["split_role"] == "validation"]
        if train_rows.empty:
            violations.append({"check": "non_empty_train_fold", "fold_id": fold_id, "details": {"row_count": 0}})
        if validation_rows.empty:
            violations.append({"check": "non_empty_validation_fold", "fold_id": fold_id, "details": {"row_count": 0}})
        train_overlap = train_rows[train_rows["label_window_end"] >= fold["validation_start_date"]]
        if len(train_overlap):
            violations.append({"check": "training_label_window_overlap", "fold_id": fold_id, "details": {"row_count": int(len(train_overlap))}})
        train_after_boundary = train_rows[train_rows["as_of_date"] >= fold["validation_start_date"]]
        if len(train_after_boundary):
            violations.append({"check": "chronological_train_boundary", "fold_id": fold_id, "details": {"row_count": int(len(train_after_boundary))}})
        validation_outside = validation_rows[
            ~validation_rows["as_of_date"].between(fold["validation_start_date"], fold["validation_end_date"])
        ]
        if len(validation_outside):
            violations.append({"check": "validation_window_membership", "fold_id": fold_id, "details": {"row_count": int(len(validation_outside))}})
        embargo_fit = fold_rows[fold_rows["embargo_flag"] & fold_rows["preprocessing_fit_allowed"]]
        if len(embargo_fit):
            violations.append({"check": "embargo_excluded_from_fit", "fold_id": fold_id, "details": {"row_count": int(len(embargo_fit))}})

    return {
        "artifact_type": "stage4_leakage_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed" if not violations else "failed",
        "benchmark_claim": False,
        "violation_count": len(violations),
        "violations": violations,
        "checks": [
            "single_role_per_row_per_fold",
            "preprocessing_fit_train_only",
            "lockbox_isolation",
            "training_label_window_overlap",
            "chronological_train_boundary",
            "validation_window_membership",
            "embargo_excluded_from_fit",
        ],
    }
