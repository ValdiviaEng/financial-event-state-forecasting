"""Stage 2 manifest-backed benchmark panel builder."""

from __future__ import annotations

import json
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

import pandas as pd

from event_state_forecasting.data.contracts import (
    APPROVED_HORIZONS,
    BENCHMARK_FAMILY_ID,
    HORIZON_TRADING_STEPS,
    NEWS_ALIGNMENT_STATUS,
    PENDING_SPLIT_ROLE,
    ROW_KEY_FIELDS,
    TARGET_FAMILY,
    ContractError,
    validate_manifest,
    validate_panel_records,
)
from event_state_forecasting.data.universe import DEFAULT_UNIVERSE_PATH, load_top50_universe
from event_state_forecasting.dataset.dataset_versioning import build_dataset_version, file_sha256, source_digest, stable_json_digest
from event_state_forecasting.dataset.row_universe import row_universe_digest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_TWELVEDATA_ROOT = PROJECT_ROOT / "data" / "raw" / "twelvedata"
DEFAULT_RAW_ALPHAVANTAGE_ROOT = PROJECT_ROOT / "data" / "raw" / "alphavantage"
DEFAULT_DATASET_OUTPUT_ROOT = PROJECT_ROOT / "data" / "datasets" / BENCHMARK_FAMILY_ID
DEFAULT_STAGE1_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage1_raw_security_coverage_audit_2026-05-12.json"
DEFAULT_STAGE1_OHLCV_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage1_universe_ohlcv_audit_2026-05-14.json"
DEFAULT_TWELVEDATA_AUDIT = PROJECT_ROOT / "data" / "manifests" / "twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json"
DEFAULT_STAGE2_CONTRACT_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage2_dataset_contract_definition_2026-05-12.json"
FULL_WINDOW_FILENAME = "time_series__2010-01-01__2026-05-13.json"
MARKET_TIMEZONE = ZoneInfo("America/New_York")


class PanelBuildError(ValueError):
    """Raised when Stage 2 panel construction cannot proceed safely."""


@dataclass(frozen=True, slots=True)
class CleanWindow:
    candidate_id: str
    start: date
    end: date
    source_manifest: Path
    status: str


@dataclass(frozen=True, slots=True)
class BuildOutputs:
    dataset_version: str
    dataset_root: Path
    panel_path: Path
    manifest_path: Path
    row_universe_digest_path: Path
    clean_window_path: Path
    cvx_patch_manifest_path: Path
    row_count: int
    row_digest: str
    manifest: dict[str, Any]


