# Next Steps Brainstorming Decision Log

## Executive Summary

This document records the selected next-step roadmap for the financial event-state forecasting project after the manual-research synthesis and interactive brainstorming process. It is intentionally detailed so implementation can proceed smoothly without re-litigating why each decision was made.

The chosen direction is **performance and credibility first**, with usability, operations, and publication readiness treated as important parallel concerns. The main near-term technical concern is the **weak model stack**, not the existing evaluation scaffold. The project should therefore strengthen market baselines, text/event representations, and multimodal fusion while preserving the repository's core strengths: stagewise artifact contracts, leakage-aware splits, saved out-of-sample predictions, explicit non-claims, provider-risk flags, and local CLI/artifact boundaries.

The selected implementation path is an **Integrated Thin Slice** followed by controlled model expansion. The thin slice should introduce two-tier versioning, sidecar feature registries, lag/rolling market features, XGBoost, core diagnostics, and Stage 10C report clarity. Heavier GPU work, FinBERT ablations, TSMixer, and ensembles follow once the first slice is stable.

### Summary Of Decisions

| Area | Decision | Reasoning |
|---|---|---|
| Primary objective | Performance and credibility first; usability, operations, and publication readiness remain important | The current benchmark is scientifically disciplined but model stack is weak |
| Main risk | Weak model stack | Research identifies weak hash embeddings, same-row market features, and shallow fusion as main blockers |
| Upgrade sequence | All in sequence: market baselines, then text features, then fusion/ranking | Avoids testing event-state gains against a weak market hurdle |
| Benchmark contract | Mostly strict | Preserve comparability but allow versioned schema/feature additions |
| Compute budget | Heavy GPU acceptable | Enables TSMixer and FinBERT, but controls must prevent overfit |
| Credibility companion | All core diagnostics | New variants need train gaps, stratified metrics, and uncertainty evidence |
| Stage 10C priority | Do in parallel | Improve report interpretation while modeling work proceeds |
| Data realism priority | Truncation/no-news first | Provider truncation and no-news rows may condition event-state results |
| Stage 3 schema tolerance | Versioned changes | Allows new sidecar features without breaking old artifacts |
| Market baseline path | Minimal suite: lag-linear, XGBoost, TSMixer | Creates a clear hurdle ladder from simple to nonlinear to neural temporal |
| Temporal selection principle | Balanced choice | Accuracy, feasibility, reproducibility, leakage safety, and future fusion all matter |
| First temporal model | TSMixer first | Best balance of temporal modeling value and implementation complexity |
| Boosted tree choice | XGBoost first | User chose stronger first hurdle despite higher dependency burden |
| FinBERT priority | Balanced, ordered as accuracy, reproducibility, low complexity, finance specificity | Guides embedding/model-source choices |
| Text upgrade | FinBERT encoder | Strong finance-specific semantic upgrade over hash embeddings |
| FinBERT aggregation | Ablation suite | Compare mean, recency, top-k, count-plus-recency instead of guessing |
| Evidence gate | All core diagnostics | Required before serious promotion of new variants |
| Versioning | Two-tier versioning | Version benchmark family and individual components separately |
| First milestone | Integrated thin slice | Best balance of model progress and credibility infrastructure |
| XGBoost policy | Fixed honest baseline plus mandatory nested Optuna tuned candidate | Preserves honest baseline and enables accuracy-focused search |
| XGBoost tuning path | Nested Optuna path | Random/TPE/refinement inside purged nested folds, freeze before final evaluation |
| XGBoost budget | Aggressive, with overfitting controls | Accuracy is important, but lockbox/final evidence must remain protected |
| XGBoost objective | Hurdle delta | Optimizes direct improvement against the selected market hurdle |
| Hurdle-delta safeguard | Composite guarded objective | Penalize one-sided gains, overfit gaps, and horizon instability |
| Hurdle weights | 30% 1d, 25% 5d, 20% 10d, 15% 20d, 10% 60d; RMSE/MAE balanced | Primary-heavy while preserving longer-horizon evidence |
| Uncertainty | Two-method suite | Date-clustered CI first, block bootstrap before final promotion |
| Stage 10C bundle | Thin-slice bundle | Wording, per-horizon tables, news context policy, report fidelity tests |
| Data realism method | Stratified metrics | Report performance by no-news, news-rich, truncation-risk, article-count buckets |
| Feature windows | Two-tier windows | Standard tabular windows plus sequence-window contract for TSMixer |
| Feature layout | Hybrid sidecar registry | Preserve existing Stage 3 artifacts and map variants via registry |
| TSMixer implementation | Pure PyTorch only | Maximum control, future fusion fit, and artifact governance |
| TSMixer strategy | Standalone then optimize | Validate independently, then tune only if evidence shows promise |
| Future ensemble policy | Always explore | Explore XGBoost + TSMixer combinations after standalone models exist |
| First high-accuracy ensemble | Horizon meta | Horizon-specific regularized combiner fits the multi-horizon benchmark |
| First market+event fusion | Horizon-specific fusion | News/event value likely differs by horizon |
| Deferred/rejected now | Dashboard/API/service, live forecasts, trading signals, LLM summaries, provider expansion | Out of scope or premature until stronger evidence exists |

### First Integrated Thin Slice Deliverables

The first implementation milestone should produce these deliverables:

| Deliverable | Description | Expected output |
|---|---|---|
| Two-tier version manifest | Define benchmark-family and component versions | `phase2_model_upgrade_candidate_v1` metadata |
| Feature sidecar registry | Map model variants to sidecar feature artifacts | `feature_registry_phase2_candidate_v1.yaml` |
| Market lag/rolling features | Standard tabular lag/rolling features | `market_lag_rolling_v1_tabular.parquet` |
| Market sequence window contract | Fixed sequence windows for later TSMixer | `market_sequence_window_v1/` or manifest-only contract first |
| Lag-linear baseline | Sanity-check temporal tabular baseline | `market_lag_linear_v1` predictions and manifests |
| XGBoost fixed baseline | Honest stronger tabular hurdle | `market_xgboost_v1_fixed` predictions and manifests |
| Diagnostics core initial | Train gap, strata, and first uncertainty outputs | `diagnostics_core_v1` artifacts |
| Stratified metrics | No-news/news-rich/truncation/article-count slices | Stage 6 slice tables |
| Stage 10C clarity | Wording, per-horizon tables, deterministic news context, fidelity tests | Updated report generator and tests |
| Deferred contracts | TSMixer, FinBERT, XGBoost Optuna, ensembles documented but not all implemented immediately | Candidate manifests or design docs |

### Inputs Required

| Input | Purpose |
|---|---|
| Existing Stage 2 panel | Canonical row universe and timing metadata |
| Existing Stage 3 market/event/label artifacts | Baseline feature/label alignment |
| Existing Stage 4 splits | Purged/embargoed folds and lockbox |
| Existing Stage 5 saved predictions | Current baseline comparisons and Stage 10C source |
| Existing Stage 6 summaries | `clean_null` baseline and selected hurdles |
| Existing aligned-news and provider flags | No-news/truncation stratification |
| Existing Stage 10C packet | Report refactor and output-fidelity baseline |
| Manual research reports | Design justification and constraints |

