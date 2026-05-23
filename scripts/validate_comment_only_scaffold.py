#!/usr/bin/env python3
"""Validate that active scaffold trees are comment-only.

The active-root rebuild still keeps future-stage `src/`, `configs/`, and
`tests/` files as comment-only scaffolds. Approved Stage 2 through Stage 7C paths
and the Stage 8 ops test path are explicitly exempt because they have been
converted to executable code with tests.

Scope: only `.py`, `.yml`, `.yaml` files under `src/`, `configs/`, and `tests/`.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIRS = ("src", "configs", "tests")
ALLOWED_EXTENSIONS = {".py", ".yml", ".yaml"}
APPROVED_EXECUTABLE_RELATIVE_PATHS = {
    "configs/features.yaml",
    "configs/artifact_packet.yaml",
    "configs/evaluation.yaml",
    "configs/labels.yaml",
    "configs/models.yaml",
    "configs/splits.yaml",
    "configs/stage7_contextual_bandit.example.yaml",
    "configs/stage7_contextual_bandit.yaml",
    "configs/stage7_splits_post_lockbox_2026-05-22.yaml",
    "src/event_state_forecasting/cli/build_benchmark_dataset.py",
    "src/event_state_forecasting/cli/build_features_and_labels.py",
    "src/event_state_forecasting/cli/build_splits_and_packet.py",
    "src/event_state_forecasting/cli/run_benchmark.py",
    "src/event_state_forecasting/cli/run_stage7_contextual_bandit.py",
    "src/event_state_forecasting/cli/run_stage7_final_execution.py",
    "src/event_state_forecasting/cli/generate_prediction_outputs.py",
    "src/event_state_forecasting/cli/train_models_and_predict.py",
    "src/event_state_forecasting/benchmark/artifact_packet.py",
    "src/event_state_forecasting/benchmark/runner.py",
    "src/event_state_forecasting/data/contracts.py",
    "src/event_state_forecasting/data/universe.py",
    "src/event_state_forecasting/dataset/dataset_versioning.py",
    "src/event_state_forecasting/dataset/panel_builder.py",
    "src/event_state_forecasting/dataset/row_universe.py",
    "src/event_state_forecasting/evaluation/comparison_summary.py",
    "src/event_state_forecasting/evaluation/ranking.py",
    "src/event_state_forecasting/evaluation/regression.py",
    "src/event_state_forecasting/evaluation/statistical_tests.py",
    "src/event_state_forecasting/features/embeddings.py",
    "src/event_state_forecasting/features/event_state.py",
    "src/event_state_forecasting/features/labels.py",
    "src/event_state_forecasting/features/market.py",
    "src/event_state_forecasting/features/news_alignment.py",
    "src/event_state_forecasting/features/no_news_state.py",
    "src/event_state_forecasting/models/comparator_ladder.py",
    "src/event_state_forecasting/models/gated_fusion.py",
    "src/event_state_forecasting/models/inference.py",
    "src/event_state_forecasting/models/market_baselines.py",
    "src/event_state_forecasting/models/training.py",
    "src/event_state_forecasting/split/leakage_checks.py",
    "src/event_state_forecasting/split/lockbox.py",
    "src/event_state_forecasting/split/purged_embargo.py",
    "src/event_state_forecasting/stage7/__init__.py",
    "src/event_state_forecasting/stage7/artifacts.py",
    "src/event_state_forecasting/stage7/config.py",
    "src/event_state_forecasting/stage7/context.py",
    "src/event_state_forecasting/stage7/data_update.py",
    "src/event_state_forecasting/stage7/final_execution.py",
    "src/event_state_forecasting/stage7/metrics.py",
    "src/event_state_forecasting/stage7/policies.py",
    "src/event_state_forecasting/stage7/replay.py",
    "src/event_state_forecasting/stage10/__init__.py",
    "src/event_state_forecasting/stage10/prediction_outputs.py",
    "tests/benchmark/test_artifact_packet_contract.py",
    "tests/benchmark/test_benchmark_runner_contract.py",
    "tests/data/test_contracts_contract.py",
    "tests/dataset/test_panel_builder_contract.py",
    "tests/dataset/test_row_universe_contract.py",
    "tests/evaluation/test_metric_contracts.py",
    "tests/features/test_event_state_contract.py",
    "tests/features/test_labels_contract.py",
    "tests/features/test_market_features_contract.py",
    "tests/features/test_news_alignment_contract.py",
    "tests/features/test_no_news_state_contract.py",
    "tests/models/test_comparator_ladder_contract.py",
    "tests/models/test_gated_fusion_contract.py",
    "tests/models/test_saved_predictions_contract.py",
    "tests/models/test_training_contract.py",
    "tests/split/test_leakage_contract.py",
    "tests/split/test_purged_embargo_contract.py",
    "tests/stage7/test_stage7_config_contract.py",
    "tests/stage7/test_stage7_context_contract.py",
    "tests/stage7/test_stage7_final_execution_contract.py",
    "tests/stage7/test_stage7_policy_metrics_contract.py",
    "tests/stage10/test_prediction_outputs_contract.py",
    "tests/ops/test_stage8_data_update_contract.py",
}


@dataclass(frozen=True, slots=True)
class Violation:
    path: Path
    line_no: int
    line: str


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate comment-only scaffold trees.")
    parser.add_argument(
        "--paths",
        nargs="*",
        default=list(DEFAULT_DIRS),
        help="Relative paths to validate (default: src configs tests).",
    )
    parser.add_argument("--max-violations", type=int, default=50)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    roots = [resolve_root(value) for value in args.paths]

    violations: list[Violation] = []
    scanned_files = 0
    missing_roots = [root for root in roots if not root.exists()]
    if missing_roots:
        for root in missing_roots:
            print(f"ERROR: missing scaffold root: {root}")
        return 2

    for root in roots:
        for path in iter_scaffold_files(root):
            scanned_files += 1
            violations.extend(find_violations(path, max_count=args.max_violations - len(violations)))
            if len(violations) >= args.max_violations:
                break
        if len(violations) >= args.max_violations:
            break

    if violations:
        print(f"COMMENT_ONLY_VALIDATION FAILED: {len(violations)} violation(s)")
        for item in violations:
            relative = item.path.relative_to(PROJECT_ROOT)
            excerpt = item.line.rstrip("\n")
            print(f"- {relative}:{item.line_no}: {excerpt}")
        return 1

    print(f"COMMENT_ONLY_VALIDATION PASSED (files_scanned={scanned_files})")
    return 0


def resolve_root(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def iter_scaffold_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        yield path


def find_violations(path: Path, *, max_count: int) -> list[Violation]:
    if is_approved_executable_path(path):
        return []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        return [Violation(path=path, line_no=0, line=f"<unreadable: {exc}>")]

    violations: list[Violation] = []
    for idx, line in enumerate(text.splitlines(True), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        violations.append(Violation(path=path, line_no=idx, line=line))
        if len(violations) >= max_count:
            break
    return violations


def is_approved_executable_path(path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return False
    return relative in APPROVED_EXECUTABLE_RELATIVE_PATHS


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
