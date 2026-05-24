# Detailed Execution Stages

Status: active-root granular execution and testing expansion. Created 2026-05-07 after user request for a highly detailed execution view and stage-specific prompt files, updated 2026-05-22 with Stage 7A research, Stage 7B decisions, Stage 7C diagnostics-only implementation plus post-lockbox holdout materialization, Stage 8 plan-first raw update script implementation, and Stage 9 documentation reconciliation. Prompt artifacts now live under `docs/Prompts/`. This document expands `docs/Execution_Plan.md`; it does not replace `ScopeDecisionLog.md`, `ResearchTruth.md`, `ProjectDefinition.md`, or `docs/Data_Separation_And_Overfitting_Control.md`.

## 1. Authority

Execution order and stage completion must obey:

| Authority | Role |
| --- | --- |
| `AgentRules.md` | Governance, approval gates, evidence rules, documentation-first discipline, and benchmark comparability. |
| `ScopeDecisionLog.md` | Owner-approved phase-1 scope and protected benchmark choices. |
| `ResearchTruth.md` | Active truth synthesis, historical-only boundaries, unresolved risks, and current implementation reality. |
| `ProjectDefinition.md` | Broad project definition, responsibilities, pipeline shape, and benchmark-family boundary. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Option B validation-design contract for data separation, preprocessing, metrics, predictions, and overfitting diagnostics. |
| `docs/Execution_Plan.md` | Stage sequence and coarse gates. |
| `docs/Unit_Testing.md`, `docs/db_Testing.md`, `docs/Benchmark_Testing.md`, `docs/Pipeline_Testing.md` | Validation obligations by layer. |
| `docs/Data_Update_Strategy.md` | Refresh, invalidation, rollback, and operations discipline. |
| `docs/agent/AgentMemory.md` | Operational-memory and event-ledger requirements. |

## 2. Protected Scope Invariants

No stage prompt may silently change these values:

| Area | Protected value |
| --- | --- |
| Phase-1 objective | Test event-state incremental value beyond market-only baselines. |
| Target family | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| First universe | Reproducible top-50 liquid large-cap universe. |
| OHLCV provider | Twelve Data. |
| News provider | Alpha Vantage. |
| SEC role | Static/company support only. |
| News alignment | Same-day as-of-close; after-hours and non-trading-day news roll forward. |
| No-news policy | Keep rows; encode explicit empty event state and no-news indicators. |
| Default event representation | Pooled dense embeddings plus scalar enrichments. |
| Default fusion | Simple gated fusion. |
| Evaluation | Purged-plus-embargoed walk-forward development evaluation plus final untouched lockbox. |
| Metrics | Regression primary; ranking mandatory secondary diagnostics. |
| Option B refinement | Split manifests, train-fold-only preprocessing, predeclared metrics, saved out-of-sample predictions, overfitting diagnostics, and contamination blockers. |
| Phase-1 runtime boundary | Local CLI/artifact-driven research only. |

Changes to any protected value require explicit approval before work continues.

## 3. Execution Dependency Graph

| Stage | Name | Status | Depends on | Unlocks |
| --- | --- | --- | --- | --- |
| Stage 0 | Active Documentation Repair | Completed | Governance, scope, research truth | Stage 0A and stable active docs. |
| Stage 0A | Comment-Only Structural Scaffold | Completed as scaffold only | Stage 0 docs, `docs/Prompts/StructuralFolderMapPrompt.md` | Stage 0B and implementation contract mapping. |
| Stage 0B | Data Separation And Overfitting Contract | Completed as design contract only | Stage 0A, Option B approval | Stage 1 and all later Option B gates. |
| Stage 1 | Raw Data Security And Coverage Audit | Completed as audit with blockers | Stage 0B | Clean raw-data status and safe provider artifacts. |
| Stage 2 | Dataset Contract Definition | Materialized for approved top-50 row universe with executable tests and completion validation | Stage 1, Stage 0B, clean-window decision | Dataset artifact contract and executable dataset validation. |
| Stage 3 | Feature And Label Pipeline | Materialized for the approved Stage 2 dataset with executable tests and validation | Stage 2 | Stage 4 split and benchmark-runner contract work. |
| Stage 4 | Split And Benchmark Runner | Materialized for the approved Stage 3 artifact with executable tests and validation | Stage 3 | Stage 5 model and comparator-ladder contract work. |
| Stage 5 | Models And Comparator Ladder | Materialized for approved Stage 4 split artifact with executable tests and validation | Stage 4, frozen comparator roster | Stage 6 metric and reporting work. |
| Stage 6 | Serious Benchmark Reporting | Materialized with executable tests and validation; current result class `clean_null` | Stages 0-5 complete | Evidence-backed clean-null conclusion and limitation-bearing comparability record. |
| Stage 7A | Contextual-Bandit Research | Executed research-only; no implementation | Stage 6 evidence preserved | Stage 7B decisions if research supports them. |
| Stage 7B | Contextual-Bandit Decision Comparison | Executed; all 10 Stage 7B decisions answered | Stage 7A research | Stage 7C diagnostics implementation. |
| Stage 7C | Contextual-Bandit Diagnostics And Documentation | Executed diagnostics-only with new post-lockbox holdout; benchmark claim false | Stage 7B decisions plus explicit Stage 7C/data-update approval | Future all-data final-execution training only if separately approved. |
| Stage 8 | Daily/Weekly Raw Data Update Scripts | Executed as plan-first scripts/tests; no live provider calls | Stage 6 state, data-update docs, explicit execution approval | Safer raw refresh workflow and Stage 2-6 rebuild trigger. |
| Stage 9 | Final Documentation Reconciliation | Executed documentation-only after Stage 8 | Approved future work | Documentation and memory consistency after future changes. |
| Stage 10A | Update-To-Prediction And Visualization Research | Executed research-only; no implementation/provider/output artifacts | Stage 6 state and Stage 8 boundary | Stage 10B decisions. |
| Stage 10B | Update-To-Prediction Decision Comparison | Executed as decision-comparison and approval capture; all `S10B-DQ-001` through `S10B-DQ-010` answered; no implementation/provider/output artifacts | Stage 10A research | Stage 10C development only after separate explicit implementation approval. |
| Stage 10C | Update-To-Prediction Development And Testing | Executed as local saved-prediction extraction packet implementation; benchmark claim false | Stage 10B decisions plus explicit Stage 10C implementation approval | Local prediction-output packet and validation artifacts. |
| Stage 11 | Holistic Audit And Improvement Research | Proposed prompt only; not executed | Stage 6 state | Improvement backlog and future decision prompts. |
| Stage 12 | DeepResearch Topic Prompt Maintenance | Proposed prompt only; not executed | Stage 10 prompt set | Stage 10 external-research prompt files. |

