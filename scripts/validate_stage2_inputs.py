#!/usr/bin/env python3
"""Validate Stage 2 dataset-implementation input readiness.

This check is intentionally a gate, not a dataset builder. It verifies whether
the inputs required by docs/Prompts/Stage2Prompt.md are present and records fail-closed
blockers without changing protected scope or materializing a benchmark dataset.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, asdict
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage2_input_readiness_2026-05-13.json"

STAGE1_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage1_raw_security_coverage_audit_2026-05-12.json"
STAGE1_REPORT = PROJECT_ROOT / "docs" / "agent" / "agent_log" / "Stage1_Raw_Data_Security_And_Coverage_Audit_2026-05-12.md"
STAGE2_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage2_dataset_contract_definition_2026-05-12.json"
STAGE2_REPORT = PROJECT_ROOT / "docs" / "agent" / "agent_log" / "Stage2_Dataset_Contract_Definition_2026-05-12.md"
REFINEMENT_SUMMARY = PROJECT_ROOT / "data" / "raw" / "alphavantage" / "daemon_summary_truncation_refinement.json"
DEPRECATED_OHLCV_SALVAGE_AUDIT = PROJECT_ROOT / "data" / "manifests" / "stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json"
STAGE1_UNIVERSE_OHLCV_AUDIT = PROJECT_ROOT / "data" / "manifests" / "stage1_universe_ohlcv_audit_2026-05-14.json"
TWELVEDATA_2010_AUDIT = PROJECT_ROOT / "data" / "manifests" / "twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json"
STAGE2_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage2_completion_validation_2026-05-14.json"
STAGE3_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage3_completion_validation_2026-05-15.json"
STAGE4_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage4_completion_validation_2026-05-15.json"
UNIVERSE_PATH = PROJECT_ROOT / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
OPTION_B_DOC = PROJECT_ROOT / "docs" / "Data_Separation_And_Overfitting_Control.md"
DATA_CONTRACT_CONFIG = PROJECT_ROOT / "configs" / "data_contracts.example.yaml"
BENCHMARK_CONFIG = PROJECT_ROOT / "configs" / "phase1_top50_benchmark.yaml"
SCOPE_DECISION_LOG = PROJECT_ROOT / "ScopeDecisionLog.md"
PROJECT_DEFINITION = PROJECT_ROOT / "ProjectDefinition.md"

APPROVED_HORIZONS = ["1d", "5d", "10d", "20d", "60d"]
DATASET_TEST_GLOBS = ["tests/data/*.py", "tests/dataset/*.py"]


@dataclass(frozen=True, slots=True)
class InputCheck:
    name: str
    required: bool
    ready: bool
    blocking: bool
    evidence: list[str]
    details: dict[str, Any]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 2 input readiness without building a dataset.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for machine-readable readiness manifest.")
    parser.add_argument("--write", action="store_true", help="Write readiness manifest to --output.")
    parser.add_argument("--json", action="store_true", help="Print full readiness JSON instead of compact text.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when required inputs are blocked.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    summary = build_summary()
    output_path = resolve_project_path(args.output)
    summary["output_path"] = str(output_path)

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print_summary(summary, as_json=args.json)
    if args.strict and summary["status"] != "ready_for_dataset_builder_gate":
        return 2
    return 0


def build_summary() -> dict[str, Any]:
    stage1 = read_json_if_exists(STAGE1_MANIFEST)
    stage2 = read_json_if_exists(STAGE2_MANIFEST)
    refinement = read_json_if_exists(REFINEMENT_SUMMARY)
    stage1_ohlcv = read_json_if_exists(STAGE1_UNIVERSE_OHLCV_AUDIT)
    active_ohlcv = read_json_if_exists(TWELVEDATA_2010_AUDIT)
    ohlcv_salvage = read_json_if_exists(DEPRECATED_OHLCV_SALVAGE_AUDIT)
    inputs = [
        check_stage1(stage1),
        check_top50_universe(stage1),
        check_approved_horizons(stage1, stage2),
        check_option_b(stage2),
        check_news_coverage(stage1, refinement),
        check_ohlcv_coverage(stage1, active_ohlcv, ohlcv_salvage),
        check_clean_window(stage1_ohlcv, ohlcv_salvage),
        check_sensitive_artifacts(stage1),
        check_executable_dataset_tests(),
        check_config_scaffolds(),
    ]
    blockers = [item.name for item in inputs if item.required and item.blocking]
    status = "ready_for_dataset_builder_gate" if not blockers else "blocked_missing_required_inputs"
    executable_tests_ready = any(item.name == "executable_dataset_tests" and item.ready for item in inputs)
    non_claims = [
        "not_models_predictions_metrics_or_benchmark_result",
        "not_stage2_input_gate_created_downstream_artifacts",
    ]
    if not stage2_dataset_present():
        non_claims.append("not_a_materialized_benchmark_dataset")
    if not executable_tests_ready:
        non_claims.append("not_an_executable_dataset_test_suite")
    return {
        "artifact_type": "stage2_input_readiness_verification",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": status,
        "benchmark_claim": False,
        "materialized_dataset_present": stage2_dataset_present(),
        "dataset_builder_executed_by_this_gate": False,
        "downstream_artifacts_created_after_input_gate": {
            "stage2_dataset": stage2_dataset_present(),
            "stage3_feature_label": stage3_feature_label_present(),
            "stage4_split_packet_gate": stage4_split_packet_present(),
            "model_prediction_metric_or_benchmark_result": False,
        },
        "required_inputs_ready": not blockers,
        "required_blockers": blockers,
        "input_checks": [asdict(item) for item in inputs],
        "stage2_contract_artifacts": [str(STAGE2_REPORT), str(STAGE2_MANIFEST)],
        "non_claims": non_claims,
    }


def stage2_dataset_present() -> bool:
    completion = read_json_if_exists(STAGE2_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def stage3_feature_label_present() -> bool:
    completion = read_json_if_exists(STAGE3_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def stage4_split_packet_present() -> bool:
    completion = read_json_if_exists(STAGE4_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def check_stage1(stage1: dict[str, Any] | None) -> InputCheck:
    ready = bool(stage1 and stage1.get("status") == "completed_as_audit_with_blocking_findings" and STAGE1_REPORT.exists())
    return InputCheck(
        name="stage1_raw_audit_artifacts",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(STAGE1_REPORT), str(STAGE1_MANIFEST)],
        details={"manifest_status": None if stage1 is None else stage1.get("status")},
    )


def check_top50_universe(stage1: dict[str, Any] | None) -> InputCheck:
    tickers = read_universe_tickers(UNIVERSE_PATH)
    stage1_count = nested_get(stage1, ["universe", "ticker_count"])
    ready = UNIVERSE_PATH.exists() and len(tickers) == 50 and stage1_count == 50
    return InputCheck(
        name="top50_universe",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(UNIVERSE_PATH)],
        details={"ticker_count": len(tickers), "stage1_ticker_count": stage1_count, "dotted_tickers": [item for item in tickers if "." in item]},
    )


def check_approved_horizons(stage1: dict[str, Any] | None, stage2: dict[str, Any] | None) -> InputCheck:
    stage1_horizons = nested_get(stage1, ["scope", "horizons"])
    stage2_horizons = nested_get(stage2, ["scope", "horizons"])
    ready = stage1_horizons == APPROVED_HORIZONS and stage2_horizons == APPROVED_HORIZONS
    return InputCheck(
        name="approved_horizons",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(STAGE1_MANIFEST), str(STAGE2_MANIFEST)],
        details={"approved_horizons": APPROVED_HORIZONS, "stage1_horizons": stage1_horizons, "stage2_horizons": stage2_horizons},
    )


def check_option_b(stage2: dict[str, Any] | None) -> InputCheck:
    ready = OPTION_B_DOC.exists() and nested_get(stage2, ["scope", "option_b_contract"]) is True
    return InputCheck(
        name="option_b_contract",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(OPTION_B_DOC), str(STAGE2_MANIFEST)],
        details={"stage2_option_b_contract": nested_get(stage2, ["scope", "option_b_contract"])},
    )


def check_news_coverage(stage1: dict[str, Any] | None, refinement: dict[str, Any] | None) -> InputCheck:
    canonical_complete = nested_get(stage1, ["alphavantage_top50", "present_canonical_windows"]) == nested_get(
        stage1, ["alphavantage_top50", "expected_canonical_windows"]
    )
    parse_ok = nested_get(stage1, ["alphavantage_top50", "parse_failures"]) == 0
    pending = nested_get(refinement, ["pending_request_count"])
    truncated_quarterly = nested_get(refinement, ["quarterly", "truncated_existing_count"])
    truncated_monthly = nested_get(refinement, ["monthly", "truncated_existing_count"])
    article_complete = pending == 0 and truncated_quarterly == 0 and truncated_monthly == 0
    ready = bool(canonical_complete and parse_ok)
    return InputCheck(
        name="alphavantage_news_coverage_and_truncation_policy",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(STAGE1_MANIFEST), str(REFINEMENT_SUMMARY)],
        details={
            "canonical_file_coverage_complete": canonical_complete,
            "parse_failures": nested_get(stage1, ["alphavantage_top50", "parse_failures"]),
            "stage1_likely_truncated_windows": nested_get(stage1, ["alphavantage_top50", "likely_truncated_windows"]),
            "refinement_pending_request_count": pending,
            "refinement_quarterly_truncated_existing_count": truncated_quarterly,
            "refinement_monthly_truncated_existing_count": truncated_monthly,
            "provider_level_article_completeness_claim": article_complete,
            "policy_status": "current_canonical_news_corpus_used_with_visible_truncation_limitations_per_latest_user_instruction",
        },
    )


def check_ohlcv_coverage(stage1: dict[str, Any] | None, active_ohlcv: dict[str, Any] | None, ohlcv_salvage: dict[str, Any] | None) -> InputCheck:
    paths = sorted(str(path.relative_to(PROJECT_ROOT)) for path in find_twelve_data_paths())
    stage1_paths = nested_get(stage1, ["provider_evidence", "twelve_data_ohlcv_paths"]) or []
    active_summary = nested_get(active_ohlcv, ["summary_counts"]) or {}
    active_ready = (
        nested_get(active_ohlcv, ["status"]) == "complete_observed_life_with_late_start_limitations"
        and nested_get(active_ohlcv, ["hard_blockers"]) == []
        and active_summary.get("full_window_file_present_top50") == 50
        and active_summary.get("full_window_file_present_support") == 1
        and active_summary.get("top50_with_gaps_after_first_available_date") == []
    )
    salvage_status = nested_get(ohlcv_salvage, ["status"])
    adjusted_branch = nested_get(ohlcv_salvage, ["branches", "adjusted_prices_daily"]) or {}
    salvage_ready = (
        salvage_status == "usable_as_salvage_evidence_with_limitations"
        and adjusted_branch.get("top50_present_count") == 50
        and adjusted_branch.get("spy_present") is True
        and adjusted_branch.get("source_values") == ["twelve_data"]
    )
    ready = bool(active_ready or paths or stage1_paths or salvage_ready)
    evidence = paths[:]
    if active_ohlcv is not None:
        evidence.append(str(TWELVEDATA_2010_AUDIT))
    if salvage_ready or ohlcv_salvage is not None:
        evidence.append(str(DEPRECATED_OHLCV_SALVAGE_AUDIT))
    if active_ready:
        status = "verified_active_raw_twelvedata_2010_top50_plus_spy_with_limitations"
    elif paths or stage1_paths:
        status = "active_raw_twelvedata_paths_present_without_2010_audit_ready_status"
    elif salvage_ready:
        status = "verified_deprecated_twelve_data_parquet_salvage_evidence"
    else:
        status = "not_evidenced_in_repository_materials"
    return InputCheck(
        name="twelve_data_ohlcv_coverage",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=evidence,
        details={
            "stage1_paths": stage1_paths,
            "active_raw_paths": paths,
            "active_2010_audit_status": nested_get(active_ohlcv, ["status"]),
            "active_2010_summary_counts": active_summary,
            "deprecated_salvage_status": salvage_status,
            "deprecated_salvage_adjusted_top50_present_count": adjusted_branch.get("top50_present_count"),
            "deprecated_salvage_spy_present": adjusted_branch.get("spy_present"),
            "deprecated_salvage_source_values": adjusted_branch.get("source_values"),
            "status": status,
        },
    )


def check_clean_window(stage1_ohlcv: dict[str, Any] | None, ohlcv_salvage: dict[str, Any] | None) -> InputCheck:
    candidates = sorted(path for path in (PROJECT_ROOT / "data" / "manifests").glob("*clean*window*"))
    decision_text = SCOPE_DECISION_LOG.read_text(encoding="utf-8") if SCOPE_DECISION_LOG.exists() else ""
    doctrine_documented = "shorter overlapping clean historical window" in decision_text
    active_candidate = nested_get(stage1_ohlcv, ["active_raw_twelvedata", "clean_window_candidate_from_raw"]) or {}
    clean_candidate = nested_get(ohlcv_salvage, ["branches", "adjusted_prices_daily", "clean_window_candidate"]) or {}
    candidate_start = active_candidate.get("all_horizons_candidate_as_of_start") or clean_candidate.get("all_horizons_candidate_as_of_start")
    candidate_end = active_candidate.get("all_horizons_candidate_as_of_end") or clean_candidate.get("all_horizons_candidate_as_of_end")
    ready = bool(doctrine_documented and candidate_start and candidate_end)
    evidence = [str(path) for path in candidates]
    evidence.extend([str(SCOPE_DECISION_LOG), str(PROJECT_DEFINITION), str(STAGE1_UNIVERSE_OHLCV_AUDIT), str(DEPRECATED_OHLCV_SALVAGE_AUDIT)])
    candidate_status = "doctrine_documented_with_active_raw_twelvedata_candidate_bounds" if active_candidate else "doctrine_documented_with_deprecated_ohlcv_candidate_bounds" if ready else "not_selected"
    return InputCheck(
        name="clean_historical_window_decision",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=evidence,
        details={
            "doctrine_documented": doctrine_documented,
            "active_raw_price_intersection_start": active_candidate.get("price_intersection_start"),
            "active_raw_price_intersection_end": active_candidate.get("price_intersection_end"),
            "active_raw_all_horizons_candidate_as_of_start": active_candidate.get("all_horizons_candidate_as_of_start"),
            "active_raw_all_horizons_candidate_as_of_end": active_candidate.get("all_horizons_candidate_as_of_end"),
            "price_intersection_start": clean_candidate.get("price_intersection_start"),
            "price_intersection_end": clean_candidate.get("price_intersection_end"),
            "all_horizons_candidate_as_of_start": candidate_start,
            "all_horizons_candidate_as_of_end": candidate_end,
            "deprecated_candidate_status": clean_candidate.get("status"),
            "status": candidate_status,
        },
    )


def check_sensitive_artifacts(stage1: dict[str, Any] | None) -> InputCheck:
    findings = nested_get(stage1, ["credential_risk", "findings"]) or []
    sensitive_count = len(findings)
    ready = stage1 is not None
    return InputCheck(
        name="sensitive_raw_ledger_log_handling",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[item.get("path", "") for item in findings if isinstance(item, dict)],
        details={
            "sensitive_file_count": sensitive_count,
            "dataset_artifact_policy": "exclude_sensitive_raw_ledgers_and_logs_from_dataset_artifacts",
            "commit_share_publication_clearance": False if findings else True,
            "status": "identified_local_only_excluded_from_dataset_artifacts" if findings else "clear",
        },
    )


def check_executable_dataset_tests() -> InputCheck:
    files = [path for pattern in DATASET_TEST_GLOBS for path in (PROJECT_ROOT).glob(pattern)]
    executable = [path for path in files if has_executable_python(path)]
    ready = bool(executable)
    return InputCheck(
        name="executable_dataset_tests",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(path) for path in files],
        details={"test_file_count": len(files), "executable_test_file_count": len(executable), "status": "comment_only" if files and not executable else "executable" if executable else "missing"},
    )


def check_config_scaffolds() -> InputCheck:
    ready = DATA_CONTRACT_CONFIG.exists() and BENCHMARK_CONFIG.exists()
    return InputCheck(
        name="stage2_config_scaffolds",
        required=True,
        ready=ready,
        blocking=not ready,
        evidence=[str(DATA_CONTRACT_CONFIG), str(BENCHMARK_CONFIG)],
        details={"active_config_status": "comment_only_not_active_config" if ready else "missing"},
    )


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_universe_tickers(path: Path) -> list[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row["ticker"] for row in csv.DictReader(handle) if row.get("ticker")]


def find_twelve_data_paths() -> list[Path]:
    candidates: set[Path] = set()
    raw_root = PROJECT_ROOT / "data" / "raw"
    if not raw_root.exists():
        return []
    candidates.update(path for path in raw_root.rglob("*twelve*") if path.exists())
    twelve_dir = raw_root / "twelvedata"
    if twelve_dir.exists():
        candidates.add(twelve_dir)
        candidates.update(path for path in twelve_dir.rglob("*") if path.is_file())
    return sorted(candidates)


def has_executable_python(path: Path) -> bool:
    if not path.exists():
        return False
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        return True
    return False


def nested_get(value: dict[str, Any] | None, keys: list[str]) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print("STAGE2 INPUT READINESS")
    print(f"status: {summary['status']}")
    print(f"required_inputs_ready: {summary['required_inputs_ready']}")
    for item in summary["input_checks"]:
        mark = "ready" if item["ready"] else "blocked" if item["blocking"] else "not_ready"
        print(f"{item['name']}: {mark}")
    blockers = summary["required_blockers"]
    if blockers:
        print("blocking_inputs: " + ", ".join(blockers))
    print(f"output: {summary['output_path']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