def build_stage2_benchmark_dataset(
    *,
    output_root: Path | str = DEFAULT_DATASET_OUTPUT_ROOT,
    universe_path: Path | str = DEFAULT_UNIVERSE_PATH,
    raw_twelvedata_root: Path | str = DEFAULT_RAW_TWELVEDATA_ROOT,
    raw_alphavantage_root: Path | str = DEFAULT_RAW_ALPHAVANTAGE_ROOT,
    stage1_manifest_path: Path | str = DEFAULT_STAGE1_MANIFEST,
    stage1_ohlcv_manifest_path: Path | str = DEFAULT_STAGE1_OHLCV_MANIFEST,
    twelvedata_audit_path: Path | str = DEFAULT_TWELVEDATA_AUDIT,
    stage2_contract_manifest_path: Path | str = DEFAULT_STAGE2_CONTRACT_MANIFEST,
    twelvedata_full_window_filename: str = FULL_WINDOW_FILENAME,
    allow_overwrite: bool = False,
) -> BuildOutputs:
    """Build the approved Stage 2 top-50 panel and write Parquet/JSON artifacts."""

    output_root = Path(output_root)
    universe_path = Path(universe_path)
    raw_twelvedata_root = Path(raw_twelvedata_root)
    raw_alphavantage_root = Path(raw_alphavantage_root)
    stage1_manifest_path = Path(stage1_manifest_path)
    stage1_ohlcv_manifest_path = Path(stage1_ohlcv_manifest_path)
    twelvedata_audit_path = Path(twelvedata_audit_path)
    stage2_contract_manifest_path = Path(stage2_contract_manifest_path)

    universe = load_top50_universe(universe_path)
    stage1_manifest = _read_json(stage1_manifest_path)
    twelvedata_audit = _read_json(twelvedata_audit_path)
    stage2_contract = _read_json(stage2_contract_manifest_path)
    _assert_approved_scope(stage1_manifest, stage2_contract)

    clean_window = load_clean_window(stage1_ohlcv_manifest_path)
    tickers = universe.tickers
    support_ticker = "SPY"
    price_by_ticker, price_source_paths, patch_events = load_twelvedata_prices(
        raw_twelvedata_root,
        (*tickers, support_ticker),
        full_window_filename=twelvedata_full_window_filename,
    )
    common_dates = _common_price_dates(price_by_ticker, (*tickers, support_ticker))
    as_of_dates = [value for value in common_dates if clean_window.start <= value <= clean_window.end]
    if not as_of_dates:
        raise PanelBuildError("clean window produced no as-of dates")
    _assert_horizon_endpoints_available(common_dates, as_of_dates)

    news_counts, news_status, news_source_paths = load_alphavantage_news_counts(
        raw_alphavantage_root,
        tickers,
        clean_window.start.year,
        clean_window.end.year,
        stage1_manifest,
    )

    source_paths = [
        universe_path,
        stage1_manifest_path,
        stage1_ohlcv_manifest_path,
        twelvedata_audit_path,
        stage2_contract_manifest_path,
        *price_source_paths,
        *news_source_paths,
    ]
    source_hash = source_digest(source_paths, root=PROJECT_ROOT)

    records = build_panel_records(
        tickers=tickers,
        support_ticker=support_ticker,
        clean_window=clean_window,
        common_dates=common_dates,
        as_of_dates=as_of_dates,
        price_by_ticker=price_by_ticker,
        news_counts=news_counts,
        news_status=news_status,
    )
    row_digest = row_universe_digest(records)
    clean_window_id = f"cw_{clean_window.start:%Y%m%d}_{clean_window.end:%Y%m%d}"
    dataset_version = build_dataset_version(clean_window_id=clean_window_id, source_hash=source_hash, row_hash=row_digest)
    for row in records:
        row["dataset_version"] = dataset_version
    validation_summary = validate_panel_records(records)

    dataset_root = output_root / dataset_version
    panel_path = dataset_root / "benchmark_panel.parquet"
    manifest_path = dataset_root / "dataset_manifest.json"
    row_digest_path = dataset_root / "row_universe_digest.json"
    clean_window_path = dataset_root / "clean_window_decision.json"
    cvx_patch_manifest_path = dataset_root / "cvx_derived_ohlc_patch_manifest.json"

    if dataset_root.exists():
        if not allow_overwrite:
            raise PanelBuildError(f"dataset output already exists: {dataset_root}")
        shutil.rmtree(dataset_root)
    dataset_root.mkdir(parents=True, exist_ok=False)

    frame = pd.DataFrame.from_records(records)
    frame.to_parquet(panel_path, partition_cols=["horizon_id"], index=False, engine="pyarrow")
    panel_digest = directory_sha256(panel_path)

    row_digest_record = build_row_digest_record(records, dataset_version, row_digest, validation_summary.horizon_counts)
    clean_window_record = build_clean_window_record(clean_window, common_dates, as_of_dates)
    audit_patch_candidates = _extract_audit_cvx_patch_candidates(twelvedata_audit)
    cvx_patch_manifest = build_cvx_patch_manifest(
        patch_events,
        price_source_paths,
        audit_patch_candidates,
        selected_full_window_filename=twelvedata_full_window_filename,
    )
    manifest = build_dataset_manifest(
        dataset_version=dataset_version,
        records=records,
        validation_summary=validation_summary,
        tickers=tickers,
        support_ticker=support_ticker,
        clean_window=clean_window,
        source_paths=source_paths,
        source_hash=source_hash,
        row_digest=row_digest,
        panel_path=panel_path,
        panel_digest=panel_digest,
        row_digest_path=row_digest_path,
        clean_window_path=clean_window_path,
        cvx_patch_manifest_path=cvx_patch_manifest_path,
        stage1_manifest=stage1_manifest,
        news_status=news_status,
        patch_events=patch_events,
        audit_patch_candidates=audit_patch_candidates,
        twelvedata_full_window_filename=twelvedata_full_window_filename,
    )
    validate_manifest(manifest)

    _write_json(row_digest_path, row_digest_record)
    _write_json(clean_window_path, clean_window_record)
    _write_json(cvx_patch_manifest_path, cvx_patch_manifest)
    _write_json(manifest_path, manifest)

    return BuildOutputs(
        dataset_version=dataset_version,
        dataset_root=dataset_root,
        panel_path=panel_path,
        manifest_path=manifest_path,
        row_universe_digest_path=row_digest_path,
        clean_window_path=clean_window_path,
        cvx_patch_manifest_path=cvx_patch_manifest_path,
        row_count=validation_summary.row_count,
        row_digest=row_digest,
        manifest=manifest,
    )


