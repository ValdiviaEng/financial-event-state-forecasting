"""Stage 3 event-state feature construction."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from event_state_forecasting.data.contracts import ROW_KEY_FIELDS
from event_state_forecasting.features.embeddings import DEFAULT_HASH_EMBEDDING_DIMENSION, article_text, hash_text_embedding, pool_embeddings, stable_text_hash
from event_state_forecasting.features.news_alignment import AlignedNewsRecord, align_news_as_of_close
from event_state_forecasting.features.no_news_state import build_no_news_states, validate_no_news_rows_preserved


class EventStateError(ValueError):
    """Raised when event-state construction cannot preserve the row contract."""


def build_event_state_features(
    panel: pd.DataFrame,
    aligned_news: list[AlignedNewsRecord],
    *,
    embedding_dimension: int = DEFAULT_HASH_EMBEDDING_DIMENSION,
) -> pd.DataFrame:
    """Build one event-state row per Stage 2 row key."""

    required = [*ROW_KEY_FIELDS, "dataset_version", "prediction_timestamp", "provider_empty_feed_flag", "provider_truncation_risk_flag"]
    missing = [column for column in required if column not in panel.columns]
    if missing:
        raise EventStateError(f"panel missing event-state fields: {missing}")

    grouped: dict[tuple[str, str], list[AlignedNewsRecord]] = defaultdict(list)
    for record in aligned_news:
        grouped[(record.ticker, record.aligned_as_of_date)].append(record)

    rows: list[dict[str, Any]] = []
    for row in panel.to_dict("records"):
        articles = grouped.get((str(row["canonical_ticker"]), str(row["as_of_date"])), [])
        vectors = [hash_text_embedding(f"{article.title}\n{article.summary}\n{article.url}", dimension=embedding_dimension) for article in articles]
        pooled = pool_embeddings(vectors, dimension=embedding_dimension)
        latest = max((datetime.fromisoformat(article.published_timestamp) for article in articles), default=None)
        prediction_timestamp = datetime.fromisoformat(str(row["prediction_timestamp"]))
        minutes_since_latest = -1.0 if latest is None else (prediction_timestamp - latest).total_seconds() / 60.0
        output_row: dict[str, Any] = {
            **{field: row[field] for field in ROW_KEY_FIELDS},
            "dataset_version": row["dataset_version"],
            "prediction_timestamp": row["prediction_timestamp"],
            "feature_availability_timestamp": row.get("feature_availability_timestamp", row["prediction_timestamp"]),
            "stage3_aligned_news_count": len(articles),
            "provider_empty_feed_flag": bool(row["provider_empty_feed_flag"]),
            "provider_truncation_risk_flag": bool(row["provider_truncation_risk_flag"]),
            "minutes_since_latest_aligned_article": minutes_since_latest,
            "aligned_article_ids": ";".join(article.article_id for article in articles),
            "event_state_embedding_model_id": "deterministic_hash_embedding_v1",
            "event_state_pooling_policy": "mean",
        }
        for idx, value in enumerate(pooled):
            output_row[f"event_state_hash_embedding_{idx:02d}"] = value
        rows.append(output_row)

    output = build_no_news_states(pd.DataFrame.from_records(rows))
    validate_no_news_rows_preserved(output)
    return output


def load_and_align_alphavantage_articles(
    *,
    raw_root: Path,
    tickers: list[str],
    trading_dates: list[Any],
    start_year: int,
    end_year: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw_records: list[dict[str, str]] = []
    source_paths: list[str] = []
    for ticker in tickers:
        for year in range(start_year, end_year + 1):
            path = canonical_alphavantage_path(raw_root, ticker, year, end_year)
            if not path.exists():
                raise EventStateError(f"missing Alpha Vantage raw file for {ticker} {year}: {path}")
            source_paths.append(str(path))
            payload = json.loads(path.read_text(encoding="utf-8"))
            feed = payload.get("feed", [])
            if not isinstance(feed, list):
                raise EventStateError(f"Alpha Vantage feed is not a list: {path}")
            for item in feed:
                if not isinstance(item, dict):
                    raise EventStateError(f"malformed Alpha Vantage feed item: {path}")
                raw_records.append(normalize_raw_article(ticker, item))

    aligned, summary = align_news_as_of_close(raw_records, trading_dates)
    frame = pd.DataFrame.from_records([asdict(record) for record in aligned])
    if frame.empty:
        frame = pd.DataFrame(columns=["article_id", "ticker", "published_timestamp", "aligned_as_of_date", "roll_forward_reason", "title", "summary", "url", "text_hash"])
    summary["source_file_count"] = len(source_paths)
    summary["source_files"] = source_paths
    return frame, summary


def normalize_raw_article(ticker: str, item: dict[str, Any]) -> dict[str, str]:
    record = {
        "ticker": ticker,
        "time_published": str(item.get("time_published", "")),
        "title": str(item.get("title", "")),
        "summary": str(item.get("summary", "")),
        "url": str(item.get("url", "")),
    }
    text_hash = stable_text_hash(article_text(record))
    article_key = "|".join([ticker, record["time_published"], record["url"], text_hash])
    record["text_hash"] = text_hash
    record["article_id"] = hashlib.sha256(article_key.encode("utf-8")).hexdigest()
    return record


def canonical_alphavantage_path(raw_root: Path, ticker: str, year: int, end_year: int) -> Path:
    year_path = raw_root / ticker / f"news_sentiment__{year}-01-01__{year}-12-31.json"
    current_path = raw_root / ticker / f"news_sentiment__{year}-01-01__current.json"
    if year_path.exists():
        return year_path
    if year == end_year and current_path.exists():
        return current_path
    return year_path
