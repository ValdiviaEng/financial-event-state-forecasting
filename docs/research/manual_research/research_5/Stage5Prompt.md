# Stage5Prompt

Status: execution prompt for Stage 5, Models And Comparator Ladder. Executed on 2026-05-21 for the approved sklearn pragmatic-broader roster. This stage produces model artifacts and saved out-of-sample predictions, not final benchmark conclusions.

## Mission

Implement the frozen market-only and event-state comparator ladder under identical rows, labels, splits, preprocessing rules, and metric definitions, then emit saved out-of-sample predictions and diagnostics.

## Ownership

| Area | Owner |
| --- | --- |
| Comparator roster freeze | User approval if roster is not already explicit. |
| Model implementation | Agent after tests/contracts. |
| Training discipline | Agent under Option B contract. |
| Saved predictions | Agent with schema validation. |
| Final interpretation | Deferred to Stage 6. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `ScopeDecisionLog.md` DQ-011 | Comparator ladder scope. |
| `ProjectDefinition.md` | Model and comparator definition. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Train-only preprocessing and saved-prediction rules. |
| `docs/Benchmark_Testing.md` | Metrics and comparability rules. |
| `configs/models.example.yaml` | Model config scaffold. |
| Stage 4 split/artifact outputs | Required training inputs. |
| `docs/Detailed_Execution_Stages.md` | Stage 5 detailed requirements. |

## Inputs

| Input | Required handling |
| --- | --- |
| Split manifest | Consume exactly; no model-specific row filtering. |
| Feature/label artifacts | Use identical rows across branches. |
| Frozen comparator roster | Must be explicit before serious model runs. |
| Model configs | Resolve and store before training. |
| Preprocessing policy | Fit learned transforms on train rows only. |

## Outputs

| Output | Required contents |
| --- | --- |
| Model artifacts | Model ID, family, config, fold, seed, training metadata. |
| Preprocessing-fit manifest | Transform type, fit rows, fold ID, parameters reference, validation status. |
| Saved predictions | Row key, fold ID, horizon ID, model ID, dataset version, prediction, split role. |
| Training diagnostics | Fit status, train metrics if allowed, warnings, limitations. |
| Search-space summary | Models, feature sets, horizons, metrics, tuning attempts. |
| Executable model tests | Comparator, gated fusion, training, inference, row equality. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Confirm Stage 4 split and artifact gates pass. | Dependency status. |
| 2 | Freeze comparator roster or request approval. | Roster record. |
| 3 | Define model IDs and allowed inputs. | Model registry/config. |
| 4 | Define hyperparameter search limits and seed policy. | Search-space record. |
| 5 | Write executable model and prediction tests. | Test files. |
| 6 | Implement market-only baseline family. | Model code/artifacts. |
| 7 | Implement approved broader comparator families if roster includes them. | Model code/artifacts. |
| 8 | Implement simple gated fusion event-state model. | Model code/artifacts. |
| 9 | Fit preprocessing on training rows only for each fold. | Preprocessing manifest. |
| 10 | Train models and produce saved out-of-sample predictions. | Prediction artifacts. |
| 11 | Validate row identity and prediction schema. | Validation output. |
| 12 | Update memory and stage evidence. | Event records. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Comparator ladder tests | `tests/models/test_comparator_ladder_contract.py`. | Roster and allowed inputs enforced. |
| Gated fusion tests | `tests/models/test_gated_fusion_contract.py`. | Model uses approved market/event-state inputs. |
| Training isolation tests | `tests/models/test_training_contract.py`. | Non-training preprocessing fit fails. |
| Saved prediction tests | `tests/models/test_saved_predictions_contract.py`. | Required prediction identity fields present. |
| Row equality checks | Future dataset/split validation. | Market-only and event-state rows identical. |
| Metric smoke tests | Future evaluation checks. | Metrics can consume saved predictions. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Roster frozen | Comparator list cannot change after result inspection. |
| Training isolated | Preprocessing and model fit use only allowed fold data. |
| Predictions saved | Out-of-sample prediction artifacts complete or exclusions explicit. |
| Search space recorded | Overfitting diagnostic inputs available. |
| No final claim | Stage 5 does not interpret results as thesis outcome. |

## Stop Conditions

Stop and ask before changing comparator ladder, adding unapproved model families, tuning on lockbox, dropping failed model families silently, or changing rows/horizons/metrics after seeing results.

## Final Response Requirements

Report roster, models implemented, tests run, prediction artifact status, preprocessing manifest status, search-space summary, and blockers for Stage 6.

## Execution Status

Stage 5 materialization exists at `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/`.

Current Stage 5 facts:

- comparator roster: `phase1_top50_pragmatic_broader_sklearn_v1`
- model count: `8`
- folds: `9`
- horizons: `5`
- model-fit records: `360`
- preprocessing-fit records: `360`
- saved prediction rows: `2088000`
- validation prediction rows: `378000`
- lockbox prediction rows: `1710000`
- benchmark claim: `false`
- metrics, overfitting diagnostics, comparison summary, and benchmark result: not created

The serious-run packet is still correctly blocked because `metrics`, `overfitting_diagnostic_report`, and `comparison_summary` are absent.
