# Stage 10B Update-To-Prediction Decision Matrix

Status: executed 2026-05-23 as a decision-comparison and approval-capture stage. `S10B-DQ-001` through `S10B-DQ-010` are now answered in `ScopeDecisionLog.md`. This memo does not implement code, call providers, mutate raw data, create prediction-output artifacts, create visualization artifacts, expose a service/API/dashboard, create trading signals, reinterpret Stage 6, or promote benchmark comparability.

## 1. Governing Boundary

Stage 10B follows `AgentRules.md`, `docs/agent/AgentTemplates.md`, `Stage10BPrompt.md`, `Stage10APrompt.md`, `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`, `Stage8Prompt.md`, `ExecutionPipeline.md`, `UsageManual.md`, `docs/Data_Update_Strategy.md`, `ScopeDecisionLog.md`, and `ResearchTruth.md`.

Preserved constraints:

| Area | Constraint preserved |
| --- | --- |
| Target | Forward excess returns only. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | Approved top-50 liquid large-cap benchmark family unless separately approved. |
| Providers | Alpha Vantage news, Twelve Data OHLCV, SEC static/company support only. |
| Alignment | Same-day as-of-close. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox for serious claims. |
| Stage 6 result | `clean_null` with `limitation_bearing` comparability. |
| Stage 8 boundary | Plan-first raw update scripts; no live provider calls or raw overwrites without explicit approval. |
| Deployment boundary | Local CLI/artifact-driven research only; no user-facing service/API/dashboard. |

## 2. Scoring Method

Scoring scale: `0` to `10`. Higher is better for every scored category.

Mandatory categories from `AgentRules.md`:

| Category | Meaning |
| --- | --- |
| Accuracy | Fit with scientifically faithful prediction/reporting behavior. |
| Complexity | Higher means lower implementation and conceptual burden. |
| Compute Intensity | Higher means lighter compute and operational burden. |
| Security | Lower exposure to credentials, raw ledgers, network calls, and service surfaces. |
| Compatibility | Alignment with approved scope, artifacts, configs, and benchmark boundaries. |
| Governance | Auditability, approval safety, and preservation of non-claims. |

Context-specific scored categories used in every matrix:

| Category | Meaning |
| --- | --- |
| Correctness | Fit with current artifact contracts and data availability. |
| Leakage/comparability safety | Higher means lower leakage, lockbox, or benchmark-comparability risk. |
| Usability | Ease for the user to run, inspect, and archive locally. |
| Maintenance cost | Higher means lower ongoing code/test/doc burden. |

Known evidence limits:

| Limit | Consequence |
| --- | --- |
| Persisted fitted-model serving is not evidenced in repository materials. | True fresh feature-only forecast scoring requires a new approved design before implementation. |
| A single approved full-pipeline command is not evidenced in repository materials. | Stage 10C should not pretend an end-to-end orchestrator already exists. |
| Current Stage 5 saved predictions are validation/lockbox split artifacts only. | Saved-prediction extraction can create historical out-of-sample packets, not arbitrary future-row forecasts. |
| Visualization artifacts are not evidenced in repository materials. | Any report/HTML/image generation requires new tests and explicit approval. |

## 3. Decision Coverage Map

| Stage 10B prompt topic | Covered by decision ID |
| --- | --- |
| Orchestration | `S10B-DQ-002` |
| Data refresh | `S10B-DQ-002` |
| Prediction method | `S10B-DQ-003`, `S10B-DQ-004` |
| Output folder | `S10B-DQ-004` |
| Output files | `S10B-DQ-005` |
| Visualization technology | `S10B-DQ-005` |
| Top-10 rule | `S10B-DQ-006` |
| News relevance | `S10B-DQ-007` |
| Trajectory graph | `S10B-DQ-008` |
| Claim wording | `S10B-DQ-001` |
| Validation bar | `S10B-DQ-009` |
| Sensitive artifacts | `S10B-DQ-010` |

## 4. Recommended Bundle

Resolved Stage 10C design bundle from the owner-approved Stage 10B decisions:

