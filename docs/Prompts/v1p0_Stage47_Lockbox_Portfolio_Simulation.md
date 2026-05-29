# v1p0 Stage 47 Prompt: Lockbox Portfolio Simulation

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Build and run a historical, lockbox-only, non-claim portfolio simulation across every valid best individual model and the best valid mixed model. The output is a counterfactual diagnostic artifact only, not a trading system, investment recommendation, benchmark promotion, or Stage 6 reinterpretation.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for Stage 47 simulation policy, non-claim boundaries, stale-model guards, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for the selected XGBoost, TSMixer, and horizon-meta model roadmap.
- Read `docs/Prompts/v1p0_Prompt_Status_Register.md`, Stage 43 through Stage 46 manifests, and `ResearchTruth.md` before selecting model inputs.
- Treat Stage 43 `updated_av_xgboost_event_market_optuna_v1` as the current valid updated Alpha Vantage individual-model evidence.
- Treat Stage 44 TSMixer as a current frozen diagnostic input only under the 2026-05-29 owner override that forbids direct TSMixer tuning; do not describe it as corrected-architecture evidence.
- Treat Stage 45 XGBoost+TSMixer meta artifacts as stale historical evidence; use a newly tuned frozen-TSMixer mixer/meta artifact if mixed-model simulation is requested.

## Required Inputs

- Stage 43 `best_model_predictions.parquet` for `updated_av_xgboost_event_market_optuna_v1`.
- Current frozen TSMixer best-individual prediction packet for `updated_av_tsmixer_event_market_optuna_v1_seed_mean`, clearly flagged as diagnostic-only stale-readout evidence with no direct TSMixer tuning or retraining in this stage.
- Best mixed-model prediction packet from the no-direct-TSMixer-tuning horizon mixer, if available.
- Updated Alpha Vantage Stage 3 `market_features.parquet` with `market_open` and `market_close`.
- Stage 46 algorithm-correction audit manifest to enforce stale-artifact rejection.
- User-approved initial capital of `100000` and the Stage 47 portfolio policy recorded in the decision docs.

## Candidate Roster Policy

- The intended roster is all valid best individual models plus the best valid mixed model on the same updated Alpha Vantage lockbox and price universe.
- Best individual models currently include the valid Stage 43 XGBoost model and the user-approved current frozen Stage 44 TSMixer diagnostic input.
- The best mixed model is the newly tuned no-direct-TSMixer-tuning horizon mixer when available.
- Do not run stale Stage 45 meta predictions as the final mixed model.
- If a required roster member is absent or schema-incompatible, record it as `blocked_missing_or_schema_incompatible` and stop before calling the roster complete.
- Do not substitute historical v0p9 or prior benchmark-family predictions unless the user explicitly approves a separate aligned-roster simulation.

## Signal Construction

- Filter predictions to `split_role == "lockbox"`.
- Collapse duplicate fold predictions by fold-mean over `fold_id` for each `model_id`, `canonical_ticker`, `as_of_date`, and `horizon_id`.
- Rank per `model_id`, `as_of_date`, and `horizon_id` by fold-mean prediction, descending for top-k and ascending for bot-k.
- Skip any model/date/horizon where the cross-section is constant after fold-mean aggregation.
- Do not fabricate tie-broken top-k or bot-k lists for constant/no-signal horizons.
- Emit top10 and bot10 lists for diagnostics, but liquidation pressure is defined separately below.

## Portfolio Policy

- Initial capital is `100000`.
- The portfolio is long-only with fractional shares.
- Exclude transaction costs, slippage, taxes, dividends, shorting, leverage, and borrowing.
- Execute buys, sells, resizes, expiries, and final forced exits at `market_open` on the next available trading day when one exists.
- Mark final remaining holdings to the last available lockbox date's `market_open` when no next trading-day open exists.
- Use rank target weights: rank `1` gets `22%`, rank `2` gets `18%`, rank `3` gets `15%`, rank `4` gets `12%`, rank `5` gets `8%`, and ranks `6` through `10` get `5%` each.
- For the `1d` horizon, rebalance to the current top10 target weights on each signal date when a non-constant 1d top10 exists.
- For longer horizons, use the same rank target weights but spend only `1 / horizon_days` of available cash per rebalance slice.
- Track horizon lots independently so `5d`, `10d`, `20d`, and `60d` entries, expiries, and diagnostics do not overwrite one another.
- If a held ticker appears on neither top10 nor sell-pressure bot-k, hold the existing lot until horizon expiry.

