# v1p0 Stage 08 Prompt: Fixed XGBoost Baseline

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `ExecutionFlow.md`.

## Purpose

Implement `market_xgboost_v1_fixed` as the honest stronger market hurdle.

## Objectives

- Add fixed XGBoost model config and dependency notes.
- Avoid Optuna or lockbox-guided tuning.
- Save predictions with the same schema as Stage 07.
- Add dependency-aware smoke tests.

## Inputs

- Stage 06 compatible features, labels, and splits.
- Stage 07 prediction schema precedent.

## Outputs

- Fixed XGBoost saved predictions.
- Fit/preprocessing records.
- Tests under `tests/models/`.

## Smoke Tests

- Tiny/sample XGBoost fit if dependency exists.
- If dependency is absent, mark blocked with remediation instead of claiming completion.
- Prediction schema check.

## Completion Criteria

- Fixed parameters and seeds are recorded.
- No tuning path is silently introduced.
- Tests pass or dependency blocker is explicit.

## Non-Claims

This stage does not implement nested Optuna or final candidate promotion.
