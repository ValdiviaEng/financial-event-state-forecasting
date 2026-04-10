from __future__ import annotations

import pytest

from src.features.news_text import build_article_text, enrich_article_text_fields, normalize_text_value


def test_normalize_text_value_collapses_whitespace_and_linebreaks() -> None:
    text = "  Apple\n launches\r\n service   now  "
    assert normalize_text_value(text) == "Apple launches service now"


def test_normalize_text_value_applies_unicode_normalization() -> None:
    full_width = "Ａｐｐｌｅ"
    assert normalize_text_value(full_width) == "Apple"


def test_build_article_text_headline_only_uses_only_headline() -> None:
    text = build_article_text(headline="Headline", summary="Summary", text_variant="headline_only")
    assert text == "Headline"


def test_build_article_text_headline_plus_summary_uses_separator() -> None:
    text = build_article_text(headline="Headline", summary="Summary", text_variant="headline_plus_summary")
    assert text == "Headline [SEP] Summary"


def test_build_article_text_falls_back_to_summary_if_headline_missing() -> None:
    text = build_article_text(headline=None, summary="Summary only", text_variant="headline_plus_summary")
    assert text == "Summary only"


def test_build_article_text_rejects_unknown_variant() -> None:
    with pytest.raises(ValueError, match="Unsupported text_variant"):
        build_article_text(headline="Headline", summary="Summary", text_variant="body_only")


def test_enrich_article_text_fields_tracks_variant_and_canonical_text() -> None:
    article = {
        "headline": "  Apple launches  ",
        "summary": " Service growth ",
        "source": " Reuters ",
    }
    enriched = enrich_article_text_fields(article, text_variant="headline_plus_summary")

    assert enriched["headline"] == "Apple launches"
    assert enriched["summary"] == "Service growth"
    assert enriched["source"] == "Reuters"
    assert enriched["canonical_text"] == "Apple launches [SEP] Service growth"
    assert enriched["text_variant"] == "headline_plus_summary"
