# Usage Manual

Status: v1p0 smoke, XGBoost-only active workflow, validated raw-merge utility, and enhanced Stage 2-6 comparison usage manual

Updated: 2026-05-28

The previous detailed Stage 10C/v0p9 usage manual has been preserved separately by the user. This active file documents validated v1p0 local commands only.

## 1. Purpose

This file is the user-facing local usage manual for validated v1p0 smoke artifacts and commands.

It must not be read as evidence of a serious benchmark rerun, live forecast, service/API/dashboard, trading output, or Stage 6 reinterpretation.

## 2. Current Status

| Area | Status |
| --- | --- |
| v1p0 implementation | First-slice smoke implementation exists under `src/event_state_forecasting/v1p0/`. |
| v1p0 commands | Stage 17-25 XGBoost commands and the refreshed XGBoost-only Stage 35-40 closeout command exist and passed under `~/venvs/ai`; TSMixer commands remain historical diagnostics only and are not active next steps. |
| v1p0 artifact roots | Smoke root: `data/v1p0_first_slice_smoke/first_slice_smoke_v1/`. |
| v1p0 feature sidecars | Stage 17 feature root: `data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z/`. |
| v1p0 saved predictions | Stage 19 model root: `data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z/`. |
| v1p0 diagnostics | Stage 20 diagnostic root: `data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z/`. |
| v1p0 search freeze | Stage 21 result root: `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage21__xgboost_search_freeze__20260524T071500Z__src_6dff1bd__run_2a802f16/`. |
| v1p0 search results | Stage 22 result root: `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/`. |
| v1p0 frozen final | Stage 23 result root: `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80/`. |
| v1p0 overfit review | Stage 24 result root: `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80/`. |
| v1p0 uncertainty review | Stage 25 result root: `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_6dff1bd__run_689fbb80/`. |
| v1p0 final sprint | Refreshed XGBoost-only Stage 35-40 closeout exists as non-claiming current-branch evidence; older Stage 26-40 packets remain historical. |
| v1p0 report outputs | Smoke report: `data/v1p0_first_slice_smoke/first_slice_smoke_v1/report.html`. |
| v1p0 tests/validators | `python -m pytest tests/v1p0` should pass under `~/venvs/ai`; focused Stage 26-40/XGBoost-only closeout contracts are included. |
| Alpha Vantage raw merge | Non-destructive versioned merge utility exists for `data/raw/alphavantage/` plus `data/raw_zip2_extended_granularity/raw/alphavantage/`; validated run root: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/`. |
| Enhanced Stage 2-6 comparison | Non-destructive rerun from the merged Alpha Vantage root completed with new versioned Stage 2-6 roots and comparison artifacts; baseline and enhanced result classes both remain `clean_null`. |
| v0p9 artifacts | Historical/completed state only; do not relabel as v1p0. |
| Fixed XGBoost | Available in required venv `~/venvs/ai`; smoke summary records `status=available`. |

## 3. Non-Claims

This manual does not claim:

- live provider execution,
- canonical raw overwrite or hidden raw-source mutation,
- hidden Stage 2 through Stage 6 reruns,
- persisted inference packaging,
- new `forecast_candidate` semantics,
- a service, API, dashboard, or authentication boundary,
- trading signals, buy/sell outputs, price targets, or portfolio advice,
- Stage 6 reinterpretation,
- benchmark-comparability promotion.

## 4. Expected v1p0 Manual Sections

Fill these sections only after implementation and validation evidence exists.

| Future section | Required evidence before filling |
| --- | --- |
| Setup | Dependencies, environment variables, and local path assumptions validated for v1p0. |
| Command catalog | Implemented v1p0 CLIs or scripts with tests. |
| Artifact inventory | Versioned v1p0 output roots, manifests, schemas, and validation results. |
| Model-output guide | Saved-prediction or report artifacts with explicit row roles and non-claims. |
| Report guide | Static report outputs and report/data fidelity tests. |
| Troubleshooting | Observed v1p0 errors and validated recovery steps. |
| Maintenance checklist | Update rules for docs, memory, validators, and guidebook entries. |

## 5. Safe Current Commands

Use these for governance validation and the first v1p0 smoke path. Activate `~/venvs/ai` first; fixed XGBoost availability is validated there and should not be assumed outside that environment.

```bash
source ~/venvs/ai/bin/activate
python scripts/validate_agent_governance.py
python -m pytest tests/v1p0
python scripts/run_v1p0_first_slice_smoke.py
python scripts/build_v1p0_market_feature_sidecars.py
python scripts/run_v1p0_historical_market_baselines.py
python scripts/run_v1p0_full_diagnostic_baseline_gate.py
python scripts/freeze_v1p0_xgboost_search_space.py
python scripts/run_v1p0_xgboost_nested_search.py
python scripts/run_v1p0_xgboost_frozen_final_evaluation.py
python scripts/run_v1p0_xgboost_overfit_promotion_review.py
python scripts/run_v1p0_xgboost_block_bootstrap_uncertainty.py
python scripts/run_v1p0_xgboost_only_stage35_40_closeout.py
python scripts/run_v1p0_xgb_tsmixer_stratified_diagnostic.py
```

The smoke command writes toy-data outputs only. The Stage 17 feature-sidecar command writes historical market feature sidecars only. The Stage 19 baseline command writes fixed-model saved predictions and train diagnostics. The Stage 20 command computes diagnostics from saved predictions. The Stage 21 command freezes search-space and objective configuration only. The Stage 22 command runs development-only XGBoost search and writes trial artifacts without lockbox use. The Stage 23 command evaluates the frozen candidate once and preserves claim-review boundaries. The Stage 24 command records overfit evidence and conservative classification without approving positive claims. The Stage 25 command records moving-block bootstrap uncertainty and train-to-real-data gap diagnostics without approving positive claims. The XGBoost-only Stage 35-40 closeout command records current-branch diagnostics, report fidelity, claim review, and completion status around `market_xgboost_v2_frozen_final` while preserving `positive_claim_approved=false`. The XGBoost-vs-TSMixer diagnostic command is post-hoc diagnostics-only and exists to document why TSMixer is not active. Historical TSMixer commands remain available for reproducibility, but they are not part of the active XGBoost-only workflow. None of these commands call market/news providers, overwrite canonical raw data, reinterpret Stage 6, or create a positive benchmark claim.

## 5A. Validated Raw Merge Commands

Use these only for local raw-audit/merge maintenance. They do not call providers and do not overwrite `data/raw/alphavantage/`.

```bash
source ~/venvs/ai/bin/activate
python scripts/merge_alphavantage_news_raw_roots.py --dry-run
python scripts/merge_alphavantage_news_raw_roots.py
python scripts/validate_alphavantage_news_merge_output.py --run-root data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z
```

The validated 2026-05-28 merge wrote a separate ignored output root under `data/raw/alphavantage_merged_versions/`, retained `608238` merged feed rows across `1408` news files, and validated `608238` per-article provenance records. Canonical adoption or replacement of `data/raw/alphavantage/` still requires explicit approval.

## 5B. Enhanced Stage 2-6 Comparison Commands

Use these only for the validated local enhanced comparison path. They do not call providers, do not overwrite canonical raw data, and do not approve positive benchmark language.

```bash
source ~/venvs/ai/bin/activate
python scripts/run_enhanced_alphavantage_stage2_6_pipeline.py --json
python scripts/run_enhanced_alphavantage_stage2_6_pipeline.py --comparison-only --enhanced-stage2-root data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086 --enhanced-stage3-root data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1 --enhanced-stage6-root data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1 --json
python scripts/validate_enhanced_stage2_6_comparison.py --comparison-json data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/enhanced_vs_baseline_comparison.json
```

The validated enhanced rerun wrote Stage 2-6 roots with source digest `c82c06990ba7`, increased aligned news rows from `67840` to `166711`, and generated `enhanced_vs_baseline_comparison.json` plus `.md`. Both baseline and enhanced Stage 6 packets remain `clean_null` with comparability `limitation_bearing`; provider-level completeness, positive benchmark language, and benchmark-comparability promotion remain unapproved.

## 6. v1p0 Smoke Artifacts

| Path | Meaning |
| --- | --- |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_lag_features.csv` | Toy market lag/rolling feature sidecar output. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_lag_linear_predictions.csv` | Toy lag-linear saved predictions. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/metrics.csv` | Toy diagnostic metrics. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/strata.csv` | Toy stratified metrics. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/uncertainty.csv` | Toy date-clustered uncertainty table. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/report.html` | Static smoke report with non-claim caveats and source-labeled metrics, strata, and uncertainty table sections. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/saved_predictions.csv` | Combined toy saved predictions for lag-linear and fixed XGBoost when the required venv is active. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_xgboost_v1_fixed_predictions.csv` | Toy fixed-XGBoost saved predictions generated under `~/venvs/ai`. |
| `data/v1p0_first_slice_smoke/first_slice_smoke_v1/v1p0_first_slice_smoke_summary.json` | Smoke summary, including XGBoost status. |

## 7. v1p0 Stage 17 Feature Artifacts

| Path | Meaning |
| --- | --- |
| `data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z/market_lag_features.parquet` | Full historical v1p0 market lag/rolling feature sidecar for the selected `20260213` Stage 2 row universe. |
| `data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z/feature_manifest.json` | Feature manifest with source IDs, feature columns, null counts, digest, validation, and non-claims. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage17__market_features__20260524T062000Z__src_6dff1bd__run_e1bdb390/` | Stage 17 result-vault packet for feature-sidecar materialization. |

