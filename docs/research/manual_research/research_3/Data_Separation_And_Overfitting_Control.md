# Data Separation And Overfitting Control

Status: active-root validation-design contract. Created 2026-05-07 after explicit user approval of Option B: keep the approved purged-plus-embargoed walk-forward plus final untouched lockbox, and add mandatory data-separation, predeclared-metric, saved-prediction, and overfitting-diagnostic requirements. Updated after Stage 7C to record the explicit post-Stage-6-lockbox diagnostic holdout rule. This document refines `DQ-012`, `DQ-013`, `DQ-018`, `DQ-021`, and `DQ-023` without changing the approved Stage 6 benchmark result.

## 1. Authority And Scope

This document is governed by:

- `AgentRules.md`
- `ScopeDecisionLog.md`
- `ResearchTruth.md`
- `ProjectDefinition.md`
- `docs/Benchmark_Testing.md`
- `docs/db_Testing.md`
- `docs/Pipeline_Testing.md`

It owns the active design contract for:

- train, validation, development-fold, and lockbox separation
- purging and embargoing requirements
- preprocessing-fit boundaries
- metric predeclaration
- saved out-of-sample prediction requirements
- quantitative overfitting diagnostics
- contamination blockers

It does not own target family, horizon set, provider stack, universe definition, or the final evaluation protocol. Those remain governed by `ScopeDecisionLog.md` and `ResearchTruth.md`.

## 2. Approved Option B Definition

Option B means:

- Keep the approved `DQ-012` evaluation doctrine: purged-plus-embargoed walk-forward development evaluation plus final untouched lockbox.
- Add explicit quantitative diagnostics for overfitting and model-selection fragility.
- Preserve the first benchmark family: top-50 universe, forward excess returns, horizons `1d`, `5d`, `10d`, `20d`, `60d`, same-day as-of-close alignment, Twelve Data OHLCV, Alpha Vantage news, SEC support only.
- Do not treat diagnostics as permission to metric-shop, tune on the lockbox, or change the benchmark family.

## 3. Data Separation Contract

Every benchmark dataset row must have stable row identity:

- canonical ticker
- as-of date
- horizon
- feature availability timestamp
- label window start and end
- split assignment
- fold ID where applicable
- lockbox membership flag

The dataset builder must assign rows to exactly one active evaluation role at a time:

- training row
- validation/development fold row
- embargoed row excluded from fitting and scoring for the affected fold
- purged row excluded from fitting and scoring for the affected fold
- final lockbox row
- excluded row with explicit exclusion reason

Random row shuffling across time is forbidden for serious claims.

## 4. Purge And Embargo Contract

For each fold, training rows must be removed when their label windows overlap the validation or test window.

The embargo window must be explicit in the split manifest. The default implementation contract should use the maximum approved horizon as the starting policy unless a more precise documented policy is approved.

The split manifest must record:

- fold ID
- train date span
- validation/test date span
- purge span
- embargo span
- lockbox boundary
- row counts by split and horizon
- excluded row counts and reasons
- hash or stable identity for the input dataset version

## 5. Lockbox Contract

The final lockbox is for reporting only.

Forbidden lockbox uses:

- hyperparameter tuning
- model selection
- feature selection
- clean-window selection
- provider-coverage policy selection
- metric selection
- threshold selection
- debugging by repeated result inspection

Allowed lockbox uses:

- final held-out metric computation after the development process is frozen
- final degradation report versus development-fold performance
- final comparison summary based on saved predictions

If lockbox leakage occurs, the affected lockbox result must be marked invalidated or not comparable, and a new lockbox policy requires explicit approval.

Stage 7C-specific rule:

- Stage 7 development replay must exclude the current Stage 6 lockbox (`2025-09-30` through `2026-02-13`) from design/tuning/debugging.
- Stage 7C post-lockbox diagnostics may use the explicit new holdout `2026-02-17` through `2026-02-25` after the approved data update.
- This Stage 7C holdout use is diagnostics-only with `benchmark_claim=false` unless a later governance record promotes it; it does not approve all-data final-execution training-output or live trading signals.

