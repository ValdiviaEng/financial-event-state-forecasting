# Stage7CPrompt

Status: executed diagnostics-only on 2026-05-22 after explicit user approval. This file remains the implementation-capable Stage 7C prompt, but the active execution produced Stage 7 code/config/tests/validators/artifacts, an approved Twelve Data update, refreshed Stage 2/3/4/5 artifacts, and a post-Stage-6-lockbox Stage 7 diagnostic artifact with `benchmark_claim=false`. All-data final-execution training-output and live trading signals remain unapproved.

## Execution Gate

Only execute this prompt if the user explicitly says to execute Stage 7C or otherwise explicitly approves Stage 7C implementation. A request to edit this prompt is not execution approval.

When executed later, Stage 7C may implement code, configs, tests, validators, benchmark diagnostics, documentation, and a separate final-execution pipeline according to the decisions below. Provider calls, approved-new-data updates, benchmark reruns, policy training, and final-execution training are allowed only if the future execution request explicitly includes those actions or grants approval broad enough to cover them.

## Mission

Implement Stage 7 as a contextual-bandit benchmark and final-execution-capable extension without changing the completed Stage 6 result. Stage 7C must produce transparent code, configs, artifacts, validators, documentation, and tests for the approved Stage 7 protocol.

The benchmark pipeline must prove and diagnose safely. The final execution pipeline must remain separate and may later train on all approved historical data for live-use predictions after benchmark choices are frozen. Final-execution outputs are not benchmark evidence.

## Non-Negotiable Boundaries

| Boundary | Required handling |
| --- | --- |
| Stage 6 result | Preserve `clean_null` and `limitation_bearing`; do not reinterpret Stage 6. |
| Current Stage 6 lockbox | Do not use `2025-09-30` through `2026-02-13` for Stage 7 design/tuning/debugging. |
| Stage 7 final evidence | Use a new post-lockbox holdout only after approved data update and predeclared Stage 7 split/holdout policy. |
| Data mutation/provider calls | Stop unless future user execution approval explicitly includes data update/provider-call work. |
| Raw news/LLM context | Out of scope unless separately approved. |
| Trading claims | No live buy/sell, shorting, investable-signal, cost-adjusted trading, portfolio, or profitability claim. |
| Bottom-k wording | Treat as downside/avoid diagnostic candidates, not live sell recommendations. |
| Off-policy claims | No real logged-policy IPW/DR claim without logged behavior actions and propensities. |
| Final execution | Separate namespace/artifacts from benchmark evidence; all-data final-execution training does not prove accuracy on its training rows. |

## Required Context To Read First

Read these before editing code or docs:

| File | Why |
| --- | --- |
| `AgentRules.md` | Governance, truth hierarchy, approval gates, benchmark integrity. |
| `docs/agent/AgentMemory.md` | Memory/logging/session reconciliation rules. |
| `docs/agent/AgentResearchWorkflows.md` | Research-heavy workflow and additive evidence rules. |
| `docs/agent/AgentTemplates.md` | Required decision/evidence structure and scoring conventions. |
| `ScopeDecisionLog.md` | Binding Stage 7B decisions and protected phase-1 scope. |
| `ResearchTruth.md` | Active truth, current limitations, and non-claims. |
| `ProjectDefinition.md` | Local artifact-driven research boundary and non-product scope. |
| `Stage7APrompt.md` | Stage 7A research-only mission. |
| `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md` | Feasibility conclusions, blockers, replay cautions. |
| `Stage7BPrompt.md` | Stage 7B decision-draft framing. |
| `docs/research_results/stage7b_contextual_bandit_decision_draft_2026-05-22.md` | Draft comparison evidence; superseded by answered `ScopeDecisionLog.md` decisions where they differ. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Lockbox, fold-local preprocessing, saved-prediction, and contamination rules. |
| `docs/Benchmark_Testing.md` | Serious-run comparability and result-policy rules. |
| `configs/models.yaml` | Stage 5 model roster, feature sets, saved-prediction schema. |
| `configs/evaluation.yaml` | Stage 6 metric policy and ranking diagnostics. |
| `docs/Execution_Plan.md` | Stage index and dependency order. |
| `docs/Detailed_Execution_Stages.md` | Granular stage status and prompt index. |
| `Complete_guidebook.txt` | Discoverability map. |
| `README.md` | Current state and safe command context. |

