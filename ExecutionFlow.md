# Execution Flow

Status: active v1p0 execution plan; first-slice smoke complete, full implementation stages are prompt-only planning

Updated: 2026-05-24

Primary authorities: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `ProjectDefinition.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `VisualizationStrategy.md`

## 1. Purpose

This file defines the v1p0 execution flow. Stages 00 through 14 cover the completed first-slice smoke path. Stages 15 through 40 are planning prompts for the remaining full v1p0 implementation, including serious benchmarks, tuning, diagnostics, overfit controls, report fidelity, visualization readiness, and final claim review.

No v1p0 implementation is complete merely because it is planned here.

Stages 15 through 40 are not approval to execute code, train models, call providers, mutate raw data, or create positive claims. They are future execution prompts.

## 2. Global Execution Rules

| Rule | Requirement |
| --- | --- |
| Truth sources | Use `ArchitecturalDesignDecisions.md` and `ResearchTruth.md` as top-level project truth for this flow. |
| Version naming | Use `v1p0` for new plans, configs, manifests, artifact families, and reports. |
| No relabeling | Do not relabel v0p9 artifacts as v1p0. |
| Reuse policy | Compare reuse vs rewrite from `deprecated/v0p9/src/` or any current v0p9 code before importing old logic. Reuse only if compatibility is cleaner than rewriting. |
| Compatibility tests | Any reused old code requires compatibility tests before it can support v1p0 claims. |
| Provider calls | No live provider calls in this flow. |
| Raw mutation | No raw overwrite or hidden data mutation. |
| Lockbox | No lockbox tuning or result-guided iteration. |
| Documentation | Each stage must update relevant docs or explicitly record that no doc update was needed. |
| Result vault | Any future serious v1p0 run must write hyperparameters, metrics, runtime, environment, overfit diagnostics, and provenance under `data/v1p0_full_results/`. |
| Overfit boundary | Optimization should explore accuracy only until the generalization frontier is characterized; training improvement with validation or test degradation must stop or constrain promotion. |

## 3. Readiness Before Stage 1

| Check | Expected result |
| --- | --- |
| Governance validator | Passes. |
| Event ledger parse | Passes. |
| Active docs | v1p0 root docs exist. |
| Deprecated sources | v0p9 source/reference paths are known and not active truth. |
| Approval gates | No live provider, raw overwrite, Stage 6 reinterpretation, or service/API/dashboard scope is triggered. |

## 4. Stage Plan

### Stage 00: Governance And Context Readiness

Purpose: confirm the work starts from valid v1p0 planning context.

Objectives: read required truth files, confirm no approval gate is triggered, and record current blockers.

Explicit paths: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `ProjectDefinition.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `VisualizationStrategy.md`, `docs/agent/agent_log/Current_State.md`, `docs/agent/agent_log/Event_Ledger.ndjson`.

Inputs: active docs and ledger.

Outputs: readiness note in memory or stage evidence.

Dependencies: none beyond governance files.

Smoke tests: governance validator and ledger JSONL parse.

Completion criteria: no missing top-level v1p0 planning files; approval gates known.

Success metrics: validator pass, ledger parse pass, no unresolved context blocker.

Readiness for next stage: proceed only if v1p0 first-slice scope remains documentation/modeling-local.

### Stage 01: v0p9 Reuse Versus Rewrite Audit

Purpose: decide whether any v0p9 code should be reused.

Objectives: inspect candidate old modules, compare reuse vs rewrite, identify compatibility tests required for any reuse.

Explicit paths: `deprecated/v0p9/src/`, `src/event_state_forecasting/` if present, `Architecture_Map.md`, `Complete_guidebook.txt`.

Inputs: old code, v1p0 architecture contracts.

Outputs: reuse audit note or manifest.

Dependencies: Stage 00.

Smoke tests: no code execution required; optional import check only if candidate reuse is selected.

Completion criteria: each candidate component is classified as rewrite, reuse, or reference-only.

Success metrics: no old code imported without a required compatibility-test plan.

Readiness for next stage: proceed only if implementation paths are not blocked by unknown old-code dependencies.

