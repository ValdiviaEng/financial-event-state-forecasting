# Next Steps Research Synthesis

## Purpose

This document consolidates the completed manual research under `docs/research/manual_research/research_*/results/` into a single dense next-steps research memo. It treats the existing repository as a governed, local, artifact-first research system whose current evidence is a disciplined `clean_null` result rather than a positive forecasting claim. The synthesis is intentionally action-oriented: it extracts what the research collectively says should happen next, what should not happen yet, and what acceptance evidence would make each next step credible.

## Source Set

The synthesis covers five manual research groups and their result reports:

| Research | Result files synthesized | Dominant topic |
|---|---|---|
| `research_1` | `DeepResearchReport_DailyWeekly Data Refresh Design.md` | Stage 8 daily/weekly data refresh design, provider-safety, manifest semantics, invalidation rules |
| `research_2` | `DRR-trajectory graph visualization.md` | Stage 10C trajectory visualization policy and caveats |
| `research_3` | `DRR-Relevant News Attribution for Stage 10C Ranking and Display Policy.md`; `DRR-Relevance signals for news ranking.md` | Relevant-news ranking, display policy, context-vs-causality wording, schema compatibility |
| `research_4` | `DRR-Top-10 Multi-Horizon Visualization.md`; `DRR-Top-Decision Ready Memo for the Future Local Update To Prediction Pipeline Architecture.md` | Static top-10 multi-horizon report design; future local update-to-prediction architecture |
| `research_5` | `DRR1...`; `DRR2...`; `DRR3...`; `DRR4...`; `DRR5...`; `DRR6...` | Repository-wide benchmark assessment, SOTA gap analysis, model/data/evaluation roadmap, Stage 10C report refinements |

## Current Project State Implied By The Research

The research consistently characterizes the repository as a **local CLI/artifact-driven benchmark harness** rather than a product, service, dashboard, API, or trading engine. The active scientific question remains narrow: whether aligned firm-news event-state features add incremental value beyond market-only baselines for multi-horizon forward excess-return forecasting over an approved top-50 universe. The active phase-one providers are Alpha Vantage `NEWS_SENTIMENT` for news and Twelve Data for OHLCV. Existing Stage 10C outputs are historical packets built from saved predictions, not fresh inference.

The current stage evidence chain is understood as follows:

| Stage | Research interpretation | Key status |
|---|---|---|
| Stage 2 | Manifest-backed benchmark panel over approved universe, common trading calendar, row identity, no-news/provider-risk metadata | Complete |
| Stage 3 | Market features, event-state features, labels, aligned news, explicit no-news states, provider truncation flags | Complete |
| Stage 4 | Purged/embargoed walk-forward folds plus final lockbox | Complete |
| Stage 5 | Frozen comparator ladder, train-only preprocessing, validation/lockbox saved predictions | Complete |
| Stage 6 | Serious benchmark metrics, ranking diagnostics, paired deltas, comparison summary | Complete with `clean_null`, `limitation_bearing` |
| Stage 7C | Contextual-bandit diagnostics only; not promoted to live signals | Complete as diagnostics |
| Stage 8 | Plan-first daily/weekly raw refresh scripts with explicit live-execution gates | Implemented as guarded operations layer |
| Stage 10C | Local historical prediction-output packet with static report, tables, news context, trajectory points | Complete, historical only |

The research repeatedly emphasizes that the current benchmarkâ€™s main achievement is not alpha discovery. Its main achievement is that it can credibly report a null result under controlled leakage-aware conditions. That is valuable because it means future upgrades can be measured against a stable, auditable baseline.

## Core Scientific Finding

The central scientific finding is stable across reports: the repository is a **strong benchmark-control system with a weak first-generation model/representation stack**. Stage 6 reports `clean_null`: the event-state gated-fusion model did not beat the selected market-only hurdle on both primary loss deltas for any primary short horizon in both validation and lockbox. Comparability is `limitation_bearing`, not invalid, because the serious packet structurally passes but upstream limitations remain: provider completeness is not claimed, Alpha Vantage truncation risk exists, split-adjustment details remain limitation-bearing, and train-vs-validation gap diagnostics are blocked because Stage 5 saved out-of-sample predictions only.

