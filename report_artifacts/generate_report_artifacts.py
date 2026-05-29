from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import colors as mcolors
from matplotlib.ticker import PercentFormatter


OUT = Path("report_artifacts")
S43 = Path("data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__20260528T100000Z__src_6dff1bd__run_40f1c9a0")
S44 = Path("data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage44__tsmixer_training__20260528T120000Z__src_6dff1bd__run_6817ae4c")
S48 = Path("data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage48__frozen_tsmixer_horizon_mixer__20260529T093301Z__src_6dff1bd__run_fc4c1756")
S47 = Path("data/v1p0_full_results/v1p0__phase1_top50_updated_av__stage47__lockbox_portfolio_simulation__20260529T113128Z__src_6dff1bd__run_dfcd4579")
S6 = Path("data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1")

HORIZON_ORDER = ["1d", "5d", "10d", "20d", "60d"]
HWEIGHTS = {"1d": 0.30, "5d": 0.25, "10d": 0.20, "20d": 0.15, "60d": 0.10}
MODEL_SHORT = {
    "updated_av_xgboost_event_market_optuna_v1": "XGBoost",
    "updated_av_tsmixer_event_market_optuna_v1_seed_mean": "TSMixer",
    "updated_av_xgb_frozen_tsmixer_horizon_mixer_v1": "Mixed model",
}
COLORS = {
    "Mixed model": "#2563eb",
    "TSMixer": "#dc2626",
    "XGBoost": "#f59e0b",
}
POLICY_ORDER = ["one_d_bot10", "botk_2_of_5", "botk_3_of_5", "botk_4_of_5", "none"]
POLICY_SHADE = {
    "one_d_bot10": 0.15,
    "botk_2_of_5": 0.30,
    "botk_3_of_5": 0.45,
    "botk_4_of_5": 0.60,
    "none": 0.78,
}


def blend_with_white(color: str, strength: float) -> str:
    rgb = np.array(mcolors.to_rgb(color))
    white = np.array([1.0, 1.0, 1.0])
    strength = float(np.clip(strength, 0.0, 1.0))
    blended = rgb * (1.0 - strength) + white * strength
    return mcolors.to_hex(blended)


def weighted_delta(deltas: pd.DataFrame) -> float:
    working = deltas.copy()
    working["metric_delta"] = 0.5 * working["rmse_delta_candidate_minus_baseline"] + 0.5 * working["mae_delta_candidate_minus_baseline"]
    working["weighted_delta"] = working["horizon_id"].map(HWEIGHTS).fillna(0.0) * working["metric_delta"]
    return float(working.groupby("horizon_id", sort=True)["weighted_delta"].mean().sum())


