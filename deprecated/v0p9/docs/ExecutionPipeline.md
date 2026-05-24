# Execution Pipeline

Status: active operations methodology for the local Stage 0 through Stage 10C repository. It defines safe sequencing for documentation maintenance, raw-data planning, approved Stage 2-6 rebuilds, Stage 7C diagnostics, Stage 8 plan-first updates, and Stage 10C output packets. It is not a new stage contract, benchmark-family approval, provider-completeness claim, live provider-call approval, persisted inference approval, service/dashboard scope, or one-command orchestrator.

## 1. Purpose

Use this document before any command sequence that can change artifacts, raw-data state, model outputs, evaluation outputs, documentation truth, or operational memory. Use `UsageManual.md` for command-level inputs and outputs.

The current repo intentionally has stagewise CLIs and validators rather than one approved full-pipeline command. A safe run means choosing the right mode, confirming approvals, running only the required stage commands, validating each artifact boundary, and updating truth/docs/memory when evidence changes.

## 2. Authority Stack

| Source | Governs |
| --- | --- |
| `AgentRules.md` and `docs/agent/Agent*.md` | Agent behavior, evidence discipline, approval gates, memory procedure. |
| `ScopeDecisionLog.md` | Owner decisions, protected scope, Stage 7/8/9/10 approvals, future approval gates. |
| `ResearchTruth.md` | Active truth synthesis through Stage 10C and current non-claims. |
| `ProjectDefinition.md` | Project identity, local artifact boundary, architecture and responsibility definitions. |
| `Stage0Prompt.md` through `Stage12Prompt.md` | Stage-specific mission, inputs, outputs, validation, and stop conditions. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Option B leakage, split, preprocessing, prediction, and diagnostic obligations. |
| `docs/Benchmark_Testing.md` and `docs/Pipeline_Testing.md` | Serious-run packet, validation, and comparability discipline. |
| `docs/Data_Update_Strategy.md` | Raw refresh, invalidation, rollback, provider-call, and ledger constraints. |
| `UsageManual.md` | Command-level usage, inputs, outputs, and active/planned function catalog. |
| `Complete_guidebook.txt` | File/function map and discoverability, subordinate to the above. |

## 3. Protected Baseline

| Area | Current protected value |
| --- | --- |
| Project mode | Local CLI/artifact-driven research system only. |
| Target | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | Approved top-50 liquid large-cap set. |
| Providers | Twelve Data OHLCV, Alpha Vantage news, SEC static/company support only. |
| Alignment | Same-day as-of-close; after-hours and non-trading-day news roll forward. |
| No-news policy | Keep no-news rows and encode explicit empty event states. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Metric hierarchy | Regression primary; ranking diagnostics mandatory secondary. |
| Current Stage 6 result | `clean_null` with `limitation_bearing` comparability. |
| Current Stage 7C status | Diagnostics-only; `benchmark_claim=false`; no live signal or all-data final-execution training output. |
| Current Stage 10C status | Local `historical_prediction` packet from existing Stage 5 saved predictions. |

## 4. Run Modes

| Mode | When to use | Commands allowed | Output status |
| --- | --- | --- | --- |
| Documentation maintenance | Docs, prompts, truth, guidebook, memory drift | Stage 0/9/11/12 prompt-guided edits, validators | Documentation evidence only. |
| Raw audit | Verify raw coverage, security, input readiness | Stage 1 audit scripts and validators | Raw evidence only. |
| Raw update planning | Daily/weekly or truncation-refinement plan | Stage 8 plan-first scripts without `--execute` | Plan manifest only. |
| Live raw update | Explicitly approved provider calls | Stage 8 or provider scripts with `--execute` and limits | Raw payload changes, no benchmark result. |
| Benchmark rebuild | Approved clean Stage 2-6 rerun | Stage 2, 3, 4, 5, 6 CLIs and validators | New evidence packet requiring comparability review. |
| Stage 7C diagnostics | Approved contextual-bandit diagnostic rerun | Stage 7C CLI and validator | Diagnostic packet only. |
| Stage 10C packet | Readable saved-prediction output packet | Stage 10C CLI and validator | Local historical-prediction packet. |
| Future persisted inference | Not deployed | None without approval | Blocked. |
| Service/API/dashboard/trading | Out of scope | None without approval | Blocked. |

