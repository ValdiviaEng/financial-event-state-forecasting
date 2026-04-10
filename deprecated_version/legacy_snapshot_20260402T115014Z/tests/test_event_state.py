from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np

from src.features.event_state import build_daily_event_states, summarize_event_state_coverage
from src.features.news_embeddings import build_article_embedding_cache


def _articles() -> list[dict]:
    return [
        {
            "article_id": "a1",
            "ticker": "AAPL",
            "headline": "Apple launches service",
            "summary": "Recurring revenue expansion",
            "canonical_text": "Apple launches service [SEP] Recurring revenue expansion",
            "text_hash": "",
            "published_ts_utc": datetime(2024, 1, 2, 18, 0, tzinfo=UTC),
            "asof_trade_date": date(2024, 1, 2),
        },
        {
            "article_id": "a2",
            "ticker": "AAPL",
            "headline": "Apple after-hours update",
            "summary": "Post-close guidance revision",
            "canonical_text": "Apple after-hours update [SEP] Post-close guidance revision",
            "text_hash": "",
            "published_ts_utc": datetime(2024, 1, 2, 22, 30, tzinfo=UTC),
            "asof_trade_date": date(2024, 1, 3),
        },
        {
            "article_id": "a3",
            "ticker": "AAPL",
            "headline": "Apple analyst response",
            "summary": "Target price increased",
            "canonical_text": "Apple analyst response [SEP] Target price increased",
            "text_hash": "",
            "published_ts_utc": datetime(2024, 1, 4, 15, 0, tzinfo=UTC),
            "asof_trade_date": date(2024, 1, 4),
        },
    ]


def test_embedding_cache_builds_and_reuses_hash_embeddings() -> None:
    articles = _articles()[:2]
    cache_first = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)
    cache_second = build_article_embedding_cache(
        articles,
        model_id="hashing",
        embedding_dim=8,
        existing_embeddings=cache_first,
    )

    assert len(cache_first) == 2
    assert len(cache_second) == 2
    assert cache_first["text_hash"].tolist() == cache_second["text_hash"].tolist()
    assert cache_first["embedding"].tolist() == cache_second["embedding"].tolist()


def test_embedding_cache_invalidates_when_text_changes() -> None:
    articles = _articles()[:1]
    cache_first = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)

    changed_articles = [dict(articles[0], summary="Revised summary", canonical_text="Apple launches service [SEP] Revised summary")]
    cache_second = build_article_embedding_cache(
        changed_articles,
        model_id="hashing",
        embedding_dim=8,
        existing_embeddings=cache_first,
    )

    assert cache_first.iloc[0]["text_hash"] != cache_second.iloc[0]["text_hash"]
    assert cache_first.iloc[0]["embedding"] != cache_second.iloc[0]["embedding"]


def test_event_state_respects_lookback_and_post_close_alignment() -> None:
    articles = _articles()
    cache = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)

    states = build_daily_event_states(
        articles,
        cache,
        model_id="hashing",
        lookback_days=2,
        decay_half_life_days=1,
        feature_dates=[date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)],
    )

    row_jan2 = states.loc[states["date"] == date(2024, 1, 2)].iloc[0]
    row_jan3 = states.loc[states["date"] == date(2024, 1, 3)].iloc[0]
    row_jan4 = states.loc[states["date"] == date(2024, 1, 4)].iloc[0]

    assert row_jan2["news_count"] == 1
    assert row_jan3["news_count"] == 2
    assert row_jan4["news_count"] == 2
    assert row_jan2["conflict"] == 0.0
    assert row_jan3["density"] == 1.0


def test_event_state_recency_weighting_matches_expected_weighted_average() -> None:
    articles = _articles()[:2]
    cache = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)
    states = build_daily_event_states(
        articles,
        cache,
        model_id="hashing",
        lookback_days=3,
        decay_half_life_days=1,
        feature_dates=[date(2024, 1, 3)],
    )

    embedding_map = {row["article_id"]: np.asarray(row["embedding"], dtype=float) for row in cache.to_dict(orient="records")}
    expected = (embedding_map["a1"] * np.exp(-1) + embedding_map["a2"] * np.exp(0)) / (np.exp(-1) + np.exp(0))
    observed = np.asarray(states.iloc[0]["state_vector"], dtype=float)

    assert np.allclose(observed, expected)


def test_event_state_no_news_fallback_and_cache_stability() -> None:
    articles = _articles()[:1]
    cache = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)

    states_first = build_daily_event_states(
        articles,
        cache,
        model_id="hashing",
        lookback_days=2,
        decay_half_life_days=1,
        feature_dates=[date(2024, 1, 1), date(2024, 1, 2)],
    )
    states_second = build_daily_event_states(
        articles,
        cache,
        model_id="hashing",
        lookback_days=2,
        decay_half_life_days=1,
        feature_dates=[date(2024, 1, 1), date(2024, 1, 2)],
    )

    no_news_row = states_first.loc[states_first["date"] == date(2024, 1, 1)].iloc[0]
    assert no_news_row["news_count"] == 0
    assert np.allclose(np.asarray(no_news_row["state_vector"], dtype=float), np.zeros(8))
    assert states_first.to_dict(orient="records") == states_second.to_dict(orient="records")

    summary = summarize_event_state_coverage(states_first)
    assert summary["row_count"] == 2