def load_clean_window(stage1_ohlcv_manifest_path: Path | str = DEFAULT_STAGE1_OHLCV_MANIFEST) -> CleanWindow:
    manifest_path = Path(stage1_ohlcv_manifest_path)
    manifest = _read_json(manifest_path)
    candidate = (((manifest.get("active_raw_twelvedata") or {}).get("clean_window_candidate_from_raw")) or {})
    start_value = candidate.get("all_horizons_candidate_as_of_start")
    end_value = candidate.get("all_horizons_candidate_as_of_end")
    if not start_value or not end_value:
        raise PanelBuildError("active raw Twelve Data all-horizon clean-window candidate is missing")
    start = _parse_date(start_value)
    end = _parse_date(end_value)
    return CleanWindow(
        candidate_id=f"active_raw_twelvedata_all_horizons_{start.isoformat()}_{end.isoformat()}",
        start=start,
        end=end,
        source_manifest=manifest_path,
        status="selected_for_stage2_materialized_dataset",
    )


def load_twelvedata_prices(
    raw_root: Path | str,
    tickers: Iterable[str],
    *,
    full_window_filename: str = FULL_WINDOW_FILENAME,
) -> tuple[dict[str, dict[date, dict[str, Any]]], list[Path], list[dict[str, Any]]]:
    raw_root = Path(raw_root)
    price_by_ticker: dict[str, dict[date, dict[str, Any]]] = {}
    source_paths: list[Path] = []
    patch_events: list[dict[str, Any]] = []
    for ticker in tickers:
        path = raw_root / ticker / full_window_filename
        if not path.exists():
            raise PanelBuildError(f"missing Twelve Data full-window file for {ticker}: {path}")
        payload = _read_json(path)
        values = payload.get("values")
        if not isinstance(values, list):
            raise PanelBuildError(f"Twelve Data file has no values list: {path}")
        rows: dict[date, dict[str, Any]] = {}
        for item in values:
            if not isinstance(item, dict):
                raise PanelBuildError(f"malformed Twelve Data row in {path}")
            parsed = _parse_twelvedata_row(item, ticker=ticker, source_path=path, patch_events=patch_events)
            row_date = parsed["date"]
            if row_date in rows:
                raise PanelBuildError(f"duplicate date in {path}: {row_date.isoformat()}")
            rows[row_date] = parsed
        if not rows:
            raise PanelBuildError(f"empty Twelve Data values file: {path}")
        price_by_ticker[ticker] = rows
        source_paths.append(path)
    return price_by_ticker, source_paths, patch_events