## Required Artifact Inputs

Use the current approved Stage 2 through Stage 6 artifacts as immutable inputs unless a future explicit data-update approval creates new Stage 7 artifacts.

| Artifact | Required use |
| --- | --- |
| Stage 3 features and labels | Source of frozen context columns and forward excess-return labels. |
| Stage 4 splits | Source of development-fold boundaries and current lockbox boundary. |
| Stage 5 saved predictions | Fold-safe prediction context and supervised-ranking baselines. |
| Stage 6 reports | Historical benchmark evidence only; not policy context and not Stage 7 tuning data. |

Current known artifact facts to preserve:

| Area | Fact |
| --- | --- |
| Target | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | Reproducible top-50 liquid large-cap set. |
| Providers | Twelve Data OHLCV, Alpha Vantage news, SEC static/company support only. |
| Alignment | Same-day as-of-close; after-hours and non-trading-day news roll forward. |
| Stage 3 | `117750` rows, `471` as-of dates, `46330` rows with aligned news, `71420` no-news rows, `59610` provider-truncation-risk rows. |
| Stage 4 | `9` development folds; lockbox `2025-09-30` through `2026-02-13`; `1059750` split-assignment rows. |
| Stage 5 | `8` model IDs; `2088000` saved validation/lockbox prediction rows; no train predictions. |
| Stage 6 | `800` metric rows; `800` ranking diagnostic rows; `800` paired-comparison rows; serious packet `passed`; result class `clean_null`; comparability `limitation_bearing`. |

## Approved Stage 7C Protocol

| Dimension | Approved value |
| --- | --- |
| Purpose | Direct contextual-bandit scope expansion beyond completed Stage 6. |
| Evaluation segment | New post-lockbox holdout after approved data update. |
| Design/replay span | Development-only rolling replay with learning curves; current Stage 6 lockbox excluded from design iteration. |
| Row filter | All eligible rows as primary evidence; news-days-only as secondary diagnostic. |
| Action space | Two-sided top-k per fixed horizon: top-k upside candidates and bottom-k downside/avoid candidates. |
| Basket sizes | Primary `k=5`; sensitivity diagnostics `k=3` and `k=10`; never choose best `k` from holdout results. |
| Reward | Two-sided forward-return package: top-k mean forward excess return, bottom-k mean forward excess return where lower is better, and secondary top-minus-bottom spread. |
| Algorithm flow | Supervised two-sided ranking diagnostics first, then epsilon-greedy regression/ranking as first adaptive bandit. |
| Epsilon policy | Primary `epsilon=0.05`; sensitivity diagnostics `epsilon=0.01` and `epsilon=0.10`; never choose best epsilon from holdout results. |
| Context | Combined frozen Stage 3 features plus fold-safe Stage 5 predictions. |
| Required ablation | Stage 5 predictions-only context. |
| Recommended ablation | Stage 3 features-only context if implementation budget allows. |
| Mandatory baselines | Full baseline bundle before any bandit-value claim. |
| Outputs | Saved benchmark diagnostics, Stage 7C docs, and separate final-execution pipeline implementation/stub. |

## Mandatory Baseline Bundle

Implement and save diagnostics for these baselines before any bandit-value claim:

| Baseline | Required purpose |
| --- | --- |
| Random top-k/bottom-k | Chance performance under exact eligibility, horizon, row-filter, and `k` rules. |
| Epsilon-random | Exploration-mechanics control for `epsilon=0.05` primary and `0.01`/`0.10` diagnostics. |
| Market-only ranker | Tests whether market features alone explain top/bottom decisions. |
| Stage 5 predictions-only supervised ranker | Tests whether saved supervised predictions alone provide the signal. |
| Combined Stage 3 plus Stage 5 supervised ranker | Static non-adaptive upper comparator before epsilon-greedy. |
| Static validation-selected rule | Applies a development-selected static rule unchanged to later replay/holdout. |

