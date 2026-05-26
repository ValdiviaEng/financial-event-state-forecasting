# Execution Plan

Status: active-root execution plan. Stages below describe approved order and gates; approved Stage 2 through Stage 7C paths, Stage 8 plan-first raw-update scripts/tests, and Stage 10C local prediction-output packet paths have been converted from the 2026-05-07 scaffold into executable implementations, while remaining provider/utility/expansion paths remain comment-only. Granular execution details now live in `docs/Detailed_Execution_Stages.md`; reusable execution prompts live under `docs/Prompts/`, including `docs/Prompts/Stage0Prompt.md`, `docs/Prompts/Stage0APrompt.md`, `docs/Prompts/Stage0BPrompt.md`, and `docs/Prompts/Stage1Prompt.md` through `docs/Prompts/Stage12Prompt.md`, including split Stage 7 and Stage 10 prompt files. Stage 7A has been executed as research-only; Stage 7B decision collection is complete; Stage 7C has been executed as diagnostics-only implementation plus post-lockbox holdout materialization; Stage 8 has been executed as plan-first script implementation without live provider calls; Stage 9 has been executed as documentation and memory reconciliation; Stage 10A has been executed as research-only workflow analysis; Stage 10B has been executed as decision-comparison and approval capture with all ten Stage 10B DQs answered; Stage 10C has been executed as a local saved-prediction extraction packet implementation; Stage 11 through Stage 12 remain unexecuted unless separately approved. Post-Stage-6 stagewise rerun methodology lives in `ExecutionPipeline.md`.

## Stage Prompt Index

| Prompt | Stage |
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

## Stage 0: Active Documentation Repair

