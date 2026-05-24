# Complete Theoretical Background

Status: minimum active-root theory skeleton, created 2026-05-06 from `ScopeDecisionLog.md`, `ResearchTruth.md`, and current repository evidence. This file is active theory truth, but it is not a benchmark result and does not claim benchmark readiness.

## Scientific Objective

Phase 1 tests whether aligned firm-news event-state features add predictive value beyond market-only baselines for end-of-day, multi-horizon, forward excess-return forecasting.

The accepted thesis is benchmark-first, not product-first. A robust positive result, a conditional positive result, or a clean null result can all be valid phase-1 outcomes if produced under the approved leakage-controlled benchmark protocol.

## Accepted Hypotheses

- H1: Recent aligned firm-news, represented as event-state features, may add incremental predictive value over market-only baselines for forward excess returns.
- H0: Event-state features may add no reliable incremental value after market-only baselines and leakage controls are enforced.
- H2: Any apparent incremental value must be evaluated across the approved horizon set and cannot be accepted from a single convenient metric or split.

## Active Scope Constraints

- Target family: forward excess returns.
- Horizons: `1d`, `5d`, `10d`, `20d`, and `60d`.
- Universe: reproducible top-50 liquid large-cap universe for the first serious benchmark.
- Provider stack: Twelve Data for OHLCV, Alpha Vantage for financial news, and SEC for static/company support only.
- News alignment: same-day as-of-close, with after-hours and non-trading-day articles rolled forward.
- Evaluation: purged-plus-embargoed walk-forward for development and final untouched lockbox for reporting.
- Option B validation refinement: strict data separation, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, and overfitting diagnostics.
- Runtime boundary: local CLI/artifact-driven research system only.

## Rejected Or Deferred Scope

- Phase 1 is not a trading bot, API, dashboard, user-facing service, or permission-management product.
- Static company metadata and KB features are deferred to phase 2.
- Uncertainty-aware outputs are deferred to a later extension.
- Graph-heavy cores, MoE, dynamic profiles, end-to-end text fine-tuning, broad derivative grids, and first-pass full live-universe benchmarking are out of phase 1 until the core benchmark is stable.
- Later top-100, top-500, or broader-universe runs are separate benchmark families unless explicitly approved otherwise.

## Methodology Constraints

- No serious result may be claimed without reproducible dataset, split, prediction, metric, and comparison artifacts.
- No serious result may be claimed if train/validation/lockbox row separation, purge/embargo accounting, fold-local preprocessing, metric predeclaration, saved out-of-sample predictions, or overfitting diagnostics are missing or violated.
- No-news rows remain in the row universe and must be represented by explicit empty event states plus no-news indicators.
- Raw file coverage is not equivalent to provider-level article completeness, feature completeness, or benchmark readiness.
- Alpha Vantage windows that hit the provider response limit must remain flagged as truncation risk until refined or explicitly accepted as a limitation.
- Provider changes, universe changes, target changes, horizon changes, alignment changes, or evaluation changes are benchmark-family changes and require explicit approval.

## Theory-To-Design Consequences

- The dataset builder must preserve a market-only row universe and add event-state features without dropping no-news rows.
- Label generation must support all approved horizons and use forward excess returns.
- Split generation must support purging, embargoing, walk-forward folds, and a final lockbox boundary.
- Benchmark runners must produce comparable market-only and event-state model outputs on identical rows and splits.
- Artifact manifests must record data versions, provider coverage status, feature contracts, split definitions, preprocessing-fit boundaries, model configs, saved predictions, metrics, and overfitting diagnostics.

## Current Unresolved Theory/Validation Questions

- The exact clean historical benchmark window must still be selected from verified overlap across OHLCV, news, labels, and split feasibility.
- The policy for 92 likely truncated Alpha Vantage top-50 canonical windows remains unresolved.
- The final comparator roster implied by the broadened mandatory ladder still needs design-level freezing.
- Option B data-separation and overfitting-control requirements are documented but not yet executable.
- Provider-reality checks for Alpha Vantage coverage and Twelve Data OHLCV adequacy remain mandatory before serious claims.

## Evidence Pointers

- `ScopeDecisionLog.md`
- `ResearchTruth.md`
- `docs/Data_Separation_And_Overfitting_Control.md`
- `docs/agent/agent_log/Project_Audit_2026-05-06.md`
- `docs/agent/agent_log/AlphaVantage_Raw_Merge_2026-05-06.md`
- `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json`

## Addendum 2026-05-24: Stage 6-10 Evidence, Manual Research Synthesis, And Next-Phase Theory

