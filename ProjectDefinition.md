# Project Definition

Status: final broad project definition for the active-root phase-1 rebuild. Created 2026-05-07 from `AgentRules.md`, `docs/agent/AgentMemory.md`, the active audit and memory logs, `ScopeDefinition.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`, active skeleton docs, and current repository state.

This document defines the project at the architecture, pipeline, processing, functional-responsibility, governance, and benchmark-family level. It intentionally contains no implementation code, no pseudo-code, and no final module-level contract. If this document conflicts with `ScopeDecisionLog.md` or `ResearchTruth.md`, those higher-authority files govern.

## 1. Purpose

The active project is a documentation-first, benchmark-first research rebuild for testing whether aligned firm-news event-state features add predictive value beyond market-only baselines for end-of-day, multi-horizon, forward excess-return forecasting.

The phase-1 project is not a trading product, service, dashboard, API, live system, HFT system, or broad multimodal platform. It is a local, artifact-driven research system whose first serious claim must be backed by leakage-controlled evaluation and reproducible evidence.

## 2. Authority And Source Basis

| Source | Role In This Definition |
| --- | --- |
| `AgentRules.md` | Binding governance constitution, source-of-truth hierarchy, approval gates, documentation-first discipline, benchmark comparability discipline. |
| `docs/agent/AgentMemory.md` | Binding interaction-log and continuity procedure. |
| `docs/agent/agent_log/Current_State.md` | Current operational task contract, priorities, blockers, and active evidence pointers. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Authoritative recorded request, task, evidence, and reconciliation history where events exist. |
| `docs/agent/agent_log/Project_Audit_2026-05-06.md` | Current-state audit of active docs, scripts, data, missing layers, and benchmark-readiness risks. |
| `docs/agent/agent_log/AlphaVantage_Raw_Merge_2026-05-06.md` | Evidence for canonical top-50 Alpha Vantage raw file coverage after raw merge. |
| `docs/agent/agent_log/TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md` | Evidence for active raw Twelve Data top-50 plus SPY support coverage back to 2010 where provider/listing history exists, plus reference-only split-adjustment review. |
| `docs/agent/agent_log/Stage2_Deprecated_OHLCV_Salvage_Audit_2026-05-13.md` | Evidence for deprecated Twelve Data parquet salvage coverage and clean-window candidate bounds. |
| `ScopeDefinition.md` | Pre-decision questionnaire, truth table, contradiction inventory, and decision framing. |
| `ScopeDecisionLog.md` | Owner-approved answers to all 24 decision questions; highest authority for resolved scope choices. |
| `ResearchTruth.md` | Current research-truth synthesis combining owner decisions, repo evidence, research notes, historical archive evidence, and unresolved risks. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Owner-approved Option B validation-design contract for data separation, fold-local preprocessing, predeclared metrics, saved predictions, and overfitting diagnostics. |
| Active skeleton docs under `docs/` | Minimum active theory, design, validation, operations, and execution docs created after the audit. |
| `docs/research_results/` | Research synthesis, comparison addenda, logs, and paper notes used as supporting evidence, not final owner approval. |
| `docs/course_material/` and `docs/reference_guides/` | Reference/course material only unless explicitly adopted into active truth. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/` | Historical reference and selective salvage source only, not active truth by default. |
| `reset/` | Reusable scaffold only, not current project truth. |

## 3. Project Thesis

The core thesis is that recent firm-specific financial news, when aligned to the correct prediction timestamp and summarized as an event state, may contain incremental predictive information beyond market-only features for forward excess returns.

The thesis is falsifiable. Phase 1 can succeed with a robust positive result, a conditional positive result, or a clean null result, provided the result is produced under the approved benchmark protocol and has the required artifact evidence.

## 4. Phase-1 Definition

| Dimension | Active Definition |
| --- | --- |
| Project mode | Local CLI and artifact-driven research system. |
| Scientific objective | Test event-state incremental value beyond market-only baselines. |
| Prediction frequency | End-of-day. |
| Target family | Forward excess returns. |
| Horizon set | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | Reproducible top-50 liquid large-cap universe for the first serious benchmark. |
| OHLCV provider | Twelve Data. |
| News provider | Alpha Vantage. |
| Static/company support | SEC only, with phase-1 static company metadata deferred unless explicitly approved later. |
| News alignment | Same-day as-of-close, with after-hours and non-trading-day news rolled forward. |
| Main event representation | Pooled dense embeddings plus scalar enrichments. |
| No-news policy | Keep rows and encode explicit empty event states with no-news indicators. |
| Default multimodal fusion | Simple gated fusion. |
| Evaluation | Purged-plus-embargoed walk-forward development evaluation plus final untouched lockbox. |
| Data separation refinement | Option B contract: strict train/validation/lockbox separation, split manifests, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, and overfitting diagnostics. |
| Primary metrics | Regression metrics. |
| Secondary metrics | Ranking metrics, mandatory as diagnostics. |
| Serious-run evidence | Dataset version, manifest, resolved config, fold definitions, saved predictions, metrics, and comparison summary. |

## 5. Resolved Decision Register

| Decision ID | Resolved Definition |
| --- | --- |
| DQ-001 | Rebuild in the active root with selective legacy salvage only after research truth and scope are finalized. |
| DQ-002 | Phase 1 is the narrow event-state incremental-value thesis, not a broad platform or architecture tournament. |
| DQ-003 | Forward excess returns are the primary target family. |
| DQ-004 | The first serious benchmark uses `1d`, `5d`, `10d`, `20d`, and `60d` horizons. |
| DQ-005 | Same-day as-of-close news alignment is canonical, with after-hours and non-trading-day news rolled forward. |
| DQ-006 | One narrow serious benchmark family must be frozen before serious implementation or reruns proceed. |
| DQ-007 | The first serious benchmark uses a reproducible top-50 liquid large-cap universe; later 100/500 expansions are separate benchmark families. |
| DQ-008 | Phase 1 uses Twelve Data for OHLCV, Alpha Vantage for news, and SEC for static/company support only. |
| DQ-009 | The default event-state package is pooled dense embeddings plus scalar enrichments. |
| DQ-010 | Simple gated fusion is the phase-1 multimodal default. |
| DQ-011 | The mandatory comparator ladder is broader than the old minimal default and needs explicit active-root roster definition before implementation. |
| DQ-012 | Serious claims require purged-plus-embargoed walk-forward evaluation plus a final untouched lockbox; Option B adds explicit data-separation and overfitting-control requirements without changing the protocol. |
| DQ-013 | Regression metrics remain primary; ranking metrics are mandatory secondary diagnostics; metrics must be predeclared and computed from saved out-of-sample predictions. |
| DQ-014 | Static company metadata and KB features stay out of phase 1 and remain phase-2 extensions. |
| DQ-015 | Uncertainty-aware outputs remain later extensions, not phase-1 defaults. |
| DQ-016 | Graph-heavy cores, MoE, dynamic profiles, end-to-end text fine-tuning, broad derivative grids, and full live-universe first-pass benchmarking are deferred until the core benchmark is stable. |
| DQ-017 | Active theory and design docs must be recreated before broader coding. |
| DQ-018 | Meaningful progress requires rerun-capable tests, manual provider checks, structured run summaries, CI-ready validation, contamination blockers, and overfitting diagnostics before major claims. |
| DQ-019 | Phase 1 remains a local CLI/artifact-driven research system only. |
| DQ-020 | Archived materials remain reference-only unless deliberately absorbed into active-root docs. |
| DQ-021 | The first serious benchmark should use a shorter verified overlapping clean historical window rather than maximum history by default. |
| DQ-022 | No-news days stay in the benchmark row universe and use explicit empty event states plus no-news indicators. |
| DQ-023 | Every serious benchmark emits the full reproducible artifact packet, including Option B split/preprocessing manifests and overfitting diagnostic report. |
| DQ-024 | Robust positive, conditional positive, and clean null outcomes all count as valid phase-1 success classes. |

## 6. Current Repository-State Definition

The active root is a post-archive rebuild root. It now contains governance files, active scope and truth files, active research docs, active-root theory/design/validation/operations docs, an active `scripts/` layer, raw universe snapshots, raw Alpha Vantage news payloads, manifests, approved executable Stage 2 through Stage 6 benchmark pipeline layers, Stage 7C diagnostic implementation, Stage 8 plan-first raw update tooling, Stage 10A research-only update-to-prediction workflow analysis, Stage 10B decision-comparison and captured-decision evidence, and remaining comment-only scaffolds for provider/utility/expansion work.

The active root currently contains materialized Stage 2 dataset artifacts, Stage 3 feature/label artifacts, Stage 4 split/packet artifacts, Stage 5 model/preprocessing/saved-prediction artifacts, and Stage 6 metric/diagnostic/comparison/reporting artifacts. The current Stage 6 result class is `clean_null` and the comparability classification is `limitation_bearing`.

The active scripts currently support governance validation, Alpha Vantage news ingestion/backfill planning, Stage 8 plan-first raw update planning, Stage 0-1 validation, Stage 2 dataset validation/building, Stage 3 feature/label validation/building, Stage 4 split/packet validation/building, Stage 5 model/prediction validation/building, Stage 6 benchmark reporting validation/building, and Stage 7C diagnostic validation. They do not constitute an approved one-command end-to-end rebuild pipeline.

The archived legacy snapshot contains useful historical design, implementation, tests, and artifacts, but it is reference-only unless a concept or implementation is deliberately reintroduced through active-root documentation and approved scope.

Reference/course material and the reset scaffold are not active project truth unless explicitly adopted through the active source-of-truth stack.

## 7. Architecture Definition

The phase-1 architecture is defined as layered research infrastructure, not as a product architecture.

| Layer | Definition |
| --- | --- |
| Governance and memory layer | Maintains source-of-truth hierarchy, approval gates, interaction logs, evidence discipline, and drift control. |
| Theory and research layer | Defines the scientific objective, accepted hypotheses, non-goals, methodology cautions, and research-supported implications. |
| Design definition layer | Converts approved theory and owner decisions into architecture maps, implementation decisions, execution stages, and validation expectations. |
| Raw data layer | Stores frozen universe snapshots, provider payloads, raw merge manifests, request status summaries, and provider-limit evidence. |
| Data validation layer | Confirms coverage, schema validity, timestamp validity, ticker normalization, empty windows, truncation risk, and credential-safety status. |
| Benchmark dataset layer | Produces a versioned, manifest-backed panel only after clean window selection and validation contracts are complete. |
| Feature and event-state layer | Builds market features and aligned event-state features on the same row universe, including explicit no-news states. |
| Target and label layer | Defines forward excess-return labels for all approved horizons with leakage-aware timestamp discipline. |
| Split and evaluation layer | Defines purged-plus-embargoed walk-forward folds, explicit purge/embargo accounting, and a final untouched lockbox. |
| Model and comparator layer | Runs market-only baselines, broader serious comparator families, and event-state models on identical rows and splits. |
| Artifact and reporting layer | Produces saved out-of-sample predictions, metrics, fold records, preprocessing-fit records, manifests, overfitting diagnostics, resolved configs, and comparison summaries. |
| Operations layer | Controls data refresh, raw merge policy, truncation refinement, benchmark invalidation, rollback, and safe reruns. |

## 8. Pipeline Definition

The approved phase-1 pipeline is conceptually defined by these stages.

1. Freeze the benchmark family using approved target, horizon, universe, provider, alignment, no-news, evaluation, metric, and artifact-packet definitions.
2. Preserve and validate the top-50 universe snapshot as the first serious benchmark seed.
3. Collect or confirm raw OHLCV, Alpha Vantage news, and SEC support data within the approved provider boundary.
4. Validate raw inputs for coverage, parseability, timestamp integrity, ticker handling, duplicate or non-canonical files, empty windows, truncation flags, and credential-safety issues.
5. Select a shorter verified overlapping clean historical window based on actual OHLCV, news, label, and split feasibility.
6. Construct a benchmark dataset where market-only and event-state branches share the same row universe.
7. Align news by the same-day as-of-close rule and roll after-hours or non-trading-day news forward to the next valid trading date.
8. Encode no-news days as explicit empty event states with no-news indicators, not as dropped rows.
9. Generate forward excess-return labels for all approved horizons.
10. Build purged-plus-embargoed walk-forward development folds and reserve the final untouched lockbox.
11. Fit all learned preprocessing only on each active fold's training rows and preserve the preprocessing-fit manifest.
12. Run the approved market-only, broader comparator, and event-state model families under identical rows, labels, and splits.
13. Emit saved out-of-sample predictions and the full serious-run artifact packet before any serious claim is made.
14. Report the required overfitting diagnostics, including train-validation gaps, fold dispersion, positive-fold/horizon rates, and validation-to-lockbox degradation.
15. Interpret results as positive, conditional positive, or clean null according to the evidence, without metric shopping or benchmark drift.

## 9. Processing Definitions

| Processing Area | Definition |
| --- | --- |
| Universe processing | Treats the top-50 snapshot as frozen phase-1 input and preserves canonical ticker identity, including dotted tickers. |
| Provider boundary processing | Normalizes provider-facing request symbols only where required while preserving canonical repository tickers in storage and artifacts. |
| Raw news processing | Preserves raw Alpha Vantage payloads, request status evidence, row counts, truncation flags, and empty-feed windows. |
| Market-data processing | Produces end-of-day market features suitable for forward excess-return labels and market-only baselines. |
| Timestamp processing | Enforces prediction-time availability and prevents future news or future market data from entering features. |
| Event-state processing | Converts recent aligned news into pooled dense embeddings plus scalar enrichments for each firm-date. |
| No-news processing | Represents lack of news as explicit state and indicator information while preserving row comparability. |
| Target processing | Converts future returns into forward excess-return labels for each approved horizon. |
| Split processing | Creates walk-forward folds with purging and embargoing appropriate to overlapping horizons plus a final untouched lockbox and row-level split manifest. |
| Benchmark processing | Compares market-only and event-state branches on identical rows, labels, folds, and metric definitions. |
| Artifact processing | Writes sufficient metadata and outputs for auditability, reruns, pairwise comparison, overfitting diagnostics, and benchmark comparability review. |

## 10. Functional Responsibility Definition

The project responsibilities are defined at a conceptual level as follows.

| Responsibility | Definition |
| --- | --- |
| Truth governance | Preserve the theory-to-design-to-code-to-test-to-operation dependency chain and prevent lower layers from redefining higher layers. |
| Scope governance | Keep phase-1 bounded to the approved event-state incremental-value benchmark and require explicit approval for scope changes. |
| Evidence governance | Prevent completion or benchmark success claims without inspectable evidence pointers. |
| Data acquisition | Obtain approved provider data within quota, provenance, and provider-boundary constraints. |
| Data quality control | Surface missing data, parse failures, truncation, empty feeds, duplicate files, and credential-risk issues before downstream use. |
| Dataset construction | Build a manifest-backed benchmark dataset only after clean window and validation contracts are defined. |
| Feature construction | Build market and event-state features without changing the row universe between branches. |
| Label construction | Define forward excess-return targets consistently across all approved horizons. |
| Evaluation construction | Create leakage-controlled folds and lockbox boundaries that preserve serious claim validity. |
| Model comparison | Compare strong market-only baselines, broader serious comparators, and event-state models without hidden winner-picking. |
| Result reporting | Report evidence-backed results as robust positive, conditional positive, or clean null. |
| Update control | Treat data, universe, target, provider, alignment, split, feature, or metric changes as potential benchmark comparability events. |

## 11. Data Definition

The first serious benchmark data definition is a top-50 liquid large-cap, end-of-day, firm-date panel with market information, aligned event-state information, and forward excess-return labels.

The current active data evidence supports complete canonical top-50 Alpha Vantage raw file coverage at 850 of 850 planned ticker-year/current windows after the 2026-05-06 raw merge. This means raw file coverage is complete for the approved top-50 news corpus.

Raw file coverage does not mean provider-level article completeness, dataset readiness, or benchmark readiness. The current merge evidence reports 92 likely truncated Alpha Vantage windows and 10 empty-feed windows. Latest Stage 2 reconciliation uses current news with visible limitation flags and makes no provider-level article-completeness claim.

Active raw Twelve Data OHLCV now covers all approved top-50 tickers plus SPY support with full-window files for requested window `2010-01-01` to `2026-05-22`. The latest coverage audit reports no post-first-available-date gaps against the SPY reference calendar, five late-start ticker limitations (`ABBV`, `GEV`, `META`, `PLTR`, `TSLA`), and one CVX OHLC anomaly handled only by derived cleaning policy during dataset materialization. This is not a materialized benchmark dataset.

Deprecated Twelve Data parquet evidence remains reference-only fallback evidence for Stage 2 input-readiness context, with an OHLCV-derived all-horizon candidate as-of window of `2024-04-01` to `2024-10-03`. This is not a materialized benchmark dataset.

Top-100 and top-500 data collection paths are future expansion inputs only. They are not comparable to the approved top-50 benchmark family unless explicitly approved and validated as separate benchmark families.

## 12. Event-State Definition

An event state is the firm-date representation of recent aligned firm-news information available as of the prediction timestamp.

The default event-state representation combines pooled dense text embeddings with scalar enrichments. The embedding part captures semantic content from recent news. The scalar part may represent structured information such as news density, absence, recency, novelty, conflict, or other approved event-state enrichments once detailed contracts are defined.

Event state is not sentiment-only text. Sentiment-only can be a weak baseline or ablation, but it is not the project identity. Event state is also not isolated article-impact modeling; it is a temporal state representation for a firm at a prediction date.

## 13. Target Definition

The primary target family is forward excess returns. The benchmark is intended to evaluate whether event-state features improve prediction beyond broad market drift and market-only baselines.

Raw returns and factor-neutral residuals remain useful reference or later extension families, but they are not the active phase-1 default target family.

The approved horizons are `1d`, `5d`, `10d`, `20d`, and `60d`. These horizons create overlapping-label and sample-availability burdens, so split design, purge windows, reporting, and interpretation must account for them.

Every benchmark row must preserve ticker, as-of date, horizon, feature availability timestamp, label-window start and end, split assignment, fold ID where applicable, and lockbox membership where applicable.

## 14. Model And Comparator Definition

The phase-1 default event-state fusion family is simple gated fusion. The purpose is to test whether event-state information conditionally contributes beyond market-only features without introducing an overly complex architecture as the first claim-bearing model.

The comparator ladder must be stronger than a minimal baseline set. The active Stage 5 roster is frozen as `phase1_top50_pragmatic_broader_sklearn_v1`; changing it after prediction materialization requires explicit approval and comparability review.

The comparator ladder must preserve identical data rows, labels, folds, and metric definitions between market-only and event-state branches. Any architecture that changes the benchmark family or requires incompatible data contracts must be treated as a separate decision.

Late fusion, residual fusion, stronger text encoders, tree-based comparators, and other serious comparator families can be considered as approved ladder elements or later ablations once the roster is explicitly defined. Graph-heavy cores, MoE, dynamic profiles, end-to-end text fine-tuning, broad derivative grids, and full live-universe first-pass benchmarking are out of phase 1 until the core benchmark is stable.

## 15. Evaluation Definition

Serious claims require purged-plus-embargoed walk-forward development evaluation plus a final untouched lockbox for reporting.

The evaluation design must protect against look-ahead leakage, overlapping-horizon contamination, benchmark drift, and repeated tuning against the final report set. Lighter smoke checks may exist for plumbing, but they do not support thesis-level claims.

The Option B data-separation refinement requires fold-local preprocessing, explicit purge and embargo manifests, lockbox access discipline, metric predeclaration, saved out-of-sample predictions, and quantitative overfitting diagnostics. The final lockbox must not be used for model selection, feature selection, threshold selection, clean-window selection, or repeated debugging by result inspection.

Regression metrics are primary because the target family is forward excess returns. Ranking metrics are mandatory secondary diagnostics because cross-sectional ordering may reveal practically relevant behavior that point-error metrics alone can obscure.

No single split, single horizon, single metric, or single convenient subset can justify a serious conclusion.

## 16. Artifact Definition

Every serious benchmark run must produce a reproducible artifact packet with at least these evidence families.

| Artifact Family | Definition |
| --- | --- |
| Dataset version | Stable identity for the benchmark dataset used by the run. |
| Dataset manifest | Data sources, coverage, clean window, row universe, label availability, provider status, and known limitations. |
| Resolved config | Complete configuration actually used for the run. |
| Fold definitions | Development folds, purge and embargo details, and lockbox boundary. |
| Split manifest | Row-level split role, fold ID, purge/embargo accounting, and excluded-row reasons. |
| Preprocessing-fit manifest | Evidence that learned preprocessing was fit only on training rows for each active fold. |
| Saved predictions | Forecast outputs sufficient for rerun review, paired comparison, and later diagnostic analysis. |
| Metrics | Regression-first metrics plus mandatory ranking diagnostics. |
| Overfitting diagnostic report | Train-validation gaps, fold dispersion, positive-fold/horizon rates, validation-to-lockbox degradation, paired comparison notes, and search-space summary. |
| Comparison summary | Market-only, comparator, and event-state results summarized under the same benchmark-family assumptions. |

Artifacts must be sufficient for future audit. A result without these artifacts is not a serious benchmark result.

## 17. Operations Definition

Data refreshes, raw merges, reruns, and updates must preserve benchmark comparability discipline.

Refreshing or replacing data can invalidate prior results if rows, labels, feature availability, provider coverage, universe membership, split boundaries, target definitions, horizon definitions, or metric definitions change.

Raw files should not be overwritten without a manifest-backed merge policy. Existing raw files should be preserved unless a reviewed cleanup plan exists. Request ledgers containing provider keys must not be committed, shared, or published as-is.

Alpha Vantage truncation-risk handling remains an operations and validation limitation. The current Stage 6 packet is limitation-bearing because provider-level article completeness is not claimed; future positive or publication-oriented claims must preserve or resolve that limitation explicitly.

## 18. Validation Gates

The project cannot move from broad definition to implementation claims until validation contracts are specific enough to test.

Required validation gates include governance/docs consistency, raw-data coverage, credential-safety checks, schema checks, row-universe checks, label checks, no-news checks, alignment checks, split leakage checks, fold-local preprocessing checks, saved-prediction checks, overfitting diagnostic checks, artifact completeness checks, model-comparison row equality checks, and benchmark comparability review.

Current structural governance validation is evidenced as passing, and active scripts are evidenced as compiling from the prior audit session. That does not prove benchmark readiness, dataset completeness, or scientific validity.

## 19. Current Non-Implementation Claims

The following claims must not be made from current active-root evidence.

| Claim | Status |
| --- | --- |
| Active feature, label, split, model, and benchmark pipeline exists. | Partially evidenced through Stage 6 stagewise CLIs and validators; no single approved end-to-end rebuild command is evidenced. |
| Active `src/`, `configs`, and `tests` layers exist. | Partially executable for approved Stage 2 through Stage 7C paths, Stage 8 ops tests, and Stage 10C prediction-output paths; provider/utility/expansion paths remain comment-only scaffolds. |
| A materialized benchmark dataset is complete. | Evidenced for the approved Stage 2 clean-window row/availability dataset, not by itself a benchmark result. |
| A leakage-controlled serious benchmark has been run. | Evidenced for Stage 6 with result class `clean_null` and comparability `limitation_bearing`; not a positive or trading-profitability result. |
| Alpha Vantage article-level completeness is guaranteed. | Not evidenced in repository materials. |
| Top-100 or top-500 data is comparable to the approved top-50 benchmark. | Not evidenced in repository materials. |
| Legacy snapshot code is active implementation truth. | Not evidenced in repository materials. |

## 20. Deferred And Out-Of-Scope Branches

Static company metadata, company KB features, uncertainty-aware outputs, calibration-first reporting, graph-heavy models, MoE, dynamic company profiles, end-to-end text fine-tuning, broad derivative grids, full live-universe first-pass benchmarking, product APIs, dashboards, authentication systems, and user-facing services are outside the phase-1 default unless later explicitly approved.

These branches may remain useful future work. They must not silently enter the phase-1 benchmark or redefine success.

## 21. Open Definition Risks

The broad project definition is stable enough to govern documentation and next-stage contract work, but the following items remain unresolved before broader implementation and serious benchmarking.

| Risk | Required Resolution |
| --- | --- |
| Materialized clean-window record is absent. | Convert the OHLCV-derived candidate into a dataset-version clean-window record only after executable dataset validation exists. |
| Alpha Vantage provider-level article completeness is not claimed. | Preserve truncation and empty-feed flags in dataset and feature artifacts. |
| Final comparator roster could drift after predictions. | Keep `phase1_top50_pragmatic_broader_sklearn_v1` frozen unless an explicit approval and comparability review changes it. |
| Dataset artifact format is documented but not executable. | Resolved for Stage 2 materialization; future dataset-family changes still need executable validation. |
| Data-separation and overfitting controls are documented but not executable. | Partially resolved through Stage 6; train-validation gap remains explicitly blocked because Stage 5 saved no train predictions. |
| Approved-stage executable test coverage is missing. | Resolved for focused Stage 2 through Stage 8 and Stage 10C claims; provider/utility/expansion tests remain future work. |
| Raw ledgers may contain API-key-bearing URLs. | Sanitize or isolate request ledgers and rotate exposed keys before commit, sharing, or publication. |
| Provider-reality validation remains incomplete for provider-level article completeness. | Treat current Alpha Vantage corpus as limitation-bearing evidence unless truncation refinement or a new approved benchmark family resolves the provider limitation. |

## 22. Maintenance Rules For This Definition

This file should be updated when owner-approved scope decisions change, `ResearchTruth.md` changes materially, active architecture definitions are refined, benchmark-family definitions change, or current repository state changes enough to make this definition misleading.

This file must not be used to bypass approval gates. Any change to target family, horizon set, provider stack, universe, news alignment, evaluation protocol, benchmark comparability, or phase boundary requires explicit approval under `AgentRules.md`.

This file is a broad project definition. Detailed implementation contracts belong in active design, testing, execution, and operations documents before code is written.
