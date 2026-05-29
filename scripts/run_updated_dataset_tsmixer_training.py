from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import optuna
import pandas as pd
from pandas.api.types import is_bool_dtype, is_numeric_dtype


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    HORIZON_WEIGHTS,
    ROW_KEY,
    TSMIXER_ARCHITECTURE_VERSION,
    TSMIXER_INVALIDATED_READOUT_POLICY,
    TSMIXER_READOUT_POLICY,
    _apply_sequence_normalization,
    _normalization_stats,
    _stage32_metric_row,
    _train_gaps,
    compute_pairwise_deltas,
    sha256_file,
    stable_digest,
)


UPDATED_STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1"
UPDATED_STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
PREVIOUS_XGBOOST_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80"
UPDATED_XGBOOST_ROOT = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__20260528T100000Z__src_6dff1bd__run_40f1c9a0"
RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"

GENERATED_TOKEN = "20260528T120000Z"
GENERATED_AT_UTC = "2026-05-28T12:00:00Z"
SOURCE_ID = "6dff1bd"
DEFAULT_TRIAL_COUNT = 800
DEFAULT_WINDOW_LENGTHS = (20, 60)
DEFAULT_FIXED_WINDOW_LENGTH = 60
DEFAULT_FIXED_SEEDS = (2026054301, 2026054302, 2026054303, 2026054304, 2026054305)
DEFAULT_TUNING_SEEDS = (2026054401, 2026054402)
DEFAULT_FIXED_EPOCHS = 8
DEFAULT_TUNING_EPOCHS = 10
DEFAULT_FIXED_BATCH_SIZE = 1024
FINAL_MODEL_ID = "updated_av_tsmixer_event_market_optuna_v1_seed_mean"
TUNING_MODEL_ID_PREFIX = "updated_av_tsmixer_event_market_optuna_v1"
FIXED_MODEL_ID_PREFIX = "updated_av_tsmixer_event_market_fixed"
PREVIOUS_XGBOOST_MODEL_ID = "market_xgboost_v2_frozen_final"
UPDATED_XGBOOST_MODEL_ID = "updated_av_xgboost_event_market_optuna_v1"


def updated_tsmixer_training_contract(
    trial_count: int = DEFAULT_TRIAL_COUNT,
    tuning_seeds: tuple[int, ...] = DEFAULT_TUNING_SEEDS,
    fixed_seeds: tuple[int, ...] = DEFAULT_FIXED_SEEDS,
    tuning_epochs: int = DEFAULT_TUNING_EPOCHS,
    fixed_epochs: int = DEFAULT_FIXED_EPOCHS,
) -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_tsmixer_training_contract",
        "generated_at_utc": GENERATED_AT_UTC,
        "model_id": FINAL_MODEL_ID,
        "candidate_model_id_prefix": TUNING_MODEL_ID_PREFIX,
        "fixed_model_id_prefix": FIXED_MODEL_ID_PREFIX,
        "trial_count": int(trial_count),
        "minimum_required_trials": 800,
        "feature_scope": "updated_alpha_vantage_market_plus_event_state_sequences",
        "architecture": {
            "version": TSMIXER_ARCHITECTURE_VERSION,
            "readout_policy": TSMIXER_READOUT_POLICY,
            "invalidates_prior_readout_policy": TSMIXER_INVALIDATED_READOUT_POLICY,
        },
        "window_lengths": list(DEFAULT_WINDOW_LENGTHS),
        "fixed_multiseed_benchmark": {
            "window_length": DEFAULT_FIXED_WINDOW_LENGTH,
            "seeds": list(fixed_seeds),
            "seed_count": len(fixed_seeds),
            "epochs": int(fixed_epochs),
            "batch_size": DEFAULT_FIXED_BATCH_SIZE,
        },
        "tuning": {
            "seeds": list(tuning_seeds),
            "seed_count": len(tuning_seeds),
            "epochs": int(tuning_epochs),
            "split_roles_for_selection": ["train", "validation"],
            "lockbox_rows_used_for_tuning": 0,
        },
        "optuna": {
            "direction": "minimize",
            "sampler": "TPESampler",
            "sampler_seed": 2026052804,
            "n_startup_trials": 80,
            "multivariate": True,
        },
        "search_space": {
            "window_length": {"type": "categorical", "choices": [20, 60]},
            "mixer_blocks": {"type": "categorical", "choices": [1, 2, 3, 4]},
            "hidden_time": {"type": "categorical", "choices": [32, 64, 96, 128, 192]},
            "hidden_feature": {"type": "categorical", "choices": [64, 128, 192, 256, 384]},
            "head_hidden": {"type": "categorical", "choices": [0, 32, 64, 128]},
            "dropout": {"type": "categorical", "choices": [0.0, 0.05, 0.10, 0.20]},
            "learning_rate": {"type": "log_float", "low": 5e-5, "high": 5e-3},
            "weight_decay": {"type": "log_float", "low": 1e-7, "high": 1e-2},
            "batch_size": {"type": "categorical", "choices": [256, 512, 1024, 2048]},
            "grad_clip_norm": {"type": "categorical", "choices": [0.5, 1.0, 2.0, 5.0]},
        },
        "selection_objective": {
            "name": "validation_weighted_rmse_mae_with_overfit_penalty",
            "metric_direction": "lower_is_better",
            "horizon_weights": HORIZON_WEIGHTS,
            "metric_weights": {"rmse": 0.5, "mae": 0.5},
            "lockbox_policy": "no_lockbox_rows_or_metrics_used_for_trial_selection",
        },
        "final_evaluation_split_roles": ["train", "validation", "lockbox"],
        "lockbox_rows_used_for_tuning": 0,
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": [
            "complete_tsmixer_training_evidence_not_positive_claim",
            "development_tuning_uses_train_validation_only",
            "lockbox_not_used_for_tuning_or_selection",
            "final_lockbox_evaluation_is_post_selection_evidence",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }


def _parse_seeds(value: str) -> tuple[int, ...]:
    seeds = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return seeds


