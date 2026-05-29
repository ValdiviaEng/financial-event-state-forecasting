#!/usr/bin/env python3
"""Validate enhanced Stage 2-6 versus baseline comparison artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


EXPECTED_ARTIFACT_TYPE = "enhanced_alphavantage_stage2_6_vs_baseline_comparison"


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate enhanced Stage 2-6 comparison artifacts.")
    parser.add_argument("--comparison-json", type=Path, required=True)
    parser.add_argument("--expected-baseline-result-class", default="clean_null")
    parser.add_argument("--expected-enhanced-result-class", default="clean_null")
    parser.add_argument("--expected-metric-comparison-rows", type=int, default=10)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        summary = validate_comparison(
            args.comparison_json,
            expected_baseline_result_class=args.expected_baseline_result_class,
            expected_enhanced_result_class=args.expected_enhanced_result_class,
            expected_metric_comparison_rows=args.expected_metric_comparison_rows,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ENHANCED_COMPARISON_VALIDATION FAILED: {exc}")
        return 2
    print("ENHANCED_COMPARISON_VALIDATION PASSED")
    print(f"baseline_result_class: {summary['baseline_result_class']}")
    print(f"enhanced_result_class: {summary['enhanced_result_class']}")
    print(f"baseline_stage3_aligned_news_rows: {summary['baseline_stage3_aligned_news_rows']}")
    print(f"enhanced_stage3_aligned_news_rows: {summary['enhanced_stage3_aligned_news_rows']}")
    print(f"metric_comparison_rows: {summary['metric_comparison_rows']}")
    return 0


def validate_comparison(
    comparison_json: Path,
    *,
    expected_baseline_result_class: str,
    expected_enhanced_result_class: str,
    expected_metric_comparison_rows: int,
) -> dict[str, Any]:
    if not comparison_json.is_file():
        raise FileNotFoundError(f"missing comparison JSON: {comparison_json}")
    comparison_md = comparison_json.with_suffix(".md")
    if not comparison_md.is_file():
        raise FileNotFoundError(f"missing comparison markdown: {comparison_md}")

    payload = read_json(comparison_json)
    if payload.get("artifact_type") != EXPECTED_ARTIFACT_TYPE:
        raise ValueError("unexpected comparison artifact type")
    baseline = payload.get("baseline") or {}
    enhanced = payload.get("enhanced") or {}
    if baseline.get("result_class") != expected_baseline_result_class:
        raise ValueError("baseline result class mismatch")
    if enhanced.get("result_class") != expected_enhanced_result_class:
        raise ValueError("enhanced result class mismatch")
    if baseline.get("comparability_classification") != "limitation_bearing":
        raise ValueError("baseline comparability classification mismatch")
    if enhanced.get("comparability_classification") != "limitation_bearing":
        raise ValueError("enhanced comparability classification mismatch")

    metric_rows = payload.get("event_state_metric_comparison") or []
    if len(metric_rows) != expected_metric_comparison_rows:
        raise ValueError(f"expected {expected_metric_comparison_rows} metric comparison rows, found {len(metric_rows)}")
    guardrails = payload.get("interpretation_guardrails") or []
    if "Positive benchmark language and comparability promotion remain approval-gated." not in guardrails:
        raise ValueError("missing positive-claim approval guardrail")
    if not isinstance(enhanced.get("stage3_aligned_news_rows"), int):
        raise ValueError("enhanced aligned news row count is missing")
    if not isinstance(baseline.get("stage3_aligned_news_rows"), int):
        raise ValueError("baseline aligned news row count is missing")

    return {
        "baseline_result_class": baseline.get("result_class"),
        "enhanced_result_class": enhanced.get("result_class"),
        "baseline_stage3_aligned_news_rows": baseline.get("stage3_aligned_news_rows"),
        "enhanced_stage3_aligned_news_rows": enhanced.get("stage3_aligned_news_rows"),
        "metric_comparison_rows": len(metric_rows),
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
