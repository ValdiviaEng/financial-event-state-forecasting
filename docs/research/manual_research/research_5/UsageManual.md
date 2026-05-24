# Usage Manual

Status: holistic local usage manual for the active Stage 0 through Stage 10C repository state. This manual supersedes the former API-centric usage reference while preserving its useful local interface details. The repository remains a local CLI/artifact-driven research system, not a user-facing service API, web API, dashboard, authentication boundary, live inference service, or trading interface.

## 1. Purpose And Authority

Use this manual to run supported local commands, inspect artifacts, understand inputs and outputs, and identify functions that are active, plan-first, stubbed, comment-only, or undeployed. Use `ExecutionPipeline.md` for run sequencing, approval gates, and comparability discipline before rebuilding or refreshing data.

Authority order if documents conflict:

1. `AgentRules.md`, `ScopeDecisionLog.md`, and `ResearchTruth.md`.
2. `ProjectDefinition.md` and protected-scope documentation.
3. Stage prompt files and stage-specific completion logs.
4. `ExecutionPipeline.md`, this manual, README, guidebook, and convenience references.

Current non-claims to preserve:

- Stage 6 remains `clean_null` with `limitation_bearing` comparability.
- Stage 7C is diagnostics-only and not a live buy/sell signal or Stage 6 reinterpretation.
- Stage 8 defaults to plan-only raw update manifests and does not call providers unless live execution is explicitly approved.
- Stage 10C emits local `historical_prediction` packets from existing Stage 5 saved predictions, not fresh future inference.
- There is no persisted fitted-model serving package for arbitrary new feature-only rows.
- There is no product API, service endpoint, dashboard, authentication layer, or trading/signal interface.

## 2. Interface Model

The supported interface is a combination of command-line entry points and versioned artifact directories.

| Interface type | Current status | How to use it | What it is not |
| --- | --- | --- | --- |
| Local Python module CLIs | Active for Stage 2 through Stage 7C and Stage 10C paths listed below | Run with `python -m event_state_forecasting.cli.<entrypoint>` after setting `PYTHONPATH=src` | Not a stable package API for external apps. |
| Standalone scripts | Active for validators, raw audits, plan-first Stage 8 updates, and provider planning utilities | Run with `python scripts/<name>.py` from repo root | Not approval for live provider calls or raw overwrites. |
| Artifact roots | Active source of truth for data, features, splits, models, metrics, diagnostics, and Stage 10C packets | Read manifests first, then Parquet/CSV/JSON outputs | Not automatically comparable across versions. |
| JSON stdout summaries | Available on selected CLIs with `--json` | Use for automation around local runs | Not a remote API response contract. |
| Programmatic imports | Implementation detail except where tests exercise them | Prefer CLIs and artifacts | Not a supported public SDK. |
| Comment-only scaffolds | Present for future utilities | Read as planned design only | Not runnable and not implemented. |

## 3. Requirements And Setup

Run commands from the repository root.

On Windows PowerShell, set `PYTHONPATH` before package-module CLIs:

```powershell
$env:PYTHONPATH="src"
```

For standalone scripts in `scripts/`, `PYTHONPATH` is usually not required unless the script imports package modules explicitly.

The active implementation expects the Python dependencies already available in the current environment. The code paths use packages such as `pandas`, `numpy`, `pyarrow`, `yaml`/`PyYAML`, `pytest`, and model/evaluation dependencies exercised by the test suite.

Provider keys are only needed for approved live provider calls:

| Provider path | Default environment variable | Default `.env` lookup | Current default behavior |
| --- | --- | --- | --- |
| Alpha Vantage news Stage 8 scripts | `ALPHAVANTAGE_API_KEY` | `.env` | Plan-only unless `--execute` is supplied and approved. |
| Twelve Data OHLCV Stage 8 scripts | `TWELVE_DATA_API_KEY` | `.env` | Plan-only unless `--execute` is supplied and approved. |

Do not commit or share raw ledgers that may contain API-key-bearing URLs. Stage 8 live ledgers are designed to be redacted, but raw historical provider ledgers can still be sensitive.

## 4. Quick Start

Validate governance and the active test suite:

```powershell
python scripts/validate_agent_governance.py
python scripts/validate_comment_only_scaffold.py
python -m pytest "tests"
```

Expected current active-root results:

| Check | Expected result |
| --- | --- |
| Governance validator | `VALIDATION PASSED` |
| Comment-only scaffold validator | `COMMENT_ONLY_VALIDATION PASSED (files_scanned=133)` |
| Test suite | `58 passed` |

Generate the current Stage 10C readable packet from existing saved predictions:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

Plan a raw update without provider calls:

```powershell
python scripts/news_update_daily.py --end-date 2026-05-22
python scripts/OHLCV_daily_update.py --end-date 2026-05-22 --include-spy
```

Rebuild Stage 2 through Stage 6 only after reading `ExecutionPipeline.md` and confirming no approval gate is triggered.

## 5. Current Artifact Inventory

| Stage | Current artifact root | Contents | Current status |
| --- | --- | --- | --- |
| Stage 2 dataset | `data/datasets/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086/` | `benchmark_panel.parquet`, `dataset_manifest.json`, `row_universe_digest.json`, `clean_window_decision.json`, `cvx_derived_ohlc_patch_manifest.json` | Materialized, validated, not a benchmark result. |
| Stage 3 features/labels | `data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1/` | `market_features.parquet`, `event_state_features.parquet`, `labels.parquet`, `aligned_news.parquet`, manifest, digest | Materialized, validated. |
| Stage 4 splits | `data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1/` | folds, assignments, lockbox, leakage validation, packet validation, runner gate | Materialized, validated. |
| Stage 5 models/predictions | `data/models/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1/` | config, roster, preprocessing manifests, saved predictions, diagnostics, serious packet validation | Materialized, validated; no metrics by itself. |
| Stage 6 reporting | `data/benchmark_runs/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage6_reporting_v1/` | metrics, ranking diagnostics, paired comparisons, overfitting report, comparison summary, comparability, manifest | Materialized, `clean_null`, `limitation_bearing`. |
| Stage 7C diagnostics | `data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout/` | contextual-bandit context, selections, metrics, replay validation, final-execution stub evidence | Diagnostics-only, `benchmark_claim=false`. |
| Stage 10C prediction outputs | `data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1/` | model outputs, top-10 tables, news context, trajectories, limits, report, validation | Local historical-prediction packet. |

Current artifact counts:

| Stage | Count summary |
| --- | --- |
| Stage 2 | `117750` rows, `471` as-of dates, `50` tickers, `23550` rows per approved horizon. |
| Stage 3 | `117750` feature/label rows, `67840` aligned news records, `71420` no-news rows after alignment. |
| Stage 4 | `9` monthly development folds, lockbox from `2025-09-30` through `2026-02-13`, `1059750` split-assignment rows. |
| Stage 5 | `8` model IDs, `360` model-fit records, `360` preprocessing-fit records, `2088000` saved prediction rows. |
| Stage 6 | `800` metric rows, `800` ranking diagnostic rows, `800` paired comparison rows, result `clean_null`. |
| Stage 7C | Post-lockbox holdout `2026-02-17` through `2026-02-25`, `22750` context rows, `180180` policy-selection rows, `4620` metric rows. |
| Stage 10C | `250` model-output rows, `50` primary top-10 rows, `50` delta top-10 rows, `10` cross-horizon rows, `86` relevant-news rows, `449` trajectory rows. |

## 6. Common Usage Paths

