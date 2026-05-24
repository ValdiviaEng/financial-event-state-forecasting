# Raw Data Layer

This directory stores immutable provider outputs and request ledgers.

## Intended raw subdirectories

- `data/raw/twelvedata/`
  - raw `time_series` payloads
  - market request ledgers
- `data/raw/finnhub/`
  - raw company-news payloads
  - news request ledgers
- `data/raw/sec/`
  - raw SEC submissions payloads or bulk snapshots
- `data/raw/split_events/`
  - raw split-event payloads by provider
  - split-event request ledgers
- `data/raw/universe/`
  - frozen universe snapshot files

## Rules

- do not edit raw payloads in place,
- write explicit request ledgers,
- preserve enough metadata to rebuild interim tables deterministically,
- keep raw outputs separate from normalized tables.

## Current implementation note

The Stage 4 market pipeline is designed to write:
- raw Twelve Data payloads under `data/raw/twelvedata/<ticker>/`
- a raw market request ledger under the Twelve Data raw layer

The Stage 6 news pipeline is designed to write:
- raw Finnhub payloads under `data/raw/finnhub/<ticker>/`
- a raw news request ledger under the Finnhub raw layer

The exact paths are controlled by:
- `configs/dataset_build.yaml`
- `src/data/price_pipeline.py`
- `src/data/news_pipeline.py`