def load_alphavantage_news_counts(
    raw_root: Path | str,
    tickers: Iterable[str],
    start_year: int,
    end_year: int,
    stage1_manifest: dict[str, Any],
) -> tuple[dict[tuple[str, date], int], dict[tuple[str, int], dict[str, Any]], list[Path]]:
    raw_root = Path(raw_root)
    likely_truncated = set(stage1_manifest.get("likely_truncated_window_ids") or [])
    empty_windows = set(stage1_manifest.get("empty_window_ids") or [])
    counts: Counter[tuple[str, date]] = Counter()
    status: dict[tuple[str, int], dict[str, Any]] = {}
    source_paths: list[Path] = []
    for ticker in tickers:
        for year in range(start_year, end_year + 1):
            path = _canonical_alphavantage_path(raw_root, ticker, year)
            if not path.exists():
                raise PanelBuildError(f"missing canonical Alpha Vantage file for {ticker} {year}: {path}")
            payload = _read_json(path)
            feed = payload.get("feed", [])
            if not isinstance(feed, list):
                raise PanelBuildError(f"Alpha Vantage file has non-list feed: {path}")
            for item in feed:
                if not isinstance(item, dict):
                    raise PanelBuildError(f"malformed Alpha Vantage feed item in {path}")
                published = _parse_alpha_time_published(item.get("time_published"), path)
                counts[(ticker, published)] += 1
            year_key = _stage1_year_key(year)
            truncation_flag = f"{ticker}:{year_key}:1000" in likely_truncated
            empty_flag = len(feed) == 0 or f"{ticker}:{year_key}:0" in empty_windows
            if truncation_flag:
                window_status = "canonical_file_present_with_truncation_risk"
            elif empty_flag:
                window_status = "canonical_file_present_empty_feed"
            else:
                window_status = "canonical_file_present"
            status[(ticker, year)] = {
                "path": path,
                "feed_count": len(feed),
                "provider_truncation_risk_flag": truncation_flag,
                "provider_empty_feed_flag": empty_flag,
                "news_provider_window_status": window_status,
            }
            source_paths.append(path)
    return dict(counts), status, source_paths


def build_panel_records(
    *,
    tickers: tuple[str, ...],
    support_ticker: str,
    clean_window: CleanWindow,
    common_dates: list[date],
    as_of_dates: list[date],
    price_by_ticker: dict[str, dict[date, dict[str, Any]]],
    news_counts: dict[tuple[str, date], int],
    news_status: dict[tuple[str, int], dict[str, Any]],
) -> list[dict[str, Any]]:
    common_index = {value: idx for idx, value in enumerate(common_dates)}
    records: list[dict[str, Any]] = []
    for ticker in tickers:
        for as_of_date in as_of_dates:
            date_index = common_index[as_of_date]
            prediction_timestamp = _market_close_timestamp(as_of_date)
            price = price_by_ticker[ticker][as_of_date]
            support_price = price_by_ticker[support_ticker][as_of_date]
            news_count = int(news_counts.get((ticker, as_of_date), 0))
            year_status = news_status[(ticker, as_of_date.year)]
            no_news = news_count == 0
            for horizon_id in APPROVED_HORIZONS:
                steps = HORIZON_TRADING_STEPS[horizon_id]
                label_window_start = common_dates[date_index + 1]
                label_window_end = common_dates[date_index + steps]
                records.append(
                    {
                        "benchmark_family_id": BENCHMARK_FAMILY_ID,
                        "dataset_version": "pending_dataset_version",
                        "canonical_ticker": ticker,
                        "as_of_date": as_of_date.isoformat(),
                        "prediction_timestamp": prediction_timestamp,
                        "horizon_id": horizon_id,
                        "feature_availability_timestamp": prediction_timestamp,
                        "label_window_start": label_window_start.isoformat(),
                        "label_window_end": label_window_end.isoformat(),
                        "row_status": "active_stage2_row",
                        "exclusion_reason": "",
                        "split_role": PENDING_SPLIT_ROLE,
                        "fold_id": PENDING_SPLIT_ROLE,
                        "lockbox_flag": False,
                        "purge_flag": False,
                        "embargo_flag": False,
                        "split_exclusion_reason": "pending_stage4_split_construction",
                        "preprocessing_fit_allowed": False,
                        "market_data_available_flag": True,
                        "news_provider_window_status": year_status["news_provider_window_status"],
                        "aligned_news_count": news_count,
                        "no_news_flag": no_news,
                        "empty_event_state_flag": no_news,
                        "provider_empty_feed_flag": bool(year_status["provider_empty_feed_flag"]),
                        "provider_truncation_risk_flag": bool(year_status["provider_truncation_risk_flag"]),
                        "news_alignment_status": NEWS_ALIGNMENT_STATUS,
                        "ohlcv_provider": "Twelve Data",
                        "news_provider": "Alpha Vantage",
                        "benchmark_reference_ticker": support_ticker,
                        "market_open": price["open"],
                        "market_high": price["high"],
                        "market_low": price["low"],
                        "market_close": price["close"],
                        "market_volume": price["volume"],
                        "benchmark_close": support_price["close"],
                        "clean_window_id": clean_window.candidate_id,
                    }
                )
    return records


