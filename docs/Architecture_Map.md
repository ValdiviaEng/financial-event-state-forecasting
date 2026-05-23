# Architecture Map

Status: active-root architecture map. It maps current active files and the intended phase-1 architecture. Approved Stage 2 through Stage 7C paths under `src/`, `configs/`, and `tests/`, Stage 8 raw-update scripts/tests, and Stage 10C prediction-output packet paths are executable; remaining provider/utility/expansion paths remain comment-only scaffolds.

## Current Active Root

- Governance: `AgentRules.md`, `docs/agent/*.md`, `docs/agent/agent_log/*`.
- Scope/truth: `ProjectDefinition.md`, `ScopeDefinition.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`.
- Operations/runbooks: `ExecutionFlow.md`, `ExecutionPipeline.md`, `UsageManual.md`, and `docs/Data_Update_Strategy.md` for local CLI/artifact-driven usage and rerun discipline.
- Prompt archive: `docs/Prompts/` for stage execution prompts, DeepResearch topic prompts, scaffold prompts, and guidebook prompts moved out of the repository root.
- Validation design: `docs/Data_Separation_And_Overfitting_Control.md` for the approved Option B data-separation and overfitting-control contract.
- Research notes: `docs/research_results/`.
- Active scripts: governance/scaffold validators, Alpha Vantage standalone/bucket runners, raw OHLCV audits/downloaders, Stage 8 plan-first raw update wrappers, and Stage 0 through Stage 7 plus Stage 10C completion validators.
- Active pipeline and diagnostics code: approved Stage 2 dataset, Stage 3 feature/label, Stage 4 split/packet, Stage 5 model/preprocessing/saved-prediction, Stage 6 evaluation/reporting, Stage 7C contextual-bandit diagnostics, and Stage 10C prediction-output packet modules under `src/event_state_forecasting/`.
- Active raw/intermediate/model/benchmark/output data: `data/raw/universe/`, `data/raw/alphavantage/`, `data/raw/twelvedata/`, `data/datasets/`, `data/features/`, `data/splits/`, `data/models/`, `data/benchmark_runs/`, `data/prediction_outputs/`, and `data/manifests/`.
- Runtime logs: `runs/logs/`.
- Historical reference: `deprecated_version/legacy_snapshot_20260402T115014Z/`.

## Current Executable And Scaffold Layers

- `src/event_state_forecasting/data/` and `src/event_state_forecasting/dataset/`: approved executable Stage 2 contracts, row-universe helpers, dataset versioning, and panel builder paths; remaining provider/raw helpers are scaffold unless explicitly implemented.
- `src/event_state_forecasting/features/`: approved executable Stage 3 market, news-alignment, event-state, no-news, embedding, and label paths.
- `src/event_state_forecasting/split/` and approved `src/event_state_forecasting/benchmark/` packet/runner-gate paths: executable Stage 4 split, lockbox, leakage, artifact-packet, and no-model runner-gate behavior.
- `src/event_state_forecasting/models/`: approved executable Stage 5 comparator-ladder, market-baseline, gated-fusion, train-only preprocessing, and saved-prediction paths.
- `src/event_state_forecasting/evaluation/` and `src/event_state_forecasting/cli/run_benchmark.py`: approved executable Stage 6 regression metrics, ranking diagnostics, paired comparisons, overfitting diagnostics, comparison summary, comparability classification, and reporting orchestration.
- `src/event_state_forecasting/stage7/` and Stage 7 CLIs: approved executable Stage 7C contextual-bandit diagnostics and final-execution stub boundaries.
- `src/event_state_forecasting/stage10/` and Stage 10C CLI: approved executable local prediction-output packet generation from existing Stage 5 saved predictions.
- `scripts/stage8_data_update_common.py` plus Stage 8 wrappers: approved executable plan-first raw update tooling; live provider calls remain approval-gated.
- `configs/`: active Stage 3, Stage 4, Stage 5, Stage 6, and Stage 7C configs exist; example and remaining future configs remain comment-only scaffolds.
- `tests/`: Stage 2 through Stage 8 contract/update tests and Stage 10C packet tests are executable for approved claims; remaining provider/utility/expansion tests remain comment-only planned tests.

Only explicitly approved executable paths should be treated as implemented. Remaining scaffold files must not be imported, executed, or cited as implemented behavior.

`UsageManual.md` describes local command usage, artifact interfaces, inputs, and outputs only; it does not introduce a user-facing service API, dashboard, or authentication boundary.

