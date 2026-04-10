from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import cast

import pandas as pd
from pydantic import SecretStr

from src.data.finnhub_client import FinnhubClient, FinnhubRequestMetadata
from src.data.news_pipeline import NewsPipeline
from src.utils.config_loader import EnvironmentSettings, ResolvedSettings
from src.utils.paths import build_project_paths


class FakeFinnhubClient:
    def __init__(self, payloads: dict[tuple[str, str, str], list[dict]]) -> None:
        self.payloads = payloads

    def iter_date_chunks(self, start_date: str, end_date: str, *, chunk_days: int):
        return FinnhubClient.iter_date_chunks(start_date, end_date, chunk_days=chunk_days)

    def get_company_news(self, symbol: str, date_from: str, date_to: str):
        payload = self.payloads[(symbol, date_from, date_to)]
        metadata = FinnhubRequestMetadata(
            endpoint="company-news",
            symbol=symbol,
            requested_at_utc=datetime.now(UTC),
            request_url=f"https://example.test/{symbol}",
            request_params={"from": date_from, "to": date_to},
            response_status=200,
            response_headers={},
        )
        return payload, metadata

    @staticmethod
    def normalize_company_news(payload: list[dict], symbol: str, source_name: str = "finnhub") -> list[dict]:
        return FinnhubClient(api_key="test").normalize_company_news(payload, symbol=symbol, source_name=source_name)


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


def test_news_pipeline_writes_raw_interim_quality_and_manifest(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    fake_client = FakeFinnhubClient(
        {
            ("AAPL", "2024-01-01", "2024-01-02"): [
                {
                    "id": 1,
                    "datetime": 1704202200,
                    "headline": "Apple launches product",
                    "summary": "Strong reception",
                    "source": "Reuters",
                    "url": "https://example.com/apple-1",
                    "category": "company",
                    "related": "AAPL",
                },
                {
                    "id": 2,
                    "datetime": 1704202200,
                    "headline": "Apple launches product",
                    "summary": "Strong reception",
                    "source": "Reuters",
                    "url": "https://example.com/apple-1",
                    "category": "company",
                    "related": "AAPL",
                },
            ],
            ("AAPL", "2024-01-03", "2024-01-03"): [
                {
                    "id": None,
                    "datetime": 1704312000,
                    "headline": "Apple analyst update",
                    "summary": None,
                    "source": "CNBC",
                    "url": None,
                    "category": "company",
                    "related": "AAPL",
                }
            ],
        }
    )
    pipeline = NewsPipeline(settings=settings, client=cast(FinnhubClient, fake_client))

    summary = pipeline.run(
        tickers=["AAPL"],
        start_date="2024-01-01",
        end_date="2024-01-03",
        chunk_days=2,
        dry_run=False,
        run_label="stage6test",
    )

    assert len(summary["results"]) == 1
    result = summary["results"][0]
    manifest_path = Path(summary["manifest_path"])
    interim_path = Path(result["interim_path"])
    quality_path = Path(result["quality_report_path"])
    ledger_path = pipeline.ledger_path()
    assert manifest_path.exists()
    assert interim_path.exists()
    assert quality_path.exists()
    assert ledger_path.exists()

    saved_articles = pd.read_parquet(interim_path)
    assert len(saved_articles) == 2
    assert "text_hash" in saved_articles.columns
    assert "asof_trade_date" in saved_articles.columns
    assert saved_articles["article_id"].notna().all()

    quality_report = json.loads(quality_path.read_text(encoding="utf-8"))
    assert quality_report["duplicate_url_count"] == 1
    assert quality_report["deduplicated_article_count"] == 2


def test_news_pipeline_dry_run_returns_planned_requests(tmp_path: Path) -> None:
    settings = _build_test_settings(tmp_path)
    pipeline = NewsPipeline(settings=settings, client=cast(FinnhubClient, FakeFinnhubClient({})))

    summary = pipeline.run(
        tickers=["AAPL", "MSFT"],
        start_date="2024-01-01",
        end_date="2024-01-03",
        chunk_days=2,
        max_symbols=1,
        dry_run=True,
    )

    assert summary["dry_run"] is True
    assert len(summary["planned_requests"]) == 2
    assert summary["planned_requests"][0]["ticker"] == "AAPL"