| Area | Recommended choice |
| --- | --- |
| Purpose | Local model-output / forecast-candidate artifact packet only, explicitly not trading advice, not a benchmark result, and not a Stage 6 reinterpretation. |
| Orchestration and refresh | Single local artifact-generation CLI consuming explicit artifact roots and data cutoffs; no scheduled job, live provider calls, raw overwrites, hidden Stage 2-6 reruns, service/API/dashboard, or Stage 6 reinterpretation. |
| Generation mode | Start with Stage 5 saved-prediction extraction and remain compatible with future approved Stage 2-6 rebuild outputs; no persisted inference package for the first implementation path. |
| Model scope | Use `event_state_gated_fusion` as the event-state view plus selected market hurdle comparison by horizon; preserve full model metadata. |
| Forecast row role | Use governed `data/prediction_outputs/phase1_top50/...` packets separate from Stage 6 evidence; reserve `forecast_candidate` for explicitly approved future-row semantics and use `historical_prediction` or `diagnostic_only` where appropriate. |
| Output folder and files | Use `data/prediction_outputs/phase1_top50/<run_date>__cutoff_<data_cutoff>__src_<digest>__rows_<digest>__stage5_<digest>__prediction_outputs_v1/` with JSON manifest, Parquet/CSV tables, limitations file, and optional static HTML. |
| Visualization | Static HTML plus CSV/Parquet packet with manifest, limitations metadata, and offline report; optional PNGs only as derived exports; notebooks development-only; no dashboard. |
| Top-10 | Per-horizon event-state score as primary, per-horizon delta over market hurdle as secondary reporting, and combined cross-horizon score only as a third-priority diagnostic with caveats and a final non-claim joint summary. |
| News | Deterministic aligned-news fields and limitation flags required; deterministic snippets optional only if validated; no LLM summaries for the first implementation. |
| Trajectory | Historical price/return context plus separate forecast markers as primary; optional historical predictions plus realized labels where elapsed; no projected price path or fan chart. |
| Validation and security | Full packet/report validation with fail-closed behavior is required; packets exclude raw API-key-bearing ledgers, raw provider secrets, unsanitized request URLs, raw request ledgers, API keys, and unsanitized provider logs. |

## 5. Decision Matrices

### S10B-DQ-001: Output Purpose And Claim Wording

Question: What should Stage 10C outputs be allowed to claim?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Local forecast-candidate artifact | Dated local artifact packet with `not_trading_advice` and `not_benchmark_result` wording. | 8 | 7 | 8 | 9 | 9 | 9 | 8 | 9 | 8 | 7 | Existing local artifacts plus new report/packet code if approved. | Yes |
| B. Research diagnostic only | Historical diagnostic packet from validation/lockbox saved predictions, not a future forecast. | 7 | 9 | 9 | 10 | 10 | 10 | 9 | 10 | 6 | 9 | Existing Stage 5/6 artifacts. | No |
| C. No Stage 10C output | Keep Stage 10A/10B documentation only and do not create prediction/report artifacts. | 5 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 2 | 10 | None. | No |

Recommendation: approve Option A only if outputs remain local artifact packets with explicit non-claim wording. If the owner wants buy/sell, price-target, or live trading wording, Stage 10C must stop because that is outside the current approved boundary.

### S10B-DQ-002: Orchestration And Data Refresh Boundary

Question: How should Stage 10C be invoked, and how should refreshed data enter it?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Manual documented sequence | User runs Stage 8 plan/update, stagewise rebuilds, and report generation manually. | 8 | 9 | 7 | 9 | 9 | 8 | 8 | 8 | 5 | 9 | Existing docs and future report command only. | No |
| B. Single local artifact CLI | Local CLI consumes explicit artifact roots/cutoff and writes a packet; provider calls remain out of scope by default. | 9 | 6 | 7 | 9 | 9 | 9 | 9 | 9 | 9 | 6 | New local CLI, tests, docs. | Yes |
| C. Scheduled task wrapper | Runs periodically around update/report steps. | 6 | 4 | 6 | 5 | 6 | 5 | 6 | 5 | 8 | 4 | Scheduler config, local environment policy, extra logs. | No |

Recommendation: approve Option B for usability, but constrain it to local artifact generation from explicit inputs. It must not directly execute live Stage 8 provider calls unless the owner separately approves live refresh execution.

### S10B-DQ-003: Model Scope And Prediction Method

Question: Which model outputs should Stage 10C expose, and how should predictions be generated?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Saved-prediction extraction | Extract approved Stage 5 validation/lockbox predictions and selected market hurdle comparisons. | 7 | 8 | 9 | 10 | 9 | 9 | 9 | 10 | 7 | 8 | Existing Stage 5 artifacts. | Yes for first implementation |
| B. Full Stage 2-6 rebuild then extraction | Rebuild after approved data changes, then create packet from refreshed saved predictions. | 8 | 5 | 4 | 8 | 9 | 8 | 8 | 8 | 6 | 5 | Existing stagewise CLIs plus rebuild time. | Yes as rebuild-compatible path |
| C. Persisted inference package | Save and load fitted models/preprocessors to score feature-only future rows. | 9 | 3 | 8 | 8 | 6 | 6 | 6 | 6 | 9 | 3 | New model package, feature-only schema, no-leakage tests. | No unless true future scoring is approved |

