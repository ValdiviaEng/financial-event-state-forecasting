# Reports Directory

This directory should eventually contain thesis-ready and analysis-ready outputs.

Examples of future contents:
- result tables,
- figures,
- experiment summaries,
- ablation writeups,
- sanity-check reports.

Rules for later implementation:
- report outputs should be generated from saved predictions and metrics rather
  than from ad hoc notebook state whenever possible.

## Current implementation note

Stage 14 evaluation helpers now write report-style machine-readable outputs such as:
- `evaluation_summary.json`
- `regression_metrics.parquet`
- `ranking_metrics.parquet`
- `ablation_summary.json`
- `ablation_summary.parquet`

These outputs are intended to be the source for later thesis-ready figures and tables.