def main() -> None:
    OUT.mkdir(exist_ok=True)

    ledger43 = pd.read_parquet(S43 / "trial_ledger.parquet")
    ledger43 = ledger43[ledger43["status"].eq("completed")].sort_values("trial_number").reset_index(drop=True)
    ledger43["best_so_far"] = ledger43["objective_value"].cummin()

    ledger48 = pd.read_parquet(S48 / "mixer_trial_ledger.parquet")
    ledger48 = ledger48[ledger48["status"].eq("completed")].sort_values("trial_number").reset_index(drop=True)
    ledger48["best_so_far"] = ledger48["objective_value"].cummin()

    xgb_metrics = pd.read_parquet(S43 / "best_model_metrics.parquet")
    tsm_metrics = pd.read_parquet(S44 / "best_tsmixer_metrics.parquet")
    mix_metrics = pd.read_parquet(S48 / "best_mixer_metrics.parquet")
    metrics = pd.concat([xgb_metrics, tsm_metrics, mix_metrics], ignore_index=True, sort=False)
    metrics["model_short"] = metrics["model_id"].map(MODEL_SHORT)
    metrics = metrics[metrics["model_short"].notna()].copy()
    lock_metrics = metrics[metrics["split_role"].eq("lockbox")].copy()
    metric_summary = lock_metrics.groupby(["model_short", "horizon_id"], as_index=False).agg(rmse=("rmse", "mean"), mae=("mae", "mean"), r2=("r2_oos_zero_baseline", "mean"))
    metric_summary["horizon_id"] = pd.Categorical(metric_summary["horizon_id"], HORIZON_ORDER, ordered=True)
    metric_summary = metric_summary.sort_values(["horizon_id", "model_short"])

    deltas48 = pd.read_parquet(S48 / "horizon_metric_deltas.parquet")
    deltas48["baseline_short"] = deltas48["baseline_model_id"].map(MODEL_SHORT)
    deltas48["metric_delta"] = 0.5 * deltas48["rmse_delta_candidate_minus_baseline"] + 0.5 * deltas48["mae_delta_candidate_minus_baseline"]
    deltas48 = deltas48[deltas48["baseline_short"].notna()].copy()
    delta_rows = []
    for (base, split), group in deltas48.groupby(["baseline_short", "split_role"], sort=True):
        delta_rows.append({"baseline_short": base, "split_role": split, "weighted_delta": weighted_delta(group), "improve_rate": float(group["both_metrics_improve"].mean())})
    delta_summary = pd.DataFrame(delta_rows)

    coef = pd.read_parquet(S48 / "best_mixer_coefficients.parquet")
    coef["horizon_id"] = pd.Categorical(coef["horizon_id"], HORIZON_ORDER, ordered=True)
    coef_summary = coef.groupby(["horizon_id", "mode"], as_index=False, observed=True).agg(xgb=("raw_xgboost_weight", "mean"), tsmixer=("raw_tsmixer_weight", "mean"))
    coef_summary = coef_summary[coef_summary["mode"].notna()].sort_values("horizon_id")

    port = pd.read_parquet(S47 / "simulation_summary.parquet")
    port["model_short"] = port["model_id"].map(MODEL_SHORT)
    port = port[port["model_short"].notna()].copy()
    port["horizon_id"] = pd.Categorical(port["horizon_id"], HORIZON_ORDER, ordered=True)
    port_mean = port.groupby(["model_short", "sell_policy"], as_index=False).agg(mean_final_equity=("final_equity", "mean"), best_final_equity=("final_equity", "max"), mean_drawdown=("max_drawdown_pct", "mean"))

    rank = pd.read_parquet(S6 / "ranking_diagnostics.parquet")
    rank_lock = rank[rank["split_role"].eq("lockbox")].copy()
    rank_summary = rank_lock.groupby("model_id", as_index=False).agg(rank_ic=("spearman_rank_ic", "mean"), hit=("directional_hit_rate", "mean"), spread=("top_minus_bottom_spread", "mean")).sort_values("rank_ic", ascending=False).head(8)

    write_main_panel(ledger43, metric_summary, delta_summary, port)
    write_tuning_curves(ledger43, ledger48)
    write_metric_bars(metric_summary)
    write_mixer_diagnostics(coef_summary, deltas48)
    write_portfolio_diagnostics(port, port_mean)
    write_portfolio_policy_returns(port)
    write_ranking_uncertainty(rank_summary)

    metric_summary.to_csv(OUT / "lockbox_metric_summary.csv", index=False)
    delta_summary.to_csv(OUT / "stage48_delta_summary.csv", index=False)
    port.sort_values("final_equity", ascending=False).head(20).to_csv(OUT / "portfolio_top20.csv", index=False)
    rank_summary.to_csv(OUT / "ranking_summary.csv", index=False)

    best43 = ledger43.sort_values(["objective_value", "trial_number"]).iloc[0]
    best48 = ledger48.sort_values(["objective_value", "trial_number"]).iloc[0]
    best_port = port.sort_values("final_equity", ascending=False).iloc[0]
    summary = {
        "auc_status": "not_applicable_continuous_excess_return_regression",
        "portfolio_top_final_equity": float(best_port["final_equity"]),
        "portfolio_top_horizon": str(best_port["horizon_id"]),
        "portfolio_top_model": str(best_port["model_short"]),
        "portfolio_top_policy": str(best_port["sell_policy"]),
        "portfolio_top_return": float(best_port["total_return"]),
        "stage43_best_trial": int(best43["trial_number"]),
        "stage43_lockbox_delta_vs_prev": -0.0005342887655541226,
        "stage43_lockbox_improve_rate": 0.6222222222222222,
        "stage43_trials": int(len(ledger43)),
        "stage47_rows": int(len(port)),
        "stage48_best_trial": int(best48["trial_number"]),
        "stage48_lockbox_delta_vs_tsmixer": float(delta_summary[(delta_summary.baseline_short.eq("TSMixer")) & (delta_summary.split_role.eq("lockbox"))]["weighted_delta"].iloc[0]),
        "stage48_lockbox_delta_vs_xgb": float(delta_summary[(delta_summary.baseline_short.eq("XGBoost")) & (delta_summary.split_role.eq("lockbox"))]["weighted_delta"].iloc[0]),
        "stage48_lockbox_rate_vs_xgb": float(delta_summary[(delta_summary.baseline_short.eq("XGBoost")) & (delta_summary.split_role.eq("lockbox"))]["improve_rate"].iloc[0]),
        "stage48_trials": int(len(ledger48)),
        "stage48_validation_delta_vs_xgb": float(delta_summary[(delta_summary.baseline_short.eq("XGBoost")) & (delta_summary.split_role.eq("validation"))]["weighted_delta"].iloc[0]),
    }
    (OUT / "summary_numbers.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": "figures_created", "files": sorted(path.name for path in OUT.iterdir())}, sort_keys=True))


