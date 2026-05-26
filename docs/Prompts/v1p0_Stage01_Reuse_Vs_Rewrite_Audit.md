# v1p0 Stage 01 Prompt: v0p9 Reuse Versus Rewrite Audit

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `ExecutionFlow.md`.

## Purpose

Decide which old code should be reused, rewritten, or treated as reference-only before v1p0 code is generated.

## Objectives

- Inspect candidate code under `deprecated/v0p9/src/` or current v0p9 source if present.
- Compare reuse vs rewrite for versioning, feature registry, market features, models, diagnostics, and reporting.
- Define compatibility tests for any reused code.

## Inputs

- `deprecated/v0p9/src/`.
- v1p0 architecture and strategy docs.

## Outputs

- Reuse audit record identifying `reuse`, `rewrite`, or `reference-only` per component.
- Compatibility-test requirements for any reuse.

## Smoke Tests

- No execution required by default.
- If import feasibility is tested, use a small isolated import check and do not claim implementation.

## Completion Criteria

- No old code is reused without a compatibility-test plan.
- Unknown imports/dependencies are recorded as blockers.
- Memory is updated if the audit changes implementation planning.

## Non-Claims

This stage does not move code, implement v1p0 behavior, or validate old code as v1p0-compatible by itself.
