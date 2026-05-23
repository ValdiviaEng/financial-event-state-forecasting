# Stage6Prompt

Status: executed on 2026-05-21 for Stage 6, Serious Benchmark Reporting. The completed run produced a full serious-run packet and a `clean_null` result class with `limitation_bearing` comparability; this is not a positive result claim.

## Mission

Compute approved metrics and diagnostics from saved out-of-sample predictions and frozen labels, validate lockbox integrity, produce comparison summary, classify the result, and preserve a complete serious-run artifact packet.

## Ownership

| Area | Owner |
| --- | --- |
| Metric computation | Agent under predeclared metric contract. |
| Diagnostic report | Agent under Option B contract. |
| Benchmark comparability classification | Agent, with user approval required for changes. |
| Final thesis interpretation | Agent reports evidence; user owns strategic decisions. |
| Artifact preservation | Agent. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `docs/Benchmark_Testing.md` | Required packet, metrics, diagnostics, comparability rules. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Saved prediction, lockbox, diagnostics, contamination blockers. |
| `ProjectDefinition.md` | Acceptable positive, conditional positive, clean null outcomes. |
| `ResearchTruth.md` | Current truth and unresolved risks. |
| Stage 5 outputs | Predictions, model artifacts, preprocessing manifests. |
| `configs/evaluation.yaml` | Active Stage 6 metric and diagnostic policy. |
| `docs/Detailed_Execution_Stages.md` | Stage 6 detailed requirements. |

## Inputs

| Input | Required handling |
| --- | --- |
| Saved predictions | Must be out-of-sample with row keys, fold IDs, horizon IDs, model IDs, dataset version. |
| Frozen labels | Must match dataset version and row keys. |
| Split manifest | Must define development folds, purge/embargo, lockbox boundary. |
| Preprocessing-fit manifest | Must prove train-only fit. |
| Resolved config | Must include model roster and metric/diagnostic policy. |
| Artifact packet | Must be complete before final claims. |

## Outputs

| Output | Required contents |
| --- | --- |
| Regression metrics | RMSE, MAE, out-of-sample `R2`, mean loss difference versus market-only baseline. |
| Ranking diagnostics | Spearman rank IC, Kendall rank correlation, directional hit diagnostic, top-minus-bottom diagnostic. |
| Overfitting diagnostics | Train-validation gap, fold dispersion, positive-fold/horizon rates, lockbox degradation, paired comparison, multiple-comparison note, search-space summary. |
| Comparison summary | Market-only, comparator, and event-state results under identical assumptions. |
| Benchmark comparability classification | Comparable, limitation-bearing, invalidated, or not comparable with reason. |
| Serious-run packet | Dataset, manifest, config, splits, preprocessing, predictions, metrics, diagnostics, summary. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Confirm Stages 0-5 are complete with evidence. | Dependency status. |
| 2 | Validate artifact packet before metrics. | Packet validation. |
| 3 | Validate saved predictions match frozen labels and split manifest. | Prediction/label validation. |
| 4 | Compute primary regression metrics. | Metric artifact. |
| 5 | Compute mandatory ranking diagnostics. | Ranking artifact. |
| 6 | Compute paired comparisons where assumptions hold. | Paired-test artifact. |
| 7 | Compute train-validation performance gaps. | Diagnostic table. |
| 8 | Compute development-fold mean and standard deviation. | Diagnostic table. |
| 9 | Compute positive-fold and positive-horizon improvement rates. | Diagnostic table. |
| 10 | Compute validation-to-lockbox degradation after development is frozen. | Lockbox diagnostic. |
| 11 | Add multiple-comparison and search-space notes. | Diagnostic narrative. |
| 12 | Build comparison summary and classify result. | Summary report. |
| 13 | Run benchmark comparability review. | Classification record. |
| 14 | Update memory and report evidence. | Event ledger and final response. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Metric contract tests | `python -m pytest "tests/evaluation"`. | Metrics use saved predictions and frozen labels. |
| Artifact packet validation | `python scripts/validate_stage6_completion.py --write`. | Full evidence packet present. |
| Prediction identity validation | Stage 6 prediction-label validation artifact. | Row keys and versions match. |
| Lockbox integrity review | Timeline and access check. | No forbidden lockbox use. |
| Overfitting diagnostic review | Required diagnostic field check. | No missing fields. |
| Comparability review | Apply invalidation triggers. | Classification explicit and evidence-backed. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Packet complete | All serious-run artifacts preserved. |
| Metrics valid | Computed only from saved out-of-sample predictions and frozen labels. |
| Diagnostics complete | Every Option B diagnostic present or explicitly blocked. |
| Lockbox clean | No tuning or selection used lockbox. |
| Result class justified | Positive, conditional positive, or clean null conclusion matches evidence. |
| Memory complete | Task, evidence, drift checkpoint, and reconciliation logged. |

## Execution Evidence

| Field | Value |
| --- | --- |
| Stage 6 artifact version | `phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1` |
| Stage 6 artifact root | `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/` |
| Result class | `clean_null` |
| Result reason | `event_state_did_not_clear_the_predeclared_short_horizon_primary_hurdle` |
| Comparability classification | `limitation_bearing` |
| Serious packet status | `passed` |
| Metric rows | `800` |
| Ranking diagnostic rows | `800` |
| Paired comparison rows | `800` |
| Completion validator | `python scripts/validate_stage6_completion.py --write` -> `STAGE6_COMPLETION_VALIDATION PASSED` |

Stage 6 preserved all five approved horizons in reporting. The predeclared result-class rule used primary horizons `1d`, `5d`, and `10d`; the event-state branch cleared `0/3` primary horizons in validation and `0/3` in lockbox on both primary loss deltas.

## Stop Conditions

Stop and ask before changing metrics after seeing results, excluding inconvenient horizons, changing model roster, rerunning lockbox repeatedly for debugging, reframing ranking diagnostics as primary, or claiming trading profitability.

## Final Response Requirements

Report artifact packet path, metrics, diagnostics, comparability classification, result class, validation outputs, limitations, and natural next steps.