Status: additive theory update after completion of the five `manual_research` groups, the `docs/research/manual_research/NextSteps-Research.md` synthesis, and the detailed `docs/NextSteps_Brainstorming.md` roadmap. This addendum does not delete or override earlier lines. It records new research context, new stage evidence, and proposed next-phase theory while preserving the distinction between implemented artifacts, research synthesis, and future candidate work.

### Addendum Source Corpus

- `docs/research/manual_research/research_1/results/DeepResearchReport_DailyWeekly Data Refresh Design.md`: Stage 8 daily/weekly data-refresh design, provider-safety, manifests, idempotency, secret redaction, and downstream invalidation rules.
- `docs/research/manual_research/research_2/results/DRR-trajectory graph visualization.md`: Stage 10C trajectory visualization policy, historical-only marker placement, caveat wording, and no-future-price-path rule.
- `docs/research/manual_research/research_3/results/DRR-Relevant News Attribution for Stage 10C Ranking and Display Policy.md`: deterministic relevant-news ranking, context-vs-causality display policy, snippet limits, no-news/truncation handling, and validation checks.
- `docs/research/manual_research/research_3/results/DRR-Relevance signals for news ranking.md`: currently available ranking signals, especially timestamp, aligned-news count, no-news flag, provider-truncation-risk flag, and current absence of extracted sentiment/topic fields.
- `docs/research/manual_research/research_4/results/DRR-Top-10 Multi-Horizon Visualization.md`: Stage 10C per-horizon top-10 visualization, cross-horizon diagnostics, static HTML/table accessibility, and report fidelity checks.
- `docs/research/manual_research/research_4/results/DRR-Top-Decision Ready Memo for the Future Local Update To Prediction Pipeline Architecture.md`: local update-to-prediction architecture options, with a lockfile-backed DAG/wrapper recommended as target architecture and offline future-row inference deferred.
- `docs/research/manual_research/research_5/results/DRR1-ValdiviaEng Financial Event State Forecasting.md` through `DRR6-Executive Summary.md`: repository-level benchmark assessment, current `clean_null` interpretation, model-stack/SOTA gap analysis, reproduction context, data-realism concerns, and Stage 10C report refinements.
- `docs/research/manual_research/NextSteps-Research.md`: consolidated manual-research synthesis and phased next-step research priorities.
- `docs/NextSteps_Brainstorming.md`: detailed decision log for the selected next roadmap, including market baseline suite, XGBoost tuning, FinBERT ablations, TSMixer, diagnostics, Stage 10C thin-slice reporting, ensembles, fusion, and deferred scope.
- `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md` and `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`: Stage 10A/10B research and decision matrix feeding Stage 10C.
- `src/event_state_forecasting/stage10/prediction_outputs.py`, `src/event_state_forecasting/cli/generate_prediction_outputs.py`, `scripts/validate_stage10c_completion.py`, and `data/manifests/stage10c_completion_validation_2026-05-23.json`: implemented and validated Stage 10C local prediction-output packet evidence.

### Updated Implemented Stage Evidence

- Stage 6 is materialized as the serious benchmark reporting stage. It produces regression metrics, ranking diagnostics, paired loss-delta comparisons, overfitting diagnostics, a comparison summary, comparability classification, and a passed serious-run packet. The result class is `clean_null`, and comparability is `limitation_bearing`. This is not a positive result, a trading-profitability claim, or evidence that event-state features can be deployed.
- Stage 7C is materialized as contextual-bandit diagnostics on a new post-Stage-6-lockbox diagnostic holdout. It remains diagnostics-only. It does not reinterpret Stage 6, create a live logged-policy value claim, authorize all-data final execution, or authorize trading signals.
- Stage 8 is implemented as plan-first daily/weekly raw-update tooling for Alpha Vantage news and Twelve Data OHLCV. Its default semantics are no provider calls, no raw overwrites, explicit manifests, secret redaction, skipped/existing-file handling, and downstream invalidation warnings. It is not a benchmark rerun, prediction generator, or provider-completeness claim.
- Stage 9 is documentation and operational-memory reconciliation only. It supports stale-status repair, prompt/index updates, and memory/ledger updates without authorizing new model behavior, provider calls, raw-data mutation, or Stage 6 reinterpretation.
- Stage 10A is research-only workflow analysis for update-to-prediction and visualization. It does not implement outputs or authorize fresh inference.
- Stage 10B is decision capture and comparison for Stage 10C output design. It defines constraints but does not itself implement prediction-output artifacts.
- Stage 10C is implemented and materialized as a local historical prediction-output packet generator from existing Stage 5 saved predictions. Its row role is `historical_prediction`, not `forecast_candidate`. It produces static local artifacts and keeps non-claims: no fresh future inference, no provider call, no raw-data mutation, no hidden Stage 2-6 rerun, no persisted inference package, no service/API/dashboard, no trading signal, no price target, and no Stage 6 reinterpretation.

