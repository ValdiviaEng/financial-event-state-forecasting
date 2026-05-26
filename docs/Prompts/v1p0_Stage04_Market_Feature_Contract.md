# v1p0 Stage 04 Prompt: Market Lag/Rolling Feature Contract

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `ExecutionFlow.md`.

## Purpose

Define the lag/rolling market feature sidecar contract before implementation.

## Objectives

- Specify lag windows, rolling windows, minimum periods, null policy, and column naming.
- Define row identity and source-provenance columns.
- Define no-lookahead checks.

## Inputs

- Stage 03 feature registry.
- Existing market/data artifact contracts.

## Outputs

- `configs/market_features_v1p0.yaml` or design equivalent.
- Feature contract and toy-data test expectations.

## Smoke Tests

- Toy-data lag/rolling no-lookahead test.
- Null/minimum-period behavior check.

## Completion Criteria

- Feature contract is specific enough to implement.
- Leakage and row identity rules are explicit.

## Non-Claims

This stage does not write production feature sidecars.