### Outputs Required

| Output | Purpose |
|---|---|
| Versioned feature sidecars | Add new features without breaking old Stage 3 artifacts |
| Model registry entries | Make model-feature composition explicit |
| New saved predictions | Compare lag-linear and XGBoost against current baselines |
| Train diagnostic predictions | Compute train-vs-validation gaps without polluting claims |
| Stratified evaluation tables | Explain behavior under news/no-news/truncation conditions |
| Date-clustered confidence intervals | First uncertainty evidence |
| Block-bootstrap intervals | Stronger uncertainty follow-up before promotion |
| Updated Stage 10C report | Clear historical packet presentation |
| Report fidelity tests | Ensure rendered outputs match source tables |

### Non-Negotiable Constraints

| Constraint | Requirement |
|---|---|
| No lockbox tuning | Lockbox/final test evidence cannot guide search |
| No live forecast semantics | `forecast_candidate` remains deferred |
| No trading claims | No buy/sell/portfolio recommendation outputs |
| No provider calls by default | Data refresh remains plan-first and gated |
| Preserve old artifacts | Current Stage 2-6 and Stage 10C artifacts remain interpretable |
| Version every change | Feature/model/diagnostic variants must carry explicit IDs |
| Fold-local learning | Any learned preprocessing, tuning, combiner, or meta-model must be fold-local or nested |
| Diagnostics before promotion | New variants are not serious candidates until diagnostics pass |

## Complete Decision Process

### Decision 1: Primary Goal

**Question:** What is the primary objective for the next phase of the project?

**Options considered:** credibility first, performance first, usability first, operations first, publication first.

**User decision:** Performance and credibility first. All other aspects remain very important.

**Reasoning:** The current repository already has strong governance and artifact discipline, but the model stack is not competitive. However, performance improvements without credibility would undermine the repository's strongest asset. Therefore, both must be optimized together.

### Decision 2: Main Risk

**Question:** Given performance and credibility are both first-class goals, which failure mode worries you most right now?

**Options considered:** weak model stack, weak evidence stack, weak data realism, weak presentation, scope creep.

**User decision:** Weak model stack.

**Reasoning:** Manual research repeatedly identifies the current event representation and market baselines as weak. The Stage 6 `clean_null` result is credible, but it may reflect underpowered features/models more than absence of signal.

### Decision 3: First Modeling Upgrade Focus

**Question:** If the weak model stack is the top concern, where should the first modeling upgrade focus?

**Options considered:** text/event features, market baselines, fusion model, ranking objective, all in sequence.

**User decision:** All in sequence.

**Reasoning:** The correct order is to strengthen market baselines first, then improve text/event features, then test fusion/ranking. This avoids falsely claiming event-state value against an underpowered market hurdle.

### Decision 4: Benchmark Contract Strictness

**Question:** How strict should we be about preserving the current Stage 2-6 benchmark contract?

**Options considered:** very strict, mostly strict, flexible, new benchmark.

**User decision:** Mostly strict.

**Reasoning:** Preserve the existing universe, labels, splits, lockbox, and result logic as much as possible, but allow additive or versioned schema/feature/model changes when they are documented and validated.

### Decision 5: Compute Budget

**Question:** How much extra dependency and compute burden are acceptable for the next modeling phase?

**Options considered:** CPU only, small GPU ok, heavy GPU ok, cloud acceptable.

**User decision:** Heavy GPU ok.

**Reasoning:** This enables FinBERT embeddings and TSMixer/PyTorch work. The tradeoff is that reproducibility, dependency capture, and overfit controls become more important.

### Decision 6: Credibility Pairing

**Question:** Which credibility upgrade should run alongside the model upgrades rather than waiting until after them?

**Options considered:** stratified evaluation, train diagnostics, uncertainty tests, workflow reproducibility, all core diagnostics.

**User decision:** All core diagnostics.

**Reasoning:** New model variants should not be promoted on primary Stage 6 metrics alone. They need train-gap diagnostics, news/no-news/truncation strata, and uncertainty evidence.

### Decision 7: Stage 10C Priority

**Question:** How should we treat the current Stage 10C report/visualization work compared with modeling and diagnostics?

**Options considered:** do minimal now, do in parallel, do after model work, high priority now.

**User decision:** Do in parallel.

**Reasoning:** Report clarity matters because more model variants will make outputs harder to interpret. However, report work should not block model/diagnostic upgrades.

### Decision 8: Data Realism Priority

**Question:** For data realism, which issue should we prioritize first?

**Options considered:** truncation/no-news, universe bias, provider metadata, new data provider, defer data realism.

**User decision:** Truncation/no-news.

**Reasoning:** Event-state value depends heavily on whether rows have reliable aligned news. Truncation and no-news conditions must become first-class evaluation strata.

### Decision 9: Stage 3 Schema Tolerance

**Question:** What is your tolerance for changing Stage 3 feature schemas in the next phase?

**Options considered:** additive only, versioned changes, minimal changes, open redesign.

**User decision:** Versioned changes.

**Reasoning:** The next phase can introduce new feature schemas if they are explicitly versioned and do not silently break current artifacts.

## Market Benchmark Suite Decisions

### Decision 10: Market Model Upgrade Direction

**Question context:** The first serious market-model upgrade defines the stronger hurdle against which event-state features are tested. It affects Stage 3 feature design, Stage 5 model roster, Stage 6 comparisons, compute/runtime, and future multimodal credibility.

| Option | What It Means | Scientific Impact | Feasibility | Compute Cost | Leakage Risk | Reproducibility | Baseline Strength | Schema Impact | Maintenance | Time To Value | Overall |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Boosted trees | Add lag/rolling market features and models like LightGBM/XGBoost/CatBoost or sklearn HistGB variants | 8 | 8 | 8 | 8 | 8 | 8 | 6 | 7 | 8 | 77 |
| PatchTST/TSMixer | Add sequence windows over OHLCV and train compact temporal neural models | 9 | 5 | 5 | 6 | 5 | 8 | 5 | 5 | 5 | 63 |
| iTransformer/TimeXer | Add transformer-style sequence/exogenous-variable models | 9 | 4 | 4 | 5 | 4 | 9 | 4 | 4 | 4 | 57 |
| Foundation models | Try Chronos/TimesFM/Moirai-style pretrained forecasting models | 8 | 3 | 3 | 5 | 3 | 7 | 4 | 3 | 3 | 49 |
| Benchmark suite | Add lag-linear, boosted tree, and one compact temporal neural model as a controlled suite | 10 | 6 | 5 | 7 | 6 | 10 | 5 | 5 | 5 | 69 |

**Recommendation given during process:** Use Benchmark Suite as phase design.

**User decision:** Benchmark suite, with clear versioning path and future improvement tracking.

**Selected path:**

