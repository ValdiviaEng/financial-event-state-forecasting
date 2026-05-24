# Data Manifests Layer

This directory stores machine-readable summaries of dataset versions used by the project.

## Required manifest fields

- `manifest_version`
- `dataset_name`
- `dataset_version`
- `schema_version`
- `created_at_utc`
- `source_tables`

## Recommended additional fields

- dataset hashes,
- source coverage statistics,
- build timestamps,
- upstream dependency references,
- quality flags.

## Rules

- every final training run should reference one manifest,
- manifests should make reruns auditable,
- manifest schema should stay aligned with `src/data/data_contracts.py`.

## Current implementation note

The Stage 10 modeling-dataset builder now writes a manifest per final panel build.

The current modeling-panel manifest includes:
- dataset identity fields,
- schema version,
- source table list,
- summary coverage for:
  - market features,
  - labels,
  - optional event states,
  - final row and column counts.
