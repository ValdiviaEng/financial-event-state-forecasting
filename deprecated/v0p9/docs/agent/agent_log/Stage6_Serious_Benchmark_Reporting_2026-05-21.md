# Stage 6 Serious Benchmark Reporting - 2026-05-21

## Scope

Materialized Stage 6 reporting artifacts for the approved Stage 5 saved-prediction artifact. This work creates regression metrics, ranking diagnostics, paired loss-delta summaries, an Option B overfitting diagnostic report, a comparison summary, a benchmark comparability record, and a full serious-run packet validation. The result class is `clean_null`; this is not a positive result claim or a trading-profitability claim.

## Owner Decisions Used

| Decision | Selected value |
| --- | --- |
| Comparison anchor | Strict market hurdle: best market-only model per horizon by validation RMSE then MAE. |
| Result rule | `short_horizon_primary_3_v1`, using `1d`, `5d`, and `10d` as primary horizons while reporting all five horizons. |
| Lockbox use | Final reporting read only, with no lockbox tuning or selection. |
| Paired comparison | Loss-delta summary without p-values. |

## Artifact Identity

| Field | Value |
| --- | --- |
| Stage 6 artifact version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1` |
| Stage 6 artifact root | `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/` |
| Input Stage 5 artifact | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1` |
| Row-universe digest | `6868e3b80086196385c3570f709b8bf747ec3f5afebb46dc624dd69b117cb58c` |

## Materialized Counts

| Count | Value |
| --- | ---: |
| Model IDs | `8` |
| Horizons | `5` |
| Metric rows | `800` |
| Ranking diagnostic rows | `800` |
| Paired comparison rows | `800` |
| Primary validation positive horizons | `0/3` |
| Primary lockbox positive horizons | `0/3` |

## Result Summary

| Field | Value |
| --- | --- |
| Result class | `clean_null` |
| Result reason | `event_state_did_not_clear_the_predeclared_short_horizon_primary_hurdle` |
| Comparability classification | `limitation_bearing` |
| Serious packet status | `passed` |
| Diagnostic status | `complete_with_explicit_train_gap_blocker` |

Selected strict market hurdles were `market_elastic_net` for `1d`, `10d`, `20d`, and `60d`, and `market_ridge` for `5d`. The event-state gated-fusion model did not improve on both primary loss deltas for any primary horizon in validation or lockbox.

## Artifact Files

| File | Purpose |
| --- | --- |
| `evaluation_manifest.json` | Stage 6 identity, counts, outputs, selected hurdles, result class, comparability, packet status, and limitations. |
| `resolved_evaluation_config.json` | Exact resolved Stage 6 evaluation policy. |
| `prediction_label_validation.json` | Saved-prediction and frozen-label identity validation. |
| `metrics.parquet` | Regression metrics and attached loss deltas. |
| `ranking_diagnostics.parquet` | Mandatory secondary ranking diagnostics. |
| `paired_comparisons.parquet` | Paired loss-delta summaries versus selected market hurdles. |
| `overfitting_diagnostic_report.json` | Option B diagnostics and explicit train-gap blocker. |
| `comparison_summary.json` | Result classification, selected market hurdles, topline metrics, ranking diagnostics, and non-claims. |
| `benchmark_comparability.json` | Limitation-bearing comparability classification. |
| `serious_packet_validation.json` | Full serious-run packet validation. |

## Validation Evidence

Commands run:

- `python -m py_compile "src/event_state_forecasting/evaluation/regression.py" "src/event_state_forecasting/evaluation/ranking.py" "src/event_state_forecasting/evaluation/statistical_tests.py" "src/event_state_forecasting/evaluation/comparison_summary.py" "src/event_state_forecasting/cli/run_benchmark.py" "scripts/validate_stage6_completion.py"`
- `python -m pytest "tests/evaluation"`
- `$env:PYTHONPATH='src'; python -m event_state_forecasting.cli.run_benchmark`
- `python scripts/validate_stage6_completion.py --write`

Observed results:

- Stage 6 py_compile completed without output.
- Focused Stage 6 evaluation tests: `4 passed`.
- Stage 6 build: `stage6_serious_benchmark_reporting_built result_class clean_null comparability limitation_bearing`.
- Stage 6 completion validation: `STAGE6_COMPLETION_VALIDATION PASSED`.

## Known Limitations

- Alpha Vantage provider-level article completeness remains unclaimed.
- Active split-adjustment method is not selected; Stage 2 uses a derived CVX manifest and does not mutate raw Twelve Data values.
- Train-validation gap is explicitly blocked because Stage 5 saved validation and lockbox predictions only.
- No p-values or statistical-significance claims are reported.
- No trading profitability, direct sentiment-string ablation, or provider-level article-completeness claim is made.
