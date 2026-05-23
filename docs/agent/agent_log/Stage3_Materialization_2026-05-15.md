# Stage 3 Feature And Label Materialization - 2026-05-15

Status: Stage 3 materialized for the approved top-50 Stage 2 dataset after user decisions resolved the prior blockers. This creates feature and label artifacts only. It does not create splits, models, predictions, metrics, a benchmark runner, or a benchmark result.

## User Decisions Applied

| Decision area | Selected value |
| --- | --- |
| Stage 3 scope | Implement Stage 3. |
| Market reference for labels | Approved-universe average, not the support market fund. |
| Return definition | Simple return difference. |
| Reference average | Leave-one-out equal-weight average of the other approved companies. |
| Event-state embeddings | Deterministic local hash embeddings. |
| Scalar enrichments | Minimal safe set. |
| Configs | Active Stage 3 configs created. |

## Artifacts

| Artifact | Path |
| --- | --- |
| Stage 3 artifact root | `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1/` |
| Market features | `market_features.parquet` |
| Event-state features | `event_state_features.parquet` |
| Labels | `labels.parquet` |
| Aligned news audit table | `aligned_news.parquet` |
| Manifest | `feature_label_manifest.json` |
| Row-universe digest | `row_universe_digest.json` |
| Completion validation | `data/manifests/stage3_completion_validation_2026-05-15.json` |

## Key Counts

| Field | Value |
| --- | --- |
| Input dataset version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086` |
| Stage 3 artifact version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1` |
| Row count | `117750` |
| Row-universe digest | `6868e3b80086196385c3570f709b8bf747ec3f5afebb46dc624dd69b117cb58c` |
| Aligned news records | `67840` |
| Rows with aligned news | `46330` |
| No-news rows after Stage 3 alignment | `71420` |
| Provider truncation-risk rows preserved | `59610` |
| Event-state vector dimension | `8` |

## Implemented Contract

| Area | Contract |
| --- | --- |
| Market features | Same-row as-of-close market values and derived intraday fields only. |
| News alignment | Same trading day at or before close aligns to that day; after-close and non-trading-day records roll forward. |
| Event state | Deterministic hash embeddings pooled by mean over aligned articles. |
| No-news state | Rows with zero aligned articles remain and receive explicit no-news and empty-event-state flags. |
| Labels | Forward simple return minus leave-one-out equal-weight approved-universe simple return. |
| Row equality | Market features, event-state features, and labels preserve the Stage 2 row-universe digest. |

## Validation

| Command | Result |
| --- | --- |
| `python -m py_compile` over `src`, `scripts`, and `tests` Python files | Completed without output. |
| `python -m pytest "tests"` | `13 passed`. |
| `python scripts/validate_stage3_readiness.py --write` | `status: ready_for_stage3_implementation`. |
| `$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels --allow-overwrite` | Built Stage 3 artifacts with `117750` rows. |
| `python scripts/validate_stage3_completion.py --write` | `STAGE3_COMPLETION_VALIDATION PASSED`. |

## Limitations

- Alpha Vantage provider-level article completeness is still not claimed; truncation-risk flags are preserved.
- Hash embeddings are deterministic local representations, not semantic model embeddings.
- Stage 3 labels use the user-selected leave-one-out approved-universe reference, not the support market fund.
- Stage 3 does not create purged/embargoed splits, model training data splits, predictions, metrics, or benchmark conclusions.

## Stage 4 Readiness

Stage 4 can now start split and benchmark-runner contract work against these Stage 3 artifacts. It still must create purged-plus-embargoed split manifests, lockbox boundaries, leakage validation, artifact-packet checks, and later model/prediction gates before any serious benchmark claim.
