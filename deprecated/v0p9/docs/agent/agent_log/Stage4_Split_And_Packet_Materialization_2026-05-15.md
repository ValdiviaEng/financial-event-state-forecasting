# Stage 4 Split And Packet Materialization - 2026-05-15

Status: Stage 4 split, lockbox, leakage, artifact-packet, and gate-safe runner artifacts were materialized for the approved Stage 3 feature/label artifact after user decisions froze the lockbox and fold cadence. This creates benchmark infrastructure only. It does not train models, create predictions, compute metrics, produce a comparison summary, or create a benchmark result.

## User Decisions Applied

| Decision area | Selected value |
| --- | --- |
| Final untouched lockbox | Last 20% of Stage 3 as-of dates. |
| Lockbox boundary | `2025-09-30` through `2026-02-13`. |
| Development fold cadence | Monthly validation. |
| Training window | Expanding training. |
| Initial training history | `126` trading dates. |
| Validation window | `21` trading dates per fold. |
| Purge/embargo basis | Approved maximum label horizon, `60` trading dates. |

## Artifacts

| Artifact | Path |
| --- | --- |
| Stage 4 artifact root | `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/` |
| Split manifest | `split_manifest.json` |
| Fold definitions | `fold_definitions.parquet` |
| Split assignments | `split_assignments.parquet` |
| Lockbox record | `lockbox_record.json` |
| Leakage validation | `leakage_validation.json` |
| Artifact-packet validation | `artifact_packet_validation.json` |
| Benchmark runner gate | `benchmark_runner_gate.json` |
| Completion validation | `data/manifests/stage4_completion_validation_2026-05-15.json` |

## Key Counts

| Field | Value |
| --- | --- |
| Input Stage 3 artifact version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1` |
| Stage 4 artifact version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1` |
| Stage 3 row count | `117750` |
| Fold count | `9` |
| Split assignment rows | `1059750` |
| Lockbox as-of dates | `95` |
| Lockbox row assignments per fold | `23750` |
| Validation rows across folds | `47250` |
| Training rows across folds | `472500` |
| Purged rows across folds | `43200` |
| Embargoed rows across folds | `91800` |
| Excluded rows across folds | `191250` |
| Row-universe digest | `6868e3b80086196385c3570f709b8bf747ec3f5afebb46dc624dd69b117cb58c` |

## Implemented Contract

| Area | Contract |
| --- | --- |
| Split schedule | Expanding walk-forward training with monthly validation windows. |
| Purge | Training rows whose label windows overlap validation are excluded. |
| Embargo | The 60 trading dates before each validation window are excluded from fitting and scoring. |
| Lockbox | Final 20% of Stage 3 as-of dates is reporting-only and excluded from development folds. |
| Leakage validation | Fails closed on row-role duplicates, train-label overlap, lockbox misuse, embargo fit misuse, and non-training preprocessing-fit allowance. |
| Artifact packet | Stage 4 pre-model packet passes; full serious-run packet remains blocked until preprocessing, predictions, metrics, diagnostics, and comparison summary exist. |
| Benchmark runner gate | Gate passes only as no-model orchestration; training, prediction, metrics, comparison summary, and serious claims are false. |

## Validation

| Command | Result |
| --- | --- |
| `python -m py_compile` over `src`, `scripts`, and `tests` Python files | Completed without output. |
| `python -m pytest "tests"` | `22 passed`. |
| `$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet` | Built Stage 4 artifacts with `9` folds and `1059750` assignment rows. |
| `python scripts/validate_stage4_completion.py --write` | `STAGE4_COMPLETION_VALIDATION PASSED`. |

## Limitations

- Stage 4 does not create models, preprocessing-fit artifacts, saved predictions, metrics, overfitting diagnostics, comparison summaries, or benchmark results.
- The full serious-run artifact packet intentionally remains blocked until Stage 5 and Stage 6 artifacts exist.
- Alpha Vantage provider-level article completeness is still not claimed; upstream truncation-risk flags remain part of the benchmark evidence chain.
- The active split-adjustment method remains unresolved as a future design item; Stage 4 uses the already materialized Stage 3 labels and does not mutate raw prices.

## Stage 5 Readiness

Stage 5 can now start model and comparator-ladder contract work against these frozen split artifacts. It still must freeze the exact comparator roster, implement fold-local preprocessing manifests, generate saved out-of-sample predictions, and preserve identical rows, labels, splits, and metric definitions before any metric or benchmark claim.