def main() -> None:
    parser = argparse.ArgumentParser(description="Run complete updated-dataset TSMixer sequence training, tuning, and benchmark evaluation.")
    parser.add_argument("--stage3-root", type=Path, default=UPDATED_STAGE3_ROOT)
    parser.add_argument("--stage4-root", type=Path, default=UPDATED_STAGE4_ROOT)
    parser.add_argument("--previous-xgboost-root", type=Path, default=PREVIOUS_XGBOOST_ROOT)
    parser.add_argument("--updated-xgboost-root", type=Path, default=UPDATED_XGBOOST_ROOT)
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--tuning-epochs", type=int, default=DEFAULT_TUNING_EPOCHS)
    parser.add_argument("--fixed-epochs", type=int, default=DEFAULT_FIXED_EPOCHS)
    parser.add_argument("--tuning-seeds", type=_parse_seeds, default=DEFAULT_TUNING_SEEDS)
    parser.add_argument("--fixed-seeds", type=_parse_seeds, default=DEFAULT_FIXED_SEEDS)
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()
    if args.trial_count < 800:
        raise RuntimeError("updated-dataset TSMixer training requires at least 800 tuning trials")

    stage3_root = args.stage3_root.resolve()
    stage4_root = args.stage4_root.resolve()
    previous_xgboost_root = args.previous_xgboost_root.resolve()
    updated_xgboost_root = args.updated_xgboost_root.resolve()
    contract = updated_tsmixer_training_contract(args.trial_count, args.tuning_seeds, args.fixed_seeds, args.tuning_epochs, args.fixed_epochs)
    contract["updated_stage3_root"] = _rel(stage3_root)
    contract["updated_stage4_root"] = _rel(stage4_root)
    contract["previous_xgboost_root"] = _rel(previous_xgboost_root)
    contract["updated_xgboost_root"] = _rel(updated_xgboost_root) if updated_xgboost_root.exists() else None
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_updated_av__stage44__tsmixer_training__{GENERATED_TOKEN}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root.resolve() if args.output_root else RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    started = time.perf_counter()
    contract_path = output_root / "tsmixer_training_contract.json"
    _write_json(contract_path, contract)

    sequence_root = output_root / "sequence_windows"
    sequence_manifest = _materialize_sequence_windows(stage3_root, stage4_root, sequence_root, DEFAULT_WINDOW_LENGTHS)
    frame_cache = _SequenceFrameCache(sequence_manifest, stage3_root, stage4_root)

    fixed_outputs = _run_or_load_fixed_benchmark(output_root, frame_cache, contract)
    tuning_outputs = _run_or_load_tuning(output_root, frame_cache, contract)
    final_outputs = _run_or_load_final_evaluation(output_root, frame_cache, tuning_outputs["best_trial"], contract)
    comparison_summary = _build_comparison_summary(final_outputs["metrics"], previous_xgboost_root, updated_xgboost_root)
    standalone_summary = _standalone_metric_summary(final_outputs["metrics"], FINAL_MODEL_ID)

    manifest_path = output_root / "updated_dataset_tsmixer_training_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage44_updated_dataset_tsmixer_training_report.md"
    comparison_json_path = output_root / "comparison_summary.json"
    comparison_md_path = output_root / "comparison_summary.md"
    _write_json(comparison_json_path, comparison_summary)
    comparison_md_path.write_text(_render_comparison_markdown(comparison_summary), encoding="utf-8")

    manifest = {
        "artifact_type": "updated_dataset_tsmixer_training_manifest",
        "artifact_id": f"updated_dataset_tsmixer_training__{sha256_file(tuning_outputs['trial_ledger_path'])[:12]}__{GENERATED_TOKEN}",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed" if tuning_outputs["trial_count_completed"] >= int(args.trial_count) else "partial",
        "model_id": FINAL_MODEL_ID,
        "candidate_model_id_prefix": TUNING_MODEL_ID_PREFIX,
        "architecture": contract["architecture"],
        "feature_summary": sequence_manifest["feature_summary"],
        "sequence_summary": sequence_manifest["validation"],
        "fixed_benchmark_summary": fixed_outputs["summary"],
        "trial_count_requested": int(args.trial_count),
        "trial_count_completed": tuning_outputs["trial_count_completed"],
        "trial_count_failed": tuning_outputs["trial_count_failed"],
        "best_development_trial": tuning_outputs["best_trial"],
        "standalone_metric_summary": standalone_summary,
        "comparison_summary": comparison_summary,
        "lockbox_rows_used_for_tuning": 0,
        "outputs": {
            "contract": _rel(contract_path),
            "sequence_manifest": _rel(sequence_root / "sequence_window_manifest.json"),
            **fixed_outputs["outputs"],
            **tuning_outputs["outputs"],
            **final_outputs["outputs"],
            "comparison_json": _rel(comparison_json_path),
            "comparison_markdown": _rel(comparison_md_path),
            "manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
            "report": _rel(report_path),
        },
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": contract["non_claims"],
    }
    _write_json(manifest_path, manifest)
    _write_json(run_manifest_path, {"stage": 44, "stage_name": "updated_dataset_tsmixer_training", "status": manifest["status"], "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_render_report(manifest), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "trial_count_completed": manifest["trial_count_completed"], "best_trial_number": manifest["best_development_trial"].get("trial_number"), "manifest": manifest["outputs"]["manifest"]}, sort_keys=True))


def _materialize_sequence_windows(stage3_root: Path, stage4_root: Path, sequence_root: Path, window_lengths: tuple[int, ...]) -> dict[str, Any]:
    manifest_path = sequence_root / "sequence_window_manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    sequence_root.mkdir(parents=True, exist_ok=True)
    market = pd.read_parquet(stage3_root / "market_features.parquet")
    event = pd.read_parquet(stage3_root / "event_state_features.parquet")
    market["as_of_date"] = pd.to_datetime(market["as_of_date"]).dt.strftime("%Y-%m-%d")
    event["as_of_date"] = pd.to_datetime(event["as_of_date"]).dt.strftime("%Y-%m-%d")
    market_columns = _numeric_feature_columns(market, ROW_KEY)
    event_columns = _numeric_feature_columns(event, ROW_KEY)
    feature_columns = market_columns + event_columns
    features = market[[*ROW_KEY, *market_columns]].merge(event[[*ROW_KEY, *event_columns]], on=ROW_KEY, how="inner", validate="one_to_one")
    base_key = ["benchmark_family_id", "canonical_ticker", "as_of_date"]
    unique_keys = features[base_key].drop_duplicates().shape[0]
    unique_key_features = features[[*base_key, *feature_columns]].drop_duplicates().shape[0]
    if unique_keys != unique_key_features:
        raise RuntimeError("updated TSMixer features vary by horizon; sequence materialization requires date-level features")
    base = features[[*base_key, *feature_columns]].drop_duplicates(base_key).sort_values(["canonical_ticker", "as_of_date"]).reset_index(drop=True)
    base["sequence_base_index"] = np.arange(len(base), dtype="int32")
    row_index = features[[*ROW_KEY]].merge(base[[*base_key, "sequence_base_index"]], on=base_key, how="left", validate="many_to_one")
    if row_index["sequence_base_index"].isna().any():
        raise RuntimeError("updated TSMixer sequence row index has unmapped rows")

    base_index_path = sequence_root / "sequence_base_index.parquet"
    row_index_path = sequence_root / "sequence_row_index.parquet"
    base[[*base_key, "sequence_base_index"]].to_parquet(base_index_path, index=False)
    row_index.to_parquet(row_index_path, index=False)

    tensor_outputs: dict[str, dict[str, Any]] = {}
    build_started = time.perf_counter()
    for window_length in window_lengths:
        values, mask = _build_sequence_tensors(base, feature_columns, int(window_length))
        values_path = sequence_root / f"sequence_{int(window_length)}d_values.npy"
        mask_path = sequence_root / f"sequence_{int(window_length)}d_observed_mask.npy"
        np.save(values_path, values)
        np.save(mask_path, mask)
        tensor_outputs[f"{int(window_length)}d"] = {
            "values": _rel(values_path),
            "observed_mask": _rel(mask_path),
            "shape": list(values.shape),
            "observed_fraction": float(mask.mean()),
            "values_digest_sha256": sha256_file(values_path),
            "mask_digest_sha256": sha256_file(mask_path),
        }

    splits = pd.read_parquet(stage4_root / "split_assignments.parquet", columns=["fold_id", *ROW_KEY, "split_role", "lockbox_flag"])
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
    missing = splits.merge(row_index[[*ROW_KEY, "sequence_base_index"]], on=ROW_KEY, how="left")["sequence_base_index"].isna().sum()
    validation = {
        "feature_rows": int(len(features)),
        "unique_sequence_rows": int(len(base)),
        "row_index_rows": int(len(row_index)),
        "row_index_duplicate_keys": int(row_index.duplicated(ROW_KEY).sum()),
        "stage4_train_validation_lockbox_rows": int(len(splits)),
        "stage4_rows_missing_sequence_index": int(missing),
        "status": "passed",
    }
    if validation["row_index_duplicate_keys"] or validation["stage4_rows_missing_sequence_index"]:
        validation["status"] = "failed"
        raise RuntimeError(f"updated TSMixer sequence validation failed: {validation}")
    manifest = {
        "artifact_type": "updated_dataset_tsmixer_sequence_window_manifest",
        "artifact_id": f"updated_dataset_tsmixer_sequence_windows__{sha256_file(base_index_path)[:12]}__{GENERATED_TOKEN}",
        "generated_at_utc": GENERATED_AT_UTC,
        "status": "completed",
        "feature_summary": {
            "feature_count": len(feature_columns),
            "market_feature_count": len(market_columns),
            "event_state_feature_count": len(event_columns),
            "feature_columns": feature_columns,
        },
        "feature_columns": feature_columns,
        "window_lengths": list(window_lengths),
        "tensor_policy": {
            "row_level": "unique benchmark_family_id/canonical_ticker/as_of_date sequences mapped to horizon rows by sequence_row_index",
            "padding_policy": "left_pad_missing_history_with_zero_values_and_false_observed_mask",
            "normalization_policy": "fold_local_train_only_normalization_in_tsmixer_training",
            "value_dtype": "float32",
            "mask_dtype": "bool",
        },
        "validation": validation,
        "runtime_seconds": round(time.perf_counter() - build_started, 3),
        "outputs": {"sequence_base_index": _rel(base_index_path), "sequence_row_index": _rel(row_index_path), "manifest": _rel(manifest_path), **tensor_outputs},
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "non_claims": ["not_tsmixer_model_evidence_by_itself", "not_positive_benchmark_claim", "not_trading_signal"],
    }
    _write_json(manifest_path, manifest)
    return manifest


def _numeric_feature_columns(frame: pd.DataFrame, key_columns: list[str]) -> list[str]:
    excluded = set(key_columns) | {"dataset_version", "feature_availability_timestamp", "prediction_timestamp"}
    columns = []
    for column in frame.columns:
        if column in excluded:
            continue
        if is_numeric_dtype(frame[column]) or is_bool_dtype(frame[column]):
            columns.append(column)
    return columns


def _build_sequence_tensors(base: pd.DataFrame, feature_columns: list[str], window_length: int) -> tuple[np.ndarray, np.ndarray]:
    values = np.zeros((len(base), window_length, len(feature_columns)), dtype="float32")
    mask = np.zeros((len(base), window_length, len(feature_columns)), dtype=bool)
    for _, group in base.groupby("canonical_ticker", sort=False):
        group = group.sort_values("as_of_date")
        indices = group["sequence_base_index"].to_numpy(dtype="int64")
        raw = group[feature_columns].to_numpy(dtype="float32")
        observed = ~np.isnan(raw)
        raw = np.nan_to_num(raw, nan=0.0).astype("float32", copy=False)
        for local_pos, global_index in enumerate(indices):
            start = max(0, local_pos - window_length + 1)
            seq = raw[start : local_pos + 1]
            seq_mask = observed[start : local_pos + 1]
            dst_start = window_length - len(seq)
            values[global_index, dst_start:, :] = seq
            mask[global_index, dst_start:, :] = seq_mask
    return values, mask


class _SequenceFrameCache:
    def __init__(self, sequence_manifest: dict[str, Any], stage3_root: Path, stage4_root: Path) -> None:
        self.sequence_manifest = sequence_manifest
        self.stage3_root = stage3_root
        self.stage4_root = stage4_root
        self._cache: dict[int, tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str]]] = {}

    def get(self, window_length: int) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str]]:
        if int(window_length) not in self._cache:
            key = f"{int(window_length)}d"
            if key not in self.sequence_manifest["outputs"]:
                raise RuntimeError(f"sequence manifest does not contain {key} tensors")
            values = np.load(PROJECT_ROOT / self.sequence_manifest["outputs"][key]["values"], mmap_mode="r")
            mask = np.load(PROJECT_ROOT / self.sequence_manifest["outputs"][key]["observed_mask"], mmap_mode="r")
            row_index = pd.read_parquet(PROJECT_ROOT / self.sequence_manifest["outputs"]["sequence_row_index"])
            labels = pd.read_parquet(self.stage3_root / "labels.parquet", columns=[*ROW_KEY, "forward_excess_return"])
            splits = pd.read_parquet(self.stage4_root / "split_assignments.parquet", columns=["fold_id", *ROW_KEY, "split_role", "lockbox_flag"])
            splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
            frame = splits.merge(row_index, on=ROW_KEY, how="inner", validate="many_to_one").merge(labels, on=ROW_KEY, how="inner", validate="many_to_one")
            frame = frame.rename(columns={"forward_excess_return": "target"})
            frame["row_key"] = frame[ROW_KEY].astype(str).agg("|".join, axis=1)
            frame["dataset_version"] = "phase1_top50_updated_av_stage3"
            frame["split_artifact_version"] = "updated_stage4_splits_v1"
            self._cache[int(window_length)] = (frame, values, mask, list(self.sequence_manifest["feature_columns"]))
        return self._cache[int(window_length)]