## 4. Common Stage Operating Rules

Every stage must follow these execution rules:

| Rule | Requirement |
| --- | --- |
| Build context first | Read current authority docs and affected scaffolds before editing. |
| Do not overwrite user work | Preserve unrelated dirty worktree changes. |
| Minimal correct change | Prefer small, testable edits over broad rewrites. |
| Tests before implementation claims | If executable code is introduced, executable tests or documented pending-test reasons must exist before completion. |
| Evidence before DONE | Completion requires command output, artifact paths, and memory updates. |
| Fail closed | Leakage, row drift, lockbox misuse, credential exposure, or missing artifacts block serious claims. |
| Update discoverability | New active files require guidebook, README or reference updates where appropriate. |
| Memory update | Current state and event ledger must record task, evidence, drift checkpoint, and reconciliation. |

## 5. Common Test Layers

| Test layer | Purpose | Applies to stages |
| --- | --- | --- |
| Governance validation | Confirms required governance and memory structure. | All stages. |
| Comment-only validation | Confirms scaffold files remain non-runnable when a stage is documentation-only. | Stage 0A, Stage 0B, documentation prompt updates. |
| Raw-data validation | Confirms raw files parse, coverage is explicit, truncation is visible, and secrets are handled. | Stage 1. |
| Contract validation | Confirms schemas, row keys, manifests, and configs match approved contracts. | Stage 2 onward. |
| Leakage validation | Confirms as-of safety, purge/embargo, lockbox isolation, and preprocessing-fit boundaries. | Stage 3 onward, hard gate in Stage 4. |
| Model comparison validation | Confirms identical rows, labels, splits, and metric definitions across branches. | Stage 5 and Stage 6. |
| Artifact packet validation | Confirms serious-run packet completeness and reproducibility. | Stage 4 through Stage 6. |
| Benchmark comparability review | Confirms no benchmark-family drift or invalidation contradiction remains. | Stage 6 and any rerun/update stage. |

## 6. Stage 0 Detailed View: Active Documentation Repair

| Dimension | Requirement |
| --- | --- |
| Primary owner | Agent operating under `AgentRules.md`; user owns approval-gated changes. |
| Objective | Restore and maintain active-root theory, design, validation, operations, onboarding, and guidebook docs. |
| Inputs | `AgentRules.md`, `docs/agent/*.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`, current repo state, audit reports. |
| Outputs | Active docs under `docs/`, root onboarding docs, updated guidebook, operational memory entries. |
| Completion class | Documentation readiness only; no pipeline readiness claim. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 0.1 | Load governance and memory rules. | File paths read and recovered active constraints. |
| 0.2 | Reconcile active scope and truth with repository state. | `ScopeDecisionLog.md`, `ResearchTruth.md`, and audit references. |
| 0.3 | Create or repair active theory/design/validation docs. | Changed doc paths and summaries. |
| 0.4 | Repair stale references to deleted scripts, outdated daemon names, or unsupported dataset claims. | Before/after doc evidence. |
| 0.5 | Update guidebook and README for discoverability. | `Complete_guidebook.txt`, `README.md`. |
| 0.6 | Update operational memory. | `Current_State.md`, `Event_Ledger.ndjson`. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Governance validator | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Scope consistency review | Search protected values across active docs. | No contradiction with `ScopeDecisionLog.md`. |
| Non-implementation review | Manual doc review. | No claim that active pipeline, tests, dataset, or model exists. |
| Memory evidence review | Read memory files. | Task/event/evidence entries match work performed. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Active docs exist | Required root and `docs/` files exist. |
| No unsupported implementation claim | Current active root remains described accurately. |
| Validation passes | Governance validator passes. |
| Memory updated | Task status, evidence, drift checkpoint, and reconciliation logged. |

