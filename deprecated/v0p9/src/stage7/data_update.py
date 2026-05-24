"""Stage 7 data-update planning and deprecated-settings preservation."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Mapping


DEFAULT_DEPRECATED_FILES = [
    "configs/features.yaml",
    "configs/labels.yaml",
    "configs/splits.yaml",
    "configs/models.yaml",
    "configs/evaluation.yaml",
    "configs/artifact_packet.yaml",
    "docs/Prompts/Stage7CPrompt.md",
    "ScopeDecisionLog.md",
    "ResearchTruth.md",
]


def build_stage7_data_update_plan(
    project_root: Path,
    config: Mapping[str, Any],
    *,
    target_end_date: str | None = None,
    new_holdout_materialized: bool = False,
) -> dict[str, Any]:
    data_policy = config["data_update_policy"]
    target = target_end_date or date.today().isoformat()
    archive_root = project_root / str(data_policy["preserve_old_settings_archive"])
    twelvedata_status = inspect_twelvedata_target_files(project_root, target)
    if new_holdout_materialized:
        status = "raw_ohlcv_updated_new_post_lockbox_holdout_materialized_diagnostics_only"
    else:
        status = "raw_ohlcv_updated_new_holdout_not_materialized" if twelvedata_status["all_target_files_exist"] else "planned_not_materialized"
    return {
        "artifact_type": "stage7_data_update_plan",
        "artifact_schema_version": "stage7_contextual_bandit_v1",
        "generated_at_utc": now_utc(),
        "status": status,
        "approved_to_call_providers_when_explicitly_executed": bool(data_policy.get("approved_to_call_providers_when_explicitly_executed")),
        "target_new_holdout_policy": data_policy["target_new_holdout_policy"],
        "target_raw_end_date": target,
        "new_post_lockbox_holdout_materialized": bool(new_holdout_materialized),
        "twelvedata_target_file_status": twelvedata_status,
        "old_stage6_lockbox_start": data_policy["old_stage6_lockbox_start"],
        "old_stage6_lockbox_end": data_policy["old_stage6_lockbox_end"],
        "deprecated_settings_archive": str(archive_root),
        "required_actions_before_claim_bearing_holdout": [
            "download_or_validate_post_lockbox_twelvedata_ohlcv_for_top50_plus_spy",
            "download_or_validate_post_lockbox_alphavantage_news_for_top50",
            "materialize_new_stage2_dataset_version",
            "materialize_new_stage3_feature_label_version",
            "materialize_new_stage4_stage7_split_with_new_post_lockbox_holdout",
            "materialize_stage5_fold_safe_predictions_for_new_artifact_family",
            "run_stage7_benchmark_on_new_holdout_without_result_driven_tuning",
        ],
        "remaining_materialization_blockers": [
            "Stage 2 builder still needs a Stage 7 clean-window manifest and raw filename parameterization before new data can become labels.",
            "Alpha Vantage post-lockbox/news completeness remains limitation-bearing until separately refreshed or explicitly accepted with flags.",
            "No new Stage 7 split/holdout artifact exists yet, so final post-lockbox accuracy claims remain blocked.",
        ],
        "non_claims": [
            "not_a_data_update_execution_record",
            "not_a_new_holdout_materialization",
            "not_a_provider_completeness_claim",
            "not_a_benchmark_result",
        ],
    }


def inspect_twelvedata_target_files(project_root: Path, target_end_date: str) -> dict[str, Any]:
    universe = project_root / "data" / "raw" / "universe" / "top50_slickcharts_2026-04-10.csv"
    tickers = read_universe_tickers(universe)
    checked = [*tickers, "SPY"] if "SPY" not in tickers else tickers
    missing: list[str] = []
    existing: list[str] = []
    for ticker in checked:
        path = project_root / "data" / "raw" / "twelvedata" / ticker / f"time_series__2010-01-01__{target_end_date}.json"
        if path.exists():
            existing.append(ticker)
        else:
            missing.append(ticker)
    return {
        "target_end_date": target_end_date,
        "checked_ticker_count": len(checked),
        "existing_target_file_count": len(existing),
        "missing_target_file_count": len(missing),
        "missing_tickers": missing,
        "all_target_files_exist": not missing,
    }


def read_universe_tickers(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    headers = [value.strip().lower() for value in lines[0].split(",")]
    if "ticker" not in headers:
        return []
    ticker_index = headers.index("ticker")
    tickers: list[str] = []
    for line in lines[1:]:
        values = line.split(",")
        if len(values) <= ticker_index:
            continue
        ticker = values[ticker_index].strip().upper()
        if ticker and ticker not in tickers:
            tickers.append(ticker)
    return tickers


def archive_deprecated_settings(project_root: Path, archive_root: Path) -> dict[str, Any]:
    archive_root.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    missing: list[str] = []
    for relative in DEFAULT_DEPRECATED_FILES:
        source = project_root / relative
        target = archive_root / relative.replace("/", "__")
        if not source.exists():
            missing.append(relative)
            continue
        shutil.copy2(source, target)
        copied.append(str(target))
    manifest = {
        "artifact_type": "stage7_deprecated_settings_archive",
        "artifact_schema_version": "stage7_contextual_bandit_v1",
        "generated_at_utc": now_utc(),
        "status": "created",
        "archive_root": str(archive_root),
        "copied_files": copied,
        "missing_files": missing,
        "non_claims": ["not_a_data_update", "not_a_benchmark_result"],
    }
    (archive_root / "deprecated_settings_archive_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
