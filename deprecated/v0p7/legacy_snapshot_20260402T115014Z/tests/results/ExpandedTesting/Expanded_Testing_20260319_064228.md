# Expanded Testing Results (Offline)

- Timestamp: 2026-03-19 06:42:28 (WSL `date +%Y%m%d_%H%M%S` -> `20260319_064228`)
- Repo: `~/1_Projects/AA/event-state-forecasting`
- Environment: WSL + `source ~/venvs/ai/bin/activate`
- Python: 3.12.3
- Tooling: `ruff 0.15.6`, `pytest 8.4.2`
- Scope constraint honored: no `ExecutionFlow.md` real-data pipeline commands executed (no market/news/KB builds).

## Environment / cache safeguards used

To minimize repo writes from caches/bytecode:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export XDG_CACHE_HOME=/tmp/esf_cache
export HF_HOME=/tmp/esf_hf
export TORCH_HOME=/tmp/esf_torch
```

Pytest invoked with `-p no:cacheprovider`.

## Commands executed and outputs

### 1) Syntax compile check

Command:

```bash
python -m compileall src
```

Result: PASS (no compile errors reported).

### 2) Ruff lint

Command:

```bash
ruff check src tests --no-cache
```

Result: FAIL

```text
F401 [*] `json` imported but unused
 --> tests/test_research_integrity.py:4:8
help: Remove unused import: `json`

Found 1 error.
[*] 1 fixable with the `--fix` option.
```

### 3) Full offline pytest suite (excluding live integration)

Command:

```bash
pytest tests -q --ignore=tests/integration -p no:cacheprovider
```

Result: FAIL

- Tests: 101 passed, 1 failed
- Failed test: `tests/test_end_to_end_minipipeline.py::test_end_to_end_minipipeline_builds_train_evaluate_and_compare`

Failure (key lines):

```text
ValueError: Input X contains NaN.
Ridge does not accept missing values encoded as NaN natively.
```

Callsite:

```text
tests/test_end_to_end_minipipeline.py:169 -> train_market_baseline_fold(... model_name="ridge" ...)
src/models/trainer.py:127 -> model.fit(train_df[feature_columns]..., ...)
```

Notes:

- The fold filters rows with complete *targets* (`filter_rows_with_complete_targets(...)`) but does not filter/impute for NaNs in *features* before fitting sklearn Ridge.
- In this synthetic mini-panel, at least one selected market feature column contains NaN in the training slice, which triggers sklearn validation.

## Next actions (optional)

1) Fix the `ruff` failure by removing the unused `json` import in `tests/test_research_integrity.py`.
2) Decide how the baseline training path should handle missing feature values (drop rows with any NaNs in selected features, or add an imputer step to the sklearn pipeline) so `tests/test_end_to_end_minipipeline.py` can pass.
