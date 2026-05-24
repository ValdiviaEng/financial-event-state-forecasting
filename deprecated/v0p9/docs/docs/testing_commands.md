# Testing Commands

Status: active-root command ledger through Stage 10C local prediction-output packet generation. Commands listed as current have evidence from Stage 2 through Stage 10C validation work.

## Current Validated Commands

```powershell
python scripts/validate_agent_governance.py
```

Expected current result: `VALIDATION PASSED`.

```powershell
python scripts/validate_comment_only_scaffold.py
```

Expected current result: `COMMENT_ONLY_VALIDATION PASSED`; approved Stage 2, Stage 3, Stage 4, Stage 5, Stage 6, Stage 7C, Stage 8, and Stage 10C executable test paths are exempted while remaining scaffolds stay comment-only.

```powershell
python scripts/validate_stage2_inputs.py
```

Expected current result after Stage 2 test conversion: prints `status: ready_for_dataset_builder_gate`.

```powershell
python -m pytest "tests/data/test_contracts_contract.py" "tests/dataset/test_row_universe_contract.py" "tests/dataset/test_panel_builder_contract.py"
```

Expected current result for the focused Stage 2 subset: `8 passed`.

```powershell
python -m pytest "tests"
```

Expected current active-root result: `58 passed`.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_benchmark_dataset
```

Expected current result when the current dataset version does not already exist: builds the Stage 2 dataset under `data/datasets/phase1_top50/` and prints `status: stage2_dataset_built`, `row_count: 117750`, and the row digest. Use `--allow-overwrite` only to replace the generated current-version dataset artifact.

```powershell
python scripts/validate_stage2_completion.py
```

Expected current result: `STAGE2_COMPLETION_VALIDATION PASSED`.

```powershell
python scripts/validate_stage3_readiness.py
```

Expected current result: prints `status: ready_for_stage3_implementation` with `stage2_dataset_ready: True` and `stage3_implementation_ready: True`.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels
```

Expected current result when the current Stage 3 artifact version does not already exist: builds artifacts under `data/features/phase1_top50/` and prints `status: stage3_features_labels_built`, `row_count: 117750`, and the row digest. Use `--allow-overwrite` only to replace the generated current-version artifact.

```powershell
python scripts/validate_stage3_completion.py
```

Expected current result: `STAGE3_COMPLETION_VALIDATION PASSED`.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet
```

Expected current result when the current Stage 4 artifact version does not already exist: builds artifacts under `data/splits/phase1_top50/` and prints `status: stage4_splits_packet_built`, `fold_count: 9`, `lockbox_start_date: 2025-09-30`, and `assignment_row_count: 1059750`. Use `--allow-overwrite` only to replace the generated current-version artifact.

```powershell
python scripts/validate_stage4_completion.py
```

Expected current result: `STAGE4_COMPLETION_VALIDATION PASSED`.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.train_models_and_predict
```

Expected current result when the current Stage 5 artifact version does not already exist: builds artifacts under `data/models/phase1_top50/` and prints `stage5_models_predictions_built model_count 8 prediction_row_count 2088000`.

```powershell
python scripts/validate_stage5_completion.py
```

Expected current result: `STAGE5_COMPLETION_VALIDATION PASSED`.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
```

Expected current result when the current Stage 6 artifact version does not already exist: builds artifacts under `data/benchmark_runs/phase1_top50/` and prints `stage6_serious_benchmark_reporting_built result_class clean_null comparability limitation_bearing` plus the artifact root.

```powershell
python scripts/validate_stage6_completion.py
```

Expected current result: `STAGE6_COMPLETION_VALIDATION PASSED`.

```powershell
python scripts/validate_stage0_stage1_completion.py
```

Expected current result: `STAGE0_STAGE1_COMPLETION_VALIDATION PASSED`.

```powershell
python scripts/audit_deprecated_ohlcv_salvage.py
```

Expected current result: prints `status: usable_as_salvage_evidence_with_limitations` with top-50 `50/50`, SPY present, and all-horizon candidate as-of range `2024-04-01` to `2024-10-03`.

```powershell
python -m py_compile @(Get-ChildItem -Path "scripts" -Filter "*.py" | ForEach-Object { $_.FullName })
```

Expected current result: completes without output.

```powershell
python scripts/run_alphavantage_news_top50_only_standalone.py --plan --skip-seed-migration
```

Expected current top-50 result: summary file reports `completed_request_count: 850`, `pending_request_count: 0`, and `planned_request_count_total: 850`.

```powershell
python scripts/run_alphavantage_news_truncation_refinement_quarterly.py --plan
```

Current plan-mode evidence after latest local verification: summary generated 2026-05-20 reported total `planned=362`, `pending=199`, quarterly `planned=282`, `valid=84`, `missing=198`, `truncated=30`, `pending=198`; monthly `planned=80`, `valid=79`, `missing=1`, `truncated=37`, `pending=1`; budget remaining `0/25` in the rolling successful-call window.

```powershell
python scripts/news_update_daily.py --end-date YYYY-MM-DD
python scripts/news_update_weekly.py --end-date YYYY-MM-DD
python scripts/OHLCV_daily_update.py --end-date YYYY-MM-DD --include-spy
python scripts/OHLCV_weekly_update.py --end-date YYYY-MM-DD --include-spy
```

Expected current result in default mode: writes a Stage 8 plan manifest, prints `status: planned_only`, performs no provider calls, and keeps `benchmark_claim=false`.

```powershell
python -m pytest "tests/stage10"
```

Expected current result for the focused Stage 10C subset: `3 passed`.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
```

Expected current result: writes a versioned Stage 10C packet under `data/prediction_outputs/phase1_top50/`, prints `stage10c_prediction_output_packet_created`, keeps `benchmark_claim=false`, and reports `model_output_rows: 250` plus `top10_primary_rows: 50`.

```powershell
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

Expected current result: `STAGE10C_COMPLETION_VALIDATION PASSED` with `model_output_rows: 250` and `top10_primary_rows: 50`.

## Commands Not Yet Available

- Stage 2 now has focused executable dataset-contract tests, Stage 3 now has executable feature/label contract tests, Stage 4 now has executable split/leakage/artifact-packet/runner-gate contract tests, Stage 5 now has executable model/prediction tests, Stage 6 now has executable evaluation metric-contract tests, Stage 7C now has executable diagnostic tests, Stage 8 now has executable raw-update script tests, and Stage 10C now has executable prediction-output packet tests; the OHLCV salvage audit remains evidence validation, not a dataset test suite.
- The active Stage 2 input-readiness gate is not a dataset builder; the Stage 2 builder lives behind `event_state_forecasting.cli.build_benchmark_dataset`.
- Stage 3 feature/label tests now exist under `tests/features/`; `scripts/validate_stage3_readiness.py` is still a readiness gate, and `scripts/validate_stage3_completion.py` validates materialized artifacts.
- Active model contract tests: `python -m pytest "tests/models"`.
- Active evaluation contract tests: `python -m pytest "tests/evaluation"`.
- No single active full-pipeline command exists that rebuilds Stage 2 through Stage 6 end to end in one invocation; run stage CLIs and validators separately.
- Standalone provider-ledger sanitization, provider normalization CLIs, operations rerun orchestration, and broader expansion-family commands remain pending unless explicitly implemented.
