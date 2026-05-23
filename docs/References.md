# References

Status: minimum active-root reference ledger. This file lists repository evidence that currently supports theory, design, validation, and operation claims. It is not a literature review by itself.

## Governance And Scope

- `AgentRules.md`: binding repository governance and truth hierarchy.
- `ProjectDefinition.md`: broad non-code active project definition synthesized from approved scope and current repository evidence.
- `docs/agent/AgentMemory.md`: binding interaction-log and memory procedure.
- `docs/agent/AgentAppendices.md`: appendix loading and governance companion rules.
- `ScopeDefinition.md`: pre-decision scope framing and contradiction inventory.
- `ScopeDecisionLog.md`: owner-approved scope decisions for phase 1.
- `ResearchTruth.md`: active research-truth synthesis.
- `docs/Data_Separation_And_Overfitting_Control.md`: approved Option B data-separation and overfitting-control design contract.
- `docs/Detailed_Execution_Stages.md`: granular execution-stage requirements, testing strategies, blockers, and prompt index.
- `Stage0Prompt.md`, `Stage0APrompt.md`, `Stage0BPrompt.md`, `Stage1Prompt.md`, `Stage2Prompt.md`, `Stage3Prompt.md`, `Stage4Prompt.md`, `Stage5Prompt.md`, `Stage6Prompt.md`, `Stage7APrompt.md`, `Stage7BPrompt.md`, `Stage7CPrompt.md`, `Stage8Prompt.md`, `Stage9Prompt.md`, `Stage10APrompt.md`, `Stage10BPrompt.md`, `Stage10CPrompt.md`, `Stage11Prompt.md`, `Stage12Prompt.md`: reusable stage execution or future-stage prompt artifacts; Stage 7A has been executed as research-only, Stage 7B decisions are answered in `ScopeDecisionLog.md`, Stage 7C diagnostics have been implemented with `benchmark_claim=false`, Stage 8 has been implemented as plan-first raw update scripts/tests without live provider calls, Stage 9 has been executed as documentation/operational-memory reconciliation only, Stage 10A has been executed as research-only update-to-prediction/visualization workflow analysis, and Stage 10B has been executed as decision-comparison/approval capture with all Stage 10B DQs answered.
- `LEGACY_DEPRECATION_SUMMARY.md`: archive/reference boundary for the legacy snapshot.

## Active Operational Evidence