This should be interpreted as: the current hash-embedding event-state representation and shallow ridge-based gated fusion are not strong enough to clear the repositoryâ€™s own hurdle. It should **not** be interpreted as: news cannot help, event-state modeling is useless, or the repository has failed. The benchmark harness is functioning correctly by refusing to overclaim.

## Major Strengths To Preserve

The research identifies these project strengths as non-negotiable assets:

| Strength | Why it matters | Preserve by |
|---|---|---|
| Stable row identity | Enables exact artifact joins across stages and prevents silent row drift | Keep row-universe digests and row-key validation |
| Fold-local preprocessing | Blocks leakage through imputation/scaling | Keep train-only preprocessors per fold/horizon/model |
| Purge/embargo and lockbox | Prevents label-window overlap and post-hoc benchmark tuning | Keep split protocol unless a new benchmark family is approved |
| Saved out-of-sample predictions | Makes Stage 6 evaluation auditable and reproducible | Keep saved predictions as canonical metric input |
| Explicit non-claims | Prevents trading/advice/live-forecast misinterpretation | Keep non-claim text in reports/manifests/validators |
| No-news as state | Avoids conditioning only on news-rich rows | Preserve no-news and empty-event-state flags |
| Provider-risk preservation | Makes data incompleteness visible | Preserve truncation/empty-feed flags through outputs |
| Plan-first data refresh | Prevents accidental provider calls or raw mutations | Keep Stage 8 default plan-only and no-overwrite |
| Static local packet reporting | Fits the projectâ€™s artifact-first boundary | Keep Stage 10C static/offline unless explicitly expanded |
| Conservative null result logic | Makes the benchmark credible | Preserve predeclared result-class gates |

## Major Weaknesses To Address

The research converges on the following weaknesses:

| Weakness | Consequence | Severity |
|---|---|---|
| 8-dimensional deterministic hash embeddings | Discards nearly all semantic information in news | Very high |
| Same-row market features only | No temporal sequence context over OHLCV history | Very high |
| Shallow ridge-based gated fusion only | Weak multimodal capacity | High |
| Modest comparator ladder | Market hurdle may be incomplete relative to modern TS/tabular baselines | High |
| No saved train predictions | Blocks train-vs-validation overfitting diagnostics | Medium-high |
| No pinned environment surfaced | Byte-identical reproduction weaker than artifact reproduction | Medium-high |
| Alpha Vantage truncation risk | Event coverage may be incomplete in news-heavy windows | Medium-high |
| Frozen top-50 snapshot applied backward | Potential survivorship/universe look-ahead sensitivity | Medium-high |
| No formal statistical p-values / CIs | Loss-delta uncertainty remains underdeveloped | Medium |
| Stage 10C HTML is functional but not maximally legible | Useful packet exists but presentation can mislead or overwhelm | Medium |

## Research-Derived Priority Stack

### Priority 0: Preserve Scope Boundaries

Before implementation changes, keep the current boundary intact:

| Boundary | Research conclusion |
|---|---|
| No trading signals | Current outputs must never be framed as buy/sell/price-target advice |
| No live forecast semantics | `historical_prediction` remains the only approved Stage 10C row role |
| No dashboard/service/API | Static local artifacts remain the active product boundary |
| No provider expansion by default | Alpha Vantage and Twelve Data remain approved phase-one providers unless separately scoped |
| No Stage 6 reinterpretation | New data or new displays cannot convert `clean_null` into a positive claim |
| No auto-rebuild after Stage 8 | Raw refresh may invalidate Stages 2-6 but must not silently regenerate benchmark evidence |

### Priority 1: Data Refresh Hardening

Research 1 recommends a **plan-first overlapping-window refresh design**. The recommended operational rules are:

| Area | Recommendation |
|---|---|
| Daily news | Use a yesterday-through-today default overlap; tolerate duplicates through deterministic deduplication |
| Weekly news | Use rolling 7-day or calendar-week-with-overlap windows; include weekend news |
| Daily OHLCV | Use yesterday-through-today or last trading day logic; skip non-trading dates safely |
| Weekly OHLCV | Use last 5 trading days or 7-calendar-day window filtered to trading dates |
| Idempotency | Use content hashes, article IDs, ticker-date keys, and manifest status entries |
| Raw policy | No overwrite by default; overwrite requires explicit flag and backup/logging policy |
| Secrets | Redact API keys from stdout, manifests, ledgers, URLs, and committed artifacts |
| Failures | Record partial failures; distinguish no-data from provider errors; use limited retries/backoff |
| Invalidation | If raw data changes, warn that Stages 2-6 and Stage 10C packets are stale/historical |