def write_main_panel(ledger43: pd.DataFrame, metric_summary: pd.DataFrame, delta_summary: pd.DataFrame, port: pd.DataFrame) -> None:
    fig, axs = plt.subplots(2, 2, figsize=(10.8, 6.6), constrained_layout=True)
    ax = axs[0, 0]
    ax.plot(ledger43["trial_number"], ledger43["objective_value"], color="#93c5fd", lw=0.7, alpha=0.65, label="trial objective")
    ax.plot(ledger43["trial_number"], ledger43["best_so_far"], color="#1d4ed8", lw=2, label="best so far")
    ax.axvline(798, color="#111827", ls="--", lw=1)
    ax.set_title("A. XGBoost Optuna search (800 trials)")
    ax.set_xlabel("trial")
    ax.set_ylabel("guarded objective")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axs[0, 1]
    subset = metric_summary[metric_summary["model_short"].isin(["XGBoost", "Mixed model", "TSMixer"])]
    x = np.arange(len(HORIZON_ORDER))
    width = 0.24
    for index, model in enumerate(["XGBoost", "Mixed model", "TSMixer"]):
        values = subset[subset["model_short"].eq(model)].set_index("horizon_id").reindex(HORIZON_ORDER)["rmse"].to_numpy()
        ax.bar(x + (index - 1) * width, values, width=width, label=model, color=COLORS[model], alpha=0.85)
    ax.set_title("B. Lockbox RMSE by horizon")
    ax.set_xticks(x)
    ax.set_xticklabels(HORIZON_ORDER)
    ax.set_ylabel("RMSE")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=7)

    ax = axs[1, 0]
    order_split = ["train", "validation", "lockbox"]
    width = 0.35
    x = np.arange(len(order_split))
    for index, base in enumerate(["XGBoost", "TSMixer"]):
        values = delta_summary[delta_summary["baseline_short"].eq(base)].set_index("split_role").reindex(order_split)["weighted_delta"].to_numpy()
        ax.bar(x + (index - 0.5) * width, values, width=width, label=f"vs {base}", color=["#d97706", "#059669"][index], alpha=0.88)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title("C. Stage 48 weighted error deltas")
    ax.set_xticks(x)
    ax.set_xticklabels(order_split)
    ax.set_ylabel("candidate - baseline; lower is better")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axs[1, 1]
    for model in ["XGBoost", "Mixed model", "TSMixer"]:
        subset = port[port["model_short"].eq(model)]
        ax.scatter(subset["max_drawdown_pct"], subset["total_return"], s=36, alpha=0.7, label=model, color=COLORS[model])
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(0, color="black", lw=0.8)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_title("D. Historical lockbox portfolios")
    ax.set_xlabel("max drawdown")
    ax.set_ylabel("total return")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=7)
    fig.suptitle("Leakage-aware multi-horizon excess-return forecasting: core evidence", fontsize=13, fontweight="bold")
    fig.savefig(OUT / "main_results_panel.pdf", bbox_inches="tight")
    fig.savefig(OUT / "main_results_panel.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def write_tuning_curves(ledger43: pd.DataFrame, ledger48: pd.DataFrame) -> None:
    fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.6), constrained_layout=True)
    for ax, data, title, best in [(axs[0], ledger43, "Stage 43 XGBoost", 798), (axs[1], ledger48, "Stage 48 frozen-TSMixer mixer", 391)]:
        ax.plot(data["trial_number"], data["objective_value"], color="#cbd5e1", lw=0.6, label="trial")
        ax.plot(data["trial_number"], data["best_so_far"], color="#dc2626", lw=2, label="incumbent")
        ax.axvline(best, color="#111827", ls="--", lw=1, label=f"best {best}")
        ax.set_title(title)
        ax.set_xlabel("trial")
        ax.set_ylabel("objective")
        ax.grid(alpha=0.25)
        ax.legend(frameon=False, fontsize=8)
    fig.savefig(OUT / "tuning_curves.pdf", bbox_inches="tight")
    plt.close(fig)


