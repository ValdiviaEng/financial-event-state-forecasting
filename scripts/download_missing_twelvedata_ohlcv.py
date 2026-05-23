#!/usr/bin/env python3
"""Plan or download missing active Twelve Data OHLCV raw payloads.

Default behavior is plan-only. Live downloads require `--execute`, a Twelve
Data API key in the environment, and non-existing target files unless
`--overwrite` is explicitly provided.
"""

from __future__ import annotations

import argparse
import csv
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UNIVERSE = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "twelvedata"
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "twelvedata_missing_ohlcv_download_plan_2026-05-14.json"
DEFAULT_START_DATE = "2010-01-01"
DEFAULT_END_DATE = "2026-05-13"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan or download missing Twelve Data OHLCV payloads.")
    parser.add_argument("--universe-file", default=str(DEFAULT_UNIVERSE), help="CSV with a ticker column.")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Active raw Twelve Data output directory.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Plan/download manifest path.")
    parser.add_argument("--start-date", default=DEFAULT_START_DATE)
    parser.add_argument("--end-date", default=DEFAULT_END_DATE)
    parser.add_argument("--include-spy", action="store_true", default=False, help="Include SPY benchmark support ticker.")
    parser.add_argument("--no-spy", dest="include_spy", action="store_false", help="Do not include SPY.")
    parser.add_argument("--execute", action="store_true", help="Perform live Twelve Data calls. Omit for plan-only mode.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing target files. Default is no overwrite.")
    parser.add_argument("--max-symbols", type=int, default=None, help="Limit number of missing entries processed.")
    parser.add_argument("--sleep-seconds", type=float, default=8.0, help="Delay between live calls.")
    parser.add_argument("--api-key-env", default="TWELVE_DATA_API_KEY")
    parser.add_argument("--env-file", default=str(PROJECT_ROOT / ".env"), help="Optional .env file used only to load --api-key-env.")
    parser.add_argument("--base-url", default="https://api.twelvedata.com/time_series")
    parser.add_argument("--write", action="store_true", help="Write the manifest in plan-only mode too.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    universe_path = resolve_project_path(args.universe_file)
    output_dir = resolve_project_path(args.output_dir)
    manifest_path = resolve_project_path(args.manifest)
    tickers = read_tickers(universe_path)
    if args.include_spy and "SPY" not in tickers:
        tickers.append("SPY")

    plan = build_plan(tickers, output_dir, args.start_date, args.end_date, overwrite=args.overwrite)
    if args.max_symbols is not None:
        plan = plan[: args.max_symbols]

    result: dict[str, Any] = {
        "artifact_type": "twelvedata_missing_ohlcv_download_plan",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "execute": args.execute,
        "universe_file": str(universe_path),
        "output_dir": str(output_dir),
        "start_date": args.start_date,
        "end_date": args.end_date,
        "planned_count": len(plan),
        "planned_entries": plan,
        "download_results": [],
        "non_claims": [
            "not_a_materialized_benchmark_dataset",
            "not_a_provider_completeness_guarantee",
            "not_a_feature_label_split_model_metric_or_benchmark_result",
        ],
    }

    if args.execute:
        api_key = load_api_key(args.api_key_env, resolve_project_path(args.env_file))
        if not api_key:
            result["status"] = "blocked_missing_api_key"
            result["api_key_env"] = args.api_key_env
            result["env_file_checked"] = str(resolve_project_path(args.env_file))
            write_manifest(manifest_path, result)
            print_summary(result, manifest_path, as_json=args.json)
            return 2
        result["download_results"] = execute_plan(plan, api_key, args.base_url, args.sleep_seconds)
        result["status"] = "executed_with_errors" if any(not item["success"] for item in result["download_results"]) else "executed"
        write_manifest(manifest_path, result)
    else:
        result["status"] = "planned_only"
        if args.write:
            write_manifest(manifest_path, result)

    print_summary(result, manifest_path, as_json=args.json)
    return 0 if result["status"] in {"planned_only", "executed"} else 2


def build_plan(tickers: list[str], output_dir: Path, start_date: str, end_date: str, *, overwrite: bool) -> list[dict[str, Any]]:
    entries = []
    for ticker in tickers:
        target = output_dir / ticker / f"time_series__{start_date}__{end_date}.json"
        if target.exists() and not overwrite:
            continue
        entries.append(
            {
                "ticker": ticker,
                "start_date": start_date,
                "end_date": end_date,
                "target_path": str(target.relative_to(PROJECT_ROOT)),
                "will_overwrite": target.exists() and overwrite,
            }
        )
    return entries


def execute_plan(plan: list[dict[str, Any]], api_key: str, base_url: str, sleep_seconds: float) -> list[dict[str, Any]]:
    results = []
    for index, entry in enumerate(plan):
        target = PROJECT_ROOT / entry["target_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
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
        url = f"{base_url}?{urlencode(params)}"
        requested_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
        try:
            with urlopen(url, timeout=30) as response:  # noqa: S310 - explicit provider URL from CLI/default.
                body = response.read().decode("utf-8")
                status_code = getattr(response, "status", None)
            payload = json.loads(body)
            if isinstance(payload, dict) and (payload.get("status") == "error" or payload.get("code") not in (None, 200)):
                raise RuntimeError(str(payload.get("message") or payload.get("code") or "provider_error"))
            target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            results.append(
                {
                    "ticker": entry["ticker"],
                    "success": True,
                    "status_code": status_code,
                    "target_path": entry["target_path"],
                    "requested_at_utc": requested_at,
                    "request_url_redacted": redact_api_key(url),
                    "row_count": len(payload.get("values", [])) if isinstance(payload, dict) and isinstance(payload.get("values"), list) else None,
                }
            )
        except Exception as exc:  # pragma: no cover - defensive operational output
            results.append(
                {
                    "ticker": entry["ticker"],
                    "success": False,
                    "target_path": entry["target_path"],
                    "requested_at_utc": requested_at,
                    "request_url_redacted": redact_api_key(url),
                    "error": repr(exc),
                }
            )
        if index < len(plan) - 1 and sleep_seconds > 0:
            time.sleep(sleep_seconds)
    return results


def read_tickers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "ticker" not in reader.fieldnames:
            raise SystemExit(f"Universe file must contain a ticker column: {path}")
        tickers = [str(row["ticker"]).strip().upper() for row in reader if str(row.get("ticker", "")).strip()]
    seen = set()
    unique = []
    for ticker in tickers:
        if ticker not in seen:
            unique.append(ticker)
            seen.add(ticker)
    return unique


def load_api_key(env_name: str, env_file: Path) -> str | None:
    direct_value = os.getenv(env_name)
    if direct_value:
        return direct_value
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() != env_name:
            continue
        return value.strip().strip('"').strip("'") or None
    return None


def redact_api_key(url: str) -> str:
    return re.sub(r"([?&]apikey=)[^&]*", r"\1REDACTED", url)


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def print_summary(result: dict[str, Any], manifest_path: Path, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    print("TWELVE DATA OHLCV MISSING DOWNLOAD PLAN")
    print(f"status: {result['status']}")
    print(f"execute: {result['execute']}")
    print(f"planned_count: {result['planned_count']}")
    if result["download_results"]:
        successes = sum(1 for item in result["download_results"] if item["success"])
        print(f"download_successes: {successes}/{len(result['download_results'])}")
    print(f"manifest: {manifest_path}")


if __name__ == "__main__":
    raise SystemExit(main())
