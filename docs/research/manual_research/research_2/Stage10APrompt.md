# Stage10APrompt

Status: executed on 2026-05-22 as research-only update-to-prediction and visualization workflow analysis. Stage 10A produced `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md` and does not authorize implementation, provider calls, raw-data mutation, prediction outputs, visualization artifacts, user-facing service/API scope, trading signals, Stage 6 reinterpretation, or benchmark-comparability promotion.

## Mission

Research a local, artifact-driven workflow that can update raw data daily or weekly, rebuild required stages, produce dated prediction outputs, and visualize top-10 forecast candidates across all horizons with relevant news context. Do not implement code, run provider calls, or create user-facing service/API scope.

## Required Context To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Approval gates and protected-scope discipline. |
| `ExecutionPipeline.md` | Existing stagewise rebuild methodology. |
| `UsageManual.md` | Current command/artifact usage and live-inference absence. |
| `docs/Data_Update_Strategy.md` | Refresh and invalidation rules. |
| `Stage8Prompt.md` | Future update-script boundary. |
| `ScopeDecisionLog.md` | Protected phase-1 benchmark shape. |
| `ResearchTruth.md` | Current evidence and non-claims. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Row identity, preprocessing, saved predictions, and lockbox rules. |
| `configs/models.yaml` | Current model roster and event-state model. |
| `configs/evaluation.yaml` | Current metric/result policy. |

## Research Questions

| Question | Required handling |
| --- | --- |
| Update-to-prediction workflow | Compare full Stage 2-6 rebuild, incremental data refresh plus full rebuild, and separate inference artifact generation. |
| Dated output folder | Propose deterministic folder naming by run date, data cutoff, dataset version, and row digest. |
| Prediction output | Define schema for ticker, date, horizon, model, predicted forward excess return, rank, and limitations. |
| Visualization | Compare static HTML, PNG/CSV bundle, notebook, and local dashboard options. |
| Top-10 views | Define per-horizon and cross-horizon ranking views without trading-profitability claims. |
| Relevant news | Research deterministic selection from aligned news rows, not local LLM summarization by default. |
| Prediction trajectory graph | Define how to show last-month observed/predicted series and future forecast points without pretending future realized prices exist. |
| Model serving | Assess whether current Stage 5 artifacts are enough or whether persisted fitted-model packaging is required. |

## Outputs

| Output | Required contents |
| --- | --- |
| Research memo | Feasible workflow options, risks, and recommended decision topics. |
| Artifact proposal | Candidate output folder schema and file list. |
| Visualization proposal | View types, dependencies, and accessibility/offline constraints. |
| Stage 10B handoff | Decisions requiring user approval before development. |

## Stop Conditions

Stop and ask before recommending a web service, live trading interface, provider change, protected-scope change, metric/result-policy change, or any interpretation that treats predictions as buy/sell advice.

## Final Response Requirements

If executed later, report research findings, candidate architectures, top risks, recommended Stage 10B decisions, and explicit non-claims.