def write_metric_bars(metric_summary: pd.DataFrame) -> None:
    subset = metric_summary[metric_summary["model_short"].isin(["XGBoost", "Mixed model", "TSMixer"])]
    fig, axs = plt.subplots(1, 2, figsize=(10.8, 3.8), constrained_layout=True)
    x = np.arange(len(HORIZON_ORDER))
    for ax, metric, ylabel in [(axs[0], "rmse", "RMSE"), (axs[1], "mae", "MAE")]:
        width = 0.24
        for index, model in enumerate(["XGBoost", "Mixed model", "TSMixer"]):
            values = subset[subset["model_short"].eq(model)].set_index("horizon_id").reindex(HORIZON_ORDER)[metric].to_numpy()
            ax.bar(x + (index - 1) * width, values, width=width, label=model, color=COLORS[model], alpha=0.85)
        ax.set_title(f"Lockbox {ylabel}")
        ax.set_xticks(x)
        ax.set_xticklabels(HORIZON_ORDER)
        ax.set_ylabel(ylabel)
        ax.grid(axis="y", alpha=0.25)
        ax.legend(frameon=False, fontsize=7)
    fig.savefig(OUT / "lockbox_rmse_mae.pdf", bbox_inches="tight")
    plt.close(fig)


def write_mixer_diagnostics(coef_summary: pd.DataFrame, deltas48: pd.DataFrame) -> None:
    fig, axs = plt.subplots(1, 2, figsize=(10.8, 3.8), constrained_layout=True)
    x = np.arange(len(HORIZON_ORDER))
    ax = axs[0]
    coef_plot = coef_summary.set_index("horizon_id").reindex(HORIZON_ORDER)
    ax.bar(x - 0.17, coef_plot["xgb"], width=0.34, label="XGB weight", color=COLORS["XGBoost"])
    ax.bar(x + 0.17, coef_plot["tsmixer"], width=0.34, label="TSMixer weight", color=COLORS["TSMixer"])
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(HORIZON_ORDER)
    ax.set_title("Stage 48 mean raw weights")
    ax.set_ylabel("raw coefficient")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)

    ax = axs[1]
    lock_delta = deltas48[deltas48["split_role"].eq("lockbox")].groupby(["baseline_short", "horizon_id"], as_index=False).agg(metric_delta=("metric_delta", "mean"), improve_rate=("both_metrics_improve", "mean"))
    for index, base in enumerate(["XGBoost", "TSMixer"]):
        values = lock_delta[lock_delta["baseline_short"].eq(base)].set_index("horizon_id").reindex(HORIZON_ORDER)["metric_delta"].to_numpy()
        ax.bar(x + (index - 0.5) * 0.34, values, width=0.34, label=f"vs {base}", color=["#d97706", "#059669"][index], alpha=0.88)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(HORIZON_ORDER)
    ax.set_title("Stage 48 lockbox horizon deltas")
    ax.set_ylabel("mean RMSE/MAE delta")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(OUT / "mixer_weights_deltas.pdf", bbox_inches="tight")
    plt.close(fig)


def write_portfolio_diagnostics(port: pd.DataFrame, port_mean: pd.DataFrame) -> None:
    fig, axs = plt.subplots(1, 2, figsize=(10.8, 3.8), constrained_layout=True)
    ax = axs[0]
    mean_plot = port_mean.sort_values("mean_final_equity")
    y = np.arange(len(mean_plot))
    colors = [COLORS.get(model, "#64748b") for model in mean_plot["model_short"]]
    ax.barh(y, mean_plot["mean_final_equity"], color=colors, alpha=0.85)
    ax.axvline(100000, color="black", lw=0.8, ls="--")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{model}\n{policy}" for model, policy in zip(mean_plot["model_short"], mean_plot["sell_policy"])], fontsize=6)
    ax.set_xlabel("mean final equity over horizons")
    ax.set_title("Portfolio diagnostic: policy mean")
    ax.grid(axis="x", alpha=0.25)

    ax = axs[1]
    for model in ["XGBoost", "Mixed model", "TSMixer"]:
        subset = port[port["model_short"].eq(model)]
        ax.scatter(subset["initial_capital_turnover"], subset["total_return"], s=36, alpha=0.75, label=model, color=COLORS[model])
    ax.axhline(0, color="black", lw=0.8)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_xscale("symlog", linthresh=0.1)
    ax.set_xlabel("turnover / initial capital")
    ax.set_ylabel("total return")
    ax.set_title("Return vs turnover")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, fontsize=7)
    fig.savefig(OUT / "portfolio_diagnostics.pdf", bbox_inches="tight")
    plt.close(fig)


