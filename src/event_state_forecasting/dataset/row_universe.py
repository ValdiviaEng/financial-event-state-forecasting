"""Row-universe hashing and equality checks for Stage 2 datasets."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from typing import Any, Iterable

from event_state_forecasting.data.contracts import ROW_KEY_FIELDS, ContractError


def row_key(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(row[field]) for field in ROW_KEY_FIELDS)


def sorted_row_keys(records: Iterable[dict[str, Any]]) -> list[tuple[str, ...]]:
    keys = [row_key(row) for row in records]
    duplicate_count = sum(count - 1 for count in Counter(keys).values() if count > 1)
    if duplicate_count:
        raise ContractError(f"row universe contains duplicate keys: {duplicate_count}")
    return sorted(keys)


def row_universe_digest(records: Iterable[dict[str, Any]]) -> str:
    keys = sorted_row_keys(records)
    payload = json.dumps(keys, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compare_row_universes(reference: Iterable[dict[str, Any]], candidate: Iterable[dict[str, Any]]) -> dict[str, Any]:
    reference_keys = set(sorted_row_keys(reference))
    candidate_keys = set(sorted_row_keys(candidate))
    missing = sorted(reference_keys - candidate_keys)
    extra = sorted(candidate_keys - reference_keys)
    return {
        "equal": not missing and not extra,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing_sample": missing[:10],
        "extra_sample": extra[:10],
    }
