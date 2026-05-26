# v1p0 Stage 12 Prompt: First Uncertainty Evidence

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `ExecutionFlow.md`.

## Purpose

Add date-clustered confidence intervals as first uncertainty evidence.

## Objectives

- Implement or plan date-clustered CI tables.
- Record method metadata and limitations.
- Keep block bootstrap as later promotion requirement.

## Inputs

- Stage 10/11 metric inputs grouped by date, fold, horizon, and model.

## Outputs

- CI tables.
- Method metadata manifest.
- Tests under `tests/evaluation/`.

## Smoke Tests

- Deterministic toy CI output.
- Missing/low-sample behavior check.

## Completion Criteria

- CI outputs are reproducible and caveated.
- Tests pass.

## Non-Claims

First uncertainty evidence is not final promotion evidence; block bootstrap remains later requirement.
