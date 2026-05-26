# v1p0 First-Slice Stage Completion Register

Status: completed smoke execution under required venv

Updated: 2026-05-24

Required environment before running v1p0 smoke commands:

```bash
source ~/venvs/ai/bin/activate
```

## Completion Summary

| Stage | Prompt | Completion status | Current-state check | Smoke test before continuation | Documentation update | Remaining limit |
| --- | --- | --- | --- | --- | --- | --- |
| Stage 00 | `docs/Prompts/v1p0_Stage00_Governance_Context_Readiness.md` | completed | Required v1p0 docs, memory, and prompt suite exist. No live provider, raw overwrite, Stage 6 reinterpretation, service/API/dashboard, trading output, or comparability-promotion gate was triggered. | `python scripts/validate_agent_governance.py`; event ledger JSONL parse. | Memory and ledger updated. | None for smoke execution. |
| Stage 01 | `docs/Prompts/v1p0_Stage01_Reuse_Vs_Rewrite_Audit.md` | completed | Active `src/event_state_forecasting/` had no v1p0 code before this slice; v0p9 source exists under `deprecated/v0p9/src/`. | Audit only; no import smoke required because rewrite was selected. | `docs/v1p0_first_slice/Stage01_Reuse_Audit.md`; `ArchitecturalDesignDecisions.md`. | v0p9 remains reference-only. |
| Stage 02 | `docs/Prompts/v1p0_Stage02_Version_Manifest_Contract.md` | completed | `configs/v1p0_version_manifest.yaml` exists and declares `implementation_version=v1p0` and `benchmark_family_id=phase1_top50_v1p0`. | `tests/v1p0/test_stage02_04_contracts.py::test_version_manifest_and_feature_registry_contracts`. | `Architecture_Map.md`; `Complete_guidebook.txt`; `ResearchTruth.md`. | Smoke config, not serious benchmark evidence. |
| Stage 03 | `docs/Prompts/v1p0_Stage03_Sidecar_Feature_Registry.md` | completed | `configs/feature_registry_v1p0.yaml` maps `market_lag_linear_v1` and `market_xgboost_v1_fixed` to `market_lag_features_v1p0`. | `tests/v1p0/test_stage02_04_contracts.py::test_version_manifest_and_feature_registry_contracts`. | `Architecture_Map.md`; `Complete_guidebook.txt`; `ResearchTruth.md`. | Smoke registry only. |
| Stage 04 | `docs/Prompts/v1p0_Stage04_Market_Feature_Contract.md` | completed | `configs/market_features_v1p0.yaml` defines row keys, source columns, lag windows, rolling windows, null policy, and shift-before-rolling lookahead policy. | `tests/v1p0/test_stage02_04_contracts.py::test_market_lag_features_shift_before_rolling_without_lookahead`. | `Architecture_Map.md`; `Complete_guidebook.txt`; `ResearchTruth.md`. | Toy no-lookahead evidence only. |
| Stage 05 | `docs/Prompts/v1p0_Stage05_Market_Feature_Builder.md` | completed | `src/event_state_forecasting/v1p0/features.py` builds toy market lag/rolling features and `data/v1p0_first_slice_smoke/first_slice_smoke_v1/market_lag_features.csv` exists after smoke execution. | `tests/v1p0/test_stage05_09_models.py::test_feature_builder_compatibility_and_lag_linear_prediction_schema`; smoke script. | `UsageManual.md`; `Architecture_Map.md`; `Complete_guidebook.txt`; `ResearchTruth.md`. | Not a production sidecar or historical benchmark artifact. |
| Stage 06 | `docs/Prompts/v1p0_Stage06_Split_Label_Compatibility.md` | completed | `validate_feature_label_split_compatibility` checks row-key presence, duplicates, and one-to-one alignment on toy feature/label/split frames. | `tests/v1p0/test_stage05_09_models.py::test_feature_builder_compatibility_and_lag_linear_prediction_schema`. | `ResearchTruth.md`; `docs/v1p0_first_slice/Stage14_Evidence_Review.md`. | Toy compatibility evidence only. |
| Stage 07 | `docs/Prompts/v1p0_Stage07_Lag_Linear_Baseline.md` | completed | `market_lag_linear_v1` uses fold-local preprocessing on train rows and emits validation/lockbox toy predictions. | `tests/v1p0/test_stage05_09_models.py::test_feature_builder_compatibility_and_lag_linear_prediction_schema`; smoke script. | `UsageManual.md`; `ResearchTruth.md`. | No serious performance claim. |
| Stage 08 | `docs/Prompts/v1p0_Stage08_Fixed_XGBoost_Baseline.md` | completed | `market_xgboost_v1_fixed` has fixed parameters in `configs/models_v1p0.yaml` and emits toy predictions under `~/venvs/ai`. | `tests/v1p0/test_stage05_09_models.py::test_fixed_xgboost_records_dependency_blocker_when_missing`; smoke script records `xgboost_status.status=available`. | `UsageManual.md`; `ResearchTruth.md`; `docs/v1p0_first_slice/Stage14_Evidence_Review.md`. | Availability is tied to required venv; no nested Optuna or serious XGBoost benchmark. |
| Stage 09 | `docs/Prompts/v1p0_Stage09_Prediction_Registry_Validation.md` | completed | Combined toy saved predictions contain both v1p0 model IDs and pass saved-prediction schema validation. | `tests/v1p0/test_stage05_09_models.py`; smoke script writes `saved_predictions.csv`. | `UsageManual.md`; `ResearchTruth.md`. | Toy schema evidence only. |
| Stage 10 | `docs/Prompts/v1p0_Stage10_Diagnostics_Core.md` | completed | `src/event_state_forecasting/v1p0/evaluation.py` computes fold/horizon/model diagnostics from toy saved predictions. | `tests/v1p0/test_stage10_13_evaluation_reporting.py::test_diagnostics_strata_uncertainty_and_report_fidelity`. | `UsageManual.md`; `ResearchTruth.md`. | Not candidate-promotion evidence. |
| Stage 11 | `docs/Prompts/v1p0_Stage11_Stratified_Metrics.md` | completed | Toy no-news, truncation-risk, and article-count strata are computed with provider-completeness claim set false. | `tests/v1p0/test_stage10_13_evaluation_reporting.py::test_diagnostics_strata_uncertainty_and_report_fidelity`. | `UsageManual.md`; `ResearchTruth.md`. | Toy strata only. |
| Stage 12 | `docs/Prompts/v1p0_Stage12_Uncertainty_Evidence.md` | completed | Date-clustered normal CI table is generated for toy predictions. | `tests/v1p0/test_stage10_13_evaluation_reporting.py::test_diagnostics_strata_uncertainty_and_report_fidelity`. | `UsageManual.md`; `ResearchTruth.md`. | Block bootstrap remains later requirement before promotion. |
| Stage 13 | `docs/Prompts/v1p0_Stage13_Report_Clarity_Fidelity.md` | completed | Static smoke report writes source-faithful tables and contains required non-claim caveats. | `tests/v1p0/test_stage10_13_evaluation_reporting.py::test_diagnostics_strata_uncertainty_and_report_fidelity`; smoke script writes `report.html`. | `UsageManual.md`; `ResearchTruth.md`; `Complete_guidebook.txt`. | Not a dashboard/API/live forecast. |
| Stage 14 | `docs/Prompts/v1p0_Stage14_Integrated_Evidence_Review.md` | completed | `docs/v1p0_first_slice/Stage14_Evidence_Review.md` and this register cite evidence for every completed stage. | Full `python -m pytest tests/v1p0`; smoke script; governance validator; ledger parse. | `docs/v1p0_first_slice/Stage14_Evidence_Review.md`; memory and ledger. | Broader expansion remains approval-gated. |

## Smoke Command Results

- `source ~/venvs/ai/bin/activate && python -m pytest tests/v1p0`: `5 passed`.
- `source ~/venvs/ai/bin/activate && python scripts/run_v1p0_first_slice_smoke.py`: completed with `model_count=2`, `prediction_rows=4`, `xgboost_status.status=available`, `benchmark_claim=false`, and `trading_signal_approved=false`.

## Non-Claims

This register does not claim serious benchmark completion, model improvement, live forecasting, provider execution, raw mutation, service/API/dashboard scope, trading advice, Stage 6 reinterpretation, or benchmark-comparability promotion.
