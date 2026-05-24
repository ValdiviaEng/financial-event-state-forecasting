"""Deterministic local hash embeddings for Stage 3 event-state artifacts."""

from __future__ import annotations

import hashlib


HASH_EMBEDDING_MODEL_ID = "deterministic_hash_embedding_v1"
DEFAULT_HASH_EMBEDDING_DIMENSION = 8


class EmbeddingError(ValueError):
    """Raised when embedding metadata or vectors are invalid."""


def build_article_embeddings(records: list[dict[str, str]], *, dimension: int = DEFAULT_HASH_EMBEDDING_DIMENSION) -> dict[str, list[float]]:
    if dimension <= 0 or dimension > 8:
        raise EmbeddingError("hash embedding dimension must be between 1 and 8")
    return {record["article_id"]: hash_text_embedding(article_text(record), dimension=dimension) for record in records}


def hash_text_embedding(text: str, *, dimension: int = DEFAULT_HASH_EMBEDDING_DIMENSION) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    for idx in range(dimension):
        start = idx * 4
        chunk = digest[start : start + 4]
        integer = int.from_bytes(chunk, byteorder="big", signed=False)
        values.append((integer / 4_294_967_295.0) * 2.0 - 1.0)
    return values


def pool_embeddings(vectors: list[list[float]], *, dimension: int = DEFAULT_HASH_EMBEDDING_DIMENSION) -> list[float]:
    if not vectors:
        return [0.0] * dimension
    if any(len(vector) != dimension for vector in vectors):
        raise EmbeddingError("embedding dimension mismatch")
    return [sum(vector[idx] for vector in vectors) / len(vectors) for idx in range(dimension)]


def article_text(record: dict[str, str]) -> str:
    return "\n".join([record.get("title", ""), record.get("summary", ""), record.get("url", "")]).strip()


def stable_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
