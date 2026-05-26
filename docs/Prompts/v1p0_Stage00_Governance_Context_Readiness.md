# v1p0 Stage 00 Prompt: Governance And Context Readiness

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Required Background

Read: `AgentRules.md`, `docs/agent/AgentMemory.md`, `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `LearningStrategy.md`, `BenchmarkingStrategy.md`, `VisualizationStrategy.md`, `ExecutionFlow.md`.

## Purpose

Confirm that v1p0 first-slice work starts from valid governance, memory, and planning context.

## Objectives

- Recover current task contract and active v1p0 scope.
- Confirm no live provider, raw overwrite, Stage 6 reinterpretation, service/API/dashboard, or trading-output approval gate is triggered.
- Validate governance and event ledger before implementation planning proceeds.

## Inputs

- Active root planning docs.
- `docs/agent/agent_log/Current_State.md`.
- `docs/agent/agent_log/Event_Ledger.ndjson`.

## Outputs

- Readiness summary in memory or task notes.
- Any blocker or stale-risk event if found.

## Smoke Tests

- `python scripts/validate_agent_governance.py`
- Event ledger JSONL parse.

## Completion Criteria

- Required v1p0 planning docs exist.
- Validation passes or blockers are logged.
- Next stage remains within approved v1p0 first-slice scope.

## Non-Claims

This stage does not implement code, create artifacts, run benchmarks, or approve broader modeling.
