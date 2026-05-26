from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from event_state_forecasting.v1p0 import final_sprint as fs


OUTPUT_ROOT = PROJECT_ROOT / "data/v1p0_full_results/ad_hoc_diagnostics/xgb_tsmixer_stratified_diagnostic_20260525T170000Z"

ROW_KEY = fs.ROW_KEY
SCORING_ROLES = ["validation", "lockbox"]
K = 5

STAGE18_MANIFEST = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage18__sequence_windows__20260525T145000Z__src_6dff1bd__run_052914ca/sequence_window_manifest.json"
STAGE31_MANIFEST = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage31__tsmixer_fixed_multiseed_benchmark__20260525T153000Z__src_6dff1bd__run_9aa67b49/stage31_tsmixer_fixed_multiseed_benchmark_manifest.json"
STAGE32_MANIFEST = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage32__tsmixer_optimization_overfit_control__20260525T160000Z__src_6dff1bd__run_54e692cf/stage32_tsmixer_optimization_manifest.json"
STAGE32_BEST = PROJECT_ROOT / "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage32__tsmixer_optimization_overfit_control__20260525T160000Z__src_6dff1bd__run_54e692cf/best_candidate_manifest.json"


def attach_target_flags(frame: pd.DataFrame, labels: pd.DataFrame, flags: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    if "target" not in out.columns:
        out = out.merge(labels, on=ROW_KEY, how="inner", validate="many_to_one")
    out = out.merge(flags, on=ROW_KEY, how="left", validate="many_to_one")
    out["aligned_news_count"] = out["aligned_news_count"].fillna(0).astype("int64")
    out["no_news_flag"] = out["no_news_flag"].fillna(True).astype(bool)
    out["provider_truncation_risk_flag"] = out["provider_truncation_risk_flag"].fillna(False).astype(bool)
    out["as_of_date"] = pd.to_datetime(out["as_of_date"])
    return out[out["split_role"].isin(SCORING_ROLES)].copy()


def load_model_predictions(path: Path, model_id: str, model_label: str, labels: pd.DataFrame, flags: pd.DataFrame) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    frame = frame[frame["model_id"].eq(model_id)].copy()
    frame = attach_target_flags(frame, labels, flags)
    frame["source_model_id"] = frame["model_id"]
    frame["model_label"] = model_label
    return frame


def fit_tuned_tsmixer_best_trial_predictions(
    tuned_trial: int,
    tuned_config: dict[str, object],
    stage32_manifest: dict[str, object],
    labels: pd.DataFrame,
    flags: pd.DataFrame,
) -> pd.DataFrame:
    stage18 = fs.StageOutput(
        18,
        "completed",
        STAGE18_MANIFEST.parent,
        STAGE18_MANIFEST,
        {"manifest": str(STAGE18_MANIFEST.relative_to(PROJECT_ROOT))},
    )
    frame, values, mask, feature_columns = fs._load_sequence_training_frame(stage18, fs.TSMIXER_FIXED_WINDOW_LENGTH)
    frame = frame[frame["split_role"].isin(["train", *SCORING_ROLES])].copy()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    records: list[pd.DataFrame] = []
    fit_records: list[dict[str, object]] = []
    for seed_position, seed in enumerate(fs.TSMIXER_OPTUNA_SEEDS, start=1):
        torch.manual_seed(seed + tuned_trial)
        rng = np.random.default_rng(seed + tuned_trial * 1009)
        seed_id = f"seed_{seed_position:02d}"
        model_id = f"market_tsmixer_v1_optuna_trial_{tuned_trial:03d}_{seed_id}"

        for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
            train = group[group["split_role"].eq("train")].copy()
            score = group[group["split_role"].isin(SCORING_ROLES)].copy()
            if train.empty or score.empty:
                continue

            started = time.perf_counter()
            train_indices = train["sequence_base_index"].to_numpy(dtype="int64")
            score_indices = score["sequence_base_index"].to_numpy(dtype="int64")
            means, stds = fs._normalization_stats(values, mask, train_indices)
            x_train_np = fs._apply_sequence_normalization(values, mask, train_indices, means, stds)
            y_train_np = train["target"].to_numpy(dtype="float32").reshape(-1, 1)
            x_train = torch.tensor(x_train_np, dtype=torch.float32, device=device)
            y_train = torch.tensor(y_train_np, dtype=torch.float32, device=device)

            model = fs._CompactTSMixer(
                window_length=fs.TSMIXER_FIXED_WINDOW_LENGTH,
                feature_count=len(feature_columns),
                hidden_time=int(tuned_config["hidden_time"]),
                hidden_feature=int(tuned_config["hidden_feature"]),
            ).to(device)
            optimizer = torch.optim.AdamW(
                model.parameters(),
                lr=float(tuned_config["learning_rate"]),
                weight_decay=float(tuned_config["weight_decay"]),
            )
            loss_fn = torch.nn.MSELoss()
            final_loss = float("nan")
            batch_size = int(tuned_config["batch_size"])
            model.train()
            for _ in range(int(stage32_manifest["epochs"])):
                order = rng.permutation(len(train))
                for start in range(0, len(order), batch_size):
                    batch_order = torch.tensor(order[start : start + batch_size], dtype=torch.long, device=device)
                    optimizer.zero_grad(set_to_none=True)
                    pred = model(x_train.index_select(0, batch_order))
                    loss = loss_fn(pred, y_train.index_select(0, batch_order))
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), float(tuned_config["grad_clip_norm"]))
                    optimizer.step()
                    final_loss = float(loss.detach().cpu())

            prediction = fs._predict_tsmixer(model, values, mask, score_indices, means, stds, batch_size, device)
            output = score[["row_key", *ROW_KEY, "fold_id", "split_role", "dataset_version", "split_artifact_version", "target"]].copy()
            output["model_id"] = model_id
            output["seed_id"] = seed_id
            output["seed"] = int(seed)
            output["model_family"] = "tsmixer_pytorch"
            output["branch"] = "market_only"
            output["feature_representation_id"] = f"market_sequence_window_{fs.TSMIXER_FIXED_WINDOW_LENGTH}d_v1"
            output["feature_artifact_version"] = f"stage18_sequence_window_{fs.TSMIXER_FIXED_WINDOW_LENGTH}d"
            output["v1p0_artifact_version"] = "v1p0_stage32_best_trial_posthoc_seed_prediction"
            output["prediction"] = prediction
            records.append(output)
            fit_records.append(
                {
                    "trial_number": tuned_trial,
                    "model_id": model_id,
                    "seed_id": seed_id,
                    "seed": int(seed),
                    "fold_id": fold_id,
                    "horizon_id": horizon_id,
                    "train_rows": int(len(train)),
                    "score_rows": int(len(score)),
                    "epochs": int(stage32_manifest["epochs"]),
                    "batch_size": batch_size,
                    "hidden_time": int(tuned_config["hidden_time"]),
                    "hidden_feature": int(tuned_config["hidden_feature"]),
                    "learning_rate": float(tuned_config["learning_rate"]),
                    "weight_decay": float(tuned_config["weight_decay"]),
                    "grad_clip_norm": float(tuned_config["grad_clip_norm"]),
                    "final_training_loss": final_loss,
                    "seconds": round(time.perf_counter() - started, 6),
                    "device": str(device),
                    "lockbox_used_for_training_or_selection": False,
                }
            )
            del x_train, y_train, model
            if device.type == "cuda":
                torch.cuda.empty_cache()

    raw = pd.concat(records, ignore_index=True)
    raw.to_parquet(OUTPUT_ROOT / "tuned_tsmixer_best_trial_seed_predictions.parquet", index=False)
    pd.DataFrame.from_records(fit_records).to_parquet(OUTPUT_ROOT / "tuned_tsmixer_best_trial_fit_manifest.parquet", index=False)

    key = ["row_key", *ROW_KEY, "fold_id", "split_role", "dataset_version", "split_artifact_version"]
    mean_pred = raw.groupby(key, sort=True, observed=True).agg(target=("target", "first"), prediction=("prediction", "mean")).reset_index()
    mean_pred["model_id"] = f"market_tsmixer_v1_optuna_trial_{tuned_trial:03d}_seed_mean"
    mean_pred["source_model_id"] = mean_pred["model_id"]
    mean_pred["model_label"] = "tuned_tsmixer"
    mean_pred["model_family"] = "tsmixer_pytorch_seed_mean"
    mean_pred["branch"] = "market_only"
    return attach_target_flags(mean_pred, labels, flags)


