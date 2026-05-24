# Data Directory

This directory holds the project's dataset layers and dataset manifests.

## Current layer policy

The project preserves a strict separation between:
- raw source preservation,
- deterministic intermediate transformations,
- final model-ready datasets,
- embedding caches,
- company knowledge-base data,
- dataset manifests.

## Canonical layer overview

- `data/raw/`
  - immutable provider payloads and request ledgers
- `data/interim/`
  - normalized source tables such as prices, news, splits, and adjusted prices
- `data/final/`
  - final labels, event states, and merged modeling panels
- `data/embeddings/`
  - offline article embedding caches
- `data/kb/`
  - company identity and metadata tables
- `data/manifests/`
  - dataset version manifests and coverage summaries

The detailed schema source of truth is `src/data/data_contracts.py`.
The prose storage guide is `docs/data_layout.md`.
