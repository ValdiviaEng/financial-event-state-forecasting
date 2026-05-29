from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = PROJECT_ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def test_stage48_frozen_tsmixer_mixer_contract_forbids_direct_tsmixer_tuning() -> None:
    module = _load_script("run_updated_dataset_frozen_tsmixer_horizon_mixer.py")
    contract = module.frozen_tsmixer_horizon_mixer_contract()

    assert contract["trial_count"] >= 800
    assert contract["base_model_policy"]["tsmixer_direct_tuning_allowed"] is False
    assert contract["base_model_policy"]["tsmixer_retraining_allowed"] is False
    assert contract["base_model_policy"]["tsmixer_architecture_status"] == "stale_mean_pooling_readout_not_corrected"
    assert contract["meta_training_policy"]["can_select_xgboost_only_per_horizon"] is True
    assert contract["meta_training_policy"]["lockbox_rows_used_for_tuning"] == 0
    assert "no_tsmixer_training_or_tuning_executed" in contract["non_claims"]


def test_stage47_rank_builder_fold_means_and_skips_constant_horizons() -> None:
    module = _load_script("run_updated_dataset_lockbox_portfolio_simulation.py")
    rows = []
    for fold_id, offset in [("fold_001", 0.0), ("fold_002", 0.2)]:
        for ticker, prediction in [("AAA", 1.0 + offset), ("BBB", 0.5 + offset), ("CCC", 0.1 + offset)]:
            rows.append(_prediction_row("model", ticker, "2026-01-02", "1d", fold_id, prediction))
        for ticker in ["AAA", "BBB", "CCC"]:
            rows.append(_prediction_row("model", ticker, "2026-01-02", "5d", fold_id, 0.7))

    signals = module.build_rank_signals(pd.DataFrame(rows))

    assert set(signals["horizon_id"]) == {"1d"}
    top = signals[(signals["side"] == "top") & (signals["rank"] == 1)].iloc[0]
    assert top["canonical_ticker"] == "AAA"
    assert top["fold_mean_prediction"] == 1.1


def test_stage47_sell_policy_uses_requested_botk_thresholds() -> None:
    module = _load_script("run_updated_dataset_lockbox_portfolio_simulation.py")
    signals = pd.DataFrame(
        [
            {"model_id": "m", "as_of_date": "2026-01-02", "horizon_id": horizon, "side": "bot", "rank": 1, "canonical_ticker": "AAA"}
            for horizon in ["1d", "5d", "10d", "20d"]
        ]
        + [
            {"model_id": "m", "as_of_date": "2026-01-02", "horizon_id": horizon, "side": "bot", "rank": 2, "canonical_ticker": "BBB"}
            for horizon in ["5d", "10d", "20d"]
        ]
        + [
            {"model_id": "m", "as_of_date": "2026-01-02", "horizon_id": "60d", "side": "bot", "rank": 3, "canonical_ticker": "CCC"}
        ]
    )

    assert module.sell_set_for_policy(signals, "one_d_bot10") == {"AAA"}
    assert module.sell_set_for_policy(signals, "none") == set()
    assert module.sell_set_for_policy(signals, "botk_4_of_5") == {"AAA"}
    assert module.sell_set_for_policy(signals, "botk_3_of_5") == {"AAA", "BBB"}
    assert module.sell_set_for_policy(signals, "botk_2_of_5") == {"AAA", "BBB"}


def test_stage47_diagnostics_cover_drawdown_exposure_turnover_and_allocation() -> None:
    module = _load_script("run_updated_dataset_lockbox_portfolio_simulation.py")
    group = {"model_id": "m", "horizon_id": "1d", "sell_policy": "none"}
    equity = pd.DataFrame(
        [
            {**group, "signal_date": "2026-01-02", "execution_date": "2026-01-03", "cash": 80.0, "market_value": 20.0, "equity": 100.0, "open_lot_count": 1},
            {**group, "signal_date": "2026-01-03", "execution_date": "2026-01-04", "cash": 70.0, "market_value": 20.0, "equity": 90.0, "open_lot_count": 1},
        ]
    )
    trades = pd.DataFrame(
        [
            {**group, "execution_date": "2026-01-03", "action": "buy", "cash_effect": -20.0},
            {**group, "execution_date": "2026-01-04", "action": "sell", "cash_effect": 5.0},
        ]
    )
    holdings = pd.DataFrame([{**group, "canonical_ticker": "AAA", "market_value": 20.0, "cost_basis": 18.0, "unrealized_pnl": 2.0}])
    summary = pd.DataFrame([{**group, "initial_capital": 100.0, "final_equity": 90.0, "total_return": -0.1, "trade_count": 2, "open_lot_count": 1, "final_mark_date": "2026-01-04", "benchmark_claim": False, "trading_signal_approved": False}])

    drawdown, exposure, turnover, allocation, enriched = module.build_diagnostic_tables(trades, equity, holdings, summary, 100.0)

    assert drawdown["drawdown_pct"].min() == -0.1
    assert exposure["gross_exposure_ratio"].iloc[0] == 0.2
    assert turnover["traded_notional"].sum() == 25.0
    assert allocation["final_weight"].iloc[0] == 20.0 / 90.0
    assert enriched["max_drawdown_pct"].iloc[0] == -0.1
    assert enriched["initial_capital_turnover"].iloc[0] == 0.25


def _prediction_row(model_id: str, ticker: str, date: str, horizon: str, fold: str, prediction: float) -> dict[str, object]:
    return {
        "model_id": model_id,
        "canonical_ticker": ticker,
        "as_of_date": date,
        "horizon_id": horizon,
        "fold_id": fold,
        "split_role": "lockbox",
        "prediction": prediction,
    }
