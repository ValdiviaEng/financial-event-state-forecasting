# Event-State Forecasting

Status: active-root rebuild with Stage 6 serious benchmark reporting completed for the approved top-50 row universe, Stage 7C contextual-bandit diagnostics materialized on a new post-Stage-6-lockbox holdout, Stage 8 plan-first raw update scripts implemented, Stage 9 documentation reconciliation completed, Stage 10A research-only update-to-prediction/visualization workflow analysis completed, Stage 10B decision-comparison/approval capture completed, and Stage 10C local prediction-output packet generation completed. This README is an onboarding summary only; `AgentRules.md`, `ScopeDecisionLog.md`, and `ResearchTruth.md` govern active truth.

## Phase-1 Objective

Test whether aligned firm-news event-state features add value beyond market-only baselines for end-of-day, multi-horizon, forward excess-return forecasting.

## Approved Benchmark Shape

- Target family: forward excess returns.
- Horizons: `1d`, `5d`, `10d`, `20d`, `60d`.
- Universe: reproducible top-50 liquid large-cap set.
- News provider: Alpha Vantage.
- OHLCV provider: Twelve Data.
- Static/company support: SEC only.
- Alignment: same-day as-of-close, with after-hours and non-trading-day news rolled forward.
- Serious evaluation: purged-plus-embargoed walk-forward plus final untouched lockbox.
- Data separation: Option B contract requiring split manifests, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, and overfitting diagnostics.

## Current State

