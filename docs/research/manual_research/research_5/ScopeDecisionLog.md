# Scope Decision Log

## 1. Session Status
- Total DQ items: 44
- Answered: 44
- Default accepted: 0
- Deferred: 0
- Skipped: 0
- Pending: 0
- Last updated decision/approval: `S10C-APPROVAL-001`
- Next expected question: explicit approval only if future work needs persisted inference packaging, new `forecast_candidate` semantics, live provider calls, service/API/dashboard scope, trading/signal outputs, Stage 6 reinterpretation, or benchmark-comparability promotion

Stage 10C is now executed for the first local saved-prediction extraction packet path under `S10C-APPROVAL-001`; future expansion beyond that packet boundary remains approval-gated.

Original phase-1 scope interview remains complete at 24 answered DQ items. Stage 7B is complete at 10 answered Stage 7B items and 0 pending/unanswered items. The answered Stage 7B items established a direct contextual-bandit scope expansion, new post-lockbox holdout direction, two-track row-filter direction, development-only rolling-replay benchmark/design policy with a later separate final-execution-pipeline concept, two-sided top-k per-horizon action-space direction, two-sided forward-return reward package, supervised-ranking-then-epsilon-greedy algorithm direction, combined Stage 3 plus Stage 5 context direction, full mandatory baseline bundle, and saved-diagnostics plus Stage 7C docs plus final-execution-stub output direction. Subsequent Stage 7C approvals on 2026-05-22 authorized Stage 7C implementation, an approved data update with old settings preserved, and minimal plus serious diagnostics, but explicitly did not approve all-data final-execution training-output, live buy/sell signals, Stage 6 reinterpretation, raw-news/LLM context expansion, or benchmark-comparability promotion. Stage 8 approval authorized local plan-first daily/weekly raw update scripts and tests only; it did not authorize live provider calls, raw overwrites, provider-completeness claims, benchmark reruns, or trading/prediction outputs. Stage 9 approval authorized documentation and operational-memory reconciliation only; it did not authorize feature code, provider calls, raw-data changes, benchmark reruns, result reinterpretation, or sensitive-artifact sharing. Stage 10A approval authorized research-only update-to-prediction and visualization workflow analysis; it did not authorize implementation, provider calls, raw-data mutation, prediction outputs, visualization artifacts, service/API scope, trading signals, Stage 6 reinterpretation, or benchmark-comparability promotion. Stage 10B continuation authorized a decision-comparison draft and pending decision register only; it does not approve Stage 10C development, provider calls, raw-data mutation, prediction-output artifacts, visualization artifacts, persisted inference packaging, service/API/dashboard scope, trading signals, Stage 6 reinterpretation, or benchmark-comparability promotion.

## 2. Decision Register
| DQ ID | Status | Blocking Status | Priority Score | Owner Decision Summary | Source Default | Decision Type |
|------|--------|-----------------|----------------|------------------------|----------------|---------------|
| DQ-001 | Answered | Blocking | 84 | Custom: rebuild in active root with selective salvage only after research truth is finalized | Option A: greenfield rebuild with selective salvage | Architecture |
| DQ-002 | Answered | Blocking | 82 | Option A selected: narrow phase-1 to the event-state incremental-value thesis | Option A: narrow event-state incremental-value thesis | Product Scope |
| DQ-003 | Answered | Blocking | 81 | Option A selected: forward excess returns as the primary target family | Option A: forward excess returns | Data Model |
| DQ-004 | Answered | Important | 64 | Custom: first serious benchmark uses `1d, 5d, 10d, 20d, 60d` horizons | Option A: `1/5/20` core | Data Model |
| DQ-005 | Answered | Blocking | 88 | Option A selected: canonicalize the implemented as-of-close same-day rule | Option A: canonicalize as-of-close same-day | Workflow |
| DQ-006 | Answered | Blocking | 86 | Option A selected: freeze one narrow serious benchmark family before more work | Option A: freeze one narrow serious benchmark family first | Testing |
| DQ-007 | Answered | Important | 69 | Custom: freeze first serious benchmark on a reproducible top-50 liquid large-cap universe; later 100/500 expansions are separate benchmark families | Option A: fixed medium liquid large-cap subset | Data Model |
| DQ-008 | Answered | Important | 71 | Custom: Twelve Data OHLCV + AlphaVantage news + SEC only | Option A: Twelve Data + Finnhub + SEC only | Integration |
| DQ-009 | Answered | Important | 67 | Option A selected: pooled dense embeddings plus scalar enrichments as the default event-state package | Option A: pooled dense embeddings plus scalar enrichments | Architecture |
| DQ-010 | Answered | Important | 65 | Option A selected: simple gated fusion as the phase-1 default | Option A: simple gated fusion | Architecture |
| DQ-011 | Answered | Important | 71 | Option C selected: expand mandatory ladder to include broader serious comparator families now | Option A: linear + market-only MLP + simple multimodal | Testing |
| DQ-012 | Answered | Blocking | 84 | Option A selected: purged+embargoed walk-forward plus final untouched lockbox; 2026-05-07 Option B refinement adds strict data separation and overfitting diagnostics without changing the protocol | Option A: purged+embargoed walk-forward plus lockbox | Testing |
| DQ-013 | Answered | Important | 69 | Option A selected: regression primary, ranking secondary but mandatory; metrics must be predeclared and computed from saved out-of-sample predictions | Option A: regression primary, ranking secondary but mandatory | Testing |
| DQ-014 | Answered | Important | 52 | Option A selected: keep static company metadata out of phase 1 and move it to phase 2 | Option A: phase-2 extension only | Data Model |
| DQ-015 | Answered | Nice-to-have | 53 | Option A selected: keep uncertainty-aware outputs as a later extension only | Option A: later extension only | Testing |
| DQ-016 | Answered | Important | 68 | Option A selected: explicitly defer the high-risk branches until the core benchmark is stable | Option A: explicitly defer the high-risk branches | Product Scope |
| DQ-017 | Answered | Blocking | 80 | Option A selected: recreate active theory/design docs before coding | Option A: recreate active docs before coding | Delivery |
| DQ-018 | Answered | Important | 74 | Option A selected: strong evidence bar with rerun-capable tests, structured run validation, contamination blockers, and overfitting diagnostics | Option A: rerun-capable tests, provider checks, structured summaries | Observability |
| DQ-019 | Answered | Important | 51 | Option A selected: keep phase 1 as a local CLI/artifact-driven research system only | Option A: local CLI/artifact research system only | Infra |
| DQ-020 | Answered | Important | 68 | Option A selected: archive remains reference-only and reused ideas must be absorbed into active-root docs | Option A: archive reference-only, active docs absorb reuse deliberately | Other |
| DQ-021 | Answered | Important | 73 | Option A selected: shorter verified overlapping clean window | Option A: shorter overlapping clean window | Data Model |
| DQ-022 | Answered | Important | 71 | Option A selected: explicit empty event state with no-news indicators | Option A: explicit empty event state plus no-news indicators | Workflow |
| DQ-023 | Answered | Important | 65 | Option A selected: require the full reproducible serious-run artifact packet; Option B refinement also requires split/preprocessing manifests and overfitting diagnostic report | Option A: dataset version + manifest + config + folds + predictions + metrics + comparison summary | Observability |
| DQ-024 | Answered | Important | 56 | Option A selected: positive, conditional positive, or clean null all count as valid phase-1 success | Option A: positive, conditional positive, or clean null all count | Delivery |

## 2A. Stage 7B Decision Register

These entries were added on 2026-05-22 from `docs/research_results/stage7b_contextual_bandit_decision_draft_2026-05-22.md`. Owner answers are complete, and later Stage 7C approvals authorized diagnostics-only implementation and the approved Twelve Data update. The answered entries and Stage 7C approvals still do not approve all-data final-execution training-output, live buy/sell signals, Stage 6 reinterpretation, raw-news/LLM context expansion, provider-stack drift, or benchmark-comparability promotion.

| Pending ID | Status | Blocking Status | Priority Score | Draft Recommendation | Alternatives Compared | Decision Type |
| --- | --- | --- | ---: | --- | --- | --- |
| S7B-DQ-001 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 82 | Owner custom decision: direct scope expansion | Research diagnostic only; separate benchmark family; later production-style policy prototype; owner custom scope expansion | Product Scope |
| S7B-DQ-002 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 86 | Owner selected: new post-lockbox holdout after approved data update | Development folds only; new post-lockbox holdout after approved data update; separate sandbox using copied historical rows | Testing |
| S7B-DQ-003 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 78 | Owner selected: two-track all-row primary plus news-days-only secondary diagnostic | All rows; news-days only with explicit non-comparability; two-track all-row plus news-days diagnostic | Testing |
| S7B-DQ-004 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 76 | Owner selected: development-only rolling replay for benchmark/design, with learning curves and a separate later all-data final-execution-pipeline concept | Last 1 year sandbox; full clean window replay; development-only rolling replay | Testing |
| S7B-DQ-005 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 74 | Owner selected: two-sided top-k per horizon, covering top-k best candidates and bottom-k worst/downside candidates | Choose one ticker per day; choose top-k basket; choose horizon-specific model/rank; choose abstain/cash | Data Model |
| S7B-DQ-006 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 84 | Owner selected: two-sided forward-return package with top-k mean return, bottom-k downside return, and secondary spread metric | Forward excess return by horizon; rank-normalized reward; sign hit; cost-adjusted exploratory diagnostic only | Data Model |
| S7B-DQ-007 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 70 | Owner selected: supervised two-sided ranking with explicit diagnostics first, then epsilon-greedy as first adaptive bandit | LinUCB; Thompson sampling; epsilon-greedy regression; non-bandit supervised ranking baseline | Architecture |
| S7B-DQ-008 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 72 | Owner selected: combined frozen Stage 3 features plus fold-safe Stage 5 predictions, with predictions-only ablation | Stage 3 features only; Stage 5 predictions as context; combined feature and prediction context | Data Model |
| S7B-DQ-009 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 80 | Owner selected: full baseline bundle before any bandit-value claim | Market-only policy; event-state supervised ranker; random policy; no-news abstain policy | Testing |
| S7B-DQ-010 | Answered | Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes | 68 | Owner selected: saved benchmark diagnostics plus Stage 7C protocol docs plus final-execution design stub; no live trading signal | Research artifact only; saved policy diagnostics; future executable Stage 7C docs; no trading signal | Observability |