| Goal | Use | Primary output | Must not claim |
| --- | --- | --- | --- |
| Check governance/docs | `validate_agent_governance.py`, `validate_comment_only_scaffold.py`, ledger JSONL parse | Pass/fail validation text | Scientific readiness or benchmark validity. |
| Check current tests | `python -m pytest "tests"` | Pytest result | Provider completeness or trading usefulness. |
| Inspect active raw input readiness | `validate_stage2_inputs.py` | Stage 2 input-readiness summary/manifest | Benchmark result or final feature availability. |
| Plan raw data refresh | Stage 8 scripts without `--execute` | Plan manifest and skipped/planned entries | Live provider execution or new benchmark output. |
| Rebuild approved benchmark artifacts | Stage 2 through Stage 6 CLIs in order, then validators | New versioned artifacts | Comparability without review. |
| Inspect Stage 6 result | Stage 6 summary/reporting artifacts | Metrics, comparison summary, comparability record | Positive result, trading profitability, or provider completeness. |
| Run Stage 7C diagnostics | `run_stage7_contextual_bandit` with approved roots | Diagnostic selections/metrics | Live signal, all-data final-execution training output, or Stage 6 reinterpretation. |
| Generate readable model outputs | `generate_prediction_outputs` | Stage 10C static packet | Fresh future inference, persisted serving, or buy/sell advice. |
| Maintain docs/prompts | Stage 0, Stage 9, Stage 11/12 prompt-maintenance rules | Docs and memory updates | Implementation approval unless explicitly granted. |

## 7. Stage And Function Status Matrix

| Stage or function family | Status | Primary files | Requirements before use | Output status |
| --- | --- | --- | --- | --- |
| Stage 0 documentation repair | Executed documentation workflow; reusable when docs drift | `Stage0Prompt.md`, active docs | Preserve protected scope and update memory | Docs only. |
| Stage 0A comment scaffold | Executed, now partially superseded by approved executable paths | `Stage0APrompt.md`, `src/`, `configs/`, `tests/` | Remaining scaffolds must stay comments only | Comments or approved code only. |
| Stage 0B Option B contract | Executed design contract | `Stage0BPrompt.md`, `docs/Data_Separation_And_Overfitting_Control.md` | Do not change benchmark family | Contract only. |
| Stage 1 raw audit | Executed through scripts/manifests; some future CLIs remain scaffold-only | `Stage1Prompt.md`, raw audit scripts | No destructive raw edits or secret exposure | Audit evidence only. |
| Stage 2 dataset | Executed and materialized | `build_benchmark_dataset`, `validate_stage2_*` | Approved raw inputs and clean-window discipline | Dataset artifact, not result. |
| Stage 3 features/labels | Executed and materialized | `build_features_and_labels`, `validate_stage3_*` | Stage 2 artifact, configs, raw roots | Feature/label artifacts. |
| Stage 4 splits/packet gate | Executed and materialized | `build_splits_and_packet`, `validate_stage4_completion.py` | Stage 3 artifact and split configs | Split artifacts, no model result. |
| Stage 5 models/predictions | Executed and materialized | `train_models_and_predict`, `validate_stage5_completion.py` | Stage 3/4 artifacts and frozen roster | Saved predictions, no metrics. |
| Stage 6 reporting | Executed and materialized | `run_benchmark`, `validate_stage6_completion.py` | Stage 5 saved predictions and frozen labels | `clean_null`, `limitation_bearing`. |
| Stage 7A research | Executed research-only | Stage 7A memo | No code or data mutation | Research memo only. |
| Stage 7B decisions | Executed decision capture | `ScopeDecisionLog.md` Stage 7B entries | User decisions required before Stage 7C | Decision evidence only. |
| Stage 7C diagnostics | Executed diagnostics-only | `run_stage7_contextual_bandit`, Stage 7 modules/tests | No Stage 6 reinterpretation, no live signals | Diagnostic packet. |
| Stage 7 final execution | Stub only; all-data training blocked | `run_stage7_final_execution.py` | Future explicit approval required for real all-data training | Stub manifest only. |
| Stage 8 raw updates | Implemented plan-first scripts/tests | `news_update_*`, `OHLCV_*_update.py` | Live `--execute` and `--overwrite` need explicit approval | Plan or approved raw payload update. |
| Stage 9 reconciliation | Executed documentation-only | `Stage9Prompt.md` | No feature code or result reinterpretation | Docs/memory updates. |
| Stage 10A research | Executed research-only | Stage 10A memo | No implementation or provider calls | Research memo only. |
| Stage 10B decisions | Executed decision capture | Stage 10B memo, `ScopeDecisionLog.md` | No implementation by itself | Decision evidence only. |
| Stage 10C prediction outputs | Executed local packet implementation | `generate_prediction_outputs`, Stage 10 modules/tests | Existing Stage 5/3/6 artifacts; no provider calls | Historical-prediction packet. |
| Stage 11 audit | Proposed prompt only | `Stage11Prompt.md` | Separate execution approval/context check | No current output. |
| Stage 12 prompt maintenance | Proposed prompt only | `Stage12Prompt.md`, DeepResearch prompts | Separate execution approval/context check | No current output. |

## 8. Command Catalog

### 8.1 Validation And Governance Commands

| Command | Status | Purpose | Inputs | Outputs | Expected current result |
| --- | --- | --- | --- | --- | --- |
| `python scripts/validate_agent_governance.py` | Active | Validate governance structure and memory/log shape | Governance docs, current memory, event ledger | Pass/fail report | `VALIDATION PASSED`. |
| `python scripts/validate_comment_only_scaffold.py` | Active | Enforce comments-only status outside approved executable paths | `src/`, `configs/`, `tests/` | Pass/fail report | `COMMENT_ONLY_VALIDATION PASSED (files_scanned=133)`. |
| `python scripts/validate_stage0_stage1_completion.py` | Active | Validate Stage 0/1 evidence availability | Raw audit/manifests/docs | Stage 0/1 validation summary | Expected pass. |
| `python scripts/validate_stage2_inputs.py` | Active | Validate raw inputs for dataset builder gate | Universe, raw Twelve Data, raw Alpha Vantage, manifests | Readiness summary and optional manifest | Run before Stage 2. |
| `python scripts/validate_stage2_completion.py --write` | Active | Validate Stage 2 dataset output | Stage 2 artifact root | Completion manifest under `data/manifests/` | Expected pass for current root. |
| `python scripts/validate_stage3_completion.py --write` | Active | Validate Stage 3 feature/label output | Stage 3 artifact root | Completion manifest | Expected pass for current root. |
| `python scripts/validate_stage4_completion.py --write` | Active | Validate Stage 4 split/packet output | Stage 4 artifact root | Completion manifest | Expected pass for current root. |
| `python scripts/validate_stage5_completion.py --write` | Active | Validate Stage 5 model/prediction output | Stage 5 artifact root | Completion manifest | Expected pass for current root. |
| `python scripts/validate_stage6_completion.py --write` | Active | Validate Stage 6 reporting output | Stage 6 artifact root | Completion manifest | Expected `clean_null` and `limitation_bearing`. |
| `python scripts/validate_stage7_completion.py` | Active | Validate Stage 7C diagnostics | Stage 7C artifact root | Validation result | Expected pass for current diagnostic root. |
| `python scripts/validate_stage10c_completion.py` | Active | Validate latest Stage 10C packet | Latest or specified prediction-output root | Validation text and optional manifest | Expected pass for current packet. |

Ledger JSONL parse check:

```powershell
python -c "import json, pathlib; p=pathlib.Path('docs/agent/agent_log/Event_Ledger.ndjson'); [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]; print('EVENT_LEDGER_JSONL_VALID')"
```

### 8.2 Stage 2 Dataset Builder

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_benchmark_dataset --json
```

Purpose: build the approved Stage 2 top-50 benchmark dataset artifacts.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--output-root` | `data/datasets/phase1_top50` | Dataset family output root. |
| `--universe-path` | Approved top-50 universe CSV | Universe input. |
| `--raw-twelvedata-root` | `data/raw/twelvedata` | Raw OHLCV root. |
| `--raw-alphavantage-root` | `data/raw/alphavantage` | Raw news root. |
| `--stage1-manifest-path` | Stage 1 raw security manifest | Raw security/coverage evidence. |
| `--stage1-ohlcv-manifest-path` | Stage 1 OHLCV audit manifest | OHLCV clean-window evidence. |
| `--twelvedata-audit-path` | Twelve Data coverage audit | OHLCV coverage/cvx evidence. |
| `--stage2-contract-manifest-path` | Stage 2 contract manifest | Dataset contract evidence. |
| `--twelvedata-full-window-filename` | Active full-window filename | File to load for every ticker. |
| `--allow-overwrite` | Off | Replace an existing identical-version dataset output directory. |
| `--json` | Off | Print machine-readable summary. |

