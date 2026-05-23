from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.data.contracts import APPROVED_HORIZONS, HORIZON_TRADING_STEPS  # noqa: E402
from event_state_forecasting.split.purged_embargo import build_purged_embargoed_folds  # noqa: E402


def test_purged_embargo_folds_keep_lockbox_and_training_separate() -> None:
    labels, dates = _labels()
    config = _config(dates)

    artifacts = build_purged_embargoed_folds(
        labels,
        split_config=config,
        artifact_version="test_stage4",
        input_artifact_version="test_stage3",
        row_universe_digest="digest",
    )

    assert len(artifacts.fold_definitions) == 1
    fold = artifacts.fold_definitions.iloc[0]
    fold_rows = artifacts.assignments[artifacts.assignments["fold_id"] == fold["fold_id"]]
    train_rows = fold_rows[fold_rows["split_role"] == "train"]
    validation_rows = fold_rows[fold_rows["split_role"] == "validation"]
    lockbox_rows = fold_rows[fold_rows["split_role"] == "lockbox"]

    assert not train_rows.empty
    assert not validation_rows.empty
    assert not lockbox_rows.empty
    assert train_rows["as_of_date"].max() < fold["validation_start_date"]
    assert train_rows["label_window_end"].max() < fold["validation_start_date"]
    assert validation_rows["as_of_date"].between(fold["validation_start_date"], fold["validation_end_date"]).all()
    assert (lockbox_rows["as_of_date"] >= artifacts.lockbox_record["start_date"]).all()
    assert artifacts.manifest["split_protocol"]["random_shuffle_allowed"] is False
    assert artifacts.manifest["benchmark_claim"] is False


def test_purged_embargo_folds_accept_explicit_post_lockbox_start() -> None:
    labels, dates = _labels()
    config = _config(dates)
    config["lockbox"] = {
        "policy": "explicit_post_stage6_lockbox_holdout_start_date",
        "fraction": 0.10,
        "start_date": dates[70],
        "expected_start_date": dates[70],
    }

    artifacts = build_purged_embargoed_folds(
        labels,
        split_config=config,
        artifact_version="test_stage4",
        input_artifact_version="test_stage3",
        row_universe_digest="digest",
    )

    assert artifacts.lockbox_record["policy"] == "explicit_final_untouched_start_date"
    assert artifacts.lockbox_record["start_date"] == dates[70]
    assert artifacts.lockbox_record["date_count"] == 10


def _labels() -> tuple[pd.DataFrame, list[str]]:
    dates = [value.date().isoformat() for value in pd.bdate_range("2024-01-02", periods=80)]
    rows = []
    for idx, as_of_date in enumerate(dates):
        for horizon in APPROVED_HORIZONS:
            end_idx = min(idx + HORIZON_TRADING_STEPS[horizon], len(dates) - 1)
            rows.append(
                {
                    "benchmark_family_id": "phase1_top50",
                    "dataset_version": "test_dataset",
                    "canonical_ticker": "AAA",
                    "as_of_date": as_of_date,
                    "horizon_id": horizon,
                    "label_window_start": dates[min(idx + 1, len(dates) - 1)],
                    "label_window_end": dates[end_idx],
                    "label_available_flag": True,
                }
            )
    return pd.DataFrame(rows), dates


def _config(dates: list[str]) -> dict[str, object]:
    return {
        "artifact_schema_version": "stage4_splits_v1",
        "split_protocol": "purged_embargoed_walk_forward_with_final_untouched_lockbox",
        "horizons": list(APPROVED_HORIZONS),
        "fold_schedule": {
            "cadence": "monthly",
            "training_window": "expanding",
            "initial_training_date_count": 5,
            "validation_date_count": 5,
        },
        "purge_embargo": {"policy": "maximum_approved_label_horizon", "trading_date_count": 60},
        "lockbox": {"fraction": 0.10, "expected_start_date": dates[72]},
    }
