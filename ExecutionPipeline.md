# Execution Pipeline

Status: active zero-to-benchmark execution guide for the local v1p0 and historical Stage 2-6 repository.

Updated: 2026-05-27

## 1. Purpose

Use this file when you want to execute the repository, rebuild local artifacts, train the active model path, or validate benchmark outputs.

This is an execution guide, not a new benchmark contract. It explains the commands that are currently evidenced in the repository and the order in which they are safe to run. It does not approve live provider calls, raw overwrites, new benchmark-family definitions, positive benchmark claims, trading outputs, persisted inference, service/API/dashboard behavior, or Stage 6 reinterpretation.

For command-level artifact descriptions, also use `UsageManual.md`. For current truth and non-claims, use `ResearchTruth.md`. For protected scope and owner decisions, use `ScopeDecisionLog.md`, `ArchitecturalDesignDecisions.md`, and `ProjectDefinition.md`.

## 2. Current Execution Model

The repository has two relevant execution tracks.

| Track | Purpose | Current status |
| --- | --- | --- |
| Historical Stage 2-6 pipeline | Builds the local top-50 benchmark dataset, features, splits, saved predictions, and Stage 6 benchmark report. | Implemented and materialized with `clean_null` and `limitation_bearing` result status. |
| v1p0 XGBoost workflow | Builds v1p0 market feature sidecars, fixed market baselines, XGBoost search/frozen-final evidence, overfit review, uncertainty diagnostics, and refreshed XGBoost-only Stage 35-40 closeout. | Active current branch, centered on `market_xgboost_v2_frozen_final`; non-claiming through Stage 40. |

The current active model path is XGBoost-only. TSMixer, XGBoost+TSMixer ensembles, and market-event fusion are historical or cancelled for the current branch unless the user explicitly reopens them.

There is no approved one-command full-pipeline orchestrator. Run stage commands deliberately and validate each artifact boundary before continuing.

## 3. Hard Boundaries

Stop and ask before any action that would do one of these:

- Change target family, horizon set, provider stack, universe, news alignment, no-news policy, split policy, comparator roster, metric policy, result rule, or benchmark comparability.
- Call live providers, use update scripts with `--execute`, or consume provider quota without explicit approval.
- Delete, overwrite, patch, or destructively normalize raw provider payloads.
- Commit, publish, or share API-key-bearing ledgers/logs.
- Treat Alpha Vantage truncation as resolved or claim provider-level article completeness.
- Reinterpret Stage 6 `clean_null` as positive, invalidated, trading-relevant, or comparable to v1p0 without explicit review.
- Treat Stage 7C, Stage 10C, v1p0 diagnostics, or XGBoost Stage 21-25 artifacts as live forecasts, buy/sell signals, portfolio advice, or service output.
- Use `scripts/run_v1p0_stage26_40_final_sprint.py` as the active closeout runner before it is repaired for the XGBoost-only branch.
- Introduce persisted fitted-model inference, new `forecast_candidate` semantics, scheduled automation, service/API/dashboard scope, LLM summaries, or trading signals.

## 4. Environment Preflight

Run from the repository root. The validated v1p0 runtime is `~/venvs/ai`.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python -m pytest tests/v1p0
```

Use the full test suite before broad Stage 2-6 claims or after code changes that affect the historical pipeline.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m pytest tests
```

For documentation-only edits, the governance validator and any affected focused tests are usually enough unless the edit changes executable commands, artifact contracts, or result status.

## 5. Local Database And Raw State

This repository does not currently expose a SQL database as the primary execution target. The local "database" is the artifact store under `data/`: raw provider JSON files, Stage 2 dataset panels, Stage 3 feature/label sidecars, Stage 4 split packets, Stage 5 saved predictions, Stage 6 reports, and v1p0 result-vault packets.

### 5.1 Audit Existing Raw Inputs

