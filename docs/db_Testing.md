# Database And Dataset Testing

Status: active-root data-testing contract with Stage 6 benchmark reporting completed for the approved top-50 row universe, Stage 8 plan-first raw update tests added, and Stage 10C local prediction-output packet tests added. The repository now has raw JSON files, manifests, executable Stage 2 through Stage 8 plus Stage 10C contract tests, a partitioned Parquet Stage 2 panel, Stage 3 feature/label artifacts, Stage 4 split artifacts, Stage 5 model-output artifacts, Stage 6 metric/diagnostic/comparison artifacts, and Stage 10C local prediction-output artifacts.

Governing refinement: `docs/Data_Separation_And_Overfitting_Control.md` defines the required row identity, split manifest, preprocessing-fit manifest, and contamination blockers for future benchmark datasets.

## Current Raw Data Facts

- Canonical top-50 Alpha Vantage raw file coverage is complete at 850/850 windows after the 2026-05-06 raw merge.
- The top-50 raw merge copied 398 missing canonical files and did not overwrite existing destination files.
- The top-50 manifest reports 209143 feed rows, 92 likely truncated canonical windows, 10 empty-feed windows, and 8 retained non-canonical AAPL slice files.
- Complete raw file coverage does not prove provider-level article completeness or benchmark dataset readiness.
- Active raw Twelve Data OHLCV full-window files now exist for the approved top-50 plus SPY support for `2010-01-01` to `2026-05-22`; the latest coverage audit reports `50/50` top-50 full-window files, no post-first-available-date gaps, five late-start tickers, and one CVX OHLC ordering anomaly handled only by derived cleaning policy during dataset materialization.

## Required Raw Data Checks

- Universe row count and ticker normalization checks for `data/raw/universe/top50_slickcharts_2026-04-10.csv`.
- Canonical Alpha Vantage path coverage checks for all top-50 ticker/year windows.
- JSON parse and schema checks for `NEWS_SENTIMENT` payloads.
- Feed-row count summaries by ticker and year.
- Truncation flag checks for provider-limit rows.
- Empty-feed window checks with explicit status rather than silent drops.
- Duplicate or non-canonical raw-file detection.
- Credential-leak checks for request ledgers before commit, sharing, or publication.

## Current Stage 2 Dataset State

- `src/event_state_forecasting/data/contracts.py`, `src/event_state_forecasting/data/universe.py`, and `src/event_state_forecasting/dataset/` now include approved executable Stage 2 contract and panel-building code.
- `tests/data/test_contracts_contract.py`, `tests/dataset/test_row_universe_contract.py`, and `tests/dataset/test_panel_builder_contract.py` are executable Stage 2 tests.
- `src/event_state_forecasting/cli/build_benchmark_dataset.py` materializes the Stage 2 dataset.
- Active dataset root: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/`.
- Stage 2 artifacts include partitioned Parquet panel rows, `dataset_manifest.json`, `row_universe_digest.json`, `clean_window_decision.json`, and `cvx_derived_ohlc_patch_manifest.json`.
- `scripts/validate_stage2_inputs.py` remains an input-readiness gate; `scripts/validate_stage2_completion.py` validates the materialized artifact set.
- Future-stage `src/`, `configs/`, and `tests/` files remain comment-only unless explicitly converted for their stage.

## Current Stage 3 Feature And Label State

- `src/event_state_forecasting/features/` now includes approved executable Stage 3 market, news-alignment, event-state, no-news, embedding, and label code.
- `src/event_state_forecasting/cli/build_features_and_labels.py` materializes Stage 3 artifacts.
- Active Stage 3 configs exist at `configs/features.yaml` and `configs/labels.yaml`.
- Stage 3 artifacts exist under `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1/`.
- `scripts/validate_stage3_completion.py` validates the materialized Stage 3 artifact set.

## Current Stage 4 Split And Packet State

- `src/event_state_forecasting/split/` now includes approved executable Stage 4 lockbox, split, and leakage-check code.
- `src/event_state_forecasting/benchmark/artifact_packet.py` and `src/event_state_forecasting/benchmark/runner.py` now include approved executable packet and runner-gate code.
- Active Stage 4 configs exist at `configs/splits.yaml` and `configs/artifact_packet.yaml`.
- Stage 4 artifacts exist under `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/`.
- `scripts/validate_stage4_completion.py` validates the materialized Stage 4 artifact set.

## Current Stage 5 Model And Prediction State

- `src/event_state_forecasting/models/` now includes approved executable Stage 5 comparator-ladder, market-baseline, gated-fusion, train-only preprocessing, and saved-prediction schema code.
- `src/event_state_forecasting/cli/train_models_and_predict.py` materializes Stage 5 artifacts.
- Active Stage 5 config exists at `configs/models.yaml`.
- Stage 5 artifacts exist under `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/`.
- `scripts/validate_stage5_completion.py` validates the materialized Stage 5 artifact set.

## Current Stage 6 Metric And Reporting State

- `src/event_state_forecasting/evaluation/` now includes approved executable Stage 6 regression metric, ranking diagnostic, paired loss-delta, overfitting diagnostic, comparison-summary, and comparability code.
- `src/event_state_forecasting/cli/run_benchmark.py` materializes Stage 6 reporting artifacts from Stage 5 saved predictions.
- Active Stage 6 config exists at `configs/evaluation.yaml`.
- Stage 6 artifacts exist under `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/`.
- `scripts/validate_stage6_completion.py` validates the materialized Stage 6 artifact set.

## Required Benchmark Dataset Checks

- Stable dataset version and manifest.
- Stable row identity: ticker, as-of date, horizon, feature availability timestamp, label-window start and end, split role, fold ID when applicable, and lockbox flag when applicable.
- Identical row universe between market-only and event-state branches.
- Valid labels for all approved horizons.
- No-news indicators preserved.
- Split membership recorded and reproducible with purge/embargo row accounting and excluded-row reasons.
- Preprocessing-fit manifest proving learned transforms are fit only on training rows for each fold.
- No future information in features as of each prediction timestamp.

## Current Blockers

- Split-adjustment method is not selected.
- The Alpha Vantage truncation-refinement policy is not scientifically resolved; current dataset rows retain truncation-risk flags and make no provider-level article-completeness claim.
- Stage 6 train-validation gap diagnostic is explicitly blocked because Stage 5 saved no train predictions.
- API-key-bearing raw ledger handling must be sanitized or isolated before raw ledgers are committed or shared.
- Future-stage comment-only validation scaffold must remain non-executable until each stage is approved for conversion.
