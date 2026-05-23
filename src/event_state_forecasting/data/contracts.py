"""Stage 2 dataset contract definitions and validators."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Iterable


BENCHMARK_FAMILY_ID = "phase1_top50"
TARGET_FAMILY = "forward_excess_returns"
APPROVED_HORIZONS = ("1d", "5d", "10d", "20d", "60d")
HORIZON_TRADING_STEPS = {"1d": 1, "5d": 5, "10d": 10, "20d": 20, "60d": 60}

ROW_KEY_FIELDS = ("benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id")
REQUIRED_PANEL_FIELDS = (
    "benchmark_family_id",
    "dataset_version",
    "canonical_ticker",
    "as_of_date",
    "prediction_timestamp",
    "horizon_id",
    "feature_availability_timestamp",
    "label_window_start",
    "label_window_end",
    "row_status",
    "exclusion_reason",
    "split_role",
    "fold_id",
    "lockbox_flag",
    "purge_flag",
    "embargo_flag",
    "split_exclusion_reason",
    "preprocessing_fit_allowed",
    "market_data_available_flag",
    "news_provider_window_status",
    "aligned_news_count",
    "no_news_flag",
    "empty_event_state_flag",
    "provider_empty_feed_flag",
    "provider_truncation_risk_flag",
    "news_alignment_status",
)

REQUIRED_MANIFEST_FAMILIES = (
    "identity",
    "protected_scope",
    "sources",
    "coverage",
    "clean_window",
    "rows_and_labels",
    "availability",
    "separation",
    "hashes",
    "limitations",
    "non_claims",
)

PENDING_SPLIT_ROLE = "pending_stage4"
NEWS_ALIGNMENT_STATUS = "stage2_raw_date_proxy_final_alignment_pending_stage3"


class ContractError(ValueError):
    """Raised when a Stage 2 dataset contract is violated."""


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    row_count: int
    duplicate_key_count: int
    horizon_counts: dict[str, int]
    missing_required_fields: list[str]


def validate_panel_records(records: Iterable[dict[str, Any]]) -> ValidationSummary:
    rows = list(records)
    if not rows:
        raise ContractError("panel must contain at least one row")

    missing_fields = sorted(field for field in REQUIRED_PANEL_FIELDS if any(field not in row for row in rows))
    if missing_fields:
        raise ContractError(f"panel rows are missing required fields: {missing_fields}")

    keys = [tuple(row[field] for field in ROW_KEY_FIELDS) for row in rows]
    duplicate_key_count = sum(count - 1 for count in Counter(keys).values() if count > 1)
    if duplicate_key_count:
        raise ContractError(f"panel has duplicate row keys: {duplicate_key_count}")

    horizons = Counter(str(row["horizon_id"]) for row in rows)
    unexpected = sorted(set(horizons) - set(APPROVED_HORIZONS))
    if unexpected:
        raise ContractError(f"panel contains unapproved horizons: {unexpected}")

    for row in rows:
        if row["benchmark_family_id"] != BENCHMARK_FAMILY_ID:
            raise ContractError("benchmark_family_id drift detected")
        if row["split_role"] != PENDING_SPLIT_ROLE:
            raise ContractError("Stage 2 rows must keep split_role pending until Stage 4")

    return ValidationSummary(
        row_count=len(rows),
        duplicate_key_count=duplicate_key_count,
        horizon_counts=dict(sorted(horizons.items())),
        missing_required_fields=missing_fields,
    )


def validate_manifest(manifest: dict[str, Any]) -> None:
    missing = [family for family in REQUIRED_MANIFEST_FAMILIES if family not in manifest]
    if missing:
        raise ContractError(f"dataset manifest is missing required families: {missing}")
    scope = manifest.get("protected_scope", {})
    if scope.get("benchmark_family_id") != BENCHMARK_FAMILY_ID:
        raise ContractError("manifest benchmark family does not match approved Stage 2 family")
    if tuple(scope.get("horizons", ())) != APPROVED_HORIZONS:
        raise ContractError("manifest horizons do not match approved horizons")
    if scope.get("target_family") != TARGET_FAMILY:
        raise ContractError("manifest target family does not match approved target")
