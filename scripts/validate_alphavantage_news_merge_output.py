#!/usr/bin/env python3
"""Validate a versioned Alpha Vantage NEWS_SENTIMENT merge output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ZONE_IDENTIFIER_MARKER = "Zone.Identifier"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate an Alpha Vantage raw merge run root.")
    parser.add_argument("--run-root", required=True, help="Merge run root containing alphavantage/ and manifests/.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    run_root = resolve_path(args.run_root)
    summary_path = run_root / "manifests" / "merge_summary.json"
    file_manifest_path = run_root / "manifests" / "file_manifest.json"
    provenance_path = run_root / "manifests" / "feed_article_provenance.jsonl"
    merged_root = run_root / "alphavantage"

    failures: list[str] = []
    if not summary_path.exists():
        failures.append(f"missing_summary:{summary_path}")
    if not file_manifest_path.exists():
        failures.append(f"missing_file_manifest:{file_manifest_path}")
    if not merged_root.exists():
        failures.append(f"missing_merged_root:{merged_root}")
    if failures:
        print_validation(failures=failures, details={"run_root": str(run_root)})
        return 2

    summary = read_json(summary_path)
    file_manifest = read_json(file_manifest_path)
    files = file_manifest.get("files", [])
    if not isinstance(files, list):
        failures.append("file_manifest_files_not_list")
        files = []

    news_files = sorted(merged_root.rglob("news_sentiment__*.json"))
    zone_output_files = [path for path in run_root.rglob("*") if path.is_file() and ZONE_IDENTIFIER_MARKER in path.name]
    merged_feed_rows = 0
    parse_failures: list[str] = []
    for path in news_files:
        try:
            payload = read_json(path)
        except json.JSONDecodeError as exc:
            parse_failures.append(f"{path}:{exc}")
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get("feed"), list):
            parse_failures.append(f"{path}:feed_not_list")
            continue
        merged_feed_rows += len(payload["feed"])

    provenance_rows = count_jsonl_rows(provenance_path) if provenance_path.exists() else None
    expected_files = summary.get("output_news_files")
    expected_rows = nested_get(summary, ["aggregate", "merged_feed_rows"])
    expected_invalid = summary.get("invalid_news_files")
    coverage_missing = nested_get(summary, ["universe_coverage_audit", "missing_annual_current_window_count"])

    if parse_failures:
        failures.append(f"parse_failures:{len(parse_failures)}")
    if zone_output_files:
        failures.append(f"zone_identifier_files_in_output:{len(zone_output_files)}")
    if len(news_files) != expected_files:
        failures.append(f"output_news_file_count_mismatch:{len(news_files)}!={expected_files}")
    if len(files) != expected_files:
        failures.append(f"file_manifest_count_mismatch:{len(files)}!={expected_files}")
    if merged_feed_rows != expected_rows:
        failures.append(f"merged_feed_rows_mismatch:{merged_feed_rows}!={expected_rows}")
    if provenance_rows is not None and provenance_rows != merged_feed_rows:
        failures.append(f"provenance_rows_mismatch:{provenance_rows}!={merged_feed_rows}")
    if expected_invalid != 0:
        failures.append(f"invalid_news_files:{expected_invalid}")
    if coverage_missing not in (0, None):
        failures.append(f"annual_current_coverage_missing:{coverage_missing}")

    details = {
        "run_root": str(run_root),
        "output_news_files": len(news_files),
        "file_manifest_records": len(files),
        "merged_feed_rows": merged_feed_rows,
        "provenance_rows": provenance_rows,
        "parse_failure_sample": parse_failures[:5],
        "zone_output_file_sample": [str(path) for path in zone_output_files[:5]],
    }
    print_validation(failures=failures, details=details)
    return 0 if not failures else 2


def resolve_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl_rows(path: Path) -> int:
    rows = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            json.loads(line)
            rows += 1
    return rows


def nested_get(payload: Any, path: list[str]) -> Any:
    value = payload
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def print_validation(*, failures: list[str], details: dict[str, Any]) -> None:
    if failures:
        print("MERGE_OUTPUT_INVALID")
        print(json.dumps({"failures": failures, "details": details}, indent=2, sort_keys=True))
        return
    print(
        "MERGE_OUTPUT_VALID "
        f"files={details['output_news_files']} "
        f"rows={details['merged_feed_rows']} "
        f"provenance_rows={details['provenance_rows']}"
    )


if __name__ == "__main__":
    sys.exit(main())