1. `market_lag_linear_v1`: lagged/rolling linear sanity baseline.
2. `market_xgboost_v1`: first strong boosted-tree hurdle.
3. `market_tsmixer_v1`: first compact temporal neural hurdle.
4. Track future improvements for more advanced temporal/foundation models.

### Decision 11: Temporal Model Selection Principle

**Question context:** Before choosing the exact compact temporal neural model, choose the selection criterion.

| Option | Accuracy Potential | Compatibility | Feasibility | Compute Cost | Leakage Risk | Reproducibility | Research Value | Future Fusion Fit | Maintenance | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Accuracy first | 10 | 5 | 4 | 4 | 5 | 4 | 8 | 8 | 4 | 4 | 56 |
| Simplicity first | 6 | 9 | 9 | 8 | 8 | 8 | 5 | 5 | 9 | 9 | 76 |
| Research relevance | 8 | 6 | 5 | 5 | 6 | 5 | 10 | 8 | 5 | 5 | 63 |
| Future fusion | 8 | 6 | 5 | 5 | 5 | 5 | 8 | 10 | 5 | 5 | 62 |
| Balanced choice | 8 | 8 | 7 | 7 | 7 | 7 | 8 | 8 | 7 | 7 | 74 |

**User decision:** Balanced choice.

**Reasoning:** The first temporal model should be strong enough to matter but simple enough to validate and reuse later.

### Decision 12: First Compact Temporal Model

| Option | Accuracy Potential | Compatibility | Feasibility | Compute Cost | Leakage Safety | Reproducibility | Research Value | Future Fusion Fit | Maintenance | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TSMixer | 8 | 8 | 8 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 73 |
| PatchTST | 9 | 7 | 6 | 6 | 6 | 6 | 9 | 8 | 6 | 6 | 69 |
| Small LSTM/GRU | 6 | 8 | 8 | 7 | 7 | 7 | 4 | 6 | 8 | 8 | 69 |
| Temporal CNN | 7 | 8 | 7 | 7 | 7 | 7 | 5 | 6 | 7 | 7 | 68 |
| Tiny Transformer | 8 | 6 | 5 | 5 | 5 | 5 | 7 | 8 | 5 | 5 | 59 |

**User decision:** TSMixer first.

**Reasoning:** TSMixer best balances temporal modeling value, implementation feasibility, and future fusion compatibility. PatchTST remains a later candidate.

### Decision 13: Boosted Tree Implementation

| Option | Accuracy Potential | Compatibility | Feasibility | Compute Cost | Leakage Safety | Reproducibility | Research Value | Feature Importance | Maintenance | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HistGradientBoosting | 7 | 10 | 10 | 9 | 8 | 9 | 6 | 7 | 10 | 10 | 86 |
| XGBoost | 9 | 7 | 7 | 8 | 8 | 7 | 9 | 9 | 7 | 7 | 78 |
| LightGBM | 9 | 6 | 6 | 9 | 8 | 6 | 9 | 9 | 6 | 6 | 74 |
| CatBoost | 8 | 6 | 6 | 7 | 8 | 7 | 8 | 8 | 6 | 6 | 70 |
| Two-step suite | 10 | 6 | 5 | 6 | 7 | 6 | 9 | 9 | 5 | 5 | 68 |

**Recommendation given during process:** HistGradientBoosting first for low dependency risk.

**User decision:** XGBoost.

**Reasoning:** User prioritized stronger baseline accuracy. XGBoost becomes the first serious boosted-tree hurdle despite dependency/versioning burden.

### Decision 14: XGBoost Tuning Policy

Initial options compared:

| Option | Accuracy Potential | Credibility | Feasibility | Compute Cost | Leakage Safety | Reproducibility | Maintenance | Comparability | Time To Value | Future Extensibility | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed conservative config | 7 | 10 | 9 | 9 | 10 | 10 | 9 | 10 | 9 | 7 | 90 |
| Tiny predeclared grid | 8 | 8 | 7 | 7 | 8 | 8 | 7 | 8 | 7 | 8 | 76 |
| Random/Bayesian search | 10 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 4 | 8 | 56 |
| Two-stage policy | 9 | 9 | 7 | 7 | 9 | 9 | 7 | 9 | 7 | 9 | 82 |
| Use defaults only | 6 | 8 | 10 | 10 | 9 | 9 | 10 | 8 | 10 | 5 | 85 |

**User decision:** Two-stage policy with mandatory second pass.

**Refinement requested by user:** Use a more ambitious exploration path:

```text
Phase 0: fixed honest baseline
Phase 1: 50 to 100 random trials
Phase 2: 150 to 300 Optuna TPE trials
Phase 3: 30 to 60 local refinement trials
Phase 4: final evaluation on untouched temporal test set
```

**Comparison of refined XGBoost tuning paths:**

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| User 4-phase search | 10 | 7 | 3 | 9 | 2 | 6 | 7 | 6 | 7 | 7 | 3 | 67 |
| Two-step frozen heuristic | 8 | 9 | 7 | 8 | 7 | 9 | 9 | 8 | 6 | 9 | 7 | 87 |
| Fold-internal tuning | 9 | 8 | 5 | 9 | 5 | 9 | 8 | 7 | 7 | 9 | 5 | 81 |
| Literature/default heuristic | 6 | 10 | 10 | 7 | 10 | 10 | 10 | 8 | 5 | 9 | 10 | 95 |
| Validation pilot grid | 8 | 8 | 7 | 8 | 7 | 7 | 9 | 8 | 6 | 7 | 7 | 79 |
| Successive halving/ASHA | 9 | 7 | 5 | 8 | 7 | 7 | 7 | 6 | 7 | 7 | 6 | 76 |
| Nested purged Optuna | 10 | 8 | 4 | 10 | 3 | 9 | 8 | 7 | 8 | 10 | 4 | 81 |
| Coarse-to-fine frozen grid | 8 | 9 | 6 | 8 | 6 | 9 | 9 | 8 | 6 | 9 | 6 | 84 |
| Small budget TPE only | 8 | 8 | 6 | 8 | 6 | 8 | 8 | 7 | 7 | 8 | 6 | 80 |

**User decision:** Nested Optuna path.

**Final selected XGBoost plan:**

```text
Phase 0: market_xgboost_v1_fixed honest baseline
Phase 1: random trials inside training/development only
Phase 2: Optuna TPE trials inside purged/nested temporal folds
Phase 3: local refinement inside the same nested framework
Phase 4: freeze chosen config or final tiny grid
Phase 5: final outer validation/lockbox evaluation once through Stage 6
```

**Final labels:**

| Model ID | Purpose |
|---|---|
| `market_xgboost_v1_fixed` | Honest fixed baseline |
| `market_xgboost_v2_nested_optuna_candidate` | Accuracy-focused tuned candidate |
| `market_xgboost_v2_frozen_final` | Only if candidate passes diagnostics and config is frozen |

### Decision 15: XGBoost Optuna Budget

**Question:** How aggressive should nested Optuna be?

**User decision:** Aggressive, always keeping overfitting under control and avoiding it.

**Reasoning:** Accuracy is a top priority, but the search must be nested, purged, and guarded.