## 7. Stage 0A Detailed View: Comment-Only Structural Scaffold

| Dimension | Requirement |
| --- | --- |
| Primary owner | Agent for scaffold creation; user owns permission to move from scaffold to implementation. |
| Objective | Create `src/`, `configs/`, and `tests/` as comment-only architecture scaffolds. |
| Inputs | Stage 0 docs, `docs/Prompts/StructuralFolderMapPrompt.md`, `ProjectDefinition.md`, `ResearchTruth.md`. |
| Outputs | Comment-only `src/event_state_forecasting/`, `configs/`, and `tests/` trees. |
| Completion class | Structural scaffold only; no runtime behavior. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 0A.1 | Verify no active implementation files would be overwritten. | Root/path listing or file checks. |
| 0A.2 | Create package, config, and planned-test scaffold files as comments only. | File paths and scaffold counts. |
| 0A.3 | Include responsibilities, inputs, outputs, planned dependencies, limitations, and blind spots in each file. | File headers and comment blocks. |
| 0A.4 | Validate generated files contain only comments or blanks. | Comment-only validation output. |
| 0A.5 | Update docs and memory to mark scaffold as non-runnable. | Guidebook, README, memory entries. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Comment-only validation | Scan `.py` and `.yaml` scaffold files for non-comment lines. | `COMMENT_ONLY_VALIDATION PASSED`. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Guidebook coverage | Count scaffold files and compare with guidebook. | Counts match all scaffold files. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Tree exists | `src/`, `configs/`, and `tests/` exist. |
| No runtime behavior | No imports, assignments, functions, classes, active YAML keys, or assertions. |
| Discoverability updated | Guidebook and README describe comment-only state. |
| Memory updated | Scaffold task completed with validation evidence. |

## 8. Stage 0B Detailed View: Data Separation And Overfitting Contract

| Dimension | Requirement |
| --- | --- |
| Primary owner | Agent for documentation propagation; user owns any protocol change beyond approved Option B. |
| Objective | Formalize Option B validation refinement without changing benchmark family or DQ-012 doctrine. |
| Inputs | Option B approval, `ScopeDecisionLog.md`, `ProjectDefinition.md`, validation docs, comment-only scaffolds. |
| Outputs | `docs/Data_Separation_And_Overfitting_Control.md`, updated active docs and scaffold comments. |
| Completion class | Design-contract readiness only; no executable enforcement. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 0B.1 | Record Option B as preserving purged/embargoed walk-forward plus lockbox. | Scope and truth doc updates. |
| 0B.2 | Define row identity and split-role contract. | Data-separation contract sections. |
| 0B.3 | Define purge, embargo, and lockbox misuse blockers. | Split and lockbox contract sections. |
| 0B.4 | Define train-fold-only preprocessing. | Preprocessing-fit contract. |
| 0B.5 | Define predeclared metrics and saved-prediction requirements. | Metric contract and config scaffolds. |
| 0B.6 | Define overfitting diagnostics. | Diagnostic contract and benchmark-testing docs. |
| 0B.7 | Propagate contract through docs, configs, source comments, and tests comments. | Changed file list and guidebook coverage. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Comment-only validation | Scan scaffold files. | `COMMENT_ONLY_VALIDATION PASSED`. |
| Option B consistency search | Search active docs for contract references and protected invariants. | Contract present without benchmark-family changes. |
| Guidebook coverage | Count active docs and config sections. | Counts reflect Option B additions. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Contract exists | `docs/Data_Separation_And_Overfitting_Control.md` exists. |
| Scope preserved | Target, horizons, providers, universe, alignment, and evaluation doctrine unchanged. |
| Docs propagated | Affected active docs and scaffolds reference Option B. |
| Validation passes | Governance, comment-only, and coverage checks pass. |

## 9. Stage 1 Detailed View: Raw Data Security And Coverage Audit