The most important implementation concept is not schedule automation. It is **auditable refresh state**: every plan or execution manifest should explain the requested window, universe digest, provider, endpoint, planned/skipped/completed/failed counts, redaction policy, no-overwrite policy, retry policy, and downstream invalidation warning.

### Priority 2: Stage 10C Presentation Clarity

Research 2, 3, 4, and 5 collectively recommend improving Stage 10Câ€™s static report before changing prediction semantics. This is a high-leverage move because it improves user interpretation without changing model outputs.

Recommended presentation changes:

| Display area | Recommendation | Schema impact |
|---|---|---|
| Top-10 per horizon | Split into per-horizon sections or small multiples for `1d`, `5d`, `10d`, `20d`, `60d` | Presentation-only |
| Cross-horizon summary | Add diagnostic matrix/table showing tickers appearing across horizons | Use existing cross-horizon diagnostic where possible |
| Ranking values | Show rank and predicted excess return together; keep numeric values visible | Existing top-10 tables |
| Limitation flags | Format `no_news_flag` and `provider_truncation_risk_flag` as readable labels, not raw booleans only | Existing fields |
| Stage 6 context | Keep `clean_null` / `limitation_bearing` prominent | Existing manifest/limitations |
| Non-claims | Repeat â€œhistorical onlyâ€, â€œnot trading adviceâ€, â€œnot price targetâ€ in report header and chart captions | Existing text |
| Trajectory plots | Plot historical excess-return or trajectory markers only; never future fan charts or projected price paths | Existing trajectory points |
| Accessibility | Add `<caption>`, `<th>`, alt text for images, readable table ordering, numeric alignment | Presentation-only |
| Static images | Optional Matplotlib PNG/SVG bar charts or sparklines; tables remain source of truth | Output artifact addition |
| Validation | Parse HTML/tables and assert displayed values match CSV/Parquet exactly | Validator/test addition |

The guiding rule: improve readability without changing claim semantics. A better chart that makes historical model outputs easier to scan is acceptable. A chart that implies forecast paths, buy/sell signals, or confidence unsupported by Stage 6 is not acceptable.

### Priority 3: Relevant-News Ranking And Context Policy

Research 3 provides a clear policy: relevant news in Stage 10C should be ranked deterministically from existing aligned-news fields and labeled as context, not causality.

Recommended default ranking:

1. Keep only articles available at or before the rowâ€™s prediction/as-of timestamp.
2. Sort by `published_timestamp` descending.
3. Use aligned-news count to display â€œshowing N of Mâ€.
4. If sentiment/topic fields are not present in Stage 3 outputs, do not pretend they exist.
5. If duplicate or near-duplicate headlines exist, show only one representative item.
6. Cap display to a small number, likely 3 to 5 items per row.
7. Preserve `no_news_flag` and `provider_truncation_risk_flag` visibly.
8. Do not include URLs, full article text, or unapproved provider content.
9. Avoid LLM summarization unless separately approved.
10. Validate timestamp availability, ticker/date match, no-news consistency, and truncation-flag preservation.

Recommended wording:

> Displayed news were available in the historical data as of the prediction time. They are shown for contextual reference only and are not causal explanations, trading recommendations, or price targets.

The important distinction is that news display improves interpretability of **context**, not explainability of the modelâ€™s internal decision. The report must not say â€œthe model predicted this because of this headline.â€

### Priority 4: Workflow-Level Reproducibility

Research 4 recommends Option B as the target architecture: a **local lockfile-backed DAG wrapper around existing stage CLIs and validators**, after a shorter Option A-style hardening phase. The research sees the repo as already strong on stage contracts but weak on workflow-level state capture.

Option comparison:

