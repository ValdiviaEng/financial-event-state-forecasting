from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from pydantic import SecretStr

from src.data.finnhub_client import FinnhubClient
from src.data.news_pipeline import NewsPipeline
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


def _build_test_settings(tmp_path: Path) -> ResolvedSettings:
    environment = EnvironmentSettings(
        twelve_data_api_key=SecretStr("test-twelve-key"),
        finnhub_api_key=SecretStr("test-finnhub-key"),
        sec_user_agent="Test User test@example.com EventStateForecasting",
        project_root=tmp_path,
        data_dir=tmp_path / "data",
        data_raw_dir=tmp_path / "data" / "raw",
        data_interim_dir=tmp_path / "data" / "interim",
        data_final_dir=tmp_path / "data" / "final",
        data_embeddings_dir=tmp_path / "data" / "embeddings",
        data_kb_dir=tmp_path / "data" / "kb",
        data_manifests_dir=tmp_path / "data" / "manifests",
        artifacts_dir=tmp_path / "artifacts",
        checkpoints_dir=tmp_path / "artifacts" / "checkpoints",
        figures_dir=tmp_path / "artifacts" / "figures",
        tables_dir=tmp_path / "artifacts" / "tables",
        runs_dir=tmp_path / "runs",
        reports_dir=tmp_path / "reports",
        notebooks_dir=tmp_path / "notebooks",
        logs_dir=tmp_path / "runs" / "logs",
        market_timezone="America/New_York",
        exchange_calendar="XNYS",
        market_close_hour=16,
        market_close_minute=0,
    )
    paths = build_project_paths(tmp_path)
    paths.ensure_base_directories()
    return ResolvedSettings(
        environment=environment,
        project_paths=paths,
        config_dir=tmp_path / "configs",
        env_file=None,
        configs={
            "project": {"runtime": {"create_base_directories_on_load": True}},
            "data_sources": {"news_data": {"default_chunk_days": 2}},
            "dataset_build": {"outputs": {"raw_news_subdir": "finnhub"}},
            "features": {"news_features": {"text_variant": "headline_plus_summary"}},
        },
    )


def test_news_pipeline_deduplicates_by_url_before_fallback_hash(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    pipeline = NewsPipeline(settings=settings, client=cast(FinnhubClient, object()))

    duplicates = [
        {
            "article_id": "1",
            "ticker": "AAPL",
            "headline": "Apple launches product",
            "summary": "Strong reception",
            "source": "Reuters",
            "url": "https://example.com/apple-1",
            "published_ts_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC),
            "published_date_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "asof_trade_date": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "after_market_close": False,
            "canonical_text": "Apple launches product [SEP] Strong reception",
            "text_variant": "headline_plus_summary",
            "text_hash": "hash-a",
        },
        {
            "article_id": "2",
            "ticker": "AAPL",
            "headline": "Different text but same URL",
            "summary": "Variant",
            "source": "Reuters",
            "url": "https://example.com/apple-1",
            "published_ts_utc": datetime(2024, 1, 2, 20, 5, tzinfo=UTC),
            "published_date_utc": datetime(2024, 1, 2, 20, 5, tzinfo=UTC).date(),
            "asof_trade_date": datetime(2024, 1, 2, 20, 5, tzinfo=UTC).date(),
            "after_market_close": False,
            "canonical_text": "Different text but same URL [SEP] Variant",
            "text_variant": "headline_plus_summary",
            "text_hash": "hash-b",
        },
    ]

    merged, duplicate_url_count, duplicate_fallback_count = pipeline._merge_and_deduplicate("AAPL", duplicates)
    assert len(merged) == 1
    assert duplicate_url_count == 1
    assert duplicate_fallback_count == 0


def test_news_pipeline_uses_fallback_hash_when_url_missing(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    pipeline = NewsPipeline(settings=settings, client=cast(FinnhubClient, object()))

    duplicates = [
        {
            "article_id": "1",
            "ticker": "AAPL",
            "headline": "Apple launches product",
            "summary": "Strong reception",
            "source": "Reuters",
            "url": None,
            "published_ts_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC),
            "published_date_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "asof_trade_date": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "after_market_close": False,
            "canonical_text": "Apple launches product [SEP] Strong reception",
            "text_variant": "headline_plus_summary",
            "text_hash": "hash-a",
        },
        {
            "article_id": "2",
            "ticker": "AAPL",
            "headline": "Apple launches product",
            "summary": "Strong reception",
            "source": "Reuters",
            "url": None,
            "published_ts_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC),
            "published_date_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "asof_trade_date": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "after_market_close": False,
            "canonical_text": "Apple launches product [SEP] Strong reception",
            "text_variant": "headline_plus_summary",
            "text_hash": "hash-a",
        },
    ]

    merged, duplicate_url_count, duplicate_fallback_count = pipeline._merge_and_deduplicate("AAPL", duplicates)
    assert len(merged) == 1
    assert duplicate_url_count == 0
    assert duplicate_fallback_count == 1


def test_news_pipeline_preserves_distinct_articles_when_url_and_fallback_differ(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    pipeline = NewsPipeline(settings=settings, client=cast(FinnhubClient, object()))

    articles = [
        {
            "article_id": "1",
            "ticker": "AAPL",
            "headline": "Apple launches product",
            "summary": "Strong reception",
            "source": "Reuters",
            "url": None,
            "published_ts_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC),
            "published_date_utc": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "asof_trade_date": datetime(2024, 1, 2, 20, 0, tzinfo=UTC).date(),
            "after_market_close": False,
            "canonical_text": "Apple launches product [SEP] Strong reception",
            "text_variant": "headline_plus_summary",
            "text_hash": "hash-a",
        },
        {
            "article_id": "2",
            "ticker": "AAPL",
            "headline": "Apple analyst downgrade",
            "summary": "Target cut",
            "source": "CNBC",
            "url": None,
            "published_ts_utc": datetime(2024, 1, 2, 21, 0, tzinfo=UTC),
            "published_date_utc": datetime(2024, 1, 2, 21, 0, tzinfo=UTC).date(),
            "asof_trade_date": datetime(2024, 1, 2, 21, 0, tzinfo=UTC).date(),
            "after_market_close": False,
            "canonical_text": "Apple analyst downgrade [SEP] Target cut",
            "text_variant": "headline_plus_summary",
            "text_hash": "hash-b",
        },
    ]

    merged, duplicate_url_count, duplicate_fallback_count = pipeline._merge_and_deduplicate("AAPL", articles)
    assert len(merged) == 2
    assert duplicate_url_count == 0
    assert duplicate_fallback_count == 0