| Dimension | Requirement |
| --- | --- |
| Primary owner | Data-validation implementer; security owner is the agent performing ledger handling under user approval. |
| Objective | Make raw provider state safe, parseable, auditable, and usable for clean-window decisions. |
| Inputs | Top-50 universe file, Alpha Vantage raw corpus, manifests, request ledgers, run logs, future Twelve Data OHLCV evidence, SEC support evidence if needed. |
| Outputs | Raw audit report, machine-readable raw audit manifest, credential-risk report, truncation-risk report, clean-window candidate inputs. |
| Completion class | Raw-data readiness for dataset-contract work, not benchmark readiness. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 1.1 | Verify frozen top-50 universe file and canonical ticker preservation. | Universe count, ordering, ticker normalization report. |
| 1.2 | Verify Alpha Vantage canonical path coverage for expected ticker-year/current windows. | Coverage matrix and missing/extra files report. |
| 1.3 | Parse every canonical raw JSON payload. | Parse status summary and failure list. |
| 1.4 | Summarize feed rows by ticker, year, and source file. | Row-count table and manifest. |
| 1.5 | Detect likely truncated windows at provider limit. | Truncation count and affected windows list. |
| 1.6 | Detect empty-feed windows and preserve them as explicit data status. | Empty-feed report. |
| 1.7 | Detect duplicate, non-canonical, and conflict files. | Duplicate/conflict manifest. |
| 1.8 | Audit raw request ledgers and logs for API-key-bearing URLs. | Credential-risk report with safe handling recommendation. |
| 1.9 | Verify or document absence of Twelve Data OHLCV evidence. | OHLCV coverage status and blocker if missing. |
| 1.10 | Verify or document absence of SEC support artifacts needed for phase 1. | SEC support status. |
| 1.11 | Produce raw audit summary for memory and downstream Stage 2. | Audit artifact and event-ledger evidence. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Raw parse test | Future executable raw-validation command or script. | All canonical files parse or failures are explicit blockers. |
| Coverage test | Future universe-to-raw matrix validation. | Expected top-50 windows accounted for. |
| Truncation test | Count feed rows at provider limit and status fields. | Likely truncated windows listed, not hidden. |
| Empty-feed test | Detect valid empty provider responses. | Empty feeds preserved with explicit reason. |
| Secret scan | Search request ledgers/logs for API key patterns and query URLs. | Secrets absent from shareable artifacts or files isolated. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Raw status known | Coverage, parse, truncation, empty-feed, and duplicate status recorded. |
| Secret risk handled | Ledger keys sanitized, isolated, or explicitly blocked from sharing. |
| Provider limitations visible | Truncation and missing OHLCV/SEC evidence are not hidden. |
| Stage 2 inputs ready | Clean-window and dataset-contract work has reliable raw evidence inputs. |

## 10. Stage 2 Detailed View: Dataset Contract Definition

| Dimension | Requirement |
| --- | --- |
| Primary owner | Dataset-contract implementer; validation owner must write executable dataset tests before completion claims. |
| Objective | Define and implement the canonical benchmark dataset artifact, row identity, clean-window policy, and validation contract. |
| Inputs | Stage 1 raw audit outputs, approved scope, Option B contract, clean-window decision, OHLCV evidence, top-50 universe. |
| Outputs | Dataset schema, dataset versioning policy, manifest schema, clean-window record, row contract, executable dataset validation tests, materialized dataset artifact if implementation is approved. |
| Completion class | Dataset readiness for feature/label work only after executable checks pass. |

Execution status as of 2026-05-14: `docs/agent/agent_log/Stage2_Dataset_Contract_Definition_2026-05-12.md` and `data/manifests/stage2_dataset_contract_definition_2026-05-12.json` define the original contract. Stage 2 has now been materialized at `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/` with a partitioned Parquet panel, dataset manifest, row-universe digest, clean-window record, CVX derived patch manifest, executable contract tests, and `scripts/validate_stage2_completion.py`. This remains dataset readiness only; downstream Stage 3 through Stage 5 artifacts exist separately, and metric/benchmark readiness remains absent.

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 2.1 | Define dataset artifact format and storage path conventions. | Contract doc, config comments or active config after approval. |
| 2.2 | Define row key fields: ticker, as-of date, horizon placeholder, feature timestamp, label windows, split role, fold ID, lockbox flag. | Schema contract. |
| 2.3 | Define dataset version identity and hashing policy. | Versioning contract and digest examples. |
| 2.4 | Define clean-window candidate evaluation using OHLCV/news/label/split feasibility. | Clean-window decision record. |
| 2.5 | Define no-news row preservation and availability indicators. | Dataset contract and tests. |
| 2.6 | Define branch row equality requirement for market-only and event-state branches. | Row-universe equality test plan. |
| 2.7 | Define manifest fields: sources, coverage, limitations, provider status, row counts, label availability, known exclusions. | Dataset manifest schema. |
| 2.8 | Implement validation tests before or with dataset builder. | Executable tests under `tests/data/` and `tests/dataset/`. |
| 2.9 | If approved, implement dataset builder modules. | `src/event_state_forecasting/dataset/` and CLI artifacts. |
| 2.10 | Validate dataset artifact and record evidence. | Test outputs, manifest paths, memory updates. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Schema contract tests | `tests/data/test_contracts_contract.py`. | Required fields enforced as blockers. |
| Universe tests | `tests/data/test_universe_contract.py`. | Top-50 rows parse deterministically; dotted tickers preserved. |
| Panel builder tests | `tests/dataset/test_panel_builder_contract.py`. | Market/news rows preserve no-news and clean-window constraints. |
| Row equality tests | `tests/dataset/test_row_universe_contract.py`. | Branch row drift fails closed. |
| Manifest tests | Future manifest validation tests. | Version, source, coverage, and limitation fields present. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Deprecated OHLCV salvage audit | `python scripts/audit_deprecated_ohlcv_salvage.py` | Reports usable salvage evidence or blockers without copying deprecated data. |
| Stage 2 input-readiness gate | `python scripts/validate_stage2_inputs.py` | Reports ready/blocked input status without building a dataset. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Clean window resolved | Clean historical window approved or explicitly recorded as blocker. |
| Dataset contract executable | Tests exist and enforce schema, row identity, row equality, and no-news policy. |
| Dataset artifact valid | If built, artifact has manifest and stable version identity. |
| No benchmark claim | Dataset readiness is not treated as model or benchmark success. |

