# Data Layout

This document defines the current canonical storage layout for the project.

The code-level source of truth for schemas is:
- `src/data/data_contracts.py`

This document translates those contracts into a storage and workflow guide.

## Design principles

- Preserve raw provider payloads immutably.
- Normalize each source into stable interim tables.
- Keep adjusted prices separate from raw prices.
- Build model-ready datasets only from validated upstream tables.
- Version final datasets with manifests.
- Prefer columnar formats for canonical tables.

## Storage layers

### Raw

Purpose:
- preserve provider responses exactly enough to make interim rebuilding deterministic,
- retain request ledgers for auditability,
- record ingestion metadata and failure states.

Recommended contents:
- `data/raw/twelvedata/`
- `data/raw/finnhub/`
- `data/raw/sec/`
- `data/raw/universe/`

Recommended file types:
- JSON for provider payloads,
- Parquet or JSON for request ledgers,
- CSV for frozen universe snapshots when appropriate.

### Interim

Purpose:
- store normalized source tables that are still close to provider semantics,
- keep split events and adjusted prices here,
- keep company metadata here before it becomes model features.

Canonical tables expected in this layer:
- `prices_daily`
- `adjusted_prices_daily`
- `news_articles`
- `split_events`
- `company_kb`

Current implementation note:
- raw `prices_daily` and split-adjusted `adjusted_prices_daily` are intentionally separate branches,
- adjusted prices are generated locally from explicit split events rather than by mutating raw price history.

### Final

Purpose:
- store training-ready or evaluation-ready datasets derived from validated upstream tables.

Canonical tables expected in this layer:
- `event_states_daily`
- `labels_multi_horizon`
- `modeling_panel`

### Embeddings

Purpose:
- store offline article embeddings and any future derived pooled representations.

Canonical tables expected in this layer:
- `article_embeddings`

### Knowledge Base

Purpose:
- store identity and profile tables that support company metadata enrichment and future entity linking.

Primary canonical table:
- `company_kb`

### Manifests

Purpose:
- store dataset manifests and coverage metadata for reproducibility.

Each final dataset version should have a manifest with at least:
- `manifest_version`
- `dataset_name`
- `dataset_version`
- `schema_version`
- `created_at_utc`
- `source_tables`

## Canonical table summary

The canonical contracts below are defined in `src/data/data_contracts.py`.

### `market_data_request_ledger`

Layer:
- raw

Purpose:
- preserve market-ingestion request metadata and quota usage.

Required columns:
- `request_id`
- `provider`
- `endpoint`
- `ticker`
- `requested_at_utc`
- `response_status`
- `success`
- `raw_path`

Uniqueness:
- unique on `request_id`

Partition recommendation:
- partition or group by `ticker`

### `prices_daily`

Layer:
- interim

Required columns:
- `date`
- `ticker`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `source`
- `ingest_ts`

Uniqueness:
- unique on `(ticker, date)`

Partition recommendation:
- partition by `ticker`

### `adjusted_prices_daily`

Layer:
- interim

Required columns:
- all `prices_daily` core columns
- `adjustment_source`

Important rule:
- keep raw and adjusted prices separate,
- do not overwrite raw normalized price history.

### `news_articles`

Layer:
- interim

Required columns:
- `article_id`
- `ticker`
- `published_ts_utc`
- `headline`
- `source`
- `url`
- `provider_id`
- `provider`

Optional columns:
- `summary`
- `image`
- `category`
- `related`
- `ingest_ts`

Uniqueness:
- unique on `(ticker, article_id)`

### `split_events`

Layer:
- interim

Required columns:
- `ticker`
- `split_date`
- `split_factor`
- `source`
- `ingest_ts`

Uniqueness:
- unique on `(ticker, split_date)`

### `article_embeddings`

Layer:
- embeddings

Required columns:
- `article_id`
- `model_id`
- `embedding_dim`
- `embedding`
- `text_hash`
- `embed_ts`

Uniqueness:
- unique on `(article_id, model_id)`

Partition recommendation:
- partition by `model_id`

### `event_states_daily`

Layer:
- final

Required columns:
- `ticker`
- `date`
- `state_vector`
- `news_count`
- `lookback_days`
- `decay_half_life_days`

Optional columns:
- `novelty`
- `conflict`
- `density`

Uniqueness:
- unique on `(ticker, date)`

### `company_kb`

Layer:
- kb/interim depending on workflow stage

Required columns:
- `ticker`
- `cik`
- `name_current`
- `former_names`
- `exchanges`
- `sic`
- `sic_description`
- `business_address`
- `mailing_address`
- `effective_date`
- `source`

Uniqueness:
- unique on `(ticker, effective_date)`

### `labels_multi_horizon`

Layer:
- final

Required columns:
- `ticker`
- `date`
- `y_excess_ret_1`
- `y_excess_ret_5`
- `y_excess_ret_20`
- `y_excess_ret_60`

Optional columns:
- raw forward returns,
- direction labels,
- downside labels.

Important note:
- horizon-specific columns may be nullable near series endpoints.

### `modeling_panel`

Layer:
- final

Required columns:
- `ticker`
- `date`
- `split_adjusted_prices_used`
- `dataset_version`

Optional columns:
- version markers for market, event-state, company, and label branches,
- many additional feature columns.

Important rule:
- this table intentionally allows many additional derived feature columns,
- but it must remain unique on `(ticker, date)`.

## Naming conventions

- Use `snake_case` for table names and file names.
- Use provider-specific raw subdirectories.
- Use canonical table names in manifests and logs.
- Prefer one logical table per file family.
- Preserve a stable distinction between raw and adjusted price history.

## Partitioning strategy

Recommended defaults:
- price-like tables: by `ticker`
- news articles: by `ticker` and optionally time buckets once scale requires it
- embeddings: by `model_id`
- final modeling panels: by date or date buckets if cross-sectional reads dominate

Partitioning should be revisited once actual data scale is measured.

## File format recommendations

- Use Parquet for canonical interim and final tables.
- Use JSON for raw API payloads and manifests where human readability matters.
- Use Arrow-compatible storage and schema handling when possible.

## Processing engine roles

- `pandas`
  - small to medium transformations,
  - fast prototyping,
  - compatibility-heavy workflows.

- `polars`
  - scalable lazy transformations,
  - efficient columnar scans,
  - larger-than-memory style processing when needed.

- `duckdb`
  - large joins,
  - filtered reads over Parquet,
  - final panel assembly without loading everything into memory.

- `pyarrow`
  - schema and Parquet interoperability,
  - explicit columnar storage support.

## Incremental update rules

### Market data
- backfill once,
- then request only missing date windows,
- write every request to a ledger,
- keep repair workflows explicit rather than silently rewriting history.

### News data
- ingest by stable date chunks,
- preserve raw payloads,
- normalize and deduplicate deterministically,
- use text hashing to support incremental embedding rebuilds.

### Knowledge base data
- preserve SEC source metadata,
- update only through explicit refresh workflows,
- record effective dates where possible.

## Validation policy

- validate schemas before writing downstream outputs,
- reject malformed intermediate tables early,
- validate uniqueness where declared,
- require manifests for versioned final datasets.

## Current implementation note

The first executable schema source now exists in `src/data/data_contracts.py`.
As more pipeline stages become real, this document should be updated to stay in sync with the contracts and actual storage behavior.
