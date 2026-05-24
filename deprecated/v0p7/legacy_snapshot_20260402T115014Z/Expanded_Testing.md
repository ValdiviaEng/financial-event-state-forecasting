# Expanded Testing

This document explains **all current test files** in the repository, what each test is supposed to validate, what inputs it needs, whether any earlier execution from `ExecutionFlow.md` is required, and the exact commands to run each test manually.

Important constraints:
- This document is descriptive only.
- It does **not** run any tests.
- It assumes the current repository state described in:
  - `README.md`
  - `Complete_guidebook.txt`
  - `execution_plan.txt`
  - `ExecutionFlow.md`

## 1. Global testing philosophy

The repository now has four practical testing layers:

1. **Pure offline unit tests**
   - no real API calls
   - synthetic data only
   - fastest and safest correctness gate

2. **Synthetic integration tests**
   - still offline
   - exercise multiple modules together
   - validate end-to-end logic without consuming API quota

3. **Training and evaluation smoke tests**
   - offline
   - use synthetic final panels
   - validate checkpointing, prediction export, and metric logic

4. **Opt-in live provider tests**
   - use your real `.env`
   - consume real API access
   - should only be run manually and sparingly

## 2. Environment prerequisites

All tests assume the recommended WSL environment.

### Activate environment

```bash
cd ~/1_Projects/AA/event-state-forecasting
source ~/venvs/ai/bin/activate
```

### Recommended pre-test sanity checks

```bash
python -m compileall src
ruff check src tests
```

### Do any tests require previous execution from `ExecutionFlow.md`?

Most tests do **not** require any prior pipeline execution because they create synthetic or temporary inputs internally.

The only tests that depend on real external state are:
- `tests/integration/test_live_twelvedata.py`
- `tests/integration/test_live_finnhub.py`
- `tests/integration/test_live_sec.py`

For those live tests you need at minimum:
- `ExecutionFlow.md` section `1. One-time setup`
- a valid local `.env`
- network access
- available API quota

No current test requires you to pre-build the full real database/panel before running it.

## 3. Recommended execution order

Run tests in this order:

1. Fast offline unit tests
2. Temporal/leakage tests
3. Pipeline integration tests
4. Training/evaluation smoke tests
5. Synthetic end-to-end mini pipeline
6. Optional live integration tests

This order minimizes wasted time and catches foundational issues early.

## 4. Test inventory with purpose, prerequisites, and commands

---

## 4.1 Core schema and provider tests

### `tests/test_data_contracts.py`

Purpose:
- validate canonical schemas,
- catch missing required columns,
- enforce uniqueness rules,
- validate manifests.

Inputs required:
- none beyond installed environment.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- always,
- especially after changing schemas, manifests, or final panel structure.

Command:

```bash
pytest tests/test_data_contracts.py -q
```

---

### `tests/test_provider_clients.py`

Purpose:
- validate normalized behavior of:
  - Twelve Data client
  - Finnhub client
  - SEC EDGAR client
  - split-event normalization
  - universe builder basics

Inputs required:
- none; uses synthetic payloads.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing provider parsing,
- after changing ticker normalization,
- after changing split normalization behavior.

Command:

```bash
pytest tests/test_provider_clients.py -q
```

---

## 4.2 Text, hashing, and deduplication tests

### `tests/test_text_normalization.py`

Purpose:
- validate conservative text normalization,
- ensure canonical text construction behaves exactly as expected,
- protect embedding-cache input consistency.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing `src/features/news_text.py`.

Command:

```bash
pytest tests/test_text_normalization.py -q
```

---

### `tests/test_hashing.py`

Purpose:
- validate deterministic hashing for text and records,
- ensure normalization-equivalent text hashes identically,
- ensure changed canonical text changes the hash.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing `src/utils/hashing.py`,
- after changing canonical text rules.

Command:

```bash
pytest tests/test_hashing.py -q
```

---

### `tests/test_news_deduplication.py`

Purpose:
- validate URL-first deduplication,
- validate fallback-hash deduplication when URL is missing,
- ensure distinct articles are not collapsed incorrectly.

Inputs required:
- none; uses synthetic article records.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing `src/data/news_pipeline.py`,
- after changing dedupe rules or URL normalization.

Command:

```bash
pytest tests/test_news_deduplication.py -q
```

---

## 4.3 Market and corporate-action pipeline tests

### `tests/test_market_pipeline.py`

Purpose:
- validate incremental market-update planning,
- validate repair-window creation,
- validate raw/interim/quality/manifest writes for market ingestion,
- ensure reruns do not duplicate `(ticker, date)` rows.