## 2C. Stage 7C Execution Approval Register

These entries record approvals that occurred after Stage 7B decision collection. They authorize the executed Stage 7C implementation/data-update/diagnostic path only under the listed exclusions.

| Approval ID | Status | Owner Decision Summary | Explicit Exclusions |
| --- | --- | --- | --- |
| S7C-APPROVAL-001 | Approved | Execute Stage 7C implementation from the completed Stage 7B decisions. | Does not reinterpret Stage 6 or approve live signals. |
| S7C-APPROVAL-002 | Approved | Use primary `k=5`, diagnostic `k=3/10`, primary epsilon `0.05`, and diagnostic epsilon `0.01/0.10`. | Does not approve abstain/cash, trading-cost reward, shorting, or live trading behavior. |
| S7C-APPROVAL-003 | Approved | Perform a Stage 7 data update while preserving old data/settings in a deprecated folder at the same address. | Does not approve provider-stack drift, universe expansion comparability, or provider-level news-completeness claims. |
| S7C-APPROVAL-004 | Approved with exclusion | Do all Stage 7C work except all-data final-execution training-output; first run a minimal functionality test and serious accuracy diagnostics. | All-data final-execution training-output remains unapproved; live buy/sell signals remain unapproved. |

## 2D. Stage 8 Execution Approval Register

These entries record Stage 8 implementation approval boundaries. They authorize local plan-first update tooling only unless a later approval explicitly opens live provider execution.

| Approval ID | Status | Owner Decision Summary | Explicit Exclusions |
| --- | --- | --- | --- |
| S8-APPROVAL-001 | Approved with exclusion | Implement Stage 8 daily/weekly raw-data update scripts for Alpha Vantage news and Twelve Data OHLCV with tests and documentation. | No live provider calls, raw overwrites, provider-stack drift, universe expansion, provider-completeness claim, benchmark rerun, Stage 6 reinterpretation, prediction output, or live trading signal. |

## 2E. Stage 9 Execution Approval Register

These entries record Stage 9 documentation-reconciliation approval boundaries. They authorize stale-status repair and memory updates only.

| Approval ID | Status | Owner Decision Summary | Explicit Exclusions |
| --- | --- | --- | --- |
| S9-APPROVAL-001 | Approved with exclusion | Implement Stage 9 final documentation reconciliation after Stage 8. | No feature code, provider call, raw-data mutation, benchmark rerun, Stage 6 reinterpretation, benchmark-comparability promotion, prediction output, sensitive-artifact sharing, or live trading signal. |

## 2F. Stage 10A Execution Approval Register

These entries record Stage 10A research approval boundaries. They authorize local workflow research only and do not authorize development.

| Approval ID | Status | Owner Decision Summary | Explicit Exclusions |
| --- | --- | --- | --- |
| S10A-APPROVAL-001 | Approved with exclusion | Execute the next stage as Stage 10A research for local update-to-prediction outputs and visualization. | No feature code, provider call, raw-data mutation, benchmark rerun, prediction-output artifact, visualization artifact, user-facing service/API scope, live trading signal, Stage 6 reinterpretation, or benchmark-comparability promotion. |

## 2G. Stage 10B Execution Approval Register

These entries record the Stage 10B continuation boundary. They authorize decision-comparison documentation and approval-decision capture only.

| Approval ID | Status | Owner Decision Summary | Explicit Exclusions |
| --- | --- | --- | --- |
| S10B-APPROVAL-001 | Approved with exclusion | Continue from the Stage 10A checkpoint by executing Stage 10B as a decision-comparison draft and approval checklist. | No Stage 10C implementation, provider call, raw-data mutation, benchmark rerun, prediction-output artifact, visualization artifact, persisted inference package, new forecast-row role, service/API/dashboard scope, live trading signal, Stage 6 reinterpretation, or benchmark-comparability promotion. |

## 2H. Stage 10B Decision Register

These entries were added on 2026-05-23 from `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`. They record all owner answers and define Stage 10C design constraints. The first Stage 10C implementation later consumed these decisions under separate approval as a local saved-prediction extraction packet; future expansion remains separately approval-gated.

| Decision ID | Status | Blocking Status | Priority Score | Owner Decision Summary | Alternatives Compared | Decision Type |
| --- | --- | --- | ---: | --- | --- | --- |
| S10B-DQ-001 | Answered | Resolved and implemented for the first Stage 10C local packet; future output-status expansion still requires approval | 88 | Owner selected: local model-output / forecast-candidate artifact only; not trading advice, not benchmark result, not service/API output. | Local forecast-candidate artifact; research diagnostic only; no Stage 10C output | Product Scope |
| S10B-DQ-002 | Answered | Resolved and implemented for the first Stage 10C local packet; future scheduler/provider/service scope still requires approval | 84 | Owner selected: single local artifact CLI consuming explicit artifact roots and data cutoffs; no scheduled job, live provider calls, raw overwrites, hidden Stage 2-6 reruns, service/API/dashboard, or Stage 6 reinterpretation. | Manual documented sequence; single local artifact CLI; scheduled task wrapper | Operations |
| S10B-DQ-003 | Answered | Resolved and implemented for saved-prediction extraction; persisted inference packaging still requires approval | 90 | Owner selected: saved-prediction extraction as first implementation path, with full Stage 2-6 rebuild output compatibility; no persisted inference package yet. | Saved-prediction extraction; full Stage 2-6 rebuild then extraction; persisted inference package | Architecture |
| S10B-DQ-004 | Answered | Resolved and implemented for the first Stage 10C local packet; new row semantics still require approval | 86 | Owner selected: versioned `data/prediction_outputs/...` packet. Use a separate governed Stage 10 output root and preserve row-role caveats. | Versioned `data/prediction_outputs`; `runs/predictions/<timestamp>`; under Stage 6 artifact root | Data Model |
| S10B-DQ-005 | Answered | Resolved and implemented for static HTML plus CSV/Parquet packet output | 80 | Owner selected: static HTML plus CSV/Parquet packet. | Static HTML plus CSV/Parquet packet; PNG/CSV bundle; notebook or local dashboard | Design |
| S10B-DQ-006 | Answered | Resolved and implemented for primary/secondary/tertiary Stage 10C tables | 78 | Owner selected: per-horizon event-state score primary, delta over market hurdle secondary reporting, combined cross-horizon score third-priority diagnostic only, with clear context/caveats and a final non-claim joint summary. | Per-horizon event-state score; per-horizon delta over market hurdle; combined cross-horizon score | Data Model |
| S10B-DQ-007 | Answered | Resolved and implemented for deterministic aligned-news context without URLs or LLM summaries | 76 | Owner selected: aligned-news fields required, deterministic text snippets optional if validated, no LLM summaries for first implementation. | Aligned-news fields only; deterministic text snippets; LLM summary | Design |
| S10B-DQ-008 | Answered | Resolved and implemented for observed history plus forecast markers, with no projected price path | 74 | Owner selected: price history plus forecast markers as primary, last-month predictions plus realized labels as optional historical diagnostic panel, no projected price path. | Price history plus forecast markers; last-month predictions plus realized labels; horizon fan chart or projected price path | Design |
| S10B-DQ-009 | Answered | Resolved and implemented with focused tests plus packet validator | 92 | Owner selected: full packet/report validation. | Full packet/report validation; minimal smoke validation; manual review only | Validation |
| S10B-DQ-010 | Answered | Resolved and implemented with sensitive-artifact exclusion checks | 90 | Owner selected: exclude raw API-key-bearing ledgers, raw provider secrets, unsanitized request URLs, API keys, raw request ledgers, and unsanitized provider logs from packets/reports. | Exclude secrets and raw ledgers; include redacted operational summaries; include raw request ledgers for audit | Security |

## 2I. Stage 10C Execution Approval Register

These entries record the Stage 10C implementation boundary. They authorize only the local saved-prediction extraction packet path implemented on 2026-05-23.

| Approval ID | Status | Owner Decision Summary | Explicit Exclusions |
| --- | --- | --- | --- |
| S10C-APPROVAL-001 | Approved with exclusion | Execute Stage 10C as a local CLI/artifact implementation under the resolved Stage 10B constraints, using existing Stage 5 saved predictions to create dated prediction-output packets and validation evidence. | No live provider calls, raw-data mutation, hidden Stage 2-6 rerun, persisted inference package, new `forecast_candidate` role, service/API/dashboard scope, trading/signal output, Stage 6 reinterpretation, or benchmark-comparability promotion. |

