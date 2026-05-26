# Architectural Design Decisions

Status: active v1p0 decision consolidation

Created: 2026-05-24

Decision sources at consolidation time, in contradiction order: `docs/NextSteps_Brainstorming.md`, `ScopeDecisionLog.md`, `ScopeDefinition.md`

Current source-file status: `docs/NextSteps_Brainstorming.md` remains active in `docs/`; `ScopeDecisionLog.md` and `ScopeDefinition.md` have been manually deprecated by the user and preserved under `deprecated/v0p9/docs/`.

## 1. Purpose

This file consolidates the active architectural and scope decisions needed for v1p0 planning. It preserves non-contradictory information from the source decision files, labels older or resolved v0p9 decisions, and separates implemented truth from future design truth.

This is a decision artifact, not an implementation result. It does not approve provider calls, raw-data mutation, benchmark reruns, Stage 6 reinterpretation, live forecasts, services, dashboards, APIs, trading outputs, or benchmark-comparability promotion.

## 2. Authority And Reconciliation Rules

| Rule | Decision |
| --- | --- |
| Source priority | `docs/NextSteps_Brainstorming.md` overrides the preserved `ScopeDecisionLog.md` content, which overrides the preserved `ScopeDefinition.md` content for contradictions in this consolidation. |
| Non-contradictory details | Preserve them, even when they came from older scope files. |
| Contradictions | Keep short reconciliation notes instead of silently dropping older decisions. |
| Active vs deprecated | Keep active v1p0 decisions separate from resolved/deprecated v0p9 or earlier restart decisions. |
| Truth labels | Clearly distinguish implemented truth from design truth. |

## 3. Current Implemented Truth

These statements describe implemented or already-executed repository state, not future design intent.

| Area | Implemented truth |
| --- | --- |
| Stage 6 result | The current Stage 6 result class remains `clean_null` and `limitation_bearing`. It must not be reinterpreted as a positive result without explicit approval. |
| Stage 2 through Stage 6 artifacts | Existing row universe, clean-window record, labels, splits, lockbox boundary, comparator roster, preprocessing manifests, saved predictions, metric policy, and Stage 6 result packet remain fixed evidence for the current benchmark family. |
| Stage 7C | Stage 7C is diagnostics-only contextual-bandit/ranking evidence with `benchmark_claim=false`. It is not live trading, final-execution training output, or Stage 6 reinterpretation. |
| Stage 8 | Stage 8 is local plan-first raw-update tooling only. It does not authorize live provider calls, raw overwrites, provider-completeness claims, benchmark reruns, or prediction outputs. |
| Stage 10C | Stage 10C is a local historical-prediction packet path using existing Stage 5 saved predictions. It is not persisted inference packaging, a live forecast system, a service/API/dashboard, a trading signal, or benchmark evidence. |
| Local operating mode | The project remains local CLI/artifact driven unless explicitly approved otherwise. |
| Deprecated archives | Deprecated v0p9 material is under `deprecated/v0p9/`; older v0p7 archive material is under `deprecated/v0p7/`. These are reference-only unless explicitly reintroduced through active docs. |

## 4. Active v1p0 Design Truth

These statements describe the selected next design direction. They require implementation, validation, and artifact evidence before becoming implemented truth.

| Area | v1p0 decision |
| --- | --- |
| Primary objective | Optimize performance and credibility together. Usability, operations, and publication readiness remain important, but the main near-term issue is the weak model stack. |
| Upgrade sequence | Strengthen market baselines first, then improve text/event representations, then test fusion/ranking. |
| Benchmark discipline | Preserve the existing benchmark family as much as possible while allowing explicitly versioned schema, feature, model, and diagnostic additions. |
| First milestone | Execute an integrated thin slice before heavier model expansion. |
| Versioning | Use two-tier versioning: benchmark-family version plus component-level feature/model/diagnostic versions. |
| Feature layout | Use a hybrid sidecar feature registry so current Stage 3 artifacts remain interpretable while new v1p0 features are mapped explicitly. |
| Data realism priority | Treat no-news, news-rich, truncation-risk, and article-count strata as first-class diagnostics. |
| Stage 10C priority | Improve Stage 10C wording, per-horizon tables, deterministic news context, caveats, and report fidelity tests in parallel with modeling work. |
| v1p0 first-slice code strategy | Rewrite minimal active v1p0 code rather than importing v0p9 modules. v0p9 code remains reference-only unless a future stage adds explicit compatibility tests for reuse. |
| v1p0 smoke environment | Execute the active first-slice smoke path under `~/venvs/ai`; fixed XGBoost is available there and should not be assumed available outside that environment. |

## 5. First Integrated Thin Slice

The first v1p0 implementation slice should be small enough to validate end-to-end and strong enough to address the weak-model-stack risk.

