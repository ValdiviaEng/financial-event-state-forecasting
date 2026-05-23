#!/usr/bin/env python3
"""Validate Stage 0 through Stage 1 completion evidence.

This check is a completion-evidence gate, not a pipeline test. It verifies that
documentation, comment-only scaffold, Option B contract, and raw-data audit
evidence exist and that current known limitations remain visible.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

from validate_comment_only_scaffold import APPROVED_EXECUTABLE_RELATIVE_PATHS


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage0_stage1_completion_validation_2026-05-14.json"

STAGE0_REQUIRED_DOCS = [
    "AgentRules.md",
    "ScopeDecisionLog.md",
    "ResearchTruth.md",
    "ProjectDefinition.md",
    "README.md",
    "Complete_guidebook.txt",
    "ExecutionFlow.md",
    "docs/Complete_Theoretical_Background.md",
    "docs/References.md",
    "docs/Implementation_Decisions.md",
    "docs/Architecture_Map.md",
    "docs/Execution_Plan.md",
    "docs/Detailed_Execution_Stages.md",
    "docs/Unit_Testing.md",
    "docs/db_Testing.md",
    "docs/Benchmark_Testing.md",
    "docs/Pipeline_Testing.md",
    "docs/Data_Update_Strategy.md",
    "docs/testing_commands.md",
    "docs/agent/agent_log/Current_State.md",
    "docs/agent/agent_log/Event_Ledger.ndjson",
]

STAGE_PROMPTS = [
    "docs/Prompts/Stage0Prompt.md",
    "docs/Prompts/Stage0APrompt.md",
    "docs/Prompts/Stage0BPrompt.md",
    "docs/Prompts/Stage1Prompt.md",
]

OPTION_B_DOC = PROJECT_ROOT / "docs" / "Data_Separation_And_Overfitting_Control.md"
STAGE1_RAW_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage1_raw_security_coverage_audit_2026-05-12.json"
STAGE1_UNIVERSE_OHLCV_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage1_universe_ohlcv_audit_2026-05-14.json"
TWELVEDATA_2010_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json"
REFINEMENT_SUMMARY = PROJECT_ROOT / "data" / "raw" / "alphavantage" / "daemon_summary_truncation_refinement.json"
STAGE2_INPUT_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage2_input_readiness_2026-05-13.json"
STAGE2_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage2_completion_validation_2026-05-14.json"
STAGE3_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage3_completion_validation_2026-05-15.json"
STAGE4_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage4_completion_validation_2026-05-15.json"
STAGE5_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage5_completion_validation_2026-05-21.json"
STAGE6_COMPLETION_MANIFEST = PROJECT_ROOT / "data" / "manifests" / "stage6_completion_validation_2026-05-21.json"

SCAFFOLD_REFERENCE_COUNTS = {
    "source_py": 84,
    "config_yaml": 18,
    "test_py": 31,
}

STALE_SNIPPETS = {
    "Twelve Data active raw payloads absent": ["docs/Detailed_Execution_Stages.md"],
    "active raw Twelve Data payloads remain absent": ["docs/agent/agent_log/Stage2_Dataset_Contract_Definition_2026-05-12.md"],
    "verified_deprecated_twelve_data_parquet_salvage_evidence_not_active_raw_payloads": [
        "data/manifests/stage2_dataset_contract_definition_2026-05-12.json"
    ],
    "quarterly `planned=282`, `valid=16`, `missing=266`": [
        "docs/testing_commands.md",
        "Complete_guidebook.txt",
        "docs/agent/agent_log/Stage3_Feature_Label_Pipeline_Readiness_2026-05-13.md",
    ],
    '"valid_existing_count": 16,\n      "missing_count": 266': ["data/manifests/stage3_feature_label_pipeline_readiness_2026-05-13.json"],
    "After one live quarterly download": ["Complete_guidebook.txt"],
}


@dataclass(frozen=True, slots=True)
class CheckResult:
    stage: str
    name: str
    ready: bool
    blocking: bool
    evidence: list[str]
    details: dict[str, Any]


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 0-1 completion evidence without building a dataset.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Path for machine-readable validation manifest.")
    parser.add_argument("--write", action="store_true", help="Write validation manifest to --output.")
    parser.add_argument("--json", action="store_true", help="Print full JSON instead of compact text.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when a blocking check fails.")
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
    if args.strict and summary["status"] != "passed":
        return 2
    return 0


def build_summary() -> dict[str, Any]:
    checks = [
        check_stage0_docs(),
        check_stage_prompts(),
        check_scaffold_comment_only(),
        check_option_b_contract(),
        check_stage1_alphavantage_raw(),
        check_stage1_twelvedata_raw(),
        check_refinement_limitations(),
        check_stage2_downstream_state_valid(),
        check_no_stale_stage0_stage1_snippets(),
    ]
    blocking = [item for item in checks if item.blocking]
    return {
        "artifact_type": "stage0_stage1_completion_validation",
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "status": "passed" if not blocking else "failed",
        "benchmark_claim": False,
        "materialized_stage2_dataset_present": stage2_dataset_present(),
        "downstream_artifacts_created_after_stage0_stage1": {
            "stage2_dataset": stage2_dataset_present(),
            "stage3_feature_label": stage3_feature_label_present(),
            "stage4_split_packet_gate": stage4_split_packet_present(),
            "stage5_model_prediction": stage5_model_prediction_present(),
            "stage6_metric_diagnostic_comparison_result": stage6_benchmark_result_present(),
        },
        "stage_statuses": {
            "stage0": "done_documentation_readiness_only",
            "stage0a": "done_comment_only_scaffold_only",
            "stage0b": "done_option_b_design_contract_only",
            "stage1": "done_raw_audit_with_limitations",
        },
        "blocking_checks": [item.name for item in blocking],
        "checks": [asdict(item) for item in checks],
        "non_blocking_stage1_limitations": [
            "provider_level_alphavantage_article_completeness_not_claimed",
            "alphavantage_refinement_remains_pending_or_quota_limited_not_provider_complete",
            "sensitive_alphavantage_ledgers_and_logs_not_cleared_for_commit_share_publication",
            "five_twelvedata_late_start_tickers_are_limitation_flagged",
            "cvx_ohlc_anomaly_requires_future_cleaning_or_patch_policy",
            "active_split_adjustment_method_not_selected",
            "sec_support_not_evidenced_and_not_required_until_consumed",
        ],
        "non_claims": [
            "not_stage0_stage1_created_metrics_or_benchmark_result",
            "not_stage0_stage1_created_dataset",
        ],
    }


def check_stage0_docs() -> CheckResult:
    missing = [path for path in STAGE0_REQUIRED_DOCS if not (PROJECT_ROOT / path).exists()]
    return CheckResult(
        stage="stage0",
        name="required_active_docs_exist",
        ready=not missing,
        blocking=bool(missing),
        evidence=STAGE0_REQUIRED_DOCS,
        details={"missing": missing},
    )


def check_stage_prompts() -> CheckResult:
    missing = [path for path in STAGE_PROMPTS if not (PROJECT_ROOT / path).exists()]
    return CheckResult(
        stage="stage0_to_stage1",
        name="stage_prompt_files_exist",
        ready=not missing,
        blocking=bool(missing),
        evidence=STAGE_PROMPTS,
        details={"missing": missing},
    )


def check_scaffold_comment_only() -> CheckResult:
    source_files = sorted((PROJECT_ROOT / "src" / "event_state_forecasting").rglob("*.py"))
    config_files = sorted((PROJECT_ROOT / "configs").rglob("*.yaml"))
    test_files = sorted((PROJECT_ROOT / "tests").rglob("*.py"))
    violations = []
    for path in [*source_files, *config_files, *test_files]:
        if path.relative_to(PROJECT_ROOT).as_posix() in APPROVED_EXECUTABLE_RELATIVE_PATHS:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                violations.append(f"{path.relative_to(PROJECT_ROOT)}:{line_number}")
                break
    counts = {"source_py": len(source_files), "config_yaml": len(config_files), "test_py": len(test_files)}
    ready = not violations
    return CheckResult(
        stage="stage0a",
        name="comment_only_scaffold_valid",
        ready=ready,
        blocking=not ready,
        evidence=["src/event_state_forecasting/", "configs/", "tests/"],
        details={"counts": counts, "reference_counts": SCAFFOLD_REFERENCE_COUNTS, "violations": violations},
    )


def check_option_b_contract() -> CheckResult:
    required_phrase_groups = {
        "split manifest": ["split manifest"],
        "fold-local preprocessing": ["fold-local preprocessing", "training-fold fitting", "training rows"],
        "predeclared metrics": ["predeclared metrics", "predeclared-metric", "metric predeclaration"],
        "saved out-of-sample predictions": ["saved out-of-sample predictions"],
        "overfitting diagnostics": ["overfitting diagnostics", "overfitting-diagnostic"],
        "contamination": ["contamination"],
        "lockbox": ["lockbox"],
    }
    text = OPTION_B_DOC.read_text(encoding="utf-8") if OPTION_B_DOC.exists() else ""
    lower_text = text.lower()
    missing = [label for label, variants in required_phrase_groups.items() if not any(variant.lower() in lower_text for variant in variants)]
    ready = OPTION_B_DOC.exists() and not missing
    return CheckResult(
        stage="stage0b",
        name="option_b_contract_complete",
        ready=ready,
        blocking=not ready,
        evidence=[str(OPTION_B_DOC.relative_to(PROJECT_ROOT))],
        details={"missing_required_phrases": missing},
    )


def check_stage1_alphavantage_raw() -> CheckResult:
    manifest = read_json_if_exists(STAGE1_RAW_MANIFEST)
    alpha = manifest.get("alphavantage_top50", {}) if manifest else {}
    credential = manifest.get("credential_risk", {}) if manifest else {}
    ready = bool(
        manifest
        and manifest.get("status") == "completed_as_audit_with_blocking_findings"
        and alpha.get("expected_canonical_windows") == 850
        and alpha.get("present_canonical_windows") == 850
        and alpha.get("missing_canonical_windows") == 0
        and alpha.get("parse_failures") == 0
        and alpha.get("likely_truncated_windows") == 92
        and alpha.get("empty_feed_windows") == 10
        and credential.get("files_with_sensitive_patterns") == 2
        and credential.get("secret_values_printed") is False
    )
    return CheckResult(
        stage="stage1",
        name="alphavantage_raw_audit_complete_with_visible_limitations",
        ready=ready,
        blocking=not ready,
        evidence=[str(STAGE1_RAW_MANIFEST.relative_to(PROJECT_ROOT))],
        details={
            "manifest_status": None if manifest is None else manifest.get("status"),
            "alphavantage_top50": alpha,
            "credential_risk_summary": {
                "files_with_sensitive_patterns": credential.get("files_with_sensitive_patterns"),
                "secret_values_printed": credential.get("secret_values_printed"),
            },
        },
    )


def check_stage1_twelvedata_raw() -> CheckResult:
    stage1_ohlcv = read_json_if_exists(STAGE1_UNIVERSE_OHLCV_MANIFEST)
    coverage = read_json_if_exists(TWELVEDATA_2010_MANIFEST)
    summary = coverage.get("summary_counts", {}) if coverage else {}
    raw_quality = coverage.get("raw_file_quality", {}) if coverage else {}
    ready = bool(
        stage1_ohlcv
        and coverage
        and coverage.get("status") == "complete_observed_life_with_late_start_limitations"
        and coverage.get("hard_blockers") == []
        and summary.get("full_window_file_present_top50") == 50
        and summary.get("full_window_file_present_support") == 1
        and summary.get("top50_parse_failure_count") == 0
        and summary.get("top50_with_gaps_after_first_available_date") == []
        and raw_quality.get("missing_required_rows") == 0
        and raw_quality.get("non_positive_ohlc_rows") == 0
        and raw_quality.get("negative_volume_rows") == 0
        and raw_quality.get("ohlc_order_violation_rows") == 1
    )
    return CheckResult(
        stage="stage1",
        name="twelvedata_2010_raw_coverage_complete_with_limitations",
        ready=ready,
        blocking=not ready,
        evidence=[str(STAGE1_UNIVERSE_OHLCV_MANIFEST.relative_to(PROJECT_ROOT)), str(TWELVEDATA_2010_MANIFEST.relative_to(PROJECT_ROOT))],
        details={"coverage_status": None if coverage is None else coverage.get("status"), "summary_counts": summary, "raw_file_quality": raw_quality},
    )


def check_refinement_limitations() -> CheckResult:
    summary = read_json_if_exists(REFINEMENT_SUMMARY)
    quarterly = summary.get("quarterly", {}) if summary else {}
    monthly = summary.get("monthly", {}) if summary else {}
    budget_remaining = None if summary is None else summary.get("successful_call_budget_remaining")
    max_successful_calls = None if summary is None else summary.get("max_successful_calls_per_24h")
    budget_ok = (
        isinstance(budget_remaining, int)
        and isinstance(max_successful_calls, int)
        and 0 <= budget_remaining <= max_successful_calls
    ) or isinstance(budget_remaining, str)
    pending_count = None if summary is None else summary.get("pending_request_count")
    planned_total = None if summary is None else summary.get("planned_request_count_total")
    quarterly_planned = quarterly.get("planned_request_count")
    quarterly_valid = quarterly.get("valid_existing_count")
    quarterly_missing = quarterly.get("missing_count")
    quarterly_pending = quarterly.get("pending_download_count")
    monthly_planned = monthly.get("planned_request_count")
    monthly_valid = monthly.get("valid_existing_count")
    monthly_missing = monthly.get("missing_count")
    monthly_pending = monthly.get("pending_download_count")
    count_consistent = all(
        isinstance(value, int)
        for value in [pending_count, planned_total, quarterly_planned, quarterly_valid, quarterly_missing, quarterly_pending, monthly_planned, monthly_valid, monthly_missing, monthly_pending]
    )
    if count_consistent:
        count_consistent = bool(
            0 <= pending_count <= planned_total
            and quarterly_planned == quarterly_valid + quarterly_missing
            and quarterly_pending == quarterly_missing
            and monthly_planned == monthly_valid + monthly_missing
            and monthly_pending == monthly_missing
        )
    ready = bool(
        summary
        and summary.get("source_truncated_window_count") == 92
        and summary.get("source_missing_raw_file_count") == 0
        and quarterly_planned == 282
        and count_consistent
        and budget_ok
    )
    return CheckResult(
        stage="stage1",
        name="alphavantage_refinement_budget_limited_not_blocking",
        ready=ready,
        blocking=not ready,
        evidence=[str(REFINEMENT_SUMMARY.relative_to(PROJECT_ROOT)), "scripts/run_alphavantage_news_truncation_refinement_quarterly.py", "scripts/run_alphavantage_news_truncation_refinement_standalone.py"],
        details={
            "pending_request_count": pending_count,
            "planned_request_count_total": planned_total,
            "successful_call_budget_remaining": budget_remaining,
            "max_successful_calls_per_24h": max_successful_calls,
            "quarterly": quarterly,
            "monthly": monthly,
        },
    )


def check_stage2_downstream_state_valid() -> CheckResult:
    manifest = read_json_if_exists(STAGE2_INPUT_MANIFEST)
    completion = read_json_if_exists(STAGE2_COMPLETION_MANIFEST)
    blockers = manifest.get("required_blockers") if manifest else None
    input_ready = manifest is not None and manifest.get("status") == "ready_for_dataset_builder_gate" and blockers == []
    completion_ready = completion is not None and completion.get("status") == "passed"
    legacy_ready = blockers == ["executable_dataset_tests"]
    ready = bool((input_ready and completion_ready) or legacy_ready)
    return CheckResult(
        stage="downstream_guard",
        name="stage2_downstream_state_valid",
        ready=ready,
        blocking=not ready,
        evidence=[str(STAGE2_INPUT_MANIFEST.relative_to(PROJECT_ROOT)), str(STAGE2_COMPLETION_MANIFEST.relative_to(PROJECT_ROOT)), "scripts/validate_stage2_inputs.py", "scripts/validate_stage2_completion.py"],
        details={
            "input_status": None if manifest is None else manifest.get("status"),
            "required_blockers": blockers,
            "completion_status": None if completion is None else completion.get("status"),
            "accepted_states": ["stage2_blocked_only_by_tests_before_materialization", "stage2_materialized_and_completion_validated"],
        },
    )


def stage2_dataset_present() -> bool:
    completion = read_json_if_exists(STAGE2_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def stage3_feature_label_present() -> bool:
    completion = read_json_if_exists(STAGE3_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def stage4_split_packet_present() -> bool:
    completion = read_json_if_exists(STAGE4_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def stage5_model_prediction_present() -> bool:
    completion = read_json_if_exists(STAGE5_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def stage6_benchmark_result_present() -> bool:
    completion = read_json_if_exists(STAGE6_COMPLETION_MANIFEST)
    return bool(completion and completion.get("status") == "passed")


def check_no_stale_stage0_stage1_snippets() -> CheckResult:
    findings: list[dict[str, str]] = []
    for snippet, paths in STALE_SNIPPETS.items():
        for relative_path in paths:
            path = PROJECT_ROOT / relative_path
            if path.exists() and snippet in path.read_text(encoding="utf-8"):
                findings.append({"path": relative_path, "snippet": snippet})
    return CheckResult(
        stage="stage0_to_stage1",
        name="known_stale_status_snippets_absent",
        ready=not findings,
        blocking=bool(findings),
        evidence=sorted({path for paths in STALE_SNIPPETS.values() for path in paths}),
        details={"findings": findings},
    )


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def print_summary(summary: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    if summary["status"] == "passed":
        print("STAGE0_STAGE1_COMPLETION_VALIDATION PASSED")
    else:
        print("STAGE0_STAGE1_COMPLETION_VALIDATION FAILED")
    print(f"status: {summary['status']}")
    for item in summary["checks"]:
        mark = "ready" if item["ready"] else "blocked" if item["blocking"] else "not_ready"
        print(f"{item['stage']}.{item['name']}: {mark}")
    if summary["blocking_checks"]:
        print("blocking_checks: " + ", ".join(summary["blocking_checks"]))
    print(f"output: {summary['output_path']}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
