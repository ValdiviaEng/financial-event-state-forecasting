# Pipeline Testing

Status: active-root pipeline-testing contract with Stage 6 metric/diagnostic/comparison materialization evidenced, Stage 7C diagnostics validated separately, and Stage 8 plan-first raw update tests added. The current serious benchmark reporting packet passes with result class `clean_null` and comparability `limitation_bearing`.

Governing refinement: `docs/Data_Separation_And_Overfitting_Control.md` defines the Option B fail-closed gates for row separation, fold-local preprocessing, saved predictions, metric predeclaration, and overfitting diagnostics.

## Required Pipeline Gates

1. Governance/docs gate: required active-root docs exist and are internally consistent.
2. Raw-data gate: provider files parse, coverage is summarized, truncation risk is visible, and credential leaks are handled.
3. Dataset gate: benchmark dataset has a versioned manifest and passes row/label/feature checks.
4. Split gate: purged-plus-embargoed folds, embargo exclusions, and lockbox boundaries are reproducible in a split manifest.
5. Preprocessing gate: every learned transform is fit only on active-fold training rows and recorded in a preprocessing-fit manifest.
6. Model gate: market-only and event-state models run on identical rows and splits.
7. Prediction gate: saved out-of-sample predictions carry row keys, fold IDs, horizon IDs, model IDs, and dataset version.
8. Metric gate: predeclared metrics consume only saved predictions and frozen labels.
9. Diagnostic gate: overfitting diagnostics and lockbox degradation are generated before serious reporting.
10. Artifact gate: run packet contains the full required evidence set.

## Current Pipeline State

- Governance validator exists and passes structurally.
- Alpha Vantage raw top-50 file coverage is complete.
- Stage 2 dataset schema, versioning, manifest, row identity, no-news, and branch-equality contracts are executable for the approved top-50 row universe.
- Stage 2 input readiness is executable as a gate via `scripts/validate_stage2_inputs.py`; Stage 2 completion is validated via `scripts/validate_stage2_completion.py`.
- Stage 2 dataset artifacts exist under `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/`.
- Stage 3 feature/label artifacts exist under `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1/` and validate with the Stage 2 row-universe digest.
- Stage 4 split artifacts exist under `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/` and validate with 9 monthly development folds, final 20% lockbox, leakage validation, and packet-gate evidence.
- Stage 5 model/preprocessing/saved-prediction artifacts exist under `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/` and validate with 8 model IDs, 360 model-fit records, 360 preprocessing-fit records, and 2088000 saved prediction rows.
- Stage 6 benchmark reporting artifacts exist under `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/` and validate with 800 metric rows, 800 ranking diagnostic rows, 800 paired comparison rows, a passed serious packet, result class `clean_null`, and comparability `limitation_bearing`.
- Stage 7C post-lockbox diagnostics exist separately with `benchmark_claim=false`; they do not reinterpret Stage 6.
- Stage 8 plan-first raw update script tests exist under `tests/ops/`; they do not execute provider calls or create benchmark artifacts.
- Remaining comment-only scaffold files are concentrated in provider, utility, and expansion-family layers.

## Completion Rule

A pipeline stage may not be marked complete unless required files exist, relevant tests have run or are explicitly pending with reason, and evidence pointers are recorded in the interaction log.

Any train/validation/lockbox row collision, overlapping-label contamination, embargo misuse, lockbox tuning, non-training preprocessing fit, row-universe mismatch, or missing saved-prediction key is a fail-closed blocker for serious claims.

The 2026-05-07 scaffold satisfied structural documentation only. Later approved Stage 2 through Stage 8 and Stage 10C conversions supersede that scaffold-only status only for their explicit executable paths, tests, and artifacts.
