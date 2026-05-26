# Benchmarking Strategy

Status: active v1p0 benchmarking strategy; first-slice smoke plus Stage 15-40 market/FinBERT/fusion/final-review evidence exists with non-claims

Updated: 2026-05-25

Primary authorities: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `LearningStrategy.md`

## 1. Purpose

This document defines benchmark design choices, candidate promotion gates, diagnostics, statistical tests, and evidence required for v1p0 claims.

It does not reinterpret the v0p9 Stage 6 `clean_null` result and does not approve positive v1p0 benchmark-improvement language.

The full v1p0 prompt plan requires future serious runs to record hyperparameters, metrics, runtime, environment, uncertainty, overfit-frontier evidence, and claim status under `data/v1p0_full_results/`.

## 2. Benchmark Family Discipline

| Rule | Requirement |
| --- | --- |
| Version identity | Every v1p0 candidate must carry benchmark-family and component version IDs. |
| Comparability | Any difference from v0p9 must be marked as versioned candidate evidence unless comparability is explicitly reviewed. |
| No lockbox tuning | Lockbox/final evidence cannot guide search or selection. |
| Saved predictions | Metrics must be computed from saved predictions, not hidden model state. |
| Manifest-backed claims | Claims require manifests, configs, prediction schemas, diagnostics, and validation output. |

## 3. First-Slice Candidate Set

| Candidate | Role |
| --- | --- |
| `market_lag_linear_v1` | Sanity-check temporal market baseline. |
| `market_xgboost_v1_fixed` | Stronger honest fixed boosted-tree market hurdle. |
| Current v0p9 baselines | Historical reference only unless explicitly loaded through comparable artifact contracts. |
| Tuned XGBoost | Deferred candidate requiring nested purged tuning. |
| TSMixer, FinBERT, ensembles | Deferred until first-slice evidence is stable. |

## 4. Candidate Promotion Gates

| Gate | Promotion requirement |
| --- | --- |
| Gate 0: design | Candidate has documented purpose, inputs, outputs, and non-claims. |
| Gate 1: schema | Configs, registry, feature sidecars, predictions, and metrics have schemas. |
| Gate 2: leakage | No feature, preprocessing, split, or metric leakage detected in tests. |
| Gate 3: smoke | Tiny/sample run succeeds and writes inspectable artifacts. |
| Gate 4: development evidence | Development folds produce saved predictions and diagnostics. |
| Gate 5: diagnostic evidence | Train-gap where available, strata, uncertainty, and failure modes are recorded. |
| Gate 6: lockbox readiness | Candidate is frozen before lockbox reporting. |
| Gate 7: claim review | Comparability, limitations, and non-claims are reviewed before any result language. |
| Gate 8: overfit frontier | Accuracy gains are checked against train/validation/final degradation before promotion. |

## 5. Diagnostics

| Diagnostic | Requirement |
| --- | --- |
| Primary regression metrics | Compute RMSE/MAE-style errors by model, horizon, fold, and row role. |
| Ranking diagnostics | Preserve secondary ranking/cross-sectional diagnostics where applicable. |
| Train gap | Compute train-vs-validation gaps only where train predictions are explicitly saved. |
| Fold dispersion | Report variability across folds and horizons. |
| Positive-horizon rates | Report consistency, not just average improvement. |
| Strata | Include no-news, news-rich, truncation-risk, and article-count strata. |
| Failure notes | Record rows/horizons/folds where candidate behavior is unstable. |
| Overfit frontier | Track where training performance continues to improve while validation or final evidence degrades. |

## 6. Statistical Evidence

| Method | v1p0 status |
| --- | --- |
| Date-clustered confidence intervals | First uncertainty method to implement. |
| Block bootstrap | Required before final promotion beyond first-slice evidence. |
| Diebold-Mariano | Later candidate, not first-slice requirement. |
| Permutation tests | Later candidate, not first-slice requirement. |

## 7. Evidence Required For Claims

| Claim type | Required evidence |
| --- | --- |
| Smoke-ready | Passing smoke test and generated sample artifacts. |
| Development candidate | Full development-fold saved predictions, metrics, diagnostics, and manifests. |
| Lockbox-reported candidate | Frozen pre-lockbox candidate plus final reporting artifacts. |
| Benchmark improvement | Paired metrics, strata, uncertainty, limitations, and comparability classification. |
| Publication-ready claim | Stronger uncertainty, limitation resolution or explicit caveats, and no stale-risk in docs. |

## 8. Result-Vault Requirements

Future serious v1p0 benchmark and optimization runs must write result packets under `data/v1p0_full_results/`. Required contents include run manifests, source artifacts, feature IDs, model IDs, hyperparameters, search spaces, trial ledgers, seeds, training time, inference time, train/validation/lockbox metrics, strata, uncertainty, overfit-frontier evidence, report artifacts, and claim status.

No run is promotion-ready if its result packet cannot be audited from saved predictions and manifests.

## 9. Non-Claims

The first slice must not claim live forecast usefulness, trading profitability, provider completeness, Stage 6 reinterpretation, or benchmark comparability without explicit evidence and approval.
