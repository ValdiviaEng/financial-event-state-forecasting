"""CLI orchestration for Stage 3 feature and label artifacts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import shutil
import sys
from typing import Any

import pandas as pd

from event_state_forecasting.data.contracts import BENCHMARK_FAMILY_ID, ROW_KEY_FIELDS
from event_state_forecasting.dataset.panel_builder import DEFAULT_RAW_ALPHAVANTAGE_ROOT, DEFAULT_RAW_TWELVEDATA_ROOT, FULL_WINDOW_FILENAME, load_twelvedata_prices
from event_state_forecasting.dataset.row_universe import row_universe_digest
from event_state_forecasting.features.event_state import build_event_state_features, load_and_align_alphavantage_articles
from event_state_forecasting.features.labels import LABEL_REFERENCE_POLICY, LABEL_RETURN_TYPE, build_forward_excess_return_labels
from event_state_forecasting.features.market import build_market_features


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_FAMILY_ROOT = PROJECT_ROOT / "data" / "datasets" / BENCHMARK_FAMILY_ID
DEFAULT_STAGE3_OUTPUT_ROOT = PROJECT_ROOT / "data" / "features" / BENCHMARK_FAMILY_ID
DEFAULT_FEATURE_CONFIG = PROJECT_ROOT / "configs" / "features.yaml"
DEFAULT_LABEL_CONFIG = PROJECT_ROOT / "configs" / "labels.yaml"


class FeatureLabelBuildError(ValueError):
    """Raised when Stage 3 artifacts cannot be built safely."""


@dataclass(frozen=True, slots=True)
class FeatureLabelOutputs:
    artifact_version: str
    artifact_root: Path
    market_features_path: Path
    event_state_features_path: Path
    labels_path: Path
    aligned_news_path: Path
    manifest_path: Path
    row_universe_digest_path: Path
    row_count: int
    row_digest: str
    manifest: dict[str, Any]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build Stage 3 market, event-state, no-news, and label artifacts.")
    parser.add_argument("--dataset-root", default=str(DEFAULT_DATASET_FAMILY_ROOT), help="Stage 2 dataset version root or family root.")
    parser.add_argument("--output-root", default=str(DEFAULT_STAGE3_OUTPUT_ROOT), help="Stage 3 artifact family output root.")
    parser.add_argument("--features-config", default=str(DEFAULT_FEATURE_CONFIG), help="Active Stage 3 feature config.")
    parser.add_argument("--labels-config", default=str(DEFAULT_LABEL_CONFIG), help="Active Stage 3 label config.")
    parser.add_argument("--raw-twelvedata-root", default=str(DEFAULT_RAW_TWELVEDATA_ROOT), help="Raw Twelve Data root.")
    parser.add_argument("--twelvedata-full-window-filename", default=FULL_WINDOW_FILENAME, help="Twelve Data raw filename to load for label reference prices.")
    parser.add_argument("--raw-alphavantage-root", default=str(DEFAULT_RAW_ALPHAVANTAGE_ROOT), help="Raw Alpha Vantage root.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Replace an existing Stage 3 artifact root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable build summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        outputs = run_feature_label_build(
            dataset_root=Path(args.dataset_root),
            output_root=Path(args.output_root),
            features_config_path=Path(args.features_config),
            labels_config_path=Path(args.labels_config),
            raw_twelvedata_root=Path(args.raw_twelvedata_root),
            twelvedata_full_window_filename=args.twelvedata_full_window_filename,
            raw_alphavantage_root=Path(args.raw_alphavantage_root),
            allow_overwrite=args.allow_overwrite,
        )
    except FeatureLabelBuildError as exc:
        print(f"STAGE3_FEATURE_LABEL_BUILD_FAILED: {exc}", file=sys.stderr)
        return 2

    summary: dict[str, Any] = {
        "status": "stage3_features_labels_built",
        "benchmark_claim": False,
        "artifact_version": outputs.artifact_version,
        "artifact_root": str(outputs.artifact_root),
        "row_count": outputs.row_count,
        "row_universe_digest": outputs.row_digest,
        "manifest_path": str(outputs.manifest_path),
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("STAGE3 FEATURE LABEL BUILD")
        print("status: stage3_features_labels_built")
        print("benchmark_claim: false")
        print(f"artifact_version: {outputs.artifact_version}")
        print(f"row_count: {outputs.row_count}")
        print(f"row_universe_digest: {outputs.row_digest}")
        print(f"artifact_root: {outputs.artifact_root}")
        print(f"manifest: {outputs.manifest_path}")
    return 0


def run_feature_label_build(
    *,
    dataset_root: Path,
    output_root: Path = DEFAULT_STAGE3_OUTPUT_ROOT,
    features_config_path: Path = DEFAULT_FEATURE_CONFIG,
    labels_config_path: Path = DEFAULT_LABEL_CONFIG,
    raw_twelvedata_root: Path = DEFAULT_RAW_TWELVEDATA_ROOT,
    twelvedata_full_window_filename: str = FULL_WINDOW_FILENAME,
    raw_alphavantage_root: Path = DEFAULT_RAW_ALPHAVANTAGE_ROOT,
    allow_overwrite: bool = False,
) -> FeatureLabelOutputs:
    dataset_root = resolve_dataset_root(dataset_root)
    manifest_path = dataset_root / "dataset_manifest.json"
    panel_path = dataset_root / "benchmark_panel.parquet"
    row_digest_path = dataset_root / "row_universe_digest.json"
    if not manifest_path.exists() or not panel_path.exists() or not row_digest_path.exists():
        raise FeatureLabelBuildError(f"missing Stage 2 dataset artifacts under {dataset_root}")

    dataset_manifest = read_json(manifest_path)
    stage2_row_digest = read_json(row_digest_path)
    features_config = read_json(features_config_path)
    labels_config = read_json(labels_config_path)
    validate_stage3_configs(features_config, labels_config)

    panel = pd.read_parquet(panel_path).sort_values(list(ROW_KEY_FIELDS)).reset_index(drop=True)
    tickers = sorted(panel["canonical_ticker"].drop_duplicates().tolist())
    dates = sorted(date.fromisoformat(value) for value in panel["as_of_date"].drop_duplicates().tolist())
    start_year = min(dates).year
    end_year = max(dates).year

    price_by_ticker, price_source_paths, _ = load_twelvedata_prices(
        raw_twelvedata_root,
        tickers,
        full_window_filename=twelvedata_full_window_filename,
    )
    close_by_ticker = {ticker: {value_date: float(values["close"]) for value_date, values in rows.items()} for ticker, rows in price_by_ticker.items()}

    aligned_news, news_summary = load_and_align_alphavantage_articles(
        raw_root=raw_alphavantage_root,
        tickers=tickers,
        trading_dates=dates,
        start_year=start_year,
        end_year=end_year,
    )
    aligned_records = [record for record in aligned_news.to_dict("records")]
    event_records = [aligned_record_from_dict(record) for record in aligned_records]

    market_features = build_market_features(panel).sort_values(list(ROW_KEY_FIELDS)).reset_index(drop=True)
    event_state_features = build_event_state_features(
        panel,
        event_records,
        embedding_dimension=int(features_config["embeddings"]["dimension"]),
    ).sort_values(list(ROW_KEY_FIELDS)).reset_index(drop=True)
    labels = build_forward_excess_return_labels(panel, close_by_ticker).sort_values(list(ROW_KEY_FIELDS)).reset_index(drop=True)

    expected_digest = stage2_row_digest.get("row_universe_digest")
    row_digest = assert_row_digest_matches(expected_digest, market_features, event_state_features, labels)
    artifact_version = f"{dataset_manifest['identity']['dataset_version']}__stage3_features_labels_v1"
    artifact_root = output_root / artifact_version
    if artifact_root.exists():
        if not allow_overwrite:
            raise FeatureLabelBuildError(f"Stage 3 output already exists: {artifact_root}")
        shutil.rmtree(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=False)

    market_features_path = artifact_root / "market_features.parquet"
    event_state_features_path = artifact_root / "event_state_features.parquet"
    labels_path = artifact_root / "labels.parquet"
    aligned_news_path = artifact_root / "aligned_news.parquet"
    stage3_row_digest_path = artifact_root / "row_universe_digest.json"
    stage3_manifest_path = artifact_root / "feature_label_manifest.json"

    market_features.to_parquet(market_features_path, index=False, engine="pyarrow")
    event_state_features.to_parquet(event_state_features_path, index=False, engine="pyarrow")
    labels.to_parquet(labels_path, index=False, engine="pyarrow")
    aligned_news.to_parquet(aligned_news_path, index=False, engine="pyarrow")

    digest_record = {
        "artifact_type": "stage3_row_universe_digest",
        "input_dataset_version": dataset_manifest["identity"]["dataset_version"],
        "artifact_version": artifact_version,
        "row_key_fields": list(ROW_KEY_FIELDS),
        "row_count": len(labels),
        "row_universe_digest": row_digest,
        "stage2_row_universe_digest": expected_digest,
        "market_features_row_universe_digest": row_digest,
        "event_state_features_row_universe_digest": row_digest,
        "labels_row_universe_digest": row_digest,
        "branch_row_universe_equal": True,
    }
    manifest = build_manifest(
        artifact_version=artifact_version,
        artifact_root=artifact_root,
        dataset_root=dataset_root,
        dataset_manifest=dataset_manifest,
        row_digest=row_digest,
        row_count=len(labels),
        features_config_path=features_config_path,
        labels_config_path=labels_config_path,
        market_features_path=market_features_path,
        event_state_features_path=event_state_features_path,
        labels_path=labels_path,
        aligned_news_path=aligned_news_path,
        row_digest_path=stage3_row_digest_path,
        news_summary=news_summary,
        price_source_paths=price_source_paths,
        event_state_features=event_state_features,
    )
    write_json(stage3_row_digest_path, digest_record)
    write_json(stage3_manifest_path, manifest)

    return FeatureLabelOutputs(
        artifact_version=artifact_version,
        artifact_root=artifact_root,
        market_features_path=market_features_path,
        event_state_features_path=event_state_features_path,
        labels_path=labels_path,
        aligned_news_path=aligned_news_path,
        manifest_path=stage3_manifest_path,
        row_universe_digest_path=stage3_row_digest_path,
        row_count=len(labels),
        row_digest=row_digest,
        manifest=manifest,
    )


def build_manifest(**kwargs: Any) -> dict[str, Any]:
    event_state_features: pd.DataFrame = kwargs["event_state_features"]
    no_news_count = int(event_state_features["no_news_flag"].sum())
    return {
        "artifact_type": "stage3_feature_label_artifact_manifest",
        "benchmark_claim": False,
        "identity": {
            "artifact_version": kwargs["artifact_version"],
            "artifact_schema_version": "stage3_features_labels_v1",
            "generated_at_utc": pd.Timestamp.now("UTC").isoformat().replace("+00:00", "Z"),
            "input_dataset_version": kwargs["dataset_manifest"]["identity"]["dataset_version"],
            "feature_artifacts_created": True,
            "label_artifacts_created": True,
            "split_artifacts_created": False,
            "model_artifacts_created": False,
        },
        "inputs": {
            "dataset_root": str(kwargs["dataset_root"]),
            "dataset_manifest": str(kwargs["dataset_root"] / "dataset_manifest.json"),
            "features_config": str(kwargs["features_config_path"]),
            "labels_config": str(kwargs["labels_config_path"]),
            "price_source_file_count": len(kwargs["price_source_paths"]),
        },
        "artifacts": {
            "artifact_root": str(kwargs["artifact_root"]),
            "market_features": str(kwargs["market_features_path"]),
            "event_state_features": str(kwargs["event_state_features_path"]),
            "labels": str(kwargs["labels_path"]),
            "aligned_news": str(kwargs["aligned_news_path"]),
            "row_universe_digest": str(kwargs["row_digest_path"]),
        },
        "row_universe": {
            "row_key_fields": list(ROW_KEY_FIELDS),
            "row_count": kwargs["row_count"],
            "row_universe_digest": kwargs["row_digest"],
            "stage2_row_universe_digest": kwargs["dataset_manifest"]["hashes"]["row_universe_digest"],
            "branch_row_universe_equal": True,
        },
        "features": {
            "market_feature_policy": "same_row_as_of_close_only",
            "event_state_embedding_model_id": "deterministic_hash_embedding_v1",
            "event_state_embedding_dimension": 8,
            "event_state_pooling_policy": "mean",
            "no_news_row_count": no_news_count,
            "rows_with_aligned_news_count": int(kwargs["row_count"] - no_news_count),
            "provider_truncation_risk_row_count": int(event_state_features["provider_truncation_risk_flag"].sum()),
        },
        "labels": {
            "target_family": "forward_excess_returns",
            "return_type": LABEL_RETURN_TYPE,
            "reference_policy": LABEL_REFERENCE_POLICY,
            "label_values_created": True,
            "label_available_row_count": kwargs["row_count"],
        },
        "news_alignment": kwargs["news_summary"],
        "limitations": [
            "Alpha Vantage provider-level article completeness is not claimed; provider truncation-risk flags are preserved.",
            "Hash embeddings are deterministic local Stage 3 representations, not semantic model embeddings.",
            "Stage 3 creates features and labels only; split construction, training, predictions, metrics, and benchmark results are pending later stages.",
        ],
        "non_claims": [
            "not_splits",
            "not_models",
            "not_predictions",
            "not_metrics",
            "not_benchmark_runner",
            "not_benchmark_result",
            "not_provider_level_article_completeness",
        ],
    }


def validate_stage3_configs(features_config: dict[str, Any], labels_config: dict[str, Any]) -> None:
    if features_config.get("artifact_schema_version") != "stage3_features_v1":
        raise FeatureLabelBuildError("features config schema version mismatch")
    embeddings = features_config.get("embeddings", {})
    if embeddings.get("model_id") != "deterministic_hash_embedding_v1" or embeddings.get("dimension") != 8:
        raise FeatureLabelBuildError("features config must use deterministic 8-dimensional hash embeddings")
    if labels_config.get("target_family") != "forward_excess_returns":
        raise FeatureLabelBuildError("labels config target family mismatch")
    if labels_config.get("return_type") != LABEL_RETURN_TYPE:
        raise FeatureLabelBuildError("labels config return type mismatch")
    if labels_config.get("reference_policy") != LABEL_REFERENCE_POLICY:
        raise FeatureLabelBuildError("labels config reference policy mismatch")


def assert_row_digest_matches(expected_digest: str, *frames: pd.DataFrame) -> str:
    digests = [row_universe_digest(frame.to_dict("records")) for frame in frames]
    if any(digest != expected_digest for digest in digests):
        raise FeatureLabelBuildError(f"Stage 3 row digest mismatch: {digests}; expected {expected_digest}")
    return expected_digest


def aligned_record_from_dict(record: dict[str, Any]):
    from event_state_forecasting.features.news_alignment import AlignedNewsRecord

    return AlignedNewsRecord(
        article_id=str(record["article_id"]),
        ticker=str(record["ticker"]),
        published_timestamp=str(record["published_timestamp"]),
        aligned_as_of_date=str(record["aligned_as_of_date"]),
        roll_forward_reason=str(record["roll_forward_reason"]),
        title=str(record.get("title", "")),
        summary=str(record.get("summary", "")),
        url=str(record.get("url", "")),
        text_hash=str(record.get("text_hash", "")),
    )


def resolve_dataset_root(path: Path) -> Path:
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if (path / "dataset_manifest.json").exists():
        return path
    candidates = sorted((child for child in path.iterdir() if (child / "dataset_manifest.json").exists()), key=lambda item: item.stat().st_mtime)
    if not candidates:
        raise FeatureLabelBuildError(f"no Stage 2 dataset manifest found under {path}")
    return candidates[-1]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise FeatureLabelBuildError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
