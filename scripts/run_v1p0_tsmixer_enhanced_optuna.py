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


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    HORIZON_WEIGHTS,
    PROJECT_ROOT as FINAL_PROJECT_ROOT,
    ROW_KEY,
    STAGE23_ROOT,
    TSMIXER_ARCHITECTURE_VERSION,
    TSMIXER_INVALIDATED_READOUT_POLICY,
    TSMIXER_READOUT_POLICY,
    StageOutput,
    _apply_sequence_normalization,
    _load_sequence_training_frame,
    _normalization_stats,
    _stage32_metric_row,
    _train_gaps,
    compute_pairwise_deltas,
    sha256_file,
    stable_digest,
)


RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
GENERATED_TOKEN = "20260528T040000Z"
GENERATED_AT_UTC = "2026-05-28T04:00:00Z"
SOURCE_ID = "6dff1bd"
DEFAULT_STAGE18_MANIFEST = "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage18__sequence_windows__20260525T145000Z__src_6dff1bd__run_052914ca/sequence_window_manifest.json"
BASELINE_MODEL_ID = "market_xgboost_v2_frozen_final"
CANDIDATE_MODEL_ID_PREFIX = "market_tsmixer_v2_enhanced_optuna_800"
DEFAULT_TRIAL_COUNT = 800
DEFAULT_SEEDS = (2026053201, 2026053202)
DEFAULT_EPOCHS = 10