## 11. Stage 3 Detailed View: Feature And Label Pipeline

| Dimension | Requirement |
| --- | --- |
| Primary owner | Feature/label implementer; validation owner must enforce as-of and target contracts. |
| Objective | Build market features, event-state features, no-news states, and forward excess-return labels without leakage. |
| Inputs | Stage 2 dataset artifact, raw/normalized provider data, approved alignment policy, approved horizon set. |
| Outputs | Feature artifacts, label artifacts, feature/label manifests, executable feature and label tests. |
| Completion class | Feature/label readiness for split construction. |

Execution status as of 2026-05-15: `docs/agent/agent_log/Stage3_Materialization_2026-05-15.md`, `data/manifests/stage3_completion_validation_2026-05-15.json`, and `scripts/validate_stage3_completion.py` record Stage 3 materialization. Feature and label artifacts exist for the approved Stage 2 dataset; Stage 4 split artifacts and Stage 5 model-output artifacts now exist separately, while metric and benchmark-result artifacts do not exist yet.

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 3.1 | Define market feature availability as of prediction timestamp. | Market feature contract. |
| 3.2 | Implement or document OHLCV transformations without future data. | Feature code and tests after approval. |
| 3.3 | Implement news alignment: same-day as-of-close, after-hours roll-forward, non-trading-day roll-forward. | Alignment tests. |
| 3.4 | Implement event-state feature construction with pooled dense embeddings plus scalar enrichments. | Event-state manifest and tests. |
| 3.5 | Implement explicit no-news states and indicators. | No-news tests and row counts. |
| 3.6 | Implement forward excess-return labels for `1d`, `5d`, `10d`, `20d`, `60d`. | Label tests and endpoint checks. |
| 3.7 | Preserve row identity and row universe equality across market-only and event-state feature sets. | Row digest comparison. |
| 3.8 | Record feature availability timestamps and label window start/end. | Feature/label manifest. |
| 3.9 | Validate missing data behavior and excluded-row reasons. | Validation report. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Market feature tests | `tests/features/test_market_features_contract.py`. | No future OHLCV used. |
| News alignment tests | `tests/features/test_news_alignment_contract.py`. | After-hours and non-trading-day behavior correct. |
| Event-state tests | `tests/features/test_event_state_contract.py`. | Event-state rows preserve branch equality. |
| No-news tests | `tests/features/test_no_news_state_contract.py`. | No-news rows retained and encoded explicitly. |
| Label tests | `tests/features/test_labels_contract.py`. | All approved horizons computed with correct windows. |
| Leakage precheck | Future split/leakage validation support. | Feature timestamp and label windows present. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| As-of safety | Feature availability timestamps prove no future information. |
| Label correctness | Approved horizons have correct forward excess-return windows. |
| Row equality | Market-only and event-state branches share identical rows. |
| Tests pass | Feature and label tests pass or stage remains incomplete. |

## 12. Stage 4 Detailed View: Split And Benchmark Runner

| Dimension | Requirement |
| --- | --- |
| Primary owner | Split/evaluation implementer; benchmark owner must enforce artifact packet gates. |
| Objective | Implement purged-plus-embargoed folds, lockbox handling, leakage checks, saved-prediction requirements, and benchmark artifact orchestration. |
| Inputs | Stage 3 feature/label artifacts, Option B contract, dataset version, and approved split/artifact-packet policy. |
| Outputs | Split manifest, fold artifacts, lockbox record, leakage validation report, benchmark runner skeleton or implementation, artifact packet validation. |
| Completion class | Benchmark infrastructure readiness for model execution, not model-result readiness. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 4.1 | Define fold schedule from clean-window dates. | Split config and fold manifest. |
| 4.2 | Apply purge for overlapping label windows. | Purge row counts by fold and horizon. |
| 4.3 | Apply explicit embargo policy. | Embargo spans and excluded-row reasons. |
| 4.4 | Reserve final untouched lockbox and enforce access policy. | Lockbox boundary record. |
| 4.5 | Validate split-role exclusivity for every row. | Split validation report. |
| 4.6 | Validate no train/validation/lockbox overlap or horizon contamination. | Leakage report. |
| 4.7 | Define artifact packet membership and validation. | Artifact-packet config and tests. |
| 4.8 | Define saved-prediction schema required from Stage 5. | Prediction contract and tests. |
| 4.9 | Build benchmark runner only after split and artifact tests exist. | Runner code and smoke tests if approved. |
| 4.10 | Record evidence and incomplete claims accurately. | Memory and run metadata. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Purge/embargo tests | `tests/split/test_purged_embargo_contract.py`. | Overlapping labels and embargoed rows excluded. |
| Leakage tests | `tests/split/test_leakage_contract.py`. | Contamination blockers fail closed. |
| Artifact packet tests | `tests/benchmark/test_artifact_packet_contract.py`. | Missing artifacts block serious-run completion. |
| Benchmark runner tests | `tests/benchmark/test_benchmark_runner_contract.py`. | Runner rejects scope drift and row drift. |
| Integration gate tests | Future `tests/integration/test_pipeline_contract.py`. | Stage order enforced. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Split manifest valid | Fold windows, purge spans, embargo spans, lockbox boundary, and row counts recorded. |
| Leakage checks pass | No contamination blocker remains. |
| Artifact packet gate exists | Missing evidence fails closed. |
| Runner does not train silently | Benchmark runner cannot bypass model/prediction/artifact requirements. |