### Decision 16: XGBoost Objective

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| RMSE primary | 8 | 10 | 10 | 7 | 9 | 9 | 10 | 9 | 6 | 8 | 10 | 96 |
| MAE primary | 7 | 10 | 10 | 8 | 9 | 9 | 10 | 9 | 6 | 8 | 10 | 96 |
| RMSE+MAE composite | 9 | 9 | 8 | 8 | 8 | 9 | 9 | 8 | 7 | 9 | 8 | 92 |
| Stage6-aligned hurdle delta | 10 | 8 | 6 | 9 | 7 | 8 | 8 | 8 | 7 | 10 | 6 | 87 |
| Ranking objective | 8 | 8 | 6 | 9 | 7 | 8 | 7 | 7 | 8 | 7 | 6 | 81 |
| Multi-objective | 10 | 7 | 4 | 9 | 6 | 7 | 7 | 6 | 8 | 8 | 4 | 76 |

**Recommendation given during process:** RMSE+MAE composite.

**User decision:** Hurdle delta.

**Reasoning:** User wants direct optimization for improvement over the selected market hurdle.

### Decision 17: Hurdle Delta Safeguard

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Direct hurdle delta | 10 | 7 | 7 | 9 | 7 | 5 | 8 | 8 | 7 | 5 | 7 | 80 |
| Nested hurdle delta | 10 | 8 | 5 | 10 | 5 | 9 | 8 | 8 | 7 | 9 | 5 | 84 |
| Composite guarded delta | 9 | 8 | 6 | 10 | 6 | 9 | 8 | 9 | 7 | 10 | 6 | 88 |
| Horizon-averaged delta | 9 | 8 | 6 | 9 | 6 | 8 | 8 | 8 | 7 | 8 | 6 | 83 |
| Primary-horizon-only delta | 8 | 9 | 7 | 8 | 7 | 8 | 8 | 9 | 6 | 8 | 7 | 85 |

**User decision:** Composite guarded.

**Selected objective structure:**

```text
objective =
  weighted_mean(primary_and_secondary_horizon_hurdle_deltas)
  + penalty_for_one_sided_improvement
  + penalty_for_train_validation_gap
  + penalty_for_horizon_instability
```

### Decision 18: Hurdle Delta Weights

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Primary-heavy balanced | 9 | 9 | 8 | 9 | 8 | 9 | 9 | 9 | 7 | 10 | 8 | 95 |
| Equal all horizons | 8 | 10 | 9 | 8 | 8 | 9 | 9 | 9 | 7 | 8 | 9 | 94 |
| Short-horizon only | 8 | 9 | 9 | 8 | 9 | 8 | 9 | 9 | 6 | 8 | 9 | 92 |
| Volatility-normalized | 9 | 8 | 6 | 9 | 7 | 8 | 8 | 7 | 7 | 8 | 6 | 83 |
| Adaptive weights | 10 | 5 | 4 | 8 | 6 | 5 | 6 | 4 | 7 | 5 | 4 | 64 |

**User decision:** Primary-heavy with explicit weights:

| Horizon | Weight |
|---|---:|
| 1d | 30% |
| 5d | 25% |
| 10d | 20% |
| 20d | 15% |
| 60d | 10% |

RMSE and MAE are balanced 50/50 within the objective.

## Text/Event Representation Decisions

### Decision 19: Text Representation Priority

**Question:** Before choosing the first text/event representation upgrade, what should matter most for semantic embeddings?

**User decision:** Balanced, ordered as accuracy, reproducibility, low complexity, finance specificity.

### Decision 20: First Text/Event Representation Upgrade

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Specificity | Compute Cost | Leakage Safety | Schema Fit | Maintenance | Future Fusion | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FinBERT-style encoder | 8 | 8 | 7 | 10 | 7 | 8 | 8 | 7 | 8 | 7 | 78 |
| Finance sentence embeddings | 9 | 7 | 6 | 9 | 6 | 8 | 8 | 6 | 9 | 6 | 74 |
| General sentence transformer | 7 | 9 | 9 | 5 | 8 | 8 | 8 | 8 | 7 | 9 | 78 |
| Local LLM embeddings | 9 | 5 | 3 | 7 | 3 | 6 | 6 | 3 | 9 | 3 | 54 |
| Provider sentiment/features | 6 | 8 | 8 | 8 | 9 | 8 | 7 | 8 | 5 | 8 | 75 |
| Hybrid first pass | 9 | 8 | 6 | 9 | 6 | 8 | 8 | 6 | 9 | 6 | 75 |

**User decision:** FinBERT encoder.

**Reasoning:** Strong first semantic finance upgrade over hash embeddings, with provider metadata and finance sentence models tracked as later candidates.

### Decision 21: FinBERT Aggregation Strategy

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Noise Robustness | Schema Fit | Interpretability | Future Fusion | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mean pooling | 6 | 10 | 10 | 7 | 9 | 9 | 5 | 9 | 8 | 5 | 78 |
| Recency weighted | 8 | 9 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | 7 | 79 |
| Top-k recent | 8 | 9 | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 7 | 79 |
| Count plus recency | 8 | 9 | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 7 | 81 |
| Ablation suite | 10 | 8 | 6 | 9 | 6 | 8 | 9 | 7 | 9 | 9 | 81 |

**User decision:** Ablation suite.

**Selected variants:**

| Variant | Purpose |
|---|---|
| `event_hash_v0` | Current baseline |
| `event_finbert_mean_v1` | Direct semantic mean-pooling replacement |
| `event_finbert_recency_v1` | Recency-weighted pooling |
| `event_finbert_topk_v1` | Top-k recent article pooling |
| `event_finbert_count_recency_v1` | Combined semantic + scalar count/recency/provider flags |

### Decision 22: FinBERT Source Strategy

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Maintenance | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hugging Face pinned | 8 | 8 | 8 | 9 | 7 | 8 | 8 | 7 | 8 | 7 | 9 | 87 |
| Local vendored weights | 8 | 10 | 5 | 9 | 7 | 9 | 8 | 7 | 8 | 6 | 5 | 82 |
| Finance sentence transformer | 9 | 7 | 7 | 8 | 7 | 8 | 8 | 7 | 9 | 7 | 7 | 84 |
| Compare two encoders | 10 | 7 | 5 | 9 | 5 | 8 | 7 | 8 | 10 | 5 | 5 | 79 |
| Defer exact model | 5 | 10 | 9 | 6 | 10 | 10 | 9 | 6 | 7 | 9 | 8 | 89 |

**User decision:** Hugging Face pinned.

**Requirements:**

| Requirement | Detail |
|---|---|
| Model pinning | Exact model ID and revision/hash |
| Tokenizer pinning | Exact tokenizer ID and revision/hash |
| Cache | Article embedding cache with text hash and model config hash |
| Offline rerun | No internet required after cache materialization |
| License/model card | Must be reviewed before serious promotion |