## 2J. Stage 10B Detailed Decision Entries

### S10B-DQ-001: What should Stage 10C outputs be allowed to claim?
- Original question: Should Stage 10C output a local forecast-candidate artifact, a historical research diagnostic only, or no Stage 10C output?
- Decision type: Product Scope
- Blocking status: Blocks Stage 10C output semantics
- Priority score: 88
- Draft recommendation before owner answer: Local dated forecast-candidate artifact only, with `not_trading_advice` and `not_benchmark_result` wording.
- Evidence references: `Stage10BPrompt.md`; Stage 10A memo; `ScopeDecisionLog.md` DQ-019; `ResearchTruth.md` RT-048; `UsageManual.md`
- Owner answer: Option A, clarified as a local model-output / forecast-candidate artifact.
- Normalized decision: Stage 10C may later design local, readable artifacts from implemented model outputs, labeled as forecast candidates or model-output summaries, with strict `not_trading_advice`, `not_benchmark_result`, and `not_stage6_reinterpretation` wording. This answer does not approve Stage 10C implementation by itself.
- Selected option: Option A: Local forecast-candidate artifact.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C may be scoped toward usable local output packets from implemented model outputs, but still may not create buy/sell, price-target, service/API/dashboard, benchmark-result, Stage 6 reinterpretation, provider-call, raw-mutation, or trading-signal claims.
- Notes: If the owner wants live trading or buy/sell wording, Stage 10C must stop for a separate scope decision.

### S10B-DQ-002: How should Stage 10C be invoked, and how should refreshed data enter it?
- Original question: Should orchestration be a manual documented sequence, a single local CLI wrapper, or a scheduled task wrapper, and should data refresh be consumed from Stage 8 outputs or invoked directly?
- Decision type: Operations
- Blocking status: Blocks Stage 10C orchestration design
- Priority score: 84
- Draft recommendation before owner answer: Single local artifact CLI or documented local sequence that consumes explicit artifact roots and approved Stage 8 outputs; no scheduler and no live provider calls by default.
- Evidence references: `Stage10BPrompt.md`; `Stage8Prompt.md`; `ExecutionPipeline.md`; `UsageManual.md`; `docs/Data_Update_Strategy.md`
- Owner answer: Option B: Single Local Artifact CLI.
- Normalized decision: Stage 10C may later design a single local artifact-generation CLI that consumes explicit existing artifact roots and data cutoffs, writes local readable output artifacts, and validates provenance/non-claims. The CLI must not call providers, overwrite raw data, silently rerun Stage 2 through Stage 6, start a service/API/dashboard, or reinterpret Stage 6.
- Selected option: Option B: Single local artifact CLI.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C orchestration should be implemented as a local artifact-output command rather than a manual-only workflow or scheduled automation, if Stage 10C implementation is later approved.
- Notes: Stage 8 `--execute`, raw `--overwrite`, and scheduled automation remain separate approvals.

### S10B-DQ-003: Which model outputs and prediction-generation method should Stage 10C expose?
- Original question: Should Stage 10C use saved-prediction extraction, full Stage 2-6 rebuild then extraction, or a new persisted inference package?
- Decision type: Architecture
- Blocking status: Blocks prediction-generation contract
- Priority score: 90
- Draft recommendation before owner answer: Saved-prediction extraction plus full-rebuild compatibility first; persisted inference packaging only after separate explicit approval if true fresh forecast rows are required.
- Evidence references: Stage 10A memo; `UsageManual.md`; `configs/models.yaml`; Stage 5 saved-prediction contract; `ExecutionPipeline.md`
- Owner answer: Option A as the first implementation path, with Option B compatibility.
- Normalized decision: Stage 10C may later generate readable local outputs from existing or explicitly supplied Stage 5 saved-prediction artifacts. The output CLI should be compatible with artifacts from a future approved Stage 2 through Stage 6 rebuild by accepting explicit artifact roots, but it must not implement persisted inference packaging or arbitrary feature-only future-row scoring yet.
- Selected option: Custom combined decision: Option A primary with Option B compatibility; Option C rejected for first Stage 10C implementation.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C should package implemented model outputs from saved predictions and preserve model provenance. A true persisted inference package remains a separate future architecture decision requiring explicit approval.
- Notes: Current Stage 5 saved predictions are validation/lockbox rows only.

### S10B-DQ-004: How should Stage 10C label rows and where should packets be written?
- Original question: Should output folders live under `data/prediction_outputs/phase1_top50`, generic `runs/predictions`, or the Stage 6 artifact root, and how should `forecast_candidate` be handled?
- Decision type: Data Model
- Blocking status: Blocks output row semantics and folder contract
- Priority score: 86
- Draft recommendation before owner answer: Use a versioned `data/prediction_outputs/phase1_top50/...` root and reserve `forecast_candidate` for explicitly approved future-row inference outputs.
- Evidence references: Stage 10A memo; `Stage10BPrompt.md`; `UsageManual.md`; `ResearchTruth.md` RT-042 and RT-048
- Owner answer: Versioned `data/prediction_outputs/...` packet.
- Normalized decision: Stage 10C may later write governed output packets under a separate versioned `data/prediction_outputs/phase1_top50/...` family, rather than generic runtime folders or Stage 6 artifact roots. Packet naming should preserve run date, data cutoff, source/row/model provenance, and output schema version where feasible.
- Selected option: Option A: Versioned `data/prediction_outputs` packet.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C output artifacts should remain separate from Stage 6 benchmark evidence and must preserve `not_benchmark_result`, `not_trading_advice`, and non-Stage-6-reinterpretation semantics.
- Notes: Use `historical_prediction` for extracted Stage 5 saved-prediction rows, `diagnostic_only` where appropriate, and reserve `forecast_candidate` for explicitly approved future-row or refreshed-artifact output semantics. No row role may imply benchmark evidence or trading advice.

### S10B-DQ-005: Which files and visualization format should Stage 10C create?
- Original question: Should outputs be a static HTML plus CSV/Parquet packet, a PNG/CSV bundle, a notebook, or a local dashboard?
- Decision type: Design
- Blocking status: Blocks report and file output design
- Priority score: 80
- Draft recommendation before owner answer: Static HTML plus CSV/Parquet packet with JSON manifest and limitations file; PNG optional; notebook development-only; no dashboard.
- Evidence references: Stage 10A memo; `Stage10BPrompt.md`; `ScopeDecisionLog.md` DQ-019; `UsageManual.md`
- Owner answer: Option A.
- Normalized decision: Stage 10C may later create a local static HTML plus CSV/Parquet packet, including a JSON manifest, machine-readable tables, limitations metadata, and an offline `report.html` generated from packet data. PNG exports may be considered only as derived optional artifacts if later implementation includes them; notebooks remain development-only and dashboards remain out of scope.
- Selected option: Option A: Static HTML plus CSV/Parquet packet.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C output design should prioritize an auditable packet with machine-readable data and a static offline report. Report/data consistency tests are required before outputs are trusted.
- Notes: A local dashboard remains outside the current phase-1 boundary unless separately approved.

### S10B-DQ-006: How should top-10 candidates be ranked?
- Original question: Should the top-10 view rank by event-state score, delta over market hurdle, or a combined cross-horizon score?
- Decision type: Data Model
- Blocking status: Blocks top-10 table semantics
- Priority score: 78
- Draft recommendation before owner answer: Deterministic per-horizon top 10 by event-state prediction with visible limitation flags; delta over market hurdle as optional secondary view.
- Evidence references: Stage 10A memo; `Stage10BPrompt.md`; Stage 6 selected market hurdles; `ResearchTruth.md` RT-043
- Owner answer: A primary, with B as secondary reporting; C as the third priority. Clear context for each graph/visualization and caveats of understanding. A final joint conclusion taking all visualizations into account would be a nice final addon, taking into account the predominant traits across the different cases.
- Normalized decision: Stage 10C may later produce per-horizon top-10 tables ranked by selected event-state model prediction as the primary view, per-horizon delta-over-market-hurdle reporting as a secondary model-comparison view, and a combined cross-horizon score only as a third-priority diagnostic view. Each visualization/table must include clear context and caveats, and the report may include a final joint summary of predominant traits across views, provided it remains a non-trading, non-benchmark, non-Stage-6-reinterpretation summary.
- Selected option: Custom combined decision: Option A primary, Option B secondary, Option C tertiary diagnostic only.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C should implement deterministic ranking and tie-break tests for the primary per-horizon view and separately validate any secondary/tertiary views. Cross-horizon aggregation must not be presented as a trading score or benchmark result.
- Notes: The final joint conclusion is approved only as caveated output interpretation across visualizations, not as buy/sell advice, price target, proof of model superiority, or Stage 6 reinterpretation.