Recommendation: approve Option A plus compatibility with Option B for the first Stage 10C artifact packet. Approve Option C only if the owner explicitly wants true future forecast rows and accepts a larger model-packaging design/test burden.

### S10B-DQ-004: Forecast Row Role And Output Folder

Question: How should Stage 10C label rows and where should packets be written?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Versioned `data/prediction_outputs` packet | New local packet root with run date, cutoff, source digest, row digest, Stage 5 digest, and `prediction_outputs_v1`. | 9 | 7 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 7 | New directory convention and manifest validator. | Yes |
| B. Generic `runs/predictions/<timestamp>` | Runtime-style output folder keyed mainly by timestamp. | 7 | 8 | 9 | 8 | 7 | 7 | 7 | 7 | 8 | 8 | Less schema work, weaker provenance naming. | No |
| C. Under Stage 6 artifact root | Store Stage 10 outputs inside the Stage 6 reporting packet. | 5 | 8 | 9 | 8 | 4 | 4 | 5 | 4 | 7 | 8 | No new root, but mixes non-benchmark outputs with benchmark evidence. | No |

Recommendation: approve Option A. Use `historical_prediction` for extracted saved predictions, `diagnostic_only` for non-forecast comparisons, and reserve `forecast_candidate` for explicitly approved future-row inference outputs.

### S10B-DQ-005: Output Files And Visualization Technology

Question: Which files and visualization format should Stage 10C create?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Static HTML plus CSV/Parquet packet | Manifest, predictions, top-10 tables, relevant news, trajectory points, limitations, and offline `report.html`. | 9 | 6 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 6 | Parquet/CSV support and static HTML generation. | Yes |
| B. PNG/CSV bundle only | Machine-readable tables plus static image exports, no HTML report. | 7 | 8 | 8 | 9 | 8 | 8 | 8 | 8 | 6 | 8 | Matplotlib or existing plotting stack if approved. | No |
| C. Notebook or local dashboard | Notebook for exploration or dashboard for interactive browsing. | 6 | 4 | 6 | 5 | 5 | 5 | 6 | 5 | 8 | 4 | Notebook execution policy or dashboard dependencies. | No |

Recommendation: approve Option A. PNGs may be optional exports generated from the same packet data. Notebook use should remain development-only. A local dashboard should remain out of scope unless separately approved.

### S10B-DQ-006: Top-10 Ranking Policy

Question: How should top-10 candidates be selected and displayed?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Per-horizon event-state score | Rank each horizon by selected event-state prediction value with deterministic tie-breaks and visible flags. | 8 | 8 | 9 | 10 | 9 | 9 | 8 | 9 | 9 | 8 | Stage 5 prediction rows and limitation flags. | Yes |
| B. Per-horizon delta over market hurdle | Rank by event-state prediction minus selected market hurdle prediction. | 8 | 6 | 9 | 10 | 8 | 8 | 8 | 8 | 8 | 6 | Requires market-hurdle joins and clear caveats. | Secondary view |
| C. Combined cross-horizon score | Collapse all horizons into one aggregate ranking. | 5 | 6 | 9 | 10 | 6 | 5 | 5 | 6 | 8 | 6 | Rank aggregation logic and stronger caveats. | No as primary |

Recommendation: approve Option A as the primary view and Option B as an optional model-comparison view. Option C should be diagnostic only because horizons have different meanings and must not be collapsed into a trading score.

### S10B-DQ-007: Relevant News Method

Question: How should relevant news be selected for display?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Aligned-news fields only | Display deterministic recency/count/sentiment/relevance fields from Stage 3 aligned news. | 8 | 8 | 9 | 10 | 10 | 10 | 9 | 10 | 8 | 8 | Existing aligned-news artifacts. | Yes |
| B. Deterministic text snippets | Include limited article titles/snippets from aligned rows with cutoff checks and source caveats. | 7 | 6 | 9 | 8 | 8 | 8 | 8 | 8 | 8 | 6 | Text fields, licensing/source review, snippet tests. | Optional |
| C. LLM summary | Generate local or provider-based summaries of relevant news. | 6 | 3 | 4 | 4 | 4 | 3 | 5 | 4 | 8 | 3 | LLM dependency, prompt/version controls, source-text policy. | No |

