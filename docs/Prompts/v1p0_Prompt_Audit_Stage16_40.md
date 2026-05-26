# v1p0 Stage 16-40 Prompt Audit

Status: prompt-repair audit; documentation artifact only.

## Purpose

This audit records the prompt-governance repair for v1p0 Stage 16 through Stage 40 after the Stage 31 through Stage 33 TSMixer/ensemble branch was silently deferred during execution. The repair strengthens prompts so future execution must stop, ask, and resolve blockers instead of silently skipping critical work.

## Audit Scope

- Audited prompt files: `docs/Prompts/v1p0_Stage16_*.md` through `docs/Prompts/v1p0_Stage40_*.md`.
- Core truth sources checked: `ArchitecturalDesignDecisions.md` and `docs/NextSteps_Brainstorming.md`.
- Supporting truth sources checked: `ResearchTruth.md`, `BenchmarkingStrategy.md`, `LearningStrategy.md`, `VisualizationStrategy.md`, and result-vault conventions.

## Root Issue

- The earlier prompts were too small and task-list oriented.
- They did not consistently require explicit blocker escalation when prerequisites were missing.
- They did not consistently explain cascade effects from earlier-stage changes.
- Stage 30 allowed smoke-only evidence to exist without sufficiently forcing Stage 31 fixed multiseed execution or a user-approved deferral.
- Stage 31 through Stage 33 were therefore vulnerable to agent-selected deferral even though `docs/NextSteps_Brainstorming.md` selected standalone TSMixer, then optimization if justified, then XGBoost+TSMixer horizon meta exploration after standalone evidence.

## Repair Applied

- Each Stage 16 through Stage 40 prompt now includes explicit objective, core truth sources, required inputs, methodology, required outputs, success measurements, blocking/user-question rules, cascade handling, tests, completion criteria, and non-claims.
- Each prompt requires `ArchitecturalDesignDecisions.md` and `docs/NextSteps_Brainstorming.md` to be used for durable decision resolution where relevant.
- Each prompt requires asking the user when a decision is missing from the truth files or when continuing would change scope, evidence, benchmark comparability, or downstream validity.
- Stage 18 now states sequence-window materialization is a hard prerequisite for Stage 30 through Stage 33, unless the user explicitly resolves a block/defer decision.
- Stage 30 now forbids substituting tabular data for Stage 18 sequence tensors and states smoke evidence is not Stage 31 evidence.
- Stage 31 now states silent deferral is not valid and requires user resolution before downstream continuation.
- Stage 32 now requires an explicit user approval gate after Stage 31 evidence before optimization.
- Stage 33 now requires standalone XGBoost and TSMixer evidence or an explicit user-resolved defer/block decision before downstream completion.
- Stage 34 through Stage 40 now require missing Stage 31 through Stage 33 status to remain visible and user-approved rather than hidden inside partial completion.

## Success Criteria For Future Prompt Execution

- A stage can complete only when its required artifacts, decisions, outputs, and validations exist, or when the user explicitly resolves a blocker.
- A downstream stage can continue after an upstream blocker only if the user explicitly approves a partial/narrower path and the later reports preserve that limitation.
- A critical branch cannot be marked deferred by the executor alone.
- Positive benchmark language, benchmark-comparability promotion, Stage 6 reinterpretation, live provider calls, raw mutation, service/API/dashboard scope, and trading outputs remain approval-gated.

## Validation Targets

- Prompt files should include the required structural headings.
- Governance validation should pass.
- Ledger JSONL parse should pass after memory updates.
- `git diff --check` should report no whitespace errors.

## Non-Claims

This audit fixes prompt instructions only. It does not execute Stage 31 through Stage 33, create TSMixer benchmark evidence, approve a positive benchmark claim, or change the Stage 39 non-claim conclusion.