| Option | Concept | Research verdict |
|---|---|---|
| A | Add governed offline orchestrator CLI and top-level run manifest | Useful bridge; low disruption; not enough as final reproducibility layer |
| B | Wrap existing stages in DVC-style lockfile-backed DAG | Recommended target; best match to artifact-first repo |
| C | Persisted offline inference bundle for future-row scoring | Defer; requires new `forecast_candidate` semantics, model packaging, security, schemas |

Recommended sequencing:

| Milestone | Deliverables | Exit criteria |
|---|---|---|
| Contract freeze | Freeze Stage 2-10 input/output contracts; define packet attestation schema | Existing validators pass; packet fields stable |
| Workflow pilot | Add DAG stages around existing CLIs and validators | Unchanged inputs no-op; changed dependencies trigger correct downstream reruns |
| Offline hardening | Add no-network tests, environment capture, secret scan | Offline path cannot call providers; no sensitive outputs |
| Migration parity | Compare old manual stage run to DAG run | Same-input outputs match or diffs are explained |
| Deferred inference design | Design-only model bundle path | No implementation until future-row semantics approved |

The critical idea is that a DAG should not replace stage validators. It should call them as hard gates. The existing stage contracts remain authoritative; the DAG records dependency state and reduces operator error.

### Priority 5: Representation Upgrade

Research 5 strongly converges on one modeling bottleneck: the event-state branchâ€™s 8-dimensional deterministic hash embedding is far too weak for modern financial news representation. The next serious event-state experiment should replace or augment it while preserving the same split/evaluation protocol.

Recommended progression:

| Step | Experiment | Why |
|---|---|---|
| 1 | Retain current hash embedding as baseline | Provides exact compatibility anchor |
| 2 | Add frozen finance-domain text embeddings | Tests semantic lift with moderate risk |
| 3 | Add recency-weighted pooling | Incorporates time proximity without deep architecture |
| 4 | Add provider metadata/sentiment if already available in raw data and approved | Tests whether discarded metadata was suppressing signal |
| 5 | Add article clustering / story dedup features | Reduces redundant headline noise |
| 6 | Add event-type/entity/polarity features | Moves from article pooling toward event representation |

Acceptance criteria should remain strict: improved event-state features must beat the current market hurdle and current hash baseline under the same folds, same lockbox, and same result-class logic. A prettier embedding is not useful unless it changes validated evidence.

### Priority 6: Stronger Market And Temporal Baselines

Research 5 also argues that the current market branch is underpowered because it uses same-row OHLCV and small sklearn models. Before testing expensive multimodal models, improve market-only baselines. Otherwise event-state gains may be evaluated against an incomplete hurdle.

Recommended additions:

| Baseline family | Purpose | Risk |
|---|---|---|
| Lagged linear models | Minimal temporal context benchmark | Low |
| Rolling volatility/liquidity features | Stronger tabular context | Low-medium |
| Strong boosted trees | Better tabular hurdle | Medium |
| TSMixer/PatchTST-style models | Sequence-aware market-only benchmark | Medium-high |
| iTransformer/TimeXer-like exogenous models | Strong temporal/exogenous integration | High |
| Time-series foundation model adapters | Research frontier comparison | High |

The conceptual order matters. First create lag/rolling-feature baselines. Then add boosted trees. Then test sequence models. Only after the strengthened market-only ladder is credible should a stronger multimodal event-state model be interpreted as a meaningful gain.

### Priority 7: Evaluation Hardening

The current Stage 6 evaluation is disciplined but incomplete. Research 5 recommends adding:

| Evaluation improvement | Why |
|---|---|
| Save train predictions | Unblocks train-vs-validation gap diagnostics |
| Block bootstrap or date-clustered confidence intervals | Adds uncertainty to loss deltas and rank metrics |
| Multiple-comparison controls | Prevents horizon/model/data-slice cherry-picking |
| News-rich vs no-news stratification | Tests whether event-state value is masked by sparse-news rows |
| Provider-truncation strata | Tests whether incomplete feeds suppress or distort signal |
| Regime slices | Tests stability across market conditions |
| Multi-seed diagnostics for nonconvex models | Measures stability of MLP/deep extensions |
| Portfolio utility diagnostics | Separates predictive metrics from actionability, still research-only |
| Turnover/concentration/cost stress tests | Future external validity; not a trading claim |
| Calibration/quantile losses | Later risk-aware output quality |

