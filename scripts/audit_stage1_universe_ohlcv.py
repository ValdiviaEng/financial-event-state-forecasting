#!/usr/bin/env python3
"""Audit Stage 1 universe and Twelve Data OHLCV evidence.

This is an evidence audit, not a dataset builder. It verifies the frozen
top-50 universe contract, checks active and deprecated Twelve Data raw OHLCV
payload coverage, and reports active raw entries that would need download if
the project requires `data/raw/twelvedata/` residency.
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, date, datetime
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPRECATED_ROOT = PROJECT_ROOT / "deprecated_version" / "legacy_snapshot_20260402T115014Z"

TOP50_PATH = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
TOP100_PATH = PROJECT_ROOT / "data" / "raw" / "universe" / "top100_slickcharts_2026-04-10.csv"
SP500_SNAPSHOT_PATH = PROJECT_ROOT / "data" / "raw" / "universe" / "sp500_snapshot_2026-03-19.csv"
DEPRECATED_TOP50_PATH = DEPRECATED_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"

ACTIVE_RAW_TWELVEDATA_DIR = PROJECT_ROOT / "data" / "raw" / "twelvedata"
DEPRECATED_RAW_TWELVEDATA_DIR = DEPRECATED_ROOT / "data" / "raw" / "twelvedata"
DEPRECATED_MARKET_SUMMARY = DEPRECATED_ROOT / "data" / "manifests" / "whole_universe_market_extract_summary_20260319.json"
DEPRECATED_ADJUSTED_SUMMARY = DEPRECATED_ROOT / "data" / "manifests" / "whole_universe_adjusted_prices_summary_20260319.json"
DEPRECATED_OHLCV_SALVAGE = PROJECT_ROOT / "data" / "manifests" / "stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json"

DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage1_universe_ohlcv_audit_2026-05-14.json"

APPROVED_HORIZONS = {"1d": 1, "5d": 5, "10d": 10, "20d": 20, "60d": 60}
DEFAULT_DOWNLOAD_START_DATE = "2010-01-01"
DEFAULT_DOWNLOAD_END_DATE = "2026-05-13"
RAW_VALUE_FIELDS = ("datetime", "open", "high", "low", "close", "volume")


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit Stage 1 universe and Twelve Data OHLCV evidence.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for the machine-readable audit manifest.")
    parser.add_argument("--write", action="store_true", help="Write the audit manifest to --output.")
    parser.add_argument("--json", action="store_true", help="Print the full audit JSON instead of compact text.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when hard blockers are present.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    output_path = resolve_project_path(args.output)
    summary = build_summary(output_path)

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print_summary(summary, as_json=args.json)
    if args.strict and summary["hard_blockers"]:
        return 2
    return 0


def build_summary(output_path: Path) -> dict[str, Any]:
    top50 = read_ticker_csv(TOP50_PATH)
    required_tickers = top50
    universe = audit_universe(top50)
    active_raw = audit_raw_twelvedata(ACTIVE_RAW_TWELVEDATA_DIR, required_tickers)
    deprecated_raw = audit_raw_twelvedata(DEPRECATED_RAW_TWELVEDATA_DIR, required_tickers)
    collection_code = audit_deprecated_collection_code()
    download_plan = build_download_plan(required_tickers)
    hard_blockers = build_hard_blockers(universe, deprecated_raw)

    return {
        "artifact_type": "stage1_universe_ohlcv_audit",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "blocked_hard_failures" if hard_blockers else "completed_with_limitations",
        "benchmark_claim": False,
        "dataset_builder_executed": False,
        "output_path": str(output_path),
        "scope": {
            "universe": "approved_top50",
            "required_ohlcv_tickers": required_tickers,
            "optional_support_tickers_not_counted_in_top50_scope": ["SPY"],
            "ohlcv_provider": "Twelve Data",
            "news_provider": "Alpha Vantage",
            "approved_horizons": list(APPROVED_HORIZONS),
        },
        "universe": universe,
        "active_raw_twelvedata": active_raw,
        "deprecated_raw_twelvedata": deprecated_raw,
        "deprecated_collection_code": collection_code,
        "download_plan_for_active_raw_missing_entries": download_plan,
        "supporting_manifests": audit_supporting_manifests(),
        "hard_blockers": hard_blockers,
        "blocking_actions": build_blocking_actions(universe, active_raw, deprecated_raw, download_plan),
        "questions_for_user": build_questions(universe, active_raw),
        "non_claims": [
            "not_a_materialized_benchmark_dataset",
            "not_a_clean_window_selection",
            "not_a_feature_label_split_model_metric_or_benchmark_result",
            "not_provider_level_news_article_completeness",
            "not_a_promotion_of_the_entire_deprecated_snapshot",
        ],
    }


def audit_universe(top50: list[str]) -> dict[str, Any]:
    top100 = read_ticker_csv(TOP100_PATH)
    deprecated_top50 = read_ticker_csv(DEPRECATED_TOP50_PATH)
    sp500_records = read_csv_records(SP500_SNAPSHOT_PATH)
    sp500_tickers = [normalize_ticker(row.get("ticker", "")) for row in sp500_records if row.get("ticker")]
    slickcharts_source_paths = sorted(
        str(path.relative_to(PROJECT_ROOT))
        for path in (PROJECT_ROOT / "data" / "raw" / "universe").glob("*slickcharts*")
        if path.suffix.lower() not in {".csv"}
    )
    duplicates = sorted({ticker for ticker in top50 if top50.count(ticker) > 1})
    missing_from_sp500 = [ticker for ticker in top50 if ticker not in sp500_tickers]
    top50_prefix_matches_top100 = bool(top100[:50] == top50 and len(top100) >= 50)
    source_names = sorted({str(row.get("source_name")) for row in sp500_records if row.get("source_name")})
    source_urls = sorted({str(row.get("source_url")) for row in sp500_records if row.get("source_url")})
    snapshot_dates = sorted({str(row.get("snapshot_date")) for row in sp500_records if row.get("snapshot_date")})

    return {
        "top50_path": str(TOP50_PATH),
        "top50_exists": TOP50_PATH.exists(),
        "top50_count": len(top50),
        "top50_first_ticker": top50[0] if top50 else None,
        "top50_last_ticker": top50[-1] if top50 else None,
        "top50_duplicates": duplicates,
        "top50_dotted_tickers": [ticker for ticker in top50 if "." in ticker],
        "top50_equals_deprecated_copy": top50 == deprecated_top50 and bool(top50),
        "top100_path": str(TOP100_PATH),
        "top100_count": len(top100),
        "top50_is_first_50_of_top100": top50_prefix_matches_top100,
        "sp500_snapshot_path": str(SP500_SNAPSHOT_PATH),
        "sp500_snapshot_count": len(sp500_tickers),
        "sp500_source_names": source_names,
        "sp500_source_urls": source_urls,
        "sp500_snapshot_dates": snapshot_dates,
        "top50_missing_from_sp500_snapshot": missing_from_sp500,
        "raw_slickcharts_source_evidenced": bool(slickcharts_source_paths),
        "raw_slickcharts_source_paths": slickcharts_source_paths,
        "provenance_limitation": (
            "top50_and_top100_csvs_are_present_and_consistent_but_no_raw_slickcharts_source_or_collection_script_is_evidenced"
            if not slickcharts_source_paths
            else None
        ),
    }


def audit_raw_twelvedata(directory: Path, required_tickers: list[str]) -> dict[str, Any]:
    ticker_results = []
    all_dates_by_ticker: dict[str, list[date]] = {}
    parse_failures: dict[str, list[str]] = {}

    for ticker in required_tickers:
        files = sorted((directory / ticker).glob("time_series__*.json")) if (directory / ticker).exists() else []
        parsed = [parse_twelvedata_file(path, ticker) for path in files]
        failures = [item["error"] for item in parsed if item.get("error")]
        if failures:
            parse_failures[ticker] = failures
        dates = sorted({value for item in parsed for value in item.get("dates", [])})
        if dates:
            all_dates_by_ticker[ticker] = dates
        ticker_results.append(
            {
                "ticker": ticker,
                "file_count": len(files),
                "files": [str(path.relative_to(PROJECT_ROOT)) for path in files],
                "rows": sum(int(item.get("row_count", 0)) for item in parsed),
                "date_min": dates[0].isoformat() if dates else None,
                "date_max": dates[-1].isoformat() if dates else None,
                "duplicate_dates_across_files": max(0, sum(int(item.get("row_count", 0)) for item in parsed) - len(dates)),
                "meta_symbols": sorted({str(item.get("meta_symbol")) for item in parsed if item.get("meta_symbol")}),
                "parse_failures": failures,
            }
        )

    present_tickers = sorted(all_dates_by_ticker)
    missing_tickers = [ticker for ticker in required_tickers if ticker not in all_dates_by_ticker]
    top50 = list(required_tickers)
    clean_window = build_clean_window_candidate(all_dates_by_ticker, top50)
    quality = audit_raw_quality(directory, required_tickers)
    return {
        "directory": str(directory),
        "directory_exists": directory.exists(),
        "required_ticker_count": len(required_tickers),
        "present_ticker_count": len(present_tickers),
        "top50_present_count": sum(ticker in present_tickers for ticker in top50),
        "spy_present": "SPY" in present_tickers,
        "missing_tickers": missing_tickers,
        "parse_failures": parse_failures,
        "ticker_summaries": ticker_results,
        "clean_window_candidate_from_raw": clean_window,
        "quality": quality,
    }


def parse_twelvedata_file(path: Path, expected_ticker: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive audit output
        return {"path": str(path), "error": repr(exc), "dates": []}
    if not isinstance(payload, dict):
        return {"path": str(path), "error": "payload_not_mapping", "dates": []}
    values = payload.get("values")
    if values is None and payload.get("status") == "ok":
        values = []
    if not isinstance(values, list):
        return {"path": str(path), "error": "values_not_list", "dates": []}
    dates = []
    missing_required_rows = 0
    for row in values:
        if not isinstance(row, dict) or any(row.get(field) in (None, "") for field in RAW_VALUE_FIELDS):
            missing_required_rows += 1
            continue
        try:
            dates.append(date.fromisoformat(str(row.get("datetime"))[:10]))
        except ValueError:
            missing_required_rows += 1
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    meta_symbol = normalize_ticker(str(meta.get("symbol", ""))) if meta.get("symbol") else None
    symbol_mismatch = meta_symbol not in (None, expected_ticker)
    return {
        "path": str(path),
        "row_count": len(values),
        "dates": dates,
        "date_min": dates[0].isoformat() if dates else None,
        "date_max": dates[-1].isoformat() if dates else None,
        "meta_symbol": meta_symbol,
        "status": payload.get("status"),
        "missing_required_rows": missing_required_rows,
        "symbol_mismatch": symbol_mismatch,
        "error": "meta_symbol_mismatch" if symbol_mismatch else None,
    }


def audit_raw_quality(directory: Path, required_tickers: list[str]) -> dict[str, Any]:
    totals = {
        "missing_required_rows": 0,
        "non_positive_ohlc_rows": 0,
        "negative_volume_rows": 0,
        "ohlc_order_violation_rows": 0,
        "sample_ohlc_order_violations": [],
    }
    for ticker in required_tickers:
        for path in sorted((directory / ticker).glob("time_series__*.json")) if (directory / ticker).exists() else []:
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            values = payload.get("values") if isinstance(payload, dict) else None
            if not isinstance(values, list):
                continue
            for row in values:
                if not isinstance(row, dict) or any(row.get(field) in (None, "") for field in RAW_VALUE_FIELDS):
                    totals["missing_required_rows"] += 1
                    continue
                try:
                    open_price = float(row["open"])
                    high = float(row["high"])
                    low = float(row["low"])
                    close = float(row["close"])
                    volume = int(float(row["volume"]))
                except (TypeError, ValueError):
                    totals["missing_required_rows"] += 1
                    continue
                if min(open_price, high, low, close) <= 0:
                    totals["non_positive_ohlc_rows"] += 1
                if volume < 0:
                    totals["negative_volume_rows"] += 1
                if high < max(open_price, close, low) or low > min(open_price, close, high):
                    totals["ohlc_order_violation_rows"] += 1
                    if len(totals["sample_ohlc_order_violations"]) < 20:
                        totals["sample_ohlc_order_violations"].append(
                            {
                                "ticker": ticker,
                                "path": str(path.relative_to(PROJECT_ROOT)),
                                "date": str(row.get("datetime"))[:10],
                                "open": open_price,
                                "high": high,
                                "low": low,
                                "close": close,
                                "volume": volume,
                            }
                        )
    return totals


def build_clean_window_candidate(dates_by_ticker: dict[str, list[date]], top50: list[str]) -> dict[str, Any]:
    required = top50
    missing = [ticker for ticker in required if ticker not in dates_by_ticker]
    if missing:
        return {"status": "blocked_missing_required_tickers", "missing_tickers": missing}
    min_dates = [dates_by_ticker[ticker][0] for ticker in required if dates_by_ticker[ticker]]
    max_dates = [dates_by_ticker[ticker][-1] for ticker in required if dates_by_ticker[ticker]]
    by_horizon: dict[str, Any] = {}
    for horizon_id, horizon_steps in APPROVED_HORIZONS.items():
        eligible_sets = []
        for ticker in required:
            values = dates_by_ticker[ticker]
            eligible_sets.append(set(values[:-horizon_steps]) if len(values) > horizon_steps else set())
        common = sorted(set.intersection(*eligible_sets)) if eligible_sets else []
        by_horizon[horizon_id] = {
            "horizon_trading_steps": horizon_steps,
            "full_top50_plus_spy_common_as_of_date_count": len(common),
            "candidate_as_of_start": common[0].isoformat() if common else None,
            "candidate_as_of_end": common[-1].isoformat() if common else None,
            "top50_base_rows_if_selected": len(common) * len(top50),
        }
    starts = [value["candidate_as_of_start"] for value in by_horizon.values() if value["candidate_as_of_start"]]
    ends = [value["candidate_as_of_end"] for value in by_horizon.values() if value["candidate_as_of_end"]]
    return {
        "status": "candidate_from_raw_twelvedata_not_owner_selected",
        "price_intersection_start": max(min_dates).isoformat() if min_dates else None,
        "price_intersection_end": min(max_dates).isoformat() if max_dates else None,
        "all_horizons_candidate_as_of_start": max(starts) if starts else None,
        "all_horizons_candidate_as_of_end": min(ends) if ends else None,
        "by_horizon": by_horizon,
    }


def audit_deprecated_collection_code() -> dict[str, Any]:
    files = {
        "universe_builder": DEPRECATED_ROOT / "src" / "data" / "universe_builder.py",
        "build_universe_cli": DEPRECATED_ROOT / "src" / "cli" / "build_universe.py",
        "twelve_data_client": DEPRECATED_ROOT / "src" / "data" / "twelve_data_client.py",
        "price_pipeline": DEPRECATED_ROOT / "src" / "data" / "price_pipeline.py",
        "build_market_data_cli": DEPRECATED_ROOT / "src" / "cli" / "build_market_data.py",
        "build_adjusted_prices_cli": DEPRECATED_ROOT / "src" / "cli" / "build_adjusted_prices.py",
        "data_sources_config": DEPRECATED_ROOT / "configs" / "data_sources.yaml",
        "dataset_build_config": DEPRECATED_ROOT / "configs" / "dataset_build.yaml",
    }
    return {
        "deprecated_root": str(DEPRECATED_ROOT),
        "files": {name: {"path": str(path), "exists": path.exists()} for name, path in files.items()},
        "observed_behavior": [
            "universe_builder_fetches_wikipedia_sp500_snapshot_and_writes_latest_snapshot",
            "build_market_data_uses_TwelveDataClient_time_series_endpoint_for_daily_OHLCV",
            "price_pipeline_writes_raw_payloads_under_data_raw_twelvedata_by_ticker",
            "price_pipeline_writes_interim_prices_daily_parquet_and_request_ledger",
            "build_adjusted_prices_applies_split_events_to_prices_daily_outputs",
        ],
        "deprecated_config_contradiction": "deprecated_data_sources_yaml_lists_finnhub_as_news_provider_but_active_scope_overrides_news_provider_to_alpha_vantage",
    }


def build_download_plan(required_tickers: list[str]) -> dict[str, Any]:
    missing = []
    for ticker in required_tickers:
        target = ACTIVE_RAW_TWELVEDATA_DIR / ticker / f"time_series__{DEFAULT_DOWNLOAD_START_DATE}__{DEFAULT_DOWNLOAD_END_DATE}.json"
        if not target.exists():
            missing.append(
                {
                    "ticker": ticker,
                    "start_date": DEFAULT_DOWNLOAD_START_DATE,
                    "end_date": DEFAULT_DOWNLOAD_END_DATE,
                    "target_path": str(target.relative_to(PROJECT_ROOT)),
                }
            )
    return {
        "missing_entry_count": len(missing),
        "missing_entries": missing,
        "suggested_script": "scripts/download_missing_twelvedata_ohlcv.py",
        "live_provider_calls_required": len(missing),
        "notes": [
            "Default plan targets the approved top50 universe for the active 2010-to-2026-05-13 raw OHLCV backfill window.",
            "Run plan mode before live downloads because provider calls consume Twelve Data quota.",
            "Do not overwrite existing raw payloads unless explicitly approved.",
        ],
    }


def audit_supporting_manifests() -> dict[str, Any]:
    return {
        "deprecated_market_extract_summary": read_json_if_exists(DEPRECATED_MARKET_SUMMARY),
        "deprecated_adjusted_prices_summary": read_json_if_exists(DEPRECATED_ADJUSTED_SUMMARY),
        "stage2_deprecated_ohlcv_salvage": read_json_if_exists(DEPRECATED_OHLCV_SALVAGE),
    }


def build_hard_blockers(universe: dict[str, Any], deprecated_raw: dict[str, Any]) -> list[str]:
    blockers = []
    if not universe["top50_exists"] or universe["top50_count"] != 50:
        blockers.append("top50_universe_missing_or_wrong_count")
    if universe["top50_duplicates"]:
        blockers.append("top50_universe_duplicate_tickers")
    if not universe["top50_is_first_50_of_top100"]:
        blockers.append("top50_not_first_50_of_top100")
    if universe["top50_missing_from_sp500_snapshot"]:
        blockers.append("top50_tickers_missing_from_sp500_snapshot")
    if deprecated_raw["top50_present_count"] != 50:
        blockers.append("deprecated_raw_twelvedata_missing_top50")
    if deprecated_raw["parse_failures"]:
        blockers.append("deprecated_raw_twelvedata_parse_failures")
    quality = deprecated_raw["quality"]
    if quality["missing_required_rows"] or quality["non_positive_ohlc_rows"] or quality["negative_volume_rows"]:
        blockers.append("deprecated_raw_twelvedata_blocking_quality_failure")
    return blockers


def build_blocking_actions(
    universe: dict[str, Any],
    active_raw: dict[str, Any],
    deprecated_raw: dict[str, Any],
    download_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    actions = []
    if not universe["raw_slickcharts_source_evidenced"]:
        actions.append(
            {
                "area": "universe_provenance",
                "status": "limitation_recorded_not_blocking",
                "action": "Top-50 completeness is verified; raw Slickcharts source/export remains absent and is recorded as a provenance limitation per latest user instruction.",
            }
        )
    if active_raw["present_ticker_count"] != active_raw["required_ticker_count"]:
        actions.append(
            {
                "area": "active_raw_twelvedata",
                "status": "active_raw_missing",
                "action": f"Run scripts/download_missing_twelvedata_ohlcv.py in plan mode, then execute if active raw residency is required. Planned top50 live calls: {download_plan['live_provider_calls_required']}.",
            }
        )
    if deprecated_raw["top50_present_count"] == 50 and deprecated_raw["spy_present"]:
        actions.append(
            {
                "area": "deprecated_raw_twelvedata",
                "status": "verified_with_limitations",
                "action": "Keep deprecated Twelve Data raw and parquet evidence explicitly limitation-flagged; do not promote the entire archive.",
            }
        )
    actions.append(
        {
            "area": "sec_support",
            "status": "not_required_for_stage1_ohlcv_news_audit_unless_dataset_contract_uses_sec_fields",
            "action": "Record SEC support as absent/not needed for phase-1 market-plus-news rows unless a later contract explicitly consumes static/company support.",
        }
    )
    actions.append(
        {
            "area": "credential_safety",
            "status": "existing_stage1_sensitive_artifacts_remain_unsafe_for_commit_share_publication",
            "action": "Do not share raw provider ledgers/logs until sanitized or isolated; rotate exposed keys if publication/commit is planned.",
        }
    )
    return actions


def build_questions(universe: dict[str, Any], active_raw: dict[str, Any]) -> list[dict[str, str]]:
    return []


def read_ticker_csv(path: Path) -> list[str]:
    if not path.exists():
        return []
    rows = read_csv_records(path)
    if not rows:
        return []
    return [normalize_ticker(row.get("ticker", "")) for row in rows if normalize_ticker(row.get("ticker", ""))]


def read_csv_records(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"read_error": "json_decode_error", "path": str(path)}


def normalize_ticker(value: Any) -> str:
    return str(value).strip().upper()


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    universe = summary["universe"]
    active_raw = summary["active_raw_twelvedata"]
    deprecated_raw = summary["deprecated_raw_twelvedata"]
    deprecated_window = deprecated_raw["clean_window_candidate_from_raw"]
    print("STAGE1 UNIVERSE AND OHLCV AUDIT")
    print(f"status: {summary['status']}")
    print(f"top50_count: {universe['top50_count']}")
    print(f"top50_is_first_50_of_top100: {universe['top50_is_first_50_of_top100']}")
    print(f"top50_missing_from_sp500_snapshot: {len(universe['top50_missing_from_sp500_snapshot'])}")
    print(f"raw_slickcharts_source_evidenced: {universe['raw_slickcharts_source_evidenced']}")
    print(f"active_raw_twelvedata_present: {active_raw['present_ticker_count']}/{active_raw['required_ticker_count']}")
    print(f"deprecated_raw_twelvedata_present: {deprecated_raw['present_ticker_count']}/{deprecated_raw['required_ticker_count']}")
    print(
        "deprecated_raw_all_horizons_candidate_as_of: "
        f"{deprecated_window.get('all_horizons_candidate_as_of_start')} to {deprecated_window.get('all_horizons_candidate_as_of_end')}"
    )
    print(f"download_plan_missing_entries: {summary['download_plan_for_active_raw_missing_entries']['missing_entry_count']}")
    print("hard_blockers: " + (", ".join(summary["hard_blockers"]) if summary["hard_blockers"] else "none"))
    print(f"output: {summary['output_path']}")


if __name__ == "__main__":
    raise SystemExit(main())