- Governance and scope decisions are active.
- Required active-root documentation skeletons exist.
- Alpha Vantage canonical top-50 raw file coverage is complete at 850/850 after the 2026-05-06 raw merge.
- Provider-level article completeness is not claimed; current Alpha Vantage news is used with explicit truncation limitation flags under the latest user instruction.
- A truncation-refinement script now validates existing quarterly files, lists missing work, and creates monthly follow-up requests for quarters that still hit the provider limit.
- Active raw Twelve Data OHLCV now has full-window files for the approved top-50 plus SPY support from `2010-01-01` to requested end date `2026-05-22`; `docs/agent/agent_log/Stage7_TwelveData_OHLCV_Update_Audit_2026-05-22.md` records no post-first-available-date gaps, 5 late-start tickers, one CVX OHLC anomaly handled only by derived cleaning policy, and reference-only deprecated split-adjustment evidence.
- Deprecated Twelve Data parquet price evidence remains reference-only salvage evidence in `docs/agent/agent_log/Stage2_Deprecated_OHLCV_Salvage_Audit_2026-05-13.md` and `data/manifests/stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json`.
- Active implementation currently includes governance/raw-data scripts, Stage 8 plan-first raw update scripts, approved executable Stage 2 dataset-contract modules, Stage 3 feature/label modules, Stage 4 split/packet-gate modules, Stage 5 model/prediction modules, Stage 6 evaluation/reporting modules, Stage 7 contextual-bandit diagnostic modules, Stage 10C prediction-output modules, active Stage 3 through Stage 7 configs, CLIs, completion validators, and focused Stage 2 through Stage 8 plus Stage 10C tests.
- Remaining future provider/utility/expansion layers remain comment-only scaffolds unless explicitly converted for an approved stage.
- A Stage 6 serious benchmark reporting artifact is currently evidenced with result class `clean_null` and comparability `limitation_bearing`.
- Option B is executable through the Stage 6 split, lockbox, leakage, packet-gate, fold-local preprocessing, saved-prediction, metric, comparison-summary, and overfitting-diagnostic checks, except train-validation gap computation is explicitly blocked because Stage 5 saved no train predictions.
- Granular execution guidance now exists in `docs/Detailed_Execution_Stages.md` plus stage prompt files under `docs/Prompts/`, from `docs/Prompts/Stage0Prompt.md` through `docs/Prompts/Stage12Prompt.md`, including `Stage0APrompt.md`, `Stage0BPrompt.md`, split Stage 7 prompts, and split Stage 10 prompts.
- Stage 7A contextual-bandit feasibility research remains research-only in `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md`. Stage 7B decision collection is complete in `ScopeDecisionLog.md`. Stage 7C implementation now exists with saved diagnostics, a final-execution stub, and a new post-Stage-6-lockbox diagnostic artifact under `data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout/`. It does not approve all-data final-execution training-output, live buy/sell signals, Stage 6 reinterpretation, or benchmark-comparability promotion.
- Stage 9 reconciliation updated active documentation and operational memory only; it did not add features, call providers, mutate raw data, rerun benchmarks, reinterpret Stage 6, or promote Stage 7C/8 outputs.
- Stage 10A research exists in `docs/research_results/stage10a_update_to_prediction_workflow_2026-05-22.md`; it proposes future local dated prediction-output and static visualization artifact decisions but did not implement code, call providers, mutate raw data, create prediction or visualization artifacts, create service/API scope, or produce trading signals.
- Stage 10B decision comparison exists in `docs/research_results/stage10b_update_to_prediction_decision_matrix_2026-05-23.md`; `S10B-DQ-001` through `S10B-DQ-010` are answered in `ScopeDecisionLog.md`. Stage 10C has since been implemented as a local saved-prediction extraction packet generator only; it did not call providers, mutate raw data, approve persisted inference packaging, create service/API/dashboard scope, reinterpret Stage 6, promote benchmark comparability, or produce trading signals.
- `ExecutionPipeline.md` documents the stagewise rebuild methodology after approved new data or truncation refinement; `UsageManual.md` documents local command usage, inputs, outputs, and artifact interfaces including Stage 8 plan-first raw update scripts. These are not a product API or service scope.
- Stage 1 raw audit artifacts now exist in `docs/agent/agent_log/Stage1_Raw_Data_Security_And_Coverage_Audit_2026-05-12.md`, `docs/agent/agent_log/Stage1_Universe_And_OHLCV_Audit_2026-05-14.md`, and `docs/agent/agent_log/TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md`; together they document complete parseable top-50 Alpha Vantage canonical file coverage, visible truncation limits, sensitive ledger/log risk, and active raw Twelve Data top-50 plus SPY support coverage back to 2010 where each ticker has provider history.
- Stage 2 materialization now exists in `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/`, with a partitioned Parquet panel, dataset manifest, row-universe digest, clean-window record, and CVX derived patch manifest.
- Stage 2 completion is documented in `docs/agent/agent_log/Stage2_Materialization_2026-05-14.md`; the dataset has `117750` rows, `471` as-of dates, `50` tickers, and `23550` rows per approved horizon.
- Stage 3 materialization exists in `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1/`, with market features, event-state features, labels, aligned news, manifest, and row-universe digest.
- Stage 3 completion is documented in `docs/agent/agent_log/Stage3_Materialization_2026-05-15.md`; it has `117750` rows, `67840` aligned news records, `71420` no-news rows after Stage 3 alignment, and the same row digest as Stage 2.
- Stage 4 materialization exists in `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/`, with split manifest, fold definitions, split assignments, lockbox record, leakage validation, artifact-packet validation, and gate-safe runner evidence.
- Stage 4 completion is documented in `docs/agent/agent_log/Stage4_Split_And_Packet_Materialization_2026-05-15.md`; it has `9` monthly development folds, lockbox `2025-09-30` through `2026-02-13`, `1059750` split-assignment rows, and a passed Stage 4 completion validator.
- Stage 5 materialization exists in `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/`, with resolved model config, comparator roster record, model-fit manifest, preprocessing-fit manifest, saved predictions, training diagnostics, search-space summary, and serious-packet validation.
- Stage 5 has `8` model IDs, `360` model-fit records, `360` preprocessing-fit records, and `2088000` saved prediction rows; it creates no metrics, overfitting diagnostic report, comparison summary, or benchmark result by itself.
- Stage 6 reporting exists in `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/`, with `800` metric rows, `800` ranking diagnostic rows, `800` paired comparison rows, a passed serious packet, result class `clean_null`, and comparability class `limitation_bearing`.
- Stage 7C post-lockbox diagnostics exist in `data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout/`, with lockbox `2026-02-17` through `2026-02-25`, `22750` fold-specific context rows, `180180` policy-selection rows, `4620` metric rows, and a passed Stage 7 validator.
- Stage 10C prediction-output packet exists in `data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1/`, with `250` model-output rows, `50` primary top-10 rows, deterministic aligned-news context, trajectory marker data, static `report.html`, and a passed Stage 10C validator. Rows are `historical_prediction`, not fresh future inference.

## Safe Current Commands

```powershell
python scripts/validate_agent_governance.py
```

```powershell
python scripts/run_alphavantage_news_top50_only_standalone.py --plan --skip-seed-migration
```

```powershell
python scripts/validate_stage2_inputs.py
```

```powershell
python scripts/validate_stage0_stage1_completion.py
```

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_benchmark_dataset
```

```powershell
python scripts/validate_stage2_completion.py
```

```powershell
python scripts/validate_stage3_readiness.py
```

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels
```

