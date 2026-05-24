# Benchmark Testing

Status: active-root benchmark-testing contract with Stage 6 serious benchmark reporting completed for the approved Stage 5 saved predictions and Stage 7C contextual-bandit diagnostics materialized on a new post-Stage-6-lockbox holdout. The Stage 6 result class remains `clean_null`; comparability remains `limitation_bearing` because provider-level Alpha Vantage article completeness is not claimed, an active split-adjustment method is not selected, and train-validation gaps are explicitly blocked by absent Stage 5 train predictions.

Governing refinement: `docs/Data_Separation_And_Overfitting_Control.md` is the active Option B contract for data separation, saved predictions, predeclared metrics, and overfitting diagnostics.

## Approved Benchmark Family

- Objective: test event-state incremental value beyond market-only baselines.
- Target: forward excess returns.
- Horizons: `1d`, `5d`, `10d`, `20d`, `60d`.
- Universe: top-50 liquid large-cap set for the first serious benchmark.
- Alignment: same-day as-of-close with after-hours and non-trading-day roll-forward.
- Evaluation: purged-plus-embargoed walk-forward plus final untouched lockbox.

## Required Artifact Packet

Every serious benchmark run must emit:

- Dataset version.
- Dataset manifest.
- Resolved config.
- Fold definitions and split manifest with purge/embargo row accounting.
- Preprocessing-fit manifest.
- Saved predictions.
- Metrics.
- Overfitting diagnostic report.
- Comparison summary.

## Current Stage 4 Split And Packet State

- Active split config exists at `configs/splits.yaml` and active artifact-packet config exists at `configs/artifact_packet.yaml`.
- `src/event_state_forecasting/split/` now includes approved executable Stage 4 lockbox, purged/embargoed split, and leakage-check code.
- `src/event_state_forecasting/benchmark/artifact_packet.py` and `src/event_state_forecasting/benchmark/runner.py` now implement pre-model packet validation and a gate-safe runner check.
- Stage 4 artifacts exist under `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/`.
- `scripts/validate_stage4_completion.py` validates the materialized Stage 4 artifact set.
- The Stage 4 pre-model packet passes. After Stage 6, the full serious-run packet passes because dataset, feature, split, preprocessing, saved-prediction, metric, diagnostic, and comparison-summary members exist.

## Current Stage 5 Model And Prediction State

- Active model config exists at `configs/models.yaml` with roster `phase1_top50_pragmatic_broader_sklearn_v1`.
- Stage 5 artifacts exist under `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/`.
- The Stage 5 artifact set has `8` model IDs, `360` model-fit records, `360` preprocessing-fit records, and `2088000` saved prediction rows.
- Saved predictions include development validation and lockbox rows only; they do not include train, purged, embargoed, or excluded rows.
- Stage 5 created no metrics, overfitting diagnostic report, comparison summary, benchmark runner result, or serious benchmark claim by itself.
- Stage 6 consumed the saved validation and lockbox predictions without changing the Stage 5 roster or rerunning model selection.

## Current Stage 6 Benchmark Reporting State

- Active evaluation config exists at `configs/evaluation.yaml`.
- Stage 6 artifacts exist under `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/`.
- The artifact set has `800` regression metric rows, `800` ranking diagnostic rows, and `800` paired comparison rows.
- The serious packet status is `passed` and the Stage 6 completion validator passes.
- Result class is `clean_null` under the predeclared `short_horizon_primary_3_v1` rule.
- Comparability classification is `limitation_bearing`, not invalidated.
- This is a serious benchmark result packet with a clean-null conclusion; it is not a trading profitability claim, provider-level article-completeness claim, or sentiment-string ablation claim.

## Current Stage 7C Contextual-Bandit Diagnostic State