def build_row_digest_record(records: list[dict[str, Any]], dataset_version: str, row_digest: str, horizon_counts: dict[str, int]) -> dict[str, Any]:
    return {
        "artifact_type": "stage2_row_universe_digest",
        "dataset_version": dataset_version,
        "benchmark_family_id": BENCHMARK_FAMILY_ID,
        "row_key_fields": list(ROW_KEY_FIELDS),
        "row_count": len(records),
        "horizon_counts": horizon_counts,
        "row_universe_digest": row_digest,
        "market_only_row_universe_digest": row_digest,
        "event_state_row_universe_digest": row_digest,
        "branch_row_universe_equal": True,
        "non_claims": ["not_features", "not_labels", "not_splits", "not_predictions", "not_benchmark_result"],
    }


def build_clean_window_record(clean_window: CleanWindow, common_dates: list[date], as_of_dates: list[date]) -> dict[str, Any]:
    return {
        "artifact_type": "stage2_clean_window_decision",
        "candidate_id": clean_window.candidate_id,
        "status": clean_window.status,
        "date_start": clean_window.start.isoformat(),
        "date_end": clean_window.end.isoformat(),
        "as_of_date_count": len(as_of_dates),
        "common_price_calendar_start": common_dates[0].isoformat(),
        "common_price_calendar_end": common_dates[-1].isoformat(),
        "source_manifest": _relative_path(clean_window.source_manifest),
        "selection_basis": "user-approved active raw Twelve Data all-horizon top-50 clean-window candidate",
        "limitations": [
            "Alpha Vantage provider-level article completeness is not claimed; truncation flags remain visible.",
            "Split-adjustment method is not selected in Stage 2.",
            "Feature and label values are not materialized in Stage 2.",
        ],
    }


def build_cvx_patch_manifest(
    patch_events: list[dict[str, Any]],
    price_source_paths: list[Path],
    audit_patch_candidates: list[dict[str, Any]],
    *,
    selected_full_window_filename: str = FULL_WINDOW_FILENAME,
) -> dict[str, Any]:
    return {
        "artifact_type": "stage2_derived_cvx_ohlc_patch_manifest",
        "policy": "derived_cleaned_data_only_raw_provider_payloads_unchanged",
        "raw_files_mutated": False,
        "patch_event_count": len(patch_events),
        "patch_events": patch_events,
        "audit_reported_patch_candidate_count": len(audit_patch_candidates),
        "audit_reported_patch_candidates": audit_patch_candidates,
        "selected_full_window_filename": selected_full_window_filename,
        "selected_full_window_note": "Only selected full-window Stage 2 source rows are patched in derived records; audit-reported duplicate-window anomalies remain visible here when they do not affect selected rows.",
        "source_files_scanned": [_relative_path(path) for path in price_source_paths if path.name == selected_full_window_filename],
        "non_claims": ["not_split_adjustment", "not_raw_data_patch", "not_benchmark_result"],
    }