- `docs/agent/agent_log/Current_State.md`: current operational memory snapshot.
- `docs/agent/agent_log/Event_Ledger.ndjson`: append-only interaction event stream.
- `docs/agent/agent_log/Project_Audit_2026-05-06.md`: active project-state audit.
- `docs/agent/agent_log/AlphaVantage_Raw_Merge_2026-05-06.md`: canonical top-50 raw merge report.
- `docs/agent/agent_log/Stage1_Raw_Data_Security_And_Coverage_Audit_2026-05-12.md`: Stage 1 raw data security and coverage audit, including credential-risk and clean-window input summaries.
- `docs/agent/agent_log/Stage1_Universe_And_OHLCV_Audit_2026-05-14.md`: Stage 1 universe and Twelve Data OHLCV audit addendum.
- `docs/agent/agent_log/TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md`: active raw Twelve Data 2010 coverage and reference-only split-adjustment review.
- `docs/agent/agent_log/Stage0_Stage1_Finalization_2026-05-14.md`: final Stage 0 through Stage 1 completion-evidence report and non-claim ledger.
- `docs/agent/agent_log/Stage2_Dataset_Contract_Definition_2026-05-12.md`: Stage 2 dataset contract and blocker artifact, including planned schema, versioning, manifest, row identity, no-news, branch-equality, and clean-window status.
- `docs/agent/agent_log/Stage2_Deprecated_OHLCV_Salvage_Audit_2026-05-13.md`: Stage 2 deprecated Twelve Data parquet salvage audit, including top-50 plus SPY coverage, quality checks, split evidence, and candidate clean-window bounds.
- `docs/agent/agent_log/Stage2_Input_Readiness_Verification_2026-05-13.md`: Stage 2 input-readiness verification, including ready inputs and blocking missing inputs before dataset implementation.
- `docs/agent/agent_log/Stage2_Materialization_2026-05-14.md`: Stage 2 materialized dataset report with artifact paths, row counts, digest, clean-window decision, limitations, and validation evidence.
- `docs/agent/agent_log/Stage3_Feature_Label_Pipeline_Readiness_2026-05-13.md`: historical Stage 3 readiness and blocker artifact before Stage 2 materialization.
- `docs/agent/agent_log/Stage3_Feature_Label_Pipeline_Readiness_2026-05-14.md`: historical Stage 3 readiness recheck after Stage 2 materialization.
- `docs/agent/agent_log/Stage3_Materialization_2026-05-15.md`: Stage 3 materialized feature/label artifact report with row counts, label contract, event-state contract, limitations, and validation evidence.
- `docs/agent/agent_log/Stage4_Split_And_Packet_Materialization_2026-05-15.md`: Stage 4 materialized split, lockbox, leakage, artifact-packet, and runner-gate report with fold counts, lockbox boundary, limitations, and validation evidence.
- `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json`: machine-readable raw merge manifest.
- `data/manifests/stage1_raw_security_coverage_audit_2026-05-12.json`: machine-readable Stage 1 raw audit manifest.
- `data/manifests/stage1_universe_ohlcv_audit_2026-05-14.json`: machine-readable Stage 1 universe/OHLCV addendum manifest.
- `data/manifests/twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json`: machine-readable active raw Twelve Data 2010 coverage audit manifest.
- `data/manifests/twelvedata_top50_spy_ohlcv_backfill_2010_completion_2026-05-14.json`: plan-mode proof that no 2010 full-window top-50/SPY OHLCV raw entries remain missing.
- `data/manifests/stage0_stage1_completion_validation_2026-05-14.json`: machine-readable Stage 0 through Stage 1 completion validation manifest.
- `data/manifests/stage2_dataset_contract_definition_2026-05-12.json`: machine-readable Stage 2 dataset contract and blocker manifest.
- `data/manifests/stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json`: machine-readable deprecated OHLCV salvage audit manifest.
- `data/manifests/stage2_input_readiness_2026-05-13.json`: machine-readable Stage 2 input-readiness verification manifest.
- `data/manifests/stage2_completion_validation_2026-05-14.json`: machine-readable Stage 2 materialized dataset completion-validation manifest.
- `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/`: materialized Stage 2 top-50 dataset root with partitioned Parquet panel and JSON manifests.
- `data/manifests/stage3_feature_label_pipeline_readiness_2026-05-13.json`: historical machine-readable Stage 3 readiness and blocker manifest before Stage 2 materialization.
- `data/manifests/stage3_feature_label_pipeline_readiness_2026-05-14.json`: machine-readable Stage 3 readiness recheck manifest.
- `data/manifests/stage3_completion_validation_2026-05-15.json`: machine-readable Stage 3 completion validation manifest.
- `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1/`: materialized Stage 3 feature and label artifact root.
- `data/manifests/stage4_completion_validation_2026-05-15.json`: machine-readable Stage 4 completion validation manifest.
- `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/`: materialized Stage 4 split and packet-gate artifact root.
- `data/raw/alphavantage/daemon_summary_top50_only_forward.json`: refreshed top-50 Alpha Vantage plan summary.
- `data/raw/alphavantage/daemon_summary_truncation_refinement.json` and `data/raw/alphavantage/daemon_summary_truncation_refinement_quarterly.json`: plan summaries for quarterly and monthly refinement of likely truncated Alpha Vantage windows.

## Research Notes