Inputs required:
- none; uses synthetic client behavior and temp paths.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/data/incremental_updates.py`
  - `src/data/price_pipeline.py`
  - `src/cli/build_market_data.py`

Command:

```bash
pytest tests/test_market_pipeline.py -q
```

---

### `tests/test_corporate_actions.py`

Purpose:
- validate split-adjustment math,
- verify cumulative factor construction,
- verify price and volume adjustment directions,
- verify missing-split mitigation behavior,
- verify adjusted-price writing through the pipeline.

Inputs required:
- none; uses synthetic split scenarios.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/data/corporate_actions.py`
  - split adjustment rules
  - adjusted-price pipeline integration.

Command:

```bash
pytest tests/test_corporate_actions.py -q
```

---

## 4.4 News pipeline and temporal alignment tests

### `tests/test_alignment.py`

Purpose:
- validate timezone normalization,
- validate market-close handling,
- validate after-hours rollover,
- validate weekend rollover,
- validate `asof_trade_date` annotation logic.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/utils/time_and_calendars.py`
  - `src/split/alignment_rules.py`

Command:

```bash
pytest tests/test_alignment.py -q
```

---

### `tests/test_news_pipeline.py`

Purpose:
- validate raw/interim news ingestion,
- validate deduplication,
- validate article enrichment,
- validate quality-report and manifest writing,
- validate dry-run request planning.

Inputs required:
- none; uses fake Finnhub client and temp paths.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/data/news_pipeline.py`
  - `src/cli/build_news_data.py`
  - article enrichment logic.

Command:

```bash
pytest tests/test_news_pipeline.py -q
```

---

## 4.5 Company KB tests

### `tests/test_company_kb_pipeline.py`

Purpose:
- validate SEC KB table generation,
- validate mapping and alias table generation,
- validate KB quality-report and manifest writing,
- validate universe enrichment hooks.

Inputs required:
- none; uses synthetic SEC payloads.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/data/company_kb_pipeline.py`
  - `src/cli/build_company_kb.py`
  - `src/data/universe_builder.py`

Command:

```bash
pytest tests/test_company_kb_pipeline.py -q
```

---

## 4.6 Feature, label, embedding, and event-state tests

### `tests/test_labels.py`

Purpose:
- validate forward and excess return construction,
- validate missing-horizon behavior,
- validate direction/downside label generation,
- enforce adjusted-price requirement.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing `src/features/labels.py`.

Command:

```bash
pytest tests/test_labels.py -q
```

---

### `tests/test_event_state.py`

Purpose:
- validate embedding-cache reuse/invalidation,
- validate recency-weighted event-state aggregation,
- validate no-news fallback,
- validate event-state stability across reruns.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/features/news_embeddings.py`
  - `src/features/event_state.py`

Command:

```bash
pytest tests/test_event_state.py -q
```

---

## 4.7 Dataset integrity and final panel tests

### `tests/test_modeling_dataset.py`

Purpose:
- validate final panel assembly,
- ensure unique `(ticker, date)` rows,
- validate optional branch joins,
- validate manifest writing.

Inputs required:
- none; uses synthetic panel inputs.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing:
  - `src/data/modeling_dataset.py`
  - `src/cli/build_modeling_dataset.py`

Command:

```bash
pytest tests/test_modeling_dataset.py -q
```

---

### `tests/test_dataset_integrity.py`

Purpose:
- validate branch tracking in final panels,
- validate manifest source-table correctness,
- validate company-feature merges do not create duplicates,
- validate split-adjusted flag persistence.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing final-panel joins,
- after changing manifest generation,
- after changing optional branch behavior.

Command:

```bash
pytest tests/test_dataset_integrity.py -q
```

---

## 4.8 Temporal validation and leakage tests

### `tests/test_walk_forward.py`

Purpose:
- validate chronological split generation,
- validate reproducibility,
- validate purge-and-embargo behavior,
- validate non-overlap.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing split logic.

Command:

```bash
pytest tests/test_walk_forward.py -q
```

---

### `tests/test_leakage.py`

Purpose:
- validate past-only feature construction,
- validate future-only labels,
- validate adjusted-price enforcement,
- validate overlap detection,
- validate scaler contamination checks,
- validate misaligned article date detection.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

When to run:
- after changing features,
- after changing labels,
- after changing leakage guardrails.

Command:

```bash
pytest tests/test_leakage.py -q
```

---

### `tests/test_research_integrity.py`

Purpose:
- validate run comparability assumptions,
- ensure baseline and multimodal use the same fold row universe,
- ensure future profile dates are rejected.

Inputs required:
- PyTorch required for the multimodal comparability portion.

Requires prior `ExecutionFlow.md` work?
- No, but the environment must support the current multimodal implementation.

