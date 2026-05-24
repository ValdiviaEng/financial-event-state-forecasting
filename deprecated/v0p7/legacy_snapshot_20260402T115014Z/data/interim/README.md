# Interim Data Layer

This directory stores normalized, validated tables derived from raw inputs.

## Canonical tables expected here

- `prices_daily`
- `adjusted_prices_daily`
- `news_articles`
- `split_events`
- `company_kb`

## Rules

- schemas must be stable and validated against `src/data/data_contracts.py`,
- transformations must be deterministic,
- validation diagnostics should be written alongside outputs when possible,
- raw and adjusted price histories must remain distinct.

## Current implementation note

The Stage 4 market pipeline is designed to write:
- canonical per-ticker `prices_daily` parquet outputs
- per-ticker market quality reports alongside interim prices

Stage 5 now adds a separate adjusted-price branch:
- `adjusted_prices_daily`
- per-ticker split-adjustment diagnostics

The repository now also includes a dedicated split-event build path that writes:
- `split_events.parquet`
- split-event quality reports
- split-event manifests

Stage 6 now adds a news branch:
- canonical per-ticker `news_articles` parquet outputs
- per-ticker news quality reports alongside interim article tables

Raw and adjusted histories remain separate by design.