- `docs/research_results/foundational_deep_research.md`
- `docs/research_results/restarting_research.md`
- `docs/research_results/restarting_research_literature_expansion.md`
- `docs/research_results/restarting_research_literature_expansion_round2.md`
- `docs/research_results/research_comparison.md`
- `docs/research_results/research_comparison_addendum_targets.md`
- `docs/research_results/research_comparison_addendum_features.md`
- `docs/research_results/research_comparison_addendum_event_representations.md`
- `docs/research_results/research_comparison_addendum_models.md`
- `docs/research_results/research_comparison_addendum_evaluation.md`
- `docs/research_results/research_comparison_addendum_extension_branches.md`
- `docs/research_results/research_comparison_addendum_repo_fit_and_modularity.md`
- `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md`
- `docs/research_results/stage7b_contextual_bandit_decision_draft_2026-05-22.md`
- `docs/research_results/stage7c_post_lockbox_diagnostics_2026-05-22.md`
- `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`
- `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`
- `docs/research_results/paper_notes/restarting_research/*.md`

## Historical Reference Only

- `deprecated_version/legacy_snapshot_20260402T115014Z/`: archived implementation and theory/design materials. These files are reference-only unless deliberately reintroduced through active-root docs.

## Current Validation Evidence

- `scripts/validate_agent_governance.py`: structural governance validator.
- `scripts/validate_comment_only_scaffold.py`: active scaffold validator enforcing that non-exempt scaffold files remain comments-only while approved Stage 2 through Stage 8 and Stage 10C paths/tests are exempted.
- `scripts/audit_deprecated_ohlcv_salvage.py`: deprecated OHLCV salvage audit command for Stage 2 market-data evidence.
- `scripts/audit_twelvedata_ohlcv_coverage.py`: active raw Twelve Data 2010 coverage and split-reference audit command.
- `scripts/validate_stage2_inputs.py`: Stage 2 input-readiness validator that lists ready and blocked inputs without building a dataset.
- `scripts/validate_stage2_completion.py`: Stage 2 completion validator for the materialized Parquet/JSON artifact set.
- `scripts/validate_stage3_readiness.py`: Stage 3 readiness validator that verifies Stage 2 dataset prerequisites and records Stage 3 implementation blockers without creating feature/label artifacts.
- `scripts/validate_stage3_completion.py`: Stage 3 completion validator for the materialized feature/label artifact set.
- `scripts/validate_stage4_completion.py`: Stage 4 completion validator for the materialized split, lockbox, leakage, artifact-packet, and runner-gate artifact set.
- `scripts/validate_stage0_stage1_completion.py`: Stage 0 through Stage 1 completion validator that checks docs, comment-only scaffold, Option B contract, raw-audit evidence, active Twelve Data status, and stale-status snippets without building a dataset.
- `scripts/run_alphavantage_news_truncation_refinement_quarterly.py`: quarterly Alpha Vantage refinement runner for Stage 1 likely truncated windows.
- `scripts/run_alphavantage_news_truncation_refinement_standalone.py`: self-contained portable Alpha Vantage refinement runner with embedded Stage 1 likely-truncated top-50 window IDs and reverse-order execution support.
- `scripts/stage8_data_update_common.py`, `scripts/news_update_daily.py`, `scripts/news_update_weekly.py`, `scripts/OHLCV_daily_update.py`, and `scripts/OHLCV_weekly_update.py`: Stage 8 plan-first raw update scripts for Alpha Vantage news and Twelve Data OHLCV.
- Active script compilation command from the 2026-05-06 audit: `python -m py_compile` over `scripts/*.py` completed without output.
- Focused Stage 2 tests now exist under `tests/data/test_contracts_contract.py`, `tests/dataset/test_row_universe_contract.py`, and `tests/dataset/test_panel_builder_contract.py`; Stage 3 feature/label tests exist under `tests/features/`; Stage 4 split and benchmark-gate tests exist under `tests/split/` and `tests/benchmark/`; Stage 5 tests exist under `tests/models/`; Stage 6 tests exist under `tests/evaluation/`; Stage 7C tests exist under `tests/stage7/`; Stage 8 update-script tests exist under `tests/ops/test_stage8_data_update_contract.py`.
