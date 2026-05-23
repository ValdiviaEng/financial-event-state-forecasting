# Stage7BPrompt

Status: executed draft-only on 2026-05-22. Stage 7B produced `docs/research_results/stage7b_contextual_bandit_decision_draft_2026-05-22.md`; subsequent owner answers in `ScopeDecisionLog.md` resolved `S7B-DQ-001` through `S7B-DQ-010` and enabled the separately approved Stage 7C diagnostics implementation. The Stage 7B prompt itself created no provider call, data mutation, Stage 6 reinterpretation, live signal, all-data final-execution output, or comparability change.

## Mission

Convert Stage 7A contextual-bandit research into a user decision matrix. Do not implement models, write code, select a protocol silently, or change Stage 6 comparability.

## Required Context To Read First

| File | Why |
| --- | --- |
| `Stage7APrompt.md` | Defines the research-only scope and required handoff. |
| Stage 7A research memo, if it exists | Supplies options and blockers. |
| `AgentRules.md` | Approval-gate and decision-presentation rules. |
| `docs/agent/AgentTemplates.md` | Decision matrix expectations. |
| `ScopeDecisionLog.md` | Protected benchmark choices. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Data separation and lockbox constraints. |
| `docs/Benchmark_Testing.md` | Benchmark comparability and serious-run discipline. |
| `configs/models.yaml` | Current model roster and model-output assumptions. |
| `configs/evaluation.yaml` | Current metric/result policy. |

## Decisions To Present

| Decision | Candidate options to compare |
| --- | --- |
| Stage 7 purpose | Research diagnostic only; separate benchmark family; later production-style policy prototype. |
| Evaluation segment | Development folds only; new post-lockbox holdout after approved data update; separate sandbox using copied historical rows. |
| Row filter | All rows; news-days only with explicit non-comparability; two-track all-row plus news-days diagnostic. |
| Time span | Last 1 year sandbox; full clean window replay; development-only rolling replay. |
| Action space | Choose one ticker per day; choose top-k basket; choose horizon-specific model; choose abstain/cash. |
| Reward | Forward excess return by horizon; rank-normalized reward; sign hit; cost-adjusted exploratory diagnostic only. |
| Algorithm class | LinUCB; Thompson sampling; epsilon-greedy regression; non-bandit supervised ranking baseline. |
| Context | Stage 3 features only; Stage 5 predictions as context; combined feature and prediction context. |
| Baselines | Market-only policy; event-state supervised ranker; random policy; no-news abstain policy. |
| Output status | Research artifact only; saved policy diagnostics; future executable Stage 7C docs; no trading signal. |

## Required Matrix Columns

| Column | Meaning |
| --- | --- |
| Scientific validity | Whether the option can support a defensible claim. |
| Leakage risk | Likelihood of using future labels, lockbox feedback, or selected-on-results choices. |
| Comparability impact | Whether the option remains comparable to Stage 6 or becomes a new benchmark family. |
| Implementation complexity | Expected repo changes and test burden. |
| Data requirements | Required artifacts and missing evidence. |
| User value | Usefulness for later decisions. |
| Recommended choice | A clear recommendation, but no silent approval. |

## Outputs

| Output | Required contents |
| --- | --- |
| Decision memo | Concise comparison table and recommendation. |
| Approval request | Exact choices the user must approve before Stage 7C. |
| Non-approval list | Choices not approved by silence. |
| Blocker list | Any blocker that prevents contextual-bandit development. |

## Stop Conditions

Stop and ask if Stage 7A research is absent, if a candidate would reuse the Stage 6 lockbox for design tuning, if the user asks for a trading-profitability claim, or if selecting an option changes protected scope.

## Final Response Requirements

If executed later, present findings as a decision matrix with one recommended option per decision and ask the user to approve or modify the full decision bundle before any code or documentation integration.
