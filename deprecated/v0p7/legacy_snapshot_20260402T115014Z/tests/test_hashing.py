from __future__ import annotations

from datetime import UTC, datetime

from src.utils.hashing import build_article_fallback_hash, stable_record_hash, stable_text_hash


def test_stable_text_hash_is_whitespace_and_unicode_normalization_aware() -> None:
    hash_a = stable_text_hash("Apple\nlaunches   service")
    hash_b = stable_text_hash("Ａｐｐｌｅ launches service")
    assert hash_a == hash_b


def test_stable_text_hash_changes_when_canonical_text_changes() -> None:
    assert stable_text_hash("Apple launches service") != stable_text_hash("Apple launches update")


def test_stable_record_hash_is_order_independent_for_dict_keys() -> None:
    record_a = {"ticker": "AAPL", "date": "2024-01-02", "value": 1.0}
    record_b = {"value": 1.0, "date": "2024-01-02", "ticker": "AAPL"}
    assert stable_record_hash(record_a) == stable_record_hash(record_b)


def test_article_fallback_hash_is_stable_for_equivalent_inputs() -> None:
    published = datetime(2024, 1, 2, 20, 30, tzinfo=UTC)
    hash_a = build_article_fallback_hash(headline=" Apple launches ", published_ts_utc=published, source="Reuters")
    hash_b = build_article_fallback_hash(headline="Apple launches", published_ts_utc=published, source=" Reuters ")
    assert hash_a == hash_b


def test_article_fallback_hash_changes_when_timestamp_changes() -> None:
    hash_a = build_article_fallback_hash(
        headline="Apple launches",
        published_ts_utc=datetime(2024, 1, 2, 20, 30, tzinfo=UTC),
        source="Reuters",
    )
    hash_b = build_article_fallback_hash(
        headline="Apple launches",
        published_ts_utc=datetime(2024, 1, 2, 20, 31, tzinfo=UTC),
        source="Reuters",
    )
    assert hash_a != hash_b
