# Stage 2 Materialization - 2026-05-14

## Status

- Stage 2 dataset materialization is complete for the approved `phase1_top50` family.
- This is not a feature artifact, label artifact, split artifact, model run, metric output, benchmark packet, or benchmark result.

## Artifacts

- Dataset root: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/`
- Partitioned panel: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/benchmark_panel.parquet/`
- Dataset manifest: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/dataset_manifest.json`
- Row-universe digest: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/row_universe_digest.json`
- Clean-window record: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/clean_window_decision.json`
- CVX derived patch manifest: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/cvx_derived_ohlc_patch_manifest.json`

## Dataset Identity

- Dataset version: `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086`
- Row-universe digest: `6868e3b80086196385c3570f709b8bf747ec3f5afebb46dc624dd69b117cb58c`
- Source digest: `d26bdc8584c7f8b5cd423ff48ab2ab95a9b460d9c09488a3210beeca533dec89`

## Row Counts

- Tickers: `50` approved top-50 tickers.
- Support ticker: `SPY`, excluded from dataset rows.
- Clean window: `2024-04-01` through `2026-02-13`.
- Common as-of dates: `471`.
- Rows: `117750`.
- Per-horizon rows: `23550` for each of `1d`, `5d`, `10d`, `20d`, and `60d`.

## Availability And Limitations

- No-news rows are preserved with `no_news_flag` and `empty_event_state_flag`.
- Rows with same-date raw news count: `44755`.
- No-news rows: `72995`.
- Alpha Vantage provider-level article completeness is not claimed; truncation-risk rows remain flagged.
- Active split-adjustment method is still not selected.
- Feature values, label values, splits, preprocessing-fit manifests, predictions, metrics, and benchmark outputs remain future-stage work.

## CVX Patch Handling

- Raw Twelve Data files were not modified.
- Selected full-window Stage 2 source rows required `0` derived OHLC patch events.
- The 2010 coverage audit still reports `1` CVX OHLC patch candidate from duplicate-window evidence for `2023-06-05`; the patch manifest records derived patch values without mutating raw data.

## Validation Evidence

- `python -m py_compile @(Get-ChildItem -Path "src","scripts","tests" -Filter "*.py" -Recurse | ForEach-Object { $_.FullName })` completed without output before materialization.
- `python -m pytest "tests/data/test_contracts_contract.py" "tests/dataset/test_row_universe_contract.py" "tests/dataset/test_panel_builder_contract.py"` passed with `8 passed`.
- Final completion validation is recorded in `data/manifests/stage2_completion_validation_2026-05-14.json` after running `python scripts/validate_stage2_completion.py --write`.
