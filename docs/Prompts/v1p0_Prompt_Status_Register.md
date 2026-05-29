# v1p0 Prompt Status Register

Status: active prompt execution status and rerun register.

Updated: 2026-05-29

## Purpose

This register tracks the current execution status of every v1p0 prompt after the Stage 16-40 prompt hardening pass. Prompt files hold the current execution specifications; this file records whether existing artifacts satisfy those prompts, whether a prompt needs rerun or user decision, and which downstream stages are invalidated by changes.

## Status Rules

- `completed_smoke_only`: first-slice smoke evidence exists, but no serious benchmark claim is created.
- `completed_current`: existing artifacts satisfy the current prompt enough for the present branch unless upstream inputs change.
- `completed_pre_hardening_reviewed`: existing artifacts were created before prompt hardening; no rerun is currently required for the XGBoost branch, but rerun is required if upstream evidence changes.
- `needs_user_decision`: execution must stop and ask before continuing.
- `needs_run`: no valid completed artifact exists under the current prompt.
- `needs_rerun`: an old artifact exists but does not satisfy the hardened prompt or is stale due to dependencies.
- `stale_if_dependency_changes`: current artifact is usable only if listed dependencies are unchanged.
- `cancelled_current_branch`: prompt/artifact may remain historical evidence, but the current user-selected workflow does not consume it.

## Current Register