### Stage 02: v1p0 Version Manifest Contract

Purpose: define v1p0 benchmark-family and component version identity.

Objectives: create schema/design for v1p0 manifest fields and naming.

Explicit paths: planned `configs/v1p0_version_manifest.yaml`, planned `data/manifests/v1p0_*`, `ArchitecturalDesignDecisions.md`.

Inputs: v1p0 naming decision and first-slice component list.

Outputs: version manifest config or design stub plus tests.

Dependencies: Stage 01.

Smoke tests: config parses and rejects v0p9 relabeling.

Completion criteria: version IDs are explicit for benchmark family and components.

Success metrics: manifest load smoke passes.

Readiness for next stage: proceed only after version IDs exist or are deliberately stubbed.

### Stage 03: Sidecar Feature Registry Contract

Purpose: define how feature artifacts map to model variants.

Objectives: create sidecar registry schema and model-feature mapping rules.

Explicit paths: planned `configs/feature_registry_v1p0.yaml`, planned registry validator, `Architecture_Map.md`.

Inputs: version manifest, first-slice model list.

Outputs: registry config or design stub plus smoke validator.

Dependencies: Stage 02.

Smoke tests: registry load, ID uniqueness, path resolution dry-run.

Completion criteria: every first-slice model has explicit feature dependency records.

Success metrics: registry smoke passes.

Readiness for next stage: proceed only when feature outputs can be named without ambiguity.

### Stage 04: Market Lag/Rolling Feature Contract

Purpose: define the tabular market feature sidecar contract.

Objectives: specify lag windows, rolling windows, column naming, null handling, row identity, and leakage checks.

Explicit paths: planned `configs/market_features_v1p0.yaml`, planned `data/features/v1p0_*`, planned tests under `tests/features/`.

Inputs: existing market panel or approved dataset roots, v1p0 registry.

Outputs: feature contract, config, and smoke-test expectations.

Dependencies: Stage 03.

Smoke tests: tiny dataframe lag/rolling no-lookahead test.

Completion criteria: feature columns and row identity fields are specified.

Success metrics: contract test passes on toy data.

Readiness for next stage: proceed only if leakage and null policies are explicit.

### Stage 05: Market Feature Sidecar Builder

Purpose: implement or stub the sidecar builder according to Stage 04.

Objectives: produce versioned lag/rolling feature sidecar artifacts without mutating old features.

Explicit paths: planned `src/event_state_forecasting/features/`, planned `data/features/v1p0_*`, planned `tests/features/test_v1p0_market_features.py`.

Inputs: feature config, market input artifact, registry.

Outputs: sidecar Parquet/manifest or smoke sample.

Dependencies: Stage 04.

Smoke tests: build tiny sample; verify row identity and no future usage.

Completion criteria: sidecar builder writes expected schema and manifest.

Success metrics: feature tests pass; manifest contains source IDs.

Readiness for next stage: proceed only if features are reproducible and versioned.

### Stage 06: Split And Label Compatibility Adapter

Purpose: ensure v1p0 features align with existing labels and splits.

Objectives: validate row keys, horizons, folds, lockbox roles, and label availability.

Explicit paths: planned tests under `tests/split/` or `tests/benchmark/`, existing split/label roots, feature sidecar roots.

Inputs: v1p0 features, existing labels and split artifacts.

Outputs: compatibility validation report.

Dependencies: Stage 05.

Smoke tests: join sample features to labels/splits and verify row counts.

Completion criteria: no row-universe drift is detected.

Success metrics: compatibility validator passes.

Readiness for next stage: proceed only if model training can consume aligned rows.

### Stage 07: Lag-Linear Baseline

Purpose: implement `market_lag_linear_v1` as temporal sanity baseline.

Objectives: fit simple lag-linear model with fold-local preprocessing and saved predictions.

Explicit paths: planned `src/event_state_forecasting/models/`, planned `configs/models_v1p0.yaml`, planned `tests/models/test_market_lag_linear_v1.py`, planned `data/models/v1p0_*`.

Inputs: feature sidecars, labels, splits, model config.