Recommendation: approve Option A for first Stage 10C. Option B can be optional if exact source/cutoff/licensing caveats are included. Option C remains unapproved.

### S10B-DQ-008: Prediction Trajectory Graph

Question: What should a trajectory graph show?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Price history plus forecast markers | Historical close/return context with separate horizon markers for current predictions. | 8 | 6 | 8 | 9 | 9 | 9 | 9 | 9 | 8 | 6 | OHLCV context plus prediction packet rows. | Yes |
| B. Last-month predictions plus realized labels | Historical out-of-sample predictions and realized labels where label windows have elapsed. | 8 | 7 | 8 | 9 | 9 | 9 | 8 | 9 | 7 | 7 | Stage 5 predictions plus labels. | Optional historical panel |
| C. Horizon fan chart or projected price path | Connect future markers into a path or fan visualization. | 5 | 4 | 7 | 9 | 5 | 4 | 5 | 4 | 7 | 4 | Additional plotting semantics and strong caveats. | No |

Recommendation: approve Option A as the default. Option B can be a separate historical-context panel. Do not approve projected price paths because forward excess-return markers are not price-level forecasts.

### S10B-DQ-009: Validation Bar

Question: What validation must Stage 10C pass before any output is trusted?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Full packet/report validation | Manifest identity, row universe, horizons, cutoff, model provenance, rank determinism, report consistency, non-claims, no-network checks. | 10 | 5 | 8 | 9 | 10 | 10 | 10 | 10 | 8 | 5 | New validators and tests. | Yes |
| B. Minimal smoke validation | Check files exist and parse, with limited semantic validation. | 6 | 9 | 9 | 9 | 6 | 5 | 6 | 5 | 8 | 9 | Basic tests only. | No |
| C. Manual review only | User inspects outputs without automated gates. | 4 | 10 | 10 | 8 | 4 | 3 | 4 | 3 | 5 | 10 | No validators. | No |

Recommendation: approve Option A. Stage 10C should not mark outputs trusted unless these checks pass and the standard repo commands also pass.

### S10B-DQ-010: Sensitive Artifacts And Distribution Policy

Question: What must Stage 10C exclude from packets and reports?

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Correctness | Leakage/comparability safety | Usability | Maintenance cost | Dependencies | Recommended option |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| A. Exclude secrets and raw ledgers | Packet includes only sanitized manifests, derived limitations, and non-sensitive source references. | 9 | 8 | 9 | 10 | 10 | 10 | 10 | 10 | 8 | 8 | Redaction/exclusion tests. | Yes |
| B. Include redacted operational summaries | Add redacted update summaries for traceability, but never raw request URLs or keys. | 8 | 6 | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 6 | Redaction tests and summary schema. | Optional |
| C. Include raw request ledgers for audit | Copy raw provider ledgers into packet. | 4 | 7 | 9 | 1 | 3 | 2 | 3 | 4 | 6 | 7 | Sensitive-ledger handling and key rotation risk. | No |

Owner decision: Option A. Stage 10C packets/reports must exclude secrets and raw ledgers. Option B redacted operational summaries and Option C raw request ledgers are not approved for the first implementation path.

## 6. Resolved Owner Decisions

Stage 10B decisions are answered. Stage 10C development still requires separate explicit implementation approval:

| Decision ID | Decision area | Owner answer |
| --- | --- | --- |
| `S10B-DQ-001` | Output purpose and claim wording. | Option A: local model-output / forecast-candidate artifact with strict non-trading, non-benchmark, non-service/API, and non-Stage-6-reinterpretation wording. |
| `S10B-DQ-002` | Orchestration and data-refresh boundary. | Option B: single local artifact CLI consuming explicit artifact roots and cutoffs; no scheduled job, provider call, raw overwrite, hidden rebuild, service/API/dashboard, or Stage 6 reinterpretation. |
| `S10B-DQ-003` | Model scope and prediction method. | Option A first with Option B compatibility: Stage 5 saved-prediction extraction and future approved rebuild-output compatibility; no persisted inference package yet. |
| `S10B-DQ-004` | Forecast row role and output folder. | Option A: governed versioned `data/prediction_outputs/phase1_top50/...` packet root separate from Stage 6 benchmark artifacts. |
| `S10B-DQ-005` | Output files and visualization technology. | Option A: static HTML plus CSV/Parquet packet with manifest, limitations metadata, and offline report; no dashboard. |
| `S10B-DQ-006` | Top-10 ranking policy. | Custom combined: event-state score primary, delta over market hurdle secondary, cross-horizon combined score diagnostic only with caveats and non-claim joint summary. |
| `S10B-DQ-007` | Relevant news method. | Custom combined: aligned-news fields required, deterministic snippets optional if validated, no LLM summaries for first implementation. |
| `S10B-DQ-008` | Trajectory graph. | Custom combined: price/return history plus separate forecast markers primary, prior predictions plus elapsed realized labels optional, no projected price path/fan chart. |
| `S10B-DQ-009` | Validation bar. | Option A: full packet/report validation with fail-closed behavior. |
| `S10B-DQ-010` | Sensitive artifact policy. | Option A: exclude raw API-key-bearing ledgers, raw provider secrets, unsanitized request URLs, raw request ledgers, API keys, and unsanitized provider logs. |

