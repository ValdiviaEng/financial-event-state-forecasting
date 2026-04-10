"""Daily event-state aggregation from aligned articles and embeddings."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd


class EventStateError(RuntimeError):
    """Raised when event-state inputs are inconsistent or insufficient."""


def build_daily_event_states(
    articles: Sequence[dict[str, Any]],
    embeddings: Sequence[dict[str, Any]] | pd.DataFrame,
    *,
    model_id: str | None = None,
    lookback_days: int,
    decay_half_life_days: int,
    feature_dates: Sequence[date | str] | None = None,
    include_novelty: bool = True,
    include_conflict: bool = True,
    include_density: bool = True,
) -> pd.DataFrame:
    """Build one daily event-state row per `(ticker, date)`.

    Articles must already be aligned to `asof_trade_date` so that same-day
    post-close articles are excluded automatically.
    """

    if lookback_days <= 0:
        raise EventStateError("lookback_days must be positive.")
    if decay_half_life_days <= 0:
        raise EventStateError("decay_half_life_days must be positive.")

    article_df = _prepare_article_frame(articles)
    embedding_df = _prepare_embedding_frame(embeddings, model_id=model_id)
    if embedding_df.empty and article_df.empty:
        return pd.DataFrame(columns=["ticker", "date", "state_vector", "news_count", "lookback_days", "decay_half_life_days"])

    merged = article_df.merge(
        embedding_df[["article_id", "model_id", "embedding_dim", "embedding"]],
        how="left",
        on="article_id",
    )
    if merged["embedding"].isna().any():
        missing = sorted(merged.loc[merged["embedding"].isna(), "article_id"].astype(str).unique().tolist())
        raise EventStateError(
            "Missing embeddings for article IDs: " + ", ".join(missing[:10])
        )

    embedding_dim = int(merged["embedding_dim"].iloc[0]) if not merged.empty else 0
    target_dates = _resolve_feature_dates(merged, feature_dates)

    rows: list[dict[str, Any]] = []
    for ticker, ticker_articles in merged.groupby("ticker", sort=True):
        ticker_articles = ticker_articles.sort_values(["asof_trade_date", "published_ts_utc", "article_id"], kind="stable")
        previous_vector: np.ndarray | None = None
        for target_date in target_dates:
            window_start = target_date - timedelta(days=lookback_days - 1)
            window_articles = ticker_articles[
                (ticker_articles["asof_trade_date"] >= window_start)
                & (ticker_articles["asof_trade_date"] <= target_date)
            ].copy()

            state_vector, weights = _aggregate_window(
                window_articles,
                target_date=target_date,
                embedding_dim=embedding_dim,
                decay_half_life_days=decay_half_life_days,
            )
            row = {
                "ticker": ticker,
                "date": target_date,
                "state_vector": state_vector.tolist(),
                "news_count": int(len(window_articles)),
                "lookback_days": lookback_days,
                "decay_half_life_days": decay_half_life_days,
            }

            if include_density:
                row["density"] = float(len(window_articles) / lookback_days)
            if include_conflict:
                row["conflict"] = _window_conflict(window_articles, state_vector, weights)
            if include_novelty:
                row["novelty"] = _cosine_distance(previous_vector, state_vector)

            rows.append(row)
            previous_vector = state_vector

    return pd.DataFrame(rows).sort_values(["ticker", "date"], kind="stable").reset_index(drop=True)


def summarize_event_state_coverage(event_states: pd.DataFrame) -> dict[str, Any]:
    """Return a compact summary of event-state coverage and sparsity."""

    return {
        "row_count": int(len(event_states)),
        "ticker_count": int(event_states["ticker"].nunique()) if "ticker" in event_states else 0,
        "date_count": int(event_states["date"].nunique()) if "date" in event_states else 0,
        "nonzero_news_rows": int((event_states.get("news_count", pd.Series(dtype=int)) > 0).sum())
        if not event_states.empty
        else 0,
    }


def _prepare_article_frame(articles: Sequence[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(list(articles)).copy()
    if frame.empty:
        return pd.DataFrame(columns=["article_id", "ticker", "asof_trade_date", "published_ts_utc"])

    required = {"article_id", "ticker", "asof_trade_date"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise EventStateError(
            "Articles are missing required fields for event-state construction: " + ", ".join(missing)
        )

    frame["article_id"] = frame["article_id"].astype(str)
    frame["asof_trade_date"] = pd.to_datetime(frame["asof_trade_date"]).dt.date
    if "published_ts_utc" in frame.columns:
        frame["published_ts_utc"] = pd.to_datetime(frame["published_ts_utc"], utc=True, errors="coerce")
    else:
        frame["published_ts_utc"] = pd.NaT
    return frame


def _prepare_embedding_frame(
    embeddings: Any,
    *,
    model_id: str | None,
) -> pd.DataFrame:
    if isinstance(embeddings, pd.DataFrame):
        frame = embeddings.copy()
    else:
        frame = pd.DataFrame(list(embeddings))
    if frame.empty:
        return pd.DataFrame(columns=["article_id", "model_id", "embedding_dim", "embedding"])

    required = {"article_id", "model_id", "embedding_dim", "embedding"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise EventStateError(
            "Embedding cache is missing required fields: " + ", ".join(missing)
        )

    frame["article_id"] = frame["article_id"].astype(str)
    if model_id is None:
        unique_models = sorted(frame["model_id"].astype(str).unique().tolist())
        if len(unique_models) != 1:
            raise EventStateError(
                "Embeddings contain multiple model IDs; specify `model_id` explicitly."
            )
        model_id = unique_models[0]

    filtered = frame[frame["model_id"].astype(str) == model_id].copy()
    if filtered.empty:
        raise EventStateError(f"No embeddings found for model_id '{model_id}'.")
    return filtered


def _resolve_feature_dates(merged_articles: pd.DataFrame, feature_dates: Sequence[date | str] | None) -> list[date]:
    if feature_dates is not None:
        return sorted({_coerce_date(value) for value in feature_dates})
    return sorted(merged_articles["asof_trade_date"].dropna().unique().tolist())


def _aggregate_window(
    window_articles: pd.DataFrame,
    *,
    target_date: date,
    embedding_dim: int,
    decay_half_life_days: int,
) -> tuple[np.ndarray, np.ndarray]:
    if window_articles.empty:
        return np.zeros(embedding_dim, dtype=float), np.array([], dtype=float)

    embeddings = np.vstack([np.asarray(value, dtype=float) for value in window_articles["embedding"].tolist()])
    deltas = np.array([(target_date - row_date).days for row_date in window_articles["asof_trade_date"].tolist()], dtype=float)
    weights = np.exp(-deltas / decay_half_life_days)
    if weights.sum() == 0:
        return np.zeros(embedding_dim, dtype=float), weights
    weighted = embeddings * weights[:, None]
    state_vector = weighted.sum(axis=0) / weights.sum()
    return state_vector.astype(float), weights


def _window_conflict(window_articles: pd.DataFrame, state_vector: np.ndarray, weights: np.ndarray) -> float:
    if window_articles.empty:
        return 0.0
    embeddings = np.vstack([np.asarray(value, dtype=float) for value in window_articles["embedding"].tolist()])
    squared_distances = np.sum((embeddings - state_vector) ** 2, axis=1)
    if len(weights) == 0 or weights.sum() == 0:
        return float(squared_distances.mean())
    return float(np.average(squared_distances, weights=weights))


def _cosine_distance(previous_vector: np.ndarray | None, current_vector: np.ndarray) -> float:
    if previous_vector is None:
        return 0.0
    prev_norm = np.linalg.norm(previous_vector)
    curr_norm = np.linalg.norm(current_vector)
    if prev_norm == 0 or curr_norm == 0:
        return 0.0
    cosine_similarity = float(np.dot(previous_vector, current_vector) / (prev_norm * curr_norm))
    return 1.0 - cosine_similarity


def _coerce_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))