- Objective: restore AgentRules-required active-root theory, design, validation, and operations docs.
- Dependencies: `AgentRules.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`.
- Files involved: `docs/Complete_Theoretical_Background.md`, `docs/References.md`, `docs/Implementation_Decisions.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, validation docs, operations docs, `README.md`.
- Required tests: governance validator.
- Completion criteria: required skeleton docs exist, stale daemon/universe references repaired, operational memory updated.
- Status: completed as active documentation repair; later approved Stage 2 through Stage 8 plus Stage 10C scoped work now provides separate implementation, diagnostic, update-tooling, or output-packet evidence for approved claims.

## Stage 0A: Comment-Only Structural Scaffold

- Objective: create the active-root `src/`, `configs/`, and `tests/` folder structure as comment-only design scaffolding.
- Dependencies: Stage 0 active docs, `ProjectDefinition.md`, `docs/Prompts/StructuralFolderMapPrompt.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`.
- Files involved: `src/event_state_forecasting/`, `configs/`, `tests/`, guidebook, architecture, implementation, validation, README, and operational memory files.
- Required tests: governance validator and scaffold comment-only validation.
- Completion criteria: folder tree exists, generated `.py` and `.yaml` files contain only comment or blank lines, docs and memory are updated, and no executable pipeline or benchmark claim is made.
- Status: completed as structural scaffold only; later approved Stage 2 through Stage 8 plus Stage 10C conversions supersede scaffold-only status only for their explicit paths.

## Stage 0B: Data Separation And Overfitting Contract

- Objective: formalize the owner-approved Option B validation refinement before executable pipeline work.
- Dependencies: Stage 0A, `ScopeDecisionLog.md`, `ResearchTruth.md`, `ProjectDefinition.md`, `docs/Benchmark_Testing.md`, `docs/db_Testing.md`, `docs/Pipeline_Testing.md`.
- Files involved: `docs/Data_Separation_And_Overfitting_Control.md`, active design docs, validation docs, config/comment scaffolds, guidebook, README, and operational memory files.
- Required tests: governance validator, documentation consistency checks, and comment-only scaffold validation after propagation.
- Completion criteria: affected docs and scaffolds consistently require split manifests, train-fold-only preprocessing, predeclared metrics, saved out-of-sample predictions, contamination blockers, and overfitting diagnostics without changing the approved benchmark family.
- Status: completed as design-contract propagation only; later stage conversions enforce the portions explicitly implemented through Stage 8 while any remaining scaffolded contracts stay pending.

## Stage 1: Raw Data Security And Coverage Audit

- Objective: make raw provider state safe and benchmark-auditable.
- Dependencies: Stage 0B.
- Files involved: `data/raw/alphavantage/`, `data/manifests/`, `docs/db_Testing.md`, `docs/Data_Update_Strategy.md`.
- Required tests: raw JSON parse checks, top-50 coverage check, truncation summary, credential-leak check for ledgers.
- Completion criteria: canonical raw status documented, provider-limit risks recorded, API-key-bearing ledger persistence sanitized or isolated.
- Status: completed as raw audit with limitations; active raw Twelve Data full-window files now cover the approved top-50 plus SPY support from 2010 where provider/listing history exists, no post-first-available-date OHLCV gaps are detected, a quarterly Alpha Vantage truncation-refinement script exists, and latest Stage 2 reconciliation treats current Alpha Vantage news as usable with visible truncation limitation flags while preserving no provider-level article-completeness claim.

## Stage 2: Dataset Contract Definition

- Objective: define the canonical benchmark dataset artifact and validation contract.
- Dependencies: Stage 1, Stage 0B, approved clean historical window.
- Files involved: future `src/` dataset modules, future `configs/`, `docs/db_Testing.md`, `docs/Pipeline_Testing.md`.
- Required tests: dataset schema checks, row-universe checks, no-news encoding checks, row-identity checks, split-role checks, and split-boundary checks.
- Completion criteria: dataset manifest format and acceptance checks are documented and implemented.
- Status: materialized for the approved top-50 Stage 2 row universe. The active dataset root is `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/`, with partitioned Parquet panel rows, dataset manifest, row-universe digest, clean-window record, CVX derived patch manifest, executable Stage 2 tests, and completion validation. Stage 3 through Stage 6 artifacts now consume this row universe.

## Stage 3: Feature And Label Pipeline

- Objective: build market features, event-state features, and forward excess-return labels.
- Dependencies: Stage 2.
- Files involved: future `src/features/`, future `src/labels/`, future tests.
- Required tests: horizon-label checks, alignment checks, missing-data behavior checks.
- Completion criteria: feature/label outputs match documented contracts and can be reproduced.
- Status: materialized for the approved Stage 2 dataset. `docs/agent/agent_log/Stage3_Materialization_2026-05-15.md` and `data/manifests/stage3_completion_validation_2026-05-15.json` confirm market features, event-state features, aligned news, and leave-one-out universe excess-return labels exist with the Stage 2 row-universe digest. Stage 4 owns split evidence, Stage 5 owns model-output evidence, and Stage 6 owns metric/reporting evidence.

## Stage 4: Split And Benchmark Runner

- Objective: implement purged-plus-embargoed walk-forward splits, lockbox handling, and reproducible run packets.
- Dependencies: Stage 3.
- Files involved: `src/event_state_forecasting/split/`, `src/event_state_forecasting/benchmark/`, `configs/splits.yaml`, `configs/artifact_packet.yaml`, `docs/Benchmark_Testing.md`.
- Required tests: fold leakage checks, purge/embargo accounting checks, lockbox isolation checks, saved-prediction checks, artifact completeness checks, repeatability checks.
- Completion criteria: split and gate-safe packet infrastructure exists; the Stage 6 serious-run packet now passes after Stage 5 and Stage 6 artifacts supplied preprocessing, saved predictions, metrics, diagnostics, and comparison summary.
- Status: materialized for the approved Stage 3 artifact. `docs/agent/agent_log/Stage4_Split_And_Packet_Materialization_2026-05-15.md` and `data/manifests/stage4_completion_validation_2026-05-15.json` confirm 9 monthly development folds, 60-trading-date purge/embargo, final 20% lockbox from `2025-09-30` through `2026-02-13`, passed leakage validation, passed Stage 4 pre-model packet validation, and a gate-safe runner check. Stage 5 model/preprocessing/saved-prediction artifacts and Stage 6 reporting artifacts now consume these splits.

## Stage 5: Models And Comparator Ladder

- Objective: implement the frozen market-only and event-state comparator ladder.
- Dependencies: Stage 4 and frozen comparator roster.
- Files involved: `src/event_state_forecasting/models/`, `src/event_state_forecasting/cli/train_models_and_predict.py`, `configs/models.yaml`, `tests/models/`, and `scripts/validate_stage5_completion.py`.
- Required tests: model smoke tests, train-fold-only preprocessing checks, identical-row comparison checks, and saved out-of-sample prediction checks.
- Completion criteria: approved comparator ladder can run on the same dataset and splits, preprocessing fits are recorded fold-locally, and validation plus lockbox saved predictions are materialized without computing metrics.
- Status: materialized for the approved Stage 4 artifact. `docs/agent/agent_log/Stage5_Model_And_Prediction_Materialization_2026-05-21.md` and `data/manifests/stage5_completion_validation_2026-05-21.json` confirm 8 model IDs, 360 model-fit records, 360 preprocessing-fit records, and 2088000 saved prediction rows. Stage 5 did not compute metrics by itself; Stage 6 reporting now consumes these saved predictions.

## Stage 6: Serious Benchmark Reporting

- Objective: run the approved benchmark family and report positive, conditional positive, or clean null outcomes.
- Dependencies: Stages 0-5 complete, including Stage 5 saved predictions.
- Files involved: `configs/evaluation.yaml`, `src/event_state_forecasting/evaluation/`, `src/event_state_forecasting/cli/run_benchmark.py`, `tests/evaluation/`, `scripts/validate_stage6_completion.py`, `data/benchmark_runs/phase1_top50/`, and `docs/Benchmark_Testing.md`.
- Required tests: metric contract tests, final validation packet review, lockbox integrity check, overfitting diagnostic review, and benchmark comparability review.
- Completion criteria: serious-run artifact packet exists, required overfitting diagnostics are reported, and no critical benchmark comparability contradiction remains.
- Status: materialized for the approved Stage 5 saved predictions. `docs/agent/agent_log/Stage6_Serious_Benchmark_Reporting_2026-05-21.md` and `data/manifests/stage6_completion_validation_2026-05-21.json` confirm `800` metric rows, `800` ranking diagnostic rows, `800` paired comparison rows, a passed serious packet, result class `clean_null`, and comparability classification `limitation_bearing`.

## Post-Stage-6 Operations

- `ExecutionPipeline.md` defines the documentation-first methodology for rerunning from Stage 2 through Stage 6 after approved new data, truncation refinement, or implementation changes.
- `UsageManual.md` defines the local command/artifact usage manual for invoking implemented stages and reading their inputs and outputs.
- `docs/Prompts/Stage7APrompt.md` has been executed as a research-only contextual-bandit feasibility study documented in `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md`.
- `docs/Prompts/Stage7BPrompt.md` has been executed as decision collection; `ScopeDecisionLog.md` records `S7B-DQ-001` through `S7B-DQ-010` as answered.
- `docs/Prompts/Stage7CPrompt.md` has been executed as diagnostics-only implementation and documentation integration. It produced Stage 7 config/code/tests, a final-execution stub, a Twelve Data raw update, updated Stage 2/3/4/5 artifacts for the refreshed window, and a Stage 7 post-lockbox diagnostic artifact with `benchmark_claim=false`.
- `docs/Prompts/Stage8Prompt.md` has been executed as plan-first daily/weekly raw update script implementation. It produced local Alpha Vantage news and Twelve Data OHLCV wrappers, shared safety helpers, and tests; it did not execute provider calls, overwrite raw files, rebuild benchmark artifacts, or create a benchmark/result/trading claim.
- `docs/Prompts/Stage9Prompt.md` has been executed as documentation and operational-memory reconciliation after Stage 8. It did not write feature code, execute provider calls, mutate raw data, rerun benchmarks, or change result interpretation.
- `docs/Prompts/Stage10APrompt.md` has been executed as research-only update-to-prediction and visualization workflow analysis documented in `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`. It did not implement orchestration, create prediction/visualization artifacts, call providers, or create service/API/trading scope.
- `docs/Prompts/Stage10BPrompt.md` has been executed as decision-comparison and approval capture documented in `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md` and `ScopeDecisionLog.md` entries `S10B-DQ-001` through `S10B-DQ-010`, all now answered. It did not implement orchestration, create prediction/visualization artifacts, call providers, or create service/API/trading scope.
- `docs/Prompts/Stage10CPrompt.md` has been executed as a local saved-prediction extraction packet implementation. It produced Stage 10C code/tests, a CLI, a packet validator, and a validated local artifact under `data/prediction_outputs/phase1_top50/`; it did not call providers, mutate raw data, create a persisted inference package, create service/API/dashboard scope, reinterpret Stage 6, promote benchmark comparability, or produce trading signals.
- `docs/Prompts/Stage11Prompt.md` and `docs/Prompts/Stage12Prompt.md` define proposed future prompt workflows only. They do not execute holistic audits, DeepResearch prompt maintenance, provider calls, user-facing API/service work, or benchmark-family changes by themselves.

## Stage 7-12 Prompt And Research Status

| Proposed stage | Purpose | Status |
| --- | --- | --- |
| Stage 7A | Contextual-bandit feasibility research for daily, news-days-only, historical replay ideas. | Executed research-only; memo at `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md`; no implementation. |
| Stage 7B | Decision matrix for any contextual-bandit protocol. | Executed and answered; `ScopeDecisionLog.md` records all 10 Stage 7B decisions. |
| Stage 7C | Contextual-bandit diagnostics, docs, and final-execution stub after approved decisions. | Executed diagnostics-only; new post-lockbox holdout artifact validated with `benchmark_claim=false`. |
| Stage 8 | Plan-first daily/weekly news and OHLCV update scripts. | Executed as local scripts/tests only; no live provider calls or raw overwrites. |
| Stage 9 | Final documentation reconciliation after approved future work. | Executed documentation-only after Stage 8; no code/provider/raw/benchmark changes. |
| Stage 10A | Research local update-to-prediction outputs and visualization. | Executed research-only; memo at `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`; no implementation/provider/output artifacts. |
| Stage 10B | Decision matrix for Stage 10 development. | Executed as decision-comparison and approval capture; memo at `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`; `S10B-DQ-001` through `S10B-DQ-010` are answered. |
| Stage 10C | Local development/testing for prediction outputs and visualization packet artifacts. | Executed as local saved-prediction extraction packet implementation; validated with `scripts/validate_stage10c_completion.py`. |
| Stage 11 | Holistic repo/model/state-of-art audit and improvement research. | Prompt-only, not executed. |
| Stage 12 | Maintenance of Stage 10 DeepResearch chat topic prompts. | Prompt-only, not executed. |