def base_masks(df: pd.DataFrame, date_cutoff: pd.Timestamp) -> dict[str, pd.Series]:
    return {
        "all_rows": pd.Series(True, index=df.index),
        "no_news_rows": df["no_news_flag"].astype(bool),
        "news_rich_rows": ~df["no_news_flag"].astype(bool),
        "high_article_count_rows": df["aligned_news_count"].fillna(0).astype("int64") >= 3,
        "early_period_rows": df["as_of_date"] <= date_cutoff,
        "late_period_rows": df["as_of_date"] > date_cutoff,
        "true_negative_return_rows": df["target"] < 0,
    }


def error_rows_for(df: pd.DataFrame, stratum_name: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if df.empty:
        return rows
    work = df.copy()
    work["error"] = work["prediction"] - work["target"]
    work["squared_error"] = work["error"] ** 2
    work["absolute_error"] = work["error"].abs()
    work["negative_target"] = work["target"] < 0
    work["negative_prediction"] = work["prediction"] < 0
    for (horizon_id, model_label), group in work.groupby(["horizon_id", "model_label"], sort=True, observed=True):
        neg = group[group["negative_target"]]
        rows.append(
            {
                "score_scope": "validation_plus_lockbox",
                "horizon_id": horizon_id,
                "stratum": stratum_name,
                "model_label": model_label,
                "row_count": int(len(group)),
                "negative_target_count": int(len(neg)),
                "rmse": float(np.sqrt(group["squared_error"].mean())) if len(group) else np.nan,
                "mae": float(group["absolute_error"].mean()) if len(group) else np.nan,
                "sign_accuracy_on_negative_returns": float((neg["negative_prediction"]).mean()) if len(neg) else np.nan,
                "realized_mean_forward_excess_return": float(group["target"].mean()) if len(group) else np.nan,
            }
        )
    return rows


def select_bottom_top_rows(df: pd.DataFrame, k: int = K) -> tuple[pd.DataFrame, pd.DataFrame]:
    bottoms: list[pd.DataFrame] = []
    tops: list[pd.DataFrame] = []
    for _, group in df.groupby(["model_label", "split_role", "fold_id", "as_of_date", "horizon_id"], sort=True, observed=True):
        n = len(group)
        if n < 2:
            continue
        effective_k = min(k, n // 2)
        if effective_k < 1:
            continue
        ordered = group.sort_values(["prediction", "canonical_ticker"], ascending=[True, True])
        bottoms.append(ordered.head(effective_k))
        tops.append(ordered.tail(effective_k))
    bottom = pd.concat(bottoms, ignore_index=True) if bottoms else pd.DataFrame(columns=df.columns)
    top = pd.concat(tops, ignore_index=True) if tops else pd.DataFrame(columns=df.columns)
    return bottom, top


def rank_metrics_for(df: pd.DataFrame, stratum_name: str) -> list[dict[str, object]]:
    bottom, top = select_bottom_top_rows(df, K)
    if bottom.empty or top.empty:
        return []
    bottom_grouped = (
        bottom.groupby(["horizon_id", "model_label"], sort=True, observed=True)
        .agg(
            bottom_k_rows=("target", "size"),
            bottom_k_realized_mean_forward_excess_return=("target", "mean"),
            bottom_k_hit_rate_negative_return=("target", lambda s: float((s < 0).mean())),
        )
        .reset_index()
    )
    top_grouped = (
        top.groupby(["horizon_id", "model_label"], sort=True, observed=True)
        .agg(
            top_k_rows=("target", "size"),
            top_k_realized_mean_forward_excess_return=("target", "mean"),
        )
        .reset_index()
    )
    merged = bottom_grouped.merge(top_grouped, on=["horizon_id", "model_label"], how="inner", validate="one_to_one")
    merged["top_minus_bottom_spread"] = merged["top_k_realized_mean_forward_excess_return"] - merged["bottom_k_realized_mean_forward_excess_return"]
    merged["stratum"] = stratum_name
    merged["score_scope"] = "validation_plus_lockbox"
    return merged.to_dict("records")


def add_error_deltas(error_metrics: pd.DataFrame) -> pd.DataFrame:
    base = error_metrics[error_metrics["model_label"].eq("fixed_xgboost")][
        ["score_scope", "horizon_id", "stratum", "rmse", "mae"]
    ].rename(columns={"rmse": "fixed_xgboost_rmse", "mae": "fixed_xgboost_mae"})
    out = error_metrics.merge(base, on=["score_scope", "horizon_id", "stratum"], how="left", validate="many_to_one")
    out["rmse_delta_vs_fixed_xgboost"] = out["rmse"] - out["fixed_xgboost_rmse"]
    out["mae_delta_vs_fixed_xgboost"] = out["mae"] - out["fixed_xgboost_mae"]
    return out.sort_values(["horizon_id", "stratum", "model_label"]).reset_index(drop=True)


def add_rank_deltas(rank_metrics: pd.DataFrame) -> pd.DataFrame:
    base = rank_metrics[rank_metrics["model_label"].eq("fixed_xgboost")][
        [
            "score_scope",
            "horizon_id",
            "stratum",
            "bottom_k_realized_mean_forward_excess_return",
            "bottom_k_hit_rate_negative_return",
            "top_minus_bottom_spread",
        ]
    ].rename(
        columns={
            "bottom_k_realized_mean_forward_excess_return": "fixed_xgboost_bottom_k_mean",
            "bottom_k_hit_rate_negative_return": "fixed_xgboost_bottom_k_hit_rate",
            "top_minus_bottom_spread": "fixed_xgboost_top_minus_bottom_spread",
        }
    )
    out = rank_metrics.merge(base, on=["score_scope", "horizon_id", "stratum"], how="left", validate="many_to_one")
    out["bottom_k_mean_delta_vs_fixed_xgboost"] = out["bottom_k_realized_mean_forward_excess_return"] - out["fixed_xgboost_bottom_k_mean"]
    out["bottom_k_hit_rate_delta_vs_fixed_xgboost"] = out["bottom_k_hit_rate_negative_return"] - out["fixed_xgboost_bottom_k_hit_rate"]
    out["top_minus_bottom_spread_delta_vs_fixed_xgboost"] = out["top_minus_bottom_spread"] - out["fixed_xgboost_top_minus_bottom_spread"]
    return out.sort_values(["horizon_id", "stratum", "model_label"]).reset_index(drop=True)


def fmt_float(value: float) -> str:
    if pd.isna(value):
        return ""
    return f"{value:.6f}"


def write_report(
    manifest: dict[str, object],
    all_rows_report: pd.DataFrame,
    date_cutoff: pd.Timestamp,
) -> None:
    lines = [
        "# XGBoost vs TSMixer Stratified Diagnostic",
        "",
        "Status: completed ad-hoc diagnostic; `benchmark_claim=false`; `positive_claim_approved=false`.",
        "",
        f"Score scope: validation + lockbox only; train rows excluded. Early/late cutoff: `{date_cutoff.date()}`. Bottom/top K: `{K}`.",
        "",
        "RMSE/MAE deltas are candidate minus fixed XGBoost; lower is better.",
        "",
        "## All Rows Compact Report",
        "",
        "| Horizon | Model | Rows | RMSE delta | MAE delta | Neg sign acc | Bottom-k mean | Bottom-k neg hit | Top-bottom spread |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in all_rows_report.sort_values(["horizon_id", "model_label"]).iterrows():
        lines.append(
            f"| {row['horizon_id']} | {row['model_label']} | {int(row['row_count'])} | "
            f"{fmt_float(row['rmse_delta_vs_fixed_xgboost'])} | "
            f"{fmt_float(row['mae_delta_vs_fixed_xgboost'])} | "
            f"{fmt_float(row['sign_accuracy_on_negative_returns'])} | "
            f"{fmt_float(row['bottom_k_realized_mean_forward_excess_return'])} | "
            f"{fmt_float(row['bottom_k_hit_rate_negative_return'])} | "
            f"{fmt_float(row['top_minus_bottom_spread'])} |"
        )
    lines.extend(["", "## Outputs", ""])
    for key, value in manifest["outputs"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "Full horizon x stratum x model tables are in `stratified_error_metrics.csv` and `stratified_rank_metrics.csv`."])
    (OUTPUT_ROOT / "diagnostic_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    stage31_manifest = json.loads(STAGE31_MANIFEST.read_text(encoding="utf-8"))
    stage32_manifest = json.loads(STAGE32_MANIFEST.read_text(encoding="utf-8"))
    stage32_best = json.loads(STAGE32_BEST.read_text(encoding="utf-8"))

    fixed_tsmixer_model_id = stage31_manifest["classification"]["best_seed_model_id"]
    tuned_trial = int(stage32_best["best_trial_number"])
    tuned_config = dict(stage32_best["best_hyperparameters"])

    labels = pd.read_parquet(fs.STAGE3_ROOT / "labels.parquet", columns=[*ROW_KEY, "forward_excess_return"])
    labels = labels.rename(columns={"forward_excess_return": "target"})
    flags = pd.read_parquet(
        fs.MARKET_FEATURE_ROOT / "market_lag_features.parquet",
        columns=[*ROW_KEY, "no_news_flag", "provider_truncation_risk_flag", "aligned_news_count"],
    )
    flags["aligned_news_count"] = flags["aligned_news_count"].fillna(0).astype("int64")

    fixed_xgb = load_model_predictions(
        fs.STAGE19_ROOT / "saved_predictions.parquet",
        "market_xgboost_v1_fixed",
        "fixed_xgboost",
        labels,
        flags,
    )
    tuned_xgb = load_model_predictions(
        fs.STAGE23_ROOT / "saved_predictions.parquet",
        "market_xgboost_v2_frozen_final",
        "tuned_xgboost",
        labels,
        flags,
    )
    fixed_tsmixer = load_model_predictions(
        PROJECT_ROOT / stage31_manifest["outputs"]["saved_predictions"],
        fixed_tsmixer_model_id,
        "fixed_tsmixer",
        labels,
        flags,
    )
    tuned_tsmixer = fit_tuned_tsmixer_best_trial_predictions(tuned_trial, tuned_config, stage32_manifest, labels, flags)
    tuned_tsmixer["source_model_id"] = f"market_tsmixer_v1_optuna_trial_{tuned_trial:03d}_seed_mean"
    tuned_tsmixer["model_label"] = "tuned_tsmixer"

    combined_cols = [
        "row_key",
        *ROW_KEY,
        "fold_id",
        "split_role",
        "target",
        "prediction",
        "source_model_id",
        "model_label",
        "model_family",
        "branch",
        "no_news_flag",
        "provider_truncation_risk_flag",
        "aligned_news_count",
    ]
    combined = pd.concat(
        [
            fixed_xgb[combined_cols],
            tuned_xgb[combined_cols],
            fixed_tsmixer[combined_cols],
            tuned_tsmixer[combined_cols],
        ],
        ignore_index=True,
        sort=False,
    )
    combined["as_of_date"] = pd.to_datetime(combined["as_of_date"])
    combined["prediction"] = combined["prediction"].astype("float64")
    combined["target"] = combined["target"].astype("float64")
    combined.to_parquet(OUTPUT_ROOT / "combined_scoring_predictions.parquet", index=False)

    unique_dates = np.array(sorted(pd.to_datetime(combined["as_of_date"].dropna().unique())))
    cutoff_index = len(unique_dates) // 2 - 1 if len(unique_dates) % 2 == 0 else len(unique_dates) // 2
    date_cutoff = pd.Timestamp(unique_dates[cutoff_index])

    error_records: list[dict[str, object]] = []
    masks = base_masks(combined, date_cutoff)
    for stratum, mask in masks.items():
        error_records.extend(error_rows_for(combined[mask].copy(), stratum))

    bottom_all, _ = select_bottom_top_rows(combined, K)
    error_records.extend(error_rows_for(bottom_all.copy(), "bottom_k_predicted_rows"))
    error_metrics = add_error_deltas(pd.DataFrame.from_records(error_records))

    rank_records: list[dict[str, object]] = []
    for stratum, mask in masks.items():
        rank_records.extend(rank_metrics_for(combined[mask].copy(), stratum))
    rank_metrics = add_rank_deltas(pd.DataFrame.from_records(rank_records))

    error_metrics.to_parquet(OUTPUT_ROOT / "stratified_error_metrics.parquet", index=False)
    error_metrics.to_csv(OUTPUT_ROOT / "stratified_error_metrics.csv", index=False)
    rank_metrics.to_parquet(OUTPUT_ROOT / "stratified_rank_metrics.parquet", index=False)
    rank_metrics.to_csv(OUTPUT_ROOT / "stratified_rank_metrics.csv", index=False)

    all_rows_error = error_metrics[error_metrics["stratum"].eq("all_rows")].copy()
    all_rows_rank = rank_metrics[rank_metrics["stratum"].eq("all_rows")].copy()
    all_rows_report = all_rows_error.merge(
        all_rows_rank[
            [
                "horizon_id",
                "model_label",
                "bottom_k_realized_mean_forward_excess_return",
                "bottom_k_hit_rate_negative_return",
                "top_minus_bottom_spread",
            ]
        ],
        on=["horizon_id", "model_label"],
        how="left",
        validate="one_to_one",
    )
    all_rows_report = all_rows_report[
        [
            "horizon_id",
            "model_label",
            "row_count",
            "rmse_delta_vs_fixed_xgboost",
            "mae_delta_vs_fixed_xgboost",
            "sign_accuracy_on_negative_returns",
            "bottom_k_realized_mean_forward_excess_return",
            "bottom_k_hit_rate_negative_return",
            "top_minus_bottom_spread",
        ]
    ]
    all_rows_report.to_csv(OUTPUT_ROOT / "all_rows_compact_report.csv", index=False)

    stratum_model_summary = (
        error_metrics.groupby(["stratum", "model_label"], sort=True, observed=True)
        .agg(
            mean_rmse_delta_vs_fixed_xgboost=("rmse_delta_vs_fixed_xgboost", "mean"),
            mean_mae_delta_vs_fixed_xgboost=("mae_delta_vs_fixed_xgboost", "mean"),
            mean_sign_accuracy_on_negative_returns=("sign_accuracy_on_negative_returns", "mean"),
        )
        .reset_index()
    )
    rank_summary = (
        rank_metrics.groupby(["stratum", "model_label"], sort=True, observed=True)
        .agg(
            mean_bottom_k_realized_mean_forward_excess_return=("bottom_k_realized_mean_forward_excess_return", "mean"),
            mean_bottom_k_hit_rate_negative_return=("bottom_k_hit_rate_negative_return", "mean"),
            mean_top_minus_bottom_spread=("top_minus_bottom_spread", "mean"),
        )
        .reset_index()
    )
    stratum_model_summary = stratum_model_summary.merge(rank_summary, on=["stratum", "model_label"], how="left")
    stratum_model_summary.to_csv(OUTPUT_ROOT / "stratum_model_summary.csv", index=False)

    manifest = {
        "artifact_type": "ad_hoc_xgb_tsmixer_stratified_diagnostic",
        "generated_at_utc": "2026-05-25T17:00:00Z",
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "score_scope": SCORING_ROLES,
        "train_rows_excluded_from_report_metrics": True,
        "deltas": "candidate_minus_fixed_xgboost_lower_is_better_for_rmse_mae",
        "ranking_k": K,
        "high_article_count_definition": "aligned_news_count >= 3",
        "early_late_cutoff": str(date_cutoff.date()),
        "bottom_k_hit_rate_definition": "share of model-specific bottom-k rows with realized forward_excess_return < 0",
        "sign_accuracy_on_negative_returns_definition": "share of rows with target < 0 where prediction < 0",
        "top_minus_bottom_spread_definition": "mean realized target of top-k predicted rows minus mean realized target of bottom-k predicted rows, selected within split_role/fold/as_of_date/horizon/model/stratum groups",
        "models": {
            "fixed_xgboost": "market_xgboost_v1_fixed from Stage 19",
            "tuned_xgboost": "market_xgboost_v2_frozen_final from Stage 23",
            "fixed_tsmixer": f"{fixed_tsmixer_model_id} from Stage 31",
            "tuned_tsmixer": f"market_tsmixer_v1_optuna_trial_{tuned_trial:03d}_seed_mean, post-hoc seed-mean predictions from Stage 32 best trial config",
        },
        "source_artifacts": {
            "stage18_manifest": str(STAGE18_MANIFEST.relative_to(PROJECT_ROOT)),
            "stage31_manifest": str(STAGE31_MANIFEST.relative_to(PROJECT_ROOT)),
            "stage32_manifest": str(STAGE32_MANIFEST.relative_to(PROJECT_ROOT)),
            "stage19_predictions": str((fs.STAGE19_ROOT / "saved_predictions.parquet").relative_to(PROJECT_ROOT)),
            "stage23_predictions": str((fs.STAGE23_ROOT / "saved_predictions.parquet").relative_to(PROJECT_ROOT)),
        },
        "outputs": {
            "combined_scoring_predictions": "combined_scoring_predictions.parquet",
            "tuned_tsmixer_best_trial_seed_predictions": "tuned_tsmixer_best_trial_seed_predictions.parquet",
            "tuned_tsmixer_best_trial_fit_manifest": "tuned_tsmixer_best_trial_fit_manifest.parquet",
            "stratified_error_metrics": "stratified_error_metrics.csv",
            "stratified_rank_metrics": "stratified_rank_metrics.csv",
            "all_rows_compact_report": "all_rows_compact_report.csv",
            "stratum_model_summary": "stratum_model_summary.csv",
        },
    }
    (OUTPUT_ROOT / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(manifest, all_rows_report, date_cutoff)

    print("DIAGNOSTIC_COMPLETED")
    print(f"output_root={OUTPUT_ROOT}")
    print(f"manifest={OUTPUT_ROOT / 'manifest.json'}")
    print(f"report={OUTPUT_ROOT / 'diagnostic_report.md'}")
    print(f"error_rows={len(error_metrics)} rank_rows={len(rank_metrics)} combined_predictions={len(combined)}")
    print("all_rows_compact")
    print(all_rows_report.sort_values(["horizon_id", "model_label"]).to_string(index=False, float_format=lambda x: f"{x:.6f}"))


if __name__ == "__main__":
    main()