def build_dataset_manifest(
    *,
    dataset_version: str,
    records: list[dict[str, Any]],
    validation_summary: Any,
    tickers: tuple[str, ...],
    support_ticker: str,
    clean_window: CleanWindow,
    source_paths: list[Path],
    source_hash: str,
    row_digest: str,
    panel_path: Path,
    panel_digest: str,
    row_digest_path: Path,
    clean_window_path: Path,
    cvx_patch_manifest_path: Path,
    stage1_manifest: dict[str, Any],
    news_status: dict[tuple[str, int], dict[str, Any]],
    patch_events: list[dict[str, Any]],
    audit_patch_candidates: list[dict[str, Any]],
    twelvedata_full_window_filename: str = FULL_WINDOW_FILENAME,
) -> dict[str, Any]:
    no_news_count = sum(1 for row in records if row["no_news_flag"])
    provider_empty_count = sum(1 for row in records if row["provider_empty_feed_flag"])
    truncation_risk_count = sum(1 for row in records if row["provider_truncation_risk_flag"])
    rows_with_news = len(records) - no_news_count
    as_of_dates = sorted({row["as_of_date"] for row in records})
    ticker_counts = Counter(row["canonical_ticker"] for row in records)
    news_year_status_counts = Counter(item["news_provider_window_status"] for item in news_status.values())
    manifest = {
        "identity": {
            "artifact_type": "stage2_materialized_benchmark_dataset",
            "stage2_completion_status": "materialized_stage2_dataset_complete",
            "dataset_version": dataset_version,
            "dataset_schema_version": "stage2_panel_v1",
            "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "benchmark_claim": False,
            "materialized_dataset_created": True,
            "feature_artifacts_created": False,
            "label_artifacts_created": False,
            "split_artifacts_created": False,
            "model_artifacts_created": False,
        },
        "protected_scope": {
            "benchmark_family_id": BENCHMARK_FAMILY_ID,
            "universe": "approved_top50",
            "target_family": TARGET_FAMILY,
            "horizons": list(APPROVED_HORIZONS),
            "ohlcv_provider": "Twelve Data",
            "news_provider": "Alpha Vantage",
            "sec_role": "static_or_company_support_only_not_consumed_by_stage2_panel",
            "alignment_policy": "same_day_as_of_close_stage2_raw_date_proxy_final_alignment_pending_stage3",
            "no_news_policy": "preserve_rows_with_explicit_empty_event_state_and_indicators",
            "evaluation_protocol": "purged_embargoed_walk_forward_plus_final_untouched_lockbox_pending_stage4",
            "option_b_contract": True,
        },
        "sources": {
            "source_digest": source_hash,
            "twelvedata_full_window_filename": twelvedata_full_window_filename,
            "source_file_count": len(source_paths),
            "source_files": [_relative_path(path) for path in source_paths],
            "sensitive_artifacts_excluded": [
                "data/raw/alphavantage/news_request_ledger.jsonl",
                "runs/logs/alphavantage_news_daemon.log",
            ],
        },
        "coverage": {
            "ticker_count": len(tickers),
            "tickers": list(tickers),
            "support_ticker": support_ticker,
            "support_ticker_excluded_from_rows": True,
            "as_of_date_start": as_of_dates[0],
            "as_of_date_end": as_of_dates[-1],
            "as_of_date_count": len(as_of_dates),
            "row_count": validation_summary.row_count,
            "horizon_counts": validation_summary.horizon_counts,
            "ticker_row_count_min": min(ticker_counts.values()),
            "ticker_row_count_max": max(ticker_counts.values()),
        },
        "clean_window": {
            "candidate_id": clean_window.candidate_id,
            "status": clean_window.status,
            "date_start": clean_window.start.isoformat(),
            "date_end": clean_window.end.isoformat(),
            "source_manifest": _relative_path(clean_window.source_manifest),
        },
        "rows_and_labels": {
            "row_key_fields": list(ROW_KEY_FIELDS),
            "duplicate_key_count": validation_summary.duplicate_key_count,
            "label_values_created": False,
            "label_family_reserved": TARGET_FAMILY,
            "label_window_policy": "label_window_start is the next common trading date after as_of_date; label_window_end is the horizon-th common trading date after as_of_date",
            "approved_horizon_trading_steps": HORIZON_TRADING_STEPS,
        },
        "availability": {
            "market_data_available_rows": validation_summary.row_count,
            "news_alignment_status": NEWS_ALIGNMENT_STATUS,
            "rows_with_news_count": rows_with_news,
            "no_news_row_count": no_news_count,
            "provider_empty_feed_row_count": provider_empty_count,
            "provider_truncation_risk_row_count": truncation_risk_count,
            "news_provider_window_status_counts_by_ticker_year": dict(sorted(news_year_status_counts.items())),
        },
        "separation": {
            "split_role": PENDING_SPLIT_ROLE,
            "fold_id": PENDING_SPLIT_ROLE,
            "lockbox_flag": False,
            "purge_flag": False,
            "embargo_flag": False,
            "preprocessing_fit_allowed": False,
            "stage4_split_required_before_training": True,
        },
        "hashes": {
            "source_digest": source_hash,
            "row_universe_digest": row_digest,
            "market_only_row_universe_digest": row_digest,
            "event_state_row_universe_digest": row_digest,
            "branch_row_universe_equal": True,
            "panel_parquet_digest": panel_digest,
        },
        "limitations": [
            "Alpha Vantage provider-level article completeness is not claimed; known truncation-risk rows are flagged.",
            "Stage 2 materializes row identity, clean-window, availability, and split-eligibility fields only; feature values and label values are Stage 3 outputs.",
            "Purged/embargoed walk-forward folds and final lockbox assignments are pending Stage 4.",
            "Active split-adjustment method is not selected in Stage 2.",
            "CVX OHLC anomaly handling is applied only in derived cleaned data; raw Twelve Data files are not modified.",
        ],
        "non_claims": [
            "not_features",
            "not_labels",
            "not_splits",
            "not_models",
            "not_predictions",
            "not_metrics",
            "not_benchmark_result",
            "not_provider_level_article_completeness",
        ],
        "artifact_paths": {
            "panel_parquet": _relative_path(panel_path),
            "dataset_manifest": "dataset_manifest.json",
            "row_universe_digest": _relative_path(row_digest_path),
            "clean_window_decision": _relative_path(clean_window_path),
            "cvx_patch_manifest": _relative_path(cvx_patch_manifest_path),
        },
        "provider_limitations_from_stage1": {
            "likely_truncated_windows": stage1_manifest.get("alphavantage_top50", {}).get("likely_truncated_windows"),
            "empty_feed_windows": stage1_manifest.get("alphavantage_top50", {}).get("empty_feed_windows"),
        },
        "derived_cleaning": {
            "cvx_patch_event_count": len(patch_events),
            "cvx_audit_reported_patch_candidate_count": len(audit_patch_candidates),
            "raw_files_mutated": False,
        },
    }
    manifest["hashes"]["manifest_digest_without_self"] = stable_json_digest(manifest)
    return manifest


