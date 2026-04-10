# Artifacts Directory

This directory should eventually contain durable outputs produced by training
and evaluation jobs.

Examples of future contents:
- model checkpoints,
- fitted scalers,
- calibration objects,
- figures and tables,
- exported evaluation summaries.

Rules for later implementation:
- artifacts should be tied to run identifiers,
- generated files should be reproducible from saved configs and manifests.

## Current implementation note

The repository now writes real artifacts through the training and evaluation stack.

Currently implemented artifact families include:
- baseline checkpoints
- multimodal checkpoints
- prediction tables
- metric files
- run metadata files
- evaluation outputs written under report-oriented directories

Artifacts should continue to be tied to run IDs and frozen dataset versions.