Outputs: saved predictions, fit records, preprocessing records.

Dependencies: Stage 06.

Smoke tests: tiny fold training and saved-prediction schema test.

Completion criteria: predictions are saved with model ID, horizon, fold, row role, and provenance.

Success metrics: model smoke passes; no lockbox tuning.

Readiness for next stage: proceed only if saved-prediction schema is stable.

### Stage 08: Fixed XGBoost Baseline

Purpose: implement `market_xgboost_v1_fixed` as an honest stronger market hurdle.

Objectives: add fixed XGBoost config, fold-local preprocessing, deterministic seeds, and saved predictions.

Explicit paths: planned `src/event_state_forecasting/models/`, planned `configs/models_v1p0.yaml`, planned `tests/models/test_market_xgboost_v1_fixed.py`, planned `data/models/v1p0_*`.

Inputs: feature sidecars, labels, splits, model config.

Outputs: saved predictions, fit records, preprocessing records, dependency notes.

Dependencies: Stage 07.

Smoke tests: tiny/small sample training; skip or mark blocked if dependency unavailable and document remediation.

Completion criteria: fixed parameters are recorded; no Optuna or lockbox-guided tuning.

Success metrics: smoke pass or explicit dependency blocker with no false completion claim.

Readiness for next stage: proceed only if fixed XGBoost prediction schema matches lag-linear schema.

### Stage 09: Prediction Packet And Model Registry Validation

Purpose: validate first-slice saved predictions as comparable candidate inputs.

Objectives: verify schema, provenance, row roles, model IDs, folds, horizons, and registry links.

Explicit paths: planned validators under `scripts/` or `tests/models/`, planned `data/models/v1p0_*`.

Inputs: predictions from Stages 07 and 08, feature registry, version manifest.

Outputs: prediction validation summary.

Dependencies: Stage 08.

Smoke tests: schema and row-count validation.

Completion criteria: prediction artifacts pass validator.

Success metrics: zero schema/provenance blockers.

Readiness for next stage: proceed only if diagnostics can consume predictions.

### Stage 10: Initial Diagnostics Core

Purpose: create core diagnostics for first-slice candidates.

Objectives: compute fold metrics, train-gap where train predictions exist, fold dispersion, and candidate limitation summaries.

Explicit paths: planned `src/event_state_forecasting/evaluation/`, planned `configs/diagnostics_v1p0.yaml`, planned `tests/evaluation/test_v1p0_diagnostics.py`.

Inputs: saved predictions, labels, splits, manifests.

Outputs: diagnostic tables and manifests.

Dependencies: Stage 09.

Smoke tests: diagnostic computation on tiny prediction sample.

Completion criteria: diagnostics are saved and linked to source predictions.

Success metrics: diagnostics tests pass.

Readiness for next stage: proceed only if strata fields are available or explicitly blocked.

### Stage 11: Stratified Metrics

Purpose: report behavior by no-news, news-rich, truncation-risk, and article-count strata.

Objectives: define bucket policy, compute stratum metrics, and preserve limitations.

Explicit paths: planned `src/event_state_forecasting/evaluation/`, planned `tests/evaluation/test_v1p0_strata.py`, planned metric artifacts.

Inputs: predictions, labels, aligned-news/truncation flags, article counts.

Outputs: stratum metric tables and manifest.

Dependencies: Stage 10.

Smoke tests: bucket assignment and aggregate consistency on toy data.

Completion criteria: strata tables identify definitions and limitations.

Success metrics: strata tests pass; no provider-completeness claim.

Readiness for next stage: proceed only if report tables can cite stratum definitions.

### Stage 12: First Uncertainty Evidence

Purpose: add first uncertainty evidence for v1p0 candidate metrics.

Objectives: implement date-clustered confidence intervals as the initial method.

Explicit paths: planned `src/event_state_forecasting/evaluation/`, planned `configs/diagnostics_v1p0.yaml`, planned `tests/evaluation/test_v1p0_uncertainty.py`.

Inputs: metric inputs grouped by date/fold/horizon.

Outputs: confidence interval tables and method metadata.

Dependencies: Stage 11.

