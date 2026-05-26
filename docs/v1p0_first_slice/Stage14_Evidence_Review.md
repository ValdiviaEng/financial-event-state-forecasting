# v1p0 Stage 14 Integrated First-Slice Evidence Review

Status: smoke-complete under required venv

Updated: 2026-05-24

## Scope Executed

The v1p0 first slice was executed as a local smoke implementation. It creates active v1p0 contracts, modules, tests, and a smoke artifact path, but it does not rerun the historical benchmark or reinterpret Stage 6.

## Evidence

| Stage range | Evidence | Status |
| --- | --- | --- |
| Stage 00 | `python scripts/validate_agent_governance.py`; event ledger JSONL parse | passed |
| Stage 01 | `docs/v1p0_first_slice/Stage01_Reuse_Audit.md` | completed; rewrite selected |
| Stage 02-04 | `configs/v1p0_version_manifest.yaml`, `configs/feature_registry_v1p0.yaml`, `configs/market_features_v1p0.yaml`, `tests/v1p0/test_stage02_04_contracts.py` | passed smoke tests |
| Stage 05-09 | `src/event_state_forecasting/v1p0/features.py`, `modeling.py`, `tests/v1p0/test_stage05_09_models.py` | lag-linear and fixed-XGBoost smoke paths passed under `~/venvs/ai` |
| Stage 10-13 | `src/event_state_forecasting/v1p0/evaluation.py`, `reporting.py`, `tests/v1p0/test_stage10_13_evaluation_reporting.py` | passed smoke tests |
| Smoke usage | `scripts/run_v1p0_first_slice_smoke.py` | completed with `benchmark_claim=false` |

Detailed per-stage completion status is recorded in `docs/v1p0_first_slice/Stage_Completion_Register.md`.

## Validation Results

- `source ~/venvs/ai/bin/activate && python -m pytest tests/v1p0`: `5 passed`.
- `source ~/venvs/ai/bin/activate && python scripts/run_v1p0_first_slice_smoke.py`: completed and wrote `data/v1p0_first_slice_smoke/first_slice_smoke_v1/`.
- Fixed XGBoost produced toy smoke predictions under the required venv.

## Artifact Outputs

- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_lag_features.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_lag_linear_predictions.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_xgboost_v1_fixed_predictions.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/saved_predictions.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/metrics.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/strata.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/uncertainty.csv`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/report.html`
- `data/v1p0_first_slice_smoke/first_slice_smoke_v1/v1p0_first_slice_smoke_summary.json`

## Residual Limits

- Smoke artifacts are toy-data evidence only, not serious benchmark evidence.
- Broader FinBERT, TSMixer, nested Optuna, ensembles, and live/update-to-prediction execution remain deferred until separately approved.

## Non-Claims

This review does not claim a benchmark result, model improvement, live forecast, trading signal, service/API/dashboard, raw-data mutation, Stage 6 reinterpretation, or benchmark-comparability promotion.