def write_ranking_uncertainty(rank_summary: pd.DataFrame) -> None:
    fig, axs = plt.subplots(1, 2, figsize=(10.8, 3.8), constrained_layout=True)
    ax = axs[0]
    rank_plot = rank_summary.sort_values("rank_ic")
    y = np.arange(len(rank_plot))
    ax.barh(y, rank_plot["rank_ic"], color="#475569")
    ax.axvline(0, color="black", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(rank_plot["model_id"], fontsize=6)
    ax.set_xlabel("mean Spearman rank IC")
    ax.set_title("Stage 6 ranking diagnostic")
    ax.grid(axis="x", alpha=0.25)

    ax = axs[1]
    summary_text = [("Lockbox MAE", 0.963, 0.992), ("Lockbox RMSE", 0.865, 0.973), ("Validation MAE", 0.759, 0.904), ("Validation RMSE", 0.607, 0.787)]
    labels = [row[0] for row in summary_text]
    mins = [row[1] for row in summary_text]
    means = [row[2] for row in summary_text]
    y = np.arange(len(labels))
    ax.barh(y - 0.16, mins, height=0.32, label="min prob.", color="#94a3b8")
    ax.barh(y + 0.16, means, height=0.32, label="mean prob.", color="#0f766e")
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_title("Stage 25 block-bootstrap support")
    ax.grid(axis="x", alpha=0.25)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(OUT / "ranking_uncertainty.pdf", bbox_inches="tight")
    plt.close(fig)


def write_portfolio_policy_returns(port: pd.DataFrame) -> None:
    plot = port.copy()
    plot["horizon_id"] = pd.Categorical(plot["horizon_id"], HORIZON_ORDER, ordered=True)
    plot["sell_policy"] = pd.Categorical(plot["sell_policy"], POLICY_ORDER, ordered=True)
    plot = plot.sort_values(["horizon_id", "model_short", "sell_policy"])

    model_order = ["Mixed model", "TSMixer", "XGBoost"]
    model_colors = {model: COLORS[model] for model in model_order}
    policy_legend = ["one_d_bot10", "botk_2_of_5", "botk_3_of_5", "botk_4_of_5", "none"]
    policy_labels = {
        "one_d_bot10": "1d",
        "botk_2_of_5": "2 of 5",
        "botk_3_of_5": "3 of 5",
        "botk_4_of_5": "4 of 5",
        "none": "none",
    }

    for horizon in HORIZON_ORDER:
        slice_df = plot[plot["horizon_id"].eq(horizon)].copy()
        slice_df["model_short"] = pd.Categorical(slice_df["model_short"], model_order, ordered=True)
        slice_df = slice_df.sort_values(["model_short", "sell_policy"])
        labels = slice_df.apply(lambda row: f"{row['model_short']} | {policy_labels[str(row['sell_policy'])]}", axis=1)

        fig, ax = plt.subplots(figsize=(9.2, 4.6), constrained_layout=True)
        x = np.arange(len(slice_df))
        colors = []
        for _, row in slice_df.iterrows():
            base = model_colors[str(row["model_short"])]
            shade = POLICY_SHADE[str(row["sell_policy"])]
            colors.append(blend_with_white(base, shade))
        ax.bar(x, slice_df["total_return"], color=colors, alpha=0.95, edgecolor="#111827", linewidth=0.6, zorder=3)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_axisbelow(True)
        ax.set_title(f"Lockbox portfolio return by model and policy ({horizon})")
        ax.set_ylabel("total return")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7)
        ax.grid(axis="y", alpha=0.25)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))

        model_handles = [
            plt.Line2D([0], [0], color=model_colors[m], lw=6, label=m) for m in model_order
        ]
        policy_handles = [
            plt.Line2D([0], [0], color=blend_with_white("#000000", POLICY_SHADE[p]), lw=6, label=policy_labels[p])
            for p in policy_legend
        ]
        model_legend = ax.legend(handles=model_handles, title="model", frameon=False, fontsize=8, loc="upper left")
        ax.legend(handles=policy_handles, title="policy", frameon=False, fontsize=8, loc="upper right")
        ax.add_artist(model_legend)

        fig.savefig(OUT / f"portfolio_returns_by_policy_model_{horizon}.pdf", bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    main()
