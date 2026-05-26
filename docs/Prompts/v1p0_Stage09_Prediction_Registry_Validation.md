# v1p0 Stage 09 Prompt: Prediction Packet And Model Registry Validation

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `ExecutionFlow.md`.

## Purpose

Validate saved predictions and registry links before diagnostics consume them.

## Objectives

- Check model IDs, horizons, folds, row roles, and provenance.
- Validate prediction schema consistency across `market_lag_linear_v1` and `market_xgboost_v1_fixed`.
- Verify registry and version manifest links.

## Inputs

- Stage 07 and Stage 08 predictions.
- Feature registry and version manifest.

## Outputs

- Prediction validation summary.
- Tests or validator script.

## Smoke Tests

- Schema check.
- Row-count/key check.
- Registry link check.

## Completion Criteria

- Prediction artifacts are safe inputs for diagnostics.
- No hidden provenance gaps remain.

## Non-Claims

This stage validates shape/provenance, not model quality.
