#!/usr/bin/env python3
"""Run a non-destructive Stage 2-6 rebuild from the merged Alpha Vantage raw root.

The historical Stage 2-6 implementation currently lives under deprecated/v0p9.
This wrapper uses that implementation without modifying it, but swaps in an
enhanced Alpha Vantage reader that consumes all merged NEWS_SENTIMENT windows
for each ticker with article-level deduplication across annual/quarterly/monthly
files. Outputs are new versioned artifacts; existing datasets, models, and
benchmark runs are not deleted or overwritten.
"""

from __future__ import annotations

import argparse
import importlib.util
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import UTC, date, datetime
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any, Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPRECATED_SRC = PROJECT_ROOT / "deprecated" / "v0p9" / "src"
if str(DEPRECATED_SRC) not in sys.path:
    sys.path.insert(0, str(DEPRECATED_SRC))


def install_deprecated_event_state_package() -> None:
    existing = sys.modules.get("event_state_forecasting")
    if existing is not None:
        existing_paths = [Path(value).resolve() for value in getattr(existing, "__path__", [])]
        if DEPRECATED_SRC.resolve() in existing_paths:
            return
        raise RuntimeError("event_state_forecasting is already imported from a non-v0p9 source tree")

    spec = importlib.util.spec_from_file_location(
        "event_state_forecasting",
        DEPRECATED_SRC / "__init__.py",
        submodule_search_locations=[str(DEPRECATED_SRC)],
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load deprecated package alias from {DEPRECATED_SRC}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["event_state_forecasting"] = module
    spec.loader.exec_module(module)


install_deprecated_event_state_package()

from event_state_forecasting.dataset import panel_builder  # type: ignore  # noqa: E402
from event_state_forecasting.cli import build_features_and_labels as stage3_cli  # type: ignore  # noqa: E402
from event_state_forecasting.cli import build_splits_and_packet as stage4_cli  # type: ignore  # noqa: E402
from event_state_forecasting.cli import train_models_and_predict as stage5_cli  # type: ignore  # noqa: E402
from event_state_forecasting.cli import run_benchmark as stage6_cli  # type: ignore  # noqa: E402
from event_state_forecasting.features import event_state as event_state_module  # type: ignore  # noqa: E402
from event_state_forecasting.features.news_alignment import align_news_as_of_close  # type: ignore  # noqa: E402


DEFAULT_MERGED_ALPHAVANTAGE_ROOT = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "alphavantage_merged_versions"
    / "alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z"
    / "alphavantage"
)
DEFAULT_BASELINE_STAGE6_ROOT = (
    PROJECT_ROOT
    / "data"
    / "benchmark_runs"
    / "phase1_top50"
    / "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1"
)
DEFAULT_TWELVEDATA_FULL_WINDOW = "time_series__2010-01-01__2026-05-13.json"
NEWS_FILE_RE = re.compile(r"^news_sentiment__(\d{4}-\d{2}-\d{2})__(\d{4}-\d{2}-\d{2}|current)\.json$")
ZONE_IDENTIFIER_MARKER = "Zone.Identifier"
PROVIDER_LIMIT = 1000


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run enhanced Alpha Vantage all-window Stage 2-6 rebuild.")
    parser.add_argument("--raw-alphavantage-root", type=Path, default=DEFAULT_MERGED_ALPHAVANTAGE_ROOT)
    parser.add_argument("--raw-twelvedata-root", type=Path, default=PROJECT_ROOT / "data" / "raw" / "twelvedata")
    parser.add_argument("--twelvedata-full-window-filename", default=DEFAULT_TWELVEDATA_FULL_WINDOW)
    parser.add_argument("--universe-path", type=Path, default=PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv")
    parser.add_argument("--stage1-manifest-path", type=Path, default=PROJECT_ROOT / "data" / "manifests" / "stage1_raw_security_coverage_audit_2026-05-12.json")
    parser.add_argument("--stage1-ohlcv-manifest-path", type=Path, default=PROJECT_ROOT / "data" / "manifests" / "stage1_universe_ohlcv_audit_2026-05-14.json")
    parser.add_argument("--twelvedata-audit-path", type=Path, default=PROJECT_ROOT / "data" / "manifests" / "twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json")
    parser.add_argument("--stage2-contract-manifest-path", type=Path, default=PROJECT_ROOT / "data" / "manifests" / "stage2_dataset_contract_definition_2026-05-12.json")
    parser.add_argument("--features-config", type=Path, default=PROJECT_ROOT / "configs" / "features.yaml")
    parser.add_argument("--labels-config", type=Path, default=PROJECT_ROOT / "configs" / "labels.yaml")
    parser.add_argument("--splits-config", type=Path, default=PROJECT_ROOT / "configs" / "splits.yaml")
    parser.add_argument("--artifact-packet-config", type=Path, default=PROJECT_ROOT / "configs" / "artifact_packet.yaml")
    parser.add_argument("--model-config", type=Path, default=PROJECT_ROOT / "configs" / "models.yaml")
    parser.add_argument("--evaluation-config", type=Path, default=PROJECT_ROOT / "configs" / "evaluation.yaml")
    parser.add_argument("--dataset-output-root", type=Path, default=PROJECT_ROOT / "data" / "datasets" / "phase1_top50")
    parser.add_argument("--stage3-output-root", type=Path, default=PROJECT_ROOT / "data" / "features" / "phase1_top50")
    parser.add_argument("--stage4-output-root", type=Path, default=PROJECT_ROOT / "data" / "splits" / "phase1_top50")
    parser.add_argument("--stage5-output-family-root", type=Path, default=PROJECT_ROOT / "data" / "models" / "phase1_top50")
    parser.add_argument("--stage6-output-family-root", type=Path, default=PROJECT_ROOT / "data" / "benchmark_runs" / "phase1_top50")
    parser.add_argument("--baseline-stage6-root", type=Path, default=DEFAULT_BASELINE_STAGE6_ROOT)
    parser.add_argument("--comparison-only", action="store_true", help="Write comparison artifacts for existing enhanced outputs without rerunning Stage 2-6.")
    parser.add_argument("--enhanced-stage2-root", type=Path, default=None)
    parser.add_argument("--enhanced-stage3-root", type=Path, default=None)
    parser.add_argument("--enhanced-stage6-root", type=Path, default=None)
    parser.add_argument("--json", action="store_true", help="Print full JSON summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    if args.comparison_only:
        return run_comparison_only(args)

    raw_root = resolve_project_path(args.raw_alphavantage_root)
    if not raw_root.exists():
        raise SystemExit(f"merged Alpha Vantage root does not exist: {raw_root}")

    install_enhanced_news_readers()

    stage2_outputs = panel_builder.build_stage2_benchmark_dataset(
        output_root=resolve_project_path(args.dataset_output_root),
        universe_path=resolve_project_path(args.universe_path),
        raw_twelvedata_root=resolve_project_path(args.raw_twelvedata_root),
        raw_alphavantage_root=raw_root,
        stage1_manifest_path=resolve_project_path(args.stage1_manifest_path),
        stage1_ohlcv_manifest_path=resolve_project_path(args.stage1_ohlcv_manifest_path),
        twelvedata_audit_path=resolve_project_path(args.twelvedata_audit_path),
        stage2_contract_manifest_path=resolve_project_path(args.stage2_contract_manifest_path),
        twelvedata_full_window_filename=args.twelvedata_full_window_filename,
        allow_overwrite=False,
    )

    stage3_outputs = stage3_cli.run_feature_label_build(
        dataset_root=stage2_outputs.dataset_root,
        output_root=resolve_project_path(args.stage3_output_root),
        features_config_path=resolve_project_path(args.features_config),
        labels_config_path=resolve_project_path(args.labels_config),
        raw_twelvedata_root=resolve_project_path(args.raw_twelvedata_root),
        twelvedata_full_window_filename=args.twelvedata_full_window_filename,
        raw_alphavantage_root=raw_root,
        allow_overwrite=False,
    )

    stage4_outputs = stage4_cli.run_stage4_build(
        stage3_root=stage3_outputs.artifact_root,
        output_root=resolve_project_path(args.stage4_output_root),
        splits_config_path=resolve_project_path(args.splits_config),
        artifact_packet_config_path=resolve_project_path(args.artifact_packet_config),
        allow_overwrite=False,
    )
    stage4_root = Path(stage4_outputs["artifact_root"])
    stage4_version = stage4_outputs["artifact_version"]
    stage5_version = f"{stage4_version}__stage5_models_v1"
    stage5_root = resolve_project_path(args.stage5_output_family_root) / stage5_version
    fail_if_exists(stage5_root, "Stage 5")

    stage5_status = stage5_cli.main(
        [
            "--feature-root",
            str(stage3_outputs.artifact_root),
            "--split-root",
            str(stage4_root),
            "--model-config",
            str(resolve_project_path(args.model_config)),
            "--split-config",
            str(resolve_project_path(args.splits_config)),
            "--packet-config",
            str(resolve_project_path(args.artifact_packet_config)),
            "--output-root",
            str(stage5_root),
        ]
    )
    if stage5_status != 0:
        raise SystemExit(stage5_status)

    stage6_version = f"{stage5_version}__stage6_reporting_v1"
    stage6_root = resolve_project_path(args.stage6_output_family_root) / stage6_version
    fail_if_exists(stage6_root, "Stage 6")
    stage6_cli.STAGE6_VERSION = stage6_version
    stage6_status = stage6_cli.main(
        [
            "--feature-root",
            str(stage3_outputs.artifact_root),
            "--split-root",
            str(stage4_root),
            "--model-root",
            str(stage5_root),
            "--evaluation-config",
            str(resolve_project_path(args.evaluation_config)),
            "--split-config",
            str(resolve_project_path(args.splits_config)),
            "--packet-config",
            str(resolve_project_path(args.artifact_packet_config)),
            "--output-root",
            str(stage6_root),
        ]
    )
    if stage6_status != 0:
        raise SystemExit(stage6_status)

    comparison = build_enhanced_comparison(
        baseline_stage6_root=resolve_project_path(args.baseline_stage6_root),
        enhanced_stage6_root=stage6_root,
        enhanced_stage3_root=stage3_outputs.artifact_root,
        enhanced_stage2_root=stage2_outputs.dataset_root,
    )
    comparison_json = stage6_root / "enhanced_vs_baseline_comparison.json"
    comparison_md = stage6_root / "enhanced_vs_baseline_comparison.md"
    write_json(comparison_json, comparison)
    comparison_md.write_text(render_comparison_markdown(comparison), encoding="utf-8")

    summary = {
        "status": "enhanced_stage2_6_pipeline_completed",
        "benchmark_claim": False,
        "raw_alphavantage_root": str(raw_root),
        "news_file_mode": "all_windows_cross_file_article_deduped",
        "stage2_dataset_root": str(stage2_outputs.dataset_root),
        "stage2_dataset_version": stage2_outputs.dataset_version,
        "stage3_artifact_root": str(stage3_outputs.artifact_root),
        "stage4_artifact_root": str(stage4_root),
        "stage5_model_root": str(stage5_root),
        "stage6_root": str(stage6_root),
        "comparison_json": str(comparison_json),
        "comparison_markdown": str(comparison_md),
        "comparison_result_class_baseline": comparison["baseline"]["result_class"],
        "comparison_result_class_enhanced": comparison["enhanced"]["result_class"],
        "enhanced_stage3_aligned_news_rows": comparison["enhanced"]["stage3_aligned_news_rows"],
        "baseline_stage3_aligned_news_rows": comparison["baseline"].get("stage3_aligned_news_rows"),
        "non_claims": [
            "not_live_provider_call",
            "not_canonical_raw_overwrite",
            "not_provider_level_article_completeness",
            "not_positive_claim_approval",
            "not_benchmark_comparability_promotion",
        ],
    }
    print_summary(summary, as_json=bool(args.json))
    return 0


def run_comparison_only(args: argparse.Namespace) -> int:
    required_roots = {
        "--enhanced-stage2-root": args.enhanced_stage2_root,
        "--enhanced-stage3-root": args.enhanced_stage3_root,
        "--enhanced-stage6-root": args.enhanced_stage6_root,
    }
    missing = [name for name, value in required_roots.items() if value is None]
    if missing:
        raise SystemExit(f"comparison-only requires: {', '.join(missing)}")

    enhanced_stage2_root = resolve_project_path(args.enhanced_stage2_root)
    enhanced_stage3_root = resolve_project_path(args.enhanced_stage3_root)
    enhanced_stage6_root = resolve_project_path(args.enhanced_stage6_root)
    expected_files = {
        "Stage 2": enhanced_stage2_root / "dataset_manifest.json",
        "Stage 3": enhanced_stage3_root / "feature_label_manifest.json",
        "Stage 6": enhanced_stage6_root / "comparison_summary.json",
    }
    missing_files = [f"{label}: {path}" for label, path in expected_files.items() if not path.is_file()]
    if missing_files:
        raise SystemExit("comparison-only missing required artifacts: " + "; ".join(missing_files))

    comparison = build_enhanced_comparison(
        baseline_stage6_root=resolve_project_path(args.baseline_stage6_root),
        enhanced_stage6_root=enhanced_stage6_root,
        enhanced_stage3_root=enhanced_stage3_root,
        enhanced_stage2_root=enhanced_stage2_root,
    )
    comparison_json = enhanced_stage6_root / "enhanced_vs_baseline_comparison.json"
    comparison_md = enhanced_stage6_root / "enhanced_vs_baseline_comparison.md"
    write_json(comparison_json, comparison)
    comparison_md.write_text(render_comparison_markdown(comparison), encoding="utf-8")

    summary = {
        "status": "enhanced_stage2_6_comparison_completed",
        "benchmark_claim": False,
        "stage2_dataset_root": str(enhanced_stage2_root),
        "stage3_artifact_root": str(enhanced_stage3_root),
        "stage6_root": str(enhanced_stage6_root),
        "comparison_json": str(comparison_json),
        "comparison_markdown": str(comparison_md),
        "comparison_result_class_baseline": comparison["baseline"]["result_class"],
        "comparison_result_class_enhanced": comparison["enhanced"]["result_class"],
        "enhanced_stage3_aligned_news_rows": comparison["enhanced"]["stage3_aligned_news_rows"],
        "baseline_stage3_aligned_news_rows": comparison["baseline"].get("stage3_aligned_news_rows"),
    }
    print_comparison_only_summary(summary, as_json=bool(args.json))
    return 0


def install_enhanced_news_readers() -> None:
    panel_builder.load_alphavantage_news_counts = load_all_window_alphavantage_news_counts
    event_state_module.load_and_align_alphavantage_articles = load_and_align_all_window_alphavantage_articles
    stage3_cli.load_and_align_alphavantage_articles = load_and_align_all_window_alphavantage_articles


def load_all_window_alphavantage_news_counts(
    raw_root: Path | str,
    tickers: Iterable[str],
    start_year: int,
    end_year: int,
    stage1_manifest: dict[str, Any],
) -> tuple[dict[tuple[str, date], int], dict[tuple[str, int], dict[str, Any]], list[Path]]:
    raw_root = Path(raw_root)
    counts: Counter[tuple[str, date]] = Counter()
    status: dict[tuple[str, int], dict[str, Any]] = {}
    source_paths: list[Path] = []
    old_likely_truncated = set(stage1_manifest.get("likely_truncated_window_ids") or [])
    by_year_article_ids: dict[tuple[str, int], set[str]] = defaultdict(set)
    by_year_truncated: dict[tuple[str, int], bool] = defaultdict(bool)
    by_year_source_paths: dict[tuple[str, int], list[Path]] = defaultdict(list)

    for ticker in tickers:
        articles, audit = load_unique_articles_for_ticker(raw_root, ticker, start_year=start_year, end_year=end_year)
        source_paths.extend(audit["source_paths"])
        for article_id, article in articles.items():
            published = parse_alpha_date(article["time_published"], audit["article_source_path_by_id"][article_id])
            if start_year <= published.year <= end_year:
                counts[(ticker, published)] += 1
                by_year_article_ids[(ticker, published.year)].add(article_id)
        for item in audit["file_audits"]:
            for year in range(start_year, end_year + 1):
                if item["window_start_year"] <= year <= item["window_end_year"]:
                    by_year_source_paths[(ticker, year)].append(item["path"])
                    if item["feed_count"] >= PROVIDER_LIMIT:
                        by_year_truncated[(ticker, year)] = True

        for year in range(start_year, end_year + 1):
            year_key = panel_builder._stage1_year_key(year)
            truncation_flag = by_year_truncated[(ticker, year)] or f"{ticker}:{year_key}:1000" in old_likely_truncated
            unique_count = len(by_year_article_ids[(ticker, year)])
            empty_flag = unique_count == 0
            if truncation_flag:
                window_status = "all_window_files_present_with_truncation_risk"
            elif empty_flag:
                window_status = "all_window_files_present_empty_feed"
            else:
                window_status = "all_window_files_present"
            paths = by_year_source_paths[(ticker, year)]
            status[(ticker, year)] = {
                "path": paths[0] if paths else raw_root / ticker,
                "source_file_count": len(paths),
                "feed_count": unique_count,
                "provider_truncation_risk_flag": bool(truncation_flag),
                "provider_empty_feed_flag": bool(empty_flag),
                "news_provider_window_status": window_status,
                "news_file_mode": "all_windows_cross_file_article_deduped",
            }
    return dict(counts), status, source_paths


def load_and_align_all_window_alphavantage_articles(
    *,
    raw_root: Path,
    tickers: list[str],
    trading_dates: list[Any],
    start_year: int,
    end_year: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    raw_records: list[dict[str, str]] = []
    source_files: list[str] = []
    source_occurrence_count = 0
    zone_sidecars_skipped = 0
    for ticker in tickers:
        articles, audit = load_unique_articles_for_ticker(raw_root, ticker, start_year=start_year, end_year=end_year)
        raw_records.extend(articles.values())
        source_files.extend(str(path) for path in audit["source_paths"])
        source_occurrence_count += int(audit["source_occurrence_count"])
        zone_sidecars_skipped += int(audit["zone_sidecars_skipped"])

    aligned, summary = align_news_as_of_close(raw_records, trading_dates)
    frame = pd.DataFrame.from_records([asdict(record) for record in aligned])
    if frame.empty:
        frame = pd.DataFrame(columns=["article_id", "ticker", "published_timestamp", "aligned_as_of_date", "roll_forward_reason", "title", "summary", "url", "text_hash"])
    summary["news_file_mode"] = "all_windows_cross_file_article_deduped"
    summary["source_file_count"] = len(source_files)
    summary["source_files"] = source_files
    summary["raw_article_source_occurrence_count"] = source_occurrence_count
    summary["deduplicated_article_count"] = len(raw_records)
    summary["cross_file_duplicate_article_occurrences_removed"] = source_occurrence_count - len(raw_records)
    summary["zone_identifier_sidecars_skipped"] = zone_sidecars_skipped
    return frame, summary


def load_unique_articles_for_ticker(raw_root: Path, ticker: str, *, start_year: int, end_year: int) -> tuple[dict[str, dict[str, str]], dict[str, Any]]:
    ticker_root = raw_root / ticker
    if not ticker_root.exists():
        raise RuntimeError(f"missing Alpha Vantage ticker root: {ticker_root}")
    articles: dict[str, dict[str, str]] = {}
    source_paths: list[Path] = []
    article_source_path_by_id: dict[str, Path] = {}
    file_audits: list[dict[str, Any]] = []
    source_occurrence_count = 0
    zone_sidecars_skipped = 0
    for path in sorted(item for item in ticker_root.iterdir() if item.is_file()):
        if ZONE_IDENTIFIER_MARKER in path.name:
            zone_sidecars_skipped += 1
            continue
        parsed = parse_news_window(path.name)
        if parsed is None:
            continue
        window_start, window_end = parsed
        if window_end.year < start_year or window_start.year > end_year:
            continue
        payload = read_json(path)
        feed = payload.get("feed", [])
        if not isinstance(feed, list):
            raise RuntimeError(f"Alpha Vantage feed is not a list: {path}")
        source_paths.append(path)
        file_audits.append(
            {
                "path": path,
                "feed_count": len(feed),
                "window_start_year": window_start.year,
                "window_end_year": window_end.year,
            }
        )
        for item in feed:
            if not isinstance(item, dict):
                raise RuntimeError(f"malformed Alpha Vantage feed item: {path}")
            normalized = event_state_module.normalize_raw_article(ticker, item)
            published = parse_alpha_date(normalized["time_published"], path)
            if not (start_year <= published.year <= end_year):
                continue
            source_occurrence_count += 1
            article_id = normalized["article_id"]
            if article_id not in articles:
                articles[article_id] = normalized
                article_source_path_by_id[article_id] = path
    return articles, {
        "source_paths": source_paths,
        "file_audits": file_audits,
        "article_source_path_by_id": article_source_path_by_id,
        "source_occurrence_count": source_occurrence_count,
        "zone_sidecars_skipped": zone_sidecars_skipped,
    }


def parse_news_window(file_name: str) -> tuple[date, date] | None:
    match = NEWS_FILE_RE.match(file_name)
    if not match:
        return None
    start = date.fromisoformat(match.group(1))
    end = date(start.year, 12, 31) if match.group(2) == "current" else date.fromisoformat(match.group(2))
    return start, end


def parse_alpha_date(value: Any, source_path: Path) -> date:
    text = str(value or "")
    try:
        return datetime.strptime(text[:8], "%Y%m%d").date()
    except ValueError as exc:
        raise RuntimeError(f"invalid Alpha Vantage time_published in {source_path}: {text}") from exc


def build_enhanced_comparison(
    *,
    baseline_stage6_root: Path,
    enhanced_stage6_root: Path,
    enhanced_stage3_root: Path,
    enhanced_stage2_root: Path,
) -> dict[str, Any]:
    baseline_summary = read_json(baseline_stage6_root / "comparison_summary.json")
    enhanced_summary = read_json(enhanced_stage6_root / "comparison_summary.json")
    baseline_comparability = read_json(baseline_stage6_root / "benchmark_comparability.json")
    enhanced_comparability = read_json(enhanced_stage6_root / "benchmark_comparability.json")
    baseline_metrics = pd.read_parquet(baseline_stage6_root / "metrics.parquet")
    enhanced_metrics = pd.read_parquet(enhanced_stage6_root / "metrics.parquet")
    enhanced_stage3_manifest = read_json(enhanced_stage3_root / "feature_label_manifest.json")
    enhanced_stage2_manifest = read_json(enhanced_stage2_root / "dataset_manifest.json")
    baseline_stage3_rows = infer_baseline_stage3_aligned_rows(baseline_stage6_root)

    metric_comparison = compare_event_state_metrics(baseline_metrics, enhanced_metrics)
    return {
        "artifact_type": "enhanced_alphavantage_stage2_6_vs_baseline_comparison",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "baseline": {
            "stage6_root": str(baseline_stage6_root),
            "result_class": baseline_summary.get("result_class"),
            "result_reason": baseline_summary.get("result_reason"),
            "comparability_classification": baseline_comparability.get("comparability_classification"),
            "primary_horizon_counts": baseline_summary.get("primary_horizon_counts"),
            "stage3_aligned_news_rows": baseline_stage3_rows,
        },
        "enhanced": {
            "stage2_root": str(enhanced_stage2_root),
            "stage3_root": str(enhanced_stage3_root),
            "stage6_root": str(enhanced_stage6_root),
            "result_class": enhanced_summary.get("result_class"),
            "result_reason": enhanced_summary.get("result_reason"),
            "comparability_classification": enhanced_comparability.get("comparability_classification"),
            "primary_horizon_counts": enhanced_summary.get("primary_horizon_counts"),
            "stage3_aligned_news_rows": enhanced_stage3_manifest.get("news_alignment", {}).get("aligned_record_count"),
            "stage3_deduplicated_article_count": enhanced_stage3_manifest.get("news_alignment", {}).get("deduplicated_article_count"),
            "stage3_cross_file_duplicate_article_occurrences_removed": enhanced_stage3_manifest.get("news_alignment", {}).get("cross_file_duplicate_article_occurrences_removed"),
            "stage2_rows_with_news": enhanced_stage2_manifest.get("availability", {}).get("rows_with_news_count"),
            "stage2_no_news_rows": enhanced_stage2_manifest.get("availability", {}).get("no_news_row_count"),
        },
        "event_state_metric_comparison": metric_comparison,
        "interpretation_guardrails": [
            "Comparison is local artifact evidence only.",
            "Provider-level article completeness is still not claimed.",
            "Positive benchmark language and comparability promotion remain approval-gated.",
        ],
    }


def compare_event_state_metrics(baseline_metrics: pd.DataFrame, enhanced_metrics: pd.DataFrame) -> list[dict[str, Any]]:
    columns = ["split_role", "horizon_id", "model_id", "rmse", "mae", "mean_squared_loss_diff", "mean_absolute_loss_diff"]
    base = baseline_metrics[(baseline_metrics["aggregation_level"] == "aggregate") & (baseline_metrics["model_id"] == "event_state_gated_fusion")][columns].copy()
    enh = enhanced_metrics[(enhanced_metrics["aggregation_level"] == "aggregate") & (enhanced_metrics["model_id"] == "event_state_gated_fusion")][columns].copy()
    merged = enh.merge(base, on=["split_role", "horizon_id", "model_id"], suffixes=("_enhanced", "_baseline"), how="outer", validate="one_to_one")
    for metric in ["rmse", "mae", "mean_squared_loss_diff", "mean_absolute_loss_diff"]:
        merged[f"{metric}_enhanced_minus_baseline"] = merged[f"{metric}_enhanced"] - merged[f"{metric}_baseline"]
    merged = merged.sort_values(["split_role", "horizon_id"])
    return json.loads(merged.to_json(orient="records"))


def infer_baseline_stage3_aligned_rows(baseline_stage6_root: Path) -> int | None:
    manifest_path = baseline_stage6_root / "evaluation_manifest.json"
    if not manifest_path.exists():
        return None
    manifest = read_json(manifest_path)
    input_version = manifest.get("identity", {}).get("input_feature_artifact_version")
    candidate_values = [
        manifest.get("inputs", {}).get("feature_label_manifest"),
        manifest.get("artifacts", {}).get("feature_label_manifest"),
        str(PROJECT_ROOT / "data" / "features" / "phase1_top50" / input_version / "feature_label_manifest.json") if input_version else None,
        str(
            PROJECT_ROOT
            / "data"
            / "features"
            / "phase1_top50"
            / "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
            / "feature_label_manifest.json"
        ),
    ]
    for candidate_value in candidate_values:
        if not candidate_value:
            continue
        feature_manifest_path = Path(candidate_value)
        if not feature_manifest_path.is_file():
            continue
        feature_manifest = read_json(feature_manifest_path)
        value = feature_manifest.get("news_alignment", {}).get("aligned_record_count")
        return int(value) if value is not None else None
    return None


def render_comparison_markdown(comparison: dict[str, Any]) -> str:
    rows = []
    for item in comparison["event_state_metric_comparison"]:
        rows.append(
            "| {split_role} | {horizon_id} | {rmse_delta} | {mae_delta} | {mse_loss_delta} | {mae_loss_delta} |".format(
                split_role=item["split_role"],
                horizon_id=item["horizon_id"],
                rmse_delta=item.get("rmse_enhanced_minus_baseline"),
                mae_delta=item.get("mae_enhanced_minus_baseline"),
                mse_loss_delta=item.get("mean_squared_loss_diff_enhanced_minus_baseline"),
                mae_loss_delta=item.get("mean_absolute_loss_diff_enhanced_minus_baseline"),
            )
        )
    return "\n".join(
        [
            "# Enhanced Alpha Vantage Stage 2-6 Comparison",
            "",
            f"Baseline result class: `{comparison['baseline']['result_class']}`.",
            f"Enhanced result class: `{comparison['enhanced']['result_class']}`.",
            f"Baseline aligned news rows: `{comparison['baseline'].get('stage3_aligned_news_rows')}`.",
            f"Enhanced aligned news rows: `{comparison['enhanced'].get('stage3_aligned_news_rows')}`.",
            "",
            "## Event-State Aggregate Metric Deltas",
            "",
            "Negative RMSE/MAE deltas mean the enhanced run has lower error than the baseline run for the event-state model. Loss-diff deltas are reported without promotion language.",
            "",
            "| Split | Horizon | RMSE Enhanced Minus Baseline | MAE Enhanced Minus Baseline | MSE Loss-Diff Enhanced Minus Baseline | MAE Loss-Diff Enhanced Minus Baseline |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
            *rows,
            "",
            "## Guardrails",
            "",
            "- This comparison is local artifact evidence only.",
            "- Provider-level article completeness is still not claimed.",
            "- Positive benchmark language and comparability promotion remain approval-gated.",
        ]
    ) + "\n"


def fail_if_exists(path: Path, label: str) -> None:
    if path.exists():
        raise SystemExit(f"{label} output already exists; refusing to overwrite: {path}")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print(f"status={summary['status']}")
    print(f"raw_alphavantage_root={summary['raw_alphavantage_root']}")
    print(f"stage2_dataset_root={summary['stage2_dataset_root']}")
    print(f"stage3_artifact_root={summary['stage3_artifact_root']}")
    print(f"stage4_artifact_root={summary['stage4_artifact_root']}")
    print(f"stage5_model_root={summary['stage5_model_root']}")
    print(f"stage6_root={summary['stage6_root']}")
    print(f"baseline_result_class={summary['comparison_result_class_baseline']}")
    print(f"enhanced_result_class={summary['comparison_result_class_enhanced']}")
    print(f"baseline_stage3_aligned_news_rows={summary['baseline_stage3_aligned_news_rows']}")
    print(f"enhanced_stage3_aligned_news_rows={summary['enhanced_stage3_aligned_news_rows']}")
    print(f"comparison_json={summary['comparison_json']}")


def print_comparison_only_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print(f"status={summary['status']}")
    print(f"stage2_dataset_root={summary['stage2_dataset_root']}")
    print(f"stage3_artifact_root={summary['stage3_artifact_root']}")
    print(f"stage6_root={summary['stage6_root']}")
    print(f"baseline_result_class={summary['comparison_result_class_baseline']}")
    print(f"enhanced_result_class={summary['comparison_result_class_enhanced']}")
    print(f"baseline_stage3_aligned_news_rows={summary['baseline_stage3_aligned_news_rows']}")
    print(f"enhanced_stage3_aligned_news_rows={summary['enhanced_stage3_aligned_news_rows']}")
    print(f"comparison_json={summary['comparison_json']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