### S10B-DQ-007: How should relevant news be selected for display?
- Original question: Should Stage 10C display aligned-news fields, deterministic text snippets, or future LLM summaries?
- Decision type: Design
- Blocking status: Blocks relevant-news display semantics
- Priority score: 76
- Draft recommendation before owner answer: Deterministic aligned-news display only; no LLM summaries by default.
- Evidence references: Stage 10A memo; `Stage10BPrompt.md`; `ResearchTruth.md` RT-017 and RT-018; Stage 3 aligned-news artifacts
- Owner answer: A required, B optional if validated, no C for first implementation.
- Normalized decision: Stage 10C must include deterministic aligned-news fields and limitation flags from existing aligned artifacts. It may include deterministic titles/snippets from already-aligned local news rows only if cutoff correctness, source handling, length limits, and caveat wording are validated. LLM summaries are rejected for the first implementation.
- Selected option: Custom combined decision: Option A required, Option B optional if validated, Option C rejected for first implementation.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C relevant-news output must be deterministic and local. Displayed news remains input context, not causal attribution, and provider-level Alpha Vantage article completeness is not claimed.
- Notes: Any future LLM summary capability requires separate reproducibility, dependency, source-text, and governance approval.

### S10B-DQ-008: What should prediction trajectory graphs show?
- Original question: Should trajectory graphs show price history plus forecast markers, last-month predictions plus realized labels, or horizon fan/projected price paths?
- Decision type: Design
- Blocking status: Blocks trajectory graph semantics
- Priority score: 74
- Draft recommendation before owner answer: Historical observed context plus separate forecast markers; no projected price path.
- Evidence references: Stage 10A memo; `Stage10BPrompt.md`; `ResearchTruth.md` target and horizon entries; `UsageManual.md`
- Owner answer: Option A as the primary trajectory graph, with Option B as an optional historical diagnostic panel.
- Normalized decision: Stage 10C may later show historical price/return context plus separate horizon-specific forecast markers as the primary trajectory graph. It may also include a historical diagnostic panel showing prior predictions plus realized labels where label windows have elapsed. Stage 10C must not draw projected price paths or horizon fan charts from forward excess-return markers.
- Selected option: Custom combined decision: Option A primary, Option B optional historical diagnostic, Option C rejected.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C graph data must validate marker dates, horizon endpoints, prediction values, model IDs, and realized-label availability. Future realized returns must be absent until label windows have elapsed.
- Notes: Graphs must clearly state that markers are predicted forward excess-return model outputs, not price targets or trading recommendations.

### S10B-DQ-009: What validation bar must Stage 10C meet?
- Original question: Should Stage 10C require full packet/report validation, minimal smoke validation, or manual review only?
- Decision type: Validation
- Blocking status: Blocks Stage 10C validation threshold
- Priority score: 92
- Draft recommendation before owner answer: Full manifest, row, rank, report-consistency, cutoff, no-network, and non-claim tests.
- Evidence references: `AgentRules.md`; `docs/agent/AgentTemplates.md`; Stage 10A validation checklist; `docs/testing_commands.md`
- Owner answer: Option A.
- Normalized decision: Stage 10C must include full packet/report validation before outputs are trusted, including manifest identity, source provenance, row universe, horizons, cutoff correctness, rank determinism, report consistency, non-claim wording, no-network/service behavior, and sensitive-artifact exclusion.
- Selected option: Option A: Full packet/report validation.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C implementation must include focused tests and validators before completion claims. Outputs should fail closed if validation fails.
- Notes: Standard repo commands remain required after implementation.

### S10B-DQ-010: What sensitive artifacts must Stage 10C exclude?
- Original question: Should packets exclude secrets and raw ledgers, include only redacted operational summaries, or copy raw request ledgers for audit?
- Decision type: Security
- Blocking status: Blocks sensitive artifact policy
- Priority score: 90
- Draft recommendation before owner answer: Exclude raw API-key-bearing ledgers, raw provider secrets, and unsanitized request URLs from packets/reports; allow redacted summaries only after tests.
- Evidence references: `docs/Data_Update_Strategy.md`; `Stage8Prompt.md`; Stage 1 sensitive-ledger findings; Stage 10A memo
- Owner answer: Option A.
- Normalized decision: Stage 10C packets and reports must exclude raw API-key-bearing ledgers, raw provider secrets, unsanitized request URLs, raw request ledgers, API keys, and unsanitized provider logs. They may include sanitized manifests, derived limitations, and non-sensitive source references only; redacted operational summaries are not approved for the first implementation path unless separately validated and approved later.
- Selected option: Option A: Exclude secrets and raw ledgers.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 10C must include redaction/exclusion tests and sanitized manifest fields, and must fail closed if sensitive material is detected.
- Notes: Raw ledgers remain unsafe to commit, publish, or package as-is. Option B redacted operational summaries and Option C raw request ledgers are not approved for the first implementation path.

## 2B. Stage 7B Detailed Entries

### S7B-DQ-001: What should Stage 7 contextual-bandit work be for?
- Original question: Should Stage 7 be a research diagnostic only, a separate contextual-bandit benchmark family, or a later production-style policy prototype?
- Decision type: Product Scope
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 82
- Draft recommendation before owner answer: Research diagnostic only.
- Recommendation confidence: 78
- Evidence references: `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md`; `Stage7BPrompt.md`; `ProjectDefinition.md`; `docs/Benchmark_Testing.md`
- Owner answer: A direct scope expansion.
- Normalized decision: Stage 7 contextual-bandit work is accepted as a direct scope expansion beyond the completed Stage 6 supervised benchmark/reporting path. The exact benchmark family, evaluation segment, row filter, time span, action space, reward, algorithm, context, baselines, and output status remain unresolved in `S7B-DQ-002` through `S7B-DQ-010`.
- Selected option: Custom: direct scope expansion.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7 continued as an explicit contextual-bandit scope-expansion track and later Stage 7C diagnostics were executed under separate approvals. This answer does not approve all-data final-execution training-output, live buy/sell signals, raw-news/LLM context expansion, Stage 6 reinterpretation, or comparability promotion.
- Affected downstream questions: S7B-DQ-002 through S7B-DQ-010
- Notes: Owner used a custom answer rather than one of the draft options. Treat as a scope-expansion decision only, not as a detailed protocol approval.

### S7B-DQ-002: What evaluation segment should Stage 7 use?
- Original question: Should Stage 7 use development folds only, a new post-lockbox holdout after an approved data update, or a separate sandbox using copied historical rows?
- Decision type: Testing
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 86
- Draft recommendation before owner answer: Development folds only.
- Recommendation confidence: 82
- Evidence references: `docs/Data_Separation_And_Overfitting_Control.md`; `docs/Benchmark_Testing.md`; Stage 4 lockbox evidence; Stage 7A memo
- Owner answer: New post-lockbox holdout.
- Normalized decision: Stage 7 contextual-bandit evaluation should use a new post-lockbox holdout after an approved data update, rather than the current Stage 6 lockbox or a sandbox-only copied historical subset.
- Selected option: Option B: new post-lockbox holdout after approved data update.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7 used a separate post-Stage-6-lockbox diagnostic holdout after the later approved Twelve Data update. This answer still does not approve all-data final-execution training-output, live buy/sell signals, benchmark reruns, Stage 6 reinterpretation, or comparability promotion beyond the diagnostics-only Stage 7C scope.
- Affected downstream questions: S7B-DQ-003, S7B-DQ-004, S7B-DQ-009
- Notes: The current Stage 6 lockbox remains fixed historical reporting evidence and must not be reused for Stage 7 design iteration.

### S7B-DQ-003: What row filter should Stage 7 use?
- Original question: Should Stage 7 use all rows, news-days only with explicit non-comparability, or a two-track all-row plus news-days diagnostic?
- Decision type: Testing
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 78
- Draft recommendation before owner answer: Two-track diagnostic: all-row primary diagnostic plus news-days-only secondary non-comparable diagnostic.
- Recommendation confidence: 76
- Evidence references: Stage 7A memo; `ScopeDecisionLog.md` DQ-022; `docs/Benchmark_Testing.md`
- Owner answer: Two-track primary+secondary.
- Normalized decision: Stage 7 should use all eligible rows as the primary evaluation population and report news-days-only rows as a predeclared secondary diagnostic. The secondary news-days diagnostic must not replace or override the all-row primary evidence without a later explicit benchmark-family decision.
- Selected option: Two-track all-row primary plus news-days-only secondary diagnostic.
- Status: Answered
- Reason pending: not applicable
- Implications: Future Stage 7 artifacts should label primary all-row evidence separately from secondary news-days evidence. News-days-only outputs remain diagnostic and non-comparable to the Stage 6 all-row benchmark unless later explicitly redefined as a separate benchmark family.
- Affected downstream questions: S7B-DQ-004, S7B-DQ-005, S7B-DQ-009
- Notes: Dropping no-news rows as if comparable to Stage 6 remains forbidden without new benchmark-family approval.