The highest-value immediate fix is saving train predictions with explicit labeling: **for diagnostics only, never for model selection or benchmark claim promotion**.

### Priority 8: Data Realism And Provider Limitations

Research 5 raises two important data-realism concerns.

First, Alpha Vantage `NEWS_SENTIMENT` has a hard result cap, and the repository already preserves truncation-risk flags. The next step is to quantify whether truncation materially affects event-state conclusions. This could include truncation-refinement windows, query slicing by time/topic where approved, duplicate detection, and explicit metrics by truncation-risk strata.

Second, the frozen top-50 universe is useful for a controlled benchmark but may introduce survivorship/universe look-ahead sensitivity when applied backward. The research recommends a historical-universe sensitivity benchmark. This does not require immediately replacing the benchmark family; it means running a companion sensitivity study to estimate how much the frozen-universe choice matters.

Data-reality experiments:

| Experiment | Goal | Expected output |
|---|---|---|
| Truncation-risk stratified Stage 6 | Measure performance differences in flagged vs unflagged rows | Slice-level metrics and limitations note |
| No-news vs news-rich Stage 6 | See whether news helps only when enough news exists | Conditional metrics by news availability |
| Historical-universe sensitivity | Estimate survivorship/look-ahead sensitivity | Comparison packet, not replacement claim |
| Provider metadata retention | Determine if discarded fields carry signal | Feature ablation table |
| Dedup/story clustering | Reduce repeated-wire noise | Cleaner aligned-news features |

### Priority 9: Deferred Advanced Models

Advanced modeling is recommended only after the benchmark harness, data quality, and baselines are strengthened. Candidate advanced directions include:

| Direction | Why attractive | Why deferred |
|---|---|---|
| Multimodal cross-attention | Directly models market/news interactions | High complexity; needs stronger baselines first |
| Graph/relational stock models | Cross-sectional target likely benefits from stock relations | Graph construction can introduce leakage and design degrees of freedom |
| Event extraction branch | More interpretable than article pooling | Requires schema changes and extraction validation |
| RAG/history retrieval | Could surface similar historical event regimes | High reproducibility and leakage risk |
| Local LLM summarization | Better human-readable news context | Not needed for core forecasting; nondeterministic; hardware-heavy |
| Offline inference bundle | Enables future-row scoring | Requires new semantics, security, environment, model-packaging approvals |

The research is clear: do not jump straight from hash embeddings to a large LLM/RAG/future-scoring system. The correct sequence is controlled ablations and stronger baselines first.

## Integrated Next-Step Roadmap

### Phase 1: Documentation And Presentation Hardening

| Item | Deliverable | Success criterion |
|---|---|---|
| Manual research archive | Move research folders under `docs/research/manual_research` | Structure exists and paths are stable |
| Research synthesis | This `NextSteps-Research.md` | All five research groups reflected |
| Brainstorming design doc | `docs/NextSteps_Brainstorming.md` | Ranked ideas with metrics and pros/cons |
| Stage 10C report clarity | Per-horizon tables, better limitations text, non-claim captions | Existing Stage 10C validator still passes; added display tests pass |
| Relevant-news wording | Context-only labels and deterministic ordering | Timestamp/no-URL/no-causality tests pass |

### Phase 2: Operational Safety And Reproducibility

| Item | Deliverable | Success criterion |
|---|---|---|
| Stage 8 manifest schema hardening | Required fields for plan/live manifests | Schema tests pass |
| Stage 8 redaction tests | No API key leakage in stdout/manifests/ledgers | Secret-pattern tests pass |
| DAG/orchestrator pilot | Local wrapper or DVC-style stage graph | Same-input rerun no-ops or reproduces artifacts |
| Environment capture | Pinned dependency file or documented lock strategy | Fresh environment can run validators |
| Top-level run attestation | Manifest linking stage inputs/outputs/validators | Full path evidence is machine-readable |

### Phase 3: Benchmark Diagnostic Hardening

| Item | Deliverable | Success criterion |
|---|---|---|
| Save train predictions | Diagnostic-only train prediction artifact | Train-gap section no longer blocked |
| Stratified Stage 6 | Metrics by news/no-news/truncation strata | Clear conditional-performance report |
| Statistical uncertainty | Block bootstrap or clustered CIs | Loss deltas include uncertainty |
| Historical-universe sensitivity | Companion sensitivity packet | Universe-bias risk is bounded or documented |
| Provider truncation refinement | Refined query windows or proof of limitation | Fewer unknown high-news windows or better caveat |