## 6. Fold-Local Preprocessing Contract

Every transformation with learned parameters must be fit only on the training rows for the active fold.

Examples:

- scalers
- imputers
- winsorization thresholds
- feature selection filters
- embedding post-processing fitted on the benchmark dataset
- target normalization
- model calibration layers if later approved

Transformations may then be applied to validation, development-test, or lockbox rows only after training-fold fitting is complete.

Global preprocessing across train and validation/test/lockbox rows is forbidden unless the transformation is proven deterministic and independent of observed labels, outcomes, and future information.

## 7. Metric Contract

Regression metrics remain primary:

- RMSE
- MAE
- out-of-sample `R2` versus a predeclared baseline
- mean loss difference versus the market-only baseline

Ranking diagnostics remain secondary:

- Spearman rank IC
- Kendall rank correlation
- cross-sectional directional hit rate as diagnostic only
- top-minus-bottom spread as diagnostic only, not as a trading claim

All metrics must be computed from saved out-of-sample predictions, frozen labels, and the split manifest.

No metric can be added, removed, promoted, demoted, or reweighted after result inspection without a benchmark comparability review and explicit approval if comparability changes.

## 8. Overfitting Diagnostic Contract

Every serious comparison summary must include these diagnostics:

- train-to-validation performance gap by model family and horizon
- development-fold mean and standard deviation by metric and horizon
- percentage of development folds where the event-state branch improves over the market-only baseline
- percentage of approved horizons where the event-state branch improves over the market-only baseline
- validation-to-lockbox degradation by model and metric
- paired saved-prediction comparison against the market-only baseline where sample assumptions are satisfied
- multiple-comparison note across horizons, models, and diagnostics
- search-space summary: number of models, feature sets, horizons, metrics, and tuning attempts considered

Diagnostics support interpretation. They do not replace the approved metrics and do not create a benchmark success claim by themselves.

## 9. Contamination Blockers

The pipeline must fail closed if any of the following are detected:

- row appears in both train and validation/test/lockbox for the same fold and horizon
- training row label window overlaps validation/test/lockbox window after purge policy is applied
- embargoed row is used for fitting or scoring
- lockbox row is used before the final frozen run
- preprocessing object is fit on non-training rows
- market-only and event-state branches use different row universes
- saved predictions lack row keys, fold IDs, horizon IDs, model IDs, or dataset version
- metric computation consumes in-sample predictions for an out-of-sample claim
- metric or model list differs from the resolved config without a comparability record

## 10. Required Artifacts

Every serious run must preserve:

- dataset version
- dataset manifest
- resolved config
- split manifest with purged and embargoed row accounting
- preprocessing-fit manifest
- saved predictions
- metric outputs
- overfitting diagnostic report
- comparison summary
- benchmark comparability classification

## 11. Stage Dependencies

This contract affects stages as follows:

| Stage | Dependency impact |
| --- | --- |
| Stage 0B | This document is the controlling contract for data separation and overfitting diagnostics. |
| Stage 1 | Raw audit must expose provider status, truncation, empty feeds, and credential risk before dataset inclusion. |
| Stage 2 | Dataset builder must emit row identities, label windows, split eligibility, and manifest hashes. |
| Stage 3 | Feature and label builders must be as-of safe and preserve row universe equality. |
| Stage 4 | Split builder and artifact packet validation become hard gates before model work. |
| Stage 5 | Models must consume split manifests and produce saved out-of-sample predictions only. |
| Stage 6 | Reports must include metric outputs, overfitting diagnostics, and lockbox degradation. |
| Stage 7C | Contextual-bandit diagnostics must preserve Stage 6 lockbox exclusion for design and use only explicitly approved post-lockbox rows for new holdout diagnostics. |

## 12. Completion Rule

This contract is complete for design purposes only when affected design, validation, execution, guidebook, README, config scaffold, test scaffold, and operational memory files reference it consistently.

It does not create executable tests, a dataset builder, a split builder, a model, or a benchmark result by itself.
