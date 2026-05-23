# Stage10BPrompt

Status: executed on 2026-05-23 as a decision-comparison and approval-capture stage. Stage 10B produced `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`, and `S10B-DQ-001` through `S10B-DQ-010` are now answered in `ScopeDecisionLog.md`; it does not authorize implementation, provider calls, raw-data mutation, prediction-output artifacts, visualization artifacts, user-facing service/API/dashboard scope, trading signals, Stage 6 reinterpretation, or benchmark-comparability promotion.

## Mission

Present a concrete decision matrix for Stage 10C development after Stage 10A research. Do not implement code or assume approval by silence.

## Required Context To Read First

| File | Why |
| --- | --- |
| `Stage10APrompt.md` | Research scope and required handoff. |
| Stage 10A research memo, if it exists | Candidate designs and risks. |
| `Stage8Prompt.md` | Raw data update script boundary. |
| `ExecutionPipeline.md` | Stagewise rebuild process. |
| `UsageManual.md` | Existing command usage and artifact interface. |
| `AgentRules.md` | Approval and decision-presentation rules. |
| `docs/agent/AgentTemplates.md` | Decision matrix expectations. |
| `ScopeDecisionLog.md` | Protected scope. |
| `docs/Data_Update_Strategy.md` | Data invalidation rules. |

## Decisions To Present

| Decision | Candidate options to compare |
| --- | --- |
| Orchestration | Manual documented sequence; single local CLI wrapper; scheduled task wrapper. |
| Data refresh | Consume Stage 8 outputs only; directly invoke update scripts; require user-supplied raw cutoff. |
| Prediction method | Full Stage 2-6 rebuild; Stage 5 saved-prediction extraction only; new persisted-model inference package. |
| Output folder | `data/prediction_runs/<date>/`; `runs/predictions/<timestamp>/`; under Stage 6 artifact root. |
| Output files | CSV/Parquet predictions; JSON manifest; HTML report; static images; news context file. |
| Visualization technology | Static HTML with embedded tables; matplotlib PNGs; notebook; local dashboard only if explicitly approved. |
| Top-10 rule | Per horizon by event-state score; per horizon by delta over market hurdle; combined score with clear caveats. |
| News relevance | Aligned-news recency/count/sentiment fields; deterministic text snippets; optional future LLM summary only after approval. |
| Trajectory graph | Last-month predictions plus realized labels where available; price history plus forecast markers; horizon fan chart. |
| Claim wording | Forecast artifact only; research diagnostic; no buy/sell/price-target claim. |

## Required Matrix Columns

| Column | Meaning |
| --- | --- |
| Correctness | Fit with current artifacts and data contracts. |
| Leakage/comparability risk | Risk of contaminating Stage 6 or new runs. |
| Usability | How easy it is for the user to run and inspect. |
| Maintenance cost | Added code/test/doc burden. |
| Dependencies | New packages or external tools required. |
| Recommended option | Clear recommended choice. |

## Outputs

| Output | Required contents |
| --- | --- |
| Stage 10 decision memo | Table of options and recommendations. |
| Approval checklist | Exact choices the user must approve before Stage 10C. |
| Implementation boundary | What Stage 10C may and may not change. |
| Test plan sketch | Required tests and validation commands. |

## Stop Conditions

Stop and ask if the user wants a web service, live inference API, live trading integration, buy/sell recommendation, provider change, target change, or metric/result-policy change.

## Final Response Requirements

If executed later, present the decision matrix and request explicit approval for the complete Stage 10C development bundle.