Use these checks before rebuilding the Stage 2 dataset.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python scripts/validate_stage2_inputs.py --write
python scripts/validate_stage0_stage1_completion.py --write
```

These checks validate readiness and write manifests. They do not create a benchmark result.

### 5.2 Plan Raw Updates Without Provider Calls

Use plan-first update commands when you need to know what daily or weekly raw refresh would do.

```bash
source ~/venvs/ai/bin/activate
python scripts/news_update_daily.py --end-date YYYY-MM-DD
python scripts/news_update_weekly.py --end-date YYYY-MM-DD
python scripts/OHLCV_daily_update.py --end-date YYYY-MM-DD --include-spy
python scripts/OHLCV_weekly_update.py --end-date YYYY-MM-DD --include-spy
```

Plan truncation refinement without provider calls.

```bash
source ~/venvs/ai/bin/activate
python scripts/run_alphavantage_news_truncation_refinement_quarterly.py --plan
python scripts/run_alphavantage_news_truncation_refinement_standalone.py --plan --order reverse
```

Live raw updates require explicit user approval for provider calls, bounded quotas, and overwrite policy. After any approved raw-data change, rebuild and revalidate downstream artifacts before using old benchmark conclusions.

### 5.3 Create Or Recreate The Stage 2 Dataset Store

Stage 2 creates the local benchmark panel from existing raw inputs.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m event_state_forecasting.cli.build_benchmark_dataset
python scripts/validate_stage2_inputs.py --write
python scripts/validate_stage2_completion.py --write
```

Required output class: `data/datasets/phase1_top50/.../` with `benchmark_panel.parquet`, `dataset_manifest.json`, `row_universe_digest.json`, `clean_window_decision.json`, and CVX derived patch evidence. This is dataset evidence only, not a model or benchmark result.

## 6. Preprocessing And Split Preparation

Stage 3 materializes features, aligned news, no-news indicators, and labels.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m event_state_forecasting.cli.build_features_and_labels
python scripts/validate_stage3_readiness.py --write
python scripts/validate_stage3_completion.py --write
```

Stage 4 materializes purged-plus-embargoed walk-forward folds, the final lockbox, leakage checks, and packet-gate evidence.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m event_state_forecasting.cli.build_splits_and_packet
python scripts/validate_stage4_completion.py --write
```

Stop if row-universe digests, split membership, label availability, no-news handling, or leakage checks fail.

## 7. Historical Stage 5-6 Benchmark Rebuild

Stage 5 trains the historical comparator roster and writes saved validation/lockbox predictions.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m event_state_forecasting.cli.train_models_and_predict
python scripts/validate_stage5_completion.py --write
```

Stage 6 computes serious benchmark reporting from saved predictions.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m event_state_forecasting.cli.run_benchmark
python scripts/validate_stage6_completion.py --write
```

Any new Stage 6 packet is a new evidence packet. Do not silently compare it to the existing `clean_null` result until rows, labels, features, splits, model roster, metric policy, lockbox use, provider coverage, and limitation flags are reviewed.

## 8. Active v1p0 XGBoost Workflow

The active v1p0 branch assumes the historical Stage 2-6-compatible source chain exists. If that chain is missing or stale, run Sections 5 through 7 first.

### 8.1 Smoke And Dependency Check

```bash
source ~/venvs/ai/bin/activate
python -m pytest tests/v1p0
python scripts/run_v1p0_first_slice_smoke.py
```

The smoke command writes toy-data outputs only and confirms local command behavior, including XGBoost availability in the required environment.

### 8.2 Market Feature Sidecars And Fixed Baselines

```bash
source ~/venvs/ai/bin/activate
python scripts/build_v1p0_market_feature_sidecars.py
python scripts/run_v1p0_historical_market_baselines.py
python scripts/run_v1p0_full_diagnostic_baseline_gate.py
```

Stage 17 writes v1p0 market lag/rolling feature sidecars. Stage 19 writes fixed lag-linear and fixed-XGBoost saved predictions. Stage 20 computes diagnostics from those saved predictions.

