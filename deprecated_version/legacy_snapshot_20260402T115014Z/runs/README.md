# Runs Directory

This directory should eventually contain run-specific execution outputs.

Examples of future contents:
- resolved configs,
- logs,
- predictions,
- per-fold metrics,
- environment snapshots,
- links to datasets and artifacts used by the run.

Rules for later implementation:
- each run should have a unique identifier,
- reruns should not overwrite old results silently.

## Current implementation note

The Stage 12 baseline-training CLI now writes run-specific outputs under `runs/<run_id>/`.

Current run contents include:
- checkpoints
- predictions
- metrics
- run metadata
- baseline training summary

Stage 13 extends the same run structure for multimodal training with:
- multimodal checkpoints
- multimodal prediction tables
- multimodal metric files
- multimodal training summary