- Active Stage 7 config exists at `configs/stage7_contextual_bandit.yaml`; the post-lockbox split config exists at `configs/stage7_splits_post_lockbox_2026-05-22.yaml`.
- Stage 7C implementation exists under `src/event_state_forecasting/stage7/` with CLI entry points `run_stage7_contextual_bandit.py` and `run_stage7_final_execution.py`.
- The approved Twelve Data update produced top-50 plus SPY raw files for requested end date `2026-05-22`; coverage audit status is `complete_observed_life_with_late_start_limitations` with no hard blockers and one CVX OHLC order anomaly handled only by derived cleaning policy.
- The Stage 7C post-lockbox diagnostic artifact exists under `data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout/`.
- The new Stage 7C holdout spans `2026-02-17` through `2026-02-25`, after the Stage 6 lockbox end `2026-02-13`; it has `22750` fold-specific context rows, `180180` policy-selection rows, and `4620` metric rows.
- Stage 7C outputs are diagnostics-only with `benchmark_claim=false`; they do not approve all-data final-execution training-output, live buy/sell signals, shorting, trading-profitability claims, real logged-policy IPW/DR claims, or Stage 6 reinterpretation.

## Metrics Policy

- Regression metrics are primary.
- Ranking metrics are mandatory secondary diagnostics.
- Metric lists must be predeclared before serious runs.
- Metrics must be computed from saved out-of-sample predictions and frozen labels.
- Single-split or single-metric wins are not sufficient for serious claims.
- Current Stage 6 primary regression metrics are RMSE, MAE, out-of-sample `R2`, and mean loss differences versus the selected strict market hurdle.
- Current Stage 6 ranking diagnostics are secondary only: Spearman rank IC, Kendall rank correlation, directional hit diagnostic, and top-minus-bottom spread.
- Current Stage 6 selected strict market hurdles are `market_elastic_net` for `1d`, `10d`, `20d`, and `60d`, and `market_ridge` for `5d`.

## Required Overfitting Diagnostics

- Train-to-validation performance gap by model family and horizon.
- Development-fold mean and standard deviation by metric and horizon.
- Percentage of development folds where the event-state branch improves over the market-only baseline.
- Percentage of approved horizons where the event-state branch improves over the market-only baseline.
- Validation-to-lockbox degradation by model and metric.
- Paired saved-prediction comparison against the market-only baseline where assumptions are satisfied.
- Multiple-comparison note across horizons, models, and diagnostics.
- Search-space summary for models, feature sets, horizons, metrics, and tuning attempts considered.

## Comparability Rules

- Top-100, top-500, provider changes, target changes, horizon changes, alignment changes, and evaluation changes are new benchmark families unless explicitly approved as comparable.
- Market-only and event-state runs must use identical rows, labels, splits, and evaluation windows for a valid incremental-value comparison.
- Learned preprocessing must be fit only on training rows for the active fold.
- The final lockbox must not be used for model selection, feature selection, clean-window selection, threshold selection, metric selection, or repeated debugging by result inspection.
- Raw data completion alone is not a benchmark result.

## Invalidation Triggers

- Provider stack change.
- Universe definition change.
- Target or horizon change.
- Split, purge, embargo, or lockbox change.
- Feature timestamp or alignment change.
- Dataset reconstruction that changes rows, labels, or provider coverage.
- Missing split manifest, preprocessing-fit manifest, saved-prediction row keys, or overfitting diagnostic report.
- Any detected train/validation/lockbox row collision, overlapping-label contamination, embargo misuse, or non-training preprocessing fit.

## Current Blockers

- Alpha Vantage provider-level article completeness remains unclaimed; truncation limitation flags stay part of the benchmark evidence.
- Active split-adjustment method remains unselected; Stage 2 used a derived CVX manifest without mutating raw Twelve Data values.
- Train-validation gap diagnostics remain explicitly blocked because Stage 5 intentionally saved validation and lockbox predictions only, not train predictions.
- API-key-bearing raw ledger handling must be sanitized or isolated before raw ledgers are committed or shared.
