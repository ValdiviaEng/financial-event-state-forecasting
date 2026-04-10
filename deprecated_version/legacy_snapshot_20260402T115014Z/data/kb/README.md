# Company Knowledge Base Layer

This directory stores company identity and profile data.

## Canonical tables expected here

- `company_kb`
- `company_ticker_mappings`
- `company_aliases`

## Rules

- separate static identity data from time-varying descriptive fields,
- document the effective date of any profile information,
- keep ticker/CIK mappings auditable and source-aware.

## Current implementation note

The Stage 7 company-KB pipeline is designed to write:
- `company_kb.parquet`
- `company_ticker_mappings.parquet`
- `company_aliases.parquet`
- a KB quality report
- a KB manifest

This phase remains static-metadata-only by design.
