#!/usr/bin/env python3
"""Audit active Twelve Data OHLCV raw coverage for the approved universe.

This script validates raw JSON coverage only. It does not build a benchmark
dataset, choose an excess-return reference, or select a split-adjustment method.
Deprecated split-adjustment artifacts are inspected as reference-only evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import UTC, date, datetime
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPRECATED_ROOT = PROJECT_ROOT / "deprecated_version" / "legacy_snapshot_20260402T115014Z"

DEFAULT_UNIVERSE = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw" / "twelvedata"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json"
DEFAULT_REPORT = PROJECT_ROOT / "docs" / "agent" / "agent_log" / "TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md"

REQUIRED_FIELDS = ("datetime", "open", "high", "low", "close", "volume")
PRICE_FIELDS = ("open", "high", "low", "close")
SPLIT_EVENTS_PATH = DEPRECATED_ROOT / "data" / "interim" / "split_events" / "split_events.parquet"
SPLIT_LEDGER_PATH = DEPRECATED_ROOT / "data" / "raw" / "split_events" / "split_event_request_ledger.parquet"
ADJUSTED_PRICES_DIR = DEPRECATED_ROOT / "data" / "interim" / "adjusted_prices_daily"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit active Twelve Data OHLCV coverage.")
    parser.add_argument("--universe-file", default=str(DEFAULT_UNIVERSE), help="CSV with approved top-50 tickers.")
    parser.add_argument("--raw-dir", default=str(DEFAULT_RAW_DIR), help="Active raw Twelve Data directory.")
    parser.add_argument("--start-date", default="2010-01-01", help="Target coverage start date.")
    parser.add_argument("--end-date", default="2026-05-13", help="Target coverage end date.")
    parser.add_argument("--include-spy", action="store_true", default=True, help="Include SPY as support/reference-calendar evidence.")
    parser.add_argument("--no-spy", dest="include_spy", action="store_false", help="Do not include SPY support ticker.")
    parser.add_argument("--reference-ticker", default="SPY", help="Ticker used only as a trading-calendar reference.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Machine-readable output manifest path.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Human-readable report path.")
    parser.add_argument("--write", action="store_true", help="Write manifest and report.")
    parser.add_argument("--json", action="store_true", help="Print full JSON summary.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when post-first-date gaps or parse/quality failures exist.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    output_path = resolve_project_path(args.output)
    report_path = resolve_project_path(args.report)
    summary = build_summary(args, output_path=output_path, report_path=report_path)

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(render_report(summary), encoding="utf-8")

    print_summary(summary, as_json=args.json)
    if args.strict and summary["hard_blockers"]:
        return 2
    return 0


def build_summary(args: argparse.Namespace, *, output_path: Path, report_path: Path) -> dict[str, Any]:
    universe_path = resolve_project_path(args.universe_file)
    raw_dir = resolve_project_path(args.raw_dir)
    target_start = date.fromisoformat(args.start_date)
    target_end = date.fromisoformat(args.end_date)
    top50 = read_tickers(universe_path)
    support_tickers = [args.reference_ticker.upper()] if args.include_spy else []
    checked_tickers = top50 + [ticker for ticker in support_tickers if ticker not in top50]

    ticker_summaries = {
        ticker: audit_ticker(raw_dir, ticker, args.start_date, args.end_date) for ticker in checked_tickers
    }
    reference_window_dates, reference_calendar = build_reference_calendar(
        ticker_summaries=ticker_summaries,
        checked_tickers=checked_tickers,
        reference_ticker=args.reference_ticker.upper(),
        target_start=target_start,
        target_end=target_end,
    )

    coverage_by_ticker = {}
    for ticker in checked_tickers:
        coverage_by_ticker[ticker] = build_ticker_coverage(
            ticker=ticker,
            ticker_summary=ticker_summaries[ticker],
            reference_dates=reference_window_dates,
            target_start=target_start,
            target_end=target_end,
            is_support=ticker in support_tickers,
        )

    hard_blockers = build_hard_blockers(coverage_by_ticker, ticker_summaries, top50, support_tickers)
    raw_quality = summarize_quality(ticker_summaries)
    summary = {
        "artifact_type": "twelvedata_ohlcv_coverage_2010_audit",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "blocked_coverage_or_quality_failures" if hard_blockers else "complete_observed_life_with_late_start_limitations",
        "benchmark_claim": False,
        "dataset_builder_executed": False,
        "split_adjustment_method_selected": False,
        "deprecated_snapshot_promoted_to_active_truth": False,
        "universe_file": str(universe_path),
        "raw_dir": str(raw_dir),
        "output_path": str(output_path),
        "report_path": str(report_path),
        "scope": {
            "provider": "Twelve Data",
            "universe": "approved_top50",
            "top50_count": len(top50),
            "support_tickers_not_counted_as_universe": support_tickers,
            "checked_tickers": checked_tickers,
            "target_start_date": args.start_date,
            "target_end_date": args.end_date,
            "reference_calendar_ticker": args.reference_ticker.upper(),
        },
        "reference_calendar": reference_calendar,
        "summary_counts": summarize_counts(coverage_by_ticker, ticker_summaries, top50, support_tickers),
        "coverage_by_ticker": strip_internal_dates(coverage_by_ticker),
        "raw_file_quality": raw_quality,
        "deprecated_split_adjustment_reference": audit_deprecated_split_reference(top50, support_tickers),
        "hard_blockers": hard_blockers,
        "limitations": build_limitations(coverage_by_ticker, top50, reference_calendar, target_end, raw_quality),
        "non_claims": [
            "not_a_materialized_benchmark_dataset",
            "not_a_clean_window_selection",
            "not_a_split_adjustment_method_selection",
            "not_a_feature_label_split_model_metric_or_benchmark_result",
            "not_a_promotion_of_the_entire_deprecated_snapshot",
        ],
    }
    return summary


def audit_ticker(raw_dir: Path, ticker: str, start_text: str, end_text: str) -> dict[str, Any]:
    ticker_dir = raw_dir / ticker
    files = sorted(ticker_dir.glob("time_series__*.json")) if ticker_dir.exists() else []
    requested_full_window = ticker_dir / f"time_series__{start_text}__{end_text}.json"
    file_summaries = []
    all_dates: list[date] = []
    quality = empty_quality_totals()
    parse_failures = []
    meta_symbols: set[str] = set()
    status_values: set[str] = set()

    for path in files:
        parsed = parse_twelvedata_file(path, ticker)
        file_summaries.append(parsed["file_summary"])
        if parsed["error"]:
            parse_failures.append(parsed["error"])
        meta_symbol = parsed["file_summary"].get("meta_symbol")
        if meta_symbol:
            meta_symbols.add(str(meta_symbol))
        status_value = parsed["file_summary"].get("status")
        if status_value:
            status_values.add(str(status_value))
        all_dates.extend(parsed["dates"])
        add_quality(quality, parsed["quality"])

    unique_dates = sorted(set(all_dates))
    return {
        "ticker": ticker,
        "file_count": len(files),
        "requested_full_window_file": str(requested_full_window.relative_to(PROJECT_ROOT)),
        "requested_full_window_file_exists": requested_full_window.exists(),
        "files": file_summaries,
        "row_count_total_across_files": len(all_dates),
        "unique_date_count": len(unique_dates),
        "duplicate_dates_across_files": max(0, len(all_dates) - len(unique_dates)),
        "date_min": unique_dates[0].isoformat() if unique_dates else None,
        "date_max": unique_dates[-1].isoformat() if unique_dates else None,
        "date_values": unique_dates,
        "parse_failures": parse_failures,
        "meta_symbols": sorted(meta_symbols),
        "status_values": sorted(status_values),
        "quality": quality,
    }


def parse_twelvedata_file(path: Path, expected_ticker: str) -> dict[str, Any]:
    relative = str(path.relative_to(PROJECT_ROOT))
    dates: list[date] = []
    quality = empty_quality_totals()
    error = None
    row_count = 0
    meta_symbol = None
    status = None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("payload_not_mapping")
        meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
        meta_symbol = normalize_ticker(meta.get("symbol")) if meta.get("symbol") else None
        status = payload.get("status")
        values = payload.get("values")
        if values is None and status == "ok":
            values = []
        if not isinstance(values, list):
            raise ValueError("values_not_list")
        row_count = len(values)
        for row in values:
            update_row_quality(quality, row)
            if isinstance(row, dict) and all(row.get(field) not in (None, "") for field in REQUIRED_FIELDS):
                try:
                    dates.append(date.fromisoformat(str(row["datetime"])[:10]))
                except ValueError:
                    pass
        if meta_symbol is not None and meta_symbol != expected_ticker:
            error = f"{relative}:meta_symbol_mismatch:{meta_symbol}!={expected_ticker}"
    except Exception as exc:  # pragma: no cover - operational audit path
        error = f"{relative}:{exc!r}"

    unique_dates = sorted(set(dates))
    return {
        "dates": dates,
        "quality": quality,
        "error": error,
        "file_summary": {
            "path": relative,
            "status": status,
            "meta_symbol": meta_symbol,
            "row_count": row_count,
            "unique_date_count": len(unique_dates),
            "date_min": unique_dates[0].isoformat() if unique_dates else None,
            "date_max": unique_dates[-1].isoformat() if unique_dates else None,
            "duplicate_dates_within_file": max(0, len(dates) - len(unique_dates)),
            "error": error,
        },
    }


def build_reference_calendar(
    *,
    ticker_summaries: dict[str, Any],
    checked_tickers: list[str],
    reference_ticker: str,
    target_start: date,
    target_end: date,
) -> tuple[list[date], dict[str, Any]]:
    reference_ticker_dates = sorted(
        value for value in ticker_summaries.get(reference_ticker, {}).get("date_values", []) if target_start <= value <= target_end
    )
    first_observed = min((dates[0] for dates in (ticker_summaries[ticker]["date_values"] for ticker in checked_tickers) if dates), default=None)
    reference_end = reference_ticker_dates[-1] if reference_ticker_dates else target_end
    full_history_tickers = []
    for ticker in checked_tickers:
        dates = ticker_summaries[ticker]["date_values"]
        if dates and first_observed is not None and dates[0] <= first_observed and dates[-1] >= reference_end:
            full_history_tickers.append(ticker)

    counter: Counter[date] = Counter()
    for ticker in full_history_tickers:
        counter.update(value for value in ticker_summaries[ticker]["date_values"] if target_start <= value <= reference_end)

    threshold = max(1, int(len(full_history_tickers) * 0.8 + 0.999999))
    majority_dates = sorted(value for value, count in counter.items() if count >= threshold)
    if not majority_dates:
        majority_dates = reference_ticker_dates
        method = "single_reference_ticker_fallback"
    else:
        method = "majority_calendar_from_full_history_tickers"

    excluded_reference_dates = sorted(set(reference_ticker_dates) - set(majority_dates))
    calendar = {
        "reference_ticker": reference_ticker,
        "method": method,
        "date_count": len(majority_dates),
        "date_min": majority_dates[0].isoformat() if majority_dates else None,
        "date_max": majority_dates[-1].isoformat() if majority_dates else None,
        "full_history_calendar_ticker_count": len(full_history_tickers),
        "full_history_calendar_tickers": full_history_tickers,
        "frequency_threshold": threshold,
        "reference_ticker_extra_dates_excluded_count": len(excluded_reference_dates),
        "reference_ticker_extra_dates_excluded_sample": [value.isoformat() for value in excluded_reference_dates[:20]],
        "notes": "Calendar is used only to audit trading-date gaps; it does not select the benchmark excess-return reference series.",
    }
    return majority_dates, calendar


def build_ticker_coverage(
    *,
    ticker: str,
    ticker_summary: dict[str, Any],
    reference_dates: list[date],
    target_start: date,
    target_end: date,
    is_support: bool,
) -> dict[str, Any]:
    dates = sorted(ticker_summary.get("date_values", []))
    if not dates:
        return {
            "ticker": ticker,
            "is_support_ticker": is_support,
            "coverage_status": "missing_all_dates",
            "first_date": None,
            "last_date": None,
            "missing_reference_dates_after_first_count": None,
            "trailing_reference_gap_count": None,
        }

    date_set = set(dates)
    reference_dates = [value for value in reference_dates if target_start <= value <= target_end]
    first_reference = reference_dates[0] if reference_dates else target_start
    last_reference = reference_dates[-1] if reference_dates else target_end
    first_date = dates[0]
    last_date = dates[-1]
    comparable_start = max(first_date, first_reference)
    comparable_end = min(last_date, last_reference)
    comparable_reference_dates = [value for value in reference_dates if comparable_start <= value <= comparable_end]
    missing_after_first = [value for value in comparable_reference_dates if value not in date_set]
    trailing_gap = [value for value in reference_dates if last_date < value <= last_reference]
    pre_first_reference = [value for value in reference_dates if first_reference <= value < first_date]

    if missing_after_first or trailing_gap:
        status = "gaps_detected_after_first_available_date"
    elif first_date <= first_reference and last_date >= last_reference:
        status = "complete_from_reference_start_to_reference_end"
    else:
        status = "complete_observed_life_after_late_start"

    return {
        "ticker": ticker,
        "is_support_ticker": is_support,
        "coverage_status": status,
        "first_date": first_date.isoformat(),
        "last_date": last_date.isoformat(),
        "unique_date_count": len(dates),
        "covers_reference_start": first_date <= first_reference,
        "covers_reference_end": last_date >= last_reference,
        "reference_dates_before_first_available_count": len(pre_first_reference),
        "missing_reference_dates_after_first_count": len(missing_after_first),
        "missing_reference_dates_after_first_sample": [value.isoformat() for value in missing_after_first[:20]],
        "trailing_reference_gap_count": len(trailing_gap),
        "trailing_reference_gap_sample": [value.isoformat() for value in trailing_gap[:20]],
        "requested_full_window_file_exists": ticker_summary["requested_full_window_file_exists"],
        "requested_full_window_file": ticker_summary["requested_full_window_file"],
        "parse_failure_count": len(ticker_summary["parse_failures"]),
        "quality": ticker_summary["quality"],
    }


def audit_deprecated_split_reference(top50: list[str], support_tickers: list[str]) -> dict[str, Any]:
    checked = set(top50 + support_tickers)
    result: dict[str, Any] = {
        "reference_only": True,
        "deprecated_code_paths": {
            "split_events_pipeline": str(DEPRECATED_ROOT / "src" / "data" / "split_events_pipeline.py"),
            "split_events_client": str(DEPRECATED_ROOT / "src" / "data" / "split_events_client.py"),
            "corporate_actions": str(DEPRECATED_ROOT / "src" / "data" / "corporate_actions.py"),
            "price_pipeline": str(DEPRECATED_ROOT / "src" / "data" / "price_pipeline.py"),
        },
        "observed_deprecated_method": [
            "fetch split events from Twelve Data splits when available with yfinance fallback",
            "normalize split factors to new_shares_per_old_share",
            "compute cumulative future split factors per historical row",
            "back-adjust OHLC prices by dividing by cumulative factor and volume by multiplying by cumulative factor",
            "skip events when local raw prices already appear split-adjusted",
            "optionally exclude rows around split dates",
        ],
        "active_decision_status": "method_not_selected_for_active_root",
    }
    try:
        import pandas as pd  # type: ignore
    except Exception as exc:  # pragma: no cover - optional dependency audit path
        result["parquet_summary_error"] = f"pandas_unavailable:{exc!r}"
        return result

    if SPLIT_EVENTS_PATH.exists():
        split_events = pd.read_parquet(SPLIT_EVENTS_PATH)
        tickers = sorted(str(value) for value in split_events.get("ticker", []).dropna().unique()) if "ticker" in split_events.columns else []
        top_tickers = [ticker for ticker in tickers if ticker in checked]
        result["split_events_parquet"] = {
            "path": str(SPLIT_EVENTS_PATH),
            "rows": int(len(split_events)),
            "columns": list(split_events.columns),
            "ticker_count": len(tickers),
            "ticker_count_in_top50_or_support": len(top_tickers),
            "tickers_in_top50_or_support": top_tickers,
            "split_date_min": stringify_date(split_events["split_date"].min()) if "split_date" in split_events.columns and len(split_events) else None,
            "split_date_max": stringify_date(split_events["split_date"].max()) if "split_date" in split_events.columns and len(split_events) else None,
        }
    else:
        result["split_events_parquet"] = {"path": str(SPLIT_EVENTS_PATH), "exists": False}

    if SPLIT_LEDGER_PATH.exists():
        split_ledger = pd.read_parquet(SPLIT_LEDGER_PATH)
        tickers = sorted(str(value) for value in split_ledger.get("ticker", []).dropna().unique()) if "ticker" in split_ledger.columns else []
        result["split_event_request_ledger"] = {
            "path": str(SPLIT_LEDGER_PATH),
            "rows": int(len(split_ledger)),
            "columns": list(split_ledger.columns),
            "ticker_count": len(tickers),
            "ticker_count_in_top50_or_support": len([ticker for ticker in tickers if ticker in checked]),
            "successful_rows": int(split_ledger["success"].fillna(False).sum()) if "success" in split_ledger.columns else None,
        }
    else:
        result["split_event_request_ledger"] = {"path": str(SPLIT_LEDGER_PATH), "exists": False}

    result["adjusted_prices_reference"] = {
        "directory": str(ADJUSTED_PRICES_DIR),
        "exists": ADJUSTED_PRICES_DIR.exists(),
        "top50_or_support_files_present": sum((ADJUSTED_PRICES_DIR / f"{ticker}.parquet").exists() for ticker in checked),
    }
    return result


def summarize_counts(
    coverage_by_ticker: dict[str, Any],
    ticker_summaries: dict[str, Any],
    top50: list[str],
    support_tickers: list[str],
) -> dict[str, Any]:
    primary = {ticker: coverage_by_ticker[ticker] for ticker in top50}
    return {
        "top50_count": len(top50),
        "support_ticker_count": len(support_tickers),
        "checked_ticker_count": len(coverage_by_ticker),
        "full_window_file_present_top50": sum(primary[ticker]["requested_full_window_file_exists"] for ticker in top50),
        "full_window_file_present_support": sum(coverage_by_ticker[ticker]["requested_full_window_file_exists"] for ticker in support_tickers),
        "top50_complete_from_reference_start_to_reference_end": sorted(
            ticker for ticker, item in primary.items() if item["coverage_status"] == "complete_from_reference_start_to_reference_end"
        ),
        "top50_complete_observed_life_after_late_start": sorted(
            ticker for ticker, item in primary.items() if item["coverage_status"] == "complete_observed_life_after_late_start"
        ),
        "top50_with_gaps_after_first_available_date": sorted(
            ticker for ticker, item in primary.items() if item["coverage_status"] == "gaps_detected_after_first_available_date"
        ),
        "top50_missing_all_dates": sorted(ticker for ticker, item in primary.items() if item["coverage_status"] == "missing_all_dates"),
        "top50_parse_failure_count": sum(len(ticker_summaries[ticker]["parse_failures"]) for ticker in top50),
    }


def summarize_quality(ticker_summaries: dict[str, Any]) -> dict[str, Any]:
    totals = empty_quality_totals()
    for item in ticker_summaries.values():
        add_quality(totals, item["quality"])
    return totals


def build_hard_blockers(
    coverage_by_ticker: dict[str, Any],
    ticker_summaries: dict[str, Any],
    top50: list[str],
    support_tickers: list[str],
) -> list[str]:
    blockers = []
    for ticker in top50 + support_tickers:
        coverage = coverage_by_ticker[ticker]
        quality = coverage["quality"]
        if coverage["coverage_status"] in {"missing_all_dates", "gaps_detected_after_first_available_date"}:
            blockers.append(f"{ticker}_coverage_{coverage['coverage_status']}")
        if not coverage["requested_full_window_file_exists"]:
            blockers.append(f"{ticker}_missing_requested_full_window_file")
        if ticker_summaries[ticker]["parse_failures"]:
            blockers.append(f"{ticker}_parse_failures")
        if quality["missing_required_rows"] or quality["non_positive_ohlc_rows"] or quality["negative_volume_rows"]:
            blockers.append(f"{ticker}_blocking_quality_failure")
    return blockers


def build_limitations(
    coverage_by_ticker: dict[str, Any],
    top50: list[str],
    reference_calendar: dict[str, Any],
    target_end: date,
    raw_quality: dict[str, Any],
) -> list[str]:
    late_starters = sorted(
        ticker for ticker in top50 if coverage_by_ticker[ticker]["coverage_status"] == "complete_observed_life_after_late_start"
    )
    limitations = [
        "This audit verifies raw OHLCV coverage and quality; it does not materialize a dataset or select a benchmark clean window.",
        "SPY is used only as a reference trading calendar and support ticker; this does not select the final excess-return reference series.",
        "Split-adjustment logic from the deprecated snapshot is reference-only until explicitly reintroduced into active-root design and approved if it changes data-cleaning contracts.",
    ]
    if late_starters:
        limitations.append(
            "Some current top-50 tickers begin after 2010 in provider data, likely due IPO, spin-off, listing, or provider-history limits; they are not counted as post-first-date missing rows: "
            + ", ".join(late_starters)
        )
    reference_end = reference_calendar.get("date_max")
    if reference_end and reference_end < target_end.isoformat():
        limitations.append(
            f"The requested end date was {target_end.isoformat()}, but the latest observed majority-calendar OHLCV date is {reference_end}; rerun a refresh later if newer completed trading days are required."
        )
    if raw_quality.get("ohlc_order_violation_rows"):
        limitations.append(
            f"Raw OHLCV quality has {raw_quality['ohlc_order_violation_rows']} OHLC order anomaly; it is not a missing-entry blocker but requires a future cleaning/patch policy before dataset materialization."
        )
    return limitations


def strip_internal_dates(coverage_by_ticker: dict[str, Any]) -> dict[str, Any]:
    return coverage_by_ticker


def empty_quality_totals() -> dict[str, Any]:
    return {
        "missing_required_rows": 0,
        "non_positive_ohlc_rows": 0,
        "negative_volume_rows": 0,
        "ohlc_order_violation_rows": 0,
        "sample_ohlc_order_violations": [],
    }


def update_row_quality(totals: dict[str, Any], row: Any) -> None:
    if not isinstance(row, dict) or any(row.get(field) in (None, "") for field in REQUIRED_FIELDS):
        totals["missing_required_rows"] += 1
        return
    try:
        prices = {field: float(row[field]) for field in PRICE_FIELDS}
        volume = int(float(row["volume"]))
    except (TypeError, ValueError):
        totals["missing_required_rows"] += 1
        return
    if min(prices.values()) <= 0:
        totals["non_positive_ohlc_rows"] += 1
    if volume < 0:
        totals["negative_volume_rows"] += 1
    if prices["high"] < max(prices["open"], prices["close"], prices["low"]) or prices["low"] > min(
        prices["open"], prices["close"], prices["high"]
    ):
        totals["ohlc_order_violation_rows"] += 1
        if len(totals["sample_ohlc_order_violations"]) < 20:
            totals["sample_ohlc_order_violations"].append(
                {
                    "date": str(row.get("datetime"))[:10],
                    "open": prices["open"],
                    "high": prices["high"],
                    "low": prices["low"],
                    "close": prices["close"],
                    "volume": volume,
                }
            )


def add_quality(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key in ("missing_required_rows", "non_positive_ohlc_rows", "negative_volume_rows", "ohlc_order_violation_rows"):
        target[key] += int(source.get(key, 0))
    for sample in source.get("sample_ohlc_order_violations", []):
        if len(target["sample_ohlc_order_violations"]) < 20:
            target["sample_ohlc_order_violations"].append(sample)


def read_tickers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("ticker")]
    tickers = []
    seen = set()
    for row in rows:
        ticker = normalize_ticker(row["ticker"])
        if ticker and ticker not in seen:
            tickers.append(ticker)
            seen.add(ticker)
    return tickers


def normalize_ticker(value: Any) -> str:
    return str(value).strip().upper()


def stringify_date(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "date") and not isinstance(value, date):
        value = value.date()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)[:10]


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def render_report(summary: dict[str, Any]) -> str:
    counts = summary["summary_counts"]
    reference = summary["reference_calendar"]
    split_ref = summary["deprecated_split_adjustment_reference"]
    lines = [
        "# Twelve Data OHLCV 2010 Coverage And Split-Adjustment Review",
        "",
        f"Generated UTC: {summary['generated_at_utc']}",
        "",
        "## Authority",
        "",
        "This is Stage 1 raw-data evidence only. It preserves the approved top-50 universe and Twelve Data OHLCV provider. It does not build a benchmark dataset, select a clean window, or choose a split-adjustment method.",
        "",
        "## Coverage Summary",
        "",
        f"- Status: `{summary['status']}`",
        f"- Target window: `{summary['scope']['target_start_date']}` to `{summary['scope']['target_end_date']}`",
        f"- Top-50 full-window files present: `{counts['full_window_file_present_top50']}/50`",
        f"- Support full-window files present: `{counts['full_window_file_present_support']}/{counts['support_ticker_count']}`",
        f"- Reference calendar: `{reference['reference_ticker']}` with `{reference['date_count']}` trading dates from `{reference['date_min']}` to `{reference['date_max']}`",
        f"- Top-50 complete from reference start: `{len(counts['top50_complete_from_reference_start_to_reference_end'])}`",
        f"- Top-50 complete after late first available date: `{len(counts['top50_complete_observed_life_after_late_start'])}`",
        f"- Top-50 with post-first-date gaps: `{len(counts['top50_with_gaps_after_first_available_date'])}`",
        f"- Top-50 missing all dates: `{len(counts['top50_missing_all_dates'])}`",
        f"- Hard blockers: `{', '.join(summary['hard_blockers']) if summary['hard_blockers'] else 'none'}`",
        "",
        "## Late-Start Tickers",
        "",
    ]
    late = counts["top50_complete_observed_life_after_late_start"]
    if late:
        lines.append("These tickers start after the 2010 reference-calendar start in provider data but have no post-first-date gaps detected:")
        lines.append("")
        for ticker in late:
            item = summary["coverage_by_ticker"][ticker]
            lines.append(f"- `{ticker}`: first `{item['first_date']}`, last `{item['last_date']}`")
    else:
        lines.append("None.")
    lines.extend(
        [
            "",
            "## Split-Adjustment Reference",
            "",
            "Deprecated snapshot evidence was inspected as reference-only. It records a candidate method, but active-root method selection is still not made.",
            "",
            f"- Split events parquet rows: `{split_ref.get('split_events_parquet', {}).get('rows')}`",
            f"- Split tickers in top-50/support: `{split_ref.get('split_events_parquet', {}).get('ticker_count_in_top50_or_support')}`",
            f"- Split date range: `{split_ref.get('split_events_parquet', {}).get('split_date_min')}` to `{split_ref.get('split_events_parquet', {}).get('split_date_max')}`",
            f"- Adjusted price files present in top-50/support: `{split_ref.get('adjusted_prices_reference', {}).get('top50_or_support_files_present')}`",
            "",
            "Deprecated method observed:",
            "",
        ]
    )
    for item in split_ref["observed_deprecated_method"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
        ]
    )
    for item in summary["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    counts = summary["summary_counts"]
    print("TWELVE DATA OHLCV 2010 COVERAGE AUDIT")
    print(f"status: {summary['status']}")
    print(f"target_window: {summary['scope']['target_start_date']} to {summary['scope']['target_end_date']}")
    print(f"top50_full_window_files: {counts['full_window_file_present_top50']}/50")
    print(f"support_full_window_files: {counts['full_window_file_present_support']}/{counts['support_ticker_count']}")
    print(f"top50_complete_from_reference_start: {len(counts['top50_complete_from_reference_start_to_reference_end'])}")
    print(f"top50_late_start_no_post_first_gaps: {len(counts['top50_complete_observed_life_after_late_start'])}")
    print(f"top50_with_post_first_gaps: {len(counts['top50_with_gaps_after_first_available_date'])}")
    print("hard_blockers: " + (", ".join(summary["hard_blockers"]) if summary["hard_blockers"] else "none"))
    print(f"manifest: {summary['output_path']}")
    print(f"report: {summary['report_path']}")


if __name__ == "__main__":
    raise SystemExit(main())