These artifacts are feature evidence only, not model evidence or benchmark-improvement evidence.

## 8. v1p0 Stage 19 Saved-Prediction Artifacts

| Path | Meaning |
| --- | --- |
| `data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z/saved_predictions.parquet` | Full historical saved predictions for `market_lag_linear_v1` and `market_xgboost_v1_fixed`, including train rows for diagnostics only. |
| `data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z/model_manifest.json` | Model manifest with prediction counts, fit counts, digest, lockbox policy, and non-claims. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage19__fixed_baselines__20260524T064500Z__src_6dff1bd__run_f5bfd7fa/` | Stage 19 result-vault packet for fixed baseline saved predictions. |

These artifacts are saved-prediction evidence only until Stage 20 metrics and diagnostics are computed.

## 9. v1p0 Stage 20 Diagnostic Artifacts

| Path | Meaning |
| --- | --- |
| `data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z/diagnostic_manifest.json` | Diagnostic manifest with counts, gate status, and non-claims. |
| `data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z/metrics.parquet` | Primary metrics by split role, fold, horizon, and model. |
| `data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z/train_validation_gaps.parquet` | Train-vs-validation gap diagnostics. |
| `data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z/strata_metrics.parquet` | No-news, truncation-risk, and article-count strata diagnostics. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage20__diagnostics__20260524T070000Z__src_6dff1bd__run_8a2ccf4f/` | Stage 20 result-vault packet. |