Inputs:

- Approved top-50 universe CSV.
- Raw Twelve Data full-window OHLCV files.
- Raw Alpha Vantage news files.
- Stage 1 and Stage 2 manifests proving scope and input-readiness evidence.

Outputs:

- `benchmark_panel.parquet`.
- `dataset_manifest.json`.
- `row_universe_digest.json`.
- `clean_window_decision.json`.
- `cvx_derived_ohlc_patch_manifest.json`.

Human stdout includes `status: stage2_dataset_built`, `benchmark_claim: false`, `row_count`, `row_universe_digest`, `dataset_root`, and `manifest`.

Important interpretation:

- Stage 2 materializes row identity, clean-window, availability, and split-eligibility fields only.
- It does not create features, labels, splits, models, predictions, metrics, or benchmark results.
- The CVX anomaly handling is derived cleaning only; raw Twelve Data files are not modified.

Validate:

```powershell
python scripts/validate_stage2_completion.py --write
```

### 8.3 Stage 3 Feature And Label Builder

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels --json
```

Purpose: build market features, event-state features, aligned news, and forward excess-return labels.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--dataset-root` | `data/datasets/phase1_top50` | Stage 2 artifact root or family root; latest valid child is selected when a family root is supplied. |
| `--output-root` | `data/features/phase1_top50` | Stage 3 artifact family output root. |
| `--features-config` | `configs/features.yaml` | Active feature config. |
| `--labels-config` | `configs/labels.yaml` | Active label config. |
| `--raw-twelvedata-root` | `data/raw/twelvedata` | Raw OHLCV source for label reference prices. |
| `--twelvedata-full-window-filename` | Active full-window filename | Raw OHLCV filename to load per ticker. |
| `--raw-alphavantage-root` | `data/raw/alphavantage` | Raw news root for alignment. |
| `--allow-overwrite` | Off | Replace an existing Stage 3 artifact root. |
| `--json` | Off | Print machine-readable summary. |

Inputs:

- Stage 2 `dataset_manifest.json`, `benchmark_panel.parquet`, and `row_universe_digest.json`.
- Stage 3 configs `features.yaml` and `labels.yaml`.
- Raw OHLCV files for reference prices.
- Raw Alpha Vantage news files for event-state alignment.

Outputs:

- `market_features.parquet`.
- `event_state_features.parquet`.
- `labels.parquet`.
- `aligned_news.parquet`.
- `row_universe_digest.json`.
- `feature_label_manifest.json`.

Feature/label policies:

- Market feature policy: same-row as-of-close only.
- Event-state embedding model: `deterministic_hash_embedding_v1`.
- Event-state embedding dimension: `8`.
- Event-state pooling policy: mean.
- Target family: `forward_excess_returns`.
- Provider-level Alpha Vantage article completeness is not claimed; truncation-risk flags are preserved.

Validate:

```powershell
python scripts/validate_stage3_completion.py --write
```

### 8.4 Stage 4 Split And Packet-Gate Builder

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet --json
```

Purpose: build purged/embargoed folds, final lockbox assignments, leakage validation, artifact-packet validation, and gate-safe runner evidence.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--stage3-root` | `data/features/phase1_top50` | Stage 3 artifact root or family root. |
| `--output-root` | `data/splits/phase1_top50` | Stage 4 split artifact family output root. |
| `--splits-config` | `configs/splits.yaml` | Active split config. |
| `--artifact-packet-config` | `configs/artifact_packet.yaml` | Packet-member requirements. |
| `--allow-overwrite` | Off | Replace an existing Stage 4 artifact root. |
| `--json` | Off | Print machine-readable summary. |

Inputs:

- Stage 3 feature-label manifest and `labels.parquet`.
- Split config.
- Artifact-packet config.

Outputs:

- `fold_definitions.parquet`.
- `split_assignments.parquet`.
- `split_manifest.json`.
- `lockbox_record.json`.
- `leakage_validation.json`.
- `artifact_packet_validation.json`.
- `benchmark_runner_gate.json`.

Human stdout includes `status: stage4_splits_packet_built`, `benchmark_claim: false`, `artifact_version`, `fold_count`, `lockbox_start_date`, `assignment_row_count`, and `artifact_root`.

Important interpretation:

- Stage 4 creates split, lockbox, leakage, and packet-gate artifacts only.
- It does not train models, compute metrics, or create a benchmark result.

Validate:

```powershell
python scripts/validate_stage4_completion.py --write
```

### 8.5 Stage 5 Model Training And Saved Predictions

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.train_models_and_predict
```

Purpose: train the frozen comparator roster on fold-local training rows and write out-of-sample validation/lockbox predictions without metrics.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--feature-root` | Current Stage 3 root | Feature/label artifact root. |
| `--split-root` | Current Stage 4 root | Split artifact root. |
| `--model-config` | `configs/models.yaml` | Frozen comparator roster and preprocessing policy. |
| `--split-config` | `configs/splits.yaml` | Split config for packet evidence. |
| `--packet-config` | `configs/artifact_packet.yaml` | Serious packet validation config. |
| `--output-root` | Derived Stage 5 root | Optional explicit model artifact root. |

Inputs:

- Stage 3 `market_features.parquet`, `event_state_features.parquet`, `labels.parquet`, and `feature_label_manifest.json`.
- Stage 4 `split_manifest.json` and `split_assignments.parquet`.
- Model config, split config, and packet config.

Outputs:

- `resolved_model_config.json`.
- `comparator_roster_record.json`.
- `saved_predictions.parquet`.
- `preprocessing_fit_manifest.parquet`.
- `model_fit_manifest.parquet`.
- `training_diagnostics.parquet`.
- `search_space_summary.json`.
- `serious_packet_validation.json`.
- `model_manifest.json`.
- `preprocessing_params/*.json`.

Saved-prediction rows include out-of-sample roles only: validation and lockbox. Stage 5 does not create metrics, an overfitting diagnostic report, a comparison summary, or a benchmark result.

Validate:

```powershell
python scripts/validate_stage5_completion.py --write
```

### 8.6 Stage 6 Serious Benchmark Reporting

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
```

Purpose: compute the serious reporting packet from saved predictions and frozen labels.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--feature-root` | Current Stage 3 root | Labels and feature manifest. |
| `--split-root` | Current Stage 4 root | Split manifest and lockbox evidence. |
| `--model-root` | Current Stage 5 root | Saved predictions and model manifest. |
| `--evaluation-config` | `configs/evaluation.yaml` | Metric, ranking, and comparison policy. |
| `--split-config` | `configs/splits.yaml` | Split config for packet evidence. |
| `--packet-config` | `configs/artifact_packet.yaml` | Serious packet validation config. |
| `--output-root` | Current Stage 6 root | Reporting artifact root. |

Inputs:

- Stage 5 `saved_predictions.parquet`, `model_manifest.json`, and `search_space_summary.json`.
- Stage 3 `labels.parquet` and feature manifest.
- Stage 4 split manifest.
- Evaluation and packet configs.

Outputs:

- `resolved_evaluation_config.json`.
- `prediction_label_validation.json`.
- `metrics.parquet`.
- `ranking_diagnostics.parquet`.
- `paired_comparisons.parquet`.
- `overfitting_diagnostic_report.json`.
- `comparison_summary.json`.
- `serious_packet_validation.json`.
- `benchmark_comparability.json`.
- `evaluation_manifest.json`.

Human stdout includes `stage6_serious_benchmark_reporting_built`, `result_class`, `comparability`, and `artifact_root`.

Current interpretation:

- Current result class is `clean_null`.
- Current comparability classification is `limitation_bearing`.
- Do not present Stage 6 as positive, profitable, tradeable, or provider-complete.
- Do not reinterpret Stage 6 using Stage 7C, Stage 8, or Stage 10C artifacts.

Validate:

```powershell
python scripts/validate_stage6_completion.py --write
```

### 8.7 Stage 7C Contextual-Bandit Diagnostics

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_stage7_contextual_bandit --json
```

Purpose: run contextual-bandit development replay diagnostics using approved Stage 3 context, Stage 4 split roles, and Stage 5 saved predictions.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--feature-root` | Current Stage 3 root | Feature/label context. |
| `--split-root` | Current Stage 4 root | Split assignments and lockbox evidence. |
| `--model-root` | Current Stage 5 root | Saved predictions. |
| `--model-config` | `configs/models.yaml` | Model roster/context. |
| `--stage7-config` | `configs/stage7_contextual_bandit.yaml` | Stage 7C diagnostic policy. |
| `--output-root` | Stage 7C family root | Diagnostic artifact root. |
| `--allow-overwrite` | Off | Replace output root. |
| `--split-roles` | `validation` | Comma-separated roles; allowed `validation`, `lockbox`. |
| `--smoke-date-limit` | None | Limit dates per fold/horizon for functionality tests. |
| `--archive-deprecated-settings` | Off | Archive deprecated settings into output evidence. |
| `--write-final-execution-stub` | On | Write final-execution stub evidence. |
| `--target-data-update-end-date` | None | Data-update planning reference. |
| `--json` | Off | Print machine-readable summary. |

Outputs include Stage 7 manifest, context artifacts, policy selections, policy metrics, replay validation, data-update plan evidence, and final-execution stub evidence.

Important interpretation:

- Stage 7C diagnostics do not approve live buy/sell signals.
- Stage 7C diagnostics do not approve all-data final-execution training output.
- Stage 7C diagnostics do not reinterpret the Stage 6 result or promote benchmark comparability.

Validate:

```powershell
python scripts/validate_stage7_completion.py
```

### 8.8 Stage 7 Final-Execution Stub

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_stage7_final_execution --json
```

Purpose: create a Stage 7 final-execution stub manifest without all-data training output.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--stage7-config` | `configs/stage7_contextual_bandit.yaml` | Config used to describe the stub. |
| `--output-root` | `data/stage7_final_execution/phase1_top50/stage7_final_execution_stub_v1` | Stub output root. |
| `--allow-overwrite` | Off | Allow replacing existing stub root. |
| `--run-all-data-training` | Off and blocked | Returns blocked status if supplied. |
| `--json` | Off | Print machine-readable summary. |

Do not use `--run-all-data-training`; it is intentionally blocked until future explicit approval adds real implementation and evidence.

### 8.9 Stage 8 Plan-First Raw Update Scripts

Stage 8 scripts are plan-first. Without `--execute`, they do not call providers and only write a manifest describing planned and skipped raw-file targets.

News daily:

```powershell
python scripts/news_update_daily.py --end-date YYYY-MM-DD
```

News weekly:

```powershell
python scripts/news_update_weekly.py --end-date YYYY-MM-DD
```

OHLCV daily:

```powershell
python scripts/OHLCV_daily_update.py --end-date YYYY-MM-DD --include-spy
```

OHLCV weekly:

```powershell
python scripts/OHLCV_weekly_update.py --end-date YYYY-MM-DD --include-spy
```

Common flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--universe-file` | Approved top-50 universe | CSV with `ticker` column. |
| `--start-date` | Cadence-derived | Optional update-window start date. |
| `--end-date` | Current UTC date | Optional update-window end date. |
| `--manifest` | `data/manifests/stage8_<provider>_<cadence>_update_plan_<date>.json` | Output manifest path. |
| `--ledger` | `data/manifests/stage8_<provider>_<cadence>_request_ledger_<date>.jsonl` | Redacted live request ledger path. |
| `--execute` | Off | Perform live provider calls. Requires explicit approval. |
| `--overwrite` | Off | Overwrite existing target raw files. Requires explicit approval. |
| `--max-tickers` | None | Limit tickers considered. |
| `--max-calls` | `1` | Maximum live calls in one execution. |
| `--sleep-seconds` | `8.0` | Delay between live calls. |
| `--timeout-seconds` | `60` | Provider request timeout. |
| `--env-file` | `.env` | Environment file fallback. |
| `--json` | Off | Print full JSON manifest. |

News-specific flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--limit` | `1000` | Alpha Vantage NEWS_SENTIMENT limit. |
| `--sort` | `LATEST` | Alpha Vantage sort policy. |
| `--base-url` | `https://www.alphavantage.co/query` | Provider endpoint. |
| `--api-key-env` | `ALPHAVANTAGE_API_KEY` | API key environment variable. |
| `--raw-root` | `data/raw/alphavantage` | Target raw root. |

OHLCV-specific flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--full-window-start-date` | `2010-01-01` | Start date for full-window OHLCV target files. |
| `--include-spy` | Off | Include SPY as support ticker, not as top-50 row universe member. |
| `--base-url` | `https://api.twelvedata.com/time_series` | Provider endpoint. |
| `--api-key-env` | `TWELVE_DATA_API_KEY` | API key environment variable. |
| `--raw-root` | `data/raw/twelvedata` | Target raw root. |

Plan manifest fields include `status`, `execute`, `provider`, `endpoint`, `cadence`, `ticker_count`, `planned_count`, `skipped_existing_count`, `planned_entries`, `skipped_existing_entries`, `raw_write_policy`, `secret_policy`, `refresh_impact_note`, and `non_claims`.

Stage 8 non-claims:

- Not a materialized benchmark dataset.
- Not a provider completeness guarantee.
- Not a feature, label, split, model, metric, or benchmark result.
- Not a Stage 6 reinterpretation.
- Not a live trading signal.

If a live Stage 8 run is approved and executed, rerun raw/input audits and review whether Stage 2 through Stage 6 must be rebuilt. Old Stage 6 evidence remains historical until a new validated packet and comparability review exist.

### 8.10 Stage 10C Prediction-Output Packet

Command:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
```

Purpose: generate a local static packet from existing Stage 5 saved predictions, Stage 3 feature/news/label artifacts, and Stage 6 evaluation context.

Primary flags:

| Flag | Default | Meaning |
| --- | --- | --- |
| `--model-root` | Current Stage 5 root | Saved predictions and model manifest. |
| `--feature-root` | Current Stage 3 root | Features, labels, aligned news, feature manifest. |
| `--evaluation-root` | Current Stage 6 root | Evaluation and comparison context. |
| `--output-root` | `data/prediction_outputs/phase1_top50` | Family root; CLI creates a versioned child packet. |
| `--data-cutoff` | None | Optional max as-of date to extract from saved predictions. |
| `--run-date` | None | Optional deterministic run date for packet names. |
| `--allow-overwrite` | Off | Clear and replace same-version packet directory. |
| `--json` | Off | Print machine-readable summary. |

Inputs:

- Stage 5 `saved_predictions.parquet` and `model_manifest.json`.
- Stage 3 `market_features.parquet`, `event_state_features.parquet`, `labels.parquet`, and `aligned_news.parquet`.
- Stage 6 `evaluation_manifest.json`, `comparison_summary.json`, and related context.

Outputs:

- `prediction_output_manifest.json`.
- `model_outputs.parquet` and `model_outputs.csv`.
- `top10_primary_event_state.parquet` and `top10_primary_event_state.csv`.
- `top10_delta_over_market.parquet` and `top10_delta_over_market.csv`.
- `cross_horizon_diagnostic.parquet` and `cross_horizon_diagnostic.csv`.
- `relevant_news_context.parquet` and `relevant_news_context.csv`.
- `trajectory_points.parquet` and `trajectory_points.csv`.
- `limitations.json`.
- `report.html`.
- `validation_report.json`.

Human stdout includes `STAGE10C PREDICTION OUTPUT PACKET`, `status`, `benchmark_claim`, `trading_signal_approved`, `artifact_root`, `data_cutoff`, `model_output_rows`, and `top10_primary_rows`.

Current packet semantics:

- `artifact_schema_version`: `prediction_outputs_v1`.
- `data_cutoff`: `2026-02-13`.
- `model_output_rows`: `250`.
- `forecast_candidate_semantics_used`: `false`.
- Row role: `historical_prediction`.
- `benchmark_claim`: `false`.
- `trading_signal_approved`: `false`.

Validate:

```powershell
python scripts/validate_stage10c_completion.py --prediction-output-root "data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1"
```

Do not treat the Stage 10C packet as fresh future inference, a persisted model-serving package, trading advice, or a benchmark result.

## 9. Stage 2 Through Stage 6 Rebuild Recipe

Use this only after reading `ExecutionPipeline.md` and confirming no approval gate is triggered.

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_benchmark_dataset
python scripts/validate_stage2_completion.py --write
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_features_and_labels
python scripts/validate_stage3_completion.py --write
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.build_splits_and_packet
python scripts/validate_stage4_completion.py --write
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.train_models_and_predict
python scripts/validate_stage5_completion.py --write
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.run_benchmark
python scripts/validate_stage6_completion.py --write
```