### S7B-DQ-004: What time span should Stage 7 use?
- Original question: Should Stage 7 use a last-one-year sandbox, full clean-window replay, or development-only rolling replay?
- Decision type: Testing
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 76
- Draft recommendation before owner answer: Development-only rolling replay.
- Recommendation confidence: 78
- Evidence references: Stage 7A memo; Stage 4 split manifest; `docs/Data_Separation_And_Overfitting_Control.md`
- Owner answer: Confirmed development-only rolling replay for the Stage 7 benchmark/design pipeline, with learning-curve diagnostics and a separate later all-data final-execution-pipeline concept.
- Normalized decision: Stage 7 benchmark/design should use development-only rolling replay for protocol tuning and diagnostics, including learning curves before later periods. The current Stage 6 lockbox remains excluded from Stage 7 design iteration. A later frozen-protocol full-history replay may be used only as non-selection/training evidence, and a later `final_execution_pipeline` may train on all approved historical data for live-use predictions, but that final-execution mode is separate from the benchmark pipeline and cannot be used as claim-bearing accuracy evidence on the same rows it trained on.
- Selected option: Development-only rolling replay, expanded with learning-curve diagnostics and a separate future all-data final-execution-pipeline concept.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C should distinguish benchmark evidence from final-execution training. Benchmark evidence remains fold/replay/holdout based; final-execution all-data training, if later approved and implemented, is for live-use prediction generation after benchmark choices are frozen and does not prove accuracy by evaluating on its own training rows.
- Affected downstream questions: S7B-DQ-002, S7B-DQ-006, S7B-DQ-007
- Notes: The user's last-year learning-curve idea is accepted as a governed diagnostic when implemented through rolling development replay, not as lockbox-inclusive sandbox tuning. Full clean-window/full-history replay is acceptable only after protocol freeze and must be labeled separately from final holdout evidence.

### S7B-DQ-005: What action space should Stage 7 use?
- Original question: Should the policy choose one ticker per day, choose a top-k basket, choose a horizon-specific model/rank, or choose abstain/cash?
- Decision type: Data Model
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 74
- Draft recommendation before owner answer: Top-k equal-weight basket per fixed horizon.
- Recommendation confidence: 76
- Evidence references: Stage 7A memo; Stage 3 labels; Stage 5 predictions
- Owner answer: Top-k basket per horizon, with the model also learning the top-k worst decisions so the system can identify both best buy candidates and worst sell/avoid candidates.
- Normalized decision: Stage 7 action space should be two-sided top-k per fixed horizon. For each horizon, the policy should identify top-k best candidates and bottom-k worst/downside candidates from the eligible ticker universe. The bottom-k side is approved as a research/downside/avoid diagnostic at this stage; live sell, short, or trading-signal behavior remains unapproved until later output-status and final-execution decisions.
- Selected option: Custom expansion of top-k basket per fixed horizon: two-sided top-k best and bottom-k worst candidates per horizon.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C should define eligible tickers, k values for top and bottom selections, horizon handling, deterministic tie-breaking, and separate artifact labels for top-k upside candidates and bottom-k downside candidates before replay. `S7B-DQ-006` must decide whether the reward is top-k mean return, bottom-k avoidance accuracy, a two-sided spread, or separate metrics.
- Affected downstream questions: S7B-DQ-006, S7B-DQ-009, S7B-DQ-010
- Notes: Abstain/cash remains out of scope unless separately approved. Bottom-k downside candidates must not be presented as live sell recommendations until output status and final-execution pipeline rules explicitly allow that behavior.

### S7B-DQ-006: What reward should Stage 7 use?
- Original question: Should the reward be forward excess return by horizon, rank-normalized reward, sign hit, or cost-adjusted exploratory diagnostic only?
- Decision type: Data Model
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 84
- Draft recommendation before owner answer: Mean forward excess return of selected top-k basket by horizon.
- Recommendation confidence: 84
- Evidence references: `ScopeDecisionLog.md` DQ-003; Stage 3 label contract; Stage 7A memo
- Owner answer: Two-sided forward-return package.
- Normalized decision: Stage 7 reward should use a two-sided forward-return package by horizon: top-k mean forward excess return as the upside metric, bottom-k mean forward excess return as the downside metric where lower is better, and top-k mean minus bottom-k mean as a secondary separation metric. Supporting rank-normalized and sign-hit diagnostics may be added later, but cost-adjusted trading reward is not approved.
- Selected option: Two-sided forward-return package.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C must define delayed reward availability by horizon, prevent immediate updates from future labels, and label top-k, bottom-k, and spread metrics separately. The spread is a research separation metric unless later explicitly approved as an executable long-short or trading metric.
- Affected downstream questions: S7B-DQ-004, S7B-DQ-005, S7B-DQ-007
- Notes: Cost-adjusted rewards, transaction costs, shorting assumptions, and live buy/sell recommendations remain out of scope unless later approved through output-status and final-execution-pipeline decisions.

### S7B-DQ-007: What algorithm class should Stage 7 use?
- Original question: Should the first bandit algorithm be LinUCB, Thompson sampling, epsilon-greedy regression, or a non-bandit supervised ranking baseline?
- Decision type: Architecture
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 70
- Draft recommendation before owner answer: Epsilon-greedy regression as first bandit with supervised ranking as a mandatory baseline.
- Recommendation confidence: 68
- Evidence references: Stage 7A memo; `configs/models.yaml`; `docs/agent/AgentTemplates.md`
- Owner answer: Supervised then epsilon-greedy, with diagnostics on accuracy and overfitting of supervised training before jumping to epsilon-greedy so results and adaptive effects can be compared transparently.
- Normalized decision: Stage 7 algorithm flow should first run a supervised two-sided ranking phase under the same action and reward definitions, with explicit accuracy, fold, learning-curve, and overfitting diagnostics before adding adaptivity. The first adaptive contextual-bandit algorithm should then be epsilon-greedy regression/ranking, compared against the frozen supervised diagnostics to isolate the effect of exploration/adaptation.
- Selected option: Supervised ranking diagnostics first, then epsilon-greedy regression/ranking as first adaptive bandit.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C should define saved supervised diagnostics before adaptive replay, including fold-level top-k/bottom-k metrics, primary/secondary row-filter metrics, learning curves, train/validation gap diagnostics if Stage 7C generates fold-local train predictions, and deterministic seeds. Epsilon-greedy replay must use delayed rewards and must not claim real-policy IPW/DR evidence without logged actions and propensities.
- Affected downstream questions: S7B-DQ-006, S7B-DQ-008, S7B-DQ-009
- Notes: LinUCB and Thompson sampling remain credible future comparisons but add assumptions and tuning burden. The supervised-first step is a transparency gate, not a substitute for the contextual-bandit comparison.

### S7B-DQ-008: What context should Stage 7 use?
- Original question: Should context use Stage 3 features only, Stage 5 predictions as context, or combined feature and prediction context?
- Decision type: Data Model
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 72
- Draft recommendation before owner answer: Frozen combined Stage 3 features plus Stage 5 predictions, with predictions-only ablation.
- Recommendation confidence: 72
- Evidence references: Stage 3 feature artifact; Stage 5 saved prediction artifact; Stage 7A memo; `configs/models.yaml`
- Owner answer: Combined Stage 3 + Stage 5.
- Normalized decision: Stage 7 context should combine frozen Stage 3 features with fold-safe Stage 5 predictions. A predictions-only ablation is required to test whether policy gains come from saved supervised predictions alone. A Stage 3 features-only diagnostic is recommended if implementation budget allows. Raw news text, LLM summaries, holdings, portfolio state, and live execution features remain out of scope unless separately approved.
- Selected option: Combined frozen Stage 3 features plus Stage 5 predictions, with predictions-only ablation.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C must define exact context columns, fold-time availability checks, context schema validation, prediction provenance requirements, and final-execution schema compatibility before implementation.
- Affected downstream questions: S7B-DQ-007, S7B-DQ-009
- Notes: Raw news text and LLM-derived context are not approved by this decision and would require separate scope/design approval.

### S7B-DQ-009: What baselines are mandatory?
- Original question: Which baselines must exist before any bandit-value claim: market-only policy, event-state supervised ranker, random policy, no-news abstain policy, or others?
- Decision type: Testing
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 80
- Draft recommendation before owner answer: Require random, epsilon-random, market-only ranking, Stage 5 supervised ranking, static validation rule, and abstain baseline if abstain is approved.
- Recommendation confidence: 84
- Evidence references: Stage 7A memo; `configs/models.yaml`; `docs/Benchmark_Testing.md`
- Owner answer: Full baseline bundle.
- Normalized decision: Stage 7 must require the full baseline bundle before any bandit-value claim: random top-k/bottom-k, epsilon-random, market-only ranker, Stage 5 predictions-only supervised ranker, combined Stage 3 plus Stage 5 supervised ranker, and a static validation-selected rule applied unchanged. Baselines should report top-k, bottom-k, spread, all-row primary, news-days secondary, fold/learning-curve, and supervised overfitting diagnostics where available. Abstain/cash and trading-cost baselines are not included unless later approved.
- Selected option: Full baseline bundle.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C must define and save baseline diagnostics before any contextual-bandit value claim. The epsilon-greedy policy must be compared against both supervised and exploration-control baselines, not merely random selection.
- Affected downstream questions: S7B-DQ-005, S7B-DQ-007, S7B-DQ-010
- Notes: Because abstain/cash is not approved in the action space, no-news abstain/cash baselines remain out of scope for the first Stage 7 bundle.

