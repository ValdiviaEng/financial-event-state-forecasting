from __future__ import annotations

import json
from pathlib import Path

from src.features.news_embeddings import build_article_embedding_cache
from src.utils.reproducibility import build_run_metadata, save_run_metadata


def test_embedding_cache_is_deterministic_for_identical_inputs() -> None:
    articles = [
        {"article_id": "a1", "headline": "Apple launches service", "summary": "Recurring revenue expansion"},
        {"article_id": "a2", "headline": "Apple analyst update", "summary": "Target price increased"},
    ]
    cache_a = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)
    cache_b = build_article_embedding_cache(articles, model_id="hashing", embedding_dim=8)

    assert cache_a["text_hash"].tolist() == cache_b["text_hash"].tolist()
    assert cache_a["embedding"].tolist() == cache_b["embedding"].tolist()


def test_run_metadata_round_trip_contains_seed_and_runtime_fields(tmp_path: Path) -> None:
    metadata = build_run_metadata(
        run_id="repro_test",
        random_seed=42,
        deterministic_torch=False,
        extra={"panel_path": "panel.parquet"},
    )
    output_path = tmp_path / "run_metadata.json"
    save_run_metadata(metadata, output_path)

    saved = json.loads(output_path.read_text(encoding="utf-8"))
    assert saved["run_id"] == "repro_test"
    assert saved["random_seed"] == 42
    assert "python_version" in saved
    assert saved["extra"]["panel_path"] == "panel.parquet"