## Intended Phase-1 Data Flow

1. Universe definition: frozen top-50 file in `data/raw/universe/`.
2. Raw provider ingestion: Twelve Data OHLCV, Alpha Vantage news, SEC support data if needed.
3. Raw validation: schema checks, coverage checks, provider-limit flags, credential-sanitization checks.
4. As-of feature panel: market features plus aligned event-state features on identical rows.
5. Label generation: forward excess-return labels for `1d`, `5d`, `10d`, `20d`, and `60d`.
6. Split generation: purged-plus-embargoed walk-forward folds, explicit purge/embargo accounting, and final untouched lockbox.
7. Fold-local preprocessing: learned transforms fit on training rows only, then applied to validation or lockbox rows.
8. Benchmark execution: market-only baselines, approved comparator ladder, and event-state models on identical rows and splits.
9. Artifact packet: dataset manifest, resolved config, split manifest, preprocessing-fit manifest, saved predictions, metrics, overfitting diagnostics, and comparison summary.

## Option B Control Flow

- Dataset rows must carry stable row identity, feature availability timestamp, label-window bounds, split role, fold ID, and lockbox flag.
- Split artifacts must record train/evaluation windows, purge spans, embargo spans, excluded rows, and row counts by horizon.
- Metric computation must consume saved out-of-sample predictions and frozen labels, not hidden training state.
- Serious reports must include train-validation gaps, fold dispersion, positive-fold/horizon rates, validation-to-lockbox degradation, paired comparison notes, and search-space summary.
- Any detected train/validation/lockbox collision, overlapping-label contamination, embargo misuse, lockbox tuning, or non-training preprocessing fit is a fail-closed blocker.

## Current Script Responsibilities

- `scripts/validate_agent_governance.py`: validates required governance file structure.
- `scripts/run_alphavantage_news_top50_only_standalone.py`: top-50 Alpha Vantage `NEWS_SENTIMENT` runner and plan summary writer.
- `scripts/alphavantage_news_bucket_common.py`: shared standard-library runner core for hardcoded ticker buckets.
- `scripts/run_alphavantage_news_top51_100_only_standalone.py`: top-51-100 wrapper.
- `scripts/run_alphavantage_news_top51_75_only_standalone.py`: top-51-75 wrapper.
- `scripts/run_alphavantage_news_top76_100_only_standalone.py`: top-76-100 wrapper.
- `scripts/run_alphavantage_news_top101_200_only_standalone.py`: top-101-200 wrapper.
- `scripts/run_alphavantage_news_top201_300_only_standalone.py`: top-201-300 wrapper.
- `scripts/run_alphavantage_news_top301_400_only_standalone.py`: top-301-400 wrapper.
- `scripts/run_alphavantage_news_top401_500_only_standalone.py`: top-401-500 wrapper.
- `scripts/run_alphavantage_news_multi_bucket_portable_standalone.py`: portable multi-bucket runner wrapper.
- `scripts/validate_stage2_inputs.py` and `scripts/validate_stage2_completion.py`: Stage 2 input and materialized-dataset validators.
- `scripts/validate_stage3_completion.py`, `scripts/validate_stage4_completion.py`, `scripts/validate_stage5_completion.py`, and `scripts/validate_stage6_completion.py`: Stage 3 through Stage 6 materialized-artifact validators.
- `scripts/validate_stage7_completion.py`: Stage 7C diagnostic artifact validator.
- `scripts/validate_stage10c_completion.py`: Stage 10C local prediction-output packet validator.
- `scripts/news_update_daily.py`, `scripts/news_update_weekly.py`, `scripts/OHLCV_daily_update.py`, and `scripts/OHLCV_weekly_update.py`: Stage 8 plan-first raw update wrappers.
- `scripts/validate_comment_only_scaffold.py`: enforces that non-approved scaffold files remain comment-only.

## Dependency Rules

- Theory docs constrain design docs.
- Design docs constrain code and tests.
- Raw data coverage reports constrain benchmark-readiness claims.
- `docs/Data_Separation_And_Overfitting_Control.md` constrains dataset, split, preprocessing, prediction, metric, and reporting contracts.
- Interaction-log files preserve request/evidence history but do not override theory or design.
- Approved executable Stage 2 through Stage 8 and Stage 10C paths/tests may be imported and validated for their scoped claims; remaining comment-only scaffold files document intended responsibilities only and must not be imported, executed, or cited as implemented behavior.