### S7B-DQ-010: What output status should Stage 7 produce?
- Original question: Should Stage 7 output a research artifact only, saved policy diagnostics, future executable Stage 7C docs, or no trading signal?
- Decision type: Observability
- Blocking status: Resolved for Stage 7C diagnostics; future approvals remain required for final-execution/live-use changes
- Priority score: 68
- Draft recommendation before owner answer: Saved policy diagnostics only; no trading signal.
- Recommendation confidence: 78
- Evidence references: `ProjectDefinition.md`; `UsageManual.md`; Stage 7A memo; Stage 7B draft memo
- Owner answer: Diagnostics + docs + stub.
- Normalized decision: Stage 7 should produce saved benchmark diagnostics plus Stage 7C protocol documentation plus a separate final-execution-pipeline design stub. The benchmark outputs should include saved policy diagnostics for supervised ranking, epsilon-greedy, and mandatory baselines. The final-execution stub may describe a later all-data live-use training mode after benchmark choices are frozen, but it is not an implementation approval and its outputs are not benchmark evidence. Live buy/sell, shorting, trading-signal, and cost-adjusted execution outputs remain unapproved.
- Selected option: Diagnostics + Stage 7C docs + final-execution design stub.
- Status: Answered
- Reason pending: not applicable
- Implications: Stage 7C may be drafted as implementation-ready protocol documentation, but code execution, policy training, data updates, and final-execution-pipeline implementation still require explicit future approval. Output artifacts must clearly label benchmark evidence separately from future final-execution outputs.
- Affected downstream questions: S7B-DQ-001, S7B-DQ-009
- Notes: Product/API/dashboard/live inference outputs remain out of scope under current phase-1 boundaries unless separately approved. Bottom-k outputs remain downside/avoid diagnostics, not live sell recommendations.

## 3. Detailed Entries

### DQ-004: What horizon set is in scope for the first serious benchmark?
- Original question: What horizon set is in scope for the first serious benchmark: `1/5/20`, `1/5/20/60`, or a smaller subset?
- Decision type: Data Model
- Blocking status: Important
- Priority score: 64
- Recommended current default: Option A: freeze `1d`, `5d`, and `20d` as the core phase-1 horizons.
- Recommendation confidence: 72
- Evidence references: `src/features/labels.py`; `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md`
- Owner answer (verbatim): custom: 1d 5d 10d 20d 60d (adapt this phrasing accordingly)
- Normalized decision: The first serious benchmark will use a custom multi-horizon set of `1d`, `5d`, `10d`, `20d`, and `60d`.
- Selected option: Custom
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Phase 1 will use a broader horizon family than the repo's default core set, adding `10d` and keeping `60d` in scope from the start. This increases overlap-control, reporting, and loss-balancing burden, but preserves a more graduated short-to-medium-to-long horizon picture.
- Affected downstream questions: DQ-012, DQ-015, DQ-024
- Notes: Custom choice narrows away from a very dense horizon grid while still expanding beyond the repo's default `1/5/20` core.

### DQ-024: What thesis outcome classes are acceptable success conditions for phase 1?
- Original question: What thesis outcome classes are acceptable success conditions for phase 1?
- Decision type: Delivery
- Blocking status: Important
- Priority score: 56
- Recommended current default: Option A: accept robust positive, conditional positive, or clean null results as phase-1 thesis success classes.
- Recommendation confidence: 83
- Evidence references: `foundational_deep_research.md`; `restarting_research.md`; `restarting_research_literature_expansion.md`
- Owner answer (verbatim): Option A
- Normalized decision: Phase 1 will count robust positive, conditional positive, or clean null results as acceptable success outcomes.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The project is benchmark-first rather than â€œmust-win.â€ This lowers pressure to overfit, metric-shop, or force a positive multimodal result and keeps the phase-1 program scientifically honest.
- Affected downstream questions: DQ-015, DQ-019
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-014: Should static company metadata or KB features enter phase 1, or stay as a phase-2 extension?
- Original question: Should static company metadata or KB features enter phase 1, or stay as a phase-2 extension?
- Decision type: Data Model
- Blocking status: Important
- Priority score: 52
- Recommended current default: Option A: keep static company metadata out of phase 1 and treat it as a phase-2 extension.
- Recommendation confidence: 70
- Evidence references: `architecture_overview.md`; snapshot `data/kb/` presence; `multimodal_models.py`; `research_comparison_addendum_extension_branches.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- Owner answer (verbatim): Option A
- Normalized decision: Static company metadata and KB features will stay out of phase 1 and remain a phase-2 extension.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The first serious benchmark stays focused on market features plus event-state only. Static company context remains a later clean extension rather than part of the default phase-1 panel.
- Affected downstream questions: DQ-019
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-019: What deployment, API, UX, permission, and security boundary is actually in scope for phase 1?
- Original question: What deployment, API, UX, permission, and security boundary is actually in scope for phase 1?
- Decision type: Infra
- Blocking status: Important
- Priority score: 51
- Recommended current default: Option A: keep phase 1 as a local CLI- and artifact-driven research system only.
- Recommendation confidence: 76
- Evidence references: root directory listing; legacy snapshot structure; `architecture_overview.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- Owner answer (verbatim): Option A
- Normalized decision: Phase 1 will remain a local CLI/artifact-driven research system only, with no user-facing service, API, dashboard, or broader product-style permission boundary.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Phase 1 stays focused on reproducible research execution rather than service/product infrastructure. API/auth/role-management and broader UX scope remain out of phase 1 unless revisited later.
- Affected downstream questions:
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-015: Are uncertainty-aware outputs in scope for phase 1, a later extension, or a primary objective shift?
- Original question: Are uncertainty-aware outputs in scope for phase 1, a later extension, or a primary objective shift?
- Decision type: Testing
- Blocking status: Nice-to-have
- Priority score: 53
- Recommended current default: Option A: keep uncertainty-aware outputs as a later extension only.
- Recommendation confidence: 78
- Evidence references: `implementation_roadmap.md`; `research_comparison_addendum_extension_branches.md`; `P10`; `P14`; `P17`; `P19`; `P20`
- Owner answer (verbatim): Option A
- Normalized decision: Uncertainty-aware outputs are out of phase 1 and will be treated as a later extension after the deterministic benchmark is stable.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Phase 1 remains focused on deterministic excess-return benchmarking. Calibration, probabilistic scoring, and uncertainty output design stay deferred until the core benchmark is established.
- Affected downstream questions: DQ-014, DQ-019
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-001: Should the active project resume as a greenfield rebuild with selective legacy salvage, reactivate the archived snapshot as the active baseline, or ignore the snapshot and start from zero?
- Original question: Should the active project resume as a greenfield rebuild with selective legacy salvage, reactivate the archived snapshot as the active baseline, or ignore the snapshot and start from zero?
- Decision type: Architecture
- Blocking status: Blocking
- Priority score: 84
- Recommended current default: Option A: rebuild at the active root and salvage legacy code or ideas only deliberately.
- Recommendation confidence: 82
- Evidence references: `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`; `DEPRECATION_MANIFEST.txt`; `architecture_overview.md`
- Owner answer (verbatim): custom: Rebuild in active root, selectively salvage legacy code/ideas, but only after the research truth is finalized.
- Normalized decision: The active project will rebuild in the active root with selective salvage from the archived snapshot, but salvage and implementation should begin only after research truth and scope are finalized.
- Selected option: Custom (Option A with sequencing constraint)
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The archived snapshot remains reference/salvage material rather than the active baseline. Truth-finalization decisions now explicitly precede implementation reuse.
- Affected downstream questions: DQ-002, DQ-003, DQ-012, DQ-017, DQ-020
- Notes: Custom answer narrows Option A by adding a sequencing rule: finalize research truth first, then salvage deliberately.

### DQ-002: What is the canonical phase-1 project objective: a narrow test of event-state incremental value over market-only baselines, a broader multimodal forecasting platform, or an architecture-comparison program?
- Original question: What is the canonical phase-1 project objective: a narrow test of event-state incremental value over market-only baselines, a broader multimodal forecasting platform, or an architecture-comparison program?
- Decision type: Product Scope
- Blocking status: Blocking
- Priority score: 82
- Recommended current default: Option A: narrow phase-1 scope to the event-state-versus-market-only thesis question.
- Recommendation confidence: 85
- Evidence references: `foundational_deep_research.md`; `restarting_research*.md`; `research_comparison.md`; `Current_State.md`
- Owner answer (verbatim): Option A.
- Normalized decision: Phase 1 is scoped to the narrow thesis question of whether event-state features add incremental value over market-only baselines.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Broad platform-building and architecture-comparison programs are not the phase-1 objective. Downstream decisions should be optimized for a single clean incremental-value benchmark.
- Affected downstream questions: DQ-003, DQ-004, DQ-007, DQ-008, DQ-009, DQ-010, DQ-011, DQ-014, DQ-015, DQ-016, DQ-019, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-003: Which target family should define the first serious benchmark: forward excess returns, raw forward returns, or factor-neutral residual returns?
- Original question: Which target family should define the first serious benchmark: forward excess returns, raw forward returns, or factor-neutral residual returns?
- Decision type: Data Model
- Blocking status: Blocking
- Priority score: 81
- Recommended current default: Option A: use forward excess returns as the primary target family.
- Recommendation confidence: 80
- Evidence references: `RESEARCH_DESIGN_old.md`; `src/features/labels.py`; `research_comparison_addendum_targets.md`; `foundational_deep_research.md`; `P09_common_risk_factors_in_the_returns_on_stocks_and_bonds.md`
- Owner answer (verbatim): Option A.
- Normalized decision: The first serious benchmark will use forward excess returns as the canonical primary target family.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The benchmark will be framed around incremental value beyond broad market drift rather than raw-return prediction or immediate factor-neutral residualization. Factor-neutral residual targets remain valid later extensions, not the initial core target.
- Affected downstream questions: DQ-004, DQ-007, DQ-008, DQ-011, DQ-012, DQ-013, DQ-021, DQ-023
- Notes: Clarified during review that Option C referred to a different target-definition family, not a different training-window schedule.