def enhanced_tsmixer_search_contract(
    trial_count: int = DEFAULT_TRIAL_COUNT,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    epochs: int = DEFAULT_EPOCHS,
) -> dict[str, Any]:
    return {
        "artifact_type": "v1p0_enhanced_tsmixer_optuna_search_contract",
        "generated_at_utc": GENERATED_AT_UTC,
        "candidate_model_id_prefix": CANDIDATE_MODEL_ID_PREFIX,
        "baseline_model_id": BASELINE_MODEL_ID,
        "trial_count": int(trial_count),
        "minimum_required_trials": 800,
        "seeds": list(seeds),
        "seed_count": len(seeds),
        "epochs": int(epochs),
        "architecture": {
            "version": TSMIXER_ARCHITECTURE_VERSION,
            "readout_policy": TSMIXER_READOUT_POLICY,
            "invalidates_prior_readout_policy": TSMIXER_INVALIDATED_READOUT_POLICY,
        },
        "optuna": {
            "direction": "minimize",
            "sampler": "TPESampler",
            "sampler_seed": 2026052802,
            "n_startup_trials": 80,
            "multivariate": True,
        },
        "split_roles_for_optimization": ["train", "validation"],
        "lockbox_rows_used_for_optimization": 0,
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
        "objective": {
            "name": "development_validation_weighted_delta_vs_market_xgb_with_overfit_penalty",
            "metric_direction": "candidate_minus_baseline_lower_is_better",
            "horizon_weights": HORIZON_WEIGHTS,
            "lockbox_policy": "no_lockbox_rows_or_metrics_used_for_trial_selection",
        },
        "freeze_gate": {
            "validation_weighted_delta_vs_market_xgb_must_be_negative": True,
            "validation_both_metric_improvement_rate_min": 0.45,
            "train_validation_gap_flag_rate_max": 0.50,
            "positive_claim_approved": False,
        },
        "non_claims": [
            "development_only_enhanced_search",
            "not_lockbox_selection",
            "not_positive_tsmixer_claim",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }


def _parse_seeds(value: str) -> tuple[int, ...]:
    seeds = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return seeds


def _load_stage_output(stage: int, manifest_rel_path: str) -> StageOutput:
    manifest_path = FINAL_PROJECT_ROOT / manifest_rel_path
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    return StageOutput(stage, str(payload.get("status", "completed")), manifest_path.parent, manifest_path, {"manifest": manifest_rel_path})


def main() -> None:
    parser = argparse.ArgumentParser(description="Run enhanced 800+ trial v1p0 TSMixer Optuna search.")
    parser.add_argument("--stage18-manifest", default=DEFAULT_STAGE18_MANIFEST)
    parser.add_argument("--trial-count", type=int, default=DEFAULT_TRIAL_COUNT)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--seeds", type=_parse_seeds, default=DEFAULT_SEEDS)
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()
    if args.trial_count < 800:
        raise RuntimeError("enhanced TSMixer search requires at least 800 trials")

    stage18 = _load_stage_output(18, args.stage18_manifest)
    contract = enhanced_tsmixer_search_contract(args.trial_count, args.seeds, args.epochs)
    contract["source_stage18_artifact"] = stage18.summary["manifest"]
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_v1p0__stage42__tsmixer_enhanced_optuna__{GENERATED_TOKEN}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root or RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    search_space_path = output_root / "search_space_manifest.json"
    ledger_jsonl_path = output_root / "trial_ledger.ndjson"
    fold_metrics_jsonl_path = output_root / "fold_metrics.ndjson"
    fit_jsonl_path = output_root / "model_fit_manifest.ndjson"
    deltas_jsonl_path = output_root / "market_hurdle_deltas.ndjson"
    frontier_jsonl_path = output_root / "overfit_frontier.ndjson"
    storage_path = output_root / "optuna_study.sqlite3"
    _write_json(search_space_path, contract)
    _raise_if_existing_tuning_uses_stale_architecture(ledger_jsonl_path)

    stage18_cache = _Stage18WindowCache(stage18)
    baseline_metrics = pd.read_parquet(STAGE23_ROOT / "metrics.parquet")
    baseline_metrics = baseline_metrics[baseline_metrics["split_role"].isin(contract["split_roles_for_optimization"])].copy()
    completed_trial_ids = _completed_trial_ids(ledger_jsonl_path)

    sampler = optuna.samplers.TPESampler(
        seed=int(contract["optuna"]["sampler_seed"]),
        n_startup_trials=int(contract["optuna"]["n_startup_trials"]),
        multivariate=bool(contract["optuna"]["multivariate"]),
    )
    study = optuna.create_study(
        study_name="v1p0_tsmixer_enhanced_800",
        direction="minimize",
        sampler=sampler,
        storage=f"sqlite:///{storage_path}",
        load_if_exists=True,
    )
    started = time.perf_counter()

    def objective(trial: optuna.Trial) -> float:
        trial_number = int(trial.number)
        if trial_number in completed_trial_ids:
            prior = _read_trial_record(ledger_jsonl_path, trial_number)
            if prior and prior.get("status") == "completed":
                return float(prior["objective_value"])
        config = _suggest_tsmixer_config(trial, contract)
        record = _execute_trial(trial_number, config, contract, stage18_cache, baseline_metrics)
        _append_jsonl(ledger_jsonl_path, record["ledger"])
        completed_trial_ids.add(trial_number)
        for row in record["metrics"]:
            _append_jsonl(fold_metrics_jsonl_path, row)
        for row in record["fit_manifest"]:
            _append_jsonl(fit_jsonl_path, row)
        for row in record["deltas"]:
            _append_jsonl(deltas_jsonl_path, row)
        _append_jsonl(frontier_jsonl_path, record["frontier"])
        print(json.dumps({"model_family": "tsmixer", "trial_number": trial_number, "status": record["ledger"]["status"], "objective_value": record["ledger"].get("objective_value")}, sort_keys=True), flush=True)
        return float(record["ledger"].get("objective_value", 1e9) or 1e9)

    remaining = max(0, int(args.trial_count) - len(completed_trial_ids))
    if remaining:
        study.optimize(objective, n_trials=remaining, show_progress_bar=False)

    trial_ledger = _read_jsonl_frame(ledger_jsonl_path)
    fold_metrics = _read_jsonl_frame(fold_metrics_jsonl_path)
    fit_manifest = _read_jsonl_frame(fit_jsonl_path)
    deltas = _read_jsonl_frame(deltas_jsonl_path)
    frontier = _read_jsonl_frame(frontier_jsonl_path)
    best_candidate = _select_best_candidate(frontier, contract)
    if study.trials:
        best_candidate["optuna_best_trial_number"] = int(study.best_trial.number)
        best_candidate["optuna_best_value"] = float(study.best_value)

    trial_ledger_path = output_root / "trial_ledger.parquet"
    fold_metrics_path = output_root / "fold_metrics.parquet"
    fit_manifest_path = output_root / "model_fit_manifest.parquet"
    deltas_path = output_root / "market_hurdle_deltas.parquet"
    frontier_path = output_root / "overfit_frontier.parquet"
    best_candidate_path = output_root / "best_candidate_manifest.json"
    manifest_path = output_root / "tsmixer_enhanced_optuna_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"
    report_path = output_root / "stage42_tsmixer_enhanced_optuna_report.md"

    trial_ledger.to_parquet(trial_ledger_path, index=False)
    fold_metrics.to_parquet(fold_metrics_path, index=False)
    fit_manifest.to_parquet(fit_manifest_path, index=False)
    deltas.to_parquet(deltas_path, index=False)
    frontier.to_parquet(frontier_path, index=False)
    _write_json(best_candidate_path, best_candidate)

    manifest = {
        "artifact_type": "v1p0_stage42_tsmixer_enhanced_optuna_manifest",
        "artifact_id": f"stage42_tsmixer_enhanced_optuna__{sha256_file(trial_ledger_path)[:12]}__{GENERATED_TOKEN}",
        "generated_at_utc": GENERATED_AT_UTC,
        "run_id": run_id,
        "status": "completed" if int((trial_ledger["status"] == "completed").sum()) >= int(args.trial_count) else "partial",
        "candidate_model_id_prefix": CANDIDATE_MODEL_ID_PREFIX,
        "baseline_model_id": BASELINE_MODEL_ID,
        "source_stage18_artifact": stage18.summary["manifest"],
        "architecture": contract["architecture"],
        "trial_count_requested": int(args.trial_count),
        "trial_count_completed": int((trial_ledger["status"] == "completed").sum()),
        "trial_count_failed": int((trial_ledger["status"] == "failed").sum()),
        "seed_count": len(args.seeds),
        "epochs": int(args.epochs),
        "lockbox_rows_used_for_optimization": 0,
        "best_candidate": best_candidate,
        "outputs": {
            "search_space_manifest": _rel(search_space_path),
            "trial_ledger_ndjson": _rel(ledger_jsonl_path),
            "trial_ledger": _rel(trial_ledger_path),
            "fold_metrics_ndjson": _rel(fold_metrics_jsonl_path),
            "fold_metrics": _rel(fold_metrics_path),
            "model_fit_manifest_ndjson": _rel(fit_jsonl_path),
            "model_fit_manifest": _rel(fit_manifest_path),
            "market_hurdle_deltas_ndjson": _rel(deltas_jsonl_path),
            "market_hurdle_deltas": _rel(deltas_path),
            "overfit_frontier_ndjson": _rel(frontier_jsonl_path),
            "overfit_frontier": _rel(frontier_path),
            "best_candidate_manifest": _rel(best_candidate_path),
            "optuna_storage": _rel(storage_path),
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
    _write_json(run_manifest_path, {"stage": 42, "stage_name": "tsmixer_enhanced_optuna", "status": manifest["status"], "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False})
    report_path.write_text(_render_report(manifest, best_candidate), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "trial_count_completed": manifest["trial_count_completed"], "best_candidate": best_candidate, "manifest": manifest["outputs"]["manifest"]}, sort_keys=True))


class _Stage18WindowCache:
    def __init__(self, stage18: StageOutput) -> None:
        self.stage18 = stage18
        self._cache: dict[int, tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str]]] = {}

    def get(self, window_length: int) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, list[str]]:
        if int(window_length) not in self._cache:
            frame, values, mask, feature_columns = _load_sequence_training_frame(self.stage18, int(window_length))
            frame = frame[frame["split_role"].isin(["train", "validation"])].copy()
            if frame["split_role"].eq("lockbox").any():
                raise RuntimeError("enhanced TSMixer optimization frame contains lockbox rows")
            self._cache[int(window_length)] = (frame, values, mask, feature_columns)
        return self._cache[int(window_length)]


