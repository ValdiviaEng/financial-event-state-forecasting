# v1p0 Stage 05 Prompt: Market Feature Sidecar Builder

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `ExecutionFlow.md`.

## Purpose

Implement the versioned market lag/rolling feature sidecar builder.

## Objectives

- Build sidecar features without mutating v0p9 artifacts.
- Write feature artifacts and manifests under v1p0 paths.
- Add focused feature tests.

## Inputs

- Stage 04 feature contract.
- Market panel/data inputs.
- Feature registry and version manifest.

## Outputs

- v1p0 market feature sidecar artifact or smoke artifact.
- Feature manifest.
- Tests under `tests/features/`.

## Smoke Tests

- Build tiny sample.
- Verify row identity, no future usage, schema, and manifest provenance.

## Completion Criteria

- Feature sidecar writes expected schema.
- Tests pass.
- Guidebook, architecture map, and memory are updated.

## Non-Claims

This stage does not train models or make benchmark claims.
