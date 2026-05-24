"""Deterministic hashing helpers for text, records, and manifests."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from src.features.news_text import normalize_text_value


def stable_text_hash(text: str | None, *, algorithm: str = "sha256") -> str:
    """Return a deterministic hash for normalized text."""

    normalized = normalize_text_value(text) or ""
    digest = hashlib.new(algorithm)
    digest.update(normalized.encode("utf-8"))
    return digest.hexdigest()


def stable_record_hash(record: dict[str, Any], *, algorithm: str = "sha256") -> str:
    """Return a deterministic hash for a record using sorted JSON serialization."""

    serialized = json.dumps(record, sort_keys=True, ensure_ascii=True, default=_json_default)
    digest = hashlib.new(algorithm)
    digest.update(serialized.encode("utf-8"))
    return digest.hexdigest()


def build_article_fallback_hash(
    *,
    headline: str | None,
    published_ts_utc: Any,
    source: str | None,
    algorithm: str = "sha256",
) -> str:
    """Build a duplicate-detection hash for cases where URL is missing."""

    payload = {
        "headline": normalize_text_value(headline),
        "published_ts_utc": _json_default(published_ts_utc),
        "source": normalize_text_value(source),
    }
    return stable_record_hash(payload, algorithm=algorithm)


def _json_default(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value