After any rebuild, compare row digests, artifact versions, model roster, metric policy, lockbox rules, input limitations, and packet validation before comparing against the existing Stage 6 packet.

## 10. Reading Results And Artifacts

Read manifests before payload files. Manifests define status, counts, identities, paths, limitations, and non-claims.

Stage 2 reading order:

- Start with `dataset_manifest.json`.
- Confirm `identity.benchmark_claim=false`.
- Check `protected_scope`, `coverage`, `clean_window`, `availability`, `limitations`, and `non_claims`.
- Use `benchmark_panel.parquet` for row-level inspection only after the manifest is understood.

Stage 3 reading order:

- Start with `feature_label_manifest.json`.
- Check `features`, `labels`, `news_alignment`, `limitations`, and `non_claims`.
- Use `market_features.parquet`, `event_state_features.parquet`, `labels.parquet`, and `aligned_news.parquet` for feature/label analysis.

Stage 4 reading order:

- Start with `split_manifest.json` and `lockbox_record.json`.
- Confirm leakage validation and packet validation pass.
- Use `split_assignments.parquet` to inspect fold and split-role membership.

Stage 5 reading order:

- Start with `model_manifest.json`.
- Confirm `benchmark_claim=false` and `non_claims` include no metrics/result.
- Use `saved_predictions.parquet` only as out-of-sample prediction evidence, not as a benchmark result.

Stage 6 reading order:

- Start with `comparison_summary.json`, `benchmark_comparability.json`, and `evaluation_manifest.json`.
- Then inspect `metrics.parquet`, `ranking_diagnostics.parquet`, and `paired_comparisons.parquet`.
- Preserve current `clean_null` and `limitation_bearing` wording unless a new approved run and comparability review changes it.

Stage 7C reading order:

- Start with `stage7_manifest.json`, `replay_validation.json`, and policy metric artifacts.
- Treat top-k/bottom-k outputs as diagnostics only, not trading signals.

Stage 10C reading order:

- Start with `prediction_output_manifest.json`, `limitations.json`, and `validation_report.json`.
- Then inspect `model_outputs.parquet`, top-10 tables, `relevant_news_context.parquet`, `trajectory_points.parquet`, and `report.html`.
- Treat rows as `historical_prediction` unless a future approved artifact explicitly says otherwise.

## 11. Artifact Field Guide

Common identity fields:

| Field | Meaning |
| --- | --- |
| `artifact_type` | Human-readable type marker for the artifact or manifest. |
| `artifact_schema_version` or stage-specific schema version | Machine-readable schema family. |
| `artifact_version` or `dataset_version` | Versioned identity derived from input versions, clean windows, hashes, and stage suffixes. |
| `artifact_root` | Directory containing the artifact packet. |
| `generated_at_utc` | Creation timestamp. |
| `benchmark_claim` | Whether the artifact claims benchmark-result status. This is false for most stages except validated reporting context. |
| `row_universe_digest` | Digest over row keys to verify row-universe consistency across stages. |

Common safety fields:

| Field | Meaning |
| --- | --- |
| `limitations` | Known limitations that must travel with the artifact. |
| `non_claims` | Explicit statements of what the artifact does not prove. |
| `sensitive_artifacts_excluded` | Files intentionally excluded from shareable evidence. |
| `provider_truncation_risk_flag` | Row/window indicator that provider-level completeness may be limited. |
| `no_news_flag` | Row indicator that no aligned news exists for the row under the current alignment policy. |
| `split_role` | Train, validation, lockbox, or pending split role depending on stage. |
| `fold_id` | Walk-forward fold identifier or pending role depending on stage. |

Common row keys:

- `benchmark_family_id`.
- `canonical_ticker`.
- `as_of_date`.
- `horizon_id`.

Approved horizons:

- `1d`.
- `5d`.
- `10d`.
- `20d`.
- `60d`.

## 12. Model-Output Usage Interface

This section preserves the useful intent of the former API-style reference: how to call the current local model-output interface and how to consume the result. The current supported call is not arbitrary future inference. It is local extraction and formatting of already-saved Stage 5 out-of-sample predictions.

### 12.1 Current Supported Call

Use this when you want a readable local packet for the latest available saved-prediction date:

```powershell
$env:PYTHONPATH="src"; python -m event_state_forecasting.cli.generate_prediction_outputs --run-date 2026-05-23 --allow-overwrite --json
```

Conceptual request contract:

| Request field | CLI flag | Required | Default/current value | Meaning |
| --- | --- | --- | --- | --- |
| `model_root` | `--model-root` | No | Current Stage 5 root | Where `saved_predictions.parquet` and `model_manifest.json` are read. |
| `feature_root` | `--feature-root` | No | Current Stage 3 root | Where feature, label, and aligned-news artifacts are read. |
| `evaluation_root` | `--evaluation-root` | No | Current Stage 6 root | Where Stage 6 selected market hurdles and result context are read. |
| `output_root` | `--output-root` | No | `data/prediction_outputs/phase1_top50` | Family root where a versioned packet child is created. |
| `data_cutoff` | `--data-cutoff` | No | Latest saved-prediction date | Max `as_of_date` to extract from saved predictions. |
| `run_date` | `--run-date` | No | Current UTC date | Packet naming date; use explicit date for deterministic reruns. |
| `allow_overwrite` | `--allow-overwrite` | No | false | Clear and replace the same-version packet directory. |
| `json` | `--json` | No | false | Print machine-readable summary to stdout. |

Conceptual response contract:

| Response field | Meaning |
| --- | --- |
| `status` | Stage 10C status, currently `stage10c_prediction_output_packet_created`. |
| `benchmark_claim` | Always false for Stage 10C packet generation. |
| `trading_signal_approved` | Always false. |
| `artifact_root` | Versioned output directory to read. |
| `data_cutoff` | Snapshot date selected from saved predictions. |
| `model_output_rows` | Number of rows in `model_outputs`. Current packet has `250`. |
| `top10_primary_rows` | Number of primary top-10 rows. Current packet has `50`. |

### 12.2 What Counts As Calling The Model

Current valid meanings:

- Rebuild Stage 5 with `train_models_and_predict` to generate saved out-of-sample predictions from approved Stage 3/4 artifacts.
- Generate a Stage 10C packet from existing Stage 5 saved predictions.
- Read `model_outputs.parquet` or CSV from the Stage 10C packet.

Current invalid meanings:

- Sending a new ad hoc feature row to a persisted model service.
- Asking for tomorrow's forecast from live data.
- Calling an HTTP endpoint.
- Treating a top-10 row as a trade recommendation.
- Treating `forecast_candidate` as approved row semantics.

### 12.3 Minimal Consumption Examples

Read the Stage 10C manifest:

