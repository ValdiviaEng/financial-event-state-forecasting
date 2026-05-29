from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import stable_digest  # noqa: E402


RESULT_ROOT = PROJECT_ROOT / "data/v1p0_full_results"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1"
XGBOOST_PREDICTIONS = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage43__xgboost_tuning__20260528T100000Z__src_6dff1bd__run_40f1c9a0/best_model_predictions.parquet"
TSMIXER_PREDICTIONS = RESULT_ROOT / "v1p0__phase1_top50_updated_av__stage44__tsmixer_training__20260528T120000Z__src_6dff1bd__run_6817ae4c/best_tsmixer_predictions.parquet"

SOURCE_ID = "6dff1bd"
INITIAL_CAPITAL = 100000.0
TOP_K = 10
BOT_K = 10
HORIZON_DAYS = {"1d": 1, "5d": 5, "10d": 10, "20d": 20, "60d": 60}
HORIZON_ORDER = tuple(HORIZON_DAYS.keys())
RANK_WEIGHTS = {1: 0.22, 2: 0.18, 3: 0.15, 4: 0.12, 5: 0.08, 6: 0.05, 7: 0.05, 8: 0.05, 9: 0.05, 10: 0.05}
SELL_POLICIES = ("one_d_bot10", "none", "botk_4_of_5", "botk_3_of_5", "botk_2_of_5")


@dataclass
class Lot:
    lot_id: int
    model_id: str
    horizon_id: str
    canonical_ticker: str
    shares: float
    entry_signal_date: str
    entry_execution_date: str
    entry_price: float
    expiry_date: str | None
    entry_rank: int