These diagnostics permit Stage 21 search-space freeze from development evidence only. They are not a promotion claim.

## 10. v1p0 Stage 21 Search-Freeze Artifacts

| Path | Meaning |
| --- | --- |
| `configs/xgboost_search_v1p0.yaml` | Frozen Stage 21 XGBoost search-space, budget, objective, stop-rule, and overfit-frontier config. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage21__xgboost_search_freeze__20260524T071500Z__src_6dff1bd__run_2a802f16/frozen_search_space.json` | Canonical frozen search-space payload with digest and non-claims. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage21__xgboost_search_freeze__20260524T071500Z__src_6dff1bd__run_2a802f16/search_space_manifest.json` | Stage 21 manifest with candidate, hurdle, objective, budgets, lockbox policy, and Stage 22 permission. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage21__xgboost_search_freeze__20260524T071500Z__src_6dff1bd__run_2a802f16/stage21_xgboost_search_space_freeze_report.md` | Human-readable Stage 21 freeze report. |

These artifacts are search-contract evidence only. They are not hyperparameter-search evidence, model-fit evidence, benchmark evidence, or promotion evidence.

## 11. v1p0 Stage 22 XGBoost Development-Search Artifacts

| Path | Meaning |
| --- | --- |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/search_manifest.json` | Stage 22 search manifest with 400/400 completed trials, best development trial, and lockbox policy. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/trial_ledger.parquet` | Trial ledger with one row per trial and objective components. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/trial_fold_metrics.parquet` | Train/validation fold-horizon metrics for all trials. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/trial_prediction_index.parquet` | Index of validation-only saved prediction files for all trials. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage22__xgboost_search__20260524T073000Z__src_6dff1bd__run_2a802f16/best_development_candidate_config.json` | Best development-selected config pending Stage 23 frozen final evaluation. |