```powershell
python -c "import json, pathlib; p=pathlib.Path('data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1/prediction_output_manifest.json'); print(json.dumps(json.loads(p.read_text()), indent=2)[:4000])"
```

Read the model-output CSV without Parquet tooling:

```powershell
python -c "import csv, pathlib; p=pathlib.Path('data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1/model_outputs.csv'); rows=list(csv.DictReader(p.open())); print(len(rows)); print(rows[0])"
```

Read the primary top-10 table:

```powershell
python -c "import csv, pathlib; p=pathlib.Path('data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1/top10_primary_event_state.csv'); [print(row['horizon_id'], row['event_state_rank'], row['canonical_ticker'], row['event_state_prediction']) for row in list(csv.DictReader(p.open()))[:10]]"
```

Read with pandas when Parquet support is available:

```powershell
python -c "import pandas as pd; p='data/prediction_outputs/phase1_top50/2026-05-23__cutoff_20260213__src_e4be8957b633__rows_6868e3b80086__stage5_b68e237c0d0f__prediction_outputs_v1/model_outputs.parquet'; df=pd.read_parquet(p); print(df[['canonical_ticker','horizon_id','row_role','event_state_prediction','delta_over_market_hurdle']].head())"
```

### 12.4 Ranking Semantics

| Ranking/view | Source file | Meaning | Caveat |
| --- | --- | --- | --- |
| Primary event-state top-10 | `top10_primary_event_state.*` | Highest per-horizon `event_state_prediction` rows from `event_state_gated_fusion`. | Per-horizon model output only; not trading advice. |
| Secondary delta top-10 | `top10_delta_over_market.*` | Highest per-horizon delta over selected Stage 6 market hurdle. | Model-comparison context, not proof of superiority. |
| Cross-horizon diagnostic | `cross_horizon_diagnostic.*` | Mean percentile-style aggregation across horizons by ticker. | Diagnostic only; not a trading score. |
| Trajectory markers | `trajectory_points.*` | Historical observed close context plus forecast markers. | No projected price path or fan chart. |
| Relevant news context | `relevant_news_context.*` | Deterministic aligned-news snippets for primary top-10 rows. | URLs excluded; no LLM summaries. |

### 12.5 Current Market Hurdle Usage

Stage 10C reads selected market hurdles from Stage 6 evaluation context. The configured Stage 6 market hurdle policy is `per_horizon_best_market_only_by_validation_rmse_then_mae`, with candidates:

- `market_zero_excess_return`.
- `market_train_mean`.
- `market_ridge`.
- `market_elastic_net`.
- `market_random_forest`.
- `market_hist_gradient_boosting`.
- `market_mlp`.

The event-state model used for Stage 10C primary output is `event_state_gated_fusion`.

## 13. Table And Column Reference

This is the local artifact equivalent of an API schema reference. Columns listed here are the columns users are most likely to read or validate.

### 13.1 Stage 5 Saved Predictions

Source file: `saved_predictions.parquet` under the Stage 5 model root.

Required columns from `configs/models.yaml`:

| Column | Meaning |
| --- | --- |
| `row_key` | Stable row identity key. |
| `benchmark_family_id` | Benchmark family, currently `phase1_top50`. |
| `canonical_ticker` | Canonical ticker. |
| `as_of_date` | Prediction as-of date. |
| `horizon_id` | One of `1d`, `5d`, `10d`, `20d`, `60d`. |
| `fold_id` | Walk-forward fold identifier. |
| `split_role` | Allowed saved-prediction roles are `validation` and `lockbox`. |
| `model_id` | Model identifier from the frozen roster. |
| `model_family` | Model family, such as `ridge`, `random_forest`, or `simple_gated_fusion`. |
| `branch` | `market_only` or `event_state`. |
| `dataset_version` | Input Stage 2 dataset version. |
| `feature_artifact_version` | Input Stage 3 artifact version. |
| `split_artifact_version` | Input Stage 4 artifact version. |
| `stage5_artifact_version` | Stage 5 artifact version. |
| `prediction` | Saved model prediction for the row/horizon/model. |

Forbidden saved-prediction roles:

- `train`.
- `purged`.
- `embargoed`.
- `excluded`.

### 13.2 Stage 10C `model_outputs`

Source files: `model_outputs.parquet` and `model_outputs.csv`.

| Column | Meaning |
| --- | --- |
| `benchmark_family_id` | Benchmark family. |
| `canonical_ticker` | Ticker. |
| `as_of_date` | Historical prediction snapshot date. |
| `horizon_id` | Forecast horizon represented by the saved prediction. |
| `row_role` | Current value should be `historical_prediction`. |
| `split_role` | Validation or lockbox source role from Stage 5. |
| `fold_id` | Source fold. |
| `event_state_model_id` | Current primary event-state model, `event_state_gated_fusion`. |
| `event_state_model_family` | Current family, `simple_gated_fusion`. |
| `event_state_branch` | Current branch, `event_state`. |
| `event_state_prediction` | Event-state model output. |
| `market_hurdle_model_id` | Selected Stage 6 market-only hurdle for the horizon. |
| `market_hurdle_prediction` | Market-hurdle model output. |
| `delta_over_market_hurdle` | `event_state_prediction - market_hurdle_prediction`. |
| `event_state_rank` | Per-horizon descending rank by event-state prediction. |
| `delta_rank` | Per-horizon descending rank by delta over market hurdle. |
| `event_state_percentile_by_horizon` | Percentile-style score derived from event-state rank. |
| `delta_percentile_by_horizon` | Percentile-style score derived from delta rank. |
| `cross_horizon_score` | Mean event-state percentile by ticker across horizons. |
| `cross_horizon_delta_score` | Mean delta percentile by ticker across horizons. |
| `dataset_version` | Source dataset version. |
| `feature_artifact_version` | Source feature artifact version. |
| `split_artifact_version` | Source split artifact version. |
| `stage5_artifact_version` | Source Stage 5 artifact version. |
| `label_window_start` | Historical label-window start used for realized label context. |
| `label_window_end` | Historical label-window end used for realized label context. |
| `realized_forward_excess_return` | Historical realized label value, present because these are historical predictions. |
| `label_available_flag` | Label availability flag. |
| `market_close` | Market close used for context. |
| `stage3_aligned_news_count` | Count of aligned news records in Stage 3. |
| `provider_empty_feed_flag` | Whether provider feed was empty for the relevant window. |
| `provider_truncation_risk_flag` | Whether provider truncation risk is present. |
| `minutes_since_latest_aligned_article` | Recency feature for latest aligned article. |
| `no_news_flag` | Whether no news aligned to the row. |
| `empty_event_state_flag` | Whether event-state vector is explicitly empty. |
| `not_trading_advice` | Must be true. |
| `not_benchmark_result` | Must be true. |
| `not_stage6_reinterpretation` | Must be true. |
| `trading_signal_approved` | Must be false. |
| `service_api_scope` | Must be false. |
| `forecast_candidate_approved` | Must be false. |

### 13.3 Stage 10C Top-10 Tables

Files:

- `top10_primary_event_state.parquet` and `.csv`.
- `top10_delta_over_market.parquet` and `.csv`.

Both tables include the `model_outputs` columns plus view metadata:

| Column | Meaning |
| --- | --- |
| `view_id` | `primary_event_state_score` or `secondary_delta_over_market_hurdle`. |
| `view_priority` | `1` for primary, `2` for secondary. |
| `ranking_caveat` | Embedded caveat explaining non-trading/non-proof semantics. |

The top-10 validator expects exactly 10 rows for each approved horizon.

### 13.4 Stage 10C `cross_horizon_diagnostic`

Source files: `cross_horizon_diagnostic.parquet` and `.csv`.