| Deliverable | Decision |
| --- | --- |
| Version manifest | Create a benchmark-family/component version manifest using v1p0 naming, such as `v1p0_model_upgrade_candidate_v1`. |
| Feature registry | Create a sidecar registry using v1p0 naming, such as `feature_registry_v1p0.yaml`, to map model variants to feature artifacts. |
| Market lag features | Add tabular lag/rolling market features as a versioned sidecar, not a silent mutation of existing Stage 3 artifacts. |
| Sequence window contract | Define the market sequence-window contract for later TSMixer work; manifest-only is acceptable before full implementation. |
| Lag-linear baseline | Add `market_lag_linear_v1` as a temporal sanity baseline. |
| Fixed XGBoost baseline | Add `market_xgboost_v1_fixed` as an honest stronger market hurdle. |
| Diagnostics core | Add train-gap capability where train predictions exist, strata tables, and first uncertainty evidence. |
| Stage 10C clarity | Improve report interpretation, horizon tables, deterministic aligned-news display, caveats, and report/data consistency tests. |
| Deferred contracts | Document but do not fully implement TSMixer, FinBERT ablations, XGBoost Optuna, and ensembles in the first thin slice unless explicitly scoped. |

## 6. Model And Feature Decisions

| Area | Decision |
| --- | --- |
| Market baseline suite | Target a ladder of `market_lag_linear_v1`, `market_xgboost_v1`, and `market_tsmixer_v1`, with future advanced temporal/foundation models tracked separately. |
| First boosted tree | Use XGBoost first. Maintain a fixed honest baseline before any tuned candidate. |
| XGBoost tuning | Add a mandatory nested Optuna candidate later, using purged/nested temporal folds, frozen choices before final evaluation, and no lockbox-guided search. |
| Tuning objective | Optimize hurdle delta with safeguards against one-sided gains, overfit gaps, and horizon instability. |
| Hurdle weights | Use primary-heavy horizon weights: 30% `1d`, 25% `5d`, 20% `10d`, 15% `20d`, 10% `60d`, with RMSE/MAE balanced. |
| Temporal neural model | Use TSMixer as the first compact temporal neural model. Implement it in pure PyTorch. |
| TSMixer strategy | Validate standalone first, then multiseed; nested TSMixer optimization only if standalone evidence is promising. |
| Text upgrade | Use a finance-specific FinBERT-style encoder as the first major event/text representation upgrade. |
| FinBERT aggregation | Compare aggregation strategies rather than guessing: mean, recency, top-k, and count-plus-recency. |
| Future market ensemble | Explore XGBoost plus TSMixer combinations after standalone models exist; the first higher-accuracy approach should be horizon-specific meta-combination rather than simple averaging. |
| Future market/event fusion | Use horizon-specific fusion as the first serious market plus event-state fusion candidate because event/news value likely differs by horizon. |

## 7. Evaluation, Diagnostics, And Claims

| Area | Decision |
| --- | --- |
| Lockbox discipline | No lockbox tuning. Search, preprocessing, combiners, learned transformations, and meta-models must be fold-local or nested. |
| Evidence before promotion | New variants are not serious candidates until diagnostics pass. |
| Core diagnostics | Include train-vs-validation gaps where train predictions exist, stratified metrics, and uncertainty evidence. |
| Strata | Report no-news, news-rich, truncation-risk, and article-count buckets. |
| Uncertainty | Implement date-clustered confidence intervals first; block bootstrap is required before final promotion. Diebold-Mariano and permutation tests remain later candidates. |
| Saved predictions | Metrics and comparisons should be computed from saved out-of-sample predictions with provenance and manifests. |
| Ranking and policy outputs | Stage 7-style ranking/bandit work remains diagnostic unless later explicitly approved for final-execution/live-use output status. |
| Result language | Continue allowing positive, conditional-positive, and clean-null outcomes as valid scientific results. |

## 8. Stage 10C Output Decisions

| Area | Decision |
| --- | --- |
| Output status | Current Stage 10C output remains `historical_prediction` or `diagnostic_only` where appropriate. Reserve `forecast_candidate` for separately approved future-row or refreshed-artifact semantics. |
| Invocation | Keep the implemented path as a local artifact CLI consuming explicit artifact roots and data cutoffs. |
| Source method | Use saved-prediction extraction for the first path. Persisted inference packaging remains separate future architecture work requiring approval. |
| Output root | Use governed, versioned `data/prediction_outputs/...` packets, separate from Stage 6 benchmark evidence. |
| Report format | Static HTML plus CSV/Parquet/manifest packet remains the preferred local format. No local dashboard is approved. |
| Ranking display | Primary per-horizon top tables may rank by selected event-state model prediction; delta over market hurdle is secondary; cross-horizon score is tertiary diagnostic only. |
| News context | Use deterministic aligned-news fields and optional deterministic snippets only if validated. No LLM summaries for the first implementation. |
| Trajectory graphs | Show historical observed context plus forecast markers; no projected price paths or horizon fan charts. |
| Validation | Packet/report validation must cover manifest identity, provenance, rows, horizons, cutoff correctness, rank determinism, report consistency, non-claims, no-network/service behavior, and sensitive-artifact exclusion. |

## 9. Out Of Scope Or Deferred