```powershell
python scripts/validate_stage3_completion.py
```

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet
```

```powershell
python scripts/validate_stage4_completion.py
```

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.train_models_and_predict
```

```powershell
python scripts/validate_stage5_completion.py
```

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
```

```powershell
python scripts/validate_stage6_completion.py
```

```powershell
python scripts/validate_stage7_completion.py
```

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
```

```powershell
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

```powershell
python scripts/audit_deprecated_ohlcv_salvage.py
```

```powershell
python scripts/run_alphavantage_news_truncation_refinement_quarterly.py --plan
```

```powershell
python scripts/run_alphavantage_news_truncation_refinement_standalone.py --plan --order reverse
```

```powershell
python scripts/news_update_daily.py --end-date 2026-05-22
```

```powershell
python scripts/OHLCV_daily_update.py --end-date 2026-05-22 --include-spy
```

## Important Cautions

- Raw top-50 file coverage is not benchmark readiness.
- Raw OHLCV coverage evidence is not by itself a benchmark result; Stage 2 now materializes a row/availability dataset only.
- Stage 2 dataset materialization did not choose a split-adjustment method; Stage 3 creates features and labels, Stage 4 creates split/lockbox/packet gates, Stage 5 creates model/preprocessing/prediction artifacts, and Stage 6 creates metric/diagnostic/comparison artifacts.
- The current Stage 6 result class is `clean_null`; do not describe it as a positive result or trading-profitability result.
- The current Stage 7C artifact is diagnostics-only with `benchmark_claim=false`; do not describe it as a live trading signal, all-data final-execution output, or Stage 6 reinterpretation.
- The current Stage 10C packet is a local historical-prediction artifact with `benchmark_claim=false`; do not describe it as fresh future inference, persisted serving, a benchmark result, Stage 6 reinterpretation, a service/API/dashboard, or trading advice.
- Stage 8 update scripts are plan-only by default; live provider calls require explicit approval, `--execute`, API key availability, quota/rate-limit controls, no-overwrite review, and redacted ledgers.
- Do not commit or share API-key-bearing raw Alpha Vantage or Twelve Data ledgers.
- Treat any live truncation-refinement run as a quota-consuming provider call; use `--once` for one request at a time if you want controlled execution.
- The standalone truncation-refinement runner embeds the Stage 1 likely-truncated top-50 window list and needs only standard-library Python plus an Alpha Vantage API key when copied to another machine.
- Treat `runs/logs/alphavantage_news_daemon.log` as sensitive until its Alpha Vantage URL-bearing lines are sanitized or isolated.
- Do not change Stage 6 metric policy, comparison framing, lockbox interpretation, comparator roster, protected scope, or benchmark comparability after result inspection without explicit approval.
- Do not treat top-100/top-500 data collection as comparable to the approved top-50 benchmark family without explicit approval.
- Archived files under `deprecated/v0p9/` and `deprecated/v0p7/` are reference-only unless reintroduced through active docs.

## Key Docs

- `AgentRules.md`
- `ProjectDefinition.md`
- `ArchitecturalDesignDecisions.md`
- `Architecture_Map.md`
- `docs/Prompts/StructuralFolderMapPrompt.md`
- `docs/NextSteps_Brainstorming.md`
- `deprecated/v0p9/docs/ScopeDecisionLog.md`
- `deprecated/v0p9/docs/ScopeDefinition.md`
- `ResearchTruth.md`
- `LearningStrategy.md`
- `BenchmarkingStrategy.md`
- `VisualizationStrategy.md`
- `Unilu_Compatibility_requirements.md`
- `docs/Data_Separation_And_Overfitting_Control.md`
- `docs/Detailed_Execution_Stages.md`
- `docs/Complete_Theoretical_Background.md`
- `docs/Implementation_Decisions.md`
- `docs/Execution_Plan.md`
- `ExecutionPipeline.md`
- `UsageManual.md`
- `docs/Prompts/Stage0Prompt.md` through `docs/Prompts/Stage12Prompt.md`
- `docs/Prompts/v1p0_Stage00_*.md` through `docs/Prompts/v1p0_Stage14_*.md`
- `docs/Prompts/v1p0_Stage15_*.md` through `docs/Prompts/v1p0_Stage40_*.md`
- `docs/Prompts/DeepResearch_Chat_Topic_*.md`
- `docs/db_Testing.md`
- `docs/Benchmark_Testing.md`
- `ExecutionFlow.md`
- `data/v1p0_full_results/README.md`
