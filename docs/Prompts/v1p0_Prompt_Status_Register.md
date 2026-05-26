# v1p0 Prompt Status Register

Status: active prompt execution status and rerun register.

Updated: 2026-05-25

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
| 31 | `v1p0_Stage31_TSMixer_Fixed_Multiseed_Benchmark.md` | completed_current | Heavy 5-seed 60d fixed TSMixer benchmark completed; best validation weighted delta vs market XGBoost was positive and both-metric rate was 0.0222. | Stage 32 optimization is not recommended without user override; downstream diagnostics need rerun if continuing. |
| 32 | `v1p0_Stage32_TSMixer_Optimization_And_Overfit_Control.md` | completed_current | User explicitly overrode Stage 31 and selected heavy Optuna; Stage 32 completed 60/60 trials with 2 seeds, zero lockbox rows for optimization, and rejected the tuned candidate from development evidence. | Tuned TSMixer should not feed Stage 33/35; use Stage 31 fixed TSMixer only if the user explicitly approves downstream work. |
| 33 | `v1p0_Stage33_Market_Ensemble_Horizon_Meta.md` | needs_user_decision | Stage 31 fixed TSMixer predictions exist and Stage 32 rejected the tuned candidate; running Stage 33 with the fixed TSMixer still requires explicit approval. | Blocks refreshed full candidate roster for Stage 35+. |
| 34 | `v1p0_Stage34_Market_Event_Horizon_Fusion.md` | needs_rerun | Existing fusion is usable as exploratory evidence but must be rerun or revalidated after Stage 28/29 and Stage 31-33 status resolution. | Feeds Stage 35+. |
| 35 | `v1p0_Stage35_Full_Diagnostic_Battery_And_Error_Analysis.md` | needs_rerun | Current diagnostics omit repaired Stage 31 fixed TSMixer and Stage 32 rejection evidence. | Must rerun after Stage 31-34 adjustments. |
| 36 | `v1p0_Stage36_Accuracy_Overfit_Frontier_Report.md` | needs_rerun | Must refresh after Stage 35 rerun and any TSMixer/ensemble additions. | Feeds Stage 37/39. |
| 37 | `v1p0_Stage37_Report_Visualization_Fidelity_Full_Packet.md` | needs_rerun | Must refresh after Stage 35/36 rerun. | Feeds Stage 39. |
| 38 | `v1p0_Stage38_Documentation_Truth_Consistency_Audit.md` | needs_rerun | Must refresh after changed Stage 28 or Stage 31-37 evidence. | Feeds Stage 39/40. |
| 39 | `v1p0_Stage39_Final_Benchmark_Claim_Review.md` | needs_rerun | Existing non-claim remains valid, but final review must rerun after new diagnostics. | Controls final language. |
| 40 | `v1p0_Stage40_V1p0_Completion_And_Next_Scope_Gate.md` | needs_rerun | Existing closure is invalid under hardened prompt until critical deferrals are executed or explicitly user-approved. | Final completion gate. |

## Immediate Execution Boundary

- XGBoost-specific serious stages are Stage 21 through Stage 25; they are already completed and do not currently need rerun unless their upstream configs change.
- Stage 26 is FinBERT source/license/cache contract, not an XGBoost stage.
- User clarified on 2026-05-25 that the requested execution boundary is XGBoost through Stage 25.
- XGBoost Stage 21-25 validation after the status update passed with focused tests (`14 passed`), manifest-chain validation (`XGBOOST_STAGE21_25_ARTIFACT_CHAIN_OK`), and status-register validation (`XGBOOST_STATUS_REGISTER_OK stages=21-25`).
- 2026-05-25 continuation approval executed Stage 26 through Stage 31 with user-selected 128d FinBERT projection and heavy 5-seed 60d TSMixer.
- 2026-05-25 user explicitly overrode Stage 31 and selected the heavy Stage 32 Optuna contract. Stage 32 completed 60/60 trials with 2 seeds, used zero lockbox rows for optimization, and rejected the tuned TSMixer candidate from development evidence.

## Non-Claims

This register is operational status only. It does not approve silent deferrals, approve positive benchmark claims, promote comparability, reinterpret Stage 6, call live providers, mutate raw data, or create trading/product scope.