| Item | Status |
| --- | --- |
| Live provider calls | Not approved by this decision file. |
| Raw data overwrites or mutation | Not approved by this decision file. |
| Hidden Stage 2 through Stage 6 reruns | Not approved by this decision file. |
| Stage 6 reinterpretation | Not approved; current result remains `clean_null` and `limitation_bearing`. |
| Benchmark-comparability promotion | Not approved without explicit approval. |
| Live forecasts or new `forecast_candidate` semantics | Deferred; requires explicit approval. |
| Persisted inference package | Deferred; requires explicit approval. |
| Service/API/dashboard | Deferred/rejected for current phase. |
| Trading signals, buy/sell outputs, portfolio advice, shorting, transaction-cost reward | Not approved. |
| LLM summaries | Rejected for first implementation; future use needs separate reproducibility and governance approval. |
| Provider expansion | Deferred. |
| Full FinBERT ablation suite | Deferred until the first thin slice is stable. |
| TSMixer implementation beyond contract/standalone path | Deferred until the thin slice is stable unless separately scoped. |
| Nested Optuna XGBoost candidate | Required later, but not part of the minimal fixed-baseline slice unless explicitly scheduled. |
| XGBoost plus TSMixer ensemble | Future exploration after standalone models exist. |
| Market plus event horizon fusion | Future exploration after market/text upgrades exist. |

## 10. Resolved Or Deprecated v0p9 Decisions

These decisions remain historically important, but they are not the active v1p0 implementation plan unless restated above.

| Older decision/source | Current reconciliation |
| --- | --- |
| `ScopeDefinition.md` described the active root as a governance-first restart shell without active `src/`, configs, tests, README, or execution docs. | Stale for current repository state. Later active-root docs, scaffold, approved stages, tests, and artifacts exist. Preserve only as restart-history context. |
| `ScopeDefinition.md` treated many DQs as final owner decisions needed. | Resolved by later `ScopeDecisionLog.md` entries and implemented stages where applicable. Remaining approval gates still apply for protected scope changes. |
| `ScopeDefinition.md` recommended `1d/5d/20d` as the initial core horizons. | Superseded by later owner-approved active horizon set: `1d`, `5d`, `10d`, `20d`, `60d`. |
| Older provider references included Finnhub for company news. | Superseded for current phase by Twelve Data OHLCV, Alpha Vantage news, and SEC context, with provider-completeness limitations retained. |
| Static company metadata as phase-2 only. | Preserved. It remains out of current phase unless separately approved. |
| Uncertainty-aware outputs as later extension only. | For v1p0 design, uncertainty evidence is part of diagnostics before promotion. This does not reinterpret prior v0p9 results and should be versioned as new diagnostic work. |
| Older delayed-use news alignment example. | Superseded by the canonical same-day as-of-close rule for the current benchmark family. Any delayed-use alternative would be a separate benchmark family. |
| Historical missing-log/validator-failing claims. | Stale. Current operational memory and ledger exist and validator has passed in recent sessions. |
| Historical NaN-related ridge failure report. | Not clean current truth because later code/artifact evidence indicates median-imputation handling; preserve as historical caution only. |

## 11. Approval Gates Still Active

Explicit approval is required before any of the following:

| Gate | Examples |
| --- | --- |
| Benchmark-family change | Target family, horizon set, universe definition, provider stack, clean-window policy, alignment policy, evaluation protocol, comparator ladder, or metric/result policy changes treated as comparable. |
| Provider/data mutation | Live provider calls, raw overwrites, provider expansion, or provider-completeness claims. |
| Output-status expansion | Persisted inference package, new `forecast_candidate` semantics, live forecasts, final-execution training output, or scheduled automation. |
| Product-surface expansion | Service, API, dashboard, notebook-as-product, user-facing interactive UI, or publication artifact that implies unsupported claims. |
| Trading semantics | Buy/sell signals, price targets, portfolio recommendations, shorting, transaction-cost reward, or executable trading policy. |
| Result reinterpretation | Stage 6 reinterpretation, benchmark-comparability promotion, or claim upgrades beyond existing evidence. |
| Governance file edits | Edits to `AgentRules.md` or `docs/agent/Agent*.md` require explicit user approval. |
| Active-file deprecation/deletion | Active decision files should not be deleted or superseded without verified no-information-loss preservation and user approval. |

## 12. Open Implementation Planning Notes

| Topic | Note |
| --- | --- |
| Naming | Use `v1p0` for next implementation plans, folders, manifests, docs, and candidate artifact families. Do not relabel v0p9 artifacts as v1p0. |
| Thin-slice boundary | The minimal v1p0 slice should prioritize market lag features, fixed XGBoost, lag-linear, sidecar registry, diagnostics, strata, and Stage 10C clarity before heavier GPU/text/fusion work. |
| Comparability | Any v1p0 variant should be reported as a versioned candidate unless it exactly preserves the current benchmark contract. |
| Deprecated material | Use `deprecated/v0p9/` and `deprecated/v0p7/` only as reference/salvage sources, not active truth. |
| Memory | This file should be added to operational memory and guide future v1p0 planning prompts. |