Smoke tests: deterministic CI output for toy grouped data.

Completion criteria: method and limitations are recorded.

Success metrics: CI smoke passes; block bootstrap remains documented as later requirement.

Readiness for next stage: proceed only if reporting can display method caveats.

### Stage 13: Stage 10C Clarity And Report Fidelity

Purpose: update local report style for v1p0 outputs without live forecast semantics.

Objectives: improve wording, per-horizon tables, deterministic context policy, caveats, and report/data fidelity checks.

Explicit paths: planned `src/event_state_forecasting/reporting/`, planned `configs/reporting_v1p0.yaml`, planned `tests/stage10/` or `tests/reporting/`.

Inputs: diagnostics, metrics, model outputs, limitations.

Outputs: static report packet or report-render smoke artifact.

Dependencies: Stage 12.

Smoke tests: report generation on small packet; rendered values equal source tables.

Completion criteria: no forbidden live/trading/benchmark-reinterpretation wording.

Success metrics: report fidelity tests pass.

Readiness for next stage: proceed only if report and machine-readable tables agree.

### Stage 14: Integrated First-Slice Evidence Review

Purpose: decide whether the first slice is complete enough for broader model expansion planning.

Objectives: review all outputs, tests, docs, memory, comparability, and remaining blockers.

Explicit paths: all v1p0 configs, code, tests, artifacts, strategy docs, `Complete_guidebook.txt`, memory files.

Inputs: outputs from Stages 00 through 13.

Outputs: completion summary and next-stage recommendation.

Dependencies: Stage 13.

Smoke tests: full relevant test subset and governance/ledger validation.

Completion criteria: evidence pointers exist for every completed stage; unresolved blockers are explicit.

Success metrics: no invalid DONE claims, no hidden approval gates, no stale doc blockers.

Readiness for next stage: broader FinBERT/TSMixer/tuning work remains deferred until user approves the next plan.

## 5. Full v1p0 Expansion Plan

Stages 15 through 40 extend the first-slice smoke plan into the full v1p0 implementation plan. They are documentation prompts only until explicitly executed later.