Execution status as of 2026-05-15: `docs/agent/agent_log/Stage4_Split_And_Packet_Materialization_2026-05-15.md`, `data/manifests/stage4_completion_validation_2026-05-15.json`, and `scripts/validate_stage4_completion.py` record Stage 4 materialization. Split, lockbox, leakage, artifact-packet, and gate-safe runner artifacts exist for the approved Stage 3 artifact; Stage 5 model/preprocessing/saved-prediction artifacts now exist separately, while metric, comparison-summary, and benchmark-result artifacts do not exist yet.

## 13. Stage 5 Detailed View: Models And Comparator Ladder

| Dimension | Requirement |
| --- | --- |
| Primary owner | Model/comparator implementer; validation owner must enforce identical rows and saved predictions. |
| Objective | Implement frozen comparator ladder and event-state model execution under identical rows, labels, splits, preprocessing, and metrics. |
| Inputs | Stage 4 split artifacts, feature/label artifacts, frozen comparator roster, model configs, preprocessing contract. |
| Outputs | Trained model artifacts, preprocessing-fit manifests, saved out-of-sample predictions, training diagnostics, model manifests. |
| Completion class | Model-output readiness for evaluation, not benchmark conclusion. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 5.1 | Freeze exact comparator roster before training. | Comparator roster record and config. |
| 5.2 | Define model IDs, allowed inputs, hyperparameter search scope, and seed policy. | Resolved model config. |
| 5.3 | Implement market-only baselines and broader comparator families in approved order. | Model artifacts and tests. |
| 5.4 | Implement event-state model family using simple gated fusion as phase-1 default. | Model artifacts and tests. |
| 5.5 | Fit learned preprocessing only on each fold's training rows. | Preprocessing-fit manifest. |
| 5.6 | Produce saved out-of-sample predictions with row keys, fold IDs, horizon IDs, model IDs, dataset version. | Prediction artifacts. |
| 5.7 | Record train/validation fit diagnostics without inspecting lockbox for selection. | Training diagnostics. |
| 5.8 | Enforce identical row universe across market-only and event-state branches. | Row equality report. |
| 5.9 | Record search-space summary for overfitting diagnostics. | Search-space manifest. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Comparator ladder tests | `tests/models/test_comparator_ladder_contract.py`. | Roster and allowed inputs match frozen config. |
| Gated fusion tests | `tests/models/test_gated_fusion_contract.py`. | Model consumes approved inputs only. |
| Training tests | `tests/models/test_training_contract.py`. | Train-only preprocessing and fold isolation enforced. |
| Saved prediction tests | `tests/models/test_saved_predictions_contract.py`. | Prediction identity fields complete; in-sample claims rejected. |
| Metric smoke tests | Future evaluation tests. | Metrics consume saved predictions only. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Roster frozen | Comparator ladder cannot drift during result inspection. |
| Predictions saved | Out-of-sample predictions exist for all required model/fold/horizon combinations or exclusions are explicit. |
| Preprocessing manifest present | Learned transforms fit only on training rows. |
| No lockbox tuning | Lockbox not used for model or feature selection. |

Execution status as of 2026-05-21: `docs/agent/agent_log/Stage5_Model_And_Prediction_Materialization_2026-05-21.md`, `data/manifests/stage5_completion_validation_2026-05-21.json`, and `scripts/validate_stage5_completion.py` record Stage 5 materialization. The active roster is `phase1_top50_pragmatic_broader_sklearn_v1`; artifacts contain `8` model IDs, `360` model-fit records, `360` preprocessing-fit records, and `2088000` saved prediction rows. Metrics, overfitting diagnostics, comparison summaries, serious-run results, and benchmark claims do not exist yet.

## 14. Stage 6 Detailed View: Serious Benchmark Reporting