### Updated Scientific Interpretation

- The strongest current scientific conclusion remains conservative: the repository is a strong benchmark-control system, but the current first-generation model and representation stack did not clear its own serious benchmark hurdle. The current Stage 6 `clean_null` result should be interpreted as credible evidence that the current deterministic hash event representation plus shallow gated fusion did not provide robust incremental value over the selected market-only hurdle under the approved protocol.
- The current `clean_null` result must not be reinterpreted as proof that news or event-state modeling cannot help. The manual research consistently identifies the current event representation and model stack as weak relative to recent financial NLP, multimodal forecasting, tabular boosting, temporal sequence modeling, and cross-sectional/ranking-aware methods.
- The repository's main value is now best described as an auditable benchmark harness that can support controlled upgrades. Its core strengths are row identity, fold-local preprocessing, purged/embargoed splits, lockbox isolation, saved out-of-sample predictions, manifest-backed artifacts, no-news-state preservation, provider-risk flags, explicit non-claims, and willingness to report a clean null.
- The main research weaknesses to address are: 8-dimensional deterministic hash embeddings, same-row market features only, shallow ridge-based gated fusion, modest market comparator strength, absent train predictions for train-gap diagnostics, limited formal uncertainty intervals, provider truncation/no-news sensitivity, frozen-universe sensitivity, and Stage 10C presentation clarity.

### Updated Stage 8 Theory

- Stage 8 should remain plan-first and provider-safe. Daily news refresh should use an overlapping yesterday-through-today or similarly conservative policy; weekly news refresh should use a rolling seven-day or calendar-week-with-overlap policy; OHLCV refresh should respect trading days and skip or defer non-trading dates.
- Idempotency is a theoretical requirement, not only an implementation convenience. Refresh manifests should distinguish planned, skipped-existing, completed, failed, duplicate, no-data, and ambiguous-empty entries. Repeated plan/live runs should not silently mutate raw files.
- Raw preservation remains mandatory. Existing raw files must not be overwritten unless an explicit overwrite flag and approval policy is used. Any overwrite, if ever approved, should be backed up and logged.
- Secret hygiene is part of the research theory because provider ledgers and request manifests can otherwise contaminate shareable artifacts. API keys and key-bearing URLs must be redacted from stdout, logs, manifests, ledgers, and committed outputs.
- Any live raw-data change invalidates downstream artifacts unless a full controlled rebuild is performed. At minimum, Stage 8 live manifests must warn that Stage 2-6 artifacts and Stage 10C packets are stale or historical relative to newer raw data.

### Updated Stage 10 Theory

- Stage 10C outputs are historical-readable artifacts, not live forecasts. The theory of Stage 10C is interpretability of existing saved predictions, not production inference.
- Per-horizon report organization is preferred: separate sections or tables for `1d`, `5d`, `10d`, `20d`, and `60d`, with a clearly labeled cross-horizon diagnostic view. This reduces ambiguity compared with one large mixed-horizon table.
- Stage 10C relevant-news display must remain context-only. Displayed news should be labeled as historically aligned input/context, not as causal explanation, model rationale, advice, or a recommendation. Wording such as “because of this news” is theoretically disallowed.
- Relevant-news ranking should begin with deterministic as-of-safe signals: publication timestamp, aligned-news count, no-news flag, provider-truncation-risk flag, and available ticker/date alignment. Sentiment or topic ranking must not be claimed unless those fields are explicitly extracted and versioned.
- Stage 10C trajectory graphics must avoid future price paths, fan charts, projected price curves, or implied price targets. Historical returns, historical trajectory markers, prediction markers, and label-window-end placement are acceptable if caveats are visible.
- Report fidelity is a theoretical requirement: any HTML/table/image representation must be traceable to CSV/Parquet packet data and must be validated against source values. Static visuals may aid comprehension but tables remain the auditable source of truth.

### New Next-Phase Research Program: Design Truth, Not Implemented Truth

The selected next-phase roadmap is design truth only until implemented and validated. It should not be cited as completed behavior.

