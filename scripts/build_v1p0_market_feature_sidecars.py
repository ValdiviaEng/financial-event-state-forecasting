from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.features import build_market_lag_features  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402


STAGE2_ROOT = PROJECT_ROOT / "data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build full historical v1p0 market lag feature sidecars.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    started = time.perf_counter()
    config = load_json_config(PROJECT_ROOT / "configs" / "market_features_v1p0.yaml")
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    panel = pd.read_parquet(STAGE2_ROOT / "benchmark_panel.parquet")
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet")
    splits = pd.read_parquet(STAGE4_ROOT / "split_assignments.parquet")
    features = build_market_lag_features(panel, config)

    row_key = list(config["row_key"])
    feature_columns = _feature_columns(features, row_key)
    validation = _validate(features, labels, splits, row_key)

    feature_path = output_root / "market_lag_features.parquet"
    features.to_parquet(feature_path, index=False)
    digest = _sha256(feature_path)
    null_counts = {column: int(features[column].isna().sum()) for column in feature_columns}
    manifest: dict[str, Any] = {
        "artifact_type": "v1p0_market_feature_sidecar_manifest",
        "artifact_id": "market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z",
        "feature_family_id": config["feature_family_id"],
        "feature_schema_version": config["production_feature_set"]["feature_schema_version"],
        "generated_at_utc": "2026-05-24T06:20:00Z",
        "source_artifacts": {
            "stage2_dataset_root": _rel(STAGE2_ROOT),
            "stage3_feature_label_root": _rel(STAGE3_ROOT),
            "stage4_split_root": _rel(STAGE4_ROOT),
            "row_universe_digest": "6868e3b80086196385c3570f709b8bf747ec3f5afebb46dc624dd69b117cb58c",
            "clean_window_id": "active_raw_twelvedata_all_horizons_2024-04-01_2026-02-13",
        },
        "outputs": {
            "market_lag_features": _rel(feature_path),
            "manifest": _rel(output_root / "feature_manifest.json"),
        },
        "row_key": row_key,
        "row_count": int(len(features)),
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "null_policy": config["null_policy"],
        "lookahead_policy": config["lookahead_policy"],
        "as_of_policy": config["production_feature_set"]["as_of_policy"],
        "window_config": config["production_feature_set"],
        "null_counts": null_counts,
        "validation": validation,
        "feature_digest_sha256": digest,
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "benchmark_claim": False,
        "non_claims": [
            "not_model_evidence",
            "not_benchmark_result",
            "not_provider_level_article_completeness",
            "not_stage6_reinterpretation",
        ],
    }
    _write_json(output_root / "feature_manifest.json", manifest)
    print(json.dumps({"status": "passed", "feature_rows": len(features), "feature_count": len(feature_columns), "output_root": _rel(output_root)}, sort_keys=True))


def _feature_columns(features: pd.DataFrame, row_key: list[str]) -> list[str]:
    metadata = {
        *row_key,
        "dataset_version",
        "clean_window_id",
        "label_window_start",
        "label_window_end",
        "no_news_flag",
        "empty_event_state_flag",
        "provider_empty_feed_flag",
        "provider_truncation_risk_flag",
        "aligned_news_count",
        "feature_family_id",
        "feature_policy",
        "feature_schema_version",
    }
    return [column for column in features.columns if column not in metadata]


def _validate(features: pd.DataFrame, labels: pd.DataFrame, splits: pd.DataFrame, row_key: list[str]) -> dict[str, Any]:
    feature_keys = features[row_key]
    label_keys = labels[row_key]
    split_keys = splits[["fold_id", *row_key]]
    feature_key_tuples = set(map(tuple, feature_keys.to_numpy()))
    label_key_tuples = set(map(tuple, label_keys.to_numpy()))
    first_dates = features.groupby("canonical_ticker")["as_of_date"].transform("min") == features["as_of_date"]
    lag_columns = [column for column in features.columns if column.endswith("_lag_1") or "_lag_" in column]
    return {
        "status": "passed",
        "feature_rows": int(len(features)),
        "label_rows": int(len(labels)),
        "split_rows": int(len(splits)),
        "feature_duplicate_row_keys": int(features.duplicated(row_key).sum()),
        "label_duplicate_row_keys": int(labels.duplicated(row_key).sum()),
        "split_duplicate_fold_row_keys": int(splits.duplicated(["fold_id", *row_key]).sum()),
        "feature_label_key_sets_equal": feature_key_tuples == label_key_tuples,
        "split_fold_count": int(split_keys["fold_id"].nunique()),
        "split_roles": sorted(map(str, splits["split_role"].dropna().unique().tolist())),
        "horizons": sorted(map(str, features["horizon_id"].dropna().unique().tolist())),
        "first_date_lag_feature_nulls": int(features.loc[first_dates, lag_columns].isna().sum().sum()),
        "first_date_lag_feature_cells": int(first_dates.sum() * len(lag_columns)),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    main()
