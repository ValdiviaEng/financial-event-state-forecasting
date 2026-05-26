# v1p0 Stage 11 Prompt: Stratified Metrics

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `ExecutionFlow.md`.

## Purpose

Report candidate behavior by no-news, news-rich, truncation-risk, and article-count strata.

## Objectives

- Define bucket rules.
- Compute stratum metrics.
- Preserve provider-completeness and truncation caveats.

## Inputs

- Stage 10 diagnostics.
- No-news flags, truncation-risk flags, article counts, predictions, labels.

## Outputs

- Strata metric tables.
- Bucket-definition manifest.
- Tests under `tests/evaluation/`.

## Smoke Tests

- Toy bucket assignment.
- Aggregate consistency check.
- Required caveat presence check.

## Completion Criteria

- Strata outputs are deterministic and documented.
- No provider-completeness claim is made.

## Non-Claims

Stratified metrics are diagnostic evidence, not trading or live forecast outputs.