### 8.3 XGBoost Search, Frozen Final, And Reviews

```bash
source ~/venvs/ai/bin/activate
python scripts/freeze_v1p0_xgboost_search_space.py
python scripts/run_v1p0_xgboost_nested_search.py
python scripts/run_v1p0_xgboost_frozen_final_evaluation.py
python scripts/run_v1p0_xgboost_overfit_promotion_review.py
python scripts/run_v1p0_xgboost_block_bootstrap_uncertainty.py
```

Stage 21 freezes search-space and objective configuration. Stage 22 runs development-only search with lockbox use forbidden. Stage 23 evaluates the frozen selected XGBoost config once. Stage 24 records overfit-frontier and conservative classification. Stage 25 records block-bootstrap uncertainty and train-to-real-data gap diagnostics.

Current active candidate: `market_xgboost_v2_frozen_final`.

Current active claim status: non-claiming; `positive_claim_approved=false`.

### 8.4 XGBoost-Only Closeout Status

Run the refreshed XGBoost-only closeout after Stage 25 evidence exists.

```bash
source ~/venvs/ai/bin/activate
python scripts/run_v1p0_xgboost_only_stage35_40_closeout.py
```

Stage 35 through Stage 40 are now refreshed for the XGBoost-only branch. The older Stage 26-40 runner and older Stage 35-40 packets predate the current XGBoost-only branch decision and must not be treated as the active closeout.

## 9. Optional Diagnostics And Output Packets

Stage 7C is diagnostics-only and does not change Stage 6.

```bash
source ~/venvs/ai/bin/activate
python scripts/validate_stage7_completion.py --stage7-root "data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout"
```

Stage 10C creates a local historical-prediction output packet from existing Stage 5 saved predictions.

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

The XGBoost-vs-TSMixer stratified diagnostic is post-hoc diagnostics-only and exists to document why TSMixer is not active.

```bash
source ~/venvs/ai/bin/activate
python scripts/run_v1p0_xgb_tsmixer_stratified_diagnostic.py
```

Do not feed TSMixer, XGBoost+TSMixer ensemble, or market-event fusion into the active XGBoost-only workflow unless the user explicitly reopens that scope.

## 10. End-To-End Command Blocks

### 10.1 Raw Artifacts To Historical Stage 6 Benchmark

```bash
source ~/venvs/ai/bin/activate
export PYTHONPATH=src
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python scripts/validate_stage2_inputs.py --write
python -m event_state_forecasting.cli.build_benchmark_dataset
python scripts/validate_stage2_completion.py --write
python -m event_state_forecasting.cli.build_features_and_labels
python scripts/validate_stage3_readiness.py --write
python scripts/validate_stage3_completion.py --write
python -m event_state_forecasting.cli.build_splits_and_packet
python scripts/validate_stage4_completion.py --write
python -m event_state_forecasting.cli.train_models_and_predict
python scripts/validate_stage5_completion.py --write
python -m event_state_forecasting.cli.run_benchmark
python scripts/validate_stage6_completion.py --write
```

Use this block only when a Stage 2-6 rebuild is approved and output-root/overwrite policy is understood.

### 10.2 Existing Stage 2-6 Chain To Active v1p0 XGBoost Candidate

```bash
source ~/venvs/ai/bin/activate
python scripts/validate_agent_governance.py
python -m pytest tests/v1p0
python scripts/run_v1p0_first_slice_smoke.py
python scripts/build_v1p0_market_feature_sidecars.py
python scripts/run_v1p0_historical_market_baselines.py
python scripts/run_v1p0_full_diagnostic_baseline_gate.py
python scripts/freeze_v1p0_xgboost_search_space.py
python scripts/run_v1p0_xgboost_nested_search.py
python scripts/run_v1p0_xgboost_frozen_final_evaluation.py
python scripts/run_v1p0_xgboost_overfit_promotion_review.py
python scripts/run_v1p0_xgboost_block_bootstrap_uncertainty.py
python scripts/run_v1p0_xgboost_only_stage35_40_closeout.py
```

