# Execution Flow

Status: active-root runbook through Stage 10C local prediction-output packet generation. This describes safe current commands and points to `ExecutionPipeline.md` for clean stagewise rebuilds and `UsageManual.md` for local command inputs/outputs and artifact usage.

## Current Safe Checks

Run governance and scaffold validators:

```powershell
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
```

Run active tests:

```powershell
python -m pytest "tests"
```

Expected current active-root result: `58 passed`.

Validate the current Stage 7C diagnostics, Stage 6 packet, and upstream artifacts:

```powershell
python scripts/validate_stage6_completion.py
python scripts/validate_stage7_completion.py
python scripts/validate_stage5_completion.py
python scripts/validate_stage4_completion.py
python scripts/validate_stage3_completion.py
python scripts/validate_stage2_completion.py
python scripts/validate_stage2_inputs.py
python scripts/validate_stage0_stage1_completion.py
```

## Stagewise Rebuild Commands

There is no single approved one-command full-pipeline orchestrator. Rebuild through the stage CLIs in order:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_benchmark_dataset
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.train_models_and_predict
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
```

Use `ExecutionPipeline.md` before rerunning after new data, truncation refinement, or code/config changes.

## Live Provider Runs

Live Alpha Vantage and Twelve Data calls require an API key and consume provider quota. Do not run live calls casually.

Plan without provider calls first:

```powershell
python scripts/run_alphavantage_news_top50_only_standalone.py --plan --skip-seed-migration
python scripts/run_alphavantage_news_truncation_refinement_quarterly.py --plan
python scripts/run_alphavantage_news_truncation_refinement_standalone.py --plan --order reverse
python scripts/news_update_daily.py --end-date YYYY-MM-DD
python scripts/OHLCV_daily_update.py --end-date YYYY-MM-DD --include-spy
```

Before live calls:

- Confirm the intended universe bucket.
- Confirm quota budget.
- Use Stage 8 `--execute` only after explicit live-call approval.
- For truncation refinement, prefer controlled one-request execution when live mode is used.
- Confirm request ledger handling does not expose API keys in committed/shared files.
- Preserve truncation flags and raw payloads.

## Benchmark Reporting

The current Stage 6 reporting command is:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
```

Current evidenced result class: `clean_null`.

Current comparability: `limitation_bearing`.

Do not change Stage 6 metric policy, comparison framing, lockbox interpretation, comparator roster, protected scope, or benchmark comparability after result inspection without explicit approval.

## Stage 10 Boundary

Stage 10A research, Stage 10B decision capture, and the first Stage 10C local prediction-output packet implementation are complete. Stage 10C is local artifact generation only: no provider calls, raw overwrites, hidden Stage 2-6 reruns, persisted inference package, service/API/dashboard scope, trading signal, Stage 6 reinterpretation, or benchmark-comparability promotion.

Generate the current Stage 10C packet from existing Stage 5 saved predictions:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
```

Validate the generated packet:

```powershell
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

Current Stage 10C row role is `historical_prediction`; `forecast_candidate` semantics remain unapproved for future feature-only rows.