When to run:
- after changing:
  - fold construction
  - run-summary structure
  - multimodal training data flow

Command:

```bash
pytest tests/test_research_integrity.py -q
```

---

## 4.9 Reproducibility and synthetic end-to-end tests

### `tests/test_reproducibility_end_to_end.py`

Purpose:
- validate deterministic embedding-cache behavior,
- validate run-metadata persistence.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

Command:

```bash
pytest tests/test_reproducibility_end_to_end.py -q
```

---

### `tests/test_end_to_end_minipipeline.py`

Purpose:
- run a synthetic mini version of the entire pipeline,
- verify final panel, baseline, multimodal, evaluation, and ablation compatibility.

Inputs required:
- PyTorch required.

Requires prior `ExecutionFlow.md` work?
- No. It builds synthetic artifacts internally.

When to run:
- before trusting large real-data experiments,
- after major cross-module refactors.

Command:

```bash
pytest tests/test_end_to_end_minipipeline.py -q
```

---

## 4.10 Baseline and multimodal training tests

### `tests/test_baseline_training.py`

Purpose:
- validate market-only training path,
- checkpoint writing,
- prediction export,
- deterministic ridge behavior.

Inputs required:
- none for ridge/elastic-net path,
- PyTorch required only if you later expand tests toward the market MLP path.

Requires prior `ExecutionFlow.md` work?
- No.

Command:

```bash
pytest tests/test_baseline_training.py -q
```

---

### `tests/test_multimodal_training.py`

Purpose:
- validate multimodal forward pass,
- validate multimodal batch schema,
- validate tiny-subset overfit,
- validate prediction export format parity.

Inputs required:
- PyTorch required.

Requires prior `ExecutionFlow.md` work?
- No. Uses synthetic final-panel-like data.

Command:

```bash
pytest tests/test_multimodal_training.py -q
```

---

## 4.11 Evaluation and ablation tests

### `tests/test_evaluation_tools.py`

Purpose:
- validate regression/classification/ranking metrics,
- validate calibration helpers,
- validate statistical comparison helpers,
- validate machine-readable evaluation outputs.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

Command:

```bash
pytest tests/test_evaluation_tools.py -q
```

---

### `tests/test_ablation_runner.py`

Purpose:
- validate run-summary loading,
- validate comparability checks,
- validate ablation summary aggregation.

Inputs required:
- none.

Requires prior `ExecutionFlow.md` work?
- No.

Command:

```bash
pytest tests/test_ablation_runner.py -q
```

---

## 4.12 Live API integration tests

These are the only tests that depend on your real local `.env` and live provider access.

Required minimum prior steps from `ExecutionFlow.md`:
- `1.1 Enter WSL and activate the recommended environment`
- `1.2 Install or refresh dependencies`
- `1.4 Verify required local files exist`

Additional live-test-specific requirement:

```bash
export RUN_LIVE_API_TESTS=true
```

### `tests/integration/test_live_twelvedata.py`

Purpose:
- verify small real Twelve Data requests,
- verify dot ticker handling on live provider responses.

Required inputs:
- valid `TWELVE_DATA_API_KEY`
- live internet access
- available quota

Requires previous `ExecutionFlow.md` data-building stages?
- No.
- This is a direct provider verification test.

Command:

```bash
pytest tests/integration/test_live_twelvedata.py -q
```

---

### `tests/integration/test_live_finnhub.py`

Purpose:
- verify a small live Finnhub company-news request,
- verify basic normalization on real returned data.

Required inputs:
- valid `FINNHUB_API_KEY`
- live internet access
- available quota

Requires previous `ExecutionFlow.md` data-building stages?
- No.

Command:

```bash
pytest tests/integration/test_live_finnhub.py -q
```

---

### `tests/integration/test_live_sec.py`

Purpose:
- verify live SEC submissions fetch,
- verify company metadata and ticker/CIK extraction.

Required inputs:
- valid `SEC_USER_AGENT`
- live internet access

Requires previous `ExecutionFlow.md` data-building stages?
- No.

Command:

```bash
pytest tests/integration/test_live_sec.py -q
```

---

## 5. Best practical order to run tests

### Level 1 - Fastest correctness gate

Run first after any refactor:

```bash
pytest \
  tests/test_data_contracts.py \
  tests/test_text_normalization.py \
  tests/test_hashing.py \
  tests/test_news_deduplication.py \
  tests/test_dataset_integrity.py -q
```

This checks:
- schemas
- text normalization
- hashing
- dedupe
- final panel integrity

No previous `ExecutionFlow.md` steps required.

---

### Level 2 - Temporal safety gate

