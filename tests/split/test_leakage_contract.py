from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.split.leakage_checks import validate_no_leakage  # noqa: E402
from event_state_forecasting.split.purged_embargo import build_purged_embargoed_folds  # noqa: E402
from tests.split.test_purged_embargo_contract import _config, _labels  # noqa: E402


def test_leakage_validation_passes_valid_stage4_splits() -> None:
    labels, dates = _labels()
    artifacts = build_purged_embargoed_folds(
        labels,
        split_config=_config(dates),
        artifact_version="test_stage4",
        input_artifact_version="test_stage3",
        row_universe_digest="digest",
    )

    report = validate_no_leakage(artifacts.assignments, artifacts.fold_definitions, artifacts.lockbox_record)

    assert report["status"] == "passed"
    assert report["violation_count"] == 0


def test_leakage_validation_fails_training_label_overlap() -> None:
    labels, dates = _labels()
    artifacts = build_purged_embargoed_folds(
        labels,
        split_config=_config(dates),
        artifact_version="test_stage4",
        input_artifact_version="test_stage3",
        row_universe_digest="digest",
    )
    bad_assignments = artifacts.assignments.copy()
    fold = artifacts.fold_definitions.iloc[0]
    train_index = bad_assignments[bad_assignments["split_role"] == "train"].index[0]
    bad_assignments.loc[train_index, "label_window_end"] = fold["validation_start_date"]

    report = validate_no_leakage(bad_assignments, artifacts.fold_definitions, artifacts.lockbox_record)

    assert report["status"] == "failed"
    assert any(item["check"] == "training_label_window_overlap" for item in report["violations"])


def test_leakage_validation_fails_non_train_preprocessing_fit() -> None:
    labels, dates = _labels()
    artifacts = build_purged_embargoed_folds(
        labels,
        split_config=_config(dates),
        artifact_version="test_stage4",
        input_artifact_version="test_stage3",
        row_universe_digest="digest",
    )
    bad_assignments = artifacts.assignments.copy()
    validation_index = bad_assignments[bad_assignments["split_role"] == "validation"].index[0]
    bad_assignments.loc[validation_index, "preprocessing_fit_allowed"] = True

    report = validate_no_leakage(bad_assignments, artifacts.fold_definitions, artifacts.lockbox_record)

    assert report["status"] == "failed"
    assert any(item["check"] == "preprocessing_fit_train_only" for item in report["violations"])
