# Learning Strategy

Status: active v1p0 learning strategy; first-slice smoke evidence exists, full-v1p0 learning plan remains prompt-only

Updated: 2026-05-24

Primary authorities: `ArchitecturalDesignDecisions.md`, `ProjectDefinition.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`

## 1. Purpose

This document defines the v1p0 learning methodology for data processing, feature construction, leakage controls, model learning, train/validation behavior, and smoke tests.

It does not claim that full v1p0 data, features, models, predictions, diagnostics, or reports exist. First-slice smoke artifacts exist separately and remain toy-data evidence only.

## 2. Learning Scope

| Area | v1p0 first-slice scope |
| --- | --- |
| Versioning | Create v1p0 family and component version records. |
| Feature construction | Add sidecar lag/rolling market features without mutating v0p9 artifacts. |
| Model learning | Add `market_lag_linear_v1` and `market_xgboost_v1_fixed`. |
| Diagnostics | Add initial train-gap capability where train predictions exist, strata, and uncertainty hooks. |
| Reporting | Improve Stage 10C-style clarity and report fidelity only after source tables exist. |

## 3. Data Processing Methodology

| Rule | Requirement |
| --- | --- |
| Input identity | Every v1p0 artifact must record source dataset, feature, split, label, and version identifiers. |
| Row identity | Preserve ticker, as-of date, horizon, split role, fold ID, lockbox flag, and label-window bounds where applicable. |
| No mutation | Do not mutate v0p9 Stage 2/3/4/5/6 artifacts in place. Write v1p0 sidecars or candidate roots. |
| No raw overwrite | No raw provider overwrite or live provider call without explicit approval. |
| Limitation flags | Preserve no-news and truncation-risk information in v1p0 feature and evaluation flows. |

## 4. Feature Construction Methodology

| Feature family | First-slice handling |
| --- | --- |
| Market lag features | Create lagged returns and rolling summaries using only information available at or before the as-of date. |
| Rolling windows | Use explicitly configured windows with minimum-period handling recorded in the manifest. |
| Event/text features | Do not implement FinBERT in the first slice unless separately approved. Preserve contracts/placeholders only. |
| Sequence windows | Define a manifest or contract for future TSMixer, but do not require full sequence tensors in the first slice. |
| Registry | Map every feature sidecar to model variants through a v1p0 registry. |

## 5. Leakage Controls

| Control | Requirement |
| --- | --- |
| Temporal availability | Feature timestamps must not use future market/news/label information. |
| Fold-local learning | Learned preprocessing must fit only on training rows for the active fold. |
| Lockbox safety | Lockbox rows must not guide feature selection, tuning, preprocessing choices, threshold choices, or model selection. |
| Label overlap | Purge/embargo constraints from the active split artifacts must remain respected. |
| Reuse audit | Any reused v0p9 code must pass compatibility tests proving it preserves v1p0 contracts. |

## 6. Model Learning Behavior

| Model | Learning behavior |
| --- | --- |
| `market_lag_linear_v1` | Simple temporal tabular baseline; primarily a sanity check. |
| `market_xgboost_v1_fixed` | Fixed honest boosted-tree market hurdle; no lockbox tuning. |
| Tuned XGBoost | Deferred; nested Optuna is required later but not part of the minimal fixed baseline unless separately scheduled. |
| TSMixer | Deferred after standalone contract and first-slice stability. |
| FinBERT | Deferred after first-slice stability and explicit extraction/aggregation contracts. |
| Ensembles and fusion | Deferred until standalone XGBoost, TSMixer, and FinBERT evidence exists. |

## 7. Train/Validation Behavior

| Behavior | Requirement |
| --- | --- |
| Development folds | Use existing purged/embargoed development folds or explicitly versioned compatible v1p0 splits. |
| Train predictions | Save train predictions only if needed for diagnostics and clearly label them non-claim-bearing. |
| Validation predictions | Save out-of-sample predictions for metrics and comparisons. |
| Lockbox predictions | Generate only after the candidate is frozen for final reporting. |
| Refit policy | Any all-data or final-execution training remains unapproved unless explicitly approved. |

## 8. Smoke Tests

| Smoke test | Purpose |
| --- | --- |
| Config load | Verify v1p0 configs parse and contain explicit version IDs. |
| Registry load | Verify feature/model registry paths and IDs resolve. |
| Row identity | Verify feature sidecars preserve row counts and keys expected by downstream stages. |
| Leakage smoke | Verify lag/rolling windows do not use future rows. |
| Model smoke | Fit tiny fold/sample for each first-slice model. |
| Prediction schema | Verify saved-prediction columns, model IDs, horizons, folds, and row roles. |
| Diagnostic smoke | Verify strata and summary tables are produced from a tiny prediction packet. |
| Full-result vault | Future serious runs must record hyperparameters, runtime, metrics, overfit diagnostics, and provenance under `data/v1p0_full_results/`. |

## 9. Completion Rule

A learning component is complete only when code/configs, smoke tests, artifacts or manifest records, and memory evidence exist. Design text alone is not implementation evidence.
