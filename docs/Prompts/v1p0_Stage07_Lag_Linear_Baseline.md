# v1p0 Stage 07 Prompt: Lag-Linear Baseline

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `ExecutionFlow.md`.

## Purpose

Implement `market_lag_linear_v1` as the first temporal sanity baseline.

## Objectives

- Add fixed model config.
- Fit with fold-local preprocessing.
- Save predictions with schema/provenance.
- Add focused tests.

## Inputs

- Stage 06 compatible features, labels, and splits.
- v1p0 model config.

## Outputs

- Saved predictions.
- Fit and preprocessing records.
- Tests under `tests/models/`.

## Smoke Tests

- Tiny fold training.
- Saved-prediction schema check.
- Fold-local preprocessing check.

## Completion Criteria

- `market_lag_linear_v1` predictions exist or smoke artifacts exist as scoped.
- Tests pass.
- Docs and memory updated.

## Non-Claims

This stage does not prove model improvement or support trading claims.
