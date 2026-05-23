# Stage11Prompt

Status: proposed prompt only, not executed. Stage 11 is a holistic audit and improvement-research prompt after Stage 10C, not an implementation prompt.

## Mission

Audit the repository, current model behavior, benchmark evidence, usability, local output artifacts, and state-of-the-art gaps after Stage 10C. Research possible improvements for accuracy, usability, continued learning, buy/sell target methodology, Yahoo News integration, local LLM/DeepSeek-style processing, and stronger training/benchmarking controls. Do not implement code, call providers, generate new artifacts, or change benchmark interpretation.

## Required Background Files To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Review and research-response requirements. |
| `docs/agent/AgentResearchWorkflows.md` | Research workflow authority. |
| `ScopeDecisionLog.md` | Protected phase-1 scope and approval gates. |
| `ResearchTruth.md` | Current truth synthesis and unresolved risks through Stage 10C. |
| `ProjectDefinition.md` | Project responsibilities and boundaries. |
| `docs/Benchmark_Testing.md` | Benchmark evidence and comparability rules. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Overfitting and leakage controls. |
| `ExecutionPipeline.md` | Current rebuild methodology. |
| `UsageManual.md` | Current local usage manual, command inputs/outputs, artifact interfaces, and limitations. |
| `Complete_guidebook.txt` | Full repository map. |
| `Stage2Prompt.md` through `Stage6Prompt.md` and matching validation reports | Current benchmark implementation and evidence history. |
| `Stage7CPrompt.md` and `data/manifests/stage7_post_lockbox_completion_validation_2026-05-22.json` | Current contextual-bandit diagnostic boundary and post-lockbox evidence. |
| `Stage8Prompt.md` and `docs/Data_Update_Strategy.md` | Plan-first update scripts, provider-call boundaries, and rebuild invalidation rules. |
| `Stage9Prompt.md` and `docs/agent/agent_log/Current_State.md` | Documentation-reconciliation boundary and current operational memory. |
| `Stage10APrompt.md` and `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md` | Research-only update-to-prediction workflow analysis. |
| `Stage10BPrompt.md` and `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md` | Decision matrix and Stage 10C design constraints. |
| `Stage10CPrompt.md` and `data/manifests/stage10c_completion_validation_2026-05-23.json` | Implemented Stage 10C packet boundary, validation, and non-claims. |

## Current Baseline To Preserve

| Area | Current fact |
| --- | --- |
| Stage 6 result | `clean_null` with `limitation_bearing` comparability; do not reframe as positive or invalidated without new approved evidence. |
| Stage 7C | Diagnostic contextual-bandit artifacts exist; no live buy/sell signals, all-data final-execution training output, or Stage 6 reinterpretation. |
| Stage 8 | Plan-first daily/weekly raw update scripts exist; live `--execute`, raw overwrites, and downstream rebuilds remain approval-gated. |
| Stage 10C | Local prediction-output packet exists under `data/prediction_outputs/phase1_top50/...` from existing Stage 5 saved predictions. |
| Stage 10C row role | Current rows are `historical_prediction`; `forecast_candidate` semantics for future feature-only rows remain unapproved. |
| Deployment | Local CLI/artifact research system only; no live inference API, service, dashboard, or trading execution scope. |

## Audit Topics

| Topic | Required handling |
| --- | --- |
| Current behavior | Describe what the repo can and cannot do now through Stage 10C, with file/artifact references. |
| Current performance | Summarize Stage 6 `clean_null` result without reframing it as positive, trading-relevant, or benchmark-invalidated. |
| Accuracy improvements | Research feature, model, data, label, evaluation, and ensembling improvements. |
| Usability improvements | Research local run orchestration, Stage 10C packet/report usability, docs, and visualization refinements. |
| Continued learning | Assess safe rolling updates, retraining cadence, drift monitoring, and Stage 8 refresh impacts without lockbox leakage. |
| Buy/sell target methodology | Explain what would be required to move from excess-return forecasts to price targets or decisions. |
| Yahoo News scraping | Research feasibility, terms/robots/legal fragility, schema compatibility, and provider-comparability impact. |
| Local AI processing | Assess local LLM/DeepSeek-style summarization or embedding feasibility, GPU limits, reproducibility, and leakage risks. |
| Memorization controls | Research stronger temporal validation, embargo, duplicate news detection, text leakage, and model-selection controls. |
| Stage 10C extensions | Identify what would be required for persisted inference packaging, true future forecast rows, richer news/trajectory displays, or scheduled update-to-output workflows. |

## Outputs

| Output | Required contents |
| --- | --- |
| Audit report | Current-state findings with file/artifact references. |
| Improvement backlog | Prioritized research/development opportunities. |
| Approval-gated items | Explicit list of changes needing user approval. |
| Risk register | Leakage, provider, legal, hardware, benchmark, and usability risks. |
| Suggested next prompts | If needed, propose future prompt files or decision bundles. |
| Non-claims | Explicitly preserve no trading advice, no benchmark promotion, no Stage 6 reinterpretation, no provider-completeness claim, and no future-inference claim for current Stage 10C packets. |

## Stop Conditions

Stop and ask before scraping a new provider, recommending ToS-sensitive collection as implementation, calling live providers, changing provider stack, changing protected target/horizon/universe/evaluation scope, generating new prediction artifacts, implementing persisted inference packaging, introducing `forecast_candidate` semantics, making buy/sell advice, or selecting a model improvement that changes benchmark comparability.

## Final Response Requirements

If executed later, present findings first, then prioritized improvements, approval gates, validation needs, and recommended next steps.
