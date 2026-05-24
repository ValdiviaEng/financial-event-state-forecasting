"""News-text selection and normalization helpers."""

from __future__ import annotations

import re
import unicodedata
from typing import Any


VALID_TEXT_VARIANTS = {"headline_only", "headline_plus_summary"}


def normalize_text_value(value: Any) -> str | None:
    """Normalize one text field conservatively without stripping financial meaning."""

    if value in (None, ""):
        return None
    normalized = unicodedata.normalize("NFKC", str(value))
    normalized = normalized.replace("\r", " ").replace("\n", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized or None


def build_article_text(
    *,
    headline: Any,
    summary: Any,
    text_variant: str = "headline_plus_summary",
) -> str:
    """Build the canonical article text used for hashing and embedding."""

    if text_variant not in VALID_TEXT_VARIANTS:
        supported = ", ".join(sorted(VALID_TEXT_VARIANTS))
        raise ValueError(f"Unsupported text_variant '{text_variant}'. Supported: {supported}")

    headline_text = normalize_text_value(headline)
    summary_text = normalize_text_value(summary)

    if text_variant == "headline_only":
        return headline_text or ""

    if headline_text and summary_text:
        return f"{headline_text} [SEP] {summary_text}"
    if headline_text:
        return headline_text
    if summary_text:
        return summary_text
    return ""


def enrich_article_text_fields(article: dict[str, Any], *, text_variant: str) -> dict[str, Any]:
    """Return a copy of an article with normalized text fields and canonical text."""

    enriched = dict(article)
    enriched["headline"] = normalize_text_value(article.get("headline"))
    enriched["summary"] = normalize_text_value(article.get("summary"))
    enriched["source"] = normalize_text_value(article.get("source"))
    enriched["canonical_text"] = build_article_text(
        headline=enriched.get("headline"),
        summary=enriched.get("summary"),
        text_variant=text_variant,
    )
    enriched["text_variant"] = text_variant
    return enriched
