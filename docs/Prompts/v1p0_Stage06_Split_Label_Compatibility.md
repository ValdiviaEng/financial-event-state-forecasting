# v1p0 Stage 06 Prompt: Split And Label Compatibility Adapter

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `ExecutionFlow.md`.

## Purpose

Verify v1p0 features align with labels, horizons, folds, and lockbox roles.

## Objectives

- Join feature sidecars to labels and split assignments.
- Validate row keys, horizons, fold IDs, row roles, and label availability.
- Record blockers before model training.

## Inputs

- Stage 05 feature sidecars.
- Existing or planned label/split artifacts.

## Outputs

- Compatibility validation report.
- Tests under `tests/split/`, `tests/benchmark/`, or equivalent.

## Smoke Tests

- Sample join row-count check.
- Missing/duplicate key check.
- Horizon/fold role check.

## Completion Criteria

- No row-universe drift or leakage blocker remains hidden.
- Model stages have validated aligned inputs.

## Non-Claims

This stage does not train models or evaluate performance.
