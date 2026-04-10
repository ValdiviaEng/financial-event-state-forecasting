"""Offline article embedding generation and cache helpers."""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import importlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.data.data_contracts import validate_records
from src.features.news_text import build_article_text
from src.utils.hashing import stable_text_hash
from src.utils.io_utils import read_parquet, write_parquet


class EmbeddingError(RuntimeError):
    """Raised when article embeddings cannot be generated safely."""


HASHING_MODEL_PREFIXES = {"hashing", "debug-hash", "hashing://default"}


def build_article_embedding_cache(
    articles: list[dict[str, Any]],
    *,
    model_id: str,
    text_variant: str = "headline_plus_summary",
    embedding_dim: int = 32,
    batch_size: int = 64,
    device: str | None = None,
    existing_embeddings: list[dict[str, Any]] | pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Build or extend an article embedding cache.

    If `existing_embeddings` is provided, rows with matching `(article_id, model_id,
    text_hash)` are reused instead of recomputed.
    """

    article_df = _prepare_article_frame(articles, text_variant=text_variant)
    if article_df.empty:
        return pd.DataFrame(
            columns=["article_id", "model_id", "embedding_dim", "embedding", "text_hash", "embed_ts"]
        )
    article_df["model_id"] = model_id
    article_df = _deduplicate_article_frame(article_df)
    existing_df = _prepare_existing_embeddings(existing_embeddings)

    if existing_df is not None:
        existing_df = existing_df[existing_df["model_id"] == model_id].copy()
        reusable = existing_df[["article_id", "model_id", "text_hash", "embedding_dim", "embedding", "embed_ts"]]
        merged = article_df.merge(
            reusable,
            how="left",
            on=["article_id", "model_id", "text_hash"],
            suffixes=("", "_cached"),
        )
    else:
        merged = article_df.copy()
        merged["embedding_dim"] = np.nan
        merged["embedding"] = None
        merged["embed_ts"] = None

    rows_to_compute = merged[merged["embedding"].isna()].copy()
    if not rows_to_compute.empty:
        generated_embeddings = generate_embeddings(
            texts=rows_to_compute["canonical_text"].fillna("").tolist(),
            model_id=model_id,
            embedding_dim=embedding_dim,
            batch_size=batch_size,
            device=device,
        )
        generated_rows = pd.DataFrame(
            {
                "article_id": rows_to_compute["article_id"].tolist(),
                "model_id": model_id,
                "text_hash": rows_to_compute["text_hash"].tolist(),
                "embedding_dim": [embedding_dim] * len(generated_embeddings),
                "embedding": [embedding.tolist() for embedding in generated_embeddings],
                "embed_ts": [datetime.now(UTC)] * len(generated_embeddings),
            }
        )
        merged = merged.merge(
            generated_rows,
            how="left",
            on=["article_id", "model_id", "text_hash"],
            suffixes=("", "_generated"),
        )
        for column in ("embedding_dim", "embedding", "embed_ts"):
            generated_column = f"{column}_generated"
            if generated_column in merged.columns:
                merged[column] = merged[column].where(merged[column].notna(), merged[generated_column])
                merged = merged.drop(columns=[generated_column])

    cache_df = merged[["article_id", "model_id", "embedding_dim", "embedding", "text_hash", "embed_ts"]].copy()
    cache_df["embedding_dim"] = cache_df["embedding_dim"].astype(int)
    records = cache_df.to_dict(orient="records")
    validate_records("article_embeddings", records)
    return cache_df.sort_values(["model_id", "article_id"], kind="stable").reset_index(drop=True)


def generate_embeddings(
    *,
    texts: list[str],
    model_id: str,
    embedding_dim: int,
    batch_size: int,
    device: str | None,
) -> list[np.ndarray]:
    """Generate dense embeddings for a list of texts.

    The first production-safe backend is a deterministic hashing embedder used in
    tests and lightweight offline workflows. A sentence-transformer backend is
    also supported when installed.
    """

    normalized_model = model_id.strip()
    if normalized_model in HASHING_MODEL_PREFIXES or normalized_model.startswith("hashing://"):
        return [_hash_embedding(text, embedding_dim=embedding_dim) for text in texts]

    try:
        sentence_transformers = importlib.import_module("sentence_transformers")
    except ModuleNotFoundError as exc:
        raise EmbeddingError(
            f"Embedding model '{model_id}' requires sentence-transformers, which is not installed."
        ) from exc

    model = sentence_transformers.SentenceTransformer(normalized_model, device=device)
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )
    return [np.asarray(vector, dtype=float) for vector in vectors]


def summarize_embedding_cache(cache_df: pd.DataFrame) -> dict[str, Any]:
    """Return a small summary of cache coverage."""

    return {
        "row_count": int(len(cache_df)),
        "model_ids": sorted(cache_df["model_id"].unique().tolist()) if not cache_df.empty else [],
        "article_count": int(cache_df["article_id"].nunique()) if not cache_df.empty else 0,
        "embedding_dims": sorted({int(value) for value in cache_df["embedding_dim"].tolist()})
        if not cache_df.empty
        else [],
    }


def write_embedding_cache(cache_df: pd.DataFrame, file_path: str | Path) -> Path:
    """Write an embedding cache to Parquet."""

    path = Path(file_path)
    write_parquet(cache_df, path, index=False)
    return path


def load_embedding_cache(file_path: str | Path) -> pd.DataFrame:
    """Load an embedding cache from Parquet."""

    return read_parquet(file_path, backend="pandas")


def _prepare_article_frame(articles: list[dict[str, Any]], *, text_variant: str) -> pd.DataFrame:
    if not articles:
        return pd.DataFrame(columns=["article_id", "model_id", "text_hash", "canonical_text"])

    frame = pd.DataFrame(articles).copy()
    required_columns = {"article_id", "headline"}
    missing = sorted(required_columns.difference(frame.columns))
    if missing:
        raise EmbeddingError(f"Articles are missing required columns for embedding cache: {', '.join(missing)}")

    if "canonical_text" not in frame.columns:
        frame["canonical_text"] = frame.apply(
            lambda row: build_article_text(
                headline=row.get("headline"),
                summary=row.get("summary"),
                text_variant=text_variant,
            ),
            axis=1,
        )
    if "text_hash" not in frame.columns:
        frame["text_hash"] = frame["canonical_text"].apply(stable_text_hash)
    else:
        frame["text_hash"] = frame.apply(
            lambda row: stable_text_hash(row.get("canonical_text"))
            if row.get("text_hash") in (None, "")
            else row.get("text_hash"),
            axis=1,
        )

    frame["model_id"] = None
    frame = frame[["article_id", "canonical_text", "text_hash", "model_id"]].copy()
    frame["article_id"] = frame["article_id"].astype(str)
    return frame


def _prepare_existing_embeddings(existing_embeddings: list[dict[str, Any]] | pd.DataFrame | None) -> pd.DataFrame | None:
    if existing_embeddings is None:
        return None
    if isinstance(existing_embeddings, pd.DataFrame):
        return existing_embeddings.copy()
    return pd.DataFrame(existing_embeddings)


def _deduplicate_article_frame(frame: pd.DataFrame) -> pd.DataFrame:
    grouped = frame.groupby(["article_id", "model_id"], sort=True, dropna=False)
    rows = []
    for (_article_id, _model_id), group in grouped:
        unique_hashes = group["text_hash"].dropna().astype(str).unique().tolist()
        if len(unique_hashes) > 1:
            raise EmbeddingError(
                f"Article ID '{_article_id}' maps to multiple text hashes in the same model cache build."
            )
        rows.append(group.iloc[0].to_dict())
    return pd.DataFrame(rows)


def _hash_embedding(text: str, *, embedding_dim: int) -> np.ndarray:
    if embedding_dim <= 0:
        raise EmbeddingError("embedding_dim must be positive.")
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = np.frombuffer(digest, dtype=np.uint8).astype(float)
    repeats = int(np.ceil(embedding_dim / len(values)))
    tiled = np.tile(values, repeats)[:embedding_dim]
    centered = tiled - tiled.mean()
    norm = np.linalg.norm(centered)
    if norm == 0:
        return centered
    return centered / norm