### Decision 23: FinBERT Extraction Policy

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Maintenance | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CLS embedding | 7 | 10 | 10 | 8 | 9 | 9 | 9 | 7 | 7 | 9 | 10 | 95 |
| Mean token pooling | 8 | 9 | 8 | 8 | 8 | 9 | 9 | 7 | 8 | 8 | 8 | 90 |
| Sentiment logits only | 6 | 10 | 10 | 9 | 10 | 9 | 10 | 9 | 5 | 10 | 10 | 98 |
| Embedding + logits | 9 | 9 | 7 | 9 | 8 | 9 | 8 | 9 | 9 | 7 | 7 | 91 |
| Compare extraction methods | 10 | 8 | 5 | 9 | 6 | 9 | 7 | 8 | 10 | 5 | 5 | 82 |

**User decision:** Embedding + logits.

**Selected extraction:** Mean token embedding plus sentiment logits/probabilities if supported by the pinned model.

**Version labels:**

| Artifact | Purpose |
|---|---|
| `article_finbert_mean_embedding_v1` | Semantic article embedding |
| `article_finbert_sentiment_logits_v1` | Compact finance sentiment sidecar |
| `event_finbert_mean_plus_logits_v1` | Combined article representation |

## Diagnostics And Evidence Decisions

### Decision 24: Evidence Gate

| Option | Credibility | Feasibility | Compute Cost | Leakage Safety | Overfit Detection | Data Realism | Statistical Rigor | Maintenance | Time To Value | Promotion Safety | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| All core diagnostics | 10 | 6 | 5 | 9 | 10 | 9 | 9 | 6 | 5 | 10 | 79 |
| Stratified first | 8 | 8 | 7 | 8 | 5 | 10 | 5 | 8 | 8 | 7 | 74 |
| Train gap first | 8 | 8 | 7 | 8 | 10 | 5 | 5 | 8 | 8 | 7 | 74 |
| Uncertainty first | 8 | 6 | 6 | 7 | 6 | 5 | 10 | 6 | 6 | 8 | 68 |
| Light gate | 4 | 10 | 10 | 6 | 3 | 3 | 3 | 10 | 10 | 3 | 62 |

**User decision:** All core diagnostics.

**Required before serious promotion:**

1. Train-vs-validation gap diagnostics.
2. News/no-news/truncation/provider-risk strata.
3. Uncertainty intervals/tests.

### Decision 25: Uncertainty Method

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Statistical Validity | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Date-clustered CI | 7 | 9 | 9 | 8 | 9 | 9 | 9 | 9 | 7 | 7 | 9 | 91 |
| Block bootstrap | 8 | 8 | 7 | 9 | 7 | 8 | 8 | 7 | 8 | 9 | 7 | 86 |
| Diebold-Mariano style | 8 | 8 | 5 | 9 | 8 | 8 | 7 | 5 | 7 | 8 | 5 | 78 |
| Permutation test | 6 | 8 | 6 | 6 | 6 | 8 | 7 | 6 | 6 | 6 | 6 | 71 |
| Two-method suite | 9 | 8 | 6 | 9 | 6 | 8 | 8 | 8 | 8 | 10 | 6 | 86 |

**User decision:** Two-method suite.

**Implementation order:**

1. `uncertainty_date_clustered_ci_v1`: first implementation.
2. `uncertainty_block_bootstrap_v1`: mandatory before final promotion.
3. Diebold-Mariano and permutation tests remain future candidates.

### Decision 26: Truncation/No-News Strategy

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Data Realism | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Measure only | 5 | 10 | 10 | 8 | 10 | 10 | 10 | 9 | 7 | 7 | 10 | 96 |
| Stratified metrics + flags | 7 | 9 | 8 | 9 | 9 | 10 | 9 | 10 | 8 | 9 | 8 | 96 |
| Truncation refinement | 8 | 7 | 5 | 9 | 5 | 7 | 7 | 8 | 8 | 10 | 5 | 79 |
| No-news model branch | 8 | 8 | 6 | 8 | 7 | 8 | 7 | 8 | 8 | 9 | 6 | 83 |
| Full data-quality program | 9 | 7 | 4 | 9 | 4 | 7 | 6 | 9 | 9 | 10 | 4 | 78 |

**User decision:** Stratified metrics.

**Required strata:**

| Stratum | Purpose |
|---|---|
| `no_news_flag` true/false | Separate no-news rows from news rows |
| `provider_truncation_risk_flag` true/false | Measure effect of likely incomplete news coverage |
| Article-count buckets | Compare `0`, `1-2`, `3-5`, `6+` aligned articles |
| News-rich vs news-sparse | Identify conditional event-state signal |

## Versioning, Features, And Layout Decisions

### Decision 27: Versioning Structure

| Option | Comparability | Flexibility | Feasibility | Reproducibility | Maintenance | Artifact Clarity | Scope Safety | Future Extensibility | Time To Value | Research Fit | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Single new benchmark family | 9 | 6 | 7 | 8 | 7 | 9 | 9 | 7 | 7 | 8 | 77 |
| Incremental variants under current family | 8 | 8 | 8 | 7 | 8 | 7 | 8 | 8 | 8 | 7 | 77 |
| Separate experiment branches | 6 | 10 | 6 | 6 | 5 | 6 | 6 | 9 | 6 | 7 | 67 |
| Full matrix versioning | 10 | 10 | 4 | 7 | 4 | 8 | 7 | 10 | 3 | 9 | 72 |
| Two-tier versioning | 10 | 9 | 7 | 9 | 7 | 9 | 9 | 10 | 7 | 10 | 87 |

**User decision:** Two-tier versioning.

**Selected IDs:**

| Component | Version |
|---|---|
| Benchmark family | `phase2_model_upgrade_candidate_v1` |
| Market features | `market_lag_rolling_v1`, `market_sequence_window_v1` |
| Market models | `market_lag_linear_v1`, `market_xgboost_v1`, `market_tsmixer_v1` |
| Event features | `event_hash_v0`, `event_finbert_*_v1` |
| Diagnostics | `diagnostics_core_v1` |
| Promotion gate | `promotion_gate_core_v1` |

### Decision 28: First Milestone

| Option | Scientific Value | Feasibility | Risk Control | Time To Value | Reproducibility | Performance Upside | Credibility Upside | Scope Control | Maintenance | Future Extensibility | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Diagnostics foundation first | 8 | 8 | 10 | 7 | 9 | 4 | 10 | 9 | 8 | 8 | 81 |
| Market suite first | 9 | 7 | 7 | 8 | 7 | 9 | 6 | 8 | 7 | 8 | 76 |
| Event FinBERT first | 9 | 5 | 6 | 6 | 6 | 9 | 6 | 6 | 5 | 9 | 67 |
| Stage 10C first | 5 | 9 | 9 | 9 | 7 | 2 | 6 | 10 | 8 | 7 | 72 |
| Integrated thin slice | 10 | 6 | 8 | 7 | 8 | 8 | 9 | 8 | 6 | 10 | 80 |

**User decision:** Integrated thin slice.

