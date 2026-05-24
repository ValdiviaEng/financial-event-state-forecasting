# Stage10CPrompt

Status: executed on 2026-05-23 as a local CLI/artifact implementation for the Stage 10B-approved model-output packet workflow. The first implementation creates historical-prediction output packets from existing Stage 5 saved predictions; further persisted inference packaging, new `forecast_candidate` row semantics, live provider calls, service/API/dashboard scope, or trading signals still require separate explicit approval.

## Mission

After Stage 10A research and Stage 10B decisions, implement the approved local workflow for readable model-output artifacts, versioned dated output folders, top-10 multi-horizon views, deterministic relevant-news context, and static trajectory/report visualization. Preserve the local CLI/artifact boundary unless a separate approval authorizes service/API scope.

The completed Stage 10B decisions define the design constraints for the executed Stage 10C local packet path. Stage 10C did not authorize provider calls, raw-data mutation, persisted inference packaging, service/API/dashboard scope, trading signals, Stage 6 reinterpretation, or benchmark-comparability promotion.

## Required Context To Read First

| File | Why |
| --- | --- |
| `Stage10APrompt.md` | Research scope and risks. |
| `Stage10BPrompt.md` | Decision matrix and required approvals. |
| `ScopeDecisionLog.md` Stage 10B decision register and Stage 10C approval register | Defines Stage 10C design constraints, executed implementation boundary, and remaining approval gates. |
| `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md` | Records Stage 10B comparison rationale, selected options, non-claims, and validation expectations. |
| `Stage8Prompt.md` | Update-script boundary and provider-call rules. |
| `ExecutionPipeline.md` | Current Stage 2-6 rebuild sequence. |
| `UsageManual.md` | CLI usage, artifact roots, command inputs/outputs, and current limitations. |
| `docs/Data_Update_Strategy.md` | Invalidation and refresh policy. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Row identity and leakage controls. |
| `configs/models.yaml` | Current model IDs and branches. |
| `configs/evaluation.yaml` | Current metric policy and result non-claims. |

## Candidate Outputs

| Output | Required contents |
| --- | --- |
| Versioned output packet | Write under `data/prediction_outputs/phase1_top50/...` with manifest, input artifact identities, command record, data cutoff, source/row/model provenance, limitations, and output schema version. |
| Model-output table | Ticker, as-of date, horizon, model, branch, prediction, row role, rank, artifact versions, and limitation flags. Use `historical_prediction` or `diagnostic_only` where appropriate; reserve `forecast_candidate` for explicitly approved future-row or refreshed-artifact semantics. |
| Top-10 views | Separate per-horizon outputs for `1d`, `5d`, `10d`, `20d`, `60d`; event-state score is primary, market-hurdle delta is secondary, and cross-horizon score is tertiary diagnostic only. |
| Relevant news context | Deterministic aligned-news fields and limitation flags are required; deterministic snippets are optional only if validated; no LLM summaries for first implementation. |
| Static report and trajectory visualization | Static HTML plus CSV/Parquet packet; price/return history plus forecast markers as primary trajectory view, optional historical diagnostics where labels have elapsed, no projected price paths or fan charts. |
| Validation report | Full packet/report validation: manifest identity, source provenance, row universe, horizons, cutoff correctness, rank determinism, report consistency, non-claim wording, no-network/service behavior, and sensitive-artifact exclusion. |

## Implemented Scope And Re-Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Verify Stage 10C implementation approval, Stage 10B decisions, and no protected-scope drift. | Approval checkpoint. |
| 2 | Use `src/event_state_forecasting/stage10/prediction_outputs.py`, `src/event_state_forecasting/cli/generate_prediction_outputs.py`, and `scripts/validate_stage10c_completion.py`. | File plan. |
| 3 | Implement a single local artifact CLI that consumes explicit artifact roots and data cutoffs without provider calls, raw overwrites, hidden Stage 2-6 reruns, scheduler behavior, or service/API/dashboard behavior. | Local CLI or script. |
| 4 | Implement top-10 table generation for all horizons using the approved primary/secondary/tertiary ranking semantics. | Tables and tests. |
| 5 | Implement deterministic relevant-news extraction from already-aligned local artifacts. | News context artifacts. |
| 6 | Implement approved static HTML plus CSV/Parquet report output and trajectory markers. | Static packet/report artifacts. |
| 7 | Add tests for schemas, rankings, version identities, and no leakage. | Executable tests. |
| 8 | Update docs, guidebook, and memory. | Discoverability and evidence. |
| 9 | Run full validations, including `tests/stage10` and `scripts/validate_stage10c_completion.py`. | Validation output. |

## Validation Strategy

| Test | Required result |
| --- | --- |
| Unit tests | New prediction-output and visualization contracts pass. |
| Existing suite | `python -m pytest "tests"` passes. |
| Stage validators | Run relevant Stage 2-6 validators if artifacts are regenerated or consumed. |
| Governance | `python scripts/validate_agent_governance.py` passes. |
| Scaffold | `python scripts/validate_comment_only_scaffold.py` passes or approved executable paths are exempted. |
| Manual artifact check | Output folder has manifest, tables, static report, limitations, non-claims, and no sensitive raw ledgers/logs. |

## Stop Conditions

Stop and ask before implementation approval is confirmed, live provider calls, raw overwrites, hidden Stage 2-6 reruns, user-facing service/API/dashboard work, persistent model-serving or inference-package changes, new forecast-row semantics beyond Stage 10B, LLM summaries, buy/sell or price-target language, metric/result-policy changes, protected-scope changes, sensitive-artifact packaging, Stage 6 reinterpretation, or benchmark-comparability changes.

## Final Response Requirements

Report created files, output folder path, artifacts generated, validation commands and results, non-claims preserved, and any follow-up blockers for any rerun or extension.
