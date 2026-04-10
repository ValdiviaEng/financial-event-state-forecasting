# Testing Commands

This document lists manual commands for running the test suite and the new expanded testing layers.

Important notes:
- These commands assume you want to run tests manually.
- The recommended environment is your WSL `ai` virtual environment.
- Live API tests are opt-in and should not be part of the default test run.

## 1. Activate the recommended environment

From inside WSL:

```bash
cd ~/1_Projects/AA/event-state-forecasting
source ~/venvs/ai/bin/activate
```

From Windows shell using WSL:

```bash
wsl bash -lc "cd /home/berserker/1_Projects/AA/event-state-forecasting && source ~/venvs/ai/bin/activate && python -V"
```

## 2. Run the full test suite

From inside WSL:

```bash
pytest -q
```

From Windows shell using WSL:

```bash
wsl bash -lc "cd /home/berserker/1_Projects/AA/event-state-forecasting && source ~/venvs/ai/bin/activate && pytest -q"
```

## 3. Run existing core test groups

### Data contracts

```bash
pytest tests/test_data_contracts.py -q
```

### Provider clients

```bash
pytest tests/test_provider_clients.py -q
```

### Market pipeline

```bash
pytest tests/test_market_pipeline.py -q
```

### Corporate actions

```bash
pytest tests/test_corporate_actions.py -q
```

### News pipeline

```bash
pytest tests/test_news_pipeline.py -q
```

### Alignment

```bash
pytest tests/test_alignment.py -q
```

### Leakage

```bash
pytest tests/test_leakage.py -q
```

### Labels

```bash
pytest tests/test_labels.py -q
```

### Event state

```bash
pytest tests/test_event_state.py -q
```

### Walk-forward splits

```bash
pytest tests/test_walk_forward.py -q
```

### Company KB pipeline

```bash
pytest tests/test_company_kb_pipeline.py -q
```

### Modeling dataset assembly

```bash
pytest tests/test_modeling_dataset.py -q
```

### Baseline training

```bash
pytest tests/test_baseline_training.py -q
```

### Multimodal training

```bash
pytest tests/test_multimodal_training.py -q
```

### Evaluation tools

```bash
pytest tests/test_evaluation_tools.py -q
```

### Ablation runner

```bash
pytest tests/test_ablation_runner.py -q
```

## 4. Run newly added expanded offline tests

### Text normalization

```bash
pytest tests/test_text_normalization.py -q
```

### Hashing and cache identity

```bash
pytest tests/test_hashing.py -q
```

### News deduplication rules

```bash
pytest tests/test_news_deduplication.py -q
```

### Dataset integrity

```bash
pytest tests/test_dataset_integrity.py -q
```

### Research integrity

```bash
pytest tests/test_research_integrity.py -q
```

### Reproducibility end-to-end checks

```bash
pytest tests/test_reproducibility_end_to_end.py -q
```

### End-to-end mini pipeline

```bash
pytest tests/test_end_to_end_minipipeline.py -q
```

## 5. Run grouped suites by intent

### Fast data correctness suite

```bash
pytest \
  tests/test_data_contracts.py \
  tests/test_text_normalization.py \
  tests/test_hashing.py \
  tests/test_news_deduplication.py \
  tests/test_dataset_integrity.py -q
```

### Temporal safety suite

```bash
pytest \
  tests/test_alignment.py \
  tests/test_leakage.py \
  tests/test_walk_forward.py \
  tests/test_research_integrity.py -q
```

### Modeling and evaluation suite

```bash
pytest \
  tests/test_baseline_training.py \
  tests/test_multimodal_training.py \
  tests/test_evaluation_tools.py \
  tests/test_ablation_runner.py -q
```

### Full synthetic end-to-end suite

```bash
pytest \
  tests/test_market_pipeline.py \
  tests/test_corporate_actions.py \
  tests/test_news_pipeline.py \
  tests/test_event_state.py \
  tests/test_modeling_dataset.py \
  tests/test_end_to_end_minipipeline.py -q
```

## 6. Run all non-live tests only

```bash
pytest tests -q --ignore=tests/integration
```

## 7. Run opt-in live API integration tests

These consume real API access and should be run manually and sparingly.

From inside WSL:

```bash
export RUN_LIVE_API_TESTS=true
pytest tests/integration/test_live_twelvedata.py -q
pytest tests/integration/test_live_finnhub.py -q
pytest tests/integration/test_live_sec.py -q
```

Run all live integration tests together:

```bash
export RUN_LIVE_API_TESTS=true
pytest tests/integration -q
```

From Windows shell using WSL:

```bash
wsl bash -lc "cd /home/berserker/1_Projects/AA/event-state-forecasting && source ~/venvs/ai/bin/activate && export RUN_LIVE_API_TESTS=true && pytest tests/integration -q"
```

## 8. Run smoke checks for tooling only

### Ruff

```bash
ruff check src tests
```

### Syntax compile check

```bash
python -m compileall src
```

## 9. Suggested execution order for manual validation

1. Fast data correctness suite
2. Temporal safety suite
3. Modeling and evaluation suite
4. Full synthetic end-to-end suite
5. Optional live integration tests

## 10. Practical caution for live tests

- Run live Twelve Data tests on a tiny symbol set only.
- Run live Finnhub tests on a small historical window only.
- Do not assume exact row counts for live providers.
- Treat live integration failures as either:
  - real code issues,
  - provider behavior drift,
  - quota/rate-limit/environment issues.

The offline test suite should remain the main correctness gate.
