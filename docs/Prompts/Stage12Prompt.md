# Stage12Prompt

Status: proposed prompt only, not executed. Stage 12 is an umbrella prompt for maintaining DeepResearch chat topic prompts related to post-Stage-10C research.

## Mission

Create, update, or validate `DeepResearch_Chat_Topic_<Topicname>.md` files that can be pasted into a deep-research chat for post-Stage-10C topics. The topic prompts must be repository-grounded, citation-seeking, and explicit that they do not execute code or change project scope.

## Required Context To Read First

| File | Why |
| --- | --- |
| `Stage10APrompt.md` | Defines Stage 10 research questions. |
| `Stage10BPrompt.md` | Defines decisions that research should inform. |
| `Stage10CPrompt.md` | Defines implemented local packet boundary, validation expectations, and remaining exclusions. |
| `ExecutionPipeline.md` | Current rebuild workflow. |
| `UsageManual.md` | Current local usage manual, command inputs/outputs, and artifact interface. |
| `docs/Data_Update_Strategy.md` | Refresh/invalidation constraints. |
| `ScopeDecisionLog.md` | Protected scope. |
| `ResearchTruth.md` | Current truth and non-claims. |
| `data/manifests/stage10c_completion_validation_2026-05-23.json` | Current Stage 10C validation evidence. |

## Topic Prompt Requirements

| Requirement | Required handling |
| --- | --- |
| Repository context | Include current Stage 2-10C status, Stage 10C packet baseline, local CLI/artifact boundary, and no live inference API. |
| Research ask | Ask for cited external research, comparable tools, risks, and implementation tradeoffs. |
| Protected scope | State that target, horizons, universe, providers, Stage 6 result, and Stage 10C packet non-claims cannot be changed by research. |
| Output format | Request concise options, recommended choice, risks, and validation implications. |
| Non-execution | State that the deep-research chat does not run code, fetch provider data, or approve implementation. |

## Current Post-Stage-10C Topic Files

| Topic prompt | Purpose |
| --- | --- |
| `DeepResearch_Chat_Topic_Update_To_Prediction_Pipeline.md` | Research local update-to-prediction orchestration. |
| `DeepResearch_Chat_Topic_Daily_Weekly_Data_Refresh.md` | Research safe daily/weekly raw update design. |
| `DeepResearch_Chat_Topic_Top10_Multi_Horizon_Visualization.md` | Research top-10 model-output visualization approaches. |
| `DeepResearch_Chat_Topic_Relevant_News_Attribution.md` | Research deterministic relevant-news selection and explanation. |
| `DeepResearch_Chat_Topic_Prediction_Trajectory_Graphs.md` | Research observed-history plus prediction-marker trajectory displays. |

## Stop Conditions

Stop and ask before adding topic prompts that introduce a new provider, user-facing service/API, trading advice, buy/sell target claim, protected-scope change, forecast-row semantic change, persisted inference packaging, or benchmark-comparability change without explicit approval.

## Final Response Requirements

If executed later, report topic prompt files created or changed, the post-Stage-10C questions they support, and validation/doc-index updates.
