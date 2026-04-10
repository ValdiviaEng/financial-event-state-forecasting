# Tables

This directory should eventually contain machine-generated tables.

Examples of future contents:
- main-results tables,
- ablation tables,
- fold summaries,
- coverage reports,
- dataset statistics.

Rules for later implementation:
- table generation should be reproducible from stored predictions and manifests.

## Current implementation note

Stage 14 evaluation and ablation helpers now write machine-readable comparison
tables such as regression metrics, ranking metrics, and ablation summaries.

These outputs may currently live under report-specific output directories, but
this directory remains the canonical destination for thesis-ready generated tables.