### Decision 29: Lag/Rolling Feature Window Policy

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Feature Strength | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Minimal windows | 6 | 10 | 10 | 7 | 10 | 10 | 10 | 9 | 6 | 6 | 10 | 94 |
| Standard windows | 8 | 9 | 8 | 9 | 9 | 9 | 8 | 8 | 8 | 8 | 8 | 92 |
| Rich technical set | 9 | 7 | 5 | 8 | 7 | 7 | 6 | 6 | 8 | 10 | 5 | 78 |
| TSMixer-aligned windows | 8 | 8 | 7 | 8 | 8 | 8 | 7 | 7 | 10 | 8 | 7 | 86 |
| Two-tier windows | 9 | 9 | 7 | 9 | 8 | 9 | 8 | 8 | 10 | 9 | 7 | 93 |

**User decision:** Two-tier windows.

**Selected tabular windows:**

| Feature family | Windows |
|---|---|
| Returns | 1d, 5d, 10d, 20d, 60d |
| Realized volatility | 5d, 20d, 60d |
| Volume z-score/ratio | 5d, 20d, 60d |
| Rolling high-low range | 5d, 20d |
| Drawdown from rolling max | 20d, 60d |
| Market-relative rolling return | 5d, 20d, 60d if leakage-safe |

**Selected sequence windows:**

| Window | Role |
|---|---|
| 20d | Short context |
| 60d | Medium context |
| 126d | Longer-context candidate after stability |

### Decision 30: Feature Layout

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Backward Compatibility | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sidecar artifacts | 7 | 10 | 8 | 8 | 9 | 10 | 10 | 8 | 8 | 10 | 8 | 96 |
| Replace Stage 3 schema | 8 | 7 | 5 | 8 | 8 | 7 | 5 | 7 | 8 | 4 | 5 | 72 |
| Feature registry | 9 | 9 | 6 | 9 | 8 | 9 | 9 | 9 | 10 | 9 | 6 | 92 |
| Separate phase2 root | 8 | 9 | 7 | 8 | 8 | 9 | 8 | 8 | 9 | 9 | 7 | 90 |
| Hybrid sidecar registry | 9 | 10 | 7 | 9 | 8 | 10 | 10 | 9 | 10 | 10 | 7 | 99 |

**User decision:** Hybrid sidecar registry.

**Selected layout examples:**

```text
features/market_lag_rolling_v1.parquet
features/market_sequence_window_v1/
features/event_finbert_mean_v1.parquet
features/event_finbert_recency_v1.parquet
configs/feature_registry_phase2_candidate_v1.yaml
configs/model_registry_phase2_candidate_v1.yaml
```

## TSMixer And Temporal Neural Decisions

### Decision 31: External Library Comparison

The user requested comparison of at least five external library options against Pure PyTorch.

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Maintenance | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure PyTorch | 8 | 8 | 6 | 8 | 7 | 9 | 9 | 7 | 10 | 8 | 6 | 86 |
| Nixtla NeuralForecast | 9 | 7 | 8 | 8 | 7 | 7 | 7 | 7 | 8 | 7 | 9 | 84 |
| Darts | 8 | 7 | 8 | 7 | 7 | 6 | 6 | 7 | 7 | 7 | 8 | 78 |
| PyTorch Forecasting | 8 | 7 | 6 | 8 | 7 | 7 | 6 | 8 | 8 | 6 | 6 | 77 |
| GluonTS | 8 | 7 | 6 | 7 | 7 | 6 | 5 | 7 | 7 | 6 | 6 | 72 |
| tsai | 8 | 7 | 7 | 7 | 7 | 7 | 6 | 6 | 7 | 6 | 7 | 75 |
| AutoGluon TimeSeries | 8 | 6 | 9 | 7 | 6 | 5 | 5 | 6 | 6 | 5 | 9 | 72 |

**Recommendation given during process:** Two-track policy with Pure PyTorch serious track and NeuralForecast exploratory reference.

**User decision:** Pure PyTorch only.

**Reasoning:** Maximum control over artifacts, leakage-safe windows, seeds, saved predictions, and future fusion.

### Decision 32: TSMixer Strategy

Initial options compared:

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed small config | 6 | 10 | 10 | 7 | 9 | 10 | 9 | 8 | 7 | 9 | 9 | 94 |
| Tiny grid | 8 | 8 | 7 | 8 | 7 | 8 | 8 | 7 | 8 | 8 | 7 | 84 |
| Multi-seed fixed | 7 | 9 | 8 | 8 | 7 | 9 | 8 | 8 | 8 | 9 | 7 | 88 |
| Nested Optuna | 9 | 6 | 4 | 8 | 3 | 7 | 7 | 5 | 9 | 7 | 4 | 69 |
| Fixed then multi-seed | 8 | 9 | 8 | 8 | 7 | 9 | 8 | 8 | 9 | 10 | 7 | 91 |

The user proposed a more coupled XGBoost/TSMixer plan involving XGBoost profiles and TSMixer optimization. It was refined as follows:

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| User coupled 3-phase ladder | 10 | 7 | 3 | 10 | 2 | 7 | 7 | 7 | 9 | 8 | 3 | 73 |
| Fixed then multiseed TSMixer | 8 | 9 | 8 | 8 | 7 | 9 | 8 | 8 | 9 | 10 | 7 | 91 |
| Independent nested TSMixer Optuna | 9 | 7 | 4 | 8 | 3 | 8 | 7 | 6 | 9 | 8 | 4 | 73 |
| XGBoost profiles + fixed TSMixer | 9 | 8 | 6 | 9 | 5 | 8 | 8 | 8 | 8 | 9 | 5 | 83 |
| XGBoost profiles + nested TSMixer | 10 | 7 | 4 | 10 | 2 | 8 | 7 | 7 | 9 | 9 | 3 | 76 |
| Standalone first, ensemble later | 10 | 8 | 5 | 9 | 4 | 9 | 8 | 8 | 10 | 10 | 4 | 85 |

**User decision:** Standalone then optimize.

**Selected TSMixer path:**

1. Validate TSMixer independently.
2. Start with smoke/default tiny parameters.
3. Run fixed/multiseed discipline.
4. Nested TSMixer optimization only if standalone evidence shows promise.
5. XGBoost remains the credible hurdle, not a weakened target.

## Ensemble And Fusion Decisions

### Decision 33: Future XGBoost + TSMixer Ensemble Rule

**Question:** What should be the rule for allowing future XGBoost + TSMixer ensembles or meta-combiners?

**Options considered:** only if complementary, always explore, defer entirely, if TSMixer wins, if XGBoost wins.

**User decision:** Always explore.

**Reasoning:** The user wants high-accuracy combined candidates explored after standalone models exist.

### Decision 34: High-Accuracy Ensemble Type