This block trains, evaluates, and closes the active XGBoost-only evidence chain through Stage 40. It does not approve positive benchmark language, Stage 6 reinterpretation, trading output, or benchmark-comparability promotion.

## 11. Expected Artifact Roots

| Stage or function | Main output root |
| --- | --- |
| Stage 2 dataset | `data/datasets/phase1_top50/...` |
| Stage 3 features and labels | `data/features/phase1_top50/...` |
| Stage 4 splits | `data/splits/phase1_top50/...` |
| Stage 5 saved predictions | `data/models/phase1_top50/...` |
| Stage 6 benchmark report | `data/benchmark_runs/phase1_top50/...` |
| v1p0 Stage 17 market sidecars | `data/features/v1p0/...` and `data/v1p0_full_results/...stage17...` |
| v1p0 Stage 19 fixed baselines | `data/models/v1p0/...` and `data/v1p0_full_results/...stage19...` |
| v1p0 Stage 20 diagnostics | `data/diagnostics/v1p0/...` and `data/v1p0_full_results/...stage20...` |
| v1p0 Stage 21-25 XGBoost evidence | `data/v1p0_full_results/...stage21...` through `...stage25...` |
| v1p0 Stage 35-40 XGBoost-only closeout | `data/v1p0_full_results/...stage35__xgboost_only...` through `...stage40__xgboost_only...` |
| Stage 7C diagnostics | `data/stage7_contextual_bandit/phase1_top50/...` |
| Stage 10C historical prediction outputs | `data/prediction_outputs/phase1_top50/...` |

Generated `data/**` artifacts are local evidence and should not be staged accidentally unless explicitly requested and reviewed.

## 12. Validation After Changes Or Runs

After code, config, artifact, or material documentation changes, run the relevant focused checks plus governance validation.

```bash
source ~/venvs/ai/bin/activate
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python -m pytest tests/v1p0
python -c "import json, pathlib; p=pathlib.Path('docs/agent/agent_log/Event_Ledger.ndjson'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('EVENT_LEDGER_JSONL_VALID')"
git diff --check
```

For Stage 2-6 rebuilds, also run the matching stage completion validator for every artifact touched. For broad Python changes, run `python -m compileall -q src scripts tests` before claiming broad completion.

## 13. Documentation And Memory Updates

Update the relevant truth and usage layer when artifacts, result class, limitations, command names, file names, active branch status, or comparability status change.

| File | Update when |
| --- | --- |
| `ResearchTruth.md` | New implemented truth or materially changed evidence exists. |
| `ProjectDefinition.md` | Active project identity, branch direction, or protected boundaries change. |
| `UsageManual.md` | A real validated command path or artifact inventory changes. |
| `ExecutionPipeline.md` | Execution sequence, approval gates, or active workflow changes. |
| `docs/Prompts/v1p0_Prompt_Status_Register.md` | Stage status, rerun requirement, cancellation, or dependency cascade changes. |
| `docs/agent/agent_log/Current_State.md` | Operational priorities, blockers, evidence pointers, or next gates change. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | New decision, artifact creation, validation result, or closeout evidence needs durable logging. |

Do not update only one layer when a run changes multiple truth layers. Prompt files and DeepResearch topic prompts must be updated when their required-background files or current-state assumptions change.

## 14. Stop Conditions

Stop and ask for clarification if:

- No approved stage, prompt, or runbook covers the requested change.
- A command would require protected-scope or comparability decisions.
- A validator failure suggests contract change rather than implementation drift.
- Raw provider files conflict or destructive overwrite policy is needed.
- Sensitive ledgers, logs, keys, unsanitized request URLs, or raw provider secrets could be exposed.
- A requested output could be read as trading advice, a buy/sell signal, a price target, a service/API/dashboard, persisted inference, or benchmark promotion.
