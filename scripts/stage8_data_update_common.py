#!/usr/bin/env python3
"""Shared Stage 8 plan-first raw data update helpers."""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, date, datetime, timedelta
import json
import os
from pathlib import Path
import re
import time
from typing import Any, Literal
from urllib.parse import urlencode
from urllib.request import Request, urlopen


Provider = Literal["alphavantage_news", "twelvedata_ohlcv"]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UNIVERSE = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
DEFAULT_ALPHAVANTAGE_ROOT = PROJECT_ROOT / "data" / "raw" / "alphavantage"
DEFAULT_TWELVEDATA_ROOT = PROJECT_ROOT / "data" / "raw" / "twelvedata"
DEFAULT_MANIFEST_DIR = PROJECT_ROOT / "data" / "manifests"
DEFAULT_OHLCV_FULL_WINDOW_START = "2010-01-01"


class Stage8UpdateError(RuntimeError):
    """Raised when a Stage 8 update request is unsafe or malformed."""


def build_news_parser(cadence: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Plan or execute Stage 8 Alpha Vantage {cadence} news updates.")
    add_common_args(parser, provider="alphavantage_news", cadence=cadence)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--sort", default="LATEST")
    parser.add_argument("--base-url", default="https://www.alphavantage.co/query")
    parser.add_argument("--api-key-env", default="ALPHAVANTAGE_API_KEY")
    parser.add_argument("--raw-root", default=str(DEFAULT_ALPHAVANTAGE_ROOT))
    return parser


def build_ohlcv_parser(cadence: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Plan or execute Stage 8 Twelve Data {cadence} OHLCV updates.")
    add_common_args(parser, provider="twelvedata_ohlcv", cadence=cadence)
    parser.add_argument("--full-window-start-date", default=DEFAULT_OHLCV_FULL_WINDOW_START)
    parser.add_argument("--include-spy", action="store_true", help="Include SPY as support ticker, not as a top-50 universe row.")
    parser.add_argument("--base-url", default="https://api.twelvedata.com/time_series")
    parser.add_argument("--api-key-env", default="TWELVE_DATA_API_KEY")
    parser.add_argument("--raw-root", default=str(DEFAULT_TWELVEDATA_ROOT))
    return parser


def add_common_args(parser: argparse.ArgumentParser, *, provider: Provider, cadence: str) -> None:
    del provider, cadence
    parser.add_argument("--universe-file", default=str(DEFAULT_UNIVERSE), help="CSV with a ticker column. Defaults to approved top-50.")
    parser.add_argument("--start-date", default=None, help="Optional update-window start date. Defaults from cadence.")
    parser.add_argument("--end-date", default=None, help="Optional update-window end date. Defaults to current UTC date.")
    parser.add_argument("--manifest", default=None, help="Manifest path. Defaults under data/manifests.")
    parser.add_argument("--ledger", default=None, help="Redacted live request ledger path. Defaults under data/manifests.")
    parser.add_argument("--execute", action="store_true", help="Perform live provider calls. Omit for plan-only mode.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing target raw files. Default is skip existing files.")
    parser.add_argument("--max-tickers", type=int, default=None, help="Limit universe tickers considered.")
    parser.add_argument("--max-calls", type=int, default=1, help="Maximum live calls in one execution. Default is 1 for safety.")
    parser.add_argument("--sleep-seconds", type=float, default=8.0, help="Delay between live provider calls.")
    parser.add_argument("--timeout-seconds", type=int, default=60)
    parser.add_argument("--env-file", default=str(PROJECT_ROOT / ".env"))
    parser.add_argument("--json", action="store_true", help="Print full JSON manifest.")


def run_news_update(cadence: str, argv: list[str] | None = None) -> int:
    args = build_news_parser(cadence).parse_args(argv)
    start_date, end_date = resolve_update_window(cadence, start_date=args.start_date, end_date=args.end_date)
    manifest_path = resolve_manifest_path(args.manifest, provider="alphavantage_news", cadence=cadence, end_date=end_date)
    ledger_path = resolve_ledger_path(args.ledger, provider="alphavantage_news", cadence=cadence, end_date=end_date)
    tickers = read_universe_tickers(resolve_project_path(args.universe_file), max_tickers=args.max_tickers)
    plan = build_news_update_plan(
        tickers=tickers,
        raw_root=resolve_project_path(args.raw_root),
        cadence=cadence,
        start_date=start_date,
        end_date=end_date,
        overwrite=args.overwrite,
        limit=args.limit,
        sort=args.sort,
        manifest_path=manifest_path,
    )
    return finalize_update(
        plan,
        args=args,
        provider="alphavantage_news",
        manifest_path=manifest_path,
        ledger_path=ledger_path,
        execute_fn=lambda active_plan, api_key: execute_news_plan(active_plan, api_key=api_key, args=args, ledger_path=ledger_path),
    )


def run_ohlcv_update(cadence: str, argv: list[str] | None = None) -> int:
    args = build_ohlcv_parser(cadence).parse_args(argv)
    _, end_date = resolve_update_window(cadence, start_date=args.start_date, end_date=args.end_date)
    manifest_path = resolve_manifest_path(args.manifest, provider="twelvedata_ohlcv", cadence=cadence, end_date=end_date)
    ledger_path = resolve_ledger_path(args.ledger, provider="twelvedata_ohlcv", cadence=cadence, end_date=end_date)
    tickers = read_universe_tickers(resolve_project_path(args.universe_file), max_tickers=args.max_tickers)
    if args.include_spy and "SPY" not in tickers:
        tickers.append("SPY")
    plan = build_ohlcv_update_plan(
        tickers=tickers,
        raw_root=resolve_project_path(args.raw_root),
        cadence=cadence,
        start_date=args.full_window_start_date,
        end_date=end_date,
        overwrite=args.overwrite,
        include_spy=bool(args.include_spy),
        manifest_path=manifest_path,
    )
    return finalize_update(
        plan,
        args=args,
        provider="twelvedata_ohlcv",
        manifest_path=manifest_path,
        ledger_path=ledger_path,
        execute_fn=lambda active_plan, api_key: execute_ohlcv_plan(active_plan, api_key=api_key, args=args, ledger_path=ledger_path),
    )


def finalize_update(
    plan: dict[str, Any],
    *,
    args: argparse.Namespace,
    provider: Provider,
    manifest_path: Path,
    ledger_path: Path,
    execute_fn: Any,
) -> int:
    plan["execute"] = bool(args.execute)
    plan["redacted_ledger_path"] = relative_path(ledger_path)
    if not args.execute:
        plan["status"] = "planned_only"
        write_json(manifest_path, plan)
        print_update_summary(plan, manifest_path=manifest_path, as_json=args.json)
        return 0

    api_key = load_api_key(args.api_key_env, resolve_project_path(args.env_file))
    if not api_key:
        plan["status"] = "blocked_missing_api_key"
        plan["api_key_env"] = args.api_key_env
        plan["env_file_checked"] = relative_path(resolve_project_path(args.env_file))
        write_json(manifest_path, plan)
        print_update_summary(plan, manifest_path=manifest_path, as_json=args.json)
        return 2

    if int(args.max_calls) <= 0:
        plan["status"] = "blocked_invalid_max_calls"
        write_json(manifest_path, plan)
        print_update_summary(plan, manifest_path=manifest_path, as_json=args.json)
        return 2

    plan["download_results"] = execute_fn(plan, api_key)
    failures = [item for item in plan["download_results"] if not item.get("success")]
    plan["status"] = "executed_with_errors" if failures else "executed"
    plan["provider_call_status"] = {
        "provider": provider,
        "attempted_calls": len(plan["download_results"]),
        "successful_calls": len(plan["download_results"]) - len(failures),
        "failed_calls": len(failures),
        "max_calls_requested": int(args.max_calls),
    }
    write_json(manifest_path, plan)
    print_update_summary(plan, manifest_path=manifest_path, as_json=args.json)
    return 0 if not failures else 2


def build_news_update_plan(
    *,
    tickers: list[str],
    raw_root: Path,
    cadence: str,
    start_date: str,
    end_date: str,
    overwrite: bool,
    limit: int,
    sort: str,
    manifest_path: Path,
) -> dict[str, Any]:
    time_from = f"{start_date.replace('-', '')}T0000"
    time_to = f"{end_date.replace('-', '')}T2359"
    planned: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for ticker in tickers:
        target = raw_root / ticker / f"news_sentiment__{start_date}__{end_date}.json"
        entry = {
            "ticker": ticker,
            "request_ticker": normalize_ticker_for_alphavantage(ticker),
            "time_from": time_from,
            "time_to": time_to,
            "target_path": relative_path(target),
            "will_overwrite": target.exists() and overwrite,
        }
        if target.exists() and not overwrite:
            skipped.append({**entry, "skip_reason": "target_exists_no_overwrite"})
        else:
            planned.append(entry)
    return build_update_manifest(
        artifact_type="stage8_alphavantage_news_update_plan",
        provider="Alpha Vantage",
        endpoint="NEWS_SENTIMENT",
        cadence=cadence,
        start_date=start_date,
        end_date=end_date,
        tickers=tickers,
        planned=planned,
        skipped=skipped,
        manifest_path=manifest_path,
        extra={"limit": int(limit), "sort": sort, "raw_root": relative_path(raw_root)},
    )


def build_ohlcv_update_plan(
    *,
    tickers: list[str],
    raw_root: Path,
    cadence: str,
    start_date: str,
    end_date: str,
    overwrite: bool,
    include_spy: bool,
    manifest_path: Path,
) -> dict[str, Any]:
    planned: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    for ticker in tickers:
        target = raw_root / ticker / f"time_series__{start_date}__{end_date}.json"
        entry = {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date,
            "target_path": relative_path(target),
            "will_overwrite": target.exists() and overwrite,
            "support_ticker": ticker == "SPY",
        }
        if target.exists() and not overwrite:
            skipped.append({**entry, "skip_reason": "target_exists_no_overwrite"})
        else:
            planned.append(entry)
    return build_update_manifest(
        artifact_type="stage8_twelvedata_ohlcv_update_plan",
        provider="Twelve Data",
        endpoint="time_series",
        cadence=cadence,
        start_date=start_date,
        end_date=end_date,
        tickers=tickers,
        planned=planned,
        skipped=skipped,
        manifest_path=manifest_path,
        extra={"include_spy_support_ticker": include_spy, "raw_root": relative_path(raw_root), "interval": "1day"},
    )


def build_update_manifest(
    *,
    artifact_type: str,
    provider: str,
    endpoint: str,
    cadence: str,
    start_date: str,
    end_date: str,
    tickers: list[str],
    planned: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    manifest_path: Path,
    extra: dict[str, Any],
) -> dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "artifact_schema_version": "stage8_data_update_v1",
        "generated_at_utc": now_utc(),
        "status": "planned_only",
        "execute": False,
        "benchmark_claim": False,
        "provider": provider,
        "endpoint": endpoint,
        "cadence": cadence,
        "universe_policy": "approved_top50_only_by_default",
        "ticker_count": len(tickers),
        "tickers": tickers,
        "start_date": start_date,
        "end_date": end_date,
        "planned_count": len(planned),
        "skipped_existing_count": len(skipped),
        "planned_entries": planned,
        "skipped_existing_entries": skipped,
        "manifest_path": relative_path(manifest_path),
        "refresh_impact_note": build_refresh_impact_note(changed_file_count=len(planned)),
        "raw_write_policy": {
            "overwrite_default": False,
            "overwrite_requested": any(bool(item.get("will_overwrite")) for item in planned),
            "existing_targets_skipped_by_default": True,
        },
        "secret_policy": {
            "stdout_contains_api_key": False,
            "manifest_contains_api_key": False,
            "live_ledger_must_use_redacted_urls": True,
        },
        "extra": extra,
        "download_results": [],
        "non_claims": [
            "not_a_materialized_benchmark_dataset",
            "not_a_provider_completeness_guarantee",
            "not_a_feature_label_split_model_metric_or_benchmark_result",
            "not_a_stage6_reinterpretation",
            "not_a_live_trading_signal",
        ],
    }


def build_refresh_impact_note(*, changed_file_count: int) -> dict[str, Any]:
    return {
        "planned_raw_file_change_count": int(changed_file_count),
        "requires_rebuild_if_executed": changed_file_count > 0,
        "required_downstream_review": [
            "rerun raw/input audits after live execution",
            "rebuild Stage 2 through Stage 6 if rows, labels, provider coverage, or feature availability change",
            "review Stage 7C post-lockbox diagnostics separately if the refreshed window is used there",
            "keep old Stage 6 clean_null result historical until a new validated packet and comparability review exist",
        ],
        "comparability_warning": "Raw updates can change rows, labels, features, splits, saved predictions, metrics, and comparability; no previous result is silently overwritten.",
    }


def execute_news_plan(plan: dict[str, Any], *, api_key: str, args: argparse.Namespace, ledger_path: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    entries = list(plan["planned_entries"])[: int(args.max_calls)]
    for index, entry in enumerate(entries):
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": entry["request_ticker"],
            "time_from": entry["time_from"],
            "time_to": entry["time_to"],
            "sort": args.sort,
            "limit": str(args.limit),
            "apikey": api_key,
        }
        url = f"{args.base_url}?{urlencode(params)}"
        target = resolve_project_path(entry["target_path"])
        result = fetch_json_to_target(url=url, target=target, timeout_seconds=int(args.timeout_seconds), provider="alphavantage")
        result.update({"ticker": entry["ticker"], "request_ticker": entry["request_ticker"], "target_path": entry["target_path"]})
        append_redacted_ledger(ledger_path, result)
        results.append(result)
        sleep_between_calls(index, len(entries), float(args.sleep_seconds))
    return results


def execute_ohlcv_plan(plan: dict[str, Any], *, api_key: str, args: argparse.Namespace, ledger_path: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    entries = list(plan["planned_entries"])[: int(args.max_calls)]
    for index, entry in enumerate(entries):
        params = {
            "symbol": entry["ticker"],
            "interval": "1day",
            "start_date": entry["start_date"],
            "end_date": entry["end_date"],
            "outputsize": "5000",
            "order": "ASC",
            "timezone": "UTC",
            "apikey": api_key,
        }
        url = f"{args.base_url}?{urlencode(params)}"
        target = resolve_project_path(entry["target_path"])
        result = fetch_json_to_target(url=url, target=target, timeout_seconds=int(args.timeout_seconds), provider="twelvedata")
        result.update({"ticker": entry["ticker"], "target_path": entry["target_path"]})
        append_redacted_ledger(ledger_path, result)
        results.append(result)
        sleep_between_calls(index, len(entries), float(args.sleep_seconds))
    return results


def fetch_json_to_target(*, url: str, target: Path, timeout_seconds: int, provider: str) -> dict[str, Any]:
    requested_at = now_utc()
    redacted_url = redact_secret_url(url)
    try:
        request = Request(url, headers={"User-Agent": "EventStateForecastingStage8Update/1.0"})
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - provider URL is explicit CLI input/default.
            body = response.read().decode("utf-8")
            status_code = getattr(response, "status", None)
        payload = json.loads(body)
        validate_provider_payload(payload, provider=provider)
        target.parent.mkdir(parents=True, exist_ok=True)
        write_raw_json(target, payload)
        return {
            "success": True,
            "requested_at_utc": requested_at,
            "request_url_redacted": redacted_url,
            "status_code": status_code,
            "row_count": provider_row_count(payload, provider=provider),
        }
    except Exception as exc:  # pragma: no cover - operational safety path.
        return {
            "success": False,
            "requested_at_utc": requested_at,
            "request_url_redacted": redacted_url,
            "error": repr(exc),
        }


def validate_provider_payload(payload: Any, *, provider: str) -> None:
    if not isinstance(payload, dict):
        raise Stage8UpdateError("provider response is not a JSON object")
    if provider == "alphavantage":
        if payload.get("Note") or payload.get("Information") or payload.get("Error Message"):
            raise Stage8UpdateError(str(payload.get("Note") or payload.get("Information") or payload.get("Error Message")))
        if not isinstance(payload.get("feed", []), list):
            raise Stage8UpdateError("Alpha Vantage feed field is not a list")
    if provider == "twelvedata":
        if payload.get("status") == "error" or payload.get("code") not in (None, 200):
            raise Stage8UpdateError(str(payload.get("message") or payload.get("code") or "provider_error"))
        if "values" in payload and not isinstance(payload.get("values"), list):
            raise Stage8UpdateError("Twelve Data values field is not a list")


def provider_row_count(payload: dict[str, Any], *, provider: str) -> int | None:
    field = "feed" if provider == "alphavantage" else "values"
    value = payload.get(field)
    return len(value) if isinstance(value, list) else None


def sleep_between_calls(index: int, total: int, seconds: float) -> None:
    if index < total - 1 and seconds > 0:
        time.sleep(seconds)


def append_redacted_ledger(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sanitized = sanitize_for_shareable_output(record)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(sanitized, sort_keys=True) + "\n")


def read_universe_tickers(path: Path, *, max_tickers: int | None = None) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "ticker" not in reader.fieldnames:
            raise Stage8UpdateError(f"universe file must contain ticker column: {path}")
        tickers = [str(row["ticker"]).strip().upper() for row in reader if str(row.get("ticker", "")).strip()]
    unique = list(dict.fromkeys(tickers))
    return unique[:max_tickers] if max_tickers is not None else unique


def resolve_update_window(cadence: str, *, start_date: str | None, end_date: str | None) -> tuple[str, str]:
    end = parse_date(end_date) if end_date else datetime.now(UTC).date()
    if start_date:
        start = parse_date(start_date)
    elif cadence == "daily":
        start = end
    elif cadence == "weekly":
        start = end - timedelta(days=6)
    else:
        raise Stage8UpdateError(f"unsupported cadence: {cadence}")
    if start > end:
        raise Stage8UpdateError("start-date must be <= end-date")
    return start.isoformat(), end.isoformat()


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise Stage8UpdateError(f"invalid ISO date: {value}") from exc


def normalize_ticker_for_alphavantage(ticker: str) -> str:
    return ticker.replace(".", "-")


def load_api_key(env_name: str, env_file: Path) -> str | None:
    value = os.getenv(env_name)
    if value:
        return value.strip() or None
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        if key.strip() == env_name:
            return raw_value.strip().strip('"').strip("'") or None
    return None


def redact_secret_url(value: str) -> str:
    return re.sub(r"([?&](?:apikey|api_key|token|key)=)[^&]*", r"\1REDACTED", value, flags=re.IGNORECASE)


def sanitize_for_shareable_output(value: Any) -> Any:
    if isinstance(value, dict):
        secret_keys = {"apikey", "api_key", "token", "key"}
        return {str(key): sanitize_for_shareable_output(item) for key, item in value.items() if str(key).lower() not in secret_keys}
    if isinstance(value, list):
        return [sanitize_for_shareable_output(item) for item in value]
    if isinstance(value, str):
        return redact_secret_url(value)
    return value


def resolve_manifest_path(value: str | None, *, provider: Provider, cadence: str, end_date: str) -> Path:
    if value:
        return resolve_project_path(value)
    return DEFAULT_MANIFEST_DIR / f"stage8_{provider}_{cadence}_update_plan_{end_date}.json"


def resolve_ledger_path(value: str | None, *, provider: Provider, cadence: str, end_date: str) -> Path:
    if value:
        return resolve_project_path(value)
    return DEFAULT_MANIFEST_DIR / f"stage8_{provider}_{cadence}_request_ledger_{end_date}.jsonl"


def resolve_project_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def relative_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sanitize_for_shareable_output(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_raw_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def print_update_summary(result: dict[str, Any], *, manifest_path: Path, as_json: bool) -> None:
    if as_json:
        print(json.dumps(sanitize_for_shareable_output(result), indent=2, sort_keys=True))
        return
    print("STAGE 8 DATA UPDATE")
    print(f"status: {result['status']}")
    print(f"provider: {result['provider']}")
    print(f"cadence: {result['cadence']}")
    print(f"execute: {result['execute']}")
    print(f"planned_count: {result['planned_count']}")
    print(f"skipped_existing_count: {result['skipped_existing_count']}")
    if result.get("download_results"):
        successes = sum(1 for item in result["download_results"] if item.get("success"))
        print(f"download_successes: {successes}/{len(result['download_results'])}")
    print(f"manifest: {manifest_path}")


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