def directory_sha256(path: Path) -> str:
    if path.is_file():
        return file_sha256(path)
    payload = []
    for child in sorted(item for item in path.rglob("*") if item.is_file()):
        payload.append({"path": _relative_path(child, root=path), "sha256": file_sha256(child)})
    return stable_json_digest(payload)


def _assert_approved_scope(stage1_manifest: dict[str, Any], stage2_contract: dict[str, Any]) -> None:
    stage1_scope = stage1_manifest.get("scope") or {}
    stage2_scope = stage2_contract.get("scope") or {}
    if stage1_scope.get("target_family") != TARGET_FAMILY or stage2_scope.get("target_family") != TARGET_FAMILY:
        raise PanelBuildError("target family drift detected in source manifests")
    if tuple(stage1_scope.get("horizons") or ()) != APPROVED_HORIZONS or tuple(stage2_scope.get("horizons") or ()) != APPROVED_HORIZONS:
        raise PanelBuildError("approved horizon drift detected in source manifests")
    if stage2_scope.get("benchmark_family_id") != BENCHMARK_FAMILY_ID:
        raise PanelBuildError("benchmark family drift detected in Stage 2 contract manifest")


def _assert_horizon_endpoints_available(common_dates: list[date], as_of_dates: list[date]) -> None:
    common_index = {value: idx for idx, value in enumerate(common_dates)}
    max_steps = max(HORIZON_TRADING_STEPS.values())
    for as_of_date in as_of_dates:
        if common_index[as_of_date] + max_steps >= len(common_dates):
            raise PanelBuildError(f"clean-window endpoint cannot support max horizon for {as_of_date.isoformat()}")


def _common_price_dates(price_by_ticker: dict[str, dict[date, dict[str, Any]]], tickers: tuple[str, ...]) -> list[date]:
    date_sets = [set(price_by_ticker[ticker]) for ticker in tickers]
    common = sorted(set.intersection(*date_sets))
    if not common:
        raise PanelBuildError("no common Twelve Data dates across top-50 plus SPY")
    return common


