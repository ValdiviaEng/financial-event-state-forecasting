# Embeddings Layer

This directory stores article-level embedding caches and any future derived pooled text representations.

## Canonical table expected here

- `article_embeddings`

## Rules

- embedding model versions must be recorded,
- text hashing should support incremental recomputation,
- storage must support efficient downstream reads,
- embedding caches should remain independent from training runs.

## Current implementation note

The Stage 9 embedding layer now has executable support for:
- offline article embedding cache generation,
- deterministic hashing-based embeddings for lightweight and test-safe workflows,
- reuse of unchanged embeddings through `(article_id, model_id, text_hash)` matching,
- event-state aggregation from cached embeddings.

Sentence-transformer style model loading is supported when the required package is installed,
but the baseline test-safe backend is the deterministic hashing embedder.