## 5. Approval Gates

Stop and ask before any action that would do one of these:

- Change target family, horizon set, universe, provider stack, alignment, no-news policy, split policy, comparator roster, metric policy, result rule, or benchmark comparability.
- Call live providers, use Stage 8 `--execute`, or consume quota without explicit approval.
- Delete, overwrite, patch, or destructively normalize raw provider payloads.
- Commit, publish, or share API-key-bearing ledgers/logs.
- Treat Alpha Vantage truncation as scientifically resolved or claim provider-level article completeness.
- Reinterpret Stage 6 `clean_null` as positive, invalidated, or trading-relevant without new approved evidence.
- Treat Stage 7C diagnostics as all-data final-execution training output, live buy/sell signals, portfolio advice, or Stage 6 reinterpretation.
- Introduce persisted model serving, new `forecast_candidate` semantics, true future feature-only forecast rows, scheduled automation, service/API/dashboard scope, LLM summaries, or trading signals.
- Reactivate comment-only scaffold files as executable behavior without implementation approval and tests.

## 6. Preflight Checklist

1. Read current context from `ResearchTruth.md`, `ScopeDecisionLog.md`, `ProjectDefinition.md`, relevant `Stage*Prompt.md`, `UsageManual.md`, and operational memory.
2. Classify the task as documentation, raw audit, raw update plan, live raw update, Stage 2-6 rebuild, Stage 7C diagnostic, Stage 10C packet, or future blocked capability.
3. Confirm required approvals for the selected mode.
4. Identify exact inputs, artifact roots, output roots, and whether any output root already exists.
5. Decide whether `--allow-overwrite` or `--overwrite` is needed; avoid both by default.
6. Check sensitive ledger/log exposure risk before provider-related work.
7. Run baseline checks unless the task is purely informational:

```powershell
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python -m pytest "tests"
```

Expected current active-root test result: `58 passed`.

## 7. Stage And Requirement Matrix