def _parse_twelvedata_row(item: dict[str, Any], *, ticker: str, source_path: Path, patch_events: list[dict[str, Any]]) -> dict[str, Any]:
    row_date = _parse_date(str(item.get("datetime") or ""))
    open_value = _parse_float(item.get("open"), source_path)
    high_value = _parse_float(item.get("high"), source_path)
    low_value = _parse_float(item.get("low"), source_path)
    close_value = _parse_float(item.get("close"), source_path)
    volume_value = int(float(str(item.get("volume"))))
    if min(open_value, high_value, low_value, close_value) <= 0:
        raise PanelBuildError(f"non-positive OHLC value in {source_path} for {row_date.isoformat()}")
    if volume_value < 0:
        raise PanelBuildError(f"negative volume in {source_path} for {row_date.isoformat()}")
    expected_high = max(open_value, high_value, low_value, close_value)
    expected_low = min(open_value, high_value, low_value, close_value)
    if high_value < expected_high or low_value > expected_low:
        if ticker != "CVX":
            raise PanelBuildError(f"unexpected OHLC order anomaly for {ticker} on {row_date.isoformat()}")
        patch_events.append(
            {
                "ticker": ticker,
                "date": row_date.isoformat(),
                "source_path": _relative_path(source_path),
                "raw_open": open_value,
                "raw_high": high_value,
                "raw_low": low_value,
                "raw_close": close_value,
                "patched_high": expected_high,
                "patched_low": expected_low,
                "policy": "set high=max(open,high,low,close) and low=min(open,high,low,close) in derived records only",
                "raw_file_mutated": False,
            }
        )
        high_value = expected_high
        low_value = expected_low
    return {
        "date": row_date,
        "open": open_value,
        "high": high_value,
        "low": low_value,
        "close": close_value,
        "volume": volume_value,
    }


def _extract_audit_cvx_patch_candidates(twelvedata_audit: dict[str, Any]) -> list[dict[str, Any]]:
    quality = (((twelvedata_audit.get("coverage_by_ticker") or {}).get("CVX") or {}).get("quality") or {})
    candidates = quality.get("sample_ohlc_order_violations") or []
    result: list[dict[str, Any]] = []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        patched_high = max(float(item["open"]), float(item["high"]), float(item["low"]), float(item["close"]))
        patched_low = min(float(item["open"]), float(item["high"]), float(item["low"]), float(item["close"]))
        result.append(
            {
                "ticker": "CVX",
                "date": str(item.get("date")),
                "audit_raw_open": item.get("open"),
                "audit_raw_high": item.get("high"),
                "audit_raw_low": item.get("low"),
                "audit_raw_close": item.get("close"),
                "derived_patch_high": patched_high,
                "derived_patch_low": patched_low,
                "raw_file_mutated": False,
            }
        )
    return result


def _canonical_alphavantage_path(raw_root: Path, ticker: str, year: int) -> Path:
    if year == 2026:
        return raw_root / ticker / "news_sentiment__2026-01-01__current.json"
    return raw_root / ticker / f"news_sentiment__{year}-01-01__{year}-12-31.json"


def _stage1_year_key(year: int) -> str:
    return "2026_current" if year == 2026 else str(year)


def _parse_alpha_time_published(value: Any, source_path: Path) -> date:
    text = str(value or "")
    try:
        return datetime.strptime(text[:8], "%Y%m%d").date()
    except ValueError as exc:
        raise PanelBuildError(f"invalid Alpha Vantage time_published in {source_path}: {text}") from exc


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise PanelBuildError(f"invalid date: {value}") from exc


def _parse_float(value: Any, source_path: Path) -> float:
    try:
        return float(str(value))
    except (TypeError, ValueError) as exc:
        raise PanelBuildError(f"invalid numeric value in {source_path}: {value}") from exc


def _market_close_timestamp(value: date) -> str:
    return datetime.combine(value, time(16, 0), tzinfo=MARKET_TIMEZONE).isoformat()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PanelBuildError(f"missing JSON artifact: {path}")
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise PanelBuildError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _relative_path(path: Path, *, root: Path = PROJECT_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "BuildOutputs",
    "CleanWindow",
    "PanelBuildError",
    "build_stage2_benchmark_dataset",
    "load_clean_window",
    "load_twelvedata_prices",
    "load_alphavantage_news_counts",
]
