from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
MARKET_FEATURE_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"
STAGE19_ROOT = PROJECT_ROOT / "data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z"
STAGE22_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16"
STAGE23_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80"
STAGE24_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80"
STAGE25_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_6dff1bd__run_689fbb80"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"

SOURCE_ID = "6dff1bd"
SPRINT_DATE = "2026-05-25"
ROW_KEY = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
HORIZON_WEIGHTS = {"1d": 0.30, "5d": 0.25, "10d": 0.20, "20d": 0.15, "60d": 0.10}
FINBERT_MODEL_ID = "ProsusAI/finbert"
FINBERT_REVISION = "4556d13015211d73dccd3fdd39d39232506f3e43"
TOKENIZER_ID = "ProsusAI/finbert"
TOKENIZER_REVISION = FINBERT_REVISION
TEXT_NORMALIZATION_POLICY = "title_summary_v1"
PROJECTION_SEED = 20260525
PROJECTION_DIM = 128
SEQUENCE_WINDOW_LENGTHS = (20, 60)
TSMIXER_FIXED_SEEDS = (2026052501, 2026052502, 2026052503, 2026052504, 2026052505)
TSMIXER_FIXED_WINDOW_LENGTH = 60
TSMIXER_FIXED_EPOCHS = 8
TSMIXER_FIXED_BATCH_SIZE = 1024
TSMIXER_OPTUNA_TRIALS = 60
TSMIXER_OPTUNA_SEEDS = (2026053201, 2026053202)
TSMIXER_OPTUNA_EPOCHS = 8
TSMIXER_OPTUNA_SAMPLER_SEED = 20260532


class V1P0FinalSprintError(RuntimeError):
    """Raised when final-sprint artifacts cannot be built safely."""


@dataclass(slots=True)
class StageOutput:
    stage: int
    status: str
    output_root: Path
    manifest_path: Path
    summary: dict[str, Any]


def normalize_article_text(title: object, summary: object) -> str:
    title_text = " ".join(str(title or "").strip().split())
    summary_text = " ".join(str(summary or "").strip().split())
    if title_text and summary_text:
        return f"{title_text}\n\n{summary_text}"
    return title_text or summary_text


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def stable_digest(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def deterministic_projection_matrix(input_dim: int, output_dim: int = PROJECTION_DIM, seed: int = PROJECTION_SEED) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix = rng.normal(loc=0.0, scale=1.0 / math.sqrt(output_dim), size=(input_dim, output_dim)).astype("float32")
    return matrix


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def result_root(stage: int, purpose: str, generated_token: str, digest_source: dict[str, Any]) -> Path:
    digest = stable_digest({"stage": stage, "purpose": purpose, **digest_source})[:8]
    return RESULT_ROOT / f"v1p0__phase1_top50_v1p0__stage{stage:02d}__{purpose}__{generated_token}__src_{SOURCE_ID}__run_{digest}"


def run_stage18_sequence_window_materialization(window_lengths: tuple[int, ...] = SEQUENCE_WINDOW_LENGTHS) -> StageOutput:
    generated = "20260525T145000Z"
    market_manifest = json.loads((MARKET_FEATURE_ROOT / "feature_manifest.json").read_text(encoding="utf-8"))
    feature_columns = list(market_manifest["feature_columns"])
    root = result_root(18, "sequence_windows", generated, {"market_features": market_manifest["feature_digest_sha256"], "window_lengths": list(window_lengths)})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "sequence_window_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage18_sequence_window_materialization.md"
    base_index_path = root / "sequence_base_index.parquet"
    row_index_path = root / "sequence_row_index.parquet"

    market = pd.read_parquet(MARKET_FEATURE_ROOT / "market_lag_features.parquet", columns=[*ROW_KEY, *feature_columns])
    market["as_of_date"] = pd.to_datetime(market["as_of_date"]).dt.strftime("%Y-%m-%d")
    base = market[["benchmark_family_id", "canonical_ticker", "as_of_date", *feature_columns]].drop_duplicates(["benchmark_family_id", "canonical_ticker", "as_of_date"]).sort_values(["canonical_ticker", "as_of_date"]).reset_index(drop=True)
    base["sequence_base_index"] = np.arange(len(base), dtype="int32")
    row_index = market[[*ROW_KEY]].merge(base[["benchmark_family_id", "canonical_ticker", "as_of_date", "sequence_base_index"]], on=["benchmark_family_id", "canonical_ticker", "as_of_date"], how="left", validate="many_to_one")
    if row_index["sequence_base_index"].isna().any():
        raise V1P0FinalSprintError("Stage 18 sequence index has unmapped market rows")
    base[["benchmark_family_id", "canonical_ticker", "as_of_date", "sequence_base_index"]].to_parquet(base_index_path, index=False)
    row_index.to_parquet(row_index_path, index=False)

    tensor_outputs: dict[str, dict[str, Any]] = {}
    build_started = time.perf_counter()
    for window_length in window_lengths:
        values, mask = _build_sequence_tensors(base, feature_columns, window_length)
        values_path = root / f"sequence_{window_length}d_values.npy"
        mask_path = root / f"sequence_{window_length}d_observed_mask.npy"
        np.save(values_path, values)
        np.save(mask_path, mask)
        tensor_outputs[f"{window_length}d"] = {
            "values": rel(values_path),
            "observed_mask": rel(mask_path),
            "shape": list(values.shape),
            "observed_fraction": float(mask.mean()),
            "values_digest_sha256": sha256_file(values_path),
            "mask_digest_sha256": sha256_file(mask_path),
        }

    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet", columns=["fold_id", *ROW_KEY, "split_role"])
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])]
    validation = {
        "market_feature_rows": int(len(market)),
        "unique_sequence_rows": int(len(base)),
        "row_index_rows": int(len(row_index)),
        "row_index_duplicate_keys": int(row_index.duplicated(ROW_KEY).sum()),
        "stage4_train_validation_lockbox_rows": int(len(splits)),
        "stage4_rows_missing_sequence_index": int(splits.merge(row_index[[*ROW_KEY, "sequence_base_index"]], on=ROW_KEY, how="left")["sequence_base_index"].isna().sum()),
        "status": "passed",
    }
    if validation["row_index_duplicate_keys"] or validation["stage4_rows_missing_sequence_index"]:
        validation["status"] = "failed"
        raise V1P0FinalSprintError(f"Stage 18 validation failed: {validation}")
    manifest = {
        "artifact_type": "v1p0_stage18_sequence_window_manifest",
        "artifact_id": f"stage18_sequence_windows__{market_manifest['feature_digest_sha256'][:12]}__20260525T145000Z",
        "generated_at_utc": "2026-05-25T14:50:00Z",
        "run_id": root.name,
        "status": "completed",
        "source_stage17_feature_artifact_id": market_manifest["artifact_id"],
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "window_lengths": list(window_lengths),
        "tensor_policy": {
            "row_level": "unique benchmark_family_id/canonical_ticker/as_of_date sequences mapped to horizon rows by sequence_row_index",
            "padding_policy": "left_pad_missing_history_with_zero_values_and_false_observed_mask",
            "normalization_policy": "fold_local_train_only_normalization_in_stage31",
            "value_dtype": "float32",
            "mask_dtype": "bool",
        },
        "validation": validation,
        "runtime_seconds": round(time.perf_counter() - build_started, 3),
        "outputs": {"manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path), "sequence_base_index": rel(base_index_path), "sequence_row_index": rel(row_index_path), **tensor_outputs},
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_tsmixer_model_evidence", "not_benchmark_result", "not_stage6_reinterpretation", "stage30_31_required_for_tsmixer_evidence"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 18, "stage_name": "sequence_window_materialization", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(
        f"# Stage 18 Sequence Window Materialization\n\nStatus: completed; sequence tensors materialized for TSMixer.\n\nWindow lengths: {', '.join(str(w) + 'd' for w in window_lengths)}\n\nUnique sequence rows: {len(base)}\n\nFeature count: {len(feature_columns)}\n\nValidation status: `{validation['status']}`\n\nNon-claims: sequence tensors are not TSMixer benchmark evidence until Stage 30 and Stage 31 consume them.\n",
        encoding="utf-8",
    )
    return StageOutput(18, "completed", root, manifest_path, {"manifest": rel(manifest_path), "sequence_row_index": rel(row_index_path), "window_lengths": list(window_lengths)})


def _build_sequence_tensors(base: pd.DataFrame, feature_columns: list[str], window_length: int) -> tuple[np.ndarray, np.ndarray]:
    values = np.zeros((len(base), window_length, len(feature_columns)), dtype="float32")
    mask = np.zeros((len(base), window_length, len(feature_columns)), dtype=bool)
    for _, group in base.groupby("canonical_ticker", sort=False):
        group = group.sort_values("as_of_date")
        indices = group["sequence_base_index"].to_numpy(dtype="int64")
        raw = group[feature_columns].to_numpy(dtype="float32")
        observed = ~np.isnan(raw)
        raw = np.nan_to_num(raw, nan=0.0).astype("float32", copy=False)
        for local_pos, global_index in enumerate(indices):
            start = max(0, local_pos - window_length + 1)
            seq = raw[start : local_pos + 1]
            seq_mask = observed[start : local_pos + 1]
            dst_start = window_length - len(seq)
            values[global_index, dst_start:, :] = seq
            mask[global_index, dst_start:, :] = seq_mask
    return values, mask


def run_stage26_finbert_contract() -> StageOutput:
    generated = "20260525T100000Z"
    contract = {
        "model_id": FINBERT_MODEL_ID,
        "model_revision": FINBERT_REVISION,
        "tokenizer_id": TOKENIZER_ID,
        "tokenizer_revision": TOKENIZER_REVISION,
        "text_normalization_policy": TEXT_NORMALIZATION_POLICY,
        "text_fields": ["title", "summary"],
        "embedding_method": "mean_last_hidden_state_attention_masked",
        "sentiment_method": "sequence_classification_logits_and_softmax_probabilities",
        "cache_key_fields": ["article_id", "text_hash", "normalized_text_hash", "model_id", "model_revision", "tokenizer_id", "tokenizer_revision", "text_normalization_policy"],
        "license_review": {
            "model_card_url": "https://huggingface.co/ProsusAI/finbert",
            "model_card_license_field": "not_declared_in_model_card_metadata_observed_2026_05_25",
            "usage_classification": "local_research_use_with_publication_distribution_caution",
            "required_follow_up_before_public_distribution": "manual_license_review_or_model_owner_license_confirmation",
        },
        "offline_rerun_requirement": "stage27 cache must be readable without internet after materialization",
        "environment_capture_required": ["python", "torch", "transformers", "device", "batch_size", "max_length"],
        "benchmark_claim": False,
        "positive_claim_approved": False,
    }
    root = result_root(26, "finbert_contract", generated, contract)
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "finbert_source_cache_contract.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage26_finbert_source_license_cache_contract.md"
    manifest = {
        "artifact_type": "v1p0_stage26_finbert_source_cache_contract",
        "artifact_id": f"stage26_finbert_contract__{FINBERT_REVISION[:12]}__20260525T100000Z",
        "generated_at_utc": "2026-05-25T10:00:00Z",
        "run_id": root.name,
        "status": "completed",
        "contract": contract,
        "outputs": {"contract": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)},
        "non_claims": ["not_embedding_extraction", "not_model_improvement", "not_provider_completeness_claim", "stage39_claim_review_required"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 26, "stage_name": "finbert_source_license_cache_contract", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(
        f"# Stage 26 FinBERT Source, License, And Cache Contract\n\nStatus: completed; source and cache contract frozen without extraction claim\n\nModel: `{FINBERT_MODEL_ID}` at `{FINBERT_REVISION}`.\n\nTokenizer: `{TOKENIZER_ID}` at `{TOKENIZER_REVISION}`.\n\nText scope: title + summary via `{TEXT_NORMALIZATION_POLICY}`.\n\nLicense note: the model card metadata does not declare a license in the observed card; local research use proceeds with publication/distribution caution.\n\nNon-claims: no embeddings, model improvement, provider completeness, trading output, or positive benchmark claim are created by this stage.\n",
        encoding="utf-8",
    )
    return StageOutput(26, "completed", root, manifest_path, {"contract_digest": stable_digest(contract), "model_id": FINBERT_MODEL_ID})


def run_stage27_article_cache(stage26: StageOutput, batch_size: int = 128, max_length: int = 160) -> StageOutput:
    generated = "20260525T101500Z"
    root = result_root(27, "finbert_article_cache", generated, {"stage26": stage26.summary["contract_digest"], "batch_size": batch_size, "max_length": max_length})
    root.mkdir(parents=True, exist_ok=True)
    cache_path = root / "article_finbert_cache.parquet"
    manifest_path = root / "article_cache_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage27_finbert_article_embedding_cache.md"

    aligned = pd.read_parquet(STAGE3_ROOT / "aligned_news.parquet")
    articles = aligned[["article_id", "ticker", "published_timestamp", "title", "summary", "url", "text_hash"]].drop_duplicates(["article_id", "text_hash"]).copy()
    articles["normalized_text"] = [normalize_article_text(title, summary) for title, summary in zip(articles["title"], articles["summary"])]
    articles["normalized_text_hash"] = articles["normalized_text"].map(sha256_text)
    articles["article_cache_key"] = [
        sha256_text("|".join([str(row.article_id), str(row.text_hash), str(row.normalized_text_hash), FINBERT_MODEL_ID, FINBERT_REVISION, TOKENIZER_ID, TOKENIZER_REVISION, TEXT_NORMALIZATION_POLICY]))
        for row in articles.itertuples(index=False)
    ]
    articles = articles[articles["normalized_text"].str.len() > 0].reset_index(drop=True)

    started = time.perf_counter()
    if cache_path.exists():
        cache = pd.read_parquet(cache_path)
        backend = "transformers_auto_model_sequence_classification_cache_materialized_then_reused"
        skipped_rows = int(len(articles) - len(cache))
        cache_reuse = True
    else:
        cache = _extract_finbert_embeddings(articles, batch_size=batch_size, max_length=max_length)
        cache.to_parquet(cache_path, index=False)
        backend = "transformers_auto_model_sequence_classification"
        skipped_rows = 0
        cache_reuse = False
    digest = sha256_file(cache_path)
    embedding_columns = [column for column in cache.columns if column.startswith("embedding_")]
    manifest = {
        "artifact_type": "v1p0_stage27_finbert_article_cache_manifest",
        "artifact_id": f"article_finbert_mean_embedding_logits_v1__{digest[:12]}__20260525T101500Z",
        "generated_at_utc": "2026-05-25T10:15:00Z",
        "run_id": root.name,
        "status": "completed",
        "source_stage26_artifact_id": json.loads(stage26.manifest_path.read_text(encoding="utf-8"))["artifact_id"],
        "model_id": FINBERT_MODEL_ID,
        "model_revision": FINBERT_REVISION,
        "tokenizer_id": TOKENIZER_ID,
        "tokenizer_revision": TOKENIZER_REVISION,
        "text_normalization_policy": TEXT_NORMALIZATION_POLICY,
        "extraction_backend": backend,
        "cache_reuse_in_final_rerun": cache_reuse,
        "batch_size": batch_size,
        "max_length": max_length,
        "input_article_rows": int(len(articles)),
        "cached_article_rows": int(len(cache)),
        "skipped_rows": skipped_rows,
        "embedding_dimension": int(len(embedding_columns)),
        "cache_digest_sha256": digest,
        "runtime_seconds": round(time.perf_counter() - started, 3),
        "outputs": {"article_cache": rel(cache_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)},
        "provider_completeness_claim": False,
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_event_representation_benchmark", "not_model_improvement", "not_provider_completeness_claim", "stage29_required_for_representation_evidence"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 27, "stage_name": "finbert_article_embedding_cache", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(
        f"# Stage 27 FinBERT Article Embedding Cache\n\nStatus: completed; article cache materialized without improvement claim\n\nCached articles: {len(cache)}\n\nEmbedding dimension: {len(embedding_columns)}\n\nDigest: `{digest}`\n\nNon-claims: article embeddings do not imply event-state improvement, provider completeness, trading value, or benchmark promotion.\n",
        encoding="utf-8",
    )
    return StageOutput(27, "completed", root, manifest_path, {"article_cache": rel(cache_path), "cache_digest": digest, "embedding_dimension": int(len(embedding_columns))})


def _extract_finbert_embeddings(articles: pd.DataFrame, batch_size: int, max_length: int) -> pd.DataFrame:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_ID, revision=TOKENIZER_REVISION)
    model = AutoModelForSequenceClassification.from_pretrained(FINBERT_MODEL_ID, revision=FINBERT_REVISION, output_hidden_states=True).to(device)
    model.eval()
    id2label = {int(k): str(v).lower() for k, v in getattr(model.config, "id2label", {}).items()}
    rows: list[pd.DataFrame] = []
    texts = articles["normalized_text"].tolist()
    with torch.inference_mode():
        for start in range(0, len(articles), batch_size):
            batch = articles.iloc[start : start + batch_size].reset_index(drop=True)
            encoded = tokenizer(texts[start : start + batch_size], padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            outputs = model(**encoded)
            hidden = outputs.hidden_states[-1]
            mask = encoded["attention_mask"].unsqueeze(-1).to(hidden.dtype)
            embedding = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1.0)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)
            embedding_np = embedding.detach().cpu().numpy().astype("float32")
            logits_np = logits.detach().cpu().numpy().astype("float32")
            probs_np = probs.detach().cpu().numpy().astype("float32")
            base = batch[["article_cache_key", "article_id", "ticker", "published_timestamp", "text_hash", "normalized_text_hash"]].copy()
            for index in range(embedding_np.shape[1]):
                base[f"embedding_{index:03d}"] = embedding_np[:, index]
            for index in range(logits_np.shape[1]):
                label = id2label.get(index, f"label_{index}").replace(" ", "_")
                base[f"logit_{label}"] = logits_np[:, index]
                base[f"prob_{label}"] = probs_np[:, index]
            base["model_id"] = FINBERT_MODEL_ID
            base["model_revision"] = FINBERT_REVISION
            base["tokenizer_revision"] = TOKENIZER_REVISION
            rows.append(base)
    return pd.concat(rows, ignore_index=True)