| Stage | Status | Required input class | Required output class | Completion validator |
| --- | --- | --- | --- | --- |
| Stage 0 | Executed doc repair workflow | Governance, truth, design docs | Active docs, README, guidebook, memory | Governance validator. |
| Stage 0A | Executed scaffold workflow | Scaffold prompt, active docs | Comment-only source/config/test scaffold | Comment-only validator. |
| Stage 0B | Executed Option B contract | Owner approval, validation docs | Data separation/overfitting contract | Governance and consistency checks. |
| Stage 1 | Executed raw audit evidence | Universe, raw provider roots, manifests | Raw audit reports, coverage/security evidence | `validate_stage0_stage1_completion.py`, raw audits. |
| Stage 2 | Executed/materialized | Raw inputs, universe, clean-window policy | Dataset panel, manifest, row digest | `validate_stage2_inputs.py`, `validate_stage2_completion.py`. |
| Stage 3 | Executed/materialized | Stage 2 artifact, raw provider roots, feature/label configs | Features, labels, aligned news, manifest | `validate_stage3_readiness.py`, `validate_stage3_completion.py`. |
| Stage 4 | Executed/materialized | Stage 3 artifact, split/packet configs | Folds, assignments, lockbox, leakage, packet gate | `validate_stage4_completion.py`. |
| Stage 5 | Executed/materialized | Stage 3/4 artifacts, model config | Model/preprocessing manifests, saved predictions | `validate_stage5_completion.py`. |
| Stage 6 | Executed/materialized | Stage 3/4/5 artifacts, evaluation config | Metrics, diagnostics, comparison summary, comparability | `validate_stage6_completion.py`. |
| Stage 7A | Executed research-only | Stage 6 evidence, research context | Feasibility memo | Research/memory evidence only. |
| Stage 7B | Executed decision-only | Stage 7A memo, decision templates | Answered Stage 7B decisions | Scope decision entries. |
| Stage 7C | Executed diagnostics-only | Refreshed Stage 3/4/5 post-lockbox artifacts, Stage 7 config | Diagnostic policy packet, final-execution stub | `validate_stage7_completion.py`. |
| Stage 8 | Executed plan-first tooling | Provider roots, universe, requested end date | Plan manifests or approved raw payload changes | `tests/ops`, plan manifests. |
| Stage 9 | Executed docs/memory reconciliation | Current active docs and evidence | Stale-status repairs, memory/ledger | Governance/scaffold/ledger checks. |
| Stage 10A | Executed research-only | Rebuild/update/output context | Research memo | Research/memory evidence only. |
| Stage 10B | Executed decision-only | Stage 10A memo, decision templates | Answered Stage 10B decisions | Scope decision entries. |
| Stage 10C | Executed/materialized | Stage 5 predictions, Stage 3 context, Stage 6 context | Static HTML plus CSV/Parquet prediction-output packet | `validate_stage10c_completion.py`. |
| Stage 11 | Proposed prompt only | Post-Stage-10C repo context | Future audit memo if executed | Not executed. |
| Stage 12 | Proposed prompt only | Post-Stage-10C prompt context | Future DeepResearch prompt maintenance if executed | Not executed. |

## 8. Active And Planned Function Catalog

| Function or capability | Status | Pipeline position | Requirements | Outputs and non-claims |
| --- | --- | --- | --- | --- |
| Governance validation | Active | Any mode pre/post check | Current governance docs and ledger | Structural compliance only. |
| Comment-only scaffold validation | Active | Any code/config/test status check | Approved executable-path exemptions | Does not prove scientific readiness. |
| Raw universe/OHLCV/news audit | Active scripts plus some scaffolded CLIs | Stage 1 | Read-only raw roots and manifests | Raw evidence, not benchmark readiness. |
| Alpha Vantage top-50 runner | Active | Raw collection support | API key for live calls; canonical ticker handling | Raw payloads and ledgers; provider completeness not claimed. |
| Alpha Vantage truncation refinement | Active | Raw refinement support | Stage 1 manifest, existing raw files, approval for live calls | Refinement files/plans; truncation may remain. |
| Twelve Data missing-download utility | Active | Raw OHLCV support | API key for live calls, date window, universe | Raw OHLCV files/plans; not a dataset by itself. |
| Stage 8 daily/weekly update scripts | Active plan-first | Raw update planning | End date, provider roots, optional live approval | Plan manifests by default; no prediction output. |
| Stage 2 dataset builder | Active | Benchmark rebuild | Approved raw inputs and clean-window assumptions | Dataset artifact; no benchmark claim. |
| Stage 3 feature/label builder | Active | Benchmark rebuild | Stage 2 root and configs | Features/labels/news; no model claim. |
| Stage 4 split/packet builder | Active | Benchmark rebuild | Stage 3 root and split configs | Folds/lockbox/packet gate; no metrics. |
| Stage 5 train/predict | Active | Benchmark rebuild | Stage 3/4 roots and frozen roster | Saved OOS predictions; no final result. |
| Stage 6 benchmark reporting | Active | Benchmark rebuild | Stage 5 saved predictions and frozen labels | `clean_null` result packet unless a new approved run changes evidence. |
| Stage 7C contextual-bandit diagnostics | Active diagnostics | Post-Stage-6 diagnostic branch | Approved Stage 7C context and holdout | Diagnostic metrics; no trading signal. |
| Stage 7 final-execution stub | Stub only | Future live-use design placeholder | No `--run-all-data-training`; future approval needed | Stub JSON only. |
| Stage 10C prediction-output packet | Active | Readable saved-prediction output | Stage 5/3/6 artifacts | Historical-prediction packet; no fresh inference. |
| Persisted fitted-model inference | Not deployed | Future extension | Separate model packaging, preprocessing, schema, cutoff, and row-role approval | Blocked. |
| `forecast_candidate` future rows | Not approved | Future extension | Persisted inference and row semantics approval | Blocked. |
| Provider normalization CLIs | Comment-only scaffold | Future raw/provider layer | Implementation approval and tests | Planned only. |
| Ledger sanitization CLI | Comment-only scaffold | Future security/ops layer | Implementation approval and redaction tests | Planned only. |
| Run-summary CLI | Comment-only scaffold | Future reporting convenience | Implementation approval and traceability tests | Planned only. |
| Service/API/dashboard | Out of scope | None | Separate scope/product approval | Blocked. |

