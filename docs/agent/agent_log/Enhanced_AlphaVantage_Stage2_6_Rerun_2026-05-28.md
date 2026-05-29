# Enhanced Alpha Vantage Stage 2-6 Rerun - 2026-05-28

## Scope
- User-approved local rerun from the versioned merged Alpha Vantage raw root through Stage 2, Stage 3, Stage 4, Stage 5, Stage 6, and baseline comparison artifacts.
- No live provider calls were made.
- Canonical `data/raw/alphavantage/` was not overwritten.
- Previous datasets, models, benchmark runs, and raw artifacts were preserved.
- This evidence does not approve positive benchmark language or benchmark-comparability promotion.

## Inputs
- Merged Alpha Vantage root: `data/raw/alphavantage_merged_versions/alphavantage_canonical_plus_zip2_extended_granularity__20260528T045221Z/alphavantage/`
- Baseline Stage 6 root: `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/`
- Wrapper: `scripts/run_enhanced_alphavantage_stage2_6_pipeline.py`
- Historical Stage 2-6 implementation source: `deprecated/v0p9/src/`, loaded under its original import name by a local alias.

## Outputs
- Stage 2 root: `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086/`
- Stage 3 root: `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1/`
- Stage 4 root: `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/`
- Stage 5 root: `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/`
- Stage 6 root: `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/`
- Comparison JSON: `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/enhanced_vs_baseline_comparison.json`
- Comparison Markdown: `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/enhanced_vs_baseline_comparison.md`

## Key Counts
- Stage 2 row count: `117750`.
- Stage 2 rows with news: `82225`.
- Stage 2 no-news rows: `35525`.
- Stage 2 provider-truncation-risk rows: `60565`.
- Stage 3 aligned news rows: `166711`.
- Stage 3 deduplicated article count: `274379`.
- Stage 3 raw article source occurrence count: `495115`.
- Stage 3 cross-file duplicate article occurrences removed: `220736`.
- Stage 3 source file count: `684`.
- Stage 5 saved prediction rows: `2088000`.
- Stage 5 model count: `8`.
- Stage 6 result class: `clean_null`.
- Stage 6 comparability classification: `limitation_bearing`.
- Comparison baseline aligned news rows: `67840`.
- Comparison enhanced aligned news rows: `166711`.
- Comparison metric rows: `10` event-state aggregate deltas.

## Validation
- `python -m py_compile scripts/run_enhanced_alphavantage_stage2_6_pipeline.py scripts/_v0p9_package_alias.py scripts/validate_stage2_completion.py scripts/validate_stage3_completion.py scripts/validate_stage4_completion.py scripts/validate_enhanced_stage2_6_comparison.py`
- `source ~/venvs/ai/bin/activate && python scripts/validate_stage2_completion.py --dataset-root data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086`
- `source ~/venvs/ai/bin/activate && python scripts/validate_stage3_completion.py --artifact-root data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1`
- `source ~/venvs/ai/bin/activate && python scripts/validate_stage4_completion.py --artifact-root data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1`
- `source ~/venvs/ai/bin/activate && python scripts/validate_stage5_completion.py --model-root data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1`
- `source ~/venvs/ai/bin/activate && python scripts/validate_stage6_completion.py --stage6-root data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1`
- `source ~/venvs/ai/bin/activate && python scripts/validate_enhanced_stage2_6_comparison.py --comparison-json data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_c82c06990ba7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/enhanced_vs_baseline_comparison.json`

Observed validation results:
- `STAGE2_COMPLETION_VALIDATION PASSED`
- `STAGE3_COMPLETION_VALIDATION PASSED`
- `STAGE4_COMPLETION_VALIDATION PASSED`
- `STAGE5_COMPLETION_VALIDATION PASSED`
- `STAGE6_COMPLETION_VALIDATION PASSED result_class: clean_null comparability: limitation_bearing`
- `ENHANCED_COMPARISON_VALIDATION PASSED baseline_result_class: clean_null enhanced_result_class: clean_null baseline_stage3_aligned_news_rows: 67840 enhanced_stage3_aligned_news_rows: 166711 metric_comparison_rows: 10`

## Interpretation Guardrails
- The enhanced run is local artifact evidence only.
- The original baseline Stage 6 result remains `clean_null` and comparability remains `limitation_bearing`.
- The enhanced Stage 6 result is also `clean_null` and comparability is also `limitation_bearing`.
- Provider-level article completeness remains unclaimed because the merged raw output still has likely truncated and empty files.
- Positive benchmark language remains unapproved.
- Benchmark-comparability promotion remains unapproved.