## Sell-Pressure Policy

- Sell pressure is always `1d` bot-k only.
- A held ticker in any horizon portfolio may be liquidated when that same model's current non-constant `1d` bot-k list contains the ticker.
- Non-1d bot-k lists, including `5d`, `10d`, `20d`, and `60d`, are diagnostics-only and must not trigger liquidation.
- If the `1d` horizon is constant or skipped for a model/date, there is no bot-k sell pressure for that model/date.
- This rule intentionally avoids using a longer-horizon bot-k flag as a near-term sell instruction.

## Required Outputs

- Stage 47 result root under `data/v1p0_full_results/` using the standard run-id convention.
- Simulation manifest with roster status, model artifact digests, stale-artifact checks, policy parameters, and non-claims.
- Run manifest and human-readable report.
- Fold-mean signal table and top10/bot10 rank-list tables.
- Trade ledger with order date, execution date, model, horizon, ticker, action, reason, shares, price, cash effect, and non-claim flags.
- Holdings or lot ledger with horizon, open date, expiry date, current value, realized PnL, unrealized PnL, and sell-pressure reason when applicable.
- Equity curve, drawdown table, exposure table, turnover table, allocation diagnostics, and final summary JSON.
- Roster blocker table for any best individual or mixed model that cannot be simulated.

## Success Measurements

- Every valid best individual model and best valid mixed model is simulated, or explicitly blocked with a missing/schema reason.
- Stage 44 current frozen TSMixer use is flagged as diagnostic-only; Stage 45 stale meta artifacts are rejected as final mixed-model inputs unless explicitly superseded by a newly tuned frozen-TSMixer mixer.
- Fold-mean aggregation removes duplicate lockbox fold rows before ranking.
- Constant/no-signal horizons are skipped and never tie-broken into artificial rankings.
- Non-1d bot-k lists never cause sells; only non-constant `1d` bot-k lists can trigger sell pressure.
- Trade ledgers reconcile to cash, holdings, and equity-curve outputs.
- No output upgrades the evidence into trading advice, a benchmark claim, or Stage 6 reinterpretation.

## Blocking And User Questions

- Block and ask if the candidate roster is incomplete and the user has not approved a partial/stale-blocked simulation.
- Block and ask before rerunning TSMixer training, rerunning the mixed model, or running any job with estimated runtime of one hour or more.
- Block and ask if price coverage lacks required `market_open` values beyond the known final-date mark convention.
- Block and ask if the user requests stale Stage 44 or Stage 45 artifacts to be treated as active evidence.
- Block and ask before adding costs, slippage, taxes, whole-share rounding, shorting, leverage, or live/scheduled semantics.

## Cascade Handling

- Any corrected TSMixer rerun or mixed-model rerun invalidates the Stage 47 candidate roster and requires the simulation to be rerun for all valid roster members.
- Any model-selection, lockbox-split, price-source, ranking, sell-pressure, or cost-assumption change invalidates Stage 47 outputs.
- Stage 47 does not invalidate Stage 39/40 claim review because it is a separate non-claim diagnostic unless someone attempts to use it for claims.
- If Stage 47 is later cited in public reports, rerun documentation truth and claim-language checks first.

## Required Tests And Validation

- Contract tests for the Stage 47 prompt and decision-doc policy.
- Unit tests for fold-mean aggregation, constant-horizon skip behavior, and deterministic ranking.
- Unit tests proving non-1d bot-k lists do not trigger sells and `1d` bot-k can trigger sells across all active horizon lots for the same model.
- Reconciliation tests for trade ledger, holdings ledger, cash, market value, and equity curve.
- Manifest tests for model roster completeness, stale-artifact rejection, non-claims, and artifact path provenance.
- Focused tests before full-suite tests under `source ~/venvs/ai/bin/activate`.

## Completion Criteria

- Stage 47 is complete only when the simulation artifacts exist, all valid roster members have been handled, stale roster members are explicitly blocked, tests pass, and the report preserves non-claim wording.

## Non-Claims

Stage 47 outputs are historical lockbox diagnostics only. They are not buy/sell recommendations, portfolio advice, live forecasts, price targets, benchmark-improvement claims, benchmark-comparability promotions, or Stage 6 reinterpretations.
