# Implementation Roadmap

This document now serves as both:
- a retrospective of what has been implemented,
- and a short roadmap of what remains after the current foundation build-out.

## Implemented stages

### Stage 0 - Bootstrap and tooling
Completed.

Delivered:
- installable dependency definitions,
- `.env.example`,
- package markers,
- basic lint/test/tooling entry points.

### Stage 1 - Configuration and runtime foundation
Completed.

Delivered:
- typed config loading,
- path resolution,
- logging,
- I/O helpers,
- reproducibility helpers,
- executable config-driven runtime setup.

### Stage 2 - Data contracts and manifests
Completed.

Delivered:
- canonical table contracts,
- schema validation,
- manifest validation,
- first executable schema tests.

### Stage 3 - Universe handling and provider client hardening
Completed.

Delivered:
- universe loading and pilot subsets,
- hardened Twelve Data, Finnhub, and SEC clients,
- provider-agnostic split normalization.

### Stage 4 - Raw market ingestion
Completed.

Delivered:
- incremental market update planning,
- raw market payload persistence,
- interim price writing,
- market quality checks,
- market ingestion CLI.

### Stage 5 - Split handling
Completed.

Delivered:
- split-adjustment math,
- adjusted price generation,
- split diagnostics,
- adjusted-price integration into the price pipeline.

### Stage 6 - News ingestion and alignment
Completed.

Delivered:
- timestamp normalization,
- as-of-close alignment,
- text normalization and hashing,
- canonical news ingestion pipeline,
- news ingestion CLI.

### Stage 7 - SEC company KB
Completed.

Delivered:
- company KB generation,
- ticker/CIK mapping table,
- alias table,
- universe enrichment hook,
- company-KB CLI.

### Stage 8 - Market features and labels
Completed.

Delivered:
- conservative adjusted-price market features,
- multi-horizon label generation,
- executable label/leakage tests.

### Stage 9 - Embeddings and event state
Completed.

Delivered:
- offline article embedding cache,
- deterministic hashing backend,
- event-state aggregation,
- executable event-state tests.

### Stage 10 - Final modeling datasets
Completed.

Delivered:
- final `(ticker, date)` panel assembly,
- manifest writing,
- final-panel CLI.

### Stage 11 - Temporal validation and leakage hardening
Completed.

Delivered:
- walk-forward folds,
- purged/embargoed folds,
- leakage assertions,
- executable walk-forward and leakage tests.

### Stage 12 - Market-only baselines
Completed.

Delivered:
- ridge and elastic-net training path,
- optional market MLP path,
- baseline checkpointing,
- prediction export,
- baseline training CLI.

### Stage 13 - First multimodal model
Completed.

Delivered:
- first market + event-state regressor,
- multimodal dataloaders,
- multimodal trainer/inference support,
- multimodal training CLI.

### Stage 14 - Evaluation and ablations
Completed.

Delivered:
- metric registry,
- calibration helpers,
- statistical-comparison helpers,
- ablation summary helpers,
- evaluation CLI,
- ablation CLI.

## Current state of the project

The repository now contains a coherent first-pass end-to-end research system from:
- data ingestion,
- to adjusted-price and news feature generation,
- to final panel construction,
- to market-only and multimodal training,
- to evaluation and ablation summaries.

The system is strong enough for pilot experiments, debugging, and methodological validation.

## Remaining priorities

### 1. Documentation hardening
- keep README, guidebook, and docs fully aligned with actual code,
- reduce stale blueprint wording,
- make onboarding easier for a new collaborator.

### 2. Reporting polish
- generate richer evaluation reports,
- add figure-generation helpers,
- standardize report-ready tables.

### 3. Multimodal research extensions
- richer multimodal architectures,
- optional company-profile training branch,
- controlled uncertainty-aware outputs,
- stronger ablation coverage.

### 4. Manual external verification
- live provider behavior,
- split-source reality on the active market-data plan,
- live Finnhub historical completeness,
- practical runtime behavior under real quotas.

## What still should not be done too early

- do not add time-varying profile branches before a clear leakage-safe design exists,
- do not add end-to-end text fine-tuning before baseline and multimodal comparisons are stable,
- do not overcomplicate evaluation before stored prediction comparison is fully trusted,
- do not treat current pilot outputs as final thesis results without live-data verification.