```bash
pytest \
  tests/test_alignment.py \
  tests/test_leakage.py \
  tests/test_walk_forward.py \
  tests/test_research_integrity.py -q
```

This checks:
- alignment
- leakage
- split chronology
- purge/embargo
- run comparability

No real pipeline execution required.

---

### Level 3 - Pipeline integration gate

```bash
pytest \
  tests/test_provider_clients.py \
  tests/test_market_pipeline.py \
  tests/test_corporate_actions.py \
  tests/test_news_pipeline.py \
  tests/test_company_kb_pipeline.py \
  tests/test_modeling_dataset.py -q
```

This checks:
- provider parsing
- market pipeline
- split pipeline
- news pipeline
- KB pipeline
- final panel assembly

No real provider execution required.

---

### Level 4 - Modeling and evaluation gate

```bash
pytest \
  tests/test_labels.py \
  tests/test_event_state.py \
  tests/test_baseline_training.py \
  tests/test_multimodal_training.py \
  tests/test_evaluation_tools.py \
  tests/test_ablation_runner.py -q
```

This checks:
- labels
- event states
- market-only training
- multimodal training
- evaluation
- ablations

Requires PyTorch for the multimodal portion.

---

### Level 5 - Full synthetic system gate

```bash
pytest \
  tests/test_reproducibility_end_to_end.py \
  tests/test_end_to_end_minipipeline.py -q
```

This is the strongest offline system test.

Requires:
- PyTorch for the multimodal parts

Still does **not** require prior real-data execution from `ExecutionFlow.md`.

---

### Level 6 - Full offline suite

```bash
pytest tests -q --ignore=tests/integration
```

This is the current full offline correctness gate.

---

### Level 7 - Optional live provider verification

Only after the full offline suite passes:

```bash
export RUN_LIVE_API_TESTS=true
pytest tests/integration -q
```

This validates real provider behavior but is not the primary correctness gate.

## 6. Which tests require real pipeline outputs from `ExecutionFlow.md`?

Current answer: **almost none**.

### No prior real-data pipeline execution required
These work entirely with synthetic or temporary inputs:
- `tests/test_data_contracts.py`
- `tests/test_provider_clients.py`
- `tests/test_text_normalization.py`
- `tests/test_hashing.py`
- `tests/test_news_deduplication.py`
- `tests/test_market_pipeline.py`
- `tests/test_corporate_actions.py`
- `tests/test_news_pipeline.py`
- `tests/test_alignment.py`
- `tests/test_leakage.py`
- `tests/test_labels.py`
- `tests/test_event_state.py`
- `tests/test_walk_forward.py`
- `tests/test_company_kb_pipeline.py`
- `tests/test_modeling_dataset.py`
- `tests/test_baseline_training.py`
- `tests/test_multimodal_training.py`
- `tests/test_evaluation_tools.py`
- `tests/test_ablation_runner.py`
- `tests/test_dataset_integrity.py`
- `tests/test_research_integrity.py`
- `tests/test_reproducibility_end_to_end.py`
- `tests/test_end_to_end_minipipeline.py`

### Require only setup, not pipeline artifacts
These need the environment and `.env`, but not previously built datasets:
- `tests/integration/test_live_twelvedata.py`
- `tests/integration/test_live_finnhub.py`
- `tests/integration/test_live_sec.py`

### Optional manual post-flow validation outside pytest
If you want to validate real built artifacts after `ExecutionFlow.md`, use:
- `docs/testing_commands.md`
- and the sanity checkpoints in `ExecutionFlow.md` section `8. Sanity checkpoints you should not skip`

## 7. Best workflow for real experimentation

If your goal is to safely move into real pilot or full experiments, use this order:

1. Activate env
2. Run tooling checks
3. Run the full offline suite
4. Optionally run live provider tests
5. Follow `ExecutionFlow.md` prototype real-data flow
6. Re-run the full offline suite
7. Train baseline
8. Train multimodal
9. Evaluate and compare runs

## 8. Commands summary

### Full offline suite

```bash
pytest tests -q --ignore=tests/integration
```

### Full live suite

```bash
export RUN_LIVE_API_TESTS=true
pytest tests/integration -q
```

### Full all-tests sweep

Only run this when you intentionally want both offline and live coverage together:

```bash
export RUN_LIVE_API_TESTS=true
pytest -q
```

That is **not** the recommended default.

## 9. Final practical note

The strongest current test command for everyday development is still:

```bash
pytest tests -q --ignore=tests/integration
```

The strongest current synthetic system test is:

```bash
pytest tests/test_end_to_end_minipipeline.py -q
```

The strongest current real-provider verification command is:

```bash
export RUN_LIVE_API_TESTS=true
pytest tests/integration -q
```

Use them in that order.