| Dimension | Requirement |
| --- | --- |
| Primary owner | Benchmark reporting owner; validation owner must independently confirm packet integrity. |
| Objective | Evaluate approved benchmark family and report robust positive, conditional positive, or clean null under full artifact evidence. |
| Inputs | Stage 5 saved predictions, frozen labels, split manifest, preprocessing-fit manifest, metrics config, diagnostic config, lockbox boundary. |
| Outputs | Metric artifacts, ranking diagnostics, overfitting diagnostic report, comparison summary, benchmark comparability classification, final run packet. |
| Completion class | Serious benchmark result only if every gate passes. |

Granular work requirements:

| Step | Action | Evidence |
| --- | --- | --- |
| 6.1 | Validate artifact packet completeness before metric interpretation. | Packet validation output. |
| 6.2 | Compute primary regression metrics from saved out-of-sample predictions and frozen labels. | Metric artifact. |
| 6.3 | Compute mandatory secondary ranking diagnostics. | Ranking diagnostic artifact. |
| 6.4 | Compute paired comparison versus market-only baseline where assumptions are satisfied. | Paired comparison artifact. |
| 6.5 | Compute train-to-validation gaps by model family and horizon. | Overfitting diagnostic report. |
| 6.6 | Compute development-fold means and standard deviations. | Diagnostic tables. |
| 6.7 | Compute positive-fold and positive-horizon rates for event-state improvement. | Diagnostic tables. |
| 6.8 | Compute validation-to-lockbox degradation after development is frozen. | Lockbox degradation report. |
| 6.9 | Add multiple-comparison and search-space summary. | Diagnostic narrative and manifest. |
| 6.10 | Classify result as robust positive, conditional positive, or clean null. | Comparison summary. |
| 6.11 | Review benchmark comparability and invalidation triggers. | Comparability classification. |
| 6.12 | Update memory and report final evidence. | Event ledger and final response. |

Testing strategy:

| Test | Command or method | Pass condition |
| --- | --- | --- |
| Metric contract tests | `tests/evaluation/test_metric_contracts.py`. | Metrics use saved predictions and frozen labels only. |
| Artifact packet validation | `python scripts/validate_stage6_completion.py --write`. | Packet includes all required evidence families. |
| Lockbox integrity review | Check lockbox access and result-inspection timeline. | No forbidden lockbox use. |
| Overfitting diagnostic review | Verify required diagnostic fields. | No missing diagnostic category. |
| Comparability review | Apply invalidation triggers. | Result comparable or explicitly classified otherwise. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |

Exit criteria:

| Criterion | Required state |
| --- | --- |
| Full packet exists | Dataset, config, split, preprocessing, predictions, metrics, diagnostics, comparison summary present. |
| Metrics valid | Computed from saved out-of-sample predictions and frozen labels. |
| Diagnostics complete | Required Option B diagnostics present. |
| Interpretation constrained | Result class reflects evidence without metric shopping. |
| Memory complete | Task, evidence, drift checkpoint, and reconciliation logged. |

Execution status as of 2026-05-21: `docs/agent/agent_log/Stage6_Serious_Benchmark_Reporting_2026-05-21.md`, `data/manifests/stage6_completion_validation_2026-05-21.json`, and `scripts/validate_stage6_completion.py` record Stage 6 materialization. The active Stage 6 artifact has `800` metric rows, `800` ranking diagnostic rows, `800` paired comparison rows, passed serious-packet validation, result class `clean_null`, and comparability classification `limitation_bearing`.

## 15. Stage 7-12 Prompt And Research Status

Stage 7A has been executed as a research-only contextual-bandit feasibility study. Stage 7B decision collection is complete. Stage 7C has been executed as diagnostics-only contextual-bandit implementation, approved Twelve Data update, refreshed Stage 2/3/4/5 artifact chain, and new post-Stage-6-lockbox diagnostic holdout. Stage 8 has been executed as plan-first daily/weekly raw update script implementation with tests, but no live provider calls or raw overwrites were executed. Stage 9 has been executed as documentation and operational-memory reconciliation only. Stage 10A has been executed as research-only update-to-prediction and visualization workflow analysis. Stage 10B has been executed as decision-comparison and approval capture with all ten Stage 10B DQs answered. Stage 10C has been executed as local prediction-output packet generation from existing Stage 5 saved predictions. Stage 11 through Stage 12 remain proposed prompt artifacts only. None of these files authorize live inference, web/API/service work, all-data final-execution training-output, live buy/sell signals, or benchmark-comparability promotion by themselves.