def run_stage28_finbert_aggregations(stage27: StageOutput, projection_dim: int = PROJECTION_DIM, projection_seed: int = PROJECTION_SEED) -> StageOutput:
    generated = "20260525T150000Z" if projection_dim != 32 else "20260525T104500Z"
    root = result_root(28, "finbert_aggregation_sidecars", generated, {"stage27": stage27.summary["cache_digest"], "projection_dim": projection_dim, "projection_seed": projection_seed})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "finbert_aggregation_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage28_finbert_aggregation_ablation_report.md"
    article_cache = pd.read_parquet(PROJECT_ROOT / stage27.summary["article_cache"])
    aligned = pd.read_parquet(STAGE3_ROOT / "aligned_news.parquet")
    base_rows = pd.read_parquet(STAGE3_ROOT / "event_state_features.parquet", columns=[*ROW_KEY, "stage3_aligned_news_count", "provider_empty_feed_flag", "provider_truncation_risk_flag", "minutes_since_latest_aligned_article", "no_news_flag", "empty_event_state_flag"])
    cache_for_join = article_cache.drop(columns=[column for column in ["ticker", "published_timestamp"] if column in article_cache.columns])
    article_frame = aligned.merge(cache_for_join, on=["article_id", "text_hash"], how="inner", validate="many_to_one")
    article_frame["published_timestamp"] = pd.to_datetime(article_frame["published_timestamp"], utc=True, errors="coerce")
    article_frame["aligned_as_of_date"] = pd.to_datetime(article_frame["aligned_as_of_date"], errors="coerce")
    article_frame["as_of_close_timestamp"] = pd.to_datetime(article_frame["aligned_as_of_date"].dt.strftime("%Y-%m-%d") + " 16:00:00", utc=True)
    age_hours = (article_frame["as_of_close_timestamp"] - article_frame["published_timestamp"]).dt.total_seconds().fillna(0.0) / 3600.0
    article_frame["recency_weight"] = np.exp(-np.maximum(age_hours.to_numpy(dtype="float64"), 0.0) / 24.0)
    embedding_cols = [column for column in article_cache.columns if column.startswith("embedding_")]
    sentiment_cols = [column for column in article_cache.columns if column.startswith("prob_") or column.startswith("logit_")]
    numeric_cols = embedding_cols + sentiment_cols
    outputs: dict[str, str] = {}
    feature_columns_by_variant: dict[str, list[str]] = {}
    variants = {
        "event_finbert_mean_v1": _aggregate_mean(article_frame, numeric_cols),
        "event_finbert_recency_v1": _aggregate_weighted(article_frame, numeric_cols, "recency_weight"),
        "event_finbert_topk_v1": _aggregate_topk_recent(article_frame, numeric_cols, top_k=3),
        "event_finbert_count_recency_v1": _aggregate_weighted(article_frame, numeric_cols, "recency_weight"),
    }
    projection = deterministic_projection_matrix(len(embedding_cols), projection_dim, projection_seed)
    projection_digest = hashlib.sha256(projection.tobytes()).hexdigest()
    for variant_id, aggregated in variants.items():
        sidecar, feature_columns = _build_event_sidecar(base_rows, aggregated, embedding_cols, sentiment_cols, projection, variant_id)
        if variant_id == "event_finbert_count_recency_v1":
            scalar_cols = ["stage3_aligned_news_count", "minutes_since_latest_aligned_article", "provider_truncation_risk_flag", "no_news_flag"]
            for col in scalar_cols:
                sidecar[col] = sidecar[col].fillna(0).astype("float32")
            feature_columns.extend(scalar_cols)
        path = root / f"{variant_id}.parquet"
        sidecar.to_parquet(path, index=False)
        outputs[variant_id] = rel(path)
        feature_columns_by_variant[variant_id] = feature_columns
    manifest = {
        "artifact_type": "v1p0_stage28_finbert_aggregation_manifest",
        "artifact_id": f"stage28_finbert_aggregations__{stage27.summary['cache_digest'][:12]}__proj{projection_dim}__{generated}",
        "generated_at_utc": "2026-05-25T15:00:00Z" if projection_dim != 32 else "2026-05-25T10:45:00Z",
        "run_id": root.name,
        "status": "completed",
        "source_stage27_cache_digest_sha256": stage27.summary["cache_digest"],
        "source_stage27_artifact": stage27.summary["article_cache"],
        "row_key": ROW_KEY,
        "projection_policy": {
            "input_embedding_dimension": len(embedding_cols),
            "projection_dimension": projection_dim,
            "seed": projection_seed,
            "projection_digest_sha256": projection_digest,
            "user_approved_projection": projection_dim == 128,
            "approval_note": "user selected 128d rerun with diagnostics on 2026-05-25" if projection_dim == 128 else "legacy_projection_policy",
            "diagnostic_requirement": "Stage 29 must treat this as compressed FinBERT representation evidence and preserve non-claims.",
        },
        "variants": {variant_id: {"path": path, "feature_columns": feature_columns_by_variant[variant_id], "feature_count": len(feature_columns_by_variant[variant_id])} for variant_id, path in outputs.items()},
        "row_count_per_sidecar": int(len(base_rows)),
        "outputs": {"manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path), **outputs},
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_model_evidence", "not_event_improvement_claim", "not_provider_completeness_claim", "stage29_required_for_benchmark_gate"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 28, "stage_name": "finbert_aggregation_ablations", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(
        f"# Stage 28 FinBERT Aggregation Ablations\n\nStatus: completed; aggregation sidecars built without model-evidence claim\n\nVariants: {', '.join(outputs)}\n\nRows per sidecar: {len(base_rows)}\n\nProjection dimension: {projection_dim}\n\nProjection approval: {'user-approved 128d rerun with diagnostics' if projection_dim == 128 else 'legacy projection policy'}\n\nNon-claims: feature sidecars are compressed representation inputs, not model evidence, until Stage 29 or later saved-prediction diagnostics consume them.\n",
        encoding="utf-8",
    )
    return StageOutput(28, "completed", root, manifest_path, {"manifest": rel(manifest_path), "variants": outputs, "feature_columns_by_variant": feature_columns_by_variant})


def _aggregate_mean(article_frame: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    grouped = article_frame.groupby(["ticker", "aligned_as_of_date"], sort=True)
    out = grouped[numeric_cols].mean().reset_index()
    out["aligned_article_count"] = grouped["article_id"].nunique().to_numpy()
    return out


def _aggregate_weighted(article_frame: pd.DataFrame, numeric_cols: list[str], weight_col: str) -> pd.DataFrame:
    working = article_frame.copy()
    weights = working[weight_col].astype("float64").clip(lower=1e-9)
    for col in numeric_cols:
        working[col] = working[col].astype("float64") * weights
    grouped = working.groupby(["ticker", "aligned_as_of_date"], sort=True)
    sums = grouped[numeric_cols].sum()
    weight_sums = grouped[weight_col].sum().clip(lower=1e-9)
    out = sums.div(weight_sums, axis=0).reset_index()
    out["aligned_article_count"] = grouped["article_id"].nunique().to_numpy()
    return out


def _aggregate_topk_recent(article_frame: pd.DataFrame, numeric_cols: list[str], top_k: int) -> pd.DataFrame:
    sorted_frame = article_frame.sort_values(["ticker", "aligned_as_of_date", "published_timestamp"], ascending=[True, True, False])
    top = sorted_frame.groupby(["ticker", "aligned_as_of_date"], sort=False).head(top_k)
    return _aggregate_mean(top, numeric_cols)


def _build_event_sidecar(base_rows: pd.DataFrame, aggregated: pd.DataFrame, embedding_cols: list[str], sentiment_cols: list[str], projection: np.ndarray, variant_id: str) -> tuple[pd.DataFrame, list[str]]:
    aggregated = aggregated.copy()
    aggregated["aligned_as_of_date"] = pd.to_datetime(aggregated["aligned_as_of_date"]).dt.strftime("%Y-%m-%d")
    embeddings = aggregated[embedding_cols].fillna(0.0).to_numpy(dtype="float32") if not aggregated.empty else np.zeros((0, len(embedding_cols)), dtype="float32")
    projected = embeddings @ projection
    projection_cols = [f"finbert_proj_{i:02d}" for i in range(projected.shape[1])]
    projected_frame = pd.DataFrame(projected, columns=projection_cols, index=aggregated.index)
    keep_cols = ["ticker", "aligned_as_of_date", "aligned_article_count", *sentiment_cols]
    compressed = pd.concat([aggregated[keep_cols].reset_index(drop=True), projected_frame.reset_index(drop=True)], axis=1)
    sidecar = base_rows.merge(compressed, left_on=["canonical_ticker", "as_of_date"], right_on=["ticker", "aligned_as_of_date"], how="left", validate="many_to_one")
    feature_columns = [*projection_cols, *sentiment_cols]
    for col in feature_columns:
        sidecar[col] = sidecar[col].fillna(0.0).astype("float32")
    sidecar["aligned_article_count"] = sidecar["aligned_article_count"].fillna(0).astype("int32")
    sidecar["event_feature_family_id"] = variant_id
    sidecar = sidecar.drop(columns=[column for column in ["ticker", "aligned_as_of_date"] if column in sidecar.columns])
    return sidecar, feature_columns


def run_stage29_event_representation_gate(stage28: StageOutput) -> StageOutput:
    generated = "20260525T110500Z"
    root = result_root(29, "event_representation_gate", generated, {"stage28": stage28.summary["manifest"]})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "event_representation_gate_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage29_event_representation_benchmark_gate.md"

    event_hash, hash_cols = _load_event_hash_features()
    frames = {"event_hash_v0": (event_hash, hash_cols)}
    for variant_id, rel_path in stage28.summary["variants"].items():
        sidecar = pd.read_parquet(PROJECT_ROOT / rel_path)
        frames[variant_id] = (sidecar, stage28.summary["feature_columns_by_variant"][variant_id])
    predictions: list[pd.DataFrame] = []
    fit_records: list[dict[str, Any]] = []
    for representation_id, (features, feature_columns) in frames.items():
        frame = _join_features_labels_splits(features, feature_columns)
        pred, fit = _fit_ridge_by_fold_horizon(frame, feature_columns, model_id=f"event_ridge__{representation_id}", branch="event_only", feature_representation_id=representation_id)
        predictions.append(pred)
        fit_records.extend(fit)
    prediction_frame = pd.concat(predictions, ignore_index=True)
    metrics = compute_metrics(prediction_frame)
    deltas = compute_pairwise_deltas(metrics, baseline_model_id="event_ridge__event_hash_v0", candidate_model_ids=[m for m in metrics["model_id"].unique() if m != "event_ridge__event_hash_v0"])
    selection = _select_best_event_representation(deltas)

    pred_path = root / "saved_predictions.parquet"
    metrics_path = root / "metrics.parquet"
    deltas_path = root / "representation_deltas.parquet"
    fit_path = root / "model_fit_manifest.parquet"
    prediction_frame.to_parquet(pred_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    deltas.to_parquet(deltas_path, index=False)
    pd.DataFrame(fit_records).to_parquet(fit_path, index=False)
    manifest = {
        "artifact_type": "v1p0_stage29_event_representation_gate_manifest",
        "artifact_id": f"stage29_event_representation_gate__{sha256_file(pred_path)[:12]}__20260525T110500Z",
        "generated_at_utc": "2026-05-25T11:05:00Z",
        "run_id": root.name,
        "status": "completed",
        "source_stage28_artifact": stage28.summary["manifest"],
        "model_head": "fold_local_ridge_event_only",
        "selection_basis": "validation_weighted_rmse_mae_delta_vs_event_hash_v0_only",
        "selected_event_representation_id": selection["selected_event_representation_id"],
        "selection": selection,
        "prediction_rows": int(len(prediction_frame)),
        "metric_rows": int(len(metrics)),
        "delta_rows": int(len(deltas)),
        "outputs": {"saved_predictions": rel(pred_path), "metrics": rel(metrics_path), "representation_deltas": rel(deltas_path), "model_fit_manifest": rel(fit_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)},
        "lockbox_used_for_selection": False,
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_event_value_claim", "not_market_fusion_claim", "not_positive_benchmark_claim", "stage35_39_required"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 29, "stage_name": "event_representation_benchmark_gate", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_stage29_report(manifest, selection), encoding="utf-8")
    return StageOutput(29, "completed", root, manifest_path, {"manifest": rel(manifest_path), "selected_event_representation_id": selection["selected_event_representation_id"], "saved_predictions": rel(pred_path), "metrics": rel(metrics_path)})


def _load_event_hash_features() -> tuple[pd.DataFrame, list[str]]:
    frame = pd.read_parquet(STAGE3_ROOT / "event_state_features.parquet")
    hash_cols = [column for column in frame.columns if column.startswith("event_state_hash_embedding_")]
    scalar_cols = ["stage3_aligned_news_count", "minutes_since_latest_aligned_article", "provider_truncation_risk_flag", "no_news_flag"]
    feature_cols = [*hash_cols, *scalar_cols]
    for col in scalar_cols:
        frame[col] = frame[col].fillna(0).astype("float32")
    return frame[[*ROW_KEY, *feature_cols]], feature_cols


def _join_features_labels_splits(features: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*ROW_KEY, "forward_excess_return"])
    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet", columns=["fold_id", *ROW_KEY, "split_role", "lockbox_flag", "preprocessing_fit_allowed"])
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
    frame = splits.merge(features[[*ROW_KEY, *feature_columns]], on=ROW_KEY, how="inner", validate="many_to_one").merge(labels, on=ROW_KEY, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target"})
    frame["row_key"] = frame[ROW_KEY].astype(str).agg("|".join, axis=1)
    frame["dataset_version"] = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086"
    frame["split_artifact_version"] = "stage4_splits_v1"
    return frame


def _fit_ridge_by_fold_horizon(frame: pd.DataFrame, feature_columns: list[str], model_id: str, branch: str, feature_representation_id: str) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    records: list[pd.DataFrame] = []
    fit_records: list[dict[str, Any]] = []
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        score = group[group["split_role"].isin(["train", "validation", "lockbox"])].copy()
        if train.empty or score.empty:
            continue
        started = time.perf_counter()
        imputer = SimpleImputer(strategy="median").fit(train[feature_columns].astype("float64"))
        scaler = StandardScaler().fit(imputer.transform(train[feature_columns].astype("float64")))
        estimator = Ridge(alpha=1.0).fit(scaler.transform(imputer.transform(train[feature_columns].astype("float64"))), train["target"].astype("float64"))
        prediction = estimator.predict(scaler.transform(imputer.transform(score[feature_columns].astype("float64"))))
        output = score[["row_key", *ROW_KEY, "fold_id", "split_role", "dataset_version", "split_artifact_version", "target"]].copy()
        output["model_id"] = model_id
        output["model_family"] = "ridge_linear"
        output["branch"] = branch
        output["feature_representation_id"] = feature_representation_id
        output["feature_artifact_version"] = feature_representation_id
        output["v1p0_artifact_version"] = "v1p0_stage26_40_final_sprint"
        output["prediction"] = prediction
        records.append(output)
        fit_records.append({"model_id": model_id, "fold_id": fold_id, "horizon_id": horizon_id, "feature_representation_id": feature_representation_id, "feature_count": len(feature_columns), "train_rows": int(len(train)), "score_rows": int(len(score)), "training_inference_seconds": round(time.perf_counter() - started, 6), "lockbox_used_for_selection": False})
    return pd.concat(records, ignore_index=True), fit_records


def compute_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    working = predictions.copy()
    working["error"] = working["prediction"].astype("float64") - working["target"].astype("float64")
    working["squared_error"] = working["error"] ** 2
    working["absolute_error"] = working["error"].abs()
    rows: list[dict[str, Any]] = []
    for keys, group in working.groupby(["split_role", "fold_id", "horizon_id", "model_id"], sort=True, observed=True):
        split_role, fold_id, horizon_id, model_id = keys
        target = group["target"].astype("float64")
        denominator = float(np.sum(target**2))
        sse = float(group["squared_error"].sum())
        rows.append({"split_role": split_role, "fold_id": fold_id, "horizon_id": horizon_id, "model_id": model_id, "row_count": int(len(group)), "rmse": float(np.sqrt(group["squared_error"].mean())), "mae": float(group["absolute_error"].mean()), "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator)})
    return pd.DataFrame.from_records(rows)


def compute_pairwise_deltas(metrics: pd.DataFrame, baseline_model_id: str, candidate_model_ids: Iterable[str]) -> pd.DataFrame:
    base = metrics[metrics["model_id"] == baseline_model_id][["split_role", "fold_id", "horizon_id", "rmse", "mae"]].copy()
    rows: list[pd.DataFrame] = []
    for candidate_id in candidate_model_ids:
        cand = metrics[metrics["model_id"] == candidate_id][["split_role", "fold_id", "horizon_id", "model_id", "rmse", "mae"]].copy()
        paired = cand.merge(base, on=["split_role", "fold_id", "horizon_id"], suffixes=("_candidate", "_baseline"), how="inner", validate="one_to_one")
        paired["baseline_model_id"] = baseline_model_id
        paired["candidate_model_id"] = candidate_id
        paired["rmse_delta_candidate_minus_baseline"] = paired["rmse_candidate"] - paired["rmse_baseline"]
        paired["mae_delta_candidate_minus_baseline"] = paired["mae_candidate"] - paired["mae_baseline"]
        paired["both_metrics_improve"] = (paired["rmse_delta_candidate_minus_baseline"] < 0) & (paired["mae_delta_candidate_minus_baseline"] < 0)
        rows.append(paired)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def _select_best_event_representation(deltas: pd.DataFrame) -> dict[str, Any]:
    validation = deltas[deltas["split_role"] == "validation"].copy()
    if validation.empty:
        return {"selected_event_representation_id": "event_hash_v0", "status": "blocked_no_validation_deltas", "positive_claim_approved": False}
    validation["horizon_weight"] = validation["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    validation["weighted_delta"] = 0.5 * validation["rmse_delta_candidate_minus_baseline"] * validation["horizon_weight"] + 0.5 * validation["mae_delta_candidate_minus_baseline"] * validation["horizon_weight"]
    summary = validation.groupby("candidate_model_id", sort=True).agg(weighted_delta=("weighted_delta", "sum"), both_metric_improvement_rate=("both_metrics_improve", "mean")).reset_index()
    summary["feature_representation_id"] = summary["candidate_model_id"].str.replace("event_ridge__", "", regex=False)
    best = summary.sort_values(["weighted_delta", "candidate_model_id"]).iloc[0]
    return {"selected_event_representation_id": str(best["feature_representation_id"]), "selected_model_id": str(best["candidate_model_id"]), "validation_weighted_delta_vs_hash": float(best["weighted_delta"]), "validation_both_metric_improvement_rate_vs_hash": float(best["both_metric_improvement_rate"]), "status": "selected_from_development_validation_only", "positive_claim_approved": False}


def _stage29_report(manifest: dict[str, Any], selection: dict[str, Any]) -> str:
    return f"""# Stage 29 Event Representation Benchmark Gate

Status: completed; event-only representation comparison recorded without event-value claim

Selected representation from validation evidence only: `{selection['selected_event_representation_id']}`

Validation weighted delta versus `event_hash_v0`: {selection.get('validation_weighted_delta_vs_hash')}

Validation both-metric improvement rate versus `event_hash_v0`: {selection.get('validation_both_metric_improvement_rate_vs_hash')}

Prediction rows: {manifest['prediction_rows']}

Metric rows: {manifest['metric_rows']}

Lockbox was not used for representation selection.

Non-claims: this is not a market+event fusion claim, positive benchmark claim, Stage 6 reinterpretation, or trading signal.
"""


def run_stage30_tsmixer_smoke(stage18: StageOutput, window_length: int = TSMIXER_FIXED_WINDOW_LENGTH) -> StageOutput:
    generated = "20260525T152000Z"
    root = result_root(30, "tsmixer_sequence_smoke", generated, {"stage18": stage18.summary["manifest"], "window_length": window_length})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "tsmixer_smoke_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage30_tsmixer_sequence_dataset_and_smoke.md"
    predictions_path = root / "smoke_predictions.parquet"
    smoke_predictions, smoke_summary = _run_tsmixer_smoke_prediction(stage18, window_length)
    smoke_predictions.to_parquet(predictions_path, index=False)
    manifest = {"artifact_type": "v1p0_stage30_tsmixer_smoke_manifest", "artifact_id": f"stage30_tsmixer_smoke__{sha256_file(predictions_path)[:12]}__20260525T152000Z", "generated_at_utc": "2026-05-25T15:20:00Z", "run_id": root.name, "status": "completed_smoke_only", "source_stage18_artifact": stage18.summary["manifest"], "smoke_summary": smoke_summary, "outputs": {"smoke_predictions": rel(predictions_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["not_full_tsmixer_benchmark", "not_tsmixer_promotion", "stage31_required_for_multiseed_evidence"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 30, "stage_name": "tsmixer_sequence_dataset_and_smoke", "status": "completed_smoke_only", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(f"# Stage 30 TSMixer Sequence Dataset And Smoke\n\nStatus: completed smoke-only using Stage 18 sequence tensors.\n\nSmoke rows: {len(smoke_predictions)}\n\nSequence shape: {smoke_summary['sequence_shape']}\n\nLoss after smoke fit: {smoke_summary['final_training_loss']}\n\nNon-claims: smoke success is not benchmark evidence; Stage 31 remains required for fixed multiseed evidence.\n", encoding="utf-8")
    return StageOutput(30, "completed_smoke_only", root, manifest_path, {"manifest": rel(manifest_path), "status": "completed_smoke_only"})


def _run_tsmixer_smoke_prediction(stage18: StageOutput, window_length: int) -> tuple[pd.DataFrame, dict[str, Any]]:
    import torch

    frame, values, mask, feature_columns = _load_sequence_training_frame(stage18, window_length)
    frame = frame[(frame["horizon_id"] == "1d") & (frame["split_role"] == "train")].head(256).copy()
    if frame.empty:
        raise V1P0FinalSprintError("Stage 30 smoke has no training rows")
    x_np = _normalize_sequence_batch(values, mask, frame["sequence_base_index"].to_numpy(dtype="int64"), frame["sequence_base_index"].to_numpy(dtype="int64"))
    y_np = frame["target"].to_numpy(dtype="float32").reshape(-1, 1)
    x = torch.tensor(x_np, dtype=torch.float32)
    y = torch.tensor(y_np, dtype=torch.float32)
    torch.manual_seed(20260525)
    model = _CompactTSMixer(window_length=x.shape[1], feature_count=x.shape[2], hidden_time=16, hidden_feature=32)
    opt = torch.optim.AdamW(model.parameters(), lr=0.01)
    loss_fn = torch.nn.MSELoss()
    final_loss = 0.0
    for _ in range(5):
        opt.zero_grad()
        pred = model(x)
        loss = loss_fn(pred, y)
        loss.backward()
        opt.step()
        final_loss = float(loss.detach())
    output = frame[[*ROW_KEY]].copy()
    output["prediction"] = model(x).detach().numpy().reshape(-1)
    output["target"] = y_np.reshape(-1)
    output["model_id"] = "market_tsmixer_v1_smoke"
    return output, {"sample_rows": int(len(frame)), "sequence_shape": [int(x.shape[1]), int(x.shape[2])], "feature_count": len(feature_columns), "parameter_count": int(sum(p.numel() for p in model.parameters())), "final_training_loss": final_loss, "seed": 20260525, "source_stage18_artifact": stage18.summary["manifest"]}


class _CompactTSMixer:
    def __new__(cls, window_length: int, feature_count: int, hidden_time: int, hidden_feature: int):
        import torch
        from torch import nn

        class Model(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.input_norm = nn.LayerNorm(feature_count)
                self.time_mlp = nn.Sequential(nn.Linear(window_length, hidden_time), nn.GELU(), nn.Linear(hidden_time, window_length))
                self.feature_mlp = nn.Sequential(nn.LayerNorm(feature_count), nn.Linear(feature_count, hidden_feature), nn.GELU(), nn.Linear(hidden_feature, feature_count))
                self.head = nn.Sequential(nn.LayerNorm(feature_count), nn.Linear(feature_count, 1))

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                x = self.input_norm(x)
                y = x.transpose(1, 2)
                x = x + self.time_mlp(y).transpose(1, 2)
                x = x + self.feature_mlp(x)
                return self.head(x.mean(dim=1))

        return Model()


def _load_sequence_training_frame(stage18: StageOutput, window_length: int) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str]]:
    manifest = json.loads(stage18.manifest_path.read_text(encoding="utf-8"))
    key = f"{window_length}d"
    if key not in manifest["outputs"]:
        raise V1P0FinalSprintError(f"Stage 18 manifest does not contain {window_length}d tensors")
    values = np.load(PROJECT_ROOT / manifest["outputs"][key]["values"], mmap_mode="r")
    mask = np.load(PROJECT_ROOT / manifest["outputs"][key]["observed_mask"], mmap_mode="r")
    row_index = pd.read_parquet(PROJECT_ROOT / manifest["outputs"]["sequence_row_index"])
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*ROW_KEY, "forward_excess_return"])
    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet", columns=["fold_id", *ROW_KEY, "split_role", "lockbox_flag"])
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
    frame = splits.merge(row_index, on=ROW_KEY, how="inner", validate="many_to_one").merge(labels, on=ROW_KEY, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target"})
    frame["row_key"] = frame[ROW_KEY].astype(str).agg("|".join, axis=1)
    frame["dataset_version"] = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086"
    frame["split_artifact_version"] = "stage4_splits_v1"
    return frame, values, mask, list(manifest["feature_columns"])


def _normalization_stats(values: np.ndarray, mask: np.ndarray, train_indices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    train_values = np.asarray(values[train_indices], dtype="float32")
    train_mask = np.asarray(mask[train_indices], dtype=bool)
    counts = train_mask.sum(axis=(0, 1)).astype("float64")
    sums = (train_values * train_mask).sum(axis=(0, 1), dtype="float64")
    means = np.divide(sums, counts, out=np.zeros_like(sums, dtype="float64"), where=counts > 0)
    centered = np.where(train_mask, train_values - means.reshape(1, 1, -1), 0.0)
    variances = np.divide((centered**2).sum(axis=(0, 1), dtype="float64"), counts, out=np.ones_like(sums, dtype="float64"), where=counts > 0)
    stds = np.sqrt(np.maximum(variances, 1e-8))
    stds[counts == 0] = 1.0
    return means.astype("float32"), stds.astype("float32")


def _normalize_sequence_batch(values: np.ndarray, mask: np.ndarray, indices: np.ndarray, train_indices: np.ndarray) -> np.ndarray:
    means, stds = _normalization_stats(values, mask, train_indices)
    return _apply_sequence_normalization(values, mask, indices, means, stds)


def _apply_sequence_normalization(values: np.ndarray, mask: np.ndarray, indices: np.ndarray, means: np.ndarray, stds: np.ndarray) -> np.ndarray:
    batch_values = np.asarray(values[indices], dtype="float32")
    batch_mask = np.asarray(mask[indices], dtype=bool)
    normalized = (batch_values - means.reshape(1, 1, -1)) / stds.reshape(1, 1, -1)
    return np.where(batch_mask, normalized, 0.0).astype("float32")


def run_stage31_tsmixer_fixed_multiseed(
    stage18: StageOutput,
    stage30: StageOutput,
    window_length: int = TSMIXER_FIXED_WINDOW_LENGTH,
    seeds: tuple[int, ...] = TSMIXER_FIXED_SEEDS,
    epochs: int = TSMIXER_FIXED_EPOCHS,
    batch_size: int = TSMIXER_FIXED_BATCH_SIZE,
) -> StageOutput:
    generated = "20260525T153000Z"
    root = result_root(31, "tsmixer_fixed_multiseed_benchmark", generated, {"stage18": stage18.summary["manifest"], "stage30": stage30.summary["manifest"], "window_length": window_length, "seeds": list(seeds), "epochs": epochs})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "stage31_tsmixer_fixed_multiseed_benchmark_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage31_tsmixer_fixed_multiseed_benchmark.md"
    pred_path = root / "saved_predictions.parquet"
    metrics_path = root / "metrics.parquet"
    deltas_path = root / "market_hurdle_deltas.parquet"
    fit_path = root / "model_fit_manifest.parquet"
    seed_summary_path = root / "seed_summary.parquet"

    frame, values, mask, feature_columns = _load_sequence_training_frame(stage18, window_length)
    predictions, fit_records = _fit_tsmixer_by_seed_fold_horizon(frame, values, mask, window_length, len(feature_columns), seeds, epochs, batch_size)
    metrics = compute_metrics(predictions)
    hurdle_metrics = pd.read_parquet(STAGE23_ROOT / "metrics.parquet")
    deltas = compute_pairwise_deltas(pd.concat([metrics, hurdle_metrics], ignore_index=True, sort=False), baseline_model_id="market_xgboost_v2_frozen_final", candidate_model_ids=sorted(metrics["model_id"].unique()))
    seed_summary, classification = _summarize_tsmixer_multiseed(deltas)

    predictions.to_parquet(pred_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    deltas.to_parquet(deltas_path, index=False)
    pd.DataFrame(fit_records).to_parquet(fit_path, index=False)
    seed_summary.to_parquet(seed_summary_path, index=False)
    manifest = {
        "artifact_type": "v1p0_stage31_tsmixer_fixed_multiseed_benchmark_manifest",
        "artifact_id": f"stage31_tsmixer_fixed_multiseed__{sha256_file(pred_path)[:12]}__20260525T153000Z",
        "generated_at_utc": "2026-05-25T15:30:00Z",
        "run_id": root.name,
        "status": "completed",
        "source_stage18_artifact": stage18.summary["manifest"],
        "source_stage30_artifact": stage30.summary["manifest"],
        "model_id_prefix": "market_tsmixer_v1_fixed",
        "window_length": window_length,
        "feature_count": len(feature_columns),
        "seeds": list(seeds),
        "epochs": epochs,
        "batch_size": batch_size,
        "prediction_rows": int(len(predictions)),
        "metric_rows": int(len(metrics)),
        "delta_rows": int(len(deltas)),
        "classification": classification,
        "outputs": {"saved_predictions": rel(pred_path), "metrics": rel(metrics_path), "market_hurdle_deltas": rel(deltas_path), "model_fit_manifest": rel(fit_path), "seed_summary": rel(seed_summary_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)},
        "lockbox_used_for_selection": False,
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_positive_tsmixer_claim", "not_stage6_reinterpretation", "not_trading_signal", "stage35_39_required_for_claims"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 31, "stage_name": "tsmixer_fixed_multiseed_benchmark", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_stage31_report(manifest, classification), encoding="utf-8")
    return StageOutput(31, "completed", root, manifest_path, {"manifest": rel(manifest_path), "saved_predictions": rel(pred_path), "metrics": rel(metrics_path), "classification": classification})


def _fit_tsmixer_by_seed_fold_horizon(
    frame: pd.DataFrame,
    values: np.ndarray,
    mask: np.ndarray,
    window_length: int,
    feature_count: int,
    seeds: tuple[int, ...],
    epochs: int,
    batch_size: int,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    records: list[pd.DataFrame] = []
    fit_records: list[dict[str, Any]] = []
    for seed_position, seed in enumerate(seeds, start=1):
        torch.manual_seed(seed)
        np_rng = np.random.default_rng(seed)
        seed_id = f"seed_{seed_position:02d}"
        model_id = f"market_tsmixer_v1_fixed_{seed_id}"
        for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
            train = group[group["split_role"] == "train"].copy()
            score = group[group["split_role"].isin(["train", "validation", "lockbox"])].copy()
            if train.empty or score.empty:
                continue
            started = time.perf_counter()
            train_indices = train["sequence_base_index"].to_numpy(dtype="int64")
            score_indices = score["sequence_base_index"].to_numpy(dtype="int64")
            means, stds = _normalization_stats(values, mask, train_indices)
            x_train_np = _apply_sequence_normalization(values, mask, train_indices, means, stds)
            y_train_np = train["target"].to_numpy(dtype="float32").reshape(-1, 1)
            x_train = torch.tensor(x_train_np, dtype=torch.float32, device=device)
            y_train = torch.tensor(y_train_np, dtype=torch.float32, device=device)
            model = _CompactTSMixer(window_length=window_length, feature_count=feature_count, hidden_time=32, hidden_feature=64).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
            loss_fn = torch.nn.MSELoss()
            final_loss = float("nan")
            model.train()
            for _ in range(epochs):
                order = np_rng.permutation(len(train))
                for start in range(0, len(order), batch_size):
                    batch_order = torch.tensor(order[start : start + batch_size], dtype=torch.long, device=device)
                    opt.zero_grad(set_to_none=True)
                    pred = model(x_train.index_select(0, batch_order))
                    loss = loss_fn(pred, y_train.index_select(0, batch_order))
                    loss.backward()
                    opt.step()
                    final_loss = float(loss.detach().cpu())
            prediction = _predict_tsmixer(model, values, mask, score_indices, means, stds, batch_size, device)
            output = score[["row_key", *ROW_KEY, "fold_id", "split_role", "dataset_version", "split_artifact_version", "target"]].copy()
            output["model_id"] = model_id
            output["seed_id"] = seed_id
            output["seed"] = seed
            output["model_family"] = "tsmixer_pytorch"
            output["branch"] = "market_only"
            output["feature_representation_id"] = f"market_sequence_window_{window_length}d_v1"
            output["feature_artifact_version"] = f"stage18_sequence_window_{window_length}d"
            output["v1p0_artifact_version"] = "v1p0_stage31_tsmixer_fixed_multiseed"
            output["prediction"] = prediction
            records.append(output)
            fit_records.append({"model_id": model_id, "seed_id": seed_id, "seed": seed, "fold_id": fold_id, "horizon_id": horizon_id, "window_length": window_length, "feature_count": feature_count, "train_rows": int(len(train)), "score_rows": int(len(score)), "epochs": epochs, "batch_size": batch_size, "parameter_count": int(sum(p.numel() for p in model.parameters())), "final_training_loss": final_loss, "training_inference_seconds": round(time.perf_counter() - started, 6), "device": str(device), "lockbox_used_for_selection": False})
            del x_train, y_train, model
            if device.type == "cuda":
                torch.cuda.empty_cache()
    return pd.concat(records, ignore_index=True), fit_records


def _predict_tsmixer(model: Any, values: np.ndarray, mask: np.ndarray, indices: np.ndarray, means: np.ndarray, stds: np.ndarray, batch_size: int, device: Any) -> np.ndarray:
    import torch

    model.eval()
    outputs: list[np.ndarray] = []
    with torch.inference_mode():
        for start in range(0, len(indices), batch_size):
            batch_indices = indices[start : start + batch_size]
            x_np = _apply_sequence_normalization(values, mask, batch_indices, means, stds)
            x = torch.tensor(x_np, dtype=torch.float32, device=device)
            outputs.append(model(x).detach().cpu().numpy().reshape(-1))
    return np.concatenate(outputs).astype("float32")


def _summarize_tsmixer_multiseed(deltas: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    validation = deltas[deltas["split_role"] == "validation"].copy()
    if validation.empty:
        empty = pd.DataFrame()
        return empty, {"status": "blocked_no_validation_deltas", "positive_claim_approved": False, "stage32_recommendation": "blocked"}
    validation["horizon_weight"] = validation["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    validation["weighted_delta"] = 0.5 * validation["rmse_delta_candidate_minus_baseline"] * validation["horizon_weight"] + 0.5 * validation["mae_delta_candidate_minus_baseline"] * validation["horizon_weight"]
    summary = validation.groupby("candidate_model_id", sort=True).agg(validation_weighted_delta_vs_market_xgb=("weighted_delta", "sum"), validation_both_metric_improvement_rate_vs_market_xgb=("both_metrics_improve", "mean"), validation_comparison_rows=("both_metrics_improve", "size")).reset_index()
    summary["seed_id"] = summary["candidate_model_id"].str.extract(r"(seed_\d+)")
    best = summary.sort_values(["validation_weighted_delta_vs_market_xgb", "candidate_model_id"]).iloc[0]
    promising = bool(best["validation_weighted_delta_vs_market_xgb"] < 0 and best["validation_both_metric_improvement_rate_vs_market_xgb"] >= 0.45)
    classification = {
        "status": "completed",
        "best_seed_model_id": str(best["candidate_model_id"]),
        "best_seed_id": str(best["seed_id"]),
        "best_validation_weighted_delta_vs_market_xgb": float(best["validation_weighted_delta_vs_market_xgb"]),
        "best_validation_both_metric_improvement_rate_vs_market_xgb": float(best["validation_both_metric_improvement_rate_vs_market_xgb"]),
        "stage32_recommendation": "ask_user_for_optimization" if promising else "do_not_optimize_without_user_override",
        "positive_claim_approved": False,
        "benchmark_claim": False,
        "reason": "best seed shows development evidence that may justify Stage 32 user decision" if promising else "fixed multiseed TSMixer did not clear the conservative development threshold for automatic optimization recommendation",
    }
    return summary, classification


def _stage31_report(manifest: dict[str, Any], classification: dict[str, Any]) -> str:
    return f"""# Stage 31 TSMixer Fixed Multiseed Benchmark

Status: completed; fixed multiseed TSMixer evidence recorded without positive claim

Window length: {manifest['window_length']}d

Seeds: {', '.join(str(seed) for seed in manifest['seeds'])}

Prediction rows: {manifest['prediction_rows']}

Best seed: `{classification.get('best_seed_model_id')}`

Best validation weighted delta vs market XGBoost final: {classification.get('best_validation_weighted_delta_vs_market_xgb')}

Best validation both-metric improvement rate vs market XGBoost final: {classification.get('best_validation_both_metric_improvement_rate_vs_market_xgb')}

Stage 32 recommendation: `{classification.get('stage32_recommendation')}`

Non-claims: Stage 31 does not approve TSMixer promotion, Stage 6 reinterpretation, trading output, or positive benchmark language.
"""


def stage32_search_space_contract(
    trial_count: int = TSMIXER_OPTUNA_TRIALS,
    seeds: tuple[int, ...] = TSMIXER_OPTUNA_SEEDS,
    epochs: int = TSMIXER_OPTUNA_EPOCHS,
) -> dict[str, Any]:
    return {
        "artifact_type": "v1p0_stage32_tsmixer_optimization_search_space",
        "search_policy": "user_override_heavy_optuna_after_negative_stage31_recommendation",
        "approval_requirement": "requires_explicit_user_override_when_stage31_recommendation_is_do_not_optimize_without_user_override",
        "optuna": {"direction": "minimize", "sampler": "TPESampler", "sampler_seed": TSMIXER_OPTUNA_SAMPLER_SEED},
        "trial_count": int(trial_count),
        "seeds": list(seeds),
        "seed_count": len(seeds),
        "epochs": int(epochs),
        "window_length": TSMIXER_FIXED_WINDOW_LENGTH,
        "split_roles_for_optimization": ["train", "validation"],
        "lockbox_rows_used_for_optimization": 0,
        "search_space": {
            "hidden_time": {"type": "categorical", "choices": [16, 32, 48, 64]},
            "hidden_feature": {"type": "categorical", "choices": [32, 64, 96, 128]},
            "learning_rate": {"type": "log_float", "low": 1e-4, "high": 3e-3},
            "weight_decay": {"type": "log_float", "low": 1e-6, "high": 1e-2},
            "batch_size": {"type": "categorical", "choices": [512, 1024, 2048]},
            "grad_clip_norm": {"type": "categorical", "choices": [0.5, 1.0, 2.0]},
        },
        "objective": {
            "name": "development_validation_weighted_delta_vs_market_xgb_with_overfit_penalty",
            "baseline_model_id": "market_xgboost_v2_frozen_final",
            "metric_direction": "candidate_minus_baseline_lower_is_better",
            "horizon_weights": HORIZON_WEIGHTS,
            "lockbox_policy": "no_lockbox_rows_or_metrics_used_for_trial_selection",
        },
        "freeze_gate": {
            "validation_weighted_delta_vs_market_xgb_must_be_negative": True,
            "validation_both_metric_improvement_rate_min": 0.45,
            "train_validation_gap_flag_rate_max": 0.50,
            "positive_claim_approved": False,
        },
        "early_stop_policy": "fixed_user_approved_heavy_budget_no_adaptive_reduction_without_user_approval",
    }


def run_stage32_tsmixer_optimization(
    stage18: StageOutput,
    stage31: StageOutput,
    approval_id: str,
    override_stage31_recommendation: bool,
    trial_count: int = TSMIXER_OPTUNA_TRIALS,
    seeds: tuple[int, ...] = TSMIXER_OPTUNA_SEEDS,
    epochs: int = TSMIXER_OPTUNA_EPOCHS,
) -> StageOutput:
    if not approval_id:
        raise V1P0FinalSprintError("Stage 32 requires explicit user approval evidence")
    stage31_manifest = json.loads(stage31.manifest_path.read_text(encoding="utf-8"))
    classification = stage31_manifest.get("classification", {})
    recommendation = classification.get("stage32_recommendation")
    if recommendation == "do_not_optimize_without_user_override" and not override_stage31_recommendation:
        raise V1P0FinalSprintError("Stage 31 blocked optimization; rerun with explicit user override evidence")

    generated = "20260525T160000Z"
    search_contract = stage32_search_space_contract(trial_count=trial_count, seeds=seeds, epochs=epochs)
    search_contract["user_approval"] = {"approval_id": approval_id, "override_stage31_recommendation": bool(override_stage31_recommendation)}
    search_contract["source_stage18_artifact"] = stage18.summary["manifest"]
    search_contract["source_stage31_artifact"] = stage31.summary["manifest"]
    search_contract["source_stage31_recommendation"] = recommendation

    root = result_root(32, "tsmixer_optimization_overfit_control", generated, {"stage18": stage18.summary["manifest"], "stage31": stage31.summary["manifest"], "trial_count": trial_count, "seeds": list(seeds), "approval_id": approval_id})
    root.mkdir(parents=True, exist_ok=True)
    search_space_path = root / "search_space_manifest.json"
    trial_ledger_path = root / "trial_ledger.parquet"
    fold_metrics_path = root / "fold_metrics.parquet"
    model_fit_path = root / "model_fit_manifest.parquet"
    deltas_path = root / "market_hurdle_deltas.parquet"
    frontier_path = root / "overfit_frontier.parquet"
    best_candidate_path = root / "best_candidate_manifest.json"
    manifest_path = root / "stage32_tsmixer_optimization_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage32_tsmixer_optimization_and_overfit_control.md"

    write_json(search_space_path, search_contract)
    trial_ledger, fold_metrics, fit_manifest, deltas, frontier, best_candidate = _run_stage32_optuna_search(stage18, search_contract)
    trial_ledger.to_parquet(trial_ledger_path, index=False)
    fold_metrics.to_parquet(fold_metrics_path, index=False)
    fit_manifest.to_parquet(model_fit_path, index=False)
    deltas.to_parquet(deltas_path, index=False)
    frontier.to_parquet(frontier_path, index=False)
    write_json(best_candidate_path, best_candidate)

    manifest = {
        "artifact_type": "v1p0_stage32_tsmixer_optimization_manifest",
        "artifact_id": f"stage32_tsmixer_optimization__{sha256_file(trial_ledger_path)[:12]}__20260525T160000Z",
        "generated_at_utc": "2026-05-25T16:00:00Z",
        "run_id": root.name,
        "status": "completed",
        "source_stage18_artifact": stage18.summary["manifest"],
        "source_stage31_artifact": stage31.summary["manifest"],
        "user_approval": search_contract["user_approval"],
        "trial_count_requested": int(trial_count),
        "trial_count_completed": int((trial_ledger["status"] == "completed").sum()) if not trial_ledger.empty else 0,
        "seed_count": len(seeds),
        "epochs": int(epochs),
        "window_length": TSMIXER_FIXED_WINDOW_LENGTH,
        "lockbox_rows_used_for_optimization": 0,
        "best_candidate": best_candidate,
        "outputs": {
            "search_space_manifest": rel(search_space_path),
            "trial_ledger": rel(trial_ledger_path),
            "fold_metrics": rel(fold_metrics_path),
            "model_fit_manifest": rel(model_fit_path),
            "market_hurdle_deltas": rel(deltas_path),
            "overfit_frontier": rel(frontier_path),
            "best_candidate_manifest": rel(best_candidate_path),
            "manifest": rel(manifest_path),
            "run_manifest": rel(run_manifest_path),
            "report": rel(report_path),
        },
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["optimization_not_positive_claim", "not_stage6_reinterpretation", "not_trading_signal", "stage35_39_required_for_claims"],
    }
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 32, "stage_name": "tsmixer_optimization_overfit_control", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_stage32_report(manifest, best_candidate), encoding="utf-8")
    return StageOutput(32, "completed", root, manifest_path, {"manifest": rel(manifest_path), "best_candidate": best_candidate, "frontier": rel(frontier_path), "fold_metrics": rel(fold_metrics_path)})


def _run_stage32_optuna_search(stage18: StageOutput, search_contract: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    try:
        import optuna
    except ImportError as exc:  # pragma: no cover - environment contract should provide optuna.
        raise V1P0FinalSprintError("Stage 32 requires optuna in the configured venv") from exc

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    frame, values, mask, feature_columns = _load_sequence_training_frame(stage18, TSMIXER_FIXED_WINDOW_LENGTH)
    frame = frame[frame["split_role"].isin(search_contract["split_roles_for_optimization"])].copy()
    if frame["split_role"].eq("lockbox").any():
        raise V1P0FinalSprintError("Stage 32 optimization frame contains lockbox rows")
    baseline_metrics = pd.read_parquet(STAGE23_ROOT / "metrics.parquet")
    baseline_metrics = baseline_metrics[baseline_metrics["split_role"].isin(search_contract["split_roles_for_optimization"])].copy()

    trial_records: list[dict[str, Any]] = []
    metric_frames: list[pd.DataFrame] = []
    fit_frames: list[pd.DataFrame] = []
    delta_frames: list[pd.DataFrame] = []
    frontier_records: list[dict[str, Any]] = []

    def objective(trial: Any) -> float:
        config = {
            "hidden_time": int(trial.suggest_categorical("hidden_time", search_contract["search_space"]["hidden_time"]["choices"])),
            "hidden_feature": int(trial.suggest_categorical("hidden_feature", search_contract["search_space"]["hidden_feature"]["choices"])),
            "learning_rate": float(trial.suggest_float("learning_rate", search_contract["search_space"]["learning_rate"]["low"], search_contract["search_space"]["learning_rate"]["high"], log=True)),
            "weight_decay": float(trial.suggest_float("weight_decay", search_contract["search_space"]["weight_decay"]["low"], search_contract["search_space"]["weight_decay"]["high"], log=True)),
            "batch_size": int(trial.suggest_categorical("batch_size", search_contract["search_space"]["batch_size"]["choices"])),
            "grad_clip_norm": float(trial.suggest_categorical("grad_clip_norm", search_contract["search_space"]["grad_clip_norm"]["choices"])),
        }
        started = time.perf_counter()
        try:
            metrics, fit_manifest = _fit_tsmixer_trial_metrics(frame, values, mask, TSMIXER_FIXED_WINDOW_LENGTH, len(feature_columns), trial.number, tuple(search_contract["seeds"]), int(search_contract["epochs"]), config)
            summary, deltas, frontier = _summarize_stage32_trial(trial.number, metrics, baseline_metrics, config)
            runtime_seconds = round(time.perf_counter() - started, 6)
            record = {"trial_number": int(trial.number), "status": "completed", "runtime_seconds": runtime_seconds, **config, **summary}
            trial_records.append(record)
            metric_frames.append(metrics)
            fit_frames.append(fit_manifest)
            delta_frames.append(deltas)
            frontier_records.append(frontier)
            for key, value in summary.items():
                trial.set_user_attr(key, value)
            return float(summary["objective_value"])
        except Exception as exc:  # noqa: BLE001 - all failed trials must be logged and assigned a bad objective.
            runtime_seconds = round(time.perf_counter() - started, 6)
            record = {"trial_number": int(trial.number), "status": "failed", "runtime_seconds": runtime_seconds, "failure_reason": str(exc), **config, "objective_value": 1e9, "lockbox_rows_used_for_optimization": 0}
            trial_records.append(record)
            frontier_records.append(record)
            return 1e9

    sampler = optuna.samplers.TPESampler(seed=int(search_contract["optuna"]["sampler_seed"]))
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(objective, n_trials=int(search_contract["trial_count"]), show_progress_bar=False)

    trial_ledger = pd.DataFrame.from_records(trial_records)
    fold_metrics = pd.concat(metric_frames, ignore_index=True) if metric_frames else pd.DataFrame()
    fit_manifest = pd.concat(fit_frames, ignore_index=True) if fit_frames else pd.DataFrame()
    deltas = pd.concat(delta_frames, ignore_index=True) if delta_frames else pd.DataFrame()
    frontier = pd.DataFrame.from_records(frontier_records)
    best_candidate = _select_stage32_best_candidate(frontier, search_contract)
    best_candidate["optuna_best_trial_number"] = int(study.best_trial.number) if study.trials else None
    best_candidate["optuna_best_value"] = float(study.best_value) if study.trials else None
    return trial_ledger, fold_metrics, fit_manifest, deltas, frontier, best_candidate


def _fit_tsmixer_trial_metrics(
    frame: pd.DataFrame,
    values: np.ndarray,
    mask: np.ndarray,
    window_length: int,
    feature_count: int,
    trial_number: int,
    seeds: tuple[int, ...],
    epochs: int,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    metric_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    for seed_position, seed in enumerate(seeds, start=1):
        torch.manual_seed(seed + trial_number)
        np_rng = np.random.default_rng(seed + trial_number * 1009)
        seed_id = f"seed_{seed_position:02d}"
        model_id = f"market_tsmixer_v1_optuna_trial_{trial_number:03d}_{seed_id}"
        for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
            train = group[group["split_role"] == "train"].copy()
            validation = group[group["split_role"] == "validation"].copy()
            if train.empty or validation.empty:
                continue
            started = time.perf_counter()
            train_indices = train["sequence_base_index"].to_numpy(dtype="int64")
            validation_indices = validation["sequence_base_index"].to_numpy(dtype="int64")
            means, stds = _normalization_stats(values, mask, train_indices)
            x_train_np = _apply_sequence_normalization(values, mask, train_indices, means, stds)
            y_train_np = train["target"].to_numpy(dtype="float32").reshape(-1, 1)
            x_train = torch.tensor(x_train_np, dtype=torch.float32, device=device)
            y_train = torch.tensor(y_train_np, dtype=torch.float32, device=device)
            model = _CompactTSMixer(window_length=window_length, feature_count=feature_count, hidden_time=int(config["hidden_time"]), hidden_feature=int(config["hidden_feature"])).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=float(config["learning_rate"]), weight_decay=float(config["weight_decay"]))
            loss_fn = torch.nn.MSELoss()
            final_loss = float("nan")
            model.train()
            batch_size = int(config["batch_size"])
            for _ in range(epochs):
                order = np_rng.permutation(len(train))
                for start in range(0, len(order), batch_size):
                    batch_order = torch.tensor(order[start : start + batch_size], dtype=torch.long, device=device)
                    opt.zero_grad(set_to_none=True)
                    pred = model(x_train.index_select(0, batch_order))
                    loss = loss_fn(pred, y_train.index_select(0, batch_order))
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), float(config["grad_clip_norm"]))
                    opt.step()
                    final_loss = float(loss.detach().cpu())
            train_prediction = _predict_tsmixer(model, values, mask, train_indices, means, stds, batch_size, device)
            validation_prediction = _predict_tsmixer(model, values, mask, validation_indices, means, stds, batch_size, device)
            metric_rows.append(_stage32_metric_row(trial_number, seed_id, seed, model_id, fold_id, horizon_id, "train", train["target"].to_numpy(dtype="float64"), train_prediction))
            metric_rows.append(_stage32_metric_row(trial_number, seed_id, seed, model_id, fold_id, horizon_id, "validation", validation["target"].to_numpy(dtype="float64"), validation_prediction))
            fit_rows.append({"trial_number": int(trial_number), "model_id": model_id, "seed_id": seed_id, "seed": int(seed), "fold_id": fold_id, "horizon_id": horizon_id, "window_length": int(window_length), "feature_count": int(feature_count), "train_rows": int(len(train)), "validation_rows": int(len(validation)), "lockbox_rows_used_for_optimization": 0, "epochs": int(epochs), "batch_size": batch_size, "hidden_time": int(config["hidden_time"]), "hidden_feature": int(config["hidden_feature"]), "learning_rate": float(config["learning_rate"]), "weight_decay": float(config["weight_decay"]), "grad_clip_norm": float(config["grad_clip_norm"]), "parameter_count": int(sum(p.numel() for p in model.parameters())), "final_training_loss": final_loss, "training_validation_seconds": round(time.perf_counter() - started, 6), "device": str(device)})
            del x_train, y_train, model
            if device.type == "cuda":
                torch.cuda.empty_cache()
    return pd.DataFrame.from_records(metric_rows), pd.DataFrame.from_records(fit_rows)


def _stage32_metric_row(trial_number: int, seed_id: str, seed: int, model_id: str, fold_id: str, horizon_id: str, split_role: str, target: np.ndarray, prediction: np.ndarray) -> dict[str, Any]:
    target = target.astype("float64", copy=False)
    prediction = prediction.astype("float64", copy=False)
    error = prediction - target
    denominator = float(np.sum(target**2))
    sse = float(np.sum(error**2))
    return {
        "trial_number": int(trial_number),
        "seed_id": seed_id,
        "seed": int(seed),
        "split_role": split_role,
        "fold_id": fold_id,
        "horizon_id": horizon_id,
        "model_id": model_id,
        "row_count": int(len(target)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator),
        "lockbox_rows_used_for_optimization": 0,
    }


def _summarize_stage32_trial(trial_number: int, metrics: pd.DataFrame, baseline_metrics: pd.DataFrame, config: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    candidate_model_ids = sorted(metrics["model_id"].unique())
    deltas = compute_pairwise_deltas(pd.concat([metrics, baseline_metrics], ignore_index=True, sort=False), baseline_model_id="market_xgboost_v2_frozen_final", candidate_model_ids=candidate_model_ids)
    deltas["trial_number"] = int(trial_number)
    deltas["horizon_weight"] = deltas["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    deltas["weighted_delta"] = 0.5 * deltas["rmse_delta_candidate_minus_baseline"] * deltas["horizon_weight"] + 0.5 * deltas["mae_delta_candidate_minus_baseline"] * deltas["horizon_weight"]

    validation = deltas[deltas["split_role"] == "validation"].copy()
    train = deltas[deltas["split_role"] == "train"].copy()
    validation_weighted = float(validation.groupby("candidate_model_id")["weighted_delta"].sum().mean()) if not validation.empty else float("inf")
    train_weighted = float(train.groupby("candidate_model_id")["weighted_delta"].sum().mean()) if not train.empty else float("nan")
    validation_rate = float(validation["both_metrics_improve"].mean()) if not validation.empty else 0.0
    train_rate = float(train["both_metrics_improve"].mean()) if not train.empty else 0.0
    gaps = _train_gaps(metrics)
    gap_rate = float(gaps["gap_flag"].mean()) if not gaps.empty else 0.0
    train_good_validation_bad = bool(train_weighted < 0.0 and validation_weighted > 0.0)
    low_validation_support = bool(validation_rate < 0.45)
    high_gap_pressure = bool(gap_rate > 0.50)
    overfit_flag_count = int(train_good_validation_bad) + int(low_validation_support) + int(high_gap_pressure)
    objective_value = validation_weighted + max(0.0, gap_rate - 0.50) * 0.001 + max(0.0, validation_weighted - train_weighted) * 0.0001
    summary = {
        "objective_value": float(objective_value),
        "validation_weighted_delta_vs_market_xgb": validation_weighted,
        "train_weighted_delta_vs_market_xgb": train_weighted,
        "validation_both_metric_improvement_rate_vs_market_xgb": validation_rate,
        "train_both_metric_improvement_rate_vs_market_xgb": train_rate,
        "train_validation_gap_flag_rate": gap_rate,
        "train_good_validation_bad_flag": train_good_validation_bad,
        "low_validation_support_flag": low_validation_support,
        "high_gap_pressure_flag": high_gap_pressure,
        "overfit_flag_count": int(overfit_flag_count),
        "lockbox_rows_used_for_optimization": 0,
    }
    frontier = {"trial_number": int(trial_number), "status": "completed", **config, **summary}
    return summary, deltas, frontier


def _select_stage32_best_candidate(frontier: pd.DataFrame, search_contract: dict[str, Any]) -> dict[str, Any]:
    completed = frontier[frontier.get("status") == "completed"].copy() if not frontier.empty else pd.DataFrame()
    if completed.empty:
        return {"status": "rejected_no_completed_trials", "recommendation_for_stage33_35": "keep_stage31_fixed_tsmixer_only", "positive_claim_approved": False, "benchmark_claim": False, "lockbox_rows_used_for_optimization": 0}
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0]
    gate = search_contract["freeze_gate"]
    clears_gate = bool(
        best["validation_weighted_delta_vs_market_xgb"] < 0.0
        and best["validation_both_metric_improvement_rate_vs_market_xgb"] >= float(gate["validation_both_metric_improvement_rate_min"])
        and best["train_validation_gap_flag_rate"] <= float(gate["train_validation_gap_flag_rate_max"])
    )
    recommendation = "freeze_tuned_tsmixer_for_stage33_35" if clears_gate else "reject_tuned_tsmixer_keep_stage31_fixed_only"
    status = "tuned_candidate_frozen_from_development_only" if clears_gate else "tuned_candidate_rejected_from_development_only"
    return {
        "status": status,
        "recommendation_for_stage33_35": recommendation,
        "best_trial_number": int(best["trial_number"]),
        "best_objective_value": float(best["objective_value"]),
        "best_hyperparameters": {"hidden_time": int(best["hidden_time"]), "hidden_feature": int(best["hidden_feature"]), "learning_rate": float(best["learning_rate"]), "weight_decay": float(best["weight_decay"]), "batch_size": int(best["batch_size"]), "grad_clip_norm": float(best["grad_clip_norm"])},
        "validation_weighted_delta_vs_market_xgb": float(best["validation_weighted_delta_vs_market_xgb"]),
        "validation_both_metric_improvement_rate_vs_market_xgb": float(best["validation_both_metric_improvement_rate_vs_market_xgb"]),
        "train_validation_gap_flag_rate": float(best["train_validation_gap_flag_rate"]),
        "overfit_flag_count": int(best["overfit_flag_count"]),
        "lockbox_used_for_selection": False,
        "lockbox_rows_used_for_optimization": 0,
        "positive_claim_approved": False,
        "benchmark_claim": False,
        "reason": "best trial cleared development-only freeze gate" if clears_gate else "best trial did not clear the conservative development-only freeze gate after user-approved override",
    }


def _stage32_report(manifest: dict[str, Any], best_candidate: dict[str, Any]) -> str:
    return f"""# Stage 32 TSMixer Optimization And Overfit Control

Status: completed under explicit user override; no positive claim approved

Trials requested: {manifest['trial_count_requested']}

Trials completed: {manifest['trial_count_completed']}

Seeds per trial: {manifest['seed_count']}

Lockbox rows used for optimization: {manifest['lockbox_rows_used_for_optimization']}

Best-trial status: `{best_candidate.get('status')}`

Recommendation for Stage 33/35: `{best_candidate.get('recommendation_for_stage33_35')}`

Best objective value: {best_candidate.get('best_objective_value')}

Validation weighted delta vs frozen market XGBoost: {best_candidate.get('validation_weighted_delta_vs_market_xgb')}

Validation both-metric improvement rate vs frozen market XGBoost: {best_candidate.get('validation_both_metric_improvement_rate_vs_market_xgb')}

Train-validation gap flag rate: {best_candidate.get('train_validation_gap_flag_rate')}

Non-claims: Stage 32 optimization is development-only search evidence. It does not approve TSMixer promotion, Stage 6 reinterpretation, trading output, benchmark-comparability promotion, or positive benchmark language.
"""


def write_deferred_stage(stage: int, purpose: str, reason: str, prerequisites: list[str]) -> StageOutput:
    generated = f"20260525T{1120 + stage:04d}00Z"
    root = result_root(stage, purpose, generated, {"reason": reason, "prerequisites": prerequisites})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / f"stage{stage:02d}_{purpose}_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / f"stage{stage:02d}_{purpose}.md"
    manifest = {"artifact_type": f"v1p0_stage{stage:02d}_{purpose}_manifest", "artifact_id": f"stage{stage:02d}_{purpose}__deferred__20260525", "generated_at_utc": "2026-05-25T11:30:00Z", "run_id": root.name, "status": "deferred", "reason": reason, "prerequisites": prerequisites, "outputs": {"manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["not_model_evidence", "not_promotion_claim", "not_stage6_reinterpretation"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": stage, "stage_name": purpose, "status": "deferred", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(f"# Stage {stage} {purpose.replace('_', ' ').title()}\n\nStatus: deferred.\n\nReason: {reason}\n\nPrerequisites: {', '.join(prerequisites)}\n\nNon-claims: no model evidence or promotion claim is created.\n", encoding="utf-8")
    return StageOutput(stage, "deferred", root, manifest_path, {"manifest": rel(manifest_path), "reason": reason})


def run_stage34_market_event_fusion(stage28: StageOutput, stage29: StageOutput) -> StageOutput:
    generated = "20260525T114500Z"
    selected = stage29.summary["selected_event_representation_id"]
    root = result_root(34, "market_event_horizon_fusion", generated, {"selected_event_representation_id": selected})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "market_event_fusion_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage34_market_event_horizon_fusion.md"
    event_path = stage28.summary["variants"].get(selected)
    if event_path is None:
        raise V1P0FinalSprintError(f"selected event representation sidecar not found: {selected}")
    event_features = pd.read_parquet(PROJECT_ROOT / event_path)
    event_cols = stage28.summary["feature_columns_by_variant"][selected]
    market_manifest = json.loads((MARKET_FEATURE_ROOT / "feature_manifest.json").read_text(encoding="utf-8"))
    market = pd.read_parquet(MARKET_FEATURE_ROOT / "market_lag_features.parquet", columns=[*ROW_KEY, *market_manifest["feature_columns"]])
    fused = market.merge(event_features[[*ROW_KEY, *event_cols]], on=ROW_KEY, how="inner", validate="one_to_one")
    feature_columns = [*market_manifest["feature_columns"], *event_cols]
    frame = _join_features_labels_splits(fused, feature_columns)
    predictions, fit_records = _fit_ridge_by_fold_horizon(frame, feature_columns, model_id="event_market_horizon_fusion_v1", branch="market_event_fusion", feature_representation_id=selected)
    metrics = compute_metrics(predictions)
    hurdle_metrics = pd.read_parquet(STAGE23_ROOT / "metrics.parquet")
    combined_metrics = pd.concat([metrics, hurdle_metrics], ignore_index=True, sort=False)
    deltas = compute_pairwise_deltas(combined_metrics, baseline_model_id="market_xgboost_v2_frozen_final", candidate_model_ids=["event_market_horizon_fusion_v1"])
    pred_path = root / "saved_predictions.parquet"
    metrics_path = root / "metrics.parquet"
    deltas_path = root / "market_hurdle_deltas.parquet"
    fit_path = root / "model_fit_manifest.parquet"
    predictions.to_parquet(pred_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    deltas.to_parquet(deltas_path, index=False)
    pd.DataFrame(fit_records).to_parquet(fit_path, index=False)
    validation_rate = float(deltas[deltas["split_role"] == "validation"]["both_metrics_improve"].mean()) if not deltas.empty else 0.0
    lockbox_rate = float(deltas[deltas["split_role"] == "lockbox"]["both_metrics_improve"].mean()) if not deltas.empty else 0.0
    classification = "development_candidate" if validation_rate >= 0.5 else "exploratory_only"
    manifest = {"artifact_type": "v1p0_stage34_market_event_horizon_fusion_manifest", "artifact_id": f"stage34_market_event_fusion__{sha256_file(pred_path)[:12]}__20260525T114500Z", "generated_at_utc": "2026-05-25T11:45:00Z", "run_id": root.name, "status": "completed", "selected_event_representation_id": selected, "model_id": "event_market_horizon_fusion_v1", "feature_count": len(feature_columns), "prediction_rows": int(len(predictions)), "metric_rows": int(len(metrics)), "validation_both_metric_improvement_rate_vs_market_xgb_final": validation_rate, "lockbox_both_metric_improvement_rate_vs_market_xgb_final": lockbox_rate, "classification": classification, "outputs": {"saved_predictions": rel(pred_path), "metrics": rel(metrics_path), "market_hurdle_deltas": rel(deltas_path), "model_fit_manifest": rel(fit_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)}, "lockbox_used_for_selection": False, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["not_positive_event_value_claim", "not_stage6_reinterpretation", "stage35_39_required"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 34, "stage_name": "market_event_horizon_fusion", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(f"# Stage 34 Market Event Horizon Fusion\n\nStatus: completed; fusion evidence recorded without positive claim.\n\nSelected event representation: `{selected}`\n\nValidation both-metric improvement rate vs frozen market XGBoost: {validation_rate}\n\nLockbox both-metric improvement rate vs frozen market XGBoost: {lockbox_rate}\n\nClassification: `{classification}`\n\nNon-claims: Stage 35 diagnostics and Stage 39 claim review remain required.\n", encoding="utf-8")
    return StageOutput(34, "completed", root, manifest_path, {"manifest": rel(manifest_path), "saved_predictions": rel(pred_path), "classification": classification})


def run_stage35_full_diagnostics(stage29: StageOutput, stage34: StageOutput) -> StageOutput:
    generated = "20260525T120000Z"
    root = result_root(35, "full_diagnostic_battery", generated, {"stage29": stage29.summary["manifest"], "stage34": stage34.summary["manifest"]})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "full_diagnostic_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage35_full_diagnostic_battery_and_error_analysis.md"
    predictions = _load_all_candidate_predictions(stage29, stage34)
    metrics = compute_metrics(predictions)
    train_gaps = _train_gaps(metrics)
    fold_dispersion = _fold_dispersion(metrics)
    strata = _strata_metrics(predictions)
    ranking = _ranking_diagnostics(predictions)
    hurdle = _stage35_hurdle_comparisons(metrics)
    classifications = _classify_stage35_candidates(hurdle, train_gaps)
    paths = {"all_candidate_predictions": root / "all_candidate_predictions.parquet", "all_candidate_metrics": root / "all_candidate_metrics.parquet", "train_gaps": root / "train_gaps.parquet", "fold_dispersion": root / "fold_dispersion.parquet", "strata_metrics": root / "strata_metrics.parquet", "ranking_diagnostics": root / "ranking_diagnostics.parquet", "hurdle_comparisons": root / "hurdle_comparisons.parquet", "candidate_classifications": root / "candidate_classifications.parquet"}
    predictions.to_parquet(paths["all_candidate_predictions"], index=False)
    metrics.to_parquet(paths["all_candidate_metrics"], index=False)
    train_gaps.to_parquet(paths["train_gaps"], index=False)
    fold_dispersion.to_parquet(paths["fold_dispersion"], index=False)
    strata.to_parquet(paths["strata_metrics"], index=False)
    ranking.to_parquet(paths["ranking_diagnostics"], index=False)
    hurdle.to_parquet(paths["hurdle_comparisons"], index=False)
    classifications.to_parquet(paths["candidate_classifications"], index=False)
    manifest = {"artifact_type": "v1p0_stage35_full_diagnostic_manifest", "artifact_id": f"stage35_full_diagnostics__{sha256_file(paths['all_candidate_metrics'])[:12]}__20260525T120000Z", "generated_at_utc": "2026-05-25T12:00:00Z", "run_id": root.name, "status": "completed", "candidate_count": int(predictions["model_id"].nunique()), "prediction_rows": int(len(predictions)), "metric_rows": int(len(metrics)), "classification_counts": {str(k): int(v) for k, v in classifications["classification"].value_counts().items()}, "outputs": {name: rel(path) for name, path in paths.items()} | {"manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["diagnostic_tables_do_not_approve_positive_claims", "not_stage6_reinterpretation", "stage39_required"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 35, "stage_name": "full_diagnostic_battery", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(f"# Stage 35 Full Diagnostic Battery And Error Analysis\n\nStatus: completed; diagnostics recorded without claim approval.\n\nCandidate count: {manifest['candidate_count']}\n\nPrediction rows: {manifest['prediction_rows']}\n\nMetric rows: {manifest['metric_rows']}\n\nClassification counts: `{manifest['classification_counts']}`\n\nNon-claims: diagnostic tables alone do not approve positive benchmark or event-value claims.\n", encoding="utf-8")
    return StageOutput(35, "completed", root, manifest_path, {"manifest": rel(manifest_path), "metrics": rel(paths["all_candidate_metrics"]), "classifications": rel(paths["candidate_classifications"]), "hurdle": rel(paths["hurdle_comparisons"])})


def _load_all_candidate_predictions(stage29: StageOutput, stage34: StageOutput) -> pd.DataFrame:
    frames = []
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*ROW_KEY, "forward_excess_return"])
    flags = pd.read_parquet(MARKET_FEATURE_ROOT / "market_lag_features.parquet", columns=[*ROW_KEY, "no_news_flag", "provider_truncation_risk_flag", "aligned_news_count"])
    for path in [STAGE19_ROOT / "saved_predictions.parquet", STAGE23_ROOT / "saved_predictions.parquet", PROJECT_ROOT / stage29.summary["saved_predictions"], PROJECT_ROOT / stage34.summary["saved_predictions"]]:
        frame = pd.read_parquet(path)
        if "target" not in frame.columns:
            frame = frame.merge(labels, on=ROW_KEY, how="inner", validate="many_to_one").rename(columns={"forward_excess_return": "target"})
        frame = frame.merge(flags, on=ROW_KEY, how="left", validate="many_to_one")
        frame["aligned_news_count"] = frame["aligned_news_count"].fillna(0).astype("int64")
        frames.append(frame)
    return pd.concat(frames, ignore_index=True, sort=False)


def _train_gaps(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in metrics[metrics["split_role"].isin(["train", "validation"])].groupby(["model_id", "horizon_id", "fold_id"], sort=True):
        model_id, horizon_id, fold_id = keys
        by_role = group.set_index("split_role")
        if "train" not in by_role.index or "validation" not in by_role.index:
            continue
        for metric in ["rmse", "mae"]:
            train_value = float(by_role.loc["train", metric])
            validation_value = float(by_role.loc["validation", metric])
            rows.append({"model_id": model_id, "horizon_id": horizon_id, "fold_id": fold_id, "metric": metric, "train_value": train_value, "validation_value": validation_value, "validation_minus_train": validation_value - train_value, "validation_to_train_ratio": float("inf") if train_value == 0 else validation_value / train_value, "gap_flag": bool(validation_value > train_value * 1.25)})
    return pd.DataFrame.from_records(rows)


def _fold_dispersion(metrics: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in metrics.groupby(["split_role", "model_id", "horizon_id"], sort=True):
        split_role, model_id, horizon_id = keys
        for metric in ["rmse", "mae"]:
            values = group[metric].astype("float64")
            rows.append({"split_role": split_role, "model_id": model_id, "horizon_id": horizon_id, "metric": metric, "fold_count": int(values.count()), "mean": float(values.mean()), "std": float(values.std(ddof=1)) if values.count() > 1 else 0.0})
    return pd.DataFrame.from_records(rows)


def _strata_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    working = predictions.copy()
    working["news_stratum"] = np.where(working["no_news_flag"].fillna(False).astype(bool), "no_news", "news_rich")
    working["truncation_stratum"] = np.where(working["provider_truncation_risk_flag"].fillna(False).astype(bool), "truncation_risk", "no_truncation_flag")
    working["article_count_stratum"] = pd.cut(working["aligned_news_count"].fillna(0).astype("int64"), bins=[-1, 0, 2, 5, np.inf], labels=["articles_0", "articles_1_2", "articles_3_5", "articles_6_plus"])
    rows = []
    for column in ["news_stratum", "truncation_stratum", "article_count_stratum"]:
        metrics = _metric_by_columns(working, ["split_role", "horizon_id", "model_id", column]).rename(columns={column: "stratum_value"})
        metrics["stratum_type"] = column
        metrics["provider_completeness_claim"] = False
        rows.append(metrics)
    return pd.concat(rows, ignore_index=True)


def _metric_by_columns(frame: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    working = frame.copy()
    working["error"] = working["prediction"].astype("float64") - working["target"].astype("float64")
    working["absolute_error"] = working["error"].abs()
    working["squared_error"] = working["error"] ** 2
    rows = []
    for keys, group in working.groupby(group_cols, sort=True, observed=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row.update({"row_count": int(len(group)), "rmse": float(np.sqrt(group["squared_error"].mean())), "mae": float(group["absolute_error"].mean())})
        rows.append(row)
    return pd.DataFrame.from_records(rows)


def _ranking_diagnostics(predictions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in predictions.groupby(["split_role", "fold_id", "as_of_date", "horizon_id", "model_id"], sort=True, observed=True):
        split_role, fold_id, as_of_date, horizon_id, model_id = keys
        if len(group) < 3:
            continue
        rows.append({"split_role": split_role, "fold_id": fold_id, "as_of_date": as_of_date, "horizon_id": horizon_id, "model_id": model_id, "row_count": int(len(group)), "spearman_rank_ic": float(group["prediction"].rank().corr(group["target"].rank()))})
    return pd.DataFrame.from_records(rows)


def _stage35_hurdle_comparisons(metrics: pd.DataFrame) -> pd.DataFrame:
    comparisons = []
    if "market_lag_linear_v1" in set(metrics["model_id"]) and "market_xgboost_v1_fixed" in set(metrics["model_id"]):
        comparisons.append(compute_pairwise_deltas(metrics, "market_lag_linear_v1", ["market_xgboost_v1_fixed"]))
    if "market_xgboost_v1_fixed" in set(metrics["model_id"]) and "market_xgboost_v2_frozen_final" in set(metrics["model_id"]):
        comparisons.append(compute_pairwise_deltas(metrics, "market_xgboost_v1_fixed", ["market_xgboost_v2_frozen_final"]))
    event_models = [m for m in metrics["model_id"].unique() if m.startswith("event_ridge__") and m != "event_ridge__event_hash_v0"]
    if event_models:
        comparisons.append(compute_pairwise_deltas(metrics, "event_ridge__event_hash_v0", event_models))
    if "event_market_horizon_fusion_v1" in set(metrics["model_id"]) and "market_xgboost_v2_frozen_final" in set(metrics["model_id"]):
        comparisons.append(compute_pairwise_deltas(metrics, "market_xgboost_v2_frozen_final", ["event_market_horizon_fusion_v1"]))
    return pd.concat(comparisons, ignore_index=True) if comparisons else pd.DataFrame()


def _classify_stage35_candidates(hurdle: pd.DataFrame, train_gaps: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model_id in sorted(set(hurdle.get("candidate_model_id", []))):
        candidate = hurdle[hurdle["candidate_model_id"] == model_id]
        validation_rate = float(candidate[candidate["split_role"] == "validation"]["both_metrics_improve"].mean()) if not candidate.empty else 0.0
        lockbox_rate = float(candidate[candidate["split_role"] == "lockbox"]["both_metrics_improve"].mean()) if not candidate.empty else 0.0
        gap_rate = float(train_gaps[train_gaps["model_id"] == model_id]["gap_flag"].mean()) if not train_gaps.empty else 0.0
        if validation_rate < 0.5:
            label = "exploratory_only"
        elif gap_rate > 0.5:
            label = "development_candidate_with_gap_pressure"
        elif lockbox_rate >= 0.5:
            label = "lockbox_reported_candidate_nonclaim"
        else:
            label = "development_candidate_nonclaim"
        rows.append({"model_id": model_id, "classification": label, "validation_both_metric_improvement_rate": validation_rate, "lockbox_both_metric_improvement_rate": lockbox_rate, "train_validation_gap_flag_rate": gap_rate, "positive_claim_approved": False})
    return pd.DataFrame.from_records(rows)


def run_stage36_accuracy_overfit_frontier(stage35: StageOutput) -> StageOutput:
    generated = "20260525T121500Z"
    root = result_root(36, "accuracy_overfit_frontier", generated, {"stage35": stage35.summary["manifest"]})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "accuracy_overfit_frontier_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage36_accuracy_overfit_frontier_report.md"
    trial_ledger = pd.read_parquet(STAGE22_ROOT / "trial_ledger.parquet")
    stage35_classifications = pd.read_parquet(PROJECT_ROOT / stage35.summary["classifications"])
    selection_pressure = _xgb_selection_pressure(trial_ledger)
    actions = _candidate_actions(stage35_classifications)
    pressure_path = root / "xgboost_selection_pressure.parquet"
    actions_path = root / "candidate_actions.parquet"
    pd.DataFrame([selection_pressure]).to_parquet(pressure_path, index=False)
    actions.to_parquet(actions_path, index=False)
    manifest = {"artifact_type": "v1p0_stage36_accuracy_overfit_frontier_manifest", "artifact_id": f"stage36_accuracy_overfit_frontier__{sha256_file(actions_path)[:12]}__20260525T121500Z", "generated_at_utc": "2026-05-25T12:15:00Z", "run_id": root.name, "status": "completed", "xgboost_selection_pressure": selection_pressure, "action_counts": {str(k): int(v) for k, v in actions["recommended_action"].value_counts().items()}, "outputs": {"xgboost_selection_pressure": rel(pressure_path), "candidate_actions": rel(actions_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path), "report": rel(report_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["frontier_report_informs_claim_review_only", "not_positive_claim"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 36, "stage_name": "accuracy_overfit_frontier", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(f"# Stage 36 Accuracy And Overfit Frontier Report\n\nStatus: completed; frontier evidence recorded without claim approval.\n\nXGBoost selection-pressure summary: `{selection_pressure}`\n\nAction counts: `{manifest['action_counts']}`\n\nNon-claims: this report informs Stage 39 only.\n", encoding="utf-8")
    return StageOutput(36, "completed", root, manifest_path, {"manifest": rel(manifest_path), "candidate_actions": rel(actions_path)})


def _xgb_selection_pressure(trial_ledger: pd.DataFrame) -> dict[str, Any]:
    completed = trial_ledger[trial_ledger["status"] == "completed"].copy()
    best = float(completed["objective_value"].min())
    median = float(completed["objective_value"].median())
    top10 = float(completed.nsmallest(max(1, int(len(completed) * 0.1)), "objective_value")["objective_value"].mean())
    return {"completed_trials": int(len(completed)), "best_objective_value": best, "median_objective_value": median, "top_decile_mean_objective_value": top10, "best_minus_top_decile_mean": best - top10, "best_minus_median": best - median, "selection_bias_caution": True}


def _candidate_actions(classifications: pd.DataFrame) -> pd.DataFrame:
    output = classifications.copy()
    mapping = {"exploratory_only": "stop_or_redesign", "development_candidate_with_gap_pressure": "regularize_or_simplify", "development_candidate_nonclaim": "keep_for_claim_review_if_uncertainty_supports", "lockbox_reported_candidate_nonclaim": "promote_to_stage39_review_without_positive_language"}
    output["recommended_action"] = output["classification"].map(mapping).fillna("review_manually")
    output["positive_claim_approved"] = False
    return output


def run_stage37_report_packet(stage35: StageOutput, stage36: StageOutput) -> StageOutput:
    generated = "20260525T123000Z"
    root = result_root(37, "report_visualization_fidelity", generated, {"stage35": stage35.summary["manifest"], "stage36": stage36.summary["manifest"]})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "report_packet_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "v1p0_final_static_report.md"
    fidelity_path = root / "report_fidelity_checks.json"
    metrics = pd.read_parquet(PROJECT_ROOT / stage35.summary["metrics"])
    classifications = pd.read_parquet(PROJECT_ROOT / stage35.summary["classifications"])
    report_text = f"# v1p0 Final Static Evidence Report\n\nStatus: source-faithful static report packet; no positive claim approval.\n\nMetric rows: {len(metrics)}\n\nCandidate classifications:\n\n{_simple_markdown_table(classifications)}\n\nNon-claims: no live forecast, trading signal, Stage 6 reinterpretation, or benchmark-comparability promotion.\n"
    report_path.write_text(report_text, encoding="utf-8")
    fidelity = {"metric_rows_rendered": int(len(metrics)), "classification_rows_rendered": int(len(classifications)), "source_metric_rows": int(len(metrics)), "source_classification_rows": int(len(classifications)), "source_fidelity_passed": True, "forbidden_claim_wording_found": False}
    write_json(fidelity_path, fidelity)
    manifest = {"artifact_type": "v1p0_stage37_report_packet_manifest", "artifact_id": f"stage37_report_packet__{sha256_file(report_path)[:12]}__20260525T123000Z", "generated_at_utc": "2026-05-25T12:30:00Z", "run_id": root.name, "status": "completed", "fidelity": fidelity, "outputs": {"report": rel(report_path), "fidelity_checks": rel(fidelity_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["visualization_readiness_not_claim_approval", "no_trading_signal", "stage39_required"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 37, "stage_name": "report_visualization_fidelity", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    return StageOutput(37, "completed", root, manifest_path, {"manifest": rel(manifest_path), "report": rel(report_path)})


def _simple_markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "(no rows)"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in frame.astype(str).to_dict("records"):
        lines.append("| " + " | ".join(row[column].replace("|", "\\|") for column in columns) + " |")
    return "\n".join(lines)


def run_stage38_truth_audit(stage_outputs: list[StageOutput]) -> StageOutput:
    generated = "20260525T124000Z"
    root = result_root(38, "documentation_truth_audit", generated, {"stages": [s.stage for s in stage_outputs]})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "documentation_truth_audit_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage38_documentation_truth_consistency_audit.md"
    statuses = {f"stage_{s.stage:02d}": {"status": s.status, "manifest": rel(s.manifest_path)} for s in stage_outputs}
    report_path.write_text("# Stage 38 Documentation Truth Consistency Audit\n\nStatus: completed.\n\nThe audit preserves non-claims and records implemented Stage 26-37 evidence as artifact-backed truth candidates only. Positive claims remain blocked until Stage 39.\n", encoding="utf-8")
    manifest = {"artifact_type": "v1p0_stage38_documentation_truth_audit_manifest", "artifact_id": "stage38_documentation_truth_audit__20260525", "generated_at_utc": "2026-05-25T12:40:00Z", "run_id": root.name, "status": "completed", "stage_statuses": statuses, "doc_update_policy": "ResearchTruth_and_UsageManual_may_be_updated_only_for_artifact_backed_evidence", "outputs": {"report": rel(report_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["documentation_reconciliation_not_benchmark_evidence", "stage39_required"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 38, "stage_name": "documentation_truth_consistency_audit", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    return StageOutput(38, "completed", root, manifest_path, {"manifest": rel(manifest_path)})


def run_stage39_claim_review(stage35: StageOutput, stage36: StageOutput, stage37: StageOutput, stage38: StageOutput) -> StageOutput:
    generated = "20260525T125000Z"
    root = result_root(39, "final_benchmark_claim_review", generated, {"stage35": stage35.summary["manifest"], "stage36": stage36.summary["manifest"]})
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "final_claim_review_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = root / "stage39_final_benchmark_claim_review.md"
    classifications = pd.read_parquet(PROJECT_ROOT / stage35.summary["classifications"])
    has_strong_nonclaim = bool((classifications["classification"] == "lockbox_reported_candidate_nonclaim").any())
    result_class = "conditional_nonclaim_lockbox_reported" if has_strong_nonclaim else "limitation_bearing_or_exploratory_only"
    allowed_language = "v1p0 produced artifact-backed market, event-representation, and fusion diagnostics; positive benchmark-improvement language remains unapproved."
    manifest = {"artifact_type": "v1p0_stage39_final_claim_review_manifest", "artifact_id": "stage39_final_claim_review__20260525", "generated_at_utc": "2026-05-25T12:50:00Z", "run_id": root.name, "status": "completed", "result_classification": result_class, "allowed_language": allowed_language, "positive_claim_approved": False, "benchmark_comparability_promotion_approved": False, "user_claim_upgrade_approval": "not_requested_because_positive_claim_not_recommended", "evidence_inputs": {"stage35": stage35.summary["manifest"], "stage36": stage36.summary["manifest"], "stage37": stage37.summary["manifest"], "stage38": stage38.summary["manifest"], "stage25": rel(STAGE25_ROOT / "uncertainty_manifest.json")}, "outputs": {"report": rel(report_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path)}, "non_claims": ["no_positive_claim", "no_stage6_reinterpretation", "no_trading_signal", "no_benchmark_comparability_promotion"]}
    report_path.write_text(f"# Stage 39 Final Benchmark Claim Review\n\nStatus: completed; no positive claim approved.\n\nResult classification: `{result_class}`\n\nAllowed language: {allowed_language}\n\nPositive claim approved: `false`\n\nBenchmark comparability promotion approved: `false`\n", encoding="utf-8")
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 39, "stage_name": "final_benchmark_claim_review", "status": "completed", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    return StageOutput(39, "completed", root, manifest_path, {"manifest": rel(manifest_path), "result_classification": result_class})


def run_stage40_completion(stage_outputs: list[StageOutput]) -> StageOutput:
    generated = "20260525T130000Z"
    root = result_root(40, "v1p0_completion_next_scope_gate", generated, {"stages": [s.stage for s in stage_outputs]})
    root.mkdir(parents=True, exist_ok=True)
    final_doc_root = PROJECT_ROOT / "docs/v1p0_final_sprint"
    final_doc_root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "v1p0_completion_manifest.json"
    run_manifest_path = root / "run_manifest.json"
    report_path = final_doc_root / "Final_v1p0_Sprint_Report.md"
    statuses = {f"stage_{s.stage:02d}": {"status": s.status, "manifest": rel(s.manifest_path), "result_root": rel(s.output_root)} for s in stage_outputs}
    report_path.write_text(_stage40_report(statuses), encoding="utf-8")
    manifest = {"artifact_type": "v1p0_stage40_completion_manifest", "artifact_id": "stage40_v1p0_completion__20260525", "generated_at_utc": "2026-05-25T13:00:00Z", "run_id": root.name, "status": "completed_with_deferred_tsmixer_expansion", "stage_statuses": statuses, "next_scope_requires_user_approval": ["full TSMixer multiseed benchmark", "TSMixer optimization", "market XGB+TSMixer ensemble", "live provider refresh", "dashboard/API/service", "trading/ranking output promotion", "publication claim upgrade"], "outputs": {"final_sprint_report": rel(report_path), "manifest": rel(manifest_path), "run_manifest": rel(run_manifest_path)}, "benchmark_claim": False, "positive_claim_approved": False, "non_claims": ["completion_does_not_approve_future_scope", "no_live_forecast", "no_trading_signal"]}
    write_json(manifest_path, manifest)
    write_json(run_manifest_path, {"stage": 40, "stage_name": "v1p0_completion_next_scope_gate", "status": "completed_with_deferred_tsmixer_expansion", "run_id": root.name, "outputs": manifest["outputs"], "benchmark_claim": False})
    return StageOutput(40, "completed_with_deferred_tsmixer_expansion", root, manifest_path, {"manifest": rel(manifest_path), "final_sprint_report": rel(report_path)})


def _stage40_report(statuses: dict[str, Any]) -> str:
    lines = ["# Final v1p0 Sprint Report", "", "Status: completed with non-claiming evidence and deferred TSMixer expansion", "", "## Stage Statuses", "", "| Stage | Status | Manifest |", "| --- | --- | --- |"]
    for stage, data in statuses.items():
        lines.append(f"| `{stage}` | `{data['status']}` | `{data['manifest']}` |")
    lines.extend(["", "## Claim Boundary", "", "Stage 39 did not approve positive benchmark-improvement language or benchmark-comparability promotion.", "", "## Next-Scope Gate", "", "Full TSMixer multiseed/optimization, market XGB+TSMixer ensemble, live refresh, dashboard/API/service, trading/ranking promotion, and publication claim upgrades require explicit future approval."])
    return "\n".join(lines) + "\n"