Do not include abstain/cash, cost-adjusted trading, portfolio, shorting, or live execution baselines unless separately approved.

## Required Metrics And Diagnostics

Every benchmark policy and baseline must report these diagnostics by horizon, fold/replay segment, row-filter track, and `k` where applicable:

| Metric group | Required fields |
| --- | --- |
| Top-k upside | Mean forward excess return of top-k selected names; standard error or dispersion; positive-rate diagnostic. |
| Bottom-k downside | Mean forward excess return of bottom-k selected names where lower is better; standard error or dispersion; negative-rate diagnostic. |
| Spread | Top-k mean minus bottom-k mean as separation evidence, not long-short trading PnL. |
| Ranking diagnostics | Rank correlation or rank-normalized diagnostics if feasible; keep raw forward-return metrics primary. |
| Sign diagnostics | Positive top-k hit rate and negative bottom-k hit rate as secondary diagnostics. |
| Learning curves | Performance before later periods and across rolling development replay. |
| Supervised overfitting | Fold-level train/validation gap only if Stage 7C creates fold-local train predictions; otherwise explicitly state blocked like Stage 6 train-gap limitation. |
| Row-filter split | All-row primary table and news-days secondary table. |
| Epsilon sensitivity | Primary `0.05`; diagnostics `0.01` and `0.10`. |
| K sensitivity | Primary `k=5`; diagnostics `k=3` and `k=10`. |

## Implementation Plan

Follow these phases in order when Stage 7C is executed later.

| Phase | Action | Required output |
| --- | --- | --- |
| 0 | Confirm explicit Stage 7C execution approval and scope. | Approval checkpoint in final response and memory. |
| 1 | Re-read context files and reconcile `ScopeDecisionLog.md` with this prompt. | Drift note if any decision conflicts. |
| 2 | Inspect existing code organization under `src/event_state_forecasting/`, `configs/`, `scripts/`, and `tests/`. | Minimal implementation map. |
| 3 | Add Stage 7 config, likely `configs/stage7_contextual_bandit.yaml` plus example if repository pattern requires it. | Config with schema version, artifact names, k, epsilon, contexts, baselines, metrics, non-claims. |
| 4 | Implement Stage 7 package, likely under `src/event_state_forecasting/stage7/` or another repo-consistent namespace. | Reusable modules for context assembly, eligibility, policy scoring, replay, metrics, artifacts, final execution. |
| 5 | Implement CLI entry points under `src/event_state_forecasting/cli/` for benchmark replay and final execution. | Local CLI commands; no service/API/dashboard. |
| 6 | Implement validator script, likely `scripts/validate_stage7_completion.py`. | Artifact and governance validation gate. |
| 7 | Add focused tests under `tests/` for leakage, delayed rewards, k/epsilon behavior, baselines, metrics, artifact schema, and final-execution separation. | Passing pytest coverage for Stage 7 behavior. |
| 8 | Implement saved benchmark diagnostics and manifests under a Stage 7 artifact root. | Artifact packet with configs, context schema, policy outputs, baseline outputs, metrics, validation evidence. |
| 9 | Implement final-execution pipeline in a separate namespace/artifact root. | All-data live-use training/output capability, clearly labeled non-benchmark evidence. |
| 10 | Update active docs and guidebook. | `ResearchTruth.md`, execution docs, benchmark docs, README/guidebook/indexes as needed. |
| 11 | Run validations and focused tests. | Command output and artifact paths in final response. |

## Recommended Code Shape

Use the existing project style and choose minimal names. If the repo structure supports it, prefer these files:

