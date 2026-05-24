"""News ingestion, normalization, deduplication, and interim storage pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import importlib
from pathlib import Path
from typing import Any

from src.data.data_contracts import SCHEMA_VERSION, get_table_contract, validate_manifest, validate_records
from src.data.finnhub_client import FinnhubClient
from src.data.quality_checks import build_news_quality_report
from src.features.news_text import enrich_article_text_fields
from src.split.alignment_rules import annotate_articles_asof_close
from src.utils.config_loader import ResolvedSettings
from src.utils.hashing import build_article_fallback_hash, stable_text_hash
from src.utils.io_utils import read_parquet, write_json, write_manifest, write_parquet


@dataclass(frozen=True, slots=True)
class NewsIngestionResult:
    """Summary of one ticker's news-ingestion output."""

    ticker: str
    raw_paths: tuple[Path, ...]
    interim_path: Path
    quality_report_path: Path
    rows_written: int
    raw_article_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "raw_paths": [str(path) for path in self.raw_paths],
            "interim_path": str(self.interim_path),
            "quality_report_path": str(self.quality_report_path),
            "rows_written": self.rows_written,
            "raw_article_count": self.raw_article_count,
        }


class NewsPipeline:
    """Pipeline for Finnhub company-news download and canonical interim storage."""

    def __init__(self, *, settings: ResolvedSettings, client: FinnhubClient) -> None:
        self.settings = settings
        self.client = client
        self.dataset_build_config = settings.get_config("dataset_build")
        self.data_sources_config = settings.data_sources_config.get("news_data", {})
        self.features_config = settings.get_config("features")

    @classmethod
    def from_settings(
        cls,
        settings: ResolvedSettings,
        client: FinnhubClient | None = None,
    ) -> "NewsPipeline":
        return cls(settings=settings, client=client or FinnhubClient.from_settings(settings))

    def raw_payload_path(self, ticker: str, date_from: str, date_to: str) -> Path:
        raw_subdir = self.dataset_build_config.get("outputs", {}).get("raw_news_subdir", "finnhub")
        return (
            self.settings.project_paths.raw_provider_dir(raw_subdir)
            / ticker
            / f"company_news__{date_from}__{date_to}.json"
        )

    def ledger_path(self) -> Path:
        raw_subdir = self.dataset_build_config.get("outputs", {}).get("raw_news_subdir", "finnhub")
        return self.settings.project_paths.raw_provider_dir(raw_subdir) / "news_request_ledger.parquet"

    def news_file_path(self, ticker: str) -> Path:
        return self.settings.project_paths.data_interim_dir / "news_articles" / f"{ticker}.parquet"

    def quality_report_path(self, ticker: str) -> Path:
        return self.settings.project_paths.data_interim_dir / "news_articles_quality" / f"{ticker}.json"

    def manifest_path(self, run_label: str | None = None) -> Path:
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        suffix = f"_{run_label}" if run_label else ""
        return self.settings.project_paths.data_manifests_dir / f"news_data_manifest{suffix}_{timestamp}.json"

    def plan_requests(
        self,
        tickers: list[str] | tuple[str, ...],
        *,
        start_date: str,
        end_date: str,
        chunk_days: int,
        max_symbols: int | None = None,
    ) -> list[dict[str, Any]]:
        selected_tickers = list(tickers[:max_symbols] if max_symbols else tickers)
        requests: list[dict[str, Any]] = []
        for ticker in selected_tickers:
            for date_from, date_to in self.client.iter_date_chunks(
                start_date,
                end_date,
                chunk_days=chunk_days,
            ):
                requests.append(
                    {
                        "ticker": ticker,
                        "date_from": date_from,
                        "date_to": date_to,
                    }
                )
        return requests

    def run(
        self,
        tickers: list[str] | tuple[str, ...],
        *,
        start_date: str,
        end_date: str,
        chunk_days: int | None = None,
        max_symbols: int | None = None,
        dry_run: bool = False,
        run_label: str | None = None,
    ) -> dict[str, Any]:
        resolved_chunk_days = chunk_days or self.data_sources_config.get(
            "default_chunk_days", self.settings.environment.finnhub_news_chunk_days
        )
        plan = self.plan_requests(
            list(tickers),
            start_date=start_date,
            end_date=end_date,
            chunk_days=resolved_chunk_days,
            max_symbols=max_symbols,
        )

        summary: dict[str, Any] = {
            "stage": "news_data_build",
            "schema_version": SCHEMA_VERSION,
            "start_date": start_date,
            "end_date": end_date,
            "chunk_days": resolved_chunk_days,
            "dry_run": dry_run,
            "planned_requests": plan,
            "results": [],
        }

        if dry_run:
            return summary

        results = [
            self.ingest_ticker_news(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                chunk_days=resolved_chunk_days,
            )
            for ticker in list(tickers[:max_symbols] if max_symbols else tickers)
        ]
        summary["results"] = [result.as_dict() for result in results]
        manifest_path = self.write_manifest(summary=summary, run_label=run_label)
        summary["manifest_path"] = str(manifest_path)
        return summary

    def ingest_ticker_news(
        self,
        *,
        ticker: str,
        start_date: str,
        end_date: str,
        chunk_days: int,
    ) -> NewsIngestionResult:
        raw_paths: list[Path] = []
        ledger_records: list[dict[str, Any]] = []
        normalized_articles: list[dict[str, Any]] = []
        raw_article_count = 0

        for date_from, date_to in self.client.iter_date_chunks(start_date, end_date, chunk_days=chunk_days):
            payload, metadata = self.client.get_company_news(ticker, date_from, date_to)
            raw_path = self.raw_payload_path(ticker, date_from, date_to)
            write_json(payload, raw_path)
            raw_paths.append(raw_path)
            ledger_records.append(metadata.as_ledger_record(raw_path=str(raw_path)))

            articles = self.client.normalize_company_news(payload, symbol=ticker)
            raw_article_count += len(articles)
            normalized_articles.extend(self._prepare_articles(articles, ingest_ts=metadata.requested_at_utc))

        merged_articles, duplicate_url_count, duplicate_fallback_count = self._merge_and_deduplicate(
            ticker,
            normalized_articles,
        )
        if merged_articles:
            validate_records("news_articles", merged_articles)

        quality_report = build_news_quality_report(
            ticker=ticker,
            raw_article_count=raw_article_count,
            deduplicated_articles=merged_articles,
            duplicate_url_count=duplicate_url_count,
            duplicate_fallback_count=duplicate_fallback_count,
        )

        pandas_module = importlib.import_module("pandas")
        news_path = self.news_file_path(ticker)
        news_frame = self._news_frame(merged_articles, pandas_module=pandas_module)
        write_parquet(news_frame, news_path, index=False)

        quality_path = self.quality_report_path(ticker)
        write_json(quality_report, quality_path)
        self._append_ledger_records(ledger_records)

        return NewsIngestionResult(
            ticker=ticker,
            raw_paths=tuple(raw_paths),
            interim_path=news_path,
            quality_report_path=quality_path,
            rows_written=len(merged_articles),
            raw_article_count=raw_article_count,
        )

    def _news_frame(self, merged_articles: list[dict[str, Any]], *, pandas_module: Any) -> Any:
        if merged_articles:
            return pandas_module.DataFrame(merged_articles)
        contract = get_table_contract("news_articles")
        return pandas_module.DataFrame(columns=list(contract.all_column_names))

    def write_manifest(self, *, summary: dict[str, Any], run_label: str | None = None) -> Path:
        manifest_payload = {
            "manifest_version": "1",
            "dataset_name": "news_articles_interim",
            "dataset_version": datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
            "schema_version": SCHEMA_VERSION,
            "created_at_utc": datetime.now(UTC).isoformat(),
            "source_tables": ["news_articles"],
            "summary": summary,
        }
        validate_manifest(manifest_payload)
        path = self.manifest_path(run_label=run_label)
        write_manifest(manifest_payload, path)
        return path

    def _prepare_articles(self, articles: list[dict[str, Any]], *, ingest_ts: datetime) -> list[dict[str, Any]]:
        news_feature_cfg = self.features_config.get("news_features", {})
        text_variant = news_feature_cfg.get("text_variant", "headline_plus_summary")

        prepared = []
        for article in articles:
            enriched = enrich_article_text_fields(article, text_variant=text_variant)
            canonical_text = enriched.get("canonical_text") or None
            text_hash = stable_text_hash(canonical_text)
            if enriched.get("article_id") is None:
                enriched["article_id"] = text_hash
            enriched["canonical_text"] = canonical_text
            enriched["text_hash"] = text_hash
            enriched["ingest_ts"] = ingest_ts
            prepared.append(enriched)

        return annotate_articles_asof_close(
            prepared,
            market_timezone=self.settings.environment.market_timezone,
            exchange_calendar=self.settings.environment.exchange_calendar,
            close_hour=self.settings.environment.market_close_hour,
            close_minute=self.settings.environment.market_close_minute,
        )

    def _merge_and_deduplicate(
        self,
        ticker: str,
        new_articles: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], int, int]:
        existing_articles: list[dict[str, Any]] = []
        news_path = self.news_file_path(ticker)
        if news_path.exists():
            existing = read_parquet(news_path, backend="pandas")
            existing_articles = existing.to_dict(orient="records")

        duplicate_url_count = 0
        duplicate_fallback_count = 0
        deduped: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str]] = set()

        combined_articles = sorted(
            existing_articles + new_articles,
            key=lambda article: (
                _coerce_timestamp(article.get("published_ts_utc")),
                str(article.get("article_id") or ""),
            ),
        )

        for article in combined_articles:
            dedupe_key_type, dedupe_key = self._dedupe_key(article)
            if (dedupe_key_type, dedupe_key) in seen_keys:
                if dedupe_key_type == "url":
                    duplicate_url_count += 1
                else:
                    duplicate_fallback_count += 1
                continue
            seen_keys.add((dedupe_key_type, dedupe_key))
            deduped.append(article)

        return deduped, duplicate_url_count, duplicate_fallback_count

    def _dedupe_key(self, article: dict[str, Any]) -> tuple[str, str]:
        url = article.get("url")
        if url:
            return "url", str(url)

        fallback_hash = build_article_fallback_hash(
            headline=article.get("headline"),
            published_ts_utc=article.get("published_ts_utc"),
            source=article.get("source"),
        )
        return "fallback", fallback_hash

    def _append_ledger_records(self, new_records: list[dict[str, Any]]) -> None:
        ledger_path = self.ledger_path()
        ledger_records: list[dict[str, Any]] = []
        if ledger_path.exists():
            existing = read_parquet(ledger_path, backend="pandas")
            ledger_records = existing.to_dict(orient="records")
        ledger_records.extend(new_records)

        pandas_module = importlib.import_module("pandas")
        write_parquet(pandas_module.DataFrame(ledger_records), ledger_path, index=False)


def _coerce_timestamp(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