### DQ-005: Which news-alignment policy should be canonical for future work?
- Original question: Which news-alignment policy should be canonical for future work: the implemented as-of-close same-day rule, the older embargo-style delay rule, or two explicitly separate benchmark families?
- Decision type: Workflow
- Blocking status: Blocking
- Priority score: 88
- Recommended current default: Option A: canonicalize the implemented as-of-close same-day rule.
- Recommendation confidence: 78
- Evidence references: `evaluation_protocol.md`; `src/split/alignment_rules.py`; `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`
- Owner answer (verbatim): Option A.
- Normalized decision: The canonical alignment policy for future work is the implemented same-day as-of-close rule, with after-hours and non-trading-day articles rolling forward.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Future benchmark design should treat same-day as-of-close alignment as active truth unless explicitly revised later. Older embargo-style examples remain historical contradictions, not active benchmark defaults.
- Affected downstream questions: DQ-006, DQ-012, DQ-021, DQ-022, DQ-023
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-006: What exact benchmark family must be frozen before serious implementation resumes?
- Original question: What exact benchmark family must be frozen before serious implementation resumes?
- Decision type: Testing
- Blocking status: Blocking
- Priority score: 86
- Recommended current default: Option A: freeze one narrow serious benchmark family before coding or reruns.
- Recommendation confidence: 84
- Evidence references: `foundational_deep_research.md`; `restarting_research.md`; `evaluation_protocol.md`; `AgentRules.md`; `AgentGlossary.md`
- Owner answer (verbatim): Option A.
- Normalized decision: The project will freeze one narrow serious benchmark family before further serious implementation or reruns rather than keeping multiple benchmark families open or delaying the freeze.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Downstream decisions should now converge toward one claim-bearing benchmark packet rather than preserving parallel benchmark families. Later benchmark changes should be treated as comparability-affecting changes rather than normal iteration.
- Affected downstream questions: DQ-001, DQ-002, DQ-003, DQ-004, DQ-007, DQ-008, DQ-009, DQ-011, DQ-012, DQ-013, DQ-017, DQ-021, DQ-022, DQ-023
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-012: What final evaluation protocol should govern serious claims: purged-plus-embargoed walk-forward plus a lockbox, simpler walk-forward only, or something lighter?
- Original question: What final evaluation protocol should govern serious claims: purged-plus-embargoed walk-forward plus a lockbox, simpler walk-forward only, or something lighter?
- Decision type: Testing
- Blocking status: Blocking
- Priority score: 84
- Recommended current default: Option A: use purged-plus-embargoed walk-forward for model development and add a final untouched lockbox for reporting.
- Recommendation confidence: 78
- Evidence references: `evaluation_protocol.md`; `purged_embargo_splits.py`; `research_comparison_addendum_evaluation.md`; `foundational_deep_research.md`; `restarting_research.md`
- Owner answer (verbatim): Option A.
- Normalized decision: Serious claims will use purged-plus-embargoed walk-forward evaluation for development and a final untouched lockbox for reporting.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Lighter evaluation protocols may still be used for plumbing or exploratory checks, but not for serious benchmark claims. Future result interpretation should assume the stronger leakage-control standard.
- Affected downstream questions: DQ-004, DQ-007, DQ-011, DQ-013, DQ-017, DQ-018, DQ-021, DQ-023
- Notes: Owner chose the explicit option rather than invoking `use default`. 2026-05-07 Option B refinement preserves this selected protocol while adding the contract in `docs/Data_Separation_And_Overfitting_Control.md` for split manifests, train/validation/lockbox separation, fold-local preprocessing, saved out-of-sample predictions, and overfitting diagnostics.

### DQ-017: Which active theory/design documents must be recreated at the root before coding begins?
- Original question: Which active theory/design documents must be recreated at the root before coding begins?
- Decision type: Delivery
- Blocking status: Blocking
- Priority score: 80
- Recommended current default: Option A: recreate active theory/design documents before coding begins.
- Recommendation confidence: 82
- Evidence references: `AgentRules.md`; root directory listing; `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`
- Owner answer (verbatim): Option A.
- Normalized decision: Active theory/design documents must be recreated at the root before coding begins.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Archived design documents remain reference material rather than active authority. New implementation work should wait until the active documentation layer is re-established.
- Affected downstream questions: DQ-018, DQ-020, DQ-023
- Notes: This is consistent with the earlier custom sequencing decision in DQ-001.

### DQ-018: What verification and observability bar is required before the project can claim meaningful active progress?
- Original question: What verification and observability bar is required before the project can claim meaningful active progress?
- Decision type: Observability
- Blocking status: Important
- Priority score: 74
- Recommended current default: Option A: require rerun-capable tests, manual provider checks, structured run summaries, and CI-ready validation before major claims.
- Recommendation confidence: 72
- Evidence references: `AgentRules.md`; `AgentMemory.md`; `implementation_roadmap.md`; `tests/results/Expanded_Testing_20260319T121411Z.md`; smoke artifact summaries
- Owner answer (verbatim): Option A.
- Normalized decision: Meaningful active progress requires a strong evidence bar including rerun-capable tests, manual provider checks, structured run summaries, and CI-ready validation before major claims.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Ad hoc or archived evidence is insufficient for major active claims. Future milestones should be backed by reproducible validation artifacts rather than informal confidence.
- Affected downstream questions: DQ-021, DQ-023, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`. 2026-05-07 Option B refinement adds contamination blockers, preprocessing-fit boundary checks, and an overfitting diagnostic report to the evidence bar.

### DQ-021: What historical date range should define the first serious benchmark family?
- Original question: What historical date range should define the first serious benchmark family?
- Decision type: Data Model
- Blocking status: Important
- Priority score: 73
- Recommended current default: Option A: freeze a shorter overlapping clean window based on what can be verified now.
- Recommendation confidence: 68
- Evidence references: `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md`; `implementation_roadmap.md`; `testing_commands.md`
- Owner answer (verbatim): Option A.
- Normalized decision: The first serious benchmark family will use a shorter overlapping clean historical window based on what can be verified confidently now.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The first benchmark prioritizes verified coverage quality over maximum historical span. Longer-window ambitions remain possible later, but only as a new verified benchmark-family choice.
- Affected downstream questions: DQ-007, DQ-008, DQ-011, DQ-022, DQ-023
- Notes: During clarification, Option C was explicitly ruled out by the owner. Option B remained credible but was not selected because the owner prioritized the more trustworthy first benchmark window. 2026-05-07 Option B validation refinement does not change the shorter clean-window decision; it requires clean-window choice to remain separate from lockbox inspection and metric shopping.

### DQ-008: Which external data stack is in scope for phase 1: legacy provider set only, legacy providers plus factor-library support, or a broader multi-provider expansion now?
- Original question: Which external data stack is in scope for phase 1: legacy provider set only, legacy providers plus factor-library support, or a broader multi-provider expansion now?
- Decision type: Integration
- Blocking status: Important
- Priority score: 71
- Recommended current default: Option A: Phase 1 uses Twelve Data, Finnhub, and SEC only.
- Recommendation confidence: 74
- Evidence references: `RESEARCH_DESIGN_old.md`; `architecture_overview.md`; `implementation_roadmap.md`; `S01_purge_embargo_validation_source_note.md`; `P09_common_risk_factors_in_the_returns_on_stocks_and_bonds.md`
- Owner answer (verbatim): Custom: Twelve Data for financial database (OHLCV) + AlphaVantage for financial news + SEC, only.
- Normalized decision: Phase 1 will use Twelve Data for OHLCV, AlphaVantage for financial news, and SEC for static/company support; broader provider expansion remains out of scope.
- Selected option: Custom
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The provider stack is now intentionally narrower than broad multi-provider expansion but diverges from the strongest historical repository evidence on the news provider choice. Provider-reality verification remains mandatory before serious benchmark claims.
- Affected downstream questions: DQ-007, DQ-011, DQ-018, DQ-022, DQ-023
- Notes: Custom decision replaces Finnhub with AlphaVantage for the phase-1 news source while preserving Twelve Data and SEC.

### DQ-011: What benchmark model ladder is mandatory before any higher-complexity branch is considered?
- Original question: What benchmark model ladder is mandatory before any higher-complexity branch is considered?
- Decision type: Testing
- Blocking status: Important
- Priority score: 71
- Recommended current default: Option A: require linear baselines, a market-only MLP, and one simple multimodal model.
- Recommendation confidence: 74
- Evidence references: `implementation_roadmap.md`; `architecture_overview.md`; `baseline_models.py`; `multimodal_models.py`; `research_comparison_addendum_models.md`; `foundational_deep_research.md`
- Owner answer (verbatim): Option C.
- Normalized decision: The mandatory benchmark ladder will expand beyond the minimum default and include broader serious comparator families before accepting higher-complexity conclusions.
- Selected option: Option C
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Phase 1 will put stronger pressure on multimodal claims and may improve eventual best-model quality, but it increases comparator burden, compute burden, and benchmark-management complexity relative to the default path.
- Affected downstream questions: DQ-009, DQ-010, DQ-013, DQ-016, DQ-023, DQ-024
- Notes: Owner preferred broader comparator pressure now over the repo's narrower default ladder. This likely brings tree-based and possibly additional serious comparator families into earlier scope.

### DQ-022: What is the official no-news-day policy for the event-state branch?
- Original question: What is the official no-news-day policy for the event-state branch?
- Decision type: Workflow
- Blocking status: Important
- Priority score: 71
- Recommended current default: Option A: keep the row and encode an explicit empty event state with no-news indicators.
- Recommendation confidence: 75
- Evidence references: `src/features/event_state.py`; `restarting_research.md`; `research_comparison_addendum_event_representations.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- Owner answer (verbatim): Option A.
- Normalized decision: No-news days will remain in the benchmark row universe and will be encoded as explicit empty event states with no-news indicators.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The multimodal benchmark keeps row-universe consistency with market-only baselines and treats lack of news as explicit state rather than dropped data or masked absence.
- Affected downstream questions: DQ-009, DQ-010, DQ-013, DQ-023
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-007: What universe should define the first serious benchmark?
- Original question: What universe should define the first serious benchmark: a fixed medium liquid large-cap subset, the full large-cap universe, or only a tiny pilot subset?
- Decision type: Data Model
- Blocking status: Important
- Priority score: 69
- Recommended current default: Option A: freeze a medium liquid large-cap subset around 50 names with explicit rules.
- Recommendation confidence: 70
- Evidence references: `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md`; smoke training summaries; `deep-research-report (5).md`
- Owner answer (verbatim): yes log custom.
- Normalized decision: Freeze the first serious benchmark on a reproducible top-50 liquid large-cap universe. Any later expansion to 100 or 500 tickers must be treated as a separate benchmark family with new coverage and provider validation rather than a silent extension of the original benchmark.
- Selected option: Custom
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The first serious benchmark keeps a controlled, coverage-friendly universe aligned with earlier repository design, while preserving a formal scaling path later. Comparability to later 100/500-scale experiments must not be assumed automatically.
- Affected downstream questions: DQ-013, DQ-016, DQ-019, DQ-023
- Notes: Custom decision operationalizes the repo's earlier 50-name large-cap guidance while adding a staged scaling methodology.

