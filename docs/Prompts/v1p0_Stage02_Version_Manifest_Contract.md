# v1p0 Stage 02 Prompt: v1p0 Version Manifest Contract

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `ExecutionFlow.md`.

## Purpose

Define v1p0 benchmark-family and component version identity.

## Objectives

- Create or plan `configs/v1p0_version_manifest.yaml`.
- Define benchmark-family ID, component IDs, source-artifact fields, and non-relabeling checks.
- Add a smoke validator or test if implementation is approved in this stage.

## Inputs

- v1p0 naming decision.
- First-slice component list.

## Outputs

- Version manifest config/design.
- Version schema expectations.
- Smoke test or placeholder if code is not yet approved.

## Smoke Tests

- Config parse test.
- Check that v0p9 artifacts are not labeled as v1p0 outputs.

## Completion Criteria

- Version naming is explicit.
- Downstream stages can reference stable IDs.
- Docs and memory updated.

## Non-Claims

This stage creates identity contracts only; it does not create model evidence.