| Prompt file | Proposed purpose | Status |
| --- | --- | --- |
| `docs/Prompts/Stage7APrompt.md` | Research contextual-bandit feasibility for historical daily replay. | Executed research-only; memo at `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md`. |
| `docs/Prompts/Stage7BPrompt.md` | Present contextual-bandit decision matrix and approval request. | Executed; decisions answered in `ScopeDecisionLog.md`. |
| `docs/Prompts/Stage7CPrompt.md` | Integrate approved contextual-bandit protocol into docs and diagnostics. | Executed diagnostics-only with Stage 7 config/code/tests/final-execution stub and post-lockbox diagnostic artifact. |
| `docs/Prompts/Stage8Prompt.md` | Daily/weekly Alpha Vantage news and Twelve Data OHLCV update scripts. | Executed as plan-first local scripts/tests; live provider calls remain unapproved. |
| `docs/Prompts/Stage9Prompt.md` | Final documentation reconciliation. | Executed documentation-only after Stage 8. |
| `docs/Prompts/Stage10APrompt.md` | Research update-to-prediction outputs and visualization. | Executed research-only; memo at `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`. |
| `docs/Prompts/Stage10BPrompt.md` | Present update-to-prediction/visualization decision matrix. | Executed as decision-comparison and approval capture; all Stage 10B decisions answered in `ScopeDecisionLog.md`; memo at `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`. |
| `docs/Prompts/Stage10CPrompt.md` | Local development/testing for prediction output and visualization packet artifacts. | Executed as local Stage 10C packet implementation; no provider calls, persisted inference package, service/API/dashboard, trading signal, Stage 6 reinterpretation, or benchmark-comparability promotion. |
| `docs/Prompts/Stage11Prompt.md` | Holistic repo/model/state-of-art audit and improvement research. | Prompt-only, not executed. |
| `docs/Prompts/Stage12Prompt.md` | Maintain Stage 10 DeepResearch chat topic prompts. | Prompt-only, not executed. |

## 16. Stage Prompt Files

Use the stage prompt files below for future execution. They are prompts only; executing one still requires respecting approval gates and current repository state.

| Prompt file | Stage |
| --- | --- |
| `docs/Prompts/Stage0Prompt.md` | Stage 0: Active Documentation Repair. |
| `docs/Prompts/Stage0APrompt.md` | Stage 0A: Comment-Only Structural Scaffold. |
| `docs/Prompts/Stage0BPrompt.md` | Stage 0B: Data Separation And Overfitting Contract. |
| `docs/Prompts/Stage1Prompt.md` | Stage 1: Raw Data Security And Coverage Audit. |
| `docs/Prompts/Stage2Prompt.md` | Stage 2: Dataset Contract Definition. |
| `docs/Prompts/Stage3Prompt.md` | Stage 3: Feature And Label Pipeline. |
| `docs/Prompts/Stage4Prompt.md` | Stage 4: Split And Benchmark Runner. |
| `docs/Prompts/Stage5Prompt.md` | Stage 5: Models And Comparator Ladder. |
| `docs/Prompts/Stage6Prompt.md` | Stage 6: Serious Benchmark Reporting. |
| `docs/Prompts/Stage7APrompt.md` | Stage 7A: Contextual-Bandit Research. |
| `docs/Prompts/Stage7BPrompt.md` | Stage 7B: Contextual-Bandit Decision Comparison. |
| `docs/Prompts/Stage7CPrompt.md` | Stage 7C: Contextual-Bandit Documentation Integration. |
| `docs/Prompts/Stage8Prompt.md` | Stage 8: Daily/Weekly Raw Data Update Scripts. |
| `docs/Prompts/Stage9Prompt.md` | Stage 9: Final Documentation Reconciliation. |
| `docs/Prompts/Stage10APrompt.md` | Stage 10A: Update-To-Prediction And Visualization Research. |
| `docs/Prompts/Stage10BPrompt.md` | Stage 10B: Update-To-Prediction Decision Comparison. |
| `docs/Prompts/Stage10CPrompt.md` | Stage 10C: Update-To-Prediction Development And Testing. |
| `docs/Prompts/Stage11Prompt.md` | Stage 11: Holistic Audit And Improvement Research. |
| `docs/Prompts/Stage12Prompt.md` | Stage 12: DeepResearch Topic Prompt Maintenance. |

## 17. Current Blocking Summary

| Blocker | Blocks | Required resolution |
| --- | --- | --- |
| Alpha Vantage provider article completeness not claimed | Dataset, feature, and result limitation reporting | Preserve truncation and empty-feed flags; do not claim provider-level article completeness. |
| API-key-bearing raw ledger risk | Safe sharing and publication | Sanitize or isolate ledgers and rotate exposed keys before publication. |
| Active split-adjustment method unresolved | Future label/benchmark comparability and later split/evaluation interpretation | Select an active split-adjustment method only after explicit approval/design; Stage 2 materialization used a derived CVX manifest and did not mutate raw values. |
| Train-validation gap blocked | Stage 6 diagnostic completeness caveat | Stage 5 saved validation and lockbox predictions only, so Stage 6 records the gap as explicitly blocked rather than inventing train metrics. |

## 18. Non-Claims

This document now records implementation status through Stage 7C. The current Stage 6 artifacts create a serious benchmark reporting packet with a `clean_null` result class and `limitation_bearing` comparability. Stage 7C creates diagnostics-only contextual-bandit evidence on a new post-lockbox holdout with `benchmark_claim=false`; it does not reinterpret Stage 6 or approve all-data final-execution training-output.