| Column | Meaning |
| --- | --- |
| `canonical_ticker` | Ticker. |
| `as_of_date` | Snapshot date. |
| `row_role` | Current role, historical prediction. |
| `split_role` | Source split role. |
| `horizon_count` | Number of horizons included. |
| `mean_event_state_prediction` | Mean event-state prediction across horizons. |
| `mean_delta_over_market_hurdle` | Mean delta across horizons. |
| `cross_horizon_score` | Aggregated event-state percentile score. |
| `cross_horizon_delta_score` | Aggregated delta percentile score. |
| `provider_truncation_risk_any` | Whether any horizon row has truncation risk. |
| `no_news_any` | Whether any horizon row has no-news flag. |
| `cross_horizon_rank` | Diagnostic cross-horizon rank. |
| `view_id` | `tertiary_cross_horizon_diagnostic`. |
| `ranking_caveat` | Non-trading diagnostic caveat. |

### 13.5 Stage 10C `relevant_news_context`

Source files: `relevant_news_context.parquet` and `.csv`.

| Column | Meaning |
| --- | --- |
| `canonical_ticker` | Ticker from the primary top-10 row. |
| `as_of_date` | Snapshot date. |
| `horizon_id` | Horizon for the primary top-10 row. |
| `event_state_rank` | Primary event-state rank. |
| `news_context_rank` | Rank among selected aligned news items for that row. |
| `context_status` | `aligned_article_found`, `article_id_not_found`, or `no_aligned_news`. |
| `article_id` | Deterministic Stage 3 aligned-news article identifier. |
| `published_timestamp` | Article timestamp when available. |
| `roll_forward_reason` | Alignment reason from Stage 3. |
| `title_snippet` | Clipped article title text. |
| `summary_snippet` | Clipped article summary text. |
| `text_hash` | Article text hash. |
| `url_included` | Must be false. |
| `llm_summary_used` | Must be false. |
| `no_news_flag` | Stage 3 no-news flag. |
| `provider_truncation_risk_flag` | Stage 3 provider truncation risk flag. |
| `stage3_aligned_news_count` | Stage 3 aligned-news count. |

### 13.6 Stage 10C `trajectory_points`

Source files: `trajectory_points.parquet` and `.csv`.

| Column | Meaning |
| --- | --- |
| `benchmark_family_id` | Benchmark family. |
| `canonical_ticker` | Ticker. |
| `as_of_date` | Historical date. |
| `horizon_id` | Null for observed close history, horizon for forecast marker rows. |
| `point_type` | `observed_close` or `forecast_marker`. |
| `market_close` | Historical market close. |
| `event_state_prediction` | Event-state output for marker rows; null for history rows. |
| `market_hurdle_prediction` | Market-hurdle output for marker rows; null for history rows. |
| `delta_over_market_hurdle` | Delta output for marker rows; null for history rows. |
| `label_window_end` | Historical label-window end for marker rows. |
| `realized_forward_excess_return` | Historical realized label for marker rows. |
| `projected_price_path` | Must be false. |

The trajectory table combines up to 21 historical observed close points per ticker with forecast-marker rows. It intentionally does not generate projected future price paths.

## 14. Config Reference

Configs are part of the usage contract because they define the meaning of command inputs and outputs.

### 14.1 `configs/features.yaml`

| Field | Current value |
| --- | --- |
| `artifact_schema_version` | `stage3_features_v1`. |
| Market close time | `16:00:00`. |
| Exchange timezone | `America/New_York`. |
| Same-day news policy | At or before close assigns to same trading date. |
| After-close policy | Roll forward to next trading date. |
| Non-trading-day policy | Roll forward to next trading date. |
| Embedding model | `deterministic_hash_embedding_v1`. |
| Embedding dimension | `8`. |
| Pooling policy | `mean`. |
| Empty vector policy | `zero_vector`. |

Stage 3 scalar event-state enrichments:

- `stage3_aligned_news_count`.
- `no_news_flag`.
- `empty_event_state_flag`.
- `provider_empty_feed_flag`.
- `provider_truncation_risk_flag`.
- `minutes_since_latest_aligned_article`.

### 14.2 `configs/labels.yaml`

| Field | Current value |
| --- | --- |
| `artifact_schema_version` | `stage3_labels_v1`. |
| `target_family` | `forward_excess_returns`. |
| `horizons` | `1d`, `5d`, `10d`, `20d`, `60d`. |
| `return_type` | `simple`. |
| `reference_policy` | `leave_one_out_equal_weight_approved_universe`. |
| `endpoint_null_policy` | `stage2_clean_window_requires_full_endpoints`. |
| `formula` | Ticker forward simple return minus leave-one-out equal-weight universe forward simple return. |

### 14.3 `configs/splits.yaml`

| Field | Current value |
| --- | --- |
| `artifact_schema_version` | `stage4_splits_v1`. |
| `split_protocol` | `purged_embargoed_walk_forward_with_final_untouched_lockbox`. |
| `benchmark_family_id` | `phase1_top50`. |
| Fold cadence | Monthly. |
| Training window | Expanding. |
| Initial training date count | `126`. |
| Validation date count | `21`. |
| Drop partial validation windows | true. |
| Purge/embargo policy | Maximum approved label horizon. |
| Purge/embargo trading dates | `60`. |
| Lockbox policy | Final fraction of Stage 3 as-of dates. |
| Lockbox fraction | `0.20`. |
| Expected lockbox start | `2025-09-30`. |
| Random shuffle allowed | false. |
| Benchmark claim | false. |

### 14.4 `configs/models.yaml`

Comparator ladder summary:

| Field | Current value |
| --- | --- |
| `artifact_schema_version` | `stage5_models_v1`. |
| `roster_id` | `phase1_top50_pragmatic_broader_sklearn_v1`. |
| Seed | `1729`. |
| Search policy | `tiny_fixed_no_hyperparameter_search`. |
| Prediction scope | `development_validation_plus_lockbox_no_metrics`. |
| Preprocessing policy | `model_specific_safe_train_only_v1`. |

Model roster:

| Model ID | Family | Branch | Allowed inputs | Preprocessing |
| --- | --- | --- | --- | --- |
| `market_zero_excess_return` | `constant_zero` | `market_only` | Market features | none. |
| `market_train_mean` | `constant_train_mean` | `market_only` | Market features | none. |
| `market_ridge` | `ridge` | `market_only` | Market features | median impute and scale. |
| `market_elastic_net` | `elastic_net` | `market_only` | Market features | median impute and scale. |
| `market_random_forest` | `random_forest` | `market_only` | Market features | median impute. |
| `market_hist_gradient_boosting` | `hist_gradient_boosting` | `market_only` | Market features | median impute. |
| `market_mlp` | `mlp` | `market_only` | Market features | median impute and scale. |
| `event_state_gated_fusion` | `simple_gated_fusion` | `event_state` | Market plus event-state features | median impute and scale. |

Market feature set:

- `market_open`.
- `market_high`.
- `market_low`.
- `market_close`.
- `market_volume`.
- `market_intraday_return`.
- `market_intraday_range_ratio`.

Event-state feature set:

- `stage3_aligned_news_count`.
- `provider_empty_feed_flag`.
- `provider_truncation_risk_flag`.
- `minutes_since_latest_aligned_article`.
- `event_state_hash_embedding_00` through `event_state_hash_embedding_07`.
- `no_news_flag`.
- `empty_event_state_flag`.

Gated-fusion gate features:

- `stage3_aligned_news_count`.
- `provider_empty_feed_flag`.
- `provider_truncation_risk_flag`.
- `minutes_since_latest_aligned_article`.
- `no_news_flag`.
- `empty_event_state_flag`.

### 14.5 `configs/evaluation.yaml`