### DQ-013: What should count as primary success metrics, and should ranking stay secondary or become co-primary?
- Original question: What should count as primary success metrics, and should ranking stay secondary or become co-primary?
- Decision type: Testing
- Blocking status: Important
- Priority score: 69
- Recommended current default: Option A: keep regression metrics primary and ranking metrics secondary but mandatory.
- Recommendation confidence: 72
- Evidence references: `evaluation_protocol.md`; `RESEARCH_DESIGN_old.md`; `research_comparison_addendum_targets.md`; `research_comparison_addendum_evaluation.md`; `P05`; `P08`; `P10`
- Owner answer (verbatim): Option A
- Normalized decision: Primary success metrics will remain regression-first, while ranking metrics will be mandatory secondary diagnostics rather than co-primary or primary.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The benchmark will remain centered on excess-return prediction quality, while still preserving ranking as an important practical and cross-sectional secondary view. Future scaling to larger universes may strengthen the relevance of ranking analysis, but not as the main phase-1 objective.
- Affected downstream questions: DQ-009, DQ-010, DQ-016, DQ-023, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`. 2026-05-07 Option B refinement requires metric lists to be frozen before serious runs and computed only from saved out-of-sample predictions and frozen labels.

### DQ-020: How should active truth, archived truth, contradictions, and stale research be governed once new implementation work restarts?
- Original question: How should active truth, archived truth, contradictions, and stale research be governed once new implementation work restarts?
- Decision type: Other
- Blocking status: Important
- Priority score: 68
- Recommended current default: Option A: keep the archive reference-only and explicitly triage any reused ideas into new active-root theory/design docs.
- Recommendation confidence: 78
- Evidence references: `AgentRules.md`; `AgentAppendices.md`; `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`; `docs/research_results/bkup/*.md`; contradictory research/log files
- Owner answer (verbatim): Option A
- Normalized decision: The archive remains reference-only. Any reused ideas, designs, or assumptions must be explicitly absorbed into new active-root theory/design documents before they become active truth.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Archived materials can guide salvage and reconstruction, but they cannot silently define current truth. Contradictions and stale research remain visible until explicitly resolved in active-root documentation.
- Affected downstream questions: DQ-016, DQ-019, DQ-023, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-016: Which branches should be explicitly out of scope until the core benchmark is stable?
- Original question: Which branches should be explicitly out of scope until the core benchmark is stable?
- Decision type: Product Scope
- Blocking status: Important
- Priority score: 68
- Recommended current default: Option A: explicitly defer the high-risk branches until the core benchmark is stable.
- Recommendation confidence: 82
- Evidence references: `foundational_deep_research.md`; `restarting_research*.md`; `research_comparison_addendum_extension_branches.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- Owner answer (verbatim): Option A
- Normalized decision: High-risk branches such as dynamic profiles, graph-heavy cores, MoE, end-to-end text fine-tuning, broad derivative grids, and full live-universe first-pass benchmarking are explicitly out of scope until the core benchmark is stable.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Phase 1 stays focused on the chosen benchmark family despite the broader comparator ladder. Risky architectural and product-scope expansions are deferred rather than left ambiguous.
- Affected downstream questions: DQ-009, DQ-010, DQ-014, DQ-015, DQ-019, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-009: What event-representation family should be the active default?
- Original question: What event-representation family should be the active default: pooled dense embeddings plus scalar enrichments, pooled dense embeddings only, or sentiment-only text features as the main representation?
- Decision type: Architecture
- Blocking status: Important
- Priority score: 67
- Recommended current default: Option A: use pooled dense embeddings and include scalar enrichments as the default event-state package.
- Recommendation confidence: 66
- Evidence references: `src/features/event_state.py`; `research_comparison_addendum_event_representations.md`; `research_comparison_addendum_features.md`; paper notes `P01`, `P15`, `P16`
- Owner answer (verbatim): Option A
- Normalized decision: The default event-state representation will use pooled dense embeddings plus scalar enrichments.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The text branch will be modeled as a richer event-state package rather than embeddings-only or sentiment-only text. This keeps the benchmark aligned with the repository's core event-state framing while preserving later ablations inside the same family.
- Affected downstream questions: DQ-010, DQ-023, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-010: Which multimodal fusion family should be the phase-1 default?
- Original question: Which multimodal fusion family should be the phase-1 default: simple gated fusion, late fusion, or residual fusion?
- Decision type: Architecture
- Blocking status: Important
- Priority score: 65
- Recommended current default: Option A: keep simple gated fusion as the phase-1 default.
- Recommendation confidence: 60
- Evidence references: `src/models/multimodal_models.py`; `architecture_overview.md`; `research_comparison_addendum_models.md`; `research_comparison.md`
- Owner answer (verbatim): Option A
- Normalized decision: The phase-1 multimodal default will use simple gated fusion.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: The first serious multimodal benchmark will use a flexible but still lightweight fusion path closely aligned with archived implementation evidence. Late and residual fusion remain later ablation or comparison families rather than the initial default.
- Affected downstream questions: DQ-023, DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`.

### DQ-023: What exact run-artifact packet must every serious benchmark emit?
- Original question: What exact run-artifact packet must every serious benchmark emit?
- Decision type: Observability
- Blocking status: Important
- Priority score: 65
- Recommended current default: Option A: require dataset version, manifest, resolved config, fold definitions, saved predictions, metrics, and comparison summary for every serious run.
- Recommendation confidence: 77
- Evidence references: `AgentRules.md`; `AgentMemory.md`; `architecture_overview.md`; `data_layout.md`; `evaluation_protocol.md`
- Owner answer (verbatim): Option A
- Normalized decision: Every serious benchmark run must emit a reproducible artifact packet including dataset version, manifest, resolved config, fold definitions, saved predictions, metrics, and a comparison summary.
- Selected option: Option A
- Status: Answered
- Reason if deferred/skipped/superseded:
- Implications: Serious runs will be auditable and benchmark-comparable by construction. Lightweight prediction-only runs may still exist for informal checks, but they will not count as serious benchmark evidence.
- Affected downstream questions: DQ-024
- Notes: Owner chose the explicit option rather than invoking `use default`. 2026-05-07 Option B refinement expands the serious-run packet contract to include split manifest row accounting, preprocessing-fit manifest, saved out-of-sample prediction keys, and an overfitting diagnostic report.

## 4. Deferred Items

### Stage 7B Pending/Unanswered Draft Items

None. Stage 7B decision collection is complete.

## 5. Skipped Or Superseded Items
None.

## 6. Final Completion Summary
- Original phase-1 interview complete.
- Total questions handled: 34
- Answered: 34
- Default accepted: 0
- Deferred: 0
- Skipped: 0
- Superseded: 0
- Top deferred items: none
- Major unresolved risks:
  - Several custom choices diverge from the repository's historical defaults and will require fresh active-root documentation before implementation, especially the provider stack (`AlphaVantage` news), the broader comparator ladder, and the custom horizon set (`1d`, `5d`, `10d`, `20d`, `60d`).
  - Later benchmark-family expansions, especially universe growth beyond the top-50 benchmark, must be treated as new benchmark families rather than directly comparable continuations.
  - Provider-reality and coverage verification remain mandatory before any serious benchmark claim despite the completed decision log.
  - The 2026-05-07 Option B refinement is documentation-contract work only until executable leakage, split, artifact, metric, and overfitting-diagnostic tests exist.