class _EnhancedTSMixer:
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


def _suggest_tsmixer_config(trial: optuna.Trial, contract: dict[str, Any]) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for name, spec in contract["search_space"].items():
        if spec["type"] == "categorical":
            config[name] = trial.suggest_categorical(name, list(spec["choices"]))
        elif spec["type"] == "log_float":
            config[name] = trial.suggest_float(name, float(spec["low"]), float(spec["high"]), log=True)
        else:
            raise RuntimeError(f"unsupported search-space type for {name}: {spec['type']}")
    config["window_length"] = int(config["window_length"])
    config["mixer_blocks"] = int(config["mixer_blocks"])
    config["hidden_time"] = int(config["hidden_time"])
    config["hidden_feature"] = int(config["hidden_feature"])
    config["head_hidden"] = int(config["head_hidden"])
    config["batch_size"] = int(config["batch_size"])
    config["dropout"] = float(config["dropout"])
    config["grad_clip_norm"] = float(config["grad_clip_norm"])
    return config


def _execute_trial(trial_number: int, config: dict[str, Any], contract: dict[str, Any], cache: _Stage18WindowCache, baseline_metrics: pd.DataFrame) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        metrics, fit_manifest = _fit_trial_metrics(trial_number, config, contract, cache)
        summary, deltas, frontier = _summarize_trial(trial_number, metrics, baseline_metrics, config)
        ledger = {"trial_number": int(trial_number), "status": "completed", "runtime_seconds": round(time.perf_counter() - started, 6), "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, **config, **summary}
        return {"ledger": ledger, "metrics": metrics.to_dict("records"), "fit_manifest": fit_manifest.to_dict("records"), "deltas": deltas.to_dict("records"), "frontier": frontier}
    except Exception as exc:  # noqa: BLE001 - failed trials are evidence and must be logged.
        ledger = {"trial_number": int(trial_number), "status": "failed", "runtime_seconds": round(time.perf_counter() - started, 6), "failure_reason": repr(exc), "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, **config, "objective_value": 1e9, "lockbox_rows_used_for_optimization": 0}
        return {"ledger": ledger, "metrics": [], "fit_manifest": [], "deltas": [], "frontier": ledger}


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
        raise RuntimeError("existing enhanced TSMixer ledger predates the corrected readout; use a fresh output root before rerunning")
    stale = completed[(completed["architecture_version"] != TSMIXER_ARCHITECTURE_VERSION) | (completed["readout_policy"] != TSMIXER_READOUT_POLICY)]
    if not stale.empty:
        raise RuntimeError("existing enhanced TSMixer ledger uses stale architecture; use a fresh output root before rerunning")


def _fit_trial_metrics(trial_number: int, config: dict[str, Any], contract: dict[str, Any], cache: _Stage18WindowCache) -> tuple[pd.DataFrame, pd.DataFrame]:
    import torch

    frame, values, mask, feature_columns = cache.get(int(config["window_length"]))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    metric_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    batch_size = int(config["batch_size"])
    epochs = int(contract["epochs"])
    for seed_position, seed in enumerate(tuple(contract["seeds"]), start=1):
        torch.manual_seed(int(seed) + int(trial_number))
        np_rng = np.random.default_rng(int(seed) + int(trial_number) * 1009)
        seed_id = f"seed_{seed_position:02d}"
        model_id = f"{CANDIDATE_MODEL_ID_PREFIX}_trial_{trial_number:04d}_{seed_id}"
        for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
            train = group[group["split_role"] == "train"].copy()
            validation = group[group["split_role"] == "validation"].copy()
            if train.empty or validation.empty:
                continue
            fit_started = time.perf_counter()
            train_indices = train["sequence_base_index"].to_numpy(dtype="int64")
            validation_indices = validation["sequence_base_index"].to_numpy(dtype="int64")
            means, stds = _normalization_stats(values, mask, train_indices)
            x_train_np = _apply_sequence_normalization(values, mask, train_indices, means, stds)
            y_train_np = train["target"].to_numpy(dtype="float32").reshape(-1, 1)
            x_train = torch.tensor(x_train_np, dtype=torch.float32, device=device)
            y_train = torch.tensor(y_train_np, dtype=torch.float32, device=device)
            model = _EnhancedTSMixer(window_length=int(config["window_length"]), feature_count=len(feature_columns), config=config).to(device)
            opt = torch.optim.AdamW(model.parameters(), lr=float(config["learning_rate"]), weight_decay=float(config["weight_decay"]))
            loss_fn = torch.nn.MSELoss()
            final_loss = float("nan")
            model.train()
            for _ in range(epochs):
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
            train_prediction = _predict_model(model, values, mask, train_indices, means, stds, batch_size, device)
            validation_prediction = _predict_model(model, values, mask, validation_indices, means, stds, batch_size, device)
            metric_rows.append(_stage32_metric_row(trial_number, seed_id, int(seed), model_id, fold_id, horizon_id, "train", train["target"].to_numpy(dtype="float64"), train_prediction))
            metric_rows.append(_stage32_metric_row(trial_number, seed_id, int(seed), model_id, fold_id, horizon_id, "validation", validation["target"].to_numpy(dtype="float64"), validation_prediction))
            fit_rows.append({
                "trial_number": int(trial_number),
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
                "validation_rows": int(len(validation)),
                "lockbox_rows_used_for_optimization": 0,
                "epochs": epochs,
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
                "training_validation_seconds": round(time.perf_counter() - fit_started, 6),
                "device": str(device),
            })
            del x_train, y_train, model
            if device.type == "cuda":
                torch.cuda.empty_cache()
    return pd.DataFrame.from_records(metric_rows), pd.DataFrame.from_records(fit_rows)


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


def _summarize_trial(trial_number: int, metrics: pd.DataFrame, baseline_metrics: pd.DataFrame, config: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    candidate_model_ids = sorted(metrics["model_id"].unique())
    deltas = compute_pairwise_deltas(pd.concat([metrics, baseline_metrics], ignore_index=True, sort=False), BASELINE_MODEL_ID, candidate_model_ids)
    deltas["trial_number"] = int(trial_number)
    deltas["horizon_weight"] = deltas["horizon_id"].map(HORIZON_WEIGHTS).fillna(0.0)
    deltas["weighted_delta"] = 0.5 * deltas["rmse_delta_candidate_minus_baseline"] * deltas["horizon_weight"] + 0.5 * deltas["mae_delta_candidate_minus_baseline"] * deltas["horizon_weight"]

    validation = deltas[deltas["split_role"] == "validation"].copy()
    train = deltas[deltas["split_role"] == "train"].copy()
    validation_weighted = float(validation.groupby("candidate_model_id")["weighted_delta"].sum().mean()) if not validation.empty else float("inf")
    train_weighted = float(train.groupby("candidate_model_id")["weighted_delta"].sum().mean()) if not train.empty else float("nan")
    validation_rate = float(validation["both_metrics_improve"].mean()) if not validation.empty else 0.0
    train_rate = float(train["both_metrics_improve"].mean()) if not train.empty else 0.0
    gaps = _train_gaps(metrics)
    gap_rate = float(gaps["gap_flag"].mean()) if not gaps.empty else 0.0
    train_good_validation_bad = bool(train_weighted < 0.0 and validation_weighted > 0.0)
    low_validation_support = bool(validation_rate < 0.45)
    high_gap_pressure = bool(gap_rate > 0.50)
    overfit_flag_count = int(train_good_validation_bad) + int(low_validation_support) + int(high_gap_pressure)
    objective_value = validation_weighted + max(0.0, gap_rate - 0.50) * 0.001 + max(0.0, validation_weighted - train_weighted) * 0.0001
    summary = {
        "objective_value": float(objective_value),
        "validation_weighted_delta_vs_market_xgb": validation_weighted,
        "train_weighted_delta_vs_market_xgb": train_weighted,
        "validation_both_metric_improvement_rate_vs_market_xgb": validation_rate,
        "train_both_metric_improvement_rate_vs_market_xgb": train_rate,
        "train_validation_gap_flag_rate": gap_rate,
        "train_good_validation_bad_flag": train_good_validation_bad,
        "low_validation_support_flag": low_validation_support,
        "high_gap_pressure_flag": high_gap_pressure,
        "overfit_flag_count": int(overfit_flag_count),
        "lockbox_rows_used_for_optimization": 0,
    }
    frontier = {"trial_number": int(trial_number), "status": "completed", "architecture_version": TSMIXER_ARCHITECTURE_VERSION, "readout_policy": TSMIXER_READOUT_POLICY, **config, **summary}
    return summary, deltas, frontier


def _select_best_candidate(frontier: pd.DataFrame, contract: dict[str, Any]) -> dict[str, Any]:
    completed = frontier[frontier.get("status") == "completed"].copy() if not frontier.empty else pd.DataFrame()
    if completed.empty:
        return {"status": "rejected_no_completed_trials", "positive_claim_approved": False, "benchmark_claim": False, "lockbox_rows_used_for_optimization": 0}
    best = completed.sort_values(["objective_value", "trial_number"]).iloc[0]
    gate = contract["freeze_gate"]
    clears_gate = bool(
        best["validation_weighted_delta_vs_market_xgb"] < 0.0
        and best["validation_both_metric_improvement_rate_vs_market_xgb"] >= float(gate["validation_both_metric_improvement_rate_min"])
        and best["train_validation_gap_flag_rate"] <= float(gate["train_validation_gap_flag_rate_max"])
    )
    return {
        "status": "enhanced_tuned_candidate_frozen_from_development_only" if clears_gate else "enhanced_tuned_candidate_rejected_from_development_only",
        "recommendation_for_followup": "freeze_enhanced_tsmixer_for_nonselective_lockbox_evaluation" if clears_gate else "reject_enhanced_tsmixer_keep_xgboost_only_active",
        "best_trial_number": int(best["trial_number"]),
        "best_objective_value": float(best["objective_value"]),
        "best_hyperparameters": {
            "window_length": int(best["window_length"]),
            "mixer_blocks": int(best["mixer_blocks"]),
            "hidden_time": int(best["hidden_time"]),
            "hidden_feature": int(best["hidden_feature"]),
            "head_hidden": int(best["head_hidden"]),
            "dropout": float(best["dropout"]),
            "learning_rate": float(best["learning_rate"]),
            "weight_decay": float(best["weight_decay"]),
            "batch_size": int(best["batch_size"]),
            "grad_clip_norm": float(best["grad_clip_norm"]),
        },
        "validation_weighted_delta_vs_market_xgb": float(best["validation_weighted_delta_vs_market_xgb"]),
        "validation_both_metric_improvement_rate_vs_market_xgb": float(best["validation_both_metric_improvement_rate_vs_market_xgb"]),
        "train_validation_gap_flag_rate": float(best["train_validation_gap_flag_rate"]),
        "overfit_flag_count": int(best["overfit_flag_count"]),
        "lockbox_used_for_selection": False,
        "lockbox_rows_used_for_optimization": 0,
        "positive_claim_approved": False,
        "benchmark_claim": False,
    }


def _render_report(manifest: dict[str, Any], best_candidate: dict[str, Any]) -> str:
    return f"""# Stage 42 TSMixer Enhanced Optuna Search

Status: {manifest['status']}; enhanced development-only TSMixer search evidence

Trials requested: {manifest['trial_count_requested']}

Trials completed: {manifest['trial_count_completed']}

Seeds per trial: {manifest['seed_count']}

Epochs per fit: {manifest['epochs']}

Best-trial status: `{best_candidate.get('status')}`

Best trial: `{best_candidate.get('best_trial_number')}`

Best objective value: {best_candidate.get('best_objective_value')}

Validation weighted delta vs frozen market XGBoost: {best_candidate.get('validation_weighted_delta_vs_market_xgb')}

Validation both-metric improvement rate vs frozen market XGBoost: {best_candidate.get('validation_both_metric_improvement_rate_vs_market_xgb')}

Lockbox rows used for optimization: {manifest['lockbox_rows_used_for_optimization']}

Non-claims: this enhanced Optuna run is not a positive TSMixer benchmark claim, not lockbox selection, not Stage 6 reinterpretation, and not a trading signal.
"""


def _completed_trial_ids(ledger_path: Path) -> set[int]:
    if not ledger_path.exists():
        return set()
    return {int(row["trial_number"]) for row in _iter_jsonl(ledger_path) if row.get("status") in {"completed", "failed"}}


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
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if not isinstance(value, (dict, list, tuple)) and pd.isna(value):
        return None
    return value


def _rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


if __name__ == "__main__":
    main()