## 9. Raw Data Update And Refinement Path

Plan first, without provider calls:

```powershell
python scripts/news_update_daily.py --end-date YYYY-MM-DD
python scripts/news_update_weekly.py --end-date YYYY-MM-DD
python scripts/OHLCV_daily_update.py --end-date YYYY-MM-DD --include-spy
python scripts/OHLCV_weekly_update.py --end-date YYYY-MM-DD --include-spy
```

Plan truncation refinement:

```powershell
python scripts/run_alphavantage_news_truncation_refinement_quarterly.py --plan
python scripts/run_alphavantage_news_truncation_refinement_standalone.py --plan --order reverse
```

If live calls are explicitly approved, use bounded flags such as `--execute`, `--max-calls`, and `--sleep-seconds`, preserve raw payloads, redact shareable ledgers, and keep existing raw files by default unless `--overwrite` is separately reviewed.

After any raw data change, rerun raw/input checks before Stage 2:

```powershell
python scripts/validate_stage2_inputs.py --write
python scripts/validate_stage0_stage1_completion.py --write
```

Raw-data changes can invalidate Stage 2 through Stage 6 and downstream Stage 7C/Stage 10C artifacts. Old artifacts remain historical evidence until a new approved run and comparability review exist.

## 10. Stage 2 Through Stage 6 Clean Rebuild

Run these in order only after preflight and approval checks. Prefer explicit roots if not using current defaults.

### Stage 2 Dataset

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_benchmark_dataset
python scripts/validate_stage2_inputs.py --write
python scripts/validate_stage2_completion.py --write
```

Required checks: dataset version, clean window, row count, row digest, no-news fields, provider limitation flags, CVX derived patch manifest. Stage 2 is not a benchmark result.

### Stage 3 Features And Labels

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels
python scripts/validate_stage3_readiness.py --write
python scripts/validate_stage3_completion.py --write
```

Required checks: market features, event-state features, aligned news, labels, row-universe digest, truncation flags, no-news flags, as-of safety.

### Stage 4 Splits And Packet Gate

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet
python scripts/validate_stage4_completion.py --write
```

Required checks: fold definitions, split assignments, purge/embargo accounting, lockbox record, leakage validation, artifact-packet validation, benchmark-runner gate.

### Stage 5 Model Training And Saved Predictions

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.train_models_and_predict
python scripts/validate_stage5_completion.py --write
```

Required checks: resolved model config, frozen roster, preprocessing-fit manifest, model-fit manifest, saved validation/lockbox predictions, search-space summary, training diagnostics. Stage 5 creates no metrics or result by itself.

