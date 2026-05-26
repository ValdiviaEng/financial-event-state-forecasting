# v1p0 Stage 10 Prompt: Initial Diagnostics Core

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `ExecutionFlow.md`.

## Purpose

Create the initial diagnostics core for v1p0 first-slice candidates.

## Objectives

- Compute fold/horizon metrics from saved predictions.
- Compute train-gap diagnostics only where train predictions exist.
- Report fold dispersion and candidate limitations.

## Inputs

- Validated predictions from Stage 09.
- Labels, splits, and manifests.

## Outputs

- Diagnostic tables.
- Diagnostic manifest.
- Tests under `tests/evaluation/`.

## Smoke Tests

- Tiny prediction sample diagnostic computation.
- Missing train-prediction behavior check.

## Completion Criteria

- Diagnostics link back to source predictions.
- Tests pass.
- Documentation and memory updated.

## Non-Claims

Diagnostics do not promote candidates by themselves.