| Field | Current value |
| --- | --- |
| `artifact_schema_version` | `stage6_evaluation_config_v1`. |
| Primary regression metrics | `rmse`, `mae`, `r2_oos`, `mean_loss_difference_vs_market_hurdle`. |
| R2 baseline | `market_zero_excess_return`. |
| Market hurdle policy | `per_horizon_best_market_only_by_validation_rmse_then_mae`. |
| Event-state model ID | `event_state_gated_fusion`. |
| Ranking diagnostics | Spearman rank IC, Kendall rank correlation, directional hit rate, top-minus-bottom spread. |
| Minimum cross-section | `20`. |
| Top/bottom fraction | `0.2`. |
| Paired comparison policy | Loss-delta summary, no p-values. |
| Result classification policy | `short_horizon_primary_3_v1`. |
| Primary horizons | `1d`, `5d`, `10d`. |
| Robust positive requirement | At least 2 primary horizons improve required loss metrics. |
| Conditional positive requirement | At least 1 primary horizon improves required loss metrics. |
| Lockbox policy | Final reporting read once. |
| Lockbox tuning allowed | false. |
| Train-validation gap policy | Explicitly block if train predictions absent. |

## 15. Raw Data And Provider Utilities

Active raw-data utility scripts:

| Script | Status | Purpose | Safe default |
| --- | --- | --- | --- |
| `scripts/run_alphavantage_news_top50_only_standalone.py --plan --skip-seed-migration` | Active planner/runner | Plan or run top-50 Alpha Vantage collection | Use plan mode unless live call approval exists. |
| `scripts/run_alphavantage_news_truncation_refinement_quarterly.py --plan` | Active planner/runner | Plan truncation-refinement requests | Plan mode. |
| `scripts/run_alphavantage_news_truncation_refinement_standalone.py --plan --order reverse` | Active planner/runner | Portable truncation-refinement planning | Plan mode. |
| `scripts/audit_deprecated_ohlcv_salvage.py` | Active audit | Audit deprecated OHLCV salvage evidence | Read-only. |
| `scripts/audit_twelvedata_ohlcv_coverage.py` | Active audit | Audit active raw Twelve Data coverage | Read-only. |
| `scripts/download_missing_twelvedata_ohlcv.py` | Active plan/execute utility | Plan or download missing Twelve Data OHLCV | Plan unless live call approval exists. |
| `scripts/audit_stage1_universe_ohlcv.py` | Active audit | Audit Stage 1 universe/OHLCV state | Read-only. |

Raw-data cautions:

- Raw top-50 Alpha Vantage file coverage is not provider-level article completeness.
- Alpha Vantage windows with exactly 1000 rows can still be truncation-risk windows.
- Twelve Data full-window OHLCV coverage is raw coverage, not a benchmark result.
- SPY is a support ticker, not a top-50 row-universe member.
- Deprecated OHLCV evidence is reference-only unless explicitly reintroduced through active docs.
- Raw request ledgers may contain API-key-bearing URLs and must not be committed or shared as-is.

## 16. Planned Or Scaffolded Command Entries

These files intentionally exist as comments only or blocked stubs. Their planned functions are documented so users know what is not available yet.

| Planned entry | Status | Planned function | Required approval before activation | Planned input/output contract |
| --- | --- | --- | --- | --- |
| `event_state_forecasting.cli.audit_raw_data` | Comment-only scaffold | `run_raw_data_audit` for raw provider coverage, schema, truncation, and credential-risk audits | Implementation approval and executable tests | Read raw roots/manifests; output audit report without raw mutation. |
| `event_state_forecasting.cli.build_market_data` | Comment-only scaffold | `run_market_data_build` | Provider-boundary implementation approval | Read universe/provider config/date range; output raw or normalized OHLCV artifacts. |
| `event_state_forecasting.cli.build_news_data` | Comment-only scaffold | `run_news_data_build` | News normalization implementation approval | Read raw Alpha Vantage payloads; output normalized news with truncation/empty-feed flags. |
| `event_state_forecasting.cli.build_splits` | Comment-only scaffold | `run_split_build` | Superseded by active `build_splits_and_packet` unless reactivated deliberately | Read dataset/labels/config; output folds, lockbox, leakage summary. |
| `event_state_forecasting.cli.sanitize_provider_ledgers` | Comment-only scaffold | `run_ledger_sanitization` | Security/sanitization implementation approval | Read raw ledgers; output redacted copies and redaction report. |
| `event_state_forecasting.cli.validate_universe` | Comment-only scaffold | `run_universe_validation` | Universe validation implementation approval | Read universe CSV; output row count, duplicates, canonical ticker report. |
| `event_state_forecasting.cli.summarize_run` | Comment-only scaffold | `run_summary_report` | Summary CLI implementation approval | Read completed packets; output traceable human-readable summaries without metric recomputation. |
| Persisted fitted-model inference package | Not deployed | Arbitrary new-row scoring | Separate explicit approval for packaging, feature-only rows, and row-role semantics | Would need saved fitted estimators, preprocessors, feature schema, cutoff policy, and validation. |
| `forecast_candidate` output rows | Not approved | True future forecast rows | Separate explicit approval | Must not overwrite current `historical_prediction` semantics. |
| Service/API/dashboard | Out of scope | User-facing serving/UI | Separate product/scope approval | Not part of phase-1 local artifact boundary. |

## 17. Error Handling And Exit Codes

Most active CLIs fail closed and return nonzero exit status on unsafe or malformed inputs.

Common failure prefixes:

| Prefix | Source | Typical cause |
| --- | --- | --- |
| `STAGE2_DATASET_BUILD_FAILED` | Stage 2 builder | Missing raw inputs, scope mismatch, clean-window issue, output already exists without overwrite. |
| `STAGE3_FEATURE_LABEL_BUILD_FAILED` | Stage 3 builder | Missing Stage 2 artifacts, config mismatch, row-digest mismatch, output already exists without overwrite. |
| `STAGE4_SPLIT_PACKET_BUILD_FAILED` | Stage 4 builder | Missing Stage 3 artifacts, leakage validation failure, packet validation issue. |
| Runtime error from Stage 5 | Stage 5 trainer | Empty train/prediction rows, label alignment failure, invalid model config. |
| Runtime error from Stage 6 | Stage 6 reporting | Missing predictions/labels/configs or invalid packet evidence. |
| `STAGE7_CONTEXTUAL_BANDIT_FAILED` | Stage 7C diagnostics | Invalid config, unsupported split role, replay/artifact validation issue. |
| `STAGE7_FINAL_EXECUTION_BLOCKED` | Stage 7 final-execution stub | Existing output root without overwrite, or blocked all-data training flag. |
| Stage 8 blocked status | Stage 8 update scripts | Missing API key, invalid max calls, provider error, or malformed provider payload. |
| `STAGE10C_PREDICTION_OUTPUTS_FAILED` | Stage 10C packet generator | Missing inputs, invalid saved-prediction context, existing output without overwrite, packet validation issue. |

Overwrite behavior:

- `--allow-overwrite` on stage artifact builders is an explicit local artifact replacement intent.
- Stage 10C `--allow-overwrite` clears the same-version packet directory before writing, preventing stale leftover files from surviving reruns.
- Stage 8 `--overwrite` applies to raw provider target files and requires stricter review than ordinary derived-artifact overwrite.

## 18. Development And Testing Notes

Useful focused checks:

```powershell
python -m pytest tests/stage10
python -m pytest tests
python -m compileall -q src scripts tests
```

Current known full-suite status after Stage 10C: `58 passed`.

Do not change protected benchmark scope without explicit approval. Protected-scope changes include target family, horizons, provider stack, universe, alignment, split policy, comparator roster, metric/result policy, lockbox interpretation, benchmark family, or benchmark comparability treatment.

## 19. Documentation Maintenance Checklist

When a stage or usage behavior changes, update the relevant active docs together:

- `UsageManual.md` for commands, inputs, outputs, and artifact reading.
- `ExecutionPipeline.md` for sequencing, approval gates, and comparability discipline.
- `ExecutionFlow.md`, README, and guidebook discoverability entries.
- Stage prompt files if the future workflow contract changes.
- `ScopeDecisionLog.md` and `ResearchTruth.md` if truth, decisions, or non-claims change.
- `docs/agent/agent_log/Current_State.md` and `docs/agent/agent_log/Event_Ledger.ndjson` for operational memory.

After documentation updates, run governance validation, scaffold validation, and ledger JSONL parsing.