### Stage 6 Serious Benchmark Reporting

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
python scripts/validate_stage6_completion.py --write
```

Required checks: prediction-label validation, regression metrics, ranking diagnostics, paired comparisons, overfitting report, comparison summary, serious packet validation, benchmark comparability classification.

## 11. Stage 7C Diagnostic Path

Use this only for the approved diagnostics branch, not Stage 6 reinterpretation.

The current Stage 7C run used:

| Item | Current value |
| --- | --- |
| Twelve Data raw target | `time_series__2010-01-01__2026-05-22.json` |
| Stage 7 split config | `configs/stage7_splits_post_lockbox_2026-05-22.yaml` |
| New holdout | `2026-02-17` through `2026-02-25` |
| Validation manifest | `data/manifests/stage7_post_lockbox_completion_validation_2026-05-22.json` |

Validate current Stage 7C artifact:

```powershell
python scripts/validate_stage7_completion.py --stage7-root "data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout"
```

Do not run or describe all-data final-execution training output unless separately approved. The existing final-execution CLI is a stub that blocks `--run-all-data-training`.

## 12. Stage 10C Prediction-Output Path

Generate the current packet from existing Stage 5 saved predictions:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
```

Validate:

```powershell
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

Stage 10C performs no provider call, raw-data mutation, hidden Stage 2-6 rerun, persisted inference packaging, service/API/dashboard behavior, or trading-signal output. Current rows are `historical_prediction`; `forecast_candidate` semantics remain unapproved.

## 13. Validation Suite After Changes

After code, config, artifact, or material documentation changes, run the relevant subset plus baseline checks:

```powershell
python -m pytest "tests"
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python -c "import json, pathlib; p=pathlib.Path('docs/agent/agent_log/Event_Ledger.ndjson'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('EVENT_LEDGER_JSONL_VALID')"
```

For artifact-producing stages, also run the stage validator for every artifact touched. For active-root Python syntax checks, use compileall on `src`, `scripts`, and `tests` before claiming broad completion.

## 14. Documentation And Memory Updates

Update these when artifacts, result class, limitations, command names, file names, or comparability status change:

- `ResearchTruth.md`.
- `ProjectDefinition.md`.
- `ScopeDecisionLog.md` if approvals or owner decisions change.
- `ExecutionFlow.md`.
- `ExecutionPipeline.md`.
- `UsageManual.md`.
- `README.md`.
- `docs/Execution_Plan.md`.
- `docs/Detailed_Execution_Stages.md`.
- `docs/Benchmark_Testing.md`.
- `docs/Pipeline_Testing.md`.
- `docs/db_Testing.md`.
- `docs/testing_commands.md`.
- `docs/Data_Update_Strategy.md`.
- `Complete_guidebook.txt`.
- `docs/agent/agent_log/Current_State.md`.
- `docs/agent/agent_log/Event_Ledger.ndjson`.

Do not update only one layer when a run changes multiple truth layers. Prompt files and DeepResearch topic prompts must be updated when their required-background files or current-state assumptions change.

## 15. Comparability Rules

Treat any new Stage 6 packet as a new evidence packet. Compare it to the existing packet only after reviewing rows, labels, features, splits, model roster, metric policy, lockbox use, provider coverage, and limitation flags.

If only Alpha Vantage truncation refinement changes news coverage, comparability is still not automatic. Feature values and provider limitation flags may change, so Stage 2 through Stage 6 must be rebuilt and the old `clean_null` result must not be silently overwritten.

Stage 7C and Stage 10C artifacts do not promote Stage 6 comparability. They are downstream diagnostics/output packets with their own non-claims.

## 16. Stop Conditions

Stop and ask for clarification if:

- No approved stage, prompt, or runbook covers the requested change.
- A command would require protected-scope or comparability decisions.
- A validator failure suggests contract change rather than implementation drift.
- Raw provider files conflict or destructive overwrite policy is needed.
- Sensitive ledgers, logs, keys, unsanitized request URLs, or raw provider secrets could be exposed.
- A requested output could be read as trading advice, a buy/sell signal, a price target, a service/API/dashboard, persisted inference, or benchmark promotion.