| Stage | Prompt | Purpose | Required future outputs | Required checks | Stop conditions |
| --- | --- | --- | --- | --- | --- |
| 15 | `docs/Prompts/v1p0_Stage15_Full_Run_Governance_And_Result_Vault.md` | Prepare governance and result-vault contract. | Run-root naming, result schema, approval gate register. | Governance validator, ledger parse. | Any request to execute training before result-vault contract exists. |
| 16 | `docs/Prompts/v1p0_Stage16_Historical_Artifact_Compatibility_Gate.md` | Verify Stage 2-6 historical artifact compatibility. | Compatibility report and comparability classification. | Row, horizon, fold, label, lockbox checks. | Row drift, missing labels, unclassified comparability. |
| 17 | `docs/Prompts/v1p0_Stage17_Production_Market_Feature_Sidecars.md` | Materialize full market lag/rolling sidecars. | Versioned feature sidecars and manifests. | No-lookahead, row-key, null-policy, digest tests. | Leakage or row mismatch. |
| 18 | `docs/Prompts/v1p0_Stage18_Sequence_Window_Materialization.md` | Materialize sequence-window artifacts for TSMixer. | Sequence contract, tensors/manifests if approved. | Shape, padding, normalization, no-future tests. | Unknown tensor semantics or memory budget. |
| 19 | `docs/Prompts/v1p0_Stage19_Historical_Lag_Linear_And_Fixed_XGBoost_Benchmark.md` | Run full lag-linear and fixed-XGBoost baselines. | Saved predictions, hyperparameters, runtime, manifests. | Fold-local preprocessing and saved-prediction tests. | Missing fixed config, dependency blocker, or lockbox tuning risk. |
| 20 | `docs/Prompts/v1p0_Stage20_Full_Diagnostic_Baseline_Gate.md` | Diagnose full fixed baselines before tuning. | Metrics, train gaps, strata, fold dispersion, failure notes. | Metric, gap, strata, dispersion tests. | Diagnostics too incomplete to guide tuning. |
| 21 | `docs/Prompts/v1p0_Stage21_XGBoost_Search_Space_And_Objective_Freeze.md` | Freeze XGBoost search space and objective. | Search-space config, objective config, budget, stop rules. | Horizon-weight, penalty, no-lockbox tests. | Search begins before config freeze. |
| 22 | `docs/Prompts/v1p0_Stage22_XGBoost_Nested_Random_And_Optuna_Search.md` | Run nested random/TPE/refinement search. | Trial ledger, trial predictions, runtime, overfit markers. | Nested split, objective recomputation, resume tests. | Lockbox access or incomplete trial ledger. |
| 23 | `docs/Prompts/v1p0_Stage23_XGBoost_Frozen_Final_Evaluation.md` | Evaluate frozen XGBoost candidate. | Frozen-final predictions, metrics, manifests. | Frozen-config digest and metric recomputation tests. | Config selected after lockbox inspection. |
| 24 | `docs/Prompts/v1p0_Stage24_XGBoost_Overfit_Frontier_And_Promotion_Review.md` | Characterize tuned XGBoost overfit frontier. | Overfit frontier, classification, promotion recommendation. | Frontier schema and classification tests. | Validation/test degradation hidden by aggregate averages. |
| 25 | `docs/Prompts/v1p0_Stage25_Block_Bootstrap_Uncertainty.md` | Add block-bootstrap uncertainty. | Bootstrap intervals, method metadata, runtime. | Determinism, block-boundary, small-sample tests. | Unstable uncertainty evidence. |
| 26 | `docs/Prompts/v1p0_Stage26_FinBERT_Source_License_And_Cache_Contract.md` | Freeze FinBERT source and cache contract. | Model/tokenizer pins, license note, cache schema. | Revision, cache-key, offline-read tests. | Model source/license unresolved. |
| 27 | `docs/Prompts/v1p0_Stage27_FinBERT_Article_Embedding_Cache.md` | Materialize article embedding cache. | Article embeddings/logits, cache manifest, runtime. | Cache schema, dimension, determinism tests. | Provider completeness or future-news leakage claim. |
| 28 | `docs/Prompts/v1p0_Stage28_FinBERT_Aggregation_Ablations.md` | Build FinBERT aggregation sidecars. | Mean, recency, top-k, count-recency sidecars. | Aggregation, no-news, row-key tests. | Aggregation chosen without ablation evidence. |
| 29 | `docs/Prompts/v1p0_Stage29_Event_Representation_Benchmark_Gate.md` | Benchmark event representation variants. | Representation predictions, diagnostics, runtime. | Registry, schema, strata tests. | Event claim against weak or unverified hurdle. |
| 30 | `docs/Prompts/v1p0_Stage30_TSMixer_Sequence_Dataset_And_Smoke.md` | Implement TSMixer smoke path. | Tiny smoke predictions, parameter count, runtime. | Dataset shape, forward pass, tiny training tests. | Sequence contract not validated. |
| 31 | `docs/Prompts/v1p0_Stage31_TSMixer_Fixed_Multiseed_Benchmark.md` | Run fixed multiseed TSMixer. | Seed-level predictions, metrics, runtime, manifests. | Multiseed, reproducibility, no-lockbox tests. | Standalone evidence not stable. |
| 32 | `docs/Prompts/v1p0_Stage32_TSMixer_Optimization_And_Overfit_Control.md` | Optimize TSMixer if justified. | Search ledger, overfit flags, frozen candidate or rejection. | Trial, overfit, no-lockbox tests. | Validation degradation while train improves. |
| 33 | `docs/Prompts/v1p0_Stage33_Market_Ensemble_Horizon_Meta.md` | Evaluate XGBoost plus TSMixer horizon meta-combiner. | Meta predictions, coefficients, runtime, diagnostics. | Fold-local meta-training and schema tests. | Standalone models missing or leaked. |
| 34 | `docs/Prompts/v1p0_Stage34_Market_Event_Horizon_Fusion.md` | Evaluate market plus FinBERT horizon fusion. | Fusion predictions, coefficients/importances, diagnostics. | Row alignment, no-news behavior, fold-local tests. | Fusion claim before strong market hurdle exists. |
| 35 | `docs/Prompts/v1p0_Stage35_Full_Diagnostic_Battery_And_Error_Analysis.md` | Run full diagnostics across all candidates. | Diagnostic battery, error analysis, candidate classifications. | Metrics, strata, hurdle comparison tests. | Missing diagnostics for any candidate. |
| 36 | `docs/Prompts/v1p0_Stage36_Accuracy_Overfit_Frontier_Report.md` | Summarize accuracy versus overfit frontier. | Frontier tables, runtime summaries, action recommendations. | Frontier schema and overfit classification tests. | Overfit boundary unclear. |
| 37 | `docs/Prompts/v1p0_Stage37_Report_Visualization_Fidelity_Full_Packet.md` | Produce full static report/visualization packet. | Source-faithful tables/charts and caveat panels. | Fidelity, accessibility, forbidden-wording tests. | Unsupported dashboard/live/trading semantics. |
| 38 | `docs/Prompts/v1p0_Stage38_Documentation_Truth_Consistency_Audit.md` | Reconcile docs and truth after evidence exists. | Updated docs and memory, if evidence-backed. | Governance, ledger, stale-path checks. | Truth update without artifact/test/manifest evidence. |
| 39 | `docs/Prompts/v1p0_Stage39_Final_Benchmark_Claim_Review.md` | Decide final allowed result language. | Claim classification and comparability review. | Claim-language and source-fidelity tests. | Positive claim without benchmark evidence. |
| 40 | `docs/Prompts/v1p0_Stage40_V1p0_Completion_And_Next_Scope_Gate.md` | Close v1p0 and gate future scope. | Completion register and next-scope approval questions. | Full selected tests, result-vault completeness, governance. | Any hidden approval gate or missing evidence. |