| File or module | Purpose |
| --- | --- |
| `configs/stage7_contextual_bandit.yaml` | Primary Stage 7 config. |
| `configs/stage7_contextual_bandit.example.yaml` | Example config if examples are maintained. |
| `src/event_state_forecasting/stage7/context.py` | Load/validate Stage 3 features and Stage 5 prediction context. |
| `src/event_state_forecasting/stage7/eligibility.py` | Build eligible ticker-date-horizon rows and row-filter tracks. |
| `src/event_state_forecasting/stage7/policies.py` | Supervised ranking, random, epsilon-random, epsilon-greedy policies. |
| `src/event_state_forecasting/stage7/replay.py` | Development rolling replay and delayed-reward handling. |
| `src/event_state_forecasting/stage7/metrics.py` | Top-k, bottom-k, spread, sign, ranking, learning-curve metrics. |
| `src/event_state_forecasting/stage7/artifacts.py` | Manifest, artifact root, schema, digest, and packet helpers. |
| `src/event_state_forecasting/stage7/final_execution.py` | Separate all-data final-execution training/output path. |
| `src/event_state_forecasting/cli/run_stage7_contextual_bandit.py` | Benchmark replay CLI. |
| `src/event_state_forecasting/cli/run_stage7_final_execution.py` | Final-execution CLI, disabled unless approved/executed. |
| `scripts/validate_stage7_completion.py` | Stage 7 completion validator. |

If existing naming conventions suggest different names, follow the repository pattern and document deviations.

## Core Algorithm Requirements

| Requirement | Implementation detail |
| --- | --- |
| Horizon handling | Evaluate `1d`, `5d`, `10d`, `20d`, and `60d` separately unless config explicitly says otherwise. |
| Reward delay | A decision at date `t` for horizon `h` updates only after that horizon's forward return is observable; no immediate future-label updates. |
| Supervised-first gate | Save supervised ranking diagnostics before running epsilon-greedy diagnostics. |
| Epsilon-greedy | Primary `epsilon=0.05`; diagnostics `0.01` and `0.10`; deterministic seeds. |
| Basket size | Primary `k=5`; diagnostics `k=3` and `k=10`; deterministic tie-breaking. |
| Context availability | Every context column must be available as of the decision date and fold/replay state. |
| Prediction provenance | Stage 5 prediction context must be fold-safe/out-of-sample for benchmark evidence. |
| No holdout tuning | Never choose `k`, epsilon, context, policy, reward, or baselines using final holdout results. |
| No IPW/DR overclaim | Do not call simulated full-information replay a real logged-policy off-policy evaluation. |
| Final execution | Train on all approved historical data only after benchmark choices are frozen; label output as live-use/non-benchmark. |

## Artifact Requirements

Stage 7 benchmark artifacts must include:

| Artifact | Required contents |
| --- | --- |
| Config snapshot | Exact Stage 7 config, k/epsilon settings, seeds, policy roster, baselines, context columns. |
| Decision manifest | References to `S7B-DQ-001` through `S7B-DQ-010` and later `S7C-PARAM-001/002` prompt parameters. |
| Context manifest | Stage 3 feature columns, Stage 5 prediction columns, fold-time availability checks. |
| Replay manifest | Fold/replay periods, reward-delay policy, eligible rows, row-filter counts. |
| Policy outputs | Saved top-k and bottom-k selections for supervised, epsilon-greedy, and baselines. |
| Metrics tables | Top-k, bottom-k, spread, sign/ranking diagnostics, learning curves, sensitivity tables. |
| Baseline packet | Full baseline bundle outputs and provenance. |
| Validation report | Leakage, schema, counts, delayed-reward, and artifact-completeness checks. |
| Non-claim statement | No Stage 6 reinterpretation, no trading signal, no provider-completeness claim. |

Final-execution artifacts must live separately from benchmark artifacts and include:

| Artifact | Required contents |
| --- | --- |
| Final-execution config | Frozen benchmark choices transferred into all-data mode. |
| Training manifest | All approved historical data used, feature/prediction schema, model/policy state provenance. |
| Candidate output | Top-k upside and bottom-k downside/avoid candidates, labeled non-benchmark and non-trading-signal unless later approved. |
| Separation warning | Clear statement that all-data outputs are not accuracy evidence on their training rows. |

## Documentation Updates When Executed

Update active docs only after implementation or artifact changes exist:

| File | Required update |
| --- | --- |
| `ResearchTruth.md` | Stage 7 implementation status, artifacts, limitations, and non-claims. |
| `docs/Benchmark_Testing.md` | Stage 7 benchmark-family rules, metrics, baselines, and comparability separation. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Stage 7 leakage, delayed-reward, context, and final-execution separation controls. |
| `docs/Execution_Plan.md` | Stage 7C execution status and command references. |
| `docs/Detailed_Execution_Stages.md` | Granular Stage 7C status and dependencies. |
| `ExecutionPipeline.md` | Stage 7 benchmark and final-execution pipeline placement. |
| `UsageManual.md` | Local command/artifact usage only; no product/web/live inference API claim. |
| `Complete_guidebook.txt` | New Stage 7 files, configs, CLIs, artifacts, and validators. |
| `README.md` | High-level status only; preserve Stage 6 state and non-claims. |
| `docs/agent/agent_log/Current_State.md` and `Event_Ledger.ndjson` | Memory, event, validation, and drift records if Stage 7C is executed. |

## Validation Commands

Run applicable validations after implementation. Use repository conventions and add Stage 7 validators/tests as needed.

Baseline governance checks:

```powershell
python scripts/validate_agent_governance.py
```

```powershell
python scripts/validate_comment_only_scaffold.py
```

Ledger parse if memory is updated:

```powershell
python -c "import json, pathlib; p=pathlib.Path('docs/agent/agent_log/Event_Ledger.ndjson'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('EVENT_LEDGER_JSONL_VALID')"
```

Expected new Stage 7 validation:

```powershell
python scripts/validate_stage7_completion.py
```

Focused tests should include Stage 7 tests plus any touched existing tests. Use the repository's test command conventions; set `PYTHONPATH=src` when needed.

## Stop And Ask Conditions

Stop and ask before proceeding if any of these occur:

| Condition | Why |
| --- | --- |
| Stage 7C execution approval is ambiguous. | This prompt is implementation-capable but not self-executing. |
| Data update or provider calls are needed but not explicitly approved. | Avoids unauthorized data mutation/API use. |
| New post-lockbox holdout dates are not available but final holdout evaluation is requested. | Prevents fake holdout claims. |
| Required Stage 3/4/5 artifacts are missing or inconsistent. | Prevents silent protocol drift. |
| Stage 5 prediction provenance is not fold-safe for benchmark use. | Prevents leakage through prediction context. |
| You need to use the current Stage 6 lockbox for design/tuning/debugging. | Violates Stage 7B and Stage 6 separation. |
| Any result suggests changing `k`, epsilon, reward, context, or baselines after holdout inspection. | Prevents selection-on-results. |
| You need raw news text, LLM context, holdings, costs, or portfolio state. | Requires separate scope/design approval. |
| User asks for buy/sell/trading-signal language. | Not approved by Stage 7B/7C prompt. |
| Existing docs conflict with `ScopeDecisionLog.md`. | Decision log is binding and conflict must be resolved explicitly. |

## Final Response Requirements When Executed

Report:

| Item | Required detail |
| --- | --- |
| Execution scope | Confirm what was approved and executed. |
| Updated files | List code, config, docs, tests, scripts, and artifacts changed. |
| Stage 7 decisions reflected | Map implementation back to `S7B-DQ-001` through `S7B-DQ-010`, `S7C-PARAM-001`, and `S7C-PARAM-002`. |
| Artifact roots | Provide benchmark and final-execution artifact locations if created. |
| Metrics and baselines | Summarize what was computed; distinguish all-row primary and news-days secondary. |
| Non-claims | State no Stage 6 reinterpretation, no trading signal, no provider-completeness claim, and no real logged-policy IPW/DR claim. |
| Validation | Include commands run and pass/fail status. |
| Blockers | List remaining approvals or missing data, especially new post-lockbox holdout requirements. |

## Final Non-Claims For This Prompt

- This prompt file does not execute Stage 7C.
- This prompt file does not implement code by itself.
- This prompt file does not train a policy.
- This prompt file does not mutate data or call providers.
- This prompt file does not create a benchmark result.
- This prompt file does not approve live buy/sell signals.
- This prompt file does not change Stage 6 `clean_null` or `limitation_bearing`.