## 7. Stage 10C Implementation Boundary If Approved

Stage 10C may change or add:

| Allowed if approved | Boundary |
| --- | --- |
| Local packet generator | Must remain local artifact generation and must not start a network listener. |
| Output manifest/schema | Must preserve source artifact roots, run date, cutoff, digests, model IDs, and non-claims. |
| Prediction extraction | Must only use approved Stage 5 saved predictions unless a separate inference-package decision is approved. |
| Static report generation | Must be offline and data-consistent with packet files. |
| Validators/tests | Must check cutoff, row universe, horizons, ranks, report consistency, non-claims, no-network behavior, and sensitive-artifact exclusion. |
| Documentation and memory | Must update truth/status docs, guidebook, references, current state, and ledger. |

Stage 10C may not change or create without separate explicit approval:

| Not approved by Stage 10B draft | Reason |
| --- | --- |
| Live provider calls or raw overwrites | Stage 8 live execution and overwrite behavior remain separately gated. |
| Provider, universe, target, horizon, alignment, metric, split, or comparator-roster changes | These are protected-scope or benchmark-comparability decisions. |
| Stage 6 reinterpretation or Stage 7C promotion | Stage 6 remains `clean_null`; Stage 7C remains diagnostics-only. |
| User-facing service/API/dashboard | Phase 1 remains local CLI/artifact-driven. |
| Buy/sell, long/short, price-target, profit, or trading recommendation outputs | Trading/signal scope remains unapproved. |
| Raw-news/LLM summarization | Requires reproducibility, source-text, dependency, and governance review. |
| Persisted inference package | Requires explicit approval because it introduces new model packaging and feature-only-row contracts. |
| Raw API-key-bearing ledgers in outputs | Sensitive artifacts must not be copied into report packets. |

## 8. Test Plan Sketch For Stage 10C

Required focused tests if Stage 10C is approved:

| Test area | Required check |
| --- | --- |
| Manifest identity | Folder fields, manifest fields, source artifact roots, and digests match. |
| Row universe and horizons | Only approved top-50 tickers and `1d`, `5d`, `10d`, `20d`, `60d` appear. |
| Prediction provenance | Every row maps to a Stage 5 saved-prediction row or explicitly approved inference package. |
| Cutoff enforcement | No news/OHLCV after `data_cutoff_date` or as-of-close cutoff is displayed. |
| Rank determinism | Recomputing ranks from predictions reproduces top-10 files exactly. |
| Report consistency | HTML tables/plots match the packet data exactly. |
| Non-claim wording | Report contains not-trading-advice, not-benchmark-result, clean-null, limitation-bearing, and provider-completeness caveats. |
| No-network/service boundary | Report generation starts no listener, API server, credential use, or provider call. |
| Sensitive artifacts | Packet excludes raw request URLs, API keys, raw ledgers, and unsanitized provider logs. |

Required validation commands after Stage 10C implementation:

```powershell
python -m pytest tests
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python -m compileall -q src scripts tests
```

Additional Stage 10C-specific validator names should be added only if implementation is approved.

## 9. Non-Claims

- Stage 10B did not implement update-to-prediction orchestration.
- Stage 10B did not run Stage 8 live provider calls.
- Stage 10B did not mutate or overwrite raw data.
- Stage 10B did not rebuild Stage 2 through Stage 6.
- Stage 10B did not create prediction-output files or visualization files.
- Stage 10B did not create a live inference API, dashboard, web service, or user-facing service boundary.
- Stage 10B did not create buy/sell, long/short, trading-profitability, or price-target claims.
- Stage 10B did not reinterpret the Stage 6 `clean_null` result or promote Stage 7C diagnostics.

## 10. Recommended Next Step

Stage 10B decisions are complete. Stage 10C should remain blocked until the owner explicitly approves implementation under the resolved Stage 10B constraints.