### 5.1 Full v1p0 Result-Vault Requirements

Every future serious run must record:

| Category | Required fields |
| --- | --- |
| Identity | Run ID, stage ID, model ID, feature ID, benchmark-family ID, component versions, git state, environment. |
| Inputs | Source artifact roots, row counts, folds, horizons, label version, split version, feature manifest digests. |
| Hyperparameters | Full resolved config, search space, selected values, random seeds, sampler settings, early-stop rules. |
| Accuracy | Train, validation, lockbox/final metrics by fold, horizon, split role, strata, and candidate. |
| Runtime | Feature build time, training time, inference time, search time, hardware/device notes, failure/retry notes. |
| Overfit evidence | Train-validation gaps, validation/final degradation flags, frontier tables, instability penalties, candidate classification. |
| Claims | Benchmark claim flag, comparability label, non-claims, approval references, report language status. |

### 5.2 Optimization Boundary

Full v1p0 optimization should seek higher accuracy, but not by consuming protected final evidence or hiding overfit. A candidate must be stopped, simplified, regularized, or demoted when training performance continues to improve while validation or final-test performance decreases, becomes horizon-unstable, or gains only in one narrow stratum without a defensible aggregate result.

## 6. Documentation Update Requirements

Each stage must update or review:

| File | When updated |
| --- | --- |
| `Complete_guidebook.txt` | Any new file, responsibility, artifact, or flow change. |
| `Architecture_Map.md` | Any path, folder, or dependency change. |
| `UsageManual.md` | Only after real v1p0 commands/artifacts exist. |
| `ResearchTruth.md` | Only after implemented truth or non-claim status changes. |
| `docs/agent/agent_log/Current_State.md` | Meaningful task/evidence changes. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Meaningful request, approval, artifact, validation, or blocker events. |

## 7. Global Completion Rule

The v1p0 first slice is complete only after all implemented stages have tests, artifacts or explicit non-artifact evidence, documentation updates, governance validation, event-ledger validation, and no unresolved approval gate that invalidates completion.

Full v1p0 is complete only after Stages 15 through 40 have been executed or explicitly skipped/deferred with evidence, the result vault is complete for all serious runs, final claim language is reviewed, and all protected approval gates remain satisfied.
