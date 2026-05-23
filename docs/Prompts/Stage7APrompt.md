# Stage7APrompt

Status: executed research-only on 2026-05-22. Stage 7A produced `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md` after the completed Stage 6 clean-null benchmark packet; it created no implementation, training run, provider call, data mutation, benchmark rerun, or Stage 6 reinterpretation.

## Mission

Research whether a contextual-bandit layer is scientifically appropriate for the existing historical event-state forecasting artifacts, especially a last-year, news-days-only daily update simulation. Do not write implementation code, run training, alter data, or reinterpret Stage 6.

## Ownership

| Area | Owner |
| --- | --- |
| Research synthesis | Agent. |
| Protected benchmark changes | User approval required before any change. |
| Contextual-bandit design choices | User after Stage 7B decision matrix. |
| Stage 6 interpretation | Frozen evidence; not owned by Stage 7A. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Approval gates and benchmark-integrity rules. |
| `docs/agent/AgentResearchWorkflows.md` | Research workflow and comparison expectations. |
| `ScopeDecisionLog.md` | Protected target, providers, universe, and evaluation doctrine. |
| `ResearchTruth.md` | Current truth, limitations, and non-claims. |
| `ProjectDefinition.md` | Benchmark-family boundary and project responsibilities. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Lockbox, saved-prediction, and overfitting-control constraints. |
| `docs/Benchmark_Testing.md` | Serious-run and comparability rules. |
| `Stage6Prompt.md` | Current result packet and locked Stage 6 interpretation. |
| `configs/models.yaml` | Current model roster and event-state model ID. |
| `configs/evaluation.yaml` | Current metric/result policy. |

## Research Questions

| Question | Required handling |
| --- | --- |
| Contextual bandit fit | Explain whether contextual bandits are suitable for daily ticker-ranking or allocation decisions from historical saved predictions/features. |
| Action space | Identify feasible actions such as choose ticker, choose top-k basket, choose horizon-specific rank, or abstain/cash. |
| Reward definition | Compare reward choices that preserve forward excess-return target semantics without trading-profitability claims. |
| Online update simulation | Define what daily updates mean in historical replay and where leakage can enter. |
| News-days-only filter | Evaluate the scientific cost of using only rows with aligned news and how it changes comparability. |
| Last-year testing | Explain why using the final lockbox for development would be forbidden unless a new benchmark family is approved. |
| Offline evaluation | Compare replay, inverse-propensity, doubly robust, and simple historical-policy diagnostics, noting missing logged propensities. |
| Baselines | Identify market-only, supervised-ranking, and random/epsilon baselines needed before claiming any bandit value. |

## Outputs

| Output | Required contents |
| --- | --- |
| Research memo | Methods, assumptions, leakage risks, and feasibility conclusion. |
| Design option inventory | Algorithms, action spaces, rewards, update cadences, and evaluation options. |
| Hard blockers | Missing logged propensities, data separation conflicts, or comparability breaks. |
| Stage 7B input | A short list of decisions that must be compared before development. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Reconstruct current Stage 6 state and protected scope. | Scope checkpoint. |
| 2 | Search current repo for existing bandit/RL implementation. | Implementation reality note. |
| 3 | Research contextual-bandit approaches for financial ranking/allocation under historical replay. | Method summary. |
| 4 | Map candidate methods to current artifacts: Stage 3 features, Stage 4 splits, Stage 5 predictions, Stage 6 metrics. | Feasibility matrix. |
| 5 | Identify leakage, lockbox, and news-days-only comparability risks. | Risk register. |
| 6 | Draft Stage 7B decision questions without selecting choices. | Decision handoff. |
| 7 | Update memory only if Stage 7A is actually executed later. | Evidence log. |

## Validation Strategy

| Check | Required result |
| --- | --- |
| Repository-first check | Do not claim existing bandit/RL code unless current files prove it. |
| Scope check | No change to target, horizons, universe, providers, or Stage 6 result policy. |
| Lockbox check | No proposal may use the Stage 6 lockbox for design iteration without declaring a new benchmark family. |
| Claim check | No trading-profitability or positive-result claim. |

## Stop Conditions

Stop and ask before recommending lockbox reuse for daily learning, changing the reward target, dropping no-news rows as if comparable to Stage 6, adding a new provider, changing universe size, introducing trading costs as primary evidence, or claiming contextual-bandit performance without a predeclared evaluation protocol.

## Final Response Requirements

If executed later, report research sources, feasible options, non-feasible options, leakage risks, required Stage 7B decisions, and explicit non-claims.
