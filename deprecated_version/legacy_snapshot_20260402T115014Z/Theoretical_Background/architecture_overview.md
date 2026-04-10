# Architecture Overview

This document describes the current implemented architecture of the repository and the intended boundaries between major subsystems.

## System goal

The repository implements a thesis-grade end-of-day financial forecasting pipeline built around:
- daily market data,
- aligned company news,
- optional company knowledge-base metadata,
- multi-horizon labels,
- market-only baselines,
- and a first multimodal market + event-state model.

The system is designed so that data correctness, leakage safety, and reproducibility are established before model complexity.

## Current end-to-end architecture

### 1. Runtime and configuration layer

Implemented modules:
- `src/utils/config_loader.py`
- `src/utils/paths.py`
- `src/utils/logging_setup.py`
- `src/utils/io_utils.py`
- `src/utils/reproducibility.py`

Responsibilities:
- load local `.env` safely,
- load YAML configs,
- resolve canonical paths,
- create run-aware logs,
- persist manifests and artifacts,
- capture reproducibility metadata.

### 2. Provider and ingestion layer

Implemented provider clients:
- `src/data/twelve_data_client.py`
- `src/data/finnhub_client.py`
- `src/data/sec_edgar_client.py`
- `src/data/split_events_client.py`

Implemented ingestion pipelines:
- `src/data/price_pipeline.py`
- `src/data/news_pipeline.py`
- `src/data/company_kb_pipeline.py`

Implemented CLI entry points:
- `src/cli/build_market_data.py`
- `src/cli/build_news_data.py`
- `src/cli/build_company_kb.py`

Responsibilities:
- fetch raw source payloads,
- preserve immutable raw dumps,
- write request ledgers,
- normalize provider-specific payloads into canonical interim tables,
- emit quality reports and manifests.

### 3. Data contracts and storage layer

Implemented module:
- `src/data/data_contracts.py`

Implemented storage guides:
- `docs/data_layout.md`
- `data/**/README.md`

Responsibilities:
- define canonical schemas,
- validate column presence and uniqueness,
- validate manifests,
- keep raw/interim/final/embeddings/KB layers separate.

### 4. Corporate-action handling layer

Implemented modules:
- `src/data/corporate_actions.py`
- integration inside `src/data/price_pipeline.py`

Responsibilities:
- normalize split events,
- compute cumulative future split factors,
- generate adjusted OHLCV histories,
- keep raw and adjusted histories separate,
- emit split-adjustment diagnostics.

### 5. Feature and target layer

Implemented modules:
- `src/features/market_features.py`
- `src/features/news_text.py`
- `src/features/news_embeddings.py`
- `src/features/event_state.py`
- `src/features/labels.py`

Responsibilities:
- build conservative market features from adjusted prices,
- normalize article text and hashes,
- precompute article embeddings,
- aggregate event states with recency weighting,
- generate multi-horizon labels.

### 6. Temporal validation and leakage-control layer

Implemented modules:
- `src/split/alignment_rules.py`
- `src/split/walk_forward_splits.py`
- `src/split/purged_embargo_splits.py`
- `src/split/leakage_checks.py`

Responsibilities:
- encode the official as-of-close policy,
- generate chronological folds,
- purge overlapping label windows,
- apply embargo logic,
- provide reusable leakage assertions.

### 7. Final dataset assembly layer

Implemented modules:
- `src/data/modeling_dataset.py`
- `src/cli/build_modeling_dataset.py`

Responsibilities:
- join adjusted prices, market features, labels, optional event states, and optional company metadata,
- preserve one row per `(ticker, date)`,
- write final panel parquet files and manifests.

### 8. Modeling layer

Implemented market-only stack:
- `src/models/baseline_models.py`
- `src/models/loss_functions.py`
- `src/models/dataloaders.py`
- `src/models/trainer.py`
- `src/models/inference.py`
- `src/cli/train_market_baseline.py`

Implemented first multimodal stack:
- `src/models/multimodal_models.py`
- multimodal extensions inside:
  - `src/models/dataloaders.py`
  - `src/models/trainer.py`
  - `src/models/inference.py`
- `src/cli/train_multimodal_model.py`

Responsibilities:
- train market-only baselines,
- train the first gated multimodal regressor,
- persist checkpoints, predictions, metrics, and run metadata.

### 9. Evaluation and ablation layer

Implemented modules:
- `src/models/metric_registry.py`
- `src/models/calibration.py`
- `src/models/statistical_tests.py`
- `src/models/ablation_runner.py`
- `src/cli/evaluate_experiments.py`
- `src/cli/run_ablations.py`

Responsibilities:
- evaluate stored predictions against frozen labels,
- compute regression, classification, and ranking metrics,
- support post-hoc calibration utilities,
- run simple statistical comparisons,
- aggregate ablation summaries across runs.

## Architectural boundaries that must remain true

- Provider clients should stay thin and provider-specific.
- Canonical schemas should stay centralized in `src/data/data_contracts.py`.
- Feature generation should operate on canonical tables, not raw payloads.
- Split logic should stay explicit and auditable.
- Alignment logic should stay centralized in `src/split/alignment_rules.py`.
- Evaluation logic should operate on saved predictions and frozen labels, not hidden notebook state.
- Training and evaluation should remain separate from ingestion pipelines.

## Current limitations

- The current multimodal model is intentionally simple.
- The company-profile branch is not yet wired into model training.
- Richer evaluation/reporting layers are still limited.
- Some documentation files still summarize future extensions that have not yet been implemented.

## Immediate next architectural priorities

1. Finish documentation hardening and consistency updates.
2. Add richer evaluation/report generation.
3. Add optional company-profile training support.
4. Add more advanced multimodal ablations only after current results are stable and reproducible.
