# Stage 5 Model And Prediction Materialization - 2026-05-21

## Scope

Materialized Stage 5 model-output artifacts for the approved Stage 4 split artifact. This work creates model-fit records, fold-local preprocessing records, training diagnostics, search-space summary, and saved validation plus lockbox predictions. It does not create metrics, an overfitting diagnostic report, a comparison summary, a benchmark-runner result, or a benchmark claim.

## Owner Decisions Used

| Decision | Selected value |
| --- | --- |
| Comparator roster | Pragmatic broader sklearn roster. |
| Preprocessing | Model-specific safe train-only preprocessing. |
| Prediction scope | Development validation plus lockbox predictions. |
| Search policy | Tiny fixed, seed `1729`, no hyperparameter search. |

## Artifact Identity

| Field | Value |
| --- | --- |
| Stage 5 artifact version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1` |
| Stage 5 artifact root | `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/` |
| Input Stage 3 artifact | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1` |
| Input Stage 4 artifact | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1` |
| Row-universe digest | `6868e3b80086196385c3570f709b8bf747ec3f5afebb46dc624dd69b117cb58c` |

## Materialized Counts

| Count | Value |
| --- | ---: |
| Model IDs | `8` |
| Folds | `9` |
| Horizons | `5` |
| Model-fit records | `360` |
| Preprocessing-fit records | `360` |
| Saved prediction rows | `2088000` |
| Validation prediction rows | `378000` |
| Lockbox prediction rows | `1710000` |

## Model IDs

- `market_zero_excess_return`
- `market_train_mean`
- `market_ridge`
- `market_elastic_net`
- `market_random_forest`
- `market_hist_gradient_boosting`
- `market_mlp`
- `event_state_gated_fusion`

## Artifact Files

| File | Purpose |
| --- | --- |
| `model_manifest.json` | Stage 5 identity, counts, output paths, non-claims, and serious-packet status. |
| `resolved_model_config.json` | Exact resolved model config used for materialization. |
| `comparator_roster_record.json` | Frozen roster record with allowed inputs and seed/search policy. |
| `model_fit_manifest.parquet` | One row per model/fold/horizon fit. |
| `preprocessing_fit_manifest.parquet` | One row per model/fold/horizon preprocessing fit with train-only metadata. |
| `preprocessing_params/*.json` | Per-fit preprocessing parameter payloads and digests. |
| `saved_predictions.parquet` | Validation plus lockbox saved predictions with row keys and model/fold/horizon identity. |
| `training_diagnostics.parquet` | Fit status, warning messages, row counts, and non-metric training diagnostics. |
| `search_space_summary.json` | Fixed roster/search-space summary for later overfitting diagnostics. |
| `serious_packet_validation.json` | Full serious-run packet status after Stage 5. |

## Validation Evidence

Commands run:

- `python -m py_compile "src/event_state_forecasting/models/comparator_ladder.py" "src/event_state_forecasting/models/market_baselines.py" "src/event_state_forecasting/models/gated_fusion.py" "src/event_state_forecasting/models/training.py" "src/event_state_forecasting/models/inference.py" "src/event_state_forecasting/cli/train_models_and_predict.py" "scripts/validate_stage5_completion.py"`
- `python -m pytest "tests/models"`
- `$env:PYTHONPATH='src'; python -m event_state_forecasting.cli.train_models_and_predict`
- `python scripts/validate_stage5_completion.py --write`

Observed results:

- Stage 5 py_compile completed without output.
- Focused Stage 5 model tests: `12 passed`.
- Stage 5 build: `stage5_models_predictions_built model_count 8 prediction_row_count 2088000`.
- Stage 5 completion validation: `STAGE5_COMPLETION_VALIDATION PASSED`.

## Packet Status

The full serious-run packet is still `blocked_missing_required_members` because these required Stage 6 members do not exist:

- `metrics`
- `overfitting_diagnostic_report`
- `comparison_summary`

## Known Limitations

- No metric was computed.
- No model comparison was interpreted.
- No overfitting diagnostic report was created.
- No lockbox result was computed or interpreted.
- No benchmark claim is allowed from Stage 5 alone.
- Seven Elastic Net fit records have convergence warnings captured in `training_diagnostics.parquet`; they are training diagnostics, not result evidence.
- Alpha Vantage provider-level article completeness remains unclaimed; truncation-risk flags remain part of the upstream feature evidence.