class _UpdatedTSMixer:
    def __new__(cls, window_length: int, feature_count: int, config: dict[str, Any]):
        import torch
        from torch import nn
        readout_size = int(window_length) * int(feature_count)

        class MixerBlock(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.time_norm = nn.LayerNorm(feature_count)
                self.time_mlp = nn.Sequential(
                    nn.Linear(window_length, int(config["hidden_time"])),
                    nn.GELU(),
                    nn.Dropout(float(config["dropout"])),
                    nn.Linear(int(config["hidden_time"]), window_length),
                )
                self.feature_mlp = nn.Sequential(
                    nn.LayerNorm(feature_count),
                    nn.Linear(feature_count, int(config["hidden_feature"])),
                    nn.GELU(),
                    nn.Dropout(float(config["dropout"])),
                    nn.Linear(int(config["hidden_feature"]), feature_count),
                )

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                y = self.time_norm(x).transpose(1, 2)
                x = x + self.time_mlp(y).transpose(1, 2)
                x = x + self.feature_mlp(x)
                return x

        class Model(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.architecture_version = TSMIXER_ARCHITECTURE_VERSION
                self.readout_policy = TSMIXER_READOUT_POLICY
                self.input_norm = nn.LayerNorm(feature_count)
                self.blocks = nn.ModuleList([MixerBlock() for _ in range(int(config["mixer_blocks"]))])
                head_hidden = int(config["head_hidden"])
                if head_hidden > 0:
                    self.head = nn.Sequential(nn.LayerNorm(readout_size), nn.Linear(readout_size, head_hidden), nn.GELU(), nn.Linear(head_hidden, 1))
                else:
                    self.head = nn.Sequential(nn.LayerNorm(readout_size), nn.Linear(readout_size, 1))

            def forward(self, x: torch.Tensor) -> torch.Tensor:
                x = self.input_norm(x)
                for block in self.blocks:
                    x = block(x)
                return self.head(x.reshape(x.shape[0], -1))

        return Model()


def _run_or_load_fixed_benchmark(output_root: Path, cache: _SequenceFrameCache, contract: dict[str, Any]) -> dict[str, Any]:
    manifest_path = output_root / "fixed_multiseed_benchmark_manifest.json"
    metrics_path = output_root / "fixed_multiseed_metrics.parquet"
    fit_path = output_root / "fixed_multiseed_fit_manifest.parquet"
    if manifest_path.exists() and metrics_path.exists() and fit_path.exists():
        if not _fit_manifest_matches_current_architecture(fit_path):
            raise RuntimeError("existing fixed TSMixer benchmark uses stale mean-pooling readout; rerun Stage 44 with the corrected architecture before reuse")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return {"summary": manifest["summary"], "outputs": {f"fixed_{key}": value for key, value in manifest["outputs"].items()}}
    fixed = contract["fixed_multiseed_benchmark"]
    config = {
        "window_length": int(fixed["window_length"]),
        "mixer_blocks": 1,
        "hidden_time": 32,
        "hidden_feature": 64,
        "head_hidden": 0,
        "dropout": 0.0,
        "learning_rate": 0.001,
        "weight_decay": 1e-4,
        "batch_size": int(fixed["batch_size"]),
        "grad_clip_norm": 2.0,
    }
    predictions, metrics, fit_manifest = _fit_config(
        cache,
        config,
        tuple(int(seed) for seed in fixed["seeds"]),
        int(fixed["epochs"]),
        model_id_prefix=FIXED_MODEL_ID_PREFIX,
        trial_number=None,
        split_roles=("train", "validation", "lockbox"),
        save_predictions=True,
        seed_mean_model_id=f"{FIXED_MODEL_ID_PREFIX}_seed_mean",
    )
    predictions_path = output_root / "fixed_multiseed_predictions.parquet"
    seed_summary_path = output_root / "fixed_multiseed_seed_summary.parquet"
    predictions.to_parquet(predictions_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    fit_manifest.to_parquet(fit_path, index=False)
    seed_summary = _seed_summary(metrics, f"{FIXED_MODEL_ID_PREFIX}_seed_mean")
    seed_summary.to_parquet(seed_summary_path, index=False)
    summary = {
        "status": "completed",
        "model_id_prefix": FIXED_MODEL_ID_PREFIX,
        "seed_mean_model_id": f"{FIXED_MODEL_ID_PREFIX}_seed_mean",
        "window_length": int(fixed["window_length"]),
        "seed_count": len(fixed["seeds"]),
        "epochs": int(fixed["epochs"]),
        "metric_summary": _metric_summary(metrics, f"{FIXED_MODEL_ID_PREFIX}_seed_mean"),
        "lockbox_used_for_selection": False,
    }
    outputs = {"predictions": _rel(predictions_path), "metrics": _rel(metrics_path), "fit_manifest": _rel(fit_path), "seed_summary": _rel(seed_summary_path), "manifest": _rel(manifest_path)}
    _write_json(manifest_path, {"artifact_type": "updated_dataset_tsmixer_fixed_multiseed_benchmark_manifest", "generated_at_utc": GENERATED_AT_UTC, "summary": summary, "outputs": outputs, "benchmark_claim": False, "positive_claim_approved": False})
    return {"summary": summary, "outputs": {f"fixed_{key}": value for key, value in outputs.items()}}


def _fit_manifest_matches_current_architecture(path: Path) -> bool:
    if not path.exists():
        return False
    frame = pd.read_parquet(path)
    if "architecture_version" not in frame.columns or "readout_policy" not in frame.columns:
        return False
    return bool((frame["architecture_version"] == TSMIXER_ARCHITECTURE_VERSION).all() and (frame["readout_policy"] == TSMIXER_READOUT_POLICY).all())


def _raise_if_existing_tuning_uses_stale_architecture(ledger_path: Path) -> None:
    if not ledger_path.exists():
        return
    ledger = _read_jsonl_frame(ledger_path)
    if ledger.empty or "status" not in ledger.columns:
        return
    completed = ledger[ledger["status"] == "completed"].copy()
    if completed.empty:
        return
    if "architecture_version" not in completed.columns or "readout_policy" not in completed.columns:
        raise RuntimeError("existing TSMixer tuning ledger predates the corrected readout; use a fresh output root before rerunning")
    stale = completed[(completed["architecture_version"] != TSMIXER_ARCHITECTURE_VERSION) | (completed["readout_policy"] != TSMIXER_READOUT_POLICY)]
    if not stale.empty:
        raise RuntimeError("existing TSMixer tuning ledger uses stale architecture; use a fresh output root before rerunning")


def _run_or_load_tuning(output_root: Path, cache: _SequenceFrameCache, contract: dict[str, Any]) -> dict[str, Any]:
    search_space_path = output_root / "search_space_manifest.json"
    ledger_jsonl_path = output_root / "trial_ledger.ndjson"
    metrics_jsonl_path = output_root / "trial_fold_metrics.ndjson"
    fit_jsonl_path = output_root / "trial_fit_manifest.ndjson"
    frontier_jsonl_path = output_root / "overfit_frontier.ndjson"
    storage_path = output_root / "optuna_study.sqlite3"
    _write_json(search_space_path, contract)
    _raise_if_existing_tuning_uses_stale_architecture(ledger_jsonl_path)

    sampler = optuna.samplers.TPESampler(
        seed=int(contract["optuna"]["sampler_seed"]),
        n_startup_trials=int(contract["optuna"]["n_startup_trials"]),
        multivariate=bool(contract["optuna"].get("multivariate", False)),
    )
    study = optuna.create_study(
        study_name="updated_av_tsmixer_event_market_800",
        direction="minimize",
        sampler=sampler,
        storage=f"sqlite:///{storage_path}",
        load_if_exists=True,
    )

    def objective(trial: optuna.Trial) -> float:
        trial_number = int(trial.number)
        prior = _read_trial_record(ledger_jsonl_path, trial_number)
        if prior and prior.get("status") == "completed":
            return float(prior["objective_value"])
        config = _suggest_tsmixer_config(trial, contract)
        record = _execute_tuning_trial(trial_number, config, cache, contract)
        _append_jsonl(ledger_jsonl_path, record["ledger"])
        for row in record["metrics"]:
            _append_jsonl(metrics_jsonl_path, row)
        for row in record["fit_manifest"]:
            _append_jsonl(fit_jsonl_path, row)
        _append_jsonl(frontier_jsonl_path, record["frontier"])
        print(json.dumps({"model_family": "tsmixer", "trial_number": trial_number, "status": record["ledger"]["status"], "objective_value": record["ledger"].get("objective_value")}, sort_keys=True), flush=True)
        return float(record["ledger"].get("objective_value", 1e9) or 1e9)

    max_batches = max(1, int(contract["trial_count"]) * 3)
    batches = 0
    while _successful_trial_count(ledger_jsonl_path) < int(contract["trial_count"]) and batches < max_batches:
        remaining_successes = int(contract["trial_count"]) - _successful_trial_count(ledger_jsonl_path)
        study.optimize(objective, n_trials=remaining_successes, show_progress_bar=False)
        batches += 1

    ledger = _read_jsonl_frame(ledger_jsonl_path)
    if ledger.empty or not (ledger["status"] == "completed").any():
        raise RuntimeError("updated-dataset TSMixer tuning produced no completed trials")
    metrics = _read_jsonl_frame(metrics_jsonl_path)
    fit_manifest = _read_jsonl_frame(fit_jsonl_path)
    frontier = _read_jsonl_frame(frontier_jsonl_path)
    completed = ledger[ledger["status"] == "completed"].copy()
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0].to_dict()
    best["params"] = json.loads(str(best["params_json"]))
    best["lockbox_used_for_selection"] = False
    best["positive_claim_approved"] = False
    best["benchmark_claim"] = False

    ledger_path = output_root / "trial_ledger.parquet"
    metrics_path = output_root / "trial_fold_metrics.parquet"
    fit_path = output_root / "trial_fit_manifest.parquet"
    frontier_path = output_root / "overfit_frontier.parquet"
    best_path = output_root / "best_development_candidate_config.json"
    ledger.to_parquet(ledger_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    fit_manifest.to_parquet(fit_path, index=False)
    frontier.to_parquet(frontier_path, index=False)
    _write_json(best_path, {"artifact_type": "updated_dataset_tsmixer_best_development_candidate_config", "generated_at_utc": GENERATED_AT_UTC, "model_id": FINAL_MODEL_ID, "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, "selected_trial_number": int(best["trial_number"]), "selection_basis": "train_validation_only", "best_trial": best, "lockbox_used_for_selection": False, "benchmark_claim": False, "positive_claim_approved": False})

    return {
        "trial_count_completed": int((ledger["status"] == "completed").sum()),
        "trial_count_failed": int((ledger["status"] == "failed").sum()),
        "best_trial": best,
        "trial_ledger_path": ledger_path,
        "outputs": {
            "search_space_manifest": _rel(search_space_path),
            "trial_ledger_ndjson": _rel(ledger_jsonl_path),
            "trial_ledger": _rel(ledger_path),
            "trial_fold_metrics_ndjson": _rel(metrics_jsonl_path),
            "trial_fold_metrics": _rel(metrics_path),
            "trial_fit_manifest_ndjson": _rel(fit_jsonl_path),
            "trial_fit_manifest": _rel(fit_path),
            "overfit_frontier_ndjson": _rel(frontier_jsonl_path),
            "overfit_frontier": _rel(frontier_path),
            "optuna_storage": _rel(storage_path),
            "best_development_candidate_config": _rel(best_path),
        },
    }


def _run_or_load_final_evaluation(output_root: Path, cache: _SequenceFrameCache, best_trial: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    metrics_path = output_root / "best_tsmixer_metrics.parquet"
    predictions_path = output_root / "best_tsmixer_predictions.parquet"
    fit_path = output_root / "best_tsmixer_fit_manifest.parquet"
    if metrics_path.exists() and predictions_path.exists() and fit_path.exists():
        if not _fit_manifest_matches_current_architecture(fit_path):
            raise RuntimeError("existing best TSMixer predictions use stale mean-pooling readout; rerun Stage 44 with the corrected architecture before reuse")
        return {"metrics": pd.read_parquet(metrics_path), "outputs": {"best_tsmixer_predictions": _rel(predictions_path), "best_tsmixer_metrics": _rel(metrics_path), "best_tsmixer_fit_manifest": _rel(fit_path)}}
    config = dict(best_trial["params"])
    predictions, metrics, fit_manifest = _fit_config(
        cache,
        config,
        tuple(int(seed) for seed in contract["tuning"]["seeds"]),
        int(contract["tuning"]["epochs"]),
        model_id_prefix=TUNING_MODEL_ID_PREFIX,
        trial_number=int(best_trial["trial_number"]),
        split_roles=("train", "validation", "lockbox"),
        save_predictions=True,
        seed_mean_model_id=FINAL_MODEL_ID,
    )
    predictions.to_parquet(predictions_path, index=False)
    metrics.to_parquet(metrics_path, index=False)
    fit_manifest.to_parquet(fit_path, index=False)
    return {"metrics": metrics, "outputs": {"best_tsmixer_predictions": _rel(predictions_path), "best_tsmixer_metrics": _rel(metrics_path), "best_tsmixer_fit_manifest": _rel(fit_path)}}


def _suggest_tsmixer_config(trial: optuna.Trial, contract: dict[str, Any]) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for name, spec in contract["search_space"].items():
        if spec["type"] == "categorical":
            config[name] = trial.suggest_categorical(name, list(spec["choices"]))
        elif spec["type"] == "log_float":
            config[name] = trial.suggest_float(name, float(spec["low"]), float(spec["high"]), log=True)
        else:
            raise RuntimeError(f"unsupported search-space type for {name}: {spec['type']}")
    return _normalize_config(config)


def _normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(config)
    for name in ["window_length", "mixer_blocks", "hidden_time", "hidden_feature", "head_hidden", "batch_size"]:
        normalized[name] = int(normalized[name])
    for name in ["dropout", "learning_rate", "weight_decay", "grad_clip_norm"]:
        normalized[name] = float(normalized[name])
    return normalized


def _execute_tuning_trial(trial_number: int, config: dict[str, Any], cache: _SequenceFrameCache, contract: dict[str, Any]) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        _, metrics, fit_manifest = _fit_config(
            cache,
            config,
            tuple(int(seed) for seed in contract["tuning"]["seeds"]),
            int(contract["tuning"]["epochs"]),
            model_id_prefix=TUNING_MODEL_ID_PREFIX,
            trial_number=trial_number,
            split_roles=("train", "validation"),
            save_predictions=False,
            seed_mean_model_id=None,
        )
        summary, frontier = _summarize_tsmixer_trial(trial_number, metrics, config)
        ledger = {"trial_number": int(trial_number), "status": "completed", "runtime_seconds": round(time.perf_counter() - started, 6), "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, "params_json": json.dumps(config, sort_keys=True), **summary}
        return {"ledger": ledger, "metrics": metrics.to_dict("records"), "fit_manifest": fit_manifest.to_dict("records"), "frontier": frontier}
    except Exception as exc:  # noqa: BLE001 - failed trials are evidence and must be logged.
        ledger = {"trial_number": int(trial_number), "status": "failed", "runtime_seconds": round(time.perf_counter() - started, 6), "failure_reason": repr(exc), "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, "params_json": json.dumps(config, sort_keys=True), "objective_value": 1e9, "lockbox_rows_used_for_tuning": 0}
        return {"ledger": ledger, "metrics": [], "fit_manifest": [], "frontier": ledger}


def _fit_config(
    cache: _SequenceFrameCache,
    config: dict[str, Any],
    seeds: tuple[int, ...],
    epochs: int,
    *,
    model_id_prefix: str,
    trial_number: int | None,
    split_roles: tuple[str, ...],
    save_predictions: bool,
    seed_mean_model_id: str | None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    import torch

    try:
        torch.set_float32_matmul_precision("medium")
    except Exception:  # noqa: BLE001 - optional speed hint only.
        pass
    frame, values, mask, feature_columns = cache.get(int(config["window_length"]))
    if "lockbox" not in split_roles:
        frame = frame[frame["split_role"].isin(split_roles)].copy()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    metric_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    batch_size = int(config["batch_size"])
    for seed_position, seed in enumerate(seeds, start=1):
        seed_id = f"seed_{seed_position:02d}"
        seed_offset = int(seed) + (0 if trial_number is None else int(trial_number) * 1009)
        torch.manual_seed(seed_offset)
        np_rng = np.random.default_rng(seed_offset)
        model_id = f"{model_id_prefix}_trial_{int(trial_number):04d}_{seed_id}" if trial_number is not None else f"{model_id_prefix}_{seed_id}"
        for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
            train = group[group["split_role"] == "train"].copy()
            score = group[group["split_role"].isin(split_roles)].copy()
            if train.empty or score.empty:
                continue
            fit_started = time.perf_counter()
            train_indices = train["sequence_base_index"].to_numpy(dtype="int64")
            means, stds = _normalization_stats(values, mask, train_indices)
            x_train_np = _apply_sequence_normalization(values, mask, train_indices, means, stds)
            y_train_np = train["target"].to_numpy(dtype="float32").reshape(-1, 1)
            x_train = torch.tensor(x_train_np, dtype=torch.float32, device=device)
            y_train = torch.tensor(y_train_np, dtype=torch.float32, device=device)
            model = _UpdatedTSMixer(window_length=int(config["window_length"]), feature_count=len(feature_columns), config=config).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=float(config["learning_rate"]), weight_decay=float(config["weight_decay"]))
            loss_fn = torch.nn.MSELoss()
            final_loss = float("nan")
            model.train()
            for _ in range(int(epochs)):
                order = np_rng.permutation(len(train))
                for start in range(0, len(order), batch_size):
                    batch_order = torch.tensor(order[start : start + batch_size], dtype=torch.long, device=device)
                    opt.zero_grad(set_to_none=True)
                    pred = model(x_train.index_select(0, batch_order))
                    loss = loss_fn(pred, y_train.index_select(0, batch_order))
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), float(config["grad_clip_norm"]))
                    opt.step()
                    final_loss = float(loss.detach().cpu())
            for split_role in split_roles:
                split = score[score["split_role"] == split_role].copy()
                if split.empty:
                    continue
                split_indices = split["sequence_base_index"].to_numpy(dtype="int64")
                split_prediction = _predict_model(model, values, mask, split_indices, means, stds, batch_size, device)
                metric_rows.append(_stage32_metric_row(-1 if trial_number is None else int(trial_number), seed_id, int(seed), model_id, fold_id, horizon_id, split_role, split["target"].to_numpy(dtype="float64"), split_prediction))
                if save_predictions:
                    prediction_frames.append(_prediction_frame(split, model_id, seed_id, int(seed), split_prediction))
            fit_rows.append({
                "trial_number": None if trial_number is None else int(trial_number),
                "model_id": model_id,
                "seed_id": seed_id,
                "seed": int(seed),
                "fold_id": fold_id,
                "horizon_id": horizon_id,
                "window_length": int(config["window_length"]),
                "feature_count": int(len(feature_columns)),
                "architecture_version": TSMIXER_ARCHITECTURE_VERSION,
                "readout_policy": TSMIXER_READOUT_POLICY,
                "train_rows": int(len(train)),
                "score_rows": int(len(score)),
                "epochs": int(epochs),
                "batch_size": batch_size,
                "mixer_blocks": int(config["mixer_blocks"]),
                "hidden_time": int(config["hidden_time"]),
                "hidden_feature": int(config["hidden_feature"]),
                "head_hidden": int(config["head_hidden"]),
                "dropout": float(config["dropout"]),
                "learning_rate": float(config["learning_rate"]),
                "weight_decay": float(config["weight_decay"]),
                "grad_clip_norm": float(config["grad_clip_norm"]),
                "parameter_count": int(sum(p.numel() for p in model.parameters())),
                "final_training_loss": final_loss,
                "training_inference_seconds": round(time.perf_counter() - fit_started, 6),
                "device": str(device),
                "lockbox_rows_used_for_tuning": 0,
            })
            del x_train, y_train, model
            if device.type == "cuda":
                torch.cuda.empty_cache()
    predictions = pd.concat(prediction_frames, ignore_index=True) if prediction_frames else pd.DataFrame()
    if save_predictions and seed_mean_model_id is not None and not predictions.empty:
        seed_mean = _seed_mean_predictions(predictions, seed_mean_model_id)
        predictions = pd.concat([predictions, seed_mean], ignore_index=True, sort=False)
        seed_mean_metrics = _compute_metrics(seed_mean)
        metric_rows.extend(seed_mean_metrics.to_dict("records"))
    return predictions, pd.DataFrame.from_records(metric_rows), pd.DataFrame.from_records(fit_rows)


def _predict_model(model: Any, values: np.ndarray, mask: np.ndarray, indices: np.ndarray, means: np.ndarray, stds: np.ndarray, batch_size: int, device: Any) -> np.ndarray:
    import torch

    model.eval()
    outputs: list[np.ndarray] = []
    with torch.inference_mode():
        for start in range(0, len(indices), batch_size):
            batch_indices = indices[start : start + batch_size]
            x_np = _apply_sequence_normalization(values, mask, batch_indices, means, stds)
            x = torch.tensor(x_np, dtype=torch.float32, device=device)
            outputs.append(model(x).detach().cpu().numpy().reshape(-1))
    return np.concatenate(outputs).astype("float32")


def _prediction_frame(split: pd.DataFrame, model_id: str, seed_id: str, seed: int, prediction: np.ndarray) -> pd.DataFrame:
    output = split[["row_key", *ROW_KEY, "fold_id", "split_role", "dataset_version", "split_artifact_version", "target"]].copy()
    output["model_id"] = model_id
    output["seed_id"] = seed_id
    output["seed"] = int(seed)
    output["model_family"] = "tsmixer_pytorch"
    output["branch"] = "updated_market_event_sequence"
    output["prediction"] = prediction.astype("float64")
    return output


def _seed_mean_predictions(predictions: pd.DataFrame, model_id: str) -> pd.DataFrame:
    meta_columns = ["row_key", *ROW_KEY, "fold_id", "split_role", "dataset_version", "split_artifact_version", "target"]
    grouped = predictions.groupby(meta_columns, sort=False, observed=True)["prediction"].mean().reset_index()
    grouped["model_id"] = model_id
    grouped["seed_id"] = "seed_mean"
    grouped["seed"] = -1
    grouped["model_family"] = "tsmixer_pytorch_seed_mean"
    grouped["branch"] = "updated_market_event_sequence"
    return grouped[[*meta_columns, "model_id", "seed_id", "seed", "model_family", "branch", "prediction"]]


def _compute_metrics(predictions: pd.DataFrame) -> pd.DataFrame:
    working = predictions.copy()
    working["error"] = working["prediction"].astype("float64") - working["target"].astype("float64")
    working["squared_error"] = working["error"] ** 2
    working["absolute_error"] = working["error"].abs()
    rows: list[dict[str, Any]] = []
    for keys, group in working.groupby(["split_role", "fold_id", "horizon_id", "model_id"], sort=True, observed=True):
        split_role, fold_id, horizon_id, model_id = keys
        target = group["target"].astype("float64")
        denominator = float(np.sum(target**2))
        sse = float(group["squared_error"].sum())
        rows.append({"trial_number": -1, "seed_id": "seed_mean", "seed": -1, "split_role": split_role, "fold_id": fold_id, "horizon_id": horizon_id, "model_id": model_id, "row_count": int(len(group)), "rmse": float(np.sqrt(group["squared_error"].mean())), "mae": float(group["absolute_error"].mean()), "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator), "lockbox_rows_used_for_optimization": 0})
    return pd.DataFrame.from_records(rows)


def _summarize_tsmixer_trial(trial_number: int, metrics: pd.DataFrame, config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    validation_weighted = _weighted_error(metrics, "validation")
    train_weighted = _weighted_error(metrics, "train")
    validation_rate_vs_zero = _positive_r2_rate(metrics, "validation")
    train_rate_vs_zero = _positive_r2_rate(metrics, "train")
    gaps = _train_gaps(metrics)
    gap_rate = float(gaps["gap_flag"].mean()) if not gaps.empty else 0.0
    gap_penalty = max(0.0, gap_rate - 0.50) * 0.001
    overfit_penalty = max(0.0, validation_weighted - train_weighted) * 0.0001 if np.isfinite(train_weighted) else 0.0
    objective_value = validation_weighted + gap_penalty + overfit_penalty
    summary = {
        "objective_value": float(objective_value),
        "validation_weighted_error": float(validation_weighted),
        "train_weighted_error": float(train_weighted),
        "validation_positive_r2_rate": validation_rate_vs_zero,
        "train_positive_r2_rate": train_rate_vs_zero,
        "train_validation_gap_flag_rate": gap_rate,
        "gap_penalty": float(gap_penalty),
        "overfit_penalty": float(overfit_penalty),
        "lockbox_rows_used_for_tuning": 0,
    }
    frontier = {"trial_number": int(trial_number), "status": "completed", "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, **config, **summary}
    return summary, frontier


def _weighted_error(metrics: pd.DataFrame, split_role: str) -> float:
    split = metrics[metrics["split_role"] == split_role].copy()
    if split.empty:
        return float("inf")
    split["horizon_weight"] = split["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    split["weighted_error"] = split["horizon_weight"] * (0.5 * split["rmse"].astype("float64") + 0.5 * split["mae"].astype("float64"))
    by_model_horizon = split.groupby(["model_id", "horizon_id"], sort=True)["weighted_error"].mean().reset_index()
    by_model = by_model_horizon.groupby("model_id", sort=True)["weighted_error"].sum()
    return float(by_model.mean())


def _positive_r2_rate(metrics: pd.DataFrame, split_role: str) -> float:
    split = metrics[metrics["split_role"] == split_role]
    if split.empty:
        return 0.0
    return float((split["r2_oos_zero_baseline"].astype("float64") > 0.0).mean())


def _seed_summary(metrics: pd.DataFrame, seed_mean_model_id: str) -> pd.DataFrame:
    rows = []
    for model_id in sorted(metrics["model_id"].unique()):
        for split_role in ["train", "validation", "lockbox"]:
            rows.append({"model_id": model_id, "split_role": split_role, "weighted_error": _weighted_error(metrics[metrics["model_id"] == model_id], split_role), "positive_r2_rate": _positive_r2_rate(metrics[metrics["model_id"] == model_id], split_role), "seed_mean_model_id": seed_mean_model_id})
    return pd.DataFrame.from_records(rows)


def _metric_summary(metrics: pd.DataFrame, model_id: str) -> list[dict[str, Any]]:
    rows = []
    for split_role in ["train", "validation", "lockbox"]:
        split = metrics[(metrics["model_id"] == model_id) & (metrics["split_role"] == split_role)]
        rows.append({"model_id": model_id, "split_role": split_role, "metric_rows": int(len(split)), "weighted_error": _weighted_error(metrics[metrics["model_id"] == model_id], split_role), "rmse_mean": float(split["rmse"].mean()) if not split.empty else None, "mae_mean": float(split["mae"].mean()) if not split.empty else None, "r2_oos_zero_baseline_mean": float(split["r2_oos_zero_baseline"].mean()) if not split.empty else None})
    return rows


def _standalone_metric_summary(metrics: pd.DataFrame, model_id: str) -> dict[str, Any]:
    return {"model_id": model_id, "metric_summary": _metric_summary(metrics, model_id), "selection_metric": "validation_weighted_error_lower_is_better", "lockbox_used_for_selection": False}


def _build_comparison_summary(best_metrics: pd.DataFrame, previous_xgboost_root: Path, updated_xgboost_root: Path) -> dict[str, Any]:
    baselines: list[tuple[str, pd.DataFrame]] = []
    previous_metrics_path = previous_xgboost_root / "metrics.parquet"
    if previous_metrics_path.exists():
        previous_metrics = pd.read_parquet(previous_metrics_path)
        previous_metrics = previous_metrics[previous_metrics["model_id"] == PREVIOUS_XGBOOST_MODEL_ID][["split_role", "fold_id", "horizon_id", "model_id", "row_count", "rmse", "mae", "r2_oos_zero_baseline"]].copy()
        baselines.append((PREVIOUS_XGBOOST_MODEL_ID, previous_metrics))
    updated_metrics_path = updated_xgboost_root / "best_model_metrics.parquet"
    if updated_metrics_path.exists():
        updated_metrics = pd.read_parquet(updated_metrics_path)
        updated_metrics = updated_metrics[updated_metrics["model_id"] == UPDATED_XGBOOST_MODEL_ID][["split_role", "fold_id", "horizon_id", "model_id", "row_count", "rmse", "mae", "r2_oos_zero_baseline"]].copy()
        baselines.append((UPDATED_XGBOOST_MODEL_ID, updated_metrics))
    summaries = []
    candidate = best_metrics[best_metrics["model_id"] == FINAL_MODEL_ID][["split_role", "fold_id", "horizon_id", "model_id", "row_count", "rmse", "mae", "r2_oos_zero_baseline"]].copy()
    for baseline_id, baseline_metrics in baselines:
        deltas = compute_pairwise_deltas(pd.concat([candidate, baseline_metrics], ignore_index=True, sort=False), baseline_id, [FINAL_MODEL_ID])
        summaries.append({"baseline_model_id": baseline_id, "candidate_model_id": FINAL_MODEL_ID, "split_summaries": _split_delta_summary(deltas), "metric_summary": _comparison_metric_summary(candidate, baseline_metrics, baseline_id)})
    return {"artifact_type": "updated_dataset_tsmixer_comparison_summary", "generated_at_utc": GENERATED_AT_UTC, "candidate_model_id": FINAL_MODEL_ID, "comparisons": summaries, "lockbox_used_for_tuning": False, "benchmark_claim": False, "positive_claim_approved": False}


def _split_delta_summary(deltas: pd.DataFrame) -> dict[str, Any]:
    summary = {}
    for split_role in ["validation", "lockbox"]:
        split = deltas[deltas["split_role"] == split_role].copy()
        summary[split_role] = {"comparison_rows": int(len(split)), "weighted_delta_candidate_minus_baseline": _weighted_delta(split), "both_metric_improvement_rate": float(split["both_metrics_improve"].mean()) if not split.empty else 0.0, "rmse_delta_mean": float(split["rmse_delta_candidate_minus_baseline"].mean()) if not split.empty else None, "mae_delta_mean": float(split["mae_delta_candidate_minus_baseline"].mean()) if not split.empty else None}
    return summary


def _weighted_delta(deltas: pd.DataFrame) -> float | None:
    if deltas.empty:
        return None
    working = deltas.copy()
    working["horizon_weight"] = working["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    working["weighted_delta"] = working["horizon_weight"] * (0.5 * working["rmse_delta_candidate_minus_baseline"] + 0.5 * working["mae_delta_candidate_minus_baseline"])
    return float(working.groupby("horizon_id", sort=True)["weighted_delta"].mean().sum())


def _comparison_metric_summary(candidate: pd.DataFrame, baseline: pd.DataFrame, baseline_id: str) -> list[dict[str, Any]]:
    rows = []
    for split_role in ["validation", "lockbox"]:
        for model_id, source in [(FINAL_MODEL_ID, candidate), (baseline_id, baseline)]:
            split = source[(source["split_role"] == split_role) & (source["model_id"] == model_id)]
            rows.append({"split_role": split_role, "model_id": model_id, "metric_rows": int(len(split)), "rmse_mean": float(split["rmse"].mean()) if not split.empty else None, "mae_mean": float(split["mae"].mean()) if not split.empty else None, "r2_oos_zero_baseline_mean": float(split["r2_oos_zero_baseline"].mean()) if not split.empty else None})
    return rows


def _render_comparison_markdown(summary: dict[str, Any]) -> str:
    lines = ["# Updated Dataset TSMixer Comparison Summary", "", f"Candidate model: `{summary['candidate_model_id']}`", "", "Lockbox was not used for tuning or selection."]
    for comparison in summary["comparisons"]:
        lines.extend(["", f"## Versus `{comparison['baseline_model_id']}`"])
        for split_role in ["validation", "lockbox"]:
            split = comparison["split_summaries"][split_role]
            lines.extend(["", f"{split_role.title()} weighted delta candidate minus baseline: {split['weighted_delta_candidate_minus_baseline']}", f"{split_role.title()} both-metric improvement rate: {split['both_metric_improvement_rate']}"])
    lines.extend(["", "Non-claims: this is not positive benchmark language, Stage 6 reinterpretation, or trading output.", ""])
    return "\n".join(lines)


def _render_report(manifest: dict[str, Any]) -> str:
    best = manifest["best_development_trial"]
    metric_rows = manifest["standalone_metric_summary"]["metric_summary"]
    validation = next((row for row in metric_rows if row["split_role"] == "validation"), {})
    lockbox = next((row for row in metric_rows if row["split_role"] == "lockbox"), {})
    return f"""# Stage 44 Updated Dataset TSMixer Training

Status: {manifest['status']}

Trials requested: {manifest['trial_count_requested']}

Trials completed: {manifest['trial_count_completed']}

Trials failed: {manifest['trial_count_failed']}

Best development trial: `{best.get('trial_number')}`

Best development objective: {best.get('objective_value')}

Validation weighted error: {validation.get('weighted_error')}

Validation RMSE/MAE: {validation.get('rmse_mean')} / {validation.get('mae_mean')}

Lockbox weighted error: {lockbox.get('weighted_error')}

Lockbox RMSE/MAE: {lockbox.get('rmse_mean')} / {lockbox.get('mae_mean')}

Lockbox rows used for tuning: {manifest['lockbox_rows_used_for_tuning']}

Non-claims: complete TSMixer training evidence is recorded without positive benchmark approval, Stage 6 reinterpretation, or trading output.
"""


def _completed_trial_ids(ledger_path: Path) -> set[int]:
    if not ledger_path.exists():
        return set()
    return {int(row["trial_number"]) for row in _iter_jsonl(ledger_path) if row.get("status") in {"completed", "failed"}}


def _successful_trial_count(ledger_path: Path) -> int:
    if not ledger_path.exists():
        return 0
    return sum(1 for row in _iter_jsonl(ledger_path) if row.get("status") == "completed")


def _read_trial_record(ledger_path: Path, trial_number: int) -> dict[str, Any] | None:
    if not ledger_path.exists():
        return None
    for row in _iter_jsonl(ledger_path):
        if int(row.get("trial_number", -1)) == int(trial_number):
            return row
    return None


def _read_jsonl_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.DataFrame.from_records(list(_iter_jsonl(path)))


def _iter_jsonl(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_json_safe(payload), sort_keys=True) + "\n")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if value is None:
        return None
    try:
        if not isinstance(value, (str, bytes)) and pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    main()