### Phase 4: Representation And Baseline Upgrades

| Item | Deliverable | Success criterion |
|---|---|---|
| Lag/rolling market features | Stronger market-only feature branch | Beats or validates current market hurdle |
| Strong tabular baseline | XGBoost/LightGBM/CatBoost or sklearn-safe equivalent | Improved market hurdle under same splits |
| Finance text embeddings | Frozen semantic embedding branch | Beats hash branch in at least one controlled ablation |
| Recency/story features | Better news aggregation | Conditional improvement in news-rich rows |
| Sequence-aware market model | PatchTST/TSMixer-style baseline | Validated against strict lockbox |

### Phase 5: Advanced Research Only After Evidence Improves

| Item | Gate before implementation |
|---|---|
| Multimodal fusion | Semantic embeddings and stronger market baselines exist |
| Graph models | Sector/relation data source and leakage policy approved |
| Event extraction | Schema and evaluation tests approved |
| RAG/LLM reasoning | Reproducibility, no-leakage, and compute plan approved |
| Offline future-row scoring | `forecast_candidate` semantics and model-bundle security approved |

## Do-Not-Implement-Yet List

| Idea | Reason to defer |
|---|---|
| Live inference service | Outside current local artifact boundary |
| Dashboard/API | Explicitly out of scope; static HTML is enough for now |
| Buy/sell signals | Current evidence is `clean_null`; trading claims disallowed |
| Future `forecast_candidate` rows | Requires new model packaging and semantics |
| LLM summarization in default report | Nondeterministic, costly, schema-changing, unnecessary for current goals |
| RAG-style forecasting | High leakage/reproducibility risk before simpler semantic baselines |
| Provider expansion | Requires new scope and comparability decisions |
| Universe expansion | Would create a new benchmark family, not a patch |
| Stage 6 reinterpretation | New displays cannot change the benchmark result |
| Automatic raw refresh to prediction rebuild | Too dangerous without explicit invalidation and approvals |

## Acceptance Evidence For A Credible Next Positive Claim

A future positive event-state claim should require all of the following:

| Requirement | Rationale |
|---|---|
| Same approved splits and lockbox or explicitly new benchmark family | Prevents cherry-picked split changes |
| Stronger market-only hurdle included | Ensures event-state gain is not due to weak baselines |
| Event-state model improves both RMSE and MAE deltas where predeclared | Keeps Stage 6 logic consistent |
| Validation and lockbox agreement | Prevents validation-only overfit |
| Stratified analysis by news/no-news/truncation | Shows whether gain depends on data artifacts |
| Train-gap diagnostic available | Addresses overfitting blocker |
| Statistical uncertainty reported | Quantifies fragility |
| No provider completeness overclaim | Preserves data honesty |
| Non-claim text preserved | Prevents trading/advice misuse |
| Reproducible artifact packet and validator pass | Makes result auditable |

## Bottom Line

The research says the repository should now move from **stage completion** to **controlled improvement**. The correct path is not to deploy or advertise the current model. The correct path is to preserve the strong benchmark harness, improve Stage 10C readability, harden Stage 8 and workflow reproducibility, close evaluation blind spots, and then introduce stronger text, temporal, and baseline models under the same leakage-aware protocol.

The highest-impact immediate work is therefore:

1. Improve Stage 10C report clarity using existing artifacts only.
2. Add deterministic relevant-news display policy and validation.
3. Harden Stage 8 manifests, redaction, idempotency, and invalidation messaging.
4. Add workflow-level reproducibility with lockfile/DAG or equivalent attestation.
5. Save train predictions for diagnostics only.
6. Add news/no-news/truncation stratified evaluation.
7. Add lagged/rolling market features and stronger market-only baselines.
8. Replace hash embeddings with finance-aware semantic embeddings in controlled ablations.
9. Quantify universe and provider-data sensitivity.
10. Defer future inference, dashboards, LLM summaries, and trading semantics until the evidence and governance boundaries justify them.