The user rejected simple average and fixed weighted average as too low ambition and requested higher-accuracy options.

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fold-local ridge combiner | 8 | 9 | 8 | 8 | 8 | 9 | 8 | 9 | 8 | 9 | 8 | 92 |
| Elastic-net meta-combiner | 9 | 8 | 7 | 9 | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 88 |
| Horizon-specific meta-combiner | 9 | 8 | 7 | 10 | 8 | 8 | 8 | 8 | 9 | 8 | 7 | 90 |
| Regime-gated combiner | 10 | 7 | 5 | 10 | 7 | 7 | 7 | 7 | 10 | 7 | 5 | 82 |
| News-state/data-quality gate | 9 | 8 | 6 | 10 | 7 | 8 | 7 | 8 | 10 | 8 | 6 | 87 |
| Residual stack XGB to TSMixer | 10 | 7 | 5 | 9 | 6 | 7 | 7 | 6 | 10 | 7 | 5 | 79 |
| Residual stack TSMixer to XGB | 10 | 7 | 5 | 9 | 6 | 7 | 7 | 6 | 10 | 7 | 5 | 79 |
| Gradient-boosted meta-model | 10 | 7 | 5 | 9 | 7 | 6 | 7 | 6 | 9 | 6 | 5 | 77 |
| Neural mixture-of-experts | 10 | 6 | 3 | 10 | 5 | 5 | 6 | 5 | 10 | 5 | 3 | 68 |
| Rank-aware meta-combiner | 9 | 8 | 6 | 10 | 7 | 8 | 7 | 7 | 9 | 8 | 6 | 85 |

**User decision:** Horizon meta.

**Selected candidate:** `market_xgb_tsmixer_horizon_meta_v1`, a horizon-specific regularized meta-combiner.

### Decision 35: Market + FinBERT Fusion

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Promotion Safety | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Late fusion ridge | 8 | 10 | 9 | 8 | 9 | 10 | 9 | 10 | 8 | 10 | 9 | 100 |
| XGBoost joint features | 9 | 8 | 8 | 9 | 8 | 8 | 8 | 7 | 8 | 8 | 8 | 89 |
| Horizon-specific fusion | 9 | 9 | 7 | 10 | 8 | 9 | 8 | 9 | 9 | 9 | 7 | 93 |
| News-state gated fusion | 10 | 8 | 6 | 10 | 7 | 8 | 8 | 9 | 10 | 8 | 6 | 90 |
| Neural cross-fusion | 10 | 6 | 3 | 10 | 4 | 6 | 6 | 5 | 10 | 6 | 3 | 69 |
| Defer fusion | 3 | 10 | 10 | 6 | 10 | 10 | 10 | 7 | 6 | 10 | 10 | 92 |

**User decision:** Horizon-specific fusion.

**Selected candidate:** `event_market_horizon_fusion_v1`, a horizon-specific regularized fusion design.

**Reasoning:** Event/news value likely differs by horizon. A horizon-specific fusion model gives higher accuracy potential than one global combiner while remaining more interpretable and safer than neural cross-fusion.

## Stage 10C And Reporting Decisions

### Decision 36: Stage 10C Thin-Slice Bundle

| Option | Accuracy Potential | Reproducibility | Low Complexity | Finance Fit | Compute Cost | Leakage Safety | Schema Fit | Interpretability | Future Fusion | Validation Strength | Time To Value | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Wording only | 1 | 9 | 10 | 8 | 10 | 10 | 10 | 6 | 5 | 5 | 10 | 84 |
| Per-horizon tables | 2 | 9 | 8 | 8 | 9 | 10 | 9 | 9 | 7 | 7 | 8 | 86 |
| News context policy | 2 | 8 | 7 | 9 | 8 | 9 | 8 | 9 | 8 | 8 | 7 | 83 |
| Static charts | 2 | 7 | 6 | 8 | 7 | 9 | 7 | 9 | 7 | 7 | 6 | 75 |
| Report fidelity tests | 1 | 10 | 7 | 8 | 8 | 10 | 9 | 8 | 8 | 10 | 7 | 86 |
| Thin-slice bundle | 2 | 9 | 7 | 9 | 8 | 10 | 8 | 10 | 8 | 10 | 7 | 88 |

**User decision:** Thin-slice bundle.

**Required components:**

1. Non-claim wording refresh.
2. Per-horizon top-10 tables.
3. Deterministic relevant-news context policy.
4. Report/data fidelity tests.
5. Static chart bundle deferred to a later candidate.

## Deferred And Rejected Current-Phase Ideas

### Decision 37: Worst/Deferred Next Steps

**Question:** Which ideas should be explicitly marked as worst/deferred next steps for now?

**User decision:** Dashboard/API/service, live forecasts, trading signals, LLM summaries, provider expansion, all of these.

| Deferred idea | Reason |
|---|---|
| Dashboard/API/service | Outside current local artifact boundary; premature before stronger evidence |
| Live forecasts / `forecast_candidate` | Requires model packaging, feature freshness contracts, and new semantics |
| Trading signals | Current evidence is `clean_null`; trading/advice claims are disallowed |
| LLM summaries | Nondeterministic, costly, and unnecessary before deterministic snippets/FinBERT are proven |
| Provider expansion | Current Alpha Vantage truncation/no-news behavior should be measured first |

## Final Selected Roadmap

### Milestone 1: Integrated Thin Slice

Implement:

1. `phase2_model_upgrade_candidate_v1` two-tier versioning.
2. `feature_registry_phase2_candidate_v1.yaml` and model registry.
3. `market_lag_rolling_v1_tabular` sidecar features.
4. `market_sequence_window_v1` contract.
5. `market_lag_linear_v1`.
6. `market_xgboost_v1_fixed`.
7. `diagnostics_core_v1` initial pieces: train predictions, stratified metrics, date-clustered CI.
8. Stage 10C thin-slice bundle.

Do not yet implement:

1. TSMixer nested optimization.
2. FinBERT full ablation suite.
3. XGBoost + TSMixer horizon meta.
4. Market + event horizon fusion.
5. Live forecasts, dashboard, trading, LLM summaries, provider expansion.

### Milestone 2: XGBoost Tuned Candidate

Implement:

1. `market_xgboost_v2_nested_optuna_candidate`.
2. Aggressive nested Optuna path.
3. Composite guarded hurdle-delta objective.
4. Horizon weights: 30/25/20/15/10.
5. RMSE/MAE balanced within objective.
6. Block-bootstrap uncertainty before promotion.

### Milestone 3: FinBERT Event Representation

Implement:

1. Hugging Face pinned FinBERT source.
2. Article embedding cache with checksums.
3. Mean embedding + sentiment logits extraction.
4. Ablation suite: mean, recency, top-k, count-plus-recency.
5. Comparison against `event_hash_v0`.

### Milestone 4: TSMixer Standalone

Implement:

1. Pure PyTorch `market_tsmixer_v1`.
2. Smoke/default tiny parameter test.
3. Fixed/multiseed evaluation.
4. Nested optimization only if standalone evidence is promising.

### Milestone 5: Ensembles And Fusion

Implement after standalone evidence:

1. `market_xgb_tsmixer_horizon_meta_v1`.
2. `event_market_horizon_fusion_v1`.
3. Optional later: regime gate, news-state gate, residual stack, rank-aware meta.

## Promotion Rules

Any serious candidate must satisfy:

| Requirement | Meaning |
|---|---|
| Full Stage 6 pass | Candidate evaluated through canonical saved predictions and metrics |
| Train-gap diagnostic | No unacceptable train/validation overfit behavior |
| Stratified diagnostics | News/no-news/truncation/article-count behavior understood |
| Date-clustered CI | First uncertainty evidence present |
| Block bootstrap | Required before final promotion |
| Lockbox untouched until final | Search/tuning cannot use final lockbox evidence |
| Versioned artifacts | Feature/model/diagnostic IDs explicit |
| Non-claims preserved | No trading/live/price-target claims |

## Research Context Used

The decisions above are grounded in the manual-research archive now located under `docs/research/manual_research/`.

### `research_1`: Daily/Weekly Data Refresh Design

Important context:

| File | Contribution |
|---|---|
| `docs/research/manual_research/research_1/results/DeepResearchReport_DailyWeekly Data Refresh Design.md` | Established plan-first refresh design, overlapping windows, idempotency, provider-safety, no-overwrite defaults, redaction, manifests, and downstream invalidation rules |

Key takeaways used:

1. Stage 8 should remain plan-first by default.
2. Live provider calls require explicit approval.
3. Raw data changes invalidate downstream Stage 2-6/10C artifacts.
4. Secret redaction and request ledgers require careful design.
5. No provider completeness, benchmark refresh, or prediction refresh should be claimed from raw updates alone.

### `research_2`: Trajectory Graph Visualization

Important context:

| File | Contribution |
|---|---|
| `docs/research/manual_research/research_2/results/DRR-trajectory graph visualization.md` | Defined safe trajectory visualization: historical excess returns/markers only, no future price paths, no fan charts, no trading signals |

Key takeaways used:

1. Visuals must show historical model outputs, not future price projections.
2. Stage 10C charts must preserve `clean_null` and limitation-bearing caveats.
3. Existing `trajectory_points` can support display-only improvements.

### `research_3`: Relevant News Attribution And Ranking

Important context:

| File | Contribution |
|---|---|
| `docs/research/manual_research/research_3/results/DRR-Relevant News Attribution for Stage 10C Ranking and Display Policy.md` | Recommended deterministic news ranking by recency/ticker relevance, context-only wording, no causal explanations, no LLM summaries |
| `docs/research/manual_research/research_3/results/DRR-Relevance signals for news ranking.md` | Clarified available current signals: timestamp, article count, no-news/truncation flags; sentiment/topics are not currently extracted unless added |

Key takeaways used:

1. Relevant news should be context, not causal explanation.
2. Display should be deterministic and as-of safe.
3. No URLs/full text/LLM summaries in first pass.
4. No-news and truncation flags should remain visible.

### `research_4`: Visualization And Future Pipeline Architecture

Important context:

| File | Contribution |
|---|---|
| `docs/research/manual_research/research_4/results/DRR-Top-10 Multi-Horizon Visualization.md` | Recommended per-horizon static views, cross-horizon diagnostics, tables as source of truth, accessibility, non-claims |
| `docs/research/manual_research/research_4/results/DRR-Top-Decision Ready Memo for the Future Local Update To Prediction Pipeline Architecture.md` | Recommended local lockfile-backed DAG/workflow reproducibility as target architecture; deferred offline inference bundle |

Key takeaways used:

1. Stage 10C should use per-horizon sections and clear non-claims.
2. Static report improvements should remain local/offline.
3. Workflow-level reproducibility should improve without replacing validators.
4. Future-row inference bundle is deferred.

### `research_5`: Repository-Wide Benchmark And SOTA Assessment

Important context:

| File | Contribution |
|---|---|
| `docs/research/manual_research/research_5/results/DRR1-ValdiviaEng Financial Event State Forecasting.md` | Identified the repo as a strong benchmark harness with weak model stack; recommended text encoders, stronger market baselines, diagnostics |
| `docs/research/manual_research/research_5/results/DRR2-ValdiviaEng Financial Event State Forecasting_in-double-detail.md` | Highlighted frozen-universe sensitivity, richer text inputs, strong tabular baselines, FinBERT late fusion, ranking-aware models |
| `docs/research/manual_research/research_5/results/DRR3-ValdiviaEng Financial Event State Forecasting_in-triple-detail.md` | Emphasized modern time-series models, semantic embeddings, saved train predictions, environment/reproducibility gaps |
| `docs/research/manual_research/research_5/results/DRR4-ValdiviaEng Financial Event State Forecasting_extended_4.md` | Compared repo against recent SOTA such as PatchTST/iTransformer/TimeXer/Chronos and multimodal finance methods |
| `docs/research/manual_research/research_5/results/DRR5-Recommended view layout.md` | Recommended per-horizon views, ranking display, caveats, schema-compatible display refinements |
| `docs/research/manual_research/research_5/results/DRR6-Executive Summary.md` | Summarized Stage 10C static report refinements and small-multiple/per-horizon layout ideas |

Key takeaways used:

1. The current Stage 6 result is `clean_null`, not a positive signal claim.
2. The repository is stronger on evaluation than model sophistication.
3. The current 8D hash embedding is a major bottleneck.
4. Same-row market features are too weak.
5. Stronger market baselines should precede claims about event-state gains.
6. Train predictions and statistical uncertainty should be added for credibility.
7. No-news/truncation strata are critical to interpret event-state performance.
8. Advanced models are worthwhile only under the same leakage-aware protocol.

## Background That Did Not Require A Separate Decision

Some items are considered obvious from project scope and research context:

| Item | Status | Reason |
|---|---|---|
| Preserve `historical_prediction` semantics | Required | Stage 10C is historical output only |
| Preserve non-claims | Required | Current benchmark is `clean_null`; no trading/live claims |
| Keep lockbox protected | Required | Core benchmark credibility depends on untouched final evidence |
| Keep provider calls gated | Required | Stage 8 research and project scope require plan-first behavior |
| Keep existing Stage 2-6 artifacts interpretable | Required | New phase should not erase current evidence |
| Use fold-local preprocessing/training | Required | Prevents leakage |
| Version sidecar features | Required | User selected versioned schema changes and mostly strict contract |
| Treat LLM summaries as deferred | Required | Nondeterminism, cost, and report-scope risk |
| Treat provider expansion as deferred | Required | Current provider limitations must be measured first |

## Final Implementation Stance

The best next step is not a single model. It is a controlled upgrade program:

1. Build the integrated thin slice.
2. Strengthen market baselines with lag-linear and XGBoost.
3. Add all core diagnostics before promoting any variant.
4. Improve Stage 10C readability in parallel.
5. Add FinBERT event representations as a versioned ablation suite.
6. Add Pure PyTorch TSMixer after the tabular pipeline is stable.
7. Tune XGBoost aggressively but only with nested, guarded, purged controls.
8. Explore horizon-specific ensembles and horizon-specific event-market fusion after standalone evidence exists.
9. Keep dashboard/API/live/trading/LLM/provider-expansion ideas deferred.

This roadmap maximizes performance upside while preserving the repository's main scientific advantage: credible, leakage-aware, artifact-backed evaluation.
