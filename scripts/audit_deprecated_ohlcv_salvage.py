#!/usr/bin/env python3
"""Audit deprecated Twelve Data OHLCV parquet files for Stage 2 salvage.

This script does not promote the deprecated snapshot to active truth and does
not build a benchmark dataset. It records whether the archived OHLCV parquet
evidence can satisfy the Stage 2 market-data input gate after explicit review.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import csv
from dataclasses import dataclass
from datetime import UTC, date, datetime
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEPRECATED_ROOT = PROJECT_ROOT / "deprecated_version" / "legacy_snapshot_20260402T115014Z"
UNIVERSE_PATH = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json"

APPROVED_HORIZONS: dict[str, int] = {"1d": 1, "5d": 5, "10d": 10, "20d": 20, "60d": 60}
PRICE_BRANCHES = {
    "prices_daily": DEPRECATED_ROOT / "data" / "interim" / "prices_daily",
    "adjusted_prices_daily": DEPRECATED_ROOT / "data" / "interim" / "adjusted_prices_daily",
}
SPLIT_EVENTS_PATH = DEPRECATED_ROOT / "data" / "interim" / "split_events" / "split_events.parquet"
SPLIT_LEDGER_PATH = DEPRECATED_ROOT / "data" / "raw" / "split_events" / "split_event_request_ledger.parquet"
FINAL_DIR = DEPRECATED_ROOT / "data" / "final"

BASE_COLUMNS = ["date", "ticker", "open", "high", "low", "close", "volume", "source", "ingest_ts"]
ADJUSTED_COLUMNS = BASE_COLUMNS + ["adjustment_source", "cumulative_split_factor", "adjustment_applied_ts"]
REQUIRED_COLUMNS = ["date", "ticker", "open", "high", "low", "close", "volume"]


@dataclass(frozen=True, slots=True)
class BranchFrame:
    ticker: str
    path: Path
    frame: pd.DataFrame


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit deprecated OHLCV parquet evidence for Stage 2 readiness.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for the machine-readable salvage audit manifest.")
    parser.add_argument("--write", action="store_true", help="Write the audit manifest to --output.")
    parser.add_argument("--json", action="store_true", help="Print the full audit JSON instead of compact text.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero unless the audit status is usable_as_salvage_evidence_with_limitations.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    output_path = resolve_project_path(args.output)
    summary = build_summary(output_path)

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print_summary(summary, as_json=args.json)
    if args.strict and summary["status"] != "usable_as_salvage_evidence_with_limitations":
        return 2
    return 0


def build_summary(output_path: Path) -> dict[str, Any]:
    top50 = read_universe_tickers(UNIVERSE_PATH)
    check_tickers = top50 + ["SPY"]
    branches = {name: audit_branch(name, path, top50, check_tickers) for name, path in PRICE_BRANCHES.items()}
    adjusted_branch = branches["adjusted_prices_daily"]
    split_events = audit_split_events(check_tickers)
    final_artifacts = audit_final_artifacts()

    hard_blockers = []
    for branch_name in ["prices_daily", "adjusted_prices_daily"]:
        branch = branches[branch_name]
        quality = branch["quality_full_span"]
        if branch["top50_present_count"] != 50 or not branch["spy_present"]:
            hard_blockers.append(f"{branch_name}_missing_top50_or_spy")
        if branch["source_values"] != ["twelve_data"]:
            hard_blockers.append(f"{branch_name}_source_not_uniform_twelve_data")
        if quality["duplicate_ticker_date_rows"] or quality["null_required_rows"] or quality["non_positive_ohlc_rows"] or quality["negative_volume_rows"]:
            hard_blockers.append(f"{branch_name}_blocking_quality_failure")
        if branch["read_errors"] or branch["schema_mismatches"]:
            hard_blockers.append(f"{branch_name}_read_or_schema_failure")

    clean_candidate = adjusted_branch["clean_window_candidate"]
    if not clean_candidate["all_horizons_candidate_as_of_start"] or not clean_candidate["all_horizons_candidate_as_of_end"]:
        hard_blockers.append("adjusted_prices_no_all_horizon_clean_candidate")

    status = "blocked_deprecated_ohlcv_salvage" if hard_blockers else "usable_as_salvage_evidence_with_limitations"
    return {
        "artifact_type": "stage2_deprecated_ohlcv_salvage_audit",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": status,
        "benchmark_claim": False,
        "materialized_dataset_created": False,
        "deprecated_snapshot_promoted_to_active_truth": False,
        "output_path": str(output_path),
        "scope": {
            "universe_path": str(UNIVERSE_PATH),
            "top50_count": len(top50),
            "checked_tickers": check_tickers,
            "approved_horizons": list(APPROVED_HORIZONS),
            "provider_under_review": "twelve_data",
        },
        "deprecated_root": str(DEPRECATED_ROOT),
        "branches": branches,
        "split_events": split_events,
        "final_artifacts": final_artifacts,
        "hard_blockers": hard_blockers,
        "limitations": build_limitations(branches, split_events),
        "non_claims": [
            "not_a_materialized_benchmark_dataset",
            "not_a_model_feature_label_split_metric_or_benchmark_result",
            "not_a_promotion_of_the_entire_deprecated_snapshot",
            "not_a_commit_or_publication_safety_clearance_for_sensitive_raw_ledgers",
        ],
    }


def audit_branch(name: str, directory: Path, top50: list[str], check_tickers: list[str]) -> dict[str, Any]:
    files = sorted(directory.glob("*.parquet")) if directory.exists() else []
    stems = {path.stem for path in files}
    frames = read_branch_frames(directory, check_tickers)
    expected_columns = ADJUSTED_COLUMNS if name == "adjusted_prices_daily" else BASE_COLUMNS
    ticker_summaries = []
    all_min_dates: list[str] = []
    all_max_dates: list[str] = []
    row_counts: list[int] = []
    source_values: set[str] = set()
    adjustment_source_values: set[str] = set()
    read_errors: dict[str, str] = {}
    schema_mismatches: dict[str, list[str]] = {}
    non_one_split_factor_rows: dict[str, int] = {}
    raw_frame_by_ticker: dict[str, pd.DataFrame] = {}

    for item in frames:
        if isinstance(item, tuple):
            ticker, error = item
            read_errors[ticker] = error
            continue
        df = item.frame
        raw_frame_by_ticker[item.ticker] = df
        if list(df.columns) != expected_columns:
            schema_mismatches[item.ticker] = list(df.columns)
        if "source" in df.columns:
            source_values.update(str(value) for value in df["source"].dropna().unique())
        if "adjustment_source" in df.columns:
            adjustment_source_values.update(str(value) for value in df["adjustment_source"].dropna().unique())
        if "cumulative_split_factor" in df.columns:
            factor_count = int((df["cumulative_split_factor"].fillna(1) != 1).sum())
            if factor_count:
                non_one_split_factor_rows[item.ticker] = factor_count
        date_min = stringify_date(df["date"].min()) if "date" in df.columns and len(df) else None
        date_max = stringify_date(df["date"].max()) if "date" in df.columns and len(df) else None
        if date_min:
            all_min_dates.append(date_min)
        if date_max:
            all_max_dates.append(date_max)
        row_counts.append(len(df))
        ticker_summaries.append({"ticker": item.ticker, "rows": int(len(df)), "date_min": date_min, "date_max": date_max})

    clean_window = build_clean_window_candidate(raw_frame_by_ticker, top50)
    return {
        "directory": str(directory),
        "file_count": len(files),
        "top50_present_count": sum(ticker in stems for ticker in top50),
        "top50_missing": [ticker for ticker in top50 if ticker not in stems],
        "spy_present": "SPY" in stems,
        "checked_ticker_count": len([item for item in frames if not isinstance(item, tuple)]),
        "expected_columns": expected_columns,
        "source_values": sorted(source_values),
        "adjustment_source_values": sorted(adjustment_source_values),
        "overall_min_date": min(all_min_dates) if all_min_dates else None,
        "overall_max_date": max(all_max_dates) if all_max_dates else None,
        "intersection_start_max_of_min_dates": max(all_min_dates) if all_min_dates else None,
        "intersection_end_min_of_max_dates": min(all_max_dates) if all_max_dates else None,
        "row_count_min": min(row_counts) if row_counts else None,
        "row_count_max": max(row_counts) if row_counts else None,
        "read_errors": read_errors,
        "schema_mismatches": schema_mismatches,
        "quality_full_span": audit_quality(raw_frame_by_ticker.values()),
        "quality_within_clean_candidate": audit_quality_within_candidate(raw_frame_by_ticker.values(), clean_window),
        "tickers_with_non_one_cumulative_split_factor_rows": non_one_split_factor_rows,
        "clean_window_candidate": clean_window,
        "earliest_end_dates": sorted(ticker_summaries, key=lambda row: (row["date_max"] or "", row["ticker"]))[:15],
        "latest_start_dates": sorted(ticker_summaries, key=lambda row: (row["date_min"] or "", row["ticker"]), reverse=True)[:15],
        "shortest_histories": sorted(ticker_summaries, key=lambda row: (row["rows"], row["ticker"]))[:15],
    }


def read_branch_frames(directory: Path, check_tickers: list[str]) -> list[BranchFrame | tuple[str, str]]:
    results: list[BranchFrame | tuple[str, str]] = []
    for ticker in check_tickers:
        path = directory / f"{ticker}.parquet"
        if not path.exists():
            continue
        try:
            frame = pd.read_parquet(path)
        except Exception as exc:  # pragma: no cover - defensive audit output
            results.append((ticker, repr(exc)))
            continue
        results.append(BranchFrame(ticker=ticker, path=path, frame=frame))
    return results


def build_clean_window_candidate(frames: dict[str, pd.DataFrame], top50: list[str]) -> dict[str, Any]:
    required_tickers = top50 + ["SPY"]
    missing = [ticker for ticker in required_tickers if ticker not in frames]
    if missing:
        return {"status": "blocked_missing_required_tickers", "missing_tickers": missing}

    date_lists = {ticker: sorted(frame["date"].tolist()) for ticker, frame in frames.items() if ticker in required_tickers}
    min_dates = [stringify_date(values[0]) for values in date_lists.values() if values]
    max_dates = [stringify_date(values[-1]) for values in date_lists.values() if values]
    price_intersection_start = max(min_dates) if min_dates else None
    price_intersection_end = min(max_dates) if max_dates else None
    by_horizon: dict[str, Any] = {}

    for horizon_id, horizon_steps in APPROVED_HORIZONS.items():
        eligible_sets = []
        for values in date_lists.values():
            eligible_sets.append(set(values[:-horizon_steps]) if len(values) > horizon_steps else set())
        common = sorted(set.intersection(*eligible_sets)) if eligible_sets else []
        by_horizon[horizon_id] = {
            "horizon_trading_steps": horizon_steps,
            "full_top50_plus_spy_common_as_of_date_count": len(common),
            "candidate_as_of_start": stringify_date(common[0]) if common else None,
            "candidate_as_of_end": stringify_date(common[-1]) if common else None,
            "top50_base_rows_if_selected": len(common) * len(top50),
        }

    starts = [value["candidate_as_of_start"] for value in by_horizon.values() if value["candidate_as_of_start"]]
    ends = [value["candidate_as_of_end"] for value in by_horizon.values() if value["candidate_as_of_end"]]
    all_horizons_start = max(starts) if starts else None
    all_horizons_end = min(ends) if ends else None
    return {
        "status": "candidate_from_deprecated_ohlcv_not_owner_selected",
        "price_intersection_start": price_intersection_start,
        "price_intersection_end": price_intersection_end,
        "all_horizons_candidate_as_of_start": all_horizons_start,
        "all_horizons_candidate_as_of_end": all_horizons_end,
        "reason_start": "latest first price date across top50 plus SPY",
        "reason_end": "earliest last eligible as-of date after preserving 60 trading-step forward label availability",
        "by_horizon": by_horizon,
    }


def audit_quality(frames: Iterable[pd.DataFrame]) -> dict[str, Any]:
    totals = empty_quality_totals()
    for frame in frames:
        update_quality_totals(totals, frame)
    return totals


def audit_quality_within_candidate(frames: Iterable[pd.DataFrame], clean_window: dict[str, Any]) -> dict[str, Any]:
    start = parse_date(clean_window.get("all_horizons_candidate_as_of_start"))
    end = parse_date(clean_window.get("all_horizons_candidate_as_of_end"))
    if start is None or end is None:
        return empty_quality_totals()
    clipped = []
    for frame in frames:
        clipped.append(frame[(frame["date"] >= start) & (frame["date"] <= end)])
    return audit_quality(clipped)


def empty_quality_totals() -> dict[str, Any]:
    return {
        "duplicate_ticker_date_rows": 0,
        "null_required_rows": 0,
        "non_positive_ohlc_rows": 0,
        "negative_volume_rows": 0,
        "ohlc_order_violation_rows": 0,
        "sample_ohlc_order_violations": [],
    }


def update_quality_totals(totals: dict[str, Any], frame: pd.DataFrame) -> None:
    if not set(REQUIRED_COLUMNS).issubset(frame.columns):
        totals["null_required_rows"] += len(frame)
        return
    totals["duplicate_ticker_date_rows"] += int(frame.duplicated(["ticker", "date"]).sum())
    totals["null_required_rows"] += int(frame[REQUIRED_COLUMNS].isna().any(axis=1).sum())
    totals["non_positive_ohlc_rows"] += int((frame[["open", "high", "low", "close"]] <= 0).any(axis=1).sum())
    totals["negative_volume_rows"] += int((frame["volume"] < 0).sum())
    violation_mask = (frame["high"] < frame[["open", "close", "low"]].max(axis=1)) | (
        frame["low"] > frame[["open", "close", "high"]].min(axis=1)
    )
    violations = frame.loc[violation_mask, ["ticker", "date", "open", "high", "low", "close", "volume"]]
    totals["ohlc_order_violation_rows"] += int(len(violations))
    for row in violations.head(max(0, 20 - len(totals["sample_ohlc_order_violations"]))).to_dict("records"):
        row["date"] = stringify_date(row["date"])
        totals["sample_ohlc_order_violations"].append(row)


def audit_split_events(check_tickers: list[str]) -> dict[str, Any]:
    split_events = read_parquet_if_exists(SPLIT_EVENTS_PATH)
    split_ledger = read_parquet_if_exists(SPLIT_LEDGER_PATH)
    result: dict[str, Any] = {
        "split_events_path": str(SPLIT_EVENTS_PATH),
        "split_event_request_ledger_path": str(SPLIT_LEDGER_PATH),
        "split_events_exists": split_events is not None,
        "split_event_request_ledger_exists": split_ledger is not None,
    }
    if split_events is not None:
        tickers = sorted(str(value) for value in split_events["ticker"].dropna().unique()) if "ticker" in split_events.columns else []
        top_tickers = [ticker for ticker in tickers if ticker in check_tickers]
        result["split_events"] = {
            "rows": int(len(split_events)),
            "columns": list(split_events.columns),
            "ticker_count": len(tickers),
            "tickers_in_top50_or_spy": top_tickers,
            "ticker_count_in_top50_or_spy": len(top_tickers),
            "split_date_min": stringify_date(split_events["split_date"].min()) if "split_date" in split_events.columns and len(split_events) else None,
            "split_date_max": stringify_date(split_events["split_date"].max()) if "split_date" in split_events.columns and len(split_events) else None,
        }
    if split_ledger is not None:
        tickers = sorted(str(value) for value in split_ledger["ticker"].dropna().unique()) if "ticker" in split_ledger.columns else []
        top_tickers = [ticker for ticker in tickers if ticker in check_tickers]
        result["split_event_request_ledger"] = {
            "rows": int(len(split_ledger)),
            "columns": list(split_ledger.columns),
            "ticker_count": len(tickers),
            "tickers_in_top50_or_spy": top_tickers,
            "ticker_count_in_top50_or_spy": len(top_tickers),
            "successful_rows": int(split_ledger["success"].fillna(False).sum()) if "success" in split_ledger.columns else None,
        }
    return result


def audit_final_artifacts() -> dict[str, Any]:
    artifacts: dict[str, Any] = {}
    if not FINAL_DIR.exists():
        return artifacts
    for path in sorted(FINAL_DIR.glob("*.parquet")):
        frame = read_parquet_if_exists(path)
        if frame is None:
            artifacts[str(path)] = {"read_error": True}
            continue
        entry: dict[str, Any] = {"rows": int(len(frame)), "columns": list(frame.columns)}
        if "ticker" in frame.columns:
            entry["ticker_count"] = int(frame["ticker"].nunique())
            entry["tickers_sample"] = sorted(str(value) for value in frame["ticker"].dropna().unique())[:20]
        if "date" in frame.columns and len(frame):
            entry["date_min"] = stringify_date(frame["date"].min())
            entry["date_max"] = stringify_date(frame["date"].max())
        artifacts[str(path)] = entry
    return artifacts


def build_limitations(branches: dict[str, Any], split_events: dict[str, Any]) -> list[str]:
    limitations = [
        "Deprecated snapshot remains reference-only; this audit records evidence but does not promote the entire snapshot.",
        "Raw Twelve Data payload files under data/raw/twelvedata are not present; verified evidence is parquet-derived interim price history.",
        "Clean-window date bounds are candidates from OHLCV feasibility and are not a benchmark-ready owner selection by themselves.",
        "Alpha Vantage news coverage and event-state feasibility are handled by separate Stage 2 readiness evidence, not by this OHLCV audit.",
    ]
    adjusted = branches["adjusted_prices_daily"]
    if adjusted["quality_full_span"]["ohlc_order_violation_rows"]:
        limitations.append("One full-span CVX OHLC ordering anomaly exists before the candidate all-horizon clean window.")
    if not split_events.get("split_events_exists"):
        limitations.append("Split-event parquet evidence was not found.")
    return limitations


def read_universe_tickers(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row["ticker"] for row in csv.DictReader(handle) if row.get("ticker")]


def read_parquet_if_exists(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_parquet(path)


def stringify_date(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    adjusted = summary["branches"]["adjusted_prices_daily"]
    candidate = adjusted["clean_window_candidate"]
    print("STAGE2 DEPRECATED OHLCV SALVAGE AUDIT")
    print(f"status: {summary['status']}")
    print(f"top50_present_adjusted: {adjusted['top50_present_count']}/50")
    print(f"spy_present_adjusted: {adjusted['spy_present']}")
    print(f"adjusted_source_values: {', '.join(adjusted['source_values'])}")
    print(f"price_intersection: {candidate.get('price_intersection_start')} to {candidate.get('price_intersection_end')}")
    print(f"all_horizons_candidate_as_of: {candidate.get('all_horizons_candidate_as_of_start')} to {candidate.get('all_horizons_candidate_as_of_end')}")
    print(f"hard_blockers: {', '.join(summary['hard_blockers']) if summary['hard_blockers'] else 'none'}")
    print(f"output: {summary['output_path']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
