# v1p0 Stage 03 Prompt: Sidecar Feature Registry Contract

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `ExecutionFlow.md`.

## Purpose

Define how v1p0 feature sidecars map to model variants.

## Objectives

- Create or plan `configs/feature_registry_v1p0.yaml`.
- Define registry fields: feature family, artifact path, source version, model consumer, row key, and limitations.
- Ensure registry supports `market_lag_linear_v1` and `market_xgboost_v1_fixed`.

## Inputs

- Stage 02 version manifest.
- First-slice model list.

## Outputs

- Feature registry contract/config.
- Registry smoke test or validation plan.

## Smoke Tests

- Registry loads.
- IDs are unique.
- Referenced planned paths are syntactically valid.

## Completion Criteria

- Each first-slice model has explicit feature dependencies.
- No silent mutation of old Stage 3 artifacts is implied.

## Non-Claims

This stage does not build features or train models.
