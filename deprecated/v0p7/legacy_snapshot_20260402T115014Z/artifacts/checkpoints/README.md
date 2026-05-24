# Checkpoints

This directory should eventually contain saved training checkpoints.

Examples of future contents:
- baseline model checkpoints,
- multimodal model checkpoints,
- best-per-fold snapshots,
- optional last-epoch checkpoints.

Rules for later implementation:
- checkpoint filenames should encode run and fold identity,
- enough metadata should be saved to restore inference cleanly.

## Current implementation note

The Stage 12 baseline-training path now writes model checkpoints here through run-specific subdirectories.

Current checkpoint types:
- sklearn baseline checkpoints as `.joblib`
- optional market MLP checkpoints as `.pt` when the PyTorch path is used
- multimodal event-state checkpoints as `.pt`

Checkpoint filenames currently encode:
- split identity
- baseline model name

Multimodal checkpoints follow the same split-aware naming rule.