These artifacts are development-search evidence only. They are not final benchmark evidence, not a lockbox result, and not a promotion claim.

## 12. v1p0 Stage 23 XGBoost Frozen-Final Artifacts

| Path | Meaning |
| --- | --- |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80/final_evaluation_manifest.json` | Stage 23 final-evaluation manifest for `market_xgboost_v2_frozen_final`. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80/saved_predictions.parquet` | Frozen-final saved predictions with train diagnostics, validation rows, lockbox rows, and targets for metric recomputation. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80/metrics.parquet` | Metrics computed from saved predictions. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage23__xgboost_frozen_final__20260524T083000Z__src_6dff1bd__run_689fbb80/hurdle_deltas.parquet` | Candidate-minus-fixed-XGBoost hurdle deltas for train, validation, and lockbox reporting. |

These artifacts are final-evaluation evidence only. They do not authorize promotion, positive conclusion language, Stage 6 reinterpretation, or benchmark-comparability promotion.

## 13. v1p0 Stage 24 XGBoost Overfit-Review Artifacts

| Path | Meaning |
| --- | --- |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80/review_manifest.json` | Stage 24 review manifest with overfit-frontier schema and candidate classification. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80/candidate_classification.json` | Conservative classification: `lockbox_reported_candidate`, `promotion_review_recommended=true`, `positive_claim_approved=false`. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80/overfit_frontier_summary.parquet` | Trial complexity/search-depth versus train/validation frontier table. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage24__xgboost_overfit_review__20260524T084500Z__src_6dff1bd__run_689fbb80/candidate_horizon_review.parquet` | Horizon-level validation/lockbox hurdle-delta review. |

These artifacts recommend later promotion review but do not approve positive claims or benchmark-comparability promotion.

## 14. v1p0 Stage 25 Block-Bootstrap Uncertainty Artifacts

| Path | Meaning |
| --- | --- |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_6dff1bd__run_689fbb80/uncertainty_manifest.json` | Stage 25 manifest with moving-block bootstrap config and uncertainty classification. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_6dff1bd__run_689fbb80/block_bootstrap_intervals.parquet` | Candidate-vs-fixed-XGBoost moving-block bootstrap intervals by split, horizon, and metric. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_6dff1bd__run_689fbb80/train_oos_generalization_gap_intervals.parquet` | Diagnostic-only train-vs-validation/lockbox gap intervals for overfit-pressure review. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage25__block_bootstrap_uncertainty__20260524T090500Z__src_6dff1bd__run_689fbb80/stage25_block_bootstrap_uncertainty_report.md` | Human-readable uncertainty and overfit-pressure report. |

These artifacts classify uncertainty as `supportive_nonclaim_uncertainty`, but `positive_claim_approved=false` remains in force.

## 15. v1p0 Stage 26-40 Final-Sprint Artifacts