| Stage | Prompt | Current status | Rerun or adjustment note | Cascade note |
| --- | --- | --- | --- | --- |
| 00 | `v1p0_Stage00_Governance_Context_Readiness.md` | completed_smoke_only | No rerun needed unless governance context changes. | Supports all later prompts. |
| 01 | `v1p0_Stage01_Reuse_Vs_Rewrite_Audit.md` | completed_smoke_only | No rerun needed unless reuse policy changes. | v0p9 remains reference-only. |
| 02 | `v1p0_Stage02_Version_Manifest_Contract.md` | completed_smoke_only | No rerun needed unless manifest naming/versioning changes. | Registry/model tests depend on this. |
| 03 | `v1p0_Stage03_Sidecar_Feature_Registry.md` | completed_smoke_only | No rerun needed unless feature registry dependencies change. | Later model IDs depend on registry integrity. |
| 04 | `v1p0_Stage04_Market_Feature_Contract.md` | completed_smoke_only | No rerun needed unless market feature contract changes. | Stage 05/17 feature builders depend on this. |
| 05 | `v1p0_Stage05_Market_Feature_Builder.md` | completed_smoke_only | No rerun needed for smoke; production sidecars are Stage 17. | Toy feature evidence only. |
| 06 | `v1p0_Stage06_Split_Label_Compatibility.md` | completed_smoke_only | No rerun needed for smoke. | Serious compatibility is Stage 16. |
| 07 | `v1p0_Stage07_Lag_Linear_Baseline.md` | completed_smoke_only | No rerun needed for smoke; historical baseline is Stage 19. | Toy model evidence only. |
| 08 | `v1p0_Stage08_Fixed_XGBoost_Baseline.md` | completed_smoke_only | No rerun needed for smoke; historical fixed XGBoost is Stage 19. | Confirms venv XGBoost availability only. |
| 09 | `v1p0_Stage09_Prediction_Registry_Validation.md` | completed_smoke_only | No rerun needed unless prediction schema changes. | Later saved-prediction schema inherits this. |
| 10 | `v1p0_Stage10_Diagnostics_Core.md` | completed_smoke_only | No rerun needed for smoke; serious diagnostics are Stage 20/35. | Toy diagnostics only. |
| 11 | `v1p0_Stage11_Stratified_Metrics.md` | completed_smoke_only | No rerun needed for smoke. | Serious strata diagnostics are Stage 20/35. |
| 12 | `v1p0_Stage12_Uncertainty_Evidence.md` | completed_smoke_only | No rerun needed for smoke; block bootstrap is Stage 25. | Toy date-clustered uncertainty only. |
| 13 | `v1p0_Stage13_Report_Clarity_Fidelity.md` | completed_smoke_only | No rerun needed for smoke. | Full packet is Stage 37. |
| 14 | `v1p0_Stage14_Integrated_Evidence_Review.md` | completed_smoke_only | No rerun needed unless first-slice evidence changes. | First-slice closeout only. |
| 15 | `v1p0_Stage15_Full_Run_Governance_And_Result_Vault.md` | completed_current | No rerun needed unless result-vault convention changes. | Defines serious result packet layout. |
| 16 | `v1p0_Stage16_Historical_Artifact_Compatibility_Gate.md` | completed_pre_hardening_reviewed | No rerun needed for current XGBoost chain unless artifact roots or compatibility policy change. | Blocks Stage 17+ if changed. |
| 17 | `v1p0_Stage17_Production_Market_Feature_Sidecars.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 16 source chain or feature policy changes. | Changes invalidate Stage 19-25 and market inputs to Stage 34+. |
| 18 | `v1p0_Stage18_Sequence_Window_Materialization.md` | completed_current | Materialized 20d and 60d sequence tensors on 2026-05-25 with validation passed. | New Stage 18 artifact feeds Stage 30-31; old deferred record is superseded for TSMixer. |
| 19 | `v1p0_Stage19_Historical_Lag_Linear_And_Fixed_XGBoost_Benchmark.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 17 features change. | Feeds Stage 20-25 and market hurdle comparisons. |
| 20 | `v1p0_Stage20_Full_Diagnostic_Baseline_Gate.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 19 predictions or diagnostic policy changes. | Feeds Stage 21 objective freeze. |
| 21 | `v1p0_Stage21_XGBoost_Search_Space_And_Objective_Freeze.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 20 policy or search objective changes. | Changes invalidate Stage 22-25. |
| 22 | `v1p0_Stage22_XGBoost_Nested_Random_And_Optuna_Search.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 21 config changes. | Changes invalidate Stage 23-25. |
| 23 | `v1p0_Stage23_XGBoost_Frozen_Final_Evaluation.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 22 candidate changes. | Changes invalidate Stage 24-25 and XGBoost claim review. |
| 24 | `v1p0_Stage24_XGBoost_Overfit_Frontier_And_Promotion_Review.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 23 metrics or classification policy changes. | Feeds Stage 25 and final diagnostics. |
| 25 | `v1p0_Stage25_Block_Bootstrap_Uncertainty.md` | completed_pre_hardening_reviewed | No rerun needed unless Stage 23/24 or bootstrap policy changes. | XGBoost evidence chain is complete through Stage 25. |
| 26 | `v1p0_Stage26_FinBERT_Source_License_And_Cache_Contract.md` | completed_current | Contract reused and validated; no rerun needed unless FinBERT model, revision, text scope, or license policy changes. | This is FinBERT, not XGBoost. |
| 27 | `v1p0_Stage27_FinBERT_Article_Embedding_Cache.md` | completed_current | Cache reused and validated; no rerun needed unless Stage 26 contract changes. | Feeds Stage 28. |
| 28 | `v1p0_Stage28_FinBERT_Aggregation_Ablations.md` | completed_current | User selected 128d rerun with diagnostics; Stage 28 reran with deterministic 128-d projection. | Stage 29 reran against the new 128d sidecars. |
| 29 | `v1p0_Stage29_Event_Representation_Benchmark_Gate.md` | completed_current | Reran using the 128d Stage 28 sidecars; selected `event_finbert_topk_v1` from validation only. | Feeds future Stage 34 rerun. |
| 30 | `v1p0_Stage30_TSMixer_Sequence_Dataset_And_Smoke.md` | completed_current | Reran using real Stage 18 60d sequence tensors; old tabular-substitute smoke is superseded. | Enabled Stage 31. |
| 31 | `v1p0_Stage31_TSMixer_Fixed_Multiseed_Benchmark.md` | completed_current | Heavy 5-seed 60d fixed TSMixer benchmark completed; best validation weighted delta vs market XGBoost was positive and both-metric rate was 0.0222. | Historical rejection evidence only for the current XGBoost-only branch. |
| 32 | `v1p0_Stage32_TSMixer_Optimization_And_Overfit_Control.md` | completed_current | User explicitly overrode Stage 31 and selected heavy Optuna; Stage 32 completed 60/60 trials with 2 seeds, zero lockbox rows for optimization, and rejected the tuned candidate from development evidence. | Tuned TSMixer must not feed downstream work; TSMixer is closed for the active XGBoost-only branch. |
| 33 | `v1p0_Stage33_Market_Ensemble_Horizon_Meta.md` | cancelled_current_branch | User selected an XGBoost-only path after Stage 31-32 and ad-hoc diagnostics showed TSMixer underperformed as a regression model. | XGBoost+TSMixer ensemble is not an active next step. |
| 34 | `v1p0_Stage34_Market_Event_Horizon_Fusion.md` | cancelled_current_branch | Existing fusion remains historical exploratory evidence, but model-only XGBoost is the active branch. | Do not feed active XGBoost-only final review unless the user later reopens event/fusion scope. |
| 35 | `v1p0_Stage35_Full_Diagnostic_Battery_And_Error_Analysis.md` | completed_current | Refreshed as an XGBoost-only diagnostic closeout using Stage 21-25 evidence; TSMixer, TSMixer ensembles, and market-event fusion are explicitly excluded from the active candidate roster. | Feeds refreshed Stage 36/37/39. |
| 36 | `v1p0_Stage36_Accuracy_Overfit_Frontier_Report.md` | completed_current | Refreshed as XGBoost-only frontier evidence after Stage 35 XGBoost-only diagnostics. | Feeds refreshed Stage 37/39. |
| 37 | `v1p0_Stage37_Report_Visualization_Fidelity_Full_Packet.md` | completed_current | Refreshed after XGBoost-only Stage 35/36 outputs. | Feeds refreshed Stage 39. |
| 38 | `v1p0_Stage38_Documentation_Truth_Consistency_Audit.md` | completed_current | Refreshed after the XGBoost-only branch decision and Stage 35-37 closeout packets. | Feeds refreshed Stage 39/40. |
| 39 | `v1p0_Stage39_Final_Benchmark_Claim_Review.md` | completed_current | Refreshed for the current XGBoost-only branch; result classification is `xgboost_only_lockbox_reported_nonclaim`, with positive claim and comparability promotion unapproved. | Controls current final language. |
| 40 | `v1p0_Stage40_V1p0_Completion_And_Next_Scope_Gate.md` | completed_current | Refreshed XGBoost-only completion gate recorded with next-scope approval list. | Final completion gate for the active branch. |
| 47 | `v1p0_Stage47_Lockbox_Portfolio_Simulation.md` | completed_current | Historical lockbox-only portfolio simulation completed using Stage 43 XGBoost, the user-approved current frozen Stage 44 TSMixer diagnostic input, and the newly tuned no-direct-TSMixer Stage 48 horizon mixer; latest run includes drawdown, exposure, turnover, allocation, and lot-PnL diagnostics. | Post-selection diagnostic only; no trading/product/claim scope. |

## Immediate Execution Boundary

- XGBoost-specific serious stages are Stage 21 through Stage 25; they are already completed and do not currently need rerun unless their upstream configs change.
- Stage 26 is FinBERT source/license/cache contract, not an XGBoost stage.
- User clarified on 2026-05-25 that the requested execution boundary is XGBoost through Stage 25.
- XGBoost Stage 21-25 validation after the status update passed with focused tests (`14 passed`), manifest-chain validation (`XGBOOST_STAGE21_25_ARTIFACT_CHAIN_OK`), and status-register validation (`XGBOOST_STATUS_REGISTER_OK stages=21-25`).
- 2026-05-25 continuation approval executed Stage 26 through Stage 31 with user-selected 128d FinBERT projection and heavy 5-seed 60d TSMixer.
- 2026-05-25 user explicitly overrode Stage 31 and selected the heavy Stage 32 Optuna contract. Stage 32 completed 60/60 trials with 2 seeds, used zero lockbox rows for optimization, and rejected the tuned TSMixer candidate from development evidence.
- 2026-05-27 user selected the active path forward: disregard TSMixer and continue with an XGBoost-only model workflow. Stage 33 and Stage 34 are therefore cancelled for the current branch, and the next executable workflow is an XGBoost-only Stage 35-40 closeout using Stage 21-25 evidence.
- 2026-05-27 refreshed XGBoost-only Stage 35-40 closeout completed via `scripts/run_v1p0_xgboost_only_stage35_40_closeout.py`; `positive_claim_approved=false` and `benchmark_comparability_promotion_approved=false` remain in force.
- 2026-05-29 corrected the TSMixer readout contract from stale mean-time pooling to flattened time-feature readout. Prior TSMixer-derived Stage 42, updated Stage 44, and updated Stage 45 meta evidence must be treated as stale until rerun with the corrected architecture; updated Stage 43 XGBoost evidence is not affected by this algorithm correction.
- 2026-05-29 user rejected the estimated 23-hour corrected TSMixer tuning run and instructed that no direct TSMixer tuning is allowed; the current frozen best Stage 44 TSMixer artifact may be used as a diagnostic input only.
- 2026-05-29 Stage 48 frozen-TSMixer horizon mixer completed 800/800 meta/mixer trials with zero lockbox rows used for tuning and no TSMixer training/tuning.
- 2026-05-29 Stage 47 lockbox portfolio simulation completed across Stage 43 XGBoost, current frozen Stage 44 TSMixer diagnostic input, and the Stage 48 mixed model for sell policies `one_d_bot10`, `none`, `botk_4_of_5`, `botk_3_of_5`, and `botk_2_of_5`; latest result root is `v1p0__phase1_top50_updated_av__stage47__lockbox_portfolio_simulation__20260529T095157Z__src_6dff1bd__run_8317929b/`.

## Non-Claims

This register is operational status only. It does not approve silent deferrals, approve positive benchmark claims, promote comparability, reinterpret Stage 6, call live providers, mutate raw data, or create trading/product scope.