- Primary next objective: performance and credibility first, with usability, operations, and publication readiness treated as parallel concerns.
- Main diagnosed risk: weak model stack, especially weak text/event representation and weak market temporal baselines.
- Benchmark-contract stance: mostly strict. Existing target, universe, horizons, splits, lockbox, and result logic remain the comparability anchor; additive or broader changes require versioned artifacts and explicit manifests.
- First implementation milestone: an integrated thin slice with two-tier versioning, a hybrid sidecar feature registry, lag/rolling market features, `market_lag_linear_v1`, `market_xgboost_v1_fixed`, initial `diagnostics_core_v1`, stratified no-news/truncation metrics, and Stage 10C report clarity updates.
- Market baseline suite: `market_lag_linear_v1` for sanity, `market_xgboost_v1_fixed` as first strong boosted-tree hurdle, and `market_tsmixer_v1` as the first compact temporal neural hurdle after the tabular pipeline stabilizes.
- XGBoost tuning design: `market_xgboost_v2_nested_optuna_candidate` may use aggressive nested Optuna under purged/nested folds, but must preserve a fixed honest baseline and freeze configurations before final evaluation. The selected tuning objective is guarded hurdle delta with horizon weights `1d=30%`, `5d=25%`, `10d=20%`, `20d=15%`, `60d=10%`, and balanced RMSE/MAE within each horizon.
- TSMixer design: pure PyTorch only, no external library dependency for the serious path. TSMixer starts standalone and smoke/fixed/multiseed, with nested optimization only if standalone evidence is promising.
- Text/event representation design: `event_finbert_embedding_v1` uses a pinned Hugging Face FinBERT-style source, article embedding cache/checksums, mean token embedding plus sentiment logits/probabilities if supported, and a controlled ablation suite over mean pooling, recency weighting, top-k recent pooling, and count-plus-recency aggregation.
- Diagnostics design: all serious promoted variants require train-gap diagnostics, no-news/news-rich/truncation/article-count stratified evaluation, date-clustered confidence intervals, and block-bootstrap uncertainty before final promotion.
- Ensemble/fusion design: after standalone evidence, always explore high-accuracy XGBoost + TSMixer combinations, with `market_xgb_tsmixer_horizon_meta_v1` as the first high-accuracy ensemble candidate. For market + FinBERT event features, `event_market_horizon_fusion_v1` is the first selected fusion candidate.

### New Deferred Or Rejected Current-Phase Theory

- Dashboard/API/service work remains out of scope for the current phase.
- Live forecasts, feature-only future rows, and `forecast_candidate` semantics remain deferred.
- Trading signals, buy/sell recommendations, price targets, and portfolio advice remain disallowed.
- Local LLM news summaries remain deferred because deterministic snippets, FinBERT features, and Stage 10C context policy should be proven first.
- Provider expansion remains deferred until current Alpha Vantage no-news/truncation behavior is measured and understood.
- Foundation-model time-series adapters, graph/relational stock models, event extraction, neural cross-fusion, residual stacks, and rank-aware meta-combiners are research candidates, not first thin-slice requirements.

### Updated Evidence Pointers

- `docs/research/manual_research/NextSteps-Research.md`
- `docs/NextSteps_Brainstorming.md`
- `docs/research/manual_research/research_1/results/DeepResearchReport_DailyWeekly Data Refresh Design.md`
- `docs/research/manual_research/research_2/results/DRR-trajectory graph visualization.md`
- `docs/research/manual_research/research_3/results/DRR-Relevant News Attribution for Stage 10C Ranking and Display Policy.md`
- `docs/research/manual_research/research_3/results/DRR-Relevance signals for news ranking.md`
- `docs/research/manual_research/research_4/results/DRR-Top-10 Multi-Horizon Visualization.md`
- `docs/research/manual_research/research_4/results/DRR-Top-Decision Ready Memo for the Future Local Update To Prediction Pipeline Architecture.md`
- `docs/research/manual_research/research_5/results/DRR1-ValdiviaEng Financial Event State Forecasting.md`
- `docs/research/manual_research/research_5/results/DRR2-ValdiviaEng Financial Event State Forecasting_in-double-detail.md`
- `docs/research/manual_research/research_5/results/DRR3-ValdiviaEng Financial Event State Forecasting_in-triple-detail.md`
- `docs/research/manual_research/research_5/results/DRR4-ValdiviaEng Financial Event State Forecasting_extended_4.md`
- `docs/research/manual_research/research_5/results/DRR5-Recommended view layout.md`
- `docs/research/manual_research/research_5/results/DRR6-Executive Summary.md`
- `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`
- `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`
- `data/manifests/stage6_completion_validation_2026-05-21.json`
- `data/manifests/stage7_post_lockbox_completion_validation_2026-05-22.json`
- `data/manifests/stage10c_completion_validation_2026-05-23.json`