def stage47_simulation_contract() -> dict[str, Any]:
    return {
        "artifact_type": "updated_dataset_lockbox_portfolio_simulation_contract",
        "stage": 47,
        "initial_capital": INITIAL_CAPITAL,
        "rank_weights": RANK_WEIGHTS,
        "horizon_days": HORIZON_DAYS,
        "sell_policies": list(SELL_POLICIES),
        "signal_policy": {
            "split_role": "lockbox",
            "fold_aggregation": "mean",
            "constant_cross_section_policy": "skip_no_signal",
            "top_k": TOP_K,
            "bot_k": BOT_K,
        },
        "execution_policy": {
            "buy_sell_price": "next_trading_day_market_open",
            "final_mark_price": "last_available_lockbox_date_market_open",
            "fractional_shares": True,
            "transaction_costs": 0.0,
            "slippage": 0.0,
            "taxes": 0.0,
            "dividends": False,
            "shorting": False,
            "leverage": False,
        },
        "non_claims": [
            "historical_lockbox_diagnostic_only",
            "not_trading_advice",
            "not_live_forecast",
            "not_positive_benchmark_claim",
            "not_stage6_reinterpretation",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Stage 47 historical lockbox portfolio simulations for updated Alpha Vantage model predictions.")
    parser.add_argument("--xgboost-predictions", type=Path, default=XGBOOST_PREDICTIONS)
    parser.add_argument("--tsmixer-predictions", type=Path, default=TSMIXER_PREDICTIONS)
    parser.add_argument("--mixer-predictions", type=Path, default=None)
    parser.add_argument("--market-features", type=Path, default=STAGE3_ROOT / "market_features.parquet")
    parser.add_argument("--initial-capital", type=float, default=INITIAL_CAPITAL)
    parser.add_argument("--output-root", type=Path, default=None)
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0)
    generated_token = generated_at.strftime("%Y%m%dT%H%M%SZ")
    contract = stage47_simulation_contract()
    contract["generated_at_utc"] = generated_at.isoformat().replace("+00:00", "Z")
    contract["initial_capital"] = float(args.initial_capital)
    input_records = [
        {"model_input": "xgboost", "path": _rel(args.xgboost_predictions.resolve()), "required": True},
        {"model_input": "current_frozen_tsmixer", "path": _rel(args.tsmixer_predictions.resolve()), "required": True, "evidence_status": "current_frozen_diagnostic_input_only"},
    ]
    if args.mixer_predictions is not None:
        input_records.append({"model_input": "best_mixed_model", "path": _rel(args.mixer_predictions.resolve()), "required": True})
    contract["model_inputs"] = input_records
    digest = stable_digest(contract)[:8]
    run_id = f"v1p0__phase1_top50_updated_av__stage47__lockbox_portfolio_simulation__{generated_token}__src_{SOURCE_ID}__run_{digest}"
    output_root = args.output_root.resolve() if args.output_root else RESULT_ROOT / run_id
    output_root.mkdir(parents=True, exist_ok=True)

    predictions, roster = _load_prediction_roster(args.xgboost_predictions, args.tsmixer_predictions, args.mixer_predictions)
    market = _load_market_prices(args.market_features)
    signals = build_rank_signals(predictions)
    trades, equity, holdings, summary = run_all_simulations(signals, market, float(args.initial_capital))
    drawdown, exposure, turnover, allocation, summary = build_diagnostic_tables(trades, equity, holdings, summary, float(args.initial_capital))

    rank_path = output_root / "rank_lists.parquet"
    trades_path = output_root / "trade_ledger.parquet"
    equity_path = output_root / "equity_curve.parquet"
    drawdown_path = output_root / "drawdown.parquet"
    exposure_path = output_root / "exposure.parquet"
    turnover_path = output_root / "turnover.parquet"
    allocation_path = output_root / "allocation_diagnostics.parquet"
    holdings_path = output_root / "final_holdings.parquet"
    summary_path = output_root / "simulation_summary.parquet"
    summary_json_path = output_root / "simulation_summary.json"
    report_md_path = output_root / "stage47_lockbox_portfolio_simulation_report.md"
    report_html_path = output_root / "stage47_lockbox_portfolio_simulation_report.html"
    equity_svg_path = output_root / "final_equity_by_model_policy.svg"
    manifest_path = output_root / "lockbox_portfolio_simulation_manifest.json"
    run_manifest_path = output_root / "run_manifest.json"

    signals.to_parquet(rank_path, index=False)
    trades.to_parquet(trades_path, index=False)
    equity.to_parquet(equity_path, index=False)
    drawdown.to_parquet(drawdown_path, index=False)
    exposure.to_parquet(exposure_path, index=False)
    turnover.to_parquet(turnover_path, index=False)
    allocation.to_parquet(allocation_path, index=False)
    holdings.to_parquet(holdings_path, index=False)
    summary.to_parquet(summary_path, index=False)
    _write_json(summary_json_path, {"rows": summary.to_dict("records")})
    equity_svg_path.write_text(_final_equity_svg(summary), encoding="utf-8")

    manifest = {
        **contract,
        "artifact_type": "updated_dataset_lockbox_portfolio_simulation_manifest",
        "artifact_id": f"updated_dataset_lockbox_portfolio_simulation__{digest}__{generated_token}",
        "run_id": run_id,
        "status": "completed",
        "model_roster": roster,
        "outputs": {
            "rank_lists": _rel(rank_path),
            "trade_ledger": _rel(trades_path),
            "equity_curve": _rel(equity_path),
            "drawdown": _rel(drawdown_path),
            "exposure": _rel(exposure_path),
            "turnover": _rel(turnover_path),
            "allocation_diagnostics": _rel(allocation_path),
            "final_holdings": _rel(holdings_path),
            "simulation_summary": _rel(summary_path),
            "simulation_summary_json": _rel(summary_json_path),
            "final_equity_by_model_policy_svg": _rel(equity_svg_path),
            "report_markdown": _rel(report_md_path),
            "report_html": _rel(report_html_path),
            "manifest": _rel(manifest_path),
            "run_manifest": _rel(run_manifest_path),
        },
        "benchmark_claim": False,
        "positive_claim_approved": False,
        "trading_signal_approved": False,
    }
    _write_json(manifest_path, manifest)
    _write_json(run_manifest_path, {"stage": 47, "stage_name": "lockbox_portfolio_simulation", "status": "completed", "run_id": run_id, "outputs": manifest["outputs"], "benchmark_claim": False, "trading_signal_approved": False})
    report_md_path.write_text(_render_markdown_report(manifest, summary), encoding="utf-8")
    report_html_path.write_text(_render_html_report(manifest, summary), encoding="utf-8")
    print(json.dumps({"status": "completed", "manifest": manifest["outputs"]["manifest"], "summary": manifest["outputs"]["simulation_summary_json"]}, sort_keys=True))


def _load_prediction_roster(xgboost_path: Path, tsmixer_path: Path, mixer_path: Path | None) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    frames = []
    roster = []
    for role, path, model_filter, status in [
        ("best_individual_xgboost", xgboost_path, "updated_av_xgboost_event_market_optuna_v1", "valid_current_evidence"),
        ("best_individual_current_frozen_tsmixer", tsmixer_path, "updated_av_tsmixer_event_market_optuna_v1_seed_mean", "current_frozen_diagnostic_input_only"),
    ]:
        frame = pd.read_parquet(path)
        frame = frame[frame["model_id"] == model_filter].copy()
        frames.append(frame)
        roster.append({"role": role, "model_id": model_filter, "path": _rel(path.resolve()), "rows": int(len(frame)), "status": status})
    if mixer_path is not None:
        frame = pd.read_parquet(mixer_path)
        model_ids = sorted(frame["model_id"].astype(str).unique().tolist())
        if len(model_ids) != 1:
            raise RuntimeError(f"mixed-model predictions must contain exactly one model_id, got {model_ids}")
        frames.append(frame.copy())
        roster.append({"role": "best_mixed_model", "model_id": model_ids[0], "path": _rel(mixer_path.resolve()), "rows": int(len(frame)), "status": "valid_current_mixer_diagnostic"})
    return pd.concat(frames, ignore_index=True, sort=False), roster


def _load_market_prices(path: Path) -> pd.DataFrame:
    market = pd.read_parquet(path, columns=["canonical_ticker", "as_of_date", "market_open", "market_close"])
    market["as_of_date"] = pd.to_datetime(market["as_of_date"]).dt.strftime("%Y-%m-%d")
    return market.drop_duplicates(["canonical_ticker", "as_of_date"]).sort_values(["as_of_date", "canonical_ticker"]).reset_index(drop=True)


def build_rank_signals(predictions: pd.DataFrame) -> pd.DataFrame:
    required = {"canonical_ticker", "as_of_date", "horizon_id", "fold_id", "split_role", "model_id", "prediction"}
    missing = required - set(predictions.columns)
    if missing:
        raise RuntimeError(f"predictions missing required columns: {sorted(missing)}")
    frame = predictions[predictions["split_role"] == "lockbox"].copy()
    frame["as_of_date"] = pd.to_datetime(frame["as_of_date"]).dt.strftime("%Y-%m-%d")

    fold_records: list[dict[str, Any]] = []
    for (model_id, as_of_date, horizon_id, fold_id), group in frame.groupby(["model_id", "as_of_date", "horizon_id", "fold_id"], sort=True):
        if group["prediction"].nunique(dropna=False) <= 1:
            continue
        top = group.sort_values(["prediction", "canonical_ticker"], ascending=[False, True]).head(TOP_K)
        bot = group.sort_values(["prediction", "canonical_ticker"], ascending=[True, True]).head(BOT_K)
        for side, side_frame in [("top", top), ("bot", bot)]:
            for rank, row in enumerate(side_frame.itertuples(index=False), start=1):
                fold_records.append(
                    {
                        "model_id": model_id,
                        "as_of_date": as_of_date,
                        "horizon_id": horizon_id,
                        "fold_id": fold_id,
                        "side": side,
                        "rank": float(rank),
                        "canonical_ticker": row.canonical_ticker,
                    }
                )

    if not fold_records:
        return pd.DataFrame(columns=["model_id", "as_of_date", "horizon_id", "side", "rank", "canonical_ticker", "fold_mean_prediction", "constant_horizon_skipped"])

    fold_frame = pd.DataFrame.from_records(fold_records)
    agg = fold_frame.groupby(["model_id", "as_of_date", "horizon_id", "side", "canonical_ticker"], as_index=False)["rank"].mean()

    records: list[dict[str, Any]] = []
    for (model_id, as_of_date, horizon_id, side), group in agg.groupby(["model_id", "as_of_date", "horizon_id", "side"], sort=True):
        group = group.sort_values(["rank", "canonical_ticker"], ascending=[True, True])
        limit = TOP_K if side == "top" else BOT_K
        for out_rank, row in enumerate(group.head(limit).itertuples(index=False), start=1):
            records.append(
                {
                    "model_id": model_id,
                    "as_of_date": as_of_date,
                    "horizon_id": horizon_id,
                    "side": side,
                    "rank": int(out_rank),
                    "canonical_ticker": row.canonical_ticker,
                    "fold_mean_prediction": float(row.rank),
                    "constant_horizon_skipped": False,
                }
            )
    return pd.DataFrame.from_records(records)


def sell_set_for_policy(signals_for_date: pd.DataFrame, policy: str) -> set[str]:
    bot = signals_for_date[signals_for_date["side"] == "bot"]
    if policy == "none" or bot.empty:
        return set()
    if policy == "one_d_bot10":
        return set(bot[bot["horizon_id"] == "1d"]["canonical_ticker"].astype(str))
    thresholds = {"botk_4_of_5": 4, "botk_3_of_5": 3, "botk_2_of_5": 2}
    if policy not in thresholds:
        raise RuntimeError(f"unsupported sell policy: {policy}")
    counts = Counter(bot.drop_duplicates(["horizon_id", "canonical_ticker"])["canonical_ticker"].astype(str))
    return {ticker for ticker, count in counts.items() if count >= thresholds[policy]}


def run_all_simulations(signals: pd.DataFrame, market: pd.DataFrame, initial_capital: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    price_lookup = {(row.canonical_ticker, row.as_of_date): float(row.market_open) for row in market.itertuples(index=False)}
    dates = sorted(signals["as_of_date"].unique().tolist())
    calendar = sorted(market["as_of_date"].unique().tolist())
    next_date = {date: _next_calendar_date(calendar, date) for date in dates}
    final_mark_date = max(dates)
    all_trades = []
    all_equity = []
    all_holdings = []
    summary_rows = []
    for model_id in sorted(signals["model_id"].unique().tolist()):
        model_signals = signals[signals["model_id"] == model_id].copy()
        for policy in SELL_POLICIES:
            for horizon_id in HORIZON_ORDER:
                trade_rows, equity_rows, holdings_rows, summary = _simulate_one(model_id, horizon_id, policy, model_signals, price_lookup, next_date, final_mark_date, initial_capital)
                all_trades.extend(trade_rows)
                all_equity.extend(equity_rows)
                all_holdings.extend(holdings_rows)
                summary_rows.append(summary)
    return pd.DataFrame.from_records(all_trades), pd.DataFrame.from_records(all_equity), pd.DataFrame.from_records(all_holdings), pd.DataFrame.from_records(summary_rows)


def build_diagnostic_tables(trades: pd.DataFrame, equity: pd.DataFrame, holdings: pd.DataFrame, summary: pd.DataFrame, initial_capital: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group_cols = ["model_id", "horizon_id", "sell_policy"]
    drawdown = _build_drawdown_table(equity, group_cols)
    exposure = _build_exposure_table(equity)
    turnover = _build_turnover_table(trades, equity, group_cols, initial_capital)
    allocation = _build_allocation_table(holdings, summary, group_cols)
    return drawdown, exposure, turnover, allocation, _augment_summary(summary, drawdown, exposure, turnover, group_cols)


def _build_drawdown_table(equity: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    if equity.empty:
        return pd.DataFrame(columns=group_cols + ["signal_date", "execution_date", "equity", "running_peak_equity", "drawdown_abs", "drawdown_pct"])
    frame = equity.sort_values(group_cols + ["execution_date", "signal_date"]).copy()
    frame["running_peak_equity"] = frame.groupby(group_cols, sort=False)["equity"].cummax()
    frame["drawdown_abs"] = frame["equity"] - frame["running_peak_equity"]
    frame["drawdown_pct"] = np.where(frame["running_peak_equity"] > 0, frame["drawdown_abs"] / frame["running_peak_equity"], 0.0)
    return frame[group_cols + ["signal_date", "execution_date", "equity", "running_peak_equity", "drawdown_abs", "drawdown_pct"]]


def _build_exposure_table(equity: pd.DataFrame) -> pd.DataFrame:
    if equity.empty:
        return pd.DataFrame(columns=list(equity.columns) + ["cash_weight", "gross_exposure", "gross_exposure_ratio"])
    frame = equity.copy()
    frame["cash_weight"] = np.where(frame["equity"] != 0, frame["cash"] / frame["equity"], 0.0)
    frame["gross_exposure"] = frame["market_value"].abs()
    frame["gross_exposure_ratio"] = np.where(frame["equity"] != 0, frame["gross_exposure"] / frame["equity"], 0.0)
    return frame


def _build_turnover_table(trades: pd.DataFrame, equity: pd.DataFrame, group_cols: list[str], initial_capital: float) -> pd.DataFrame:
    columns = group_cols + ["execution_date", "trade_count", "buy_notional", "sell_notional", "traded_notional", "equity", "turnover_ratio", "initial_capital_turnover"]
    if trades.empty:
        return pd.DataFrame(columns=columns)
    frame = trades.copy()
    frame["trade_notional"] = frame["cash_effect"].abs()
    frame["buy_notional"] = np.where(frame["action"] == "buy", frame["trade_notional"], 0.0)
    frame["sell_notional"] = np.where(frame["action"] == "sell", frame["trade_notional"], 0.0)
    grouped = frame.groupby(group_cols + ["execution_date"], as_index=False).agg(trade_count=("action", "size"), buy_notional=("buy_notional", "sum"), sell_notional=("sell_notional", "sum"), traded_notional=("trade_notional", "sum"))
    equity_lookup = equity.sort_values(group_cols + ["execution_date", "signal_date"]).drop_duplicates(group_cols + ["execution_date"], keep="last")[group_cols + ["execution_date", "equity"]]
    grouped = grouped.merge(equity_lookup, on=group_cols + ["execution_date"], how="left")
    grouped["turnover_ratio"] = np.where(grouped["equity"] > 0, grouped["traded_notional"] / grouped["equity"], 0.0)
    grouped["initial_capital_turnover"] = grouped["traded_notional"] / float(initial_capital)
    return grouped[columns]


def _build_allocation_table(holdings: pd.DataFrame, summary: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    columns = list(holdings.columns) + ["final_equity", "final_weight"]
    if holdings.empty:
        return pd.DataFrame(columns=columns)
    frame = holdings.copy()
    final_equity = summary[group_cols + ["final_equity"]]
    frame = frame.merge(final_equity, on=group_cols, how="left")
    frame["final_weight"] = np.where(frame["final_equity"] > 0, frame["market_value"] / frame["final_equity"], 0.0)
    return frame


def _augment_summary(summary: pd.DataFrame, drawdown: pd.DataFrame, exposure: pd.DataFrame, turnover: pd.DataFrame, group_cols: list[str]) -> pd.DataFrame:
    frame = summary.copy()
    if not drawdown.empty:
        dd = drawdown.groupby(group_cols, as_index=False).agg(max_drawdown_abs=("drawdown_abs", "min"), max_drawdown_pct=("drawdown_pct", "min"))
        frame = frame.merge(dd, on=group_cols, how="left")
    else:
        frame["max_drawdown_abs"] = 0.0
        frame["max_drawdown_pct"] = 0.0
    if not exposure.empty:
        exp = exposure.groupby(group_cols, as_index=False).agg(average_gross_exposure_ratio=("gross_exposure_ratio", "mean"), final_cash=("cash", "last"), final_market_value=("market_value", "last"))
        frame = frame.merge(exp, on=group_cols, how="left")
    else:
        frame["average_gross_exposure_ratio"] = 0.0
        frame["final_cash"] = 0.0
        frame["final_market_value"] = 0.0
    if not turnover.empty:
        turns = turnover.groupby(group_cols, as_index=False).agg(total_traded_notional=("traded_notional", "sum"), average_turnover_ratio=("turnover_ratio", "mean"), initial_capital_turnover=("initial_capital_turnover", "sum"))
        frame = frame.merge(turns, on=group_cols, how="left")
    else:
        frame["total_traded_notional"] = 0.0
        frame["average_turnover_ratio"] = 0.0
        frame["initial_capital_turnover"] = 0.0
    fill_cols = ["max_drawdown_abs", "max_drawdown_pct", "average_gross_exposure_ratio", "final_cash", "final_market_value", "total_traded_notional", "average_turnover_ratio", "initial_capital_turnover"]
    frame[fill_cols] = frame[fill_cols].fillna(0.0)
    return frame


def _simulate_one(model_id: str, horizon_id: str, policy: str, signals: pd.DataFrame, price_lookup: dict[tuple[str, str], float], next_date: dict[str, str | None], final_mark_date: str, initial_capital: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    cash = float(initial_capital)
    lots: list[Lot] = []
    trades: list[dict[str, Any]] = []
    equity_rows: list[dict[str, Any]] = []
    lot_id = 0
    signal_dates = sorted(signals["as_of_date"].unique().tolist())
    calendar_dates = sorted(set(next_date.values()) - {None})
    for signal_date in signal_dates:
        execution_date = next_date.get(signal_date)
        if execution_date is None:
            continue
        date_signals = signals[signals["as_of_date"] == signal_date]
        sell_set = sell_set_for_policy(date_signals, policy)
        cash, sold = _sell_lots(lots, price_lookup, execution_date, cash, reason="sell_pressure", tickers=sell_set)
        trades.extend(_trade_rows(model_id, horizon_id, policy, signal_date, execution_date, sold))
        cash, expired = _sell_expired_lots(lots, price_lookup, execution_date, cash)
        trades.extend(_trade_rows(model_id, horizon_id, policy, signal_date, execution_date, expired))
        top = date_signals[(date_signals["horizon_id"] == horizon_id) & (date_signals["side"] == "top")].sort_values("rank")
        if not top.empty:
            if horizon_id == "1d":
                current_value = cash + _market_value(lots, price_lookup, execution_date)
                target_tickers = set(top["canonical_ticker"].astype(str))
                cash, removed = _sell_lots(lots, price_lookup, execution_date, cash, reason="left_top10", tickers={lot.canonical_ticker for lot in lots if lot.canonical_ticker not in target_tickers})
                trades.extend(_trade_rows(model_id, horizon_id, policy, signal_date, execution_date, removed))
                for row in top.itertuples(index=False):
                    ticker = str(row.canonical_ticker)
                    price = price_lookup.get((ticker, execution_date))
                    if price is None or price <= 0:
                        continue
                    target_value = current_value * float(RANK_WEIGHTS[int(row.rank)])
                    existing = sum(lot.shares for lot in lots if lot.canonical_ticker == ticker)
                    delta_shares = target_value / price - existing
                    if abs(delta_shares) < 1e-12:
                        continue
                    if delta_shares < 0:
                        sell_value = -delta_shares * price
                        cash += sell_value
                        realized_pnl = _reduce_lots(lots, ticker, -delta_shares, price)
                        trades.append(_trade_row(model_id, horizon_id, policy, signal_date, execution_date, ticker, "sell", "rank_resize", -delta_shares, price, sell_value, realized_pnl=realized_pnl))
                    else:
                        cost = delta_shares * price
                        if cost > cash:
                            delta_shares = cash / price
                            cost = cash
                        if delta_shares > 0:
                            cash -= cost
                            lot_id += 1
                            lot = Lot(lot_id, model_id, horizon_id, ticker, delta_shares, signal_date, execution_date, price, None, int(row.rank))
                            lots.append(lot)
                            trades.append(_trade_row(model_id, horizon_id, policy, signal_date, execution_date, ticker, "buy", "rank_target", delta_shares, price, -cost, lot=lot))
            else:
                slice_cash = cash / float(HORIZON_DAYS[horizon_id])
                for row in top.itertuples(index=False):
                    ticker = str(row.canonical_ticker)
                    price = price_lookup.get((ticker, execution_date))
                    if price is None or price <= 0:
                        continue
                    budget = min(cash, slice_cash * float(RANK_WEIGHTS[int(row.rank)]))
                    if budget <= 0:
                        continue
                    shares = budget / price
                    cash -= budget
                    lot_id += 1
                    expiry = _advance_date(calendar_dates, execution_date, HORIZON_DAYS[horizon_id])
                    lot = Lot(lot_id, model_id, horizon_id, ticker, shares, signal_date, execution_date, price, expiry, int(row.rank))
                    lots.append(lot)
                    trades.append(_trade_row(model_id, horizon_id, policy, signal_date, execution_date, ticker, "buy", "horizon_slice", shares, price, -budget, lot=lot))
        equity_rows.append(_equity_row(model_id, horizon_id, policy, signal_date, execution_date, cash, lots, price_lookup))
    final_equity = cash + _market_value(lots, price_lookup, final_mark_date)
    holdings_rows = [_holding_row(model_id, horizon_id, policy, lot, price_lookup, final_mark_date) for lot in lots]
    summary = {"model_id": model_id, "horizon_id": horizon_id, "sell_policy": policy, "initial_capital": float(initial_capital), "final_equity": float(final_equity), "total_return": float(final_equity / initial_capital - 1.0), "trade_count": int(len(trades)), "open_lot_count": int(len(lots)), "final_mark_date": final_mark_date, "benchmark_claim": False, "trading_signal_approved": False}
    return trades, equity_rows, holdings_rows, summary


def _sell_lots(lots: list[Lot], price_lookup: dict[tuple[str, str], float], execution_date: str, cash: float, *, reason: str, tickers: set[str]) -> tuple[float, list[dict[str, Any]]]:
    if not tickers:
        return cash, []
    sold = []
    remaining = []
    for lot in lots:
        if lot.canonical_ticker in tickers:
            price = price_lookup.get((lot.canonical_ticker, execution_date))
            if price is None or price <= 0:
                remaining.append(lot)
                continue
            value = lot.shares * price
            cash += value
            sold.append({"ticker": lot.canonical_ticker, "shares": lot.shares, "price": price, "cash_effect": value, "reason": reason, "lot": lot, "realized_pnl": lot.shares * (price - lot.entry_price)})
        else:
            remaining.append(lot)
    lots[:] = remaining
    return cash, sold


def _sell_expired_lots(lots: list[Lot], price_lookup: dict[tuple[str, str], float], execution_date: str, cash: float) -> tuple[float, list[dict[str, Any]]]:
    sold = []
    remaining = []
    for lot in lots:
        if lot.expiry_date is not None and lot.expiry_date <= execution_date:
            price = price_lookup.get((lot.canonical_ticker, execution_date))
            if price is None or price <= 0:
                remaining.append(lot)
                continue
            value = lot.shares * price
            cash += value
            sold.append({"ticker": lot.canonical_ticker, "shares": lot.shares, "price": price, "cash_effect": value, "reason": "horizon_expiry", "lot": lot, "realized_pnl": lot.shares * (price - lot.entry_price)})
        else:
            remaining.append(lot)
    lots[:] = remaining
    return cash, sold


def _reduce_lots(lots: list[Lot], ticker: str, shares_to_remove: float, exit_price: float) -> float:
    remaining_remove = shares_to_remove
    realized_pnl = 0.0
    kept = []
    for lot in lots:
        if lot.canonical_ticker != ticker or remaining_remove <= 0:
            kept.append(lot)
            continue
        removed = min(lot.shares, remaining_remove)
        realized_pnl += removed * (exit_price - lot.entry_price)
        lot.shares -= removed
        remaining_remove -= removed
        if lot.shares > 1e-12:
            kept.append(lot)
    lots[:] = kept
    return float(realized_pnl)


def _trade_rows(model_id: str, horizon_id: str, policy: str, signal_date: str, execution_date: str, sold: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_trade_row(model_id, horizon_id, policy, signal_date, execution_date, row["ticker"], "sell", row["reason"], row["shares"], row["price"], row["cash_effect"], lot=row.get("lot"), realized_pnl=float(row.get("realized_pnl", 0.0))) for row in sold]


def _trade_row(model_id: str, horizon_id: str, policy: str, signal_date: str, execution_date: str, ticker: str, action: str, reason: str, shares: float, price: float, cash_effect: float, *, lot: Lot | None = None, realized_pnl: float = 0.0) -> dict[str, Any]:
    return {
        "model_id": model_id,
        "horizon_id": horizon_id,
        "sell_policy": policy,
        "signal_date": signal_date,
        "execution_date": execution_date,
        "canonical_ticker": ticker,
        "action": action,
        "reason": reason,
        "shares": float(shares),
        "price": float(price),
        "cash_effect": float(cash_effect),
        "lot_id": None if lot is None else int(lot.lot_id),
        "entry_signal_date": None if lot is None else lot.entry_signal_date,
        "entry_execution_date": None if lot is None else lot.entry_execution_date,
        "entry_price": None if lot is None else float(lot.entry_price),
        "expiry_date": None if lot is None else lot.expiry_date,
        "entry_rank": None if lot is None else int(lot.entry_rank),
        "realized_pnl": float(realized_pnl),
        "sell_pressure_reason": reason if action == "sell" and reason == "sell_pressure" else None,
        "benchmark_claim": False,
        "trading_signal_approved": False,
    }


def _equity_row(model_id: str, horizon_id: str, policy: str, signal_date: str, execution_date: str, cash: float, lots: list[Lot], price_lookup: dict[tuple[str, str], float]) -> dict[str, Any]:
    market_value = _market_value(lots, price_lookup, execution_date)
    return {"model_id": model_id, "horizon_id": horizon_id, "sell_policy": policy, "signal_date": signal_date, "execution_date": execution_date, "cash": float(cash), "market_value": float(market_value), "equity": float(cash + market_value), "open_lot_count": int(len(lots))}


def _holding_row(model_id: str, horizon_id: str, policy: str, lot: Lot, price_lookup: dict[tuple[str, str], float], final_mark_date: str) -> dict[str, Any]:
    mark = price_lookup.get((lot.canonical_ticker, final_mark_date), lot.entry_price)
    cost_basis = lot.shares * lot.entry_price
    market_value = lot.shares * mark
    return {
        "model_id": model_id,
        "horizon_id": horizon_id,
        "sell_policy": policy,
        "lot_id": int(lot.lot_id),
        "canonical_ticker": lot.canonical_ticker,
        "shares": float(lot.shares),
        "entry_signal_date": lot.entry_signal_date,
        "entry_execution_date": lot.entry_execution_date,
        "entry_price": float(lot.entry_price),
        "entry_rank": int(lot.entry_rank),
        "expiry_date": lot.expiry_date,
        "final_mark_date": final_mark_date,
        "final_mark_price": float(mark),
        "cost_basis": float(cost_basis),
        "market_value": float(market_value),
        "realized_pnl": 0.0,
        "unrealized_pnl": float(market_value - cost_basis),
        "total_pnl": float(market_value - cost_basis),
        "sell_pressure_reason": None,
    }


def _market_value(lots: list[Lot], price_lookup: dict[tuple[str, str], float], date: str) -> float:
    return float(sum(lot.shares * price_lookup.get((lot.canonical_ticker, date), lot.entry_price) for lot in lots))


def _next_calendar_date(calendar: list[str], date: str) -> str | None:
    for item in calendar:
        if item > date:
            return item
    return None


def _advance_date(calendar: list[str], start_date: str, days: int) -> str | None:
    if start_date not in calendar:
        return None
    index = calendar.index(start_date) + int(days)
    if index >= len(calendar):
        return None
    return calendar[index]


def _final_equity_svg(summary: pd.DataFrame) -> str:
    rows = summary.groupby(["model_id", "sell_policy"], sort=True)["final_equity"].mean().reset_index()
    values = [(f"{row.model_id} / {row.sell_policy}", float(row.final_equity)) for row in rows.itertuples(index=False)]
    max_value = max([value for _, value in values] + [1.0])
    width = 1100
    row_height = 24
    height = 70 + row_height * len(values)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', '<text x="20" y="28" font-family="Arial" font-size="18" font-weight="700">Final Equity By Model And Sell Policy</text>']
    for index, (label, value) in enumerate(values):
        y = 50 + index * row_height
        bar_width = 500 * value / max_value
        parts.append(f'<text x="20" y="{y + 13}" font-family="Arial" font-size="11">{_escape(label)}</text>')
        parts.append(f'<rect x="470" y="{y}" width="{bar_width:.2f}" height="15" fill="#2b6cb0" opacity="0.85"/>')
        parts.append(f'<text x="980" y="{y + 13}" font-family="Arial" font-size="11">{value:.2f}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def _render_markdown_report(manifest: dict[str, Any], summary: pd.DataFrame) -> str:
    best = summary.sort_values("final_equity", ascending=False).head(10)
    lines = ["# Stage 47 Lockbox Portfolio Simulation", "", f"Status: `{manifest['status']}`", "", "Historical lockbox diagnostic only. No trading advice or benchmark claim is approved.", "", "## Top Final Equity Rows", ""]
    lines.append(_markdown_table(best))
    lines.extend(["", "## Sell Policies", "", "- `one_d_bot10`: sell pressure from non-constant 1d bot10 only.", "- `none`: no signal-driven liquidation.", "- `botk_4_of_5`, `botk_3_of_5`, `botk_2_of_5`: liquidation only when the ticker appears in bot10 on at least the threshold number of horizons.", "", "## Non-Claims", "", "This is not a live forecast, buy/sell recommendation, portfolio advice, benchmark-improvement claim, or Stage 6 reinterpretation.", ""])
    return "\n".join(lines)


def _render_html_report(manifest: dict[str, Any], summary: pd.DataFrame) -> str:
    table = summary.sort_values("final_equity", ascending=False).to_html(index=False, escape=True)
    svg = Path(PROJECT_ROOT / manifest["outputs"]["final_equity_by_model_policy_svg"]).read_text(encoding="utf-8")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Stage 47 Lockbox Portfolio Simulation</title><style>body{{font-family:Arial,sans-serif;margin:32px}} table{{border-collapse:collapse;font-size:12px}} td,th{{border:1px solid #ddd;padding:4px 6px}}</style></head><body><h1>Stage 47 Lockbox Portfolio Simulation</h1><p>Historical lockbox diagnostic only. No trading advice, live forecast, benchmark claim, or Stage 6 reinterpretation is approved.</p>{svg}<h2>Summary</h2>{table}</body></html>"""


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "(no rows)"
    columns = list(frame.columns)
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in frame.itertuples(index=False):
        values = []
        for value in row:
            if isinstance(value, float):
                values.append(f"{value:.6f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _escape(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(_json_safe(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if not isinstance(value, (dict, list, tuple, str, bytes)):
        try:
            if pd.isna(value):
                return None
        except TypeError:
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