| Path | Meaning |
| --- | --- |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage26__finbert_contract__20260525T100000Z__src_6dff1bd__run_8d49f671/finbert_source_cache_contract.json` | Frozen `ProsusAI/finbert` source/tokenizer/cache contract with title+summary normalization and license caution. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage27__finbert_article_cache__20260525T101500Z__src_6dff1bd__run_0767625d/article_finbert_cache.parquet` | Article-level FinBERT mean-token embeddings and sentiment logits/probabilities for 67,840 aligned articles. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage28__finbert_aggregation_sidecars__20260525T150000Z__src_6dff1bd__run_b2c43a8a/finbert_aggregation_manifest.json` | User-approved deterministic 128d event-level FinBERT aggregation sidecars: mean, recency, top-k, and count-recency. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage29__event_representation_gate__20260525T110500Z__src_6dff1bd__run_ad936935/event_representation_gate_manifest.json` | Event-only representation gate on 128d sidecars; selected `event_finbert_topk_v1` from validation evidence only. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage18__sequence_windows__20260525T145000Z__src_6dff1bd__run_052914ca/sequence_window_manifest.json` | Stage 18 materialized 20d and 60d sequence tensors for TSMixer. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage30__tsmixer_sequence_smoke__20260525T152000Z__src_6dff1bd__run_bdb60d04/tsmixer_smoke_manifest.json` | TSMixer smoke packet using real Stage 18 60d sequence tensors. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage31__tsmixer_fixed_multiseed_benchmark__20260525T153000Z__src_6dff1bd__run_9aa67b49/stage31_tsmixer_fixed_multiseed_benchmark_manifest.json` | Heavy 5-seed 60d fixed TSMixer evidence; Stage 32 optimization is not recommended without user override. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage32__tsmixer_optimization_overfit_control__20260525T160000Z__src_6dff1bd__run_54e692cf/stage32_tsmixer_optimization_manifest.json` | User-overridden heavy Optuna TSMixer optimization; 60/60 trials, 2 seeds, zero lockbox rows for optimization, tuned candidate rejected from development evidence. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage34__market_event_horizon_fusion__20260525T114500Z__src_6dff1bd__run_8d6ed544/market_event_fusion_manifest.json` | Market+event horizon fusion evidence classified `exploratory_only`. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage35__full_diagnostic_battery__20260525T120000Z__src_6dff1bd__run_01835475/full_diagnostic_manifest.json` | Full diagnostic battery across available candidates. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage39__final_benchmark_claim_review__20260525T125000Z__src_6dff1bd__run_fc51d717/final_claim_review_manifest.json` | Final claim review: no positive claim or comparability promotion approved. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage35__xgboost_only_diagnostic_battery__20260527T010000Z__src_6dff1bd__run_0d72db4b/xgboost_only_diagnostic_manifest.json` | Refreshed XGBoost-only diagnostic battery around `market_xgboost_v2_frozen_final`; TSMixer/fusion closed for current branch. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage39__xgboost_only_final_claim_review__20260527T015000Z__src_6dff1bd__run_4ba71f22/xgboost_only_final_claim_review_manifest.json` | Refreshed XGBoost-only final claim review: `positive_claim_approved=false`, `benchmark_comparability_promotion_approved=false`. |
| `data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage40__xgboost_only_completion_gate__20260527T020000Z__src_6dff1bd__run_2bd1eee0/xgboost_only_completion_manifest.json` | Refreshed XGBoost-only completion gate and next-scope approval list. |
| `docs/v1p0_final_sprint/Final_v1p0_Sprint_Report.md` | Stage 26-40 status report and next-scope gate. |

These artifacts remain local research artifacts. They do not approve live forecasts, trading outputs, services, provider completeness, Stage 6 reinterpretation, or positive benchmark-improvement language. The current refreshed closeout is XGBoost-only and does not consume TSMixer, XGBoost+TSMixer ensemble, or market-event fusion as active candidates.

As of the current workflow decision and refreshed closeout, TSMixer and market-event fusion are not active next steps. Reopening them requires explicit future approval.

## 16. Pointer Files

| File | Purpose |
| --- | --- |
| `ProjectDefinition.md` | v1p0 project definition and non-implementation boundary. |
| `ArchitecturalDesignDecisions.md` | Active v1p0 decisions. |
| `Architecture_Map.md` | v1p0 architecture and file-flow plan. |
| `Complete_guidebook.txt` | Detailed v1p0 guidebook. |
| `ResearchTruth.md` | Implemented truth and non-claims. |
| `docs/agent/agent_log/Current_State.md` | Operational memory. |
| `docs/v1p0_final_sprint/Final_v1p0_Sprint_Report.md` | Ordered final-sprint evidence and prompt-status record. |

## 17. Completion Rule

Do not expand this manual beyond validated local commands. Serious v1p0 benchmark usage requires full feature/model/artifact validation against real benchmark artifacts and explicit approval for reruns.
