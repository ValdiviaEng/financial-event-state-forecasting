# v1p0 Stage 32 Prompt: TSMixer Optimization And Overfit Control

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Optimize TSMixer only after Stage 31 standalone multiseed evidence exists and the user approves optimization based on that evidence. This stage must track the true overfit frontier and cannot be auto-deferred or auto-executed without the Stage 31 decision point.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for TSMixer strategy, approval gates, and non-claim boundaries.
- Read `docs/NextSteps_Brainstorming.md` Decision 32 for standalone-then-optimize sequencing and the rationale against premature nested optimization.
- Read Stage 31 multiseed evidence, `BenchmarkingStrategy.md`, and `LearningStrategy.md`.
- If Stage 31 evidence is absent or ambiguous, ask the user whether to run Stage 31, defer TSMixer, or stop the branch; do not infer the answer.

## Required Inputs

- Complete Stage 31 fixed multiseed benchmark evidence and classification.
- User approval to optimize, captured after reviewing Stage 31 evidence.
- Proposed TSMixer search space, objective, budget, seeds, early-stop policy, and regularization controls.
- Development-only folds and Stage 18 tensors.

## Methodology

- Ask whether TSMixer optimization is approved based on Stage 31 evidence before defining or running search.
- Define search space, budget, objective, early stopping, regularization, failure handling, and overfit flags.
- Run nested development-only optimization if approved; never use lockbox feedback for search.
- Record every trial with hyperparameters, train/validation metrics, runtime, memory, parameter count, seed, failure reason, and overfit flags.
- Stop, narrow, or block search when validation performance degrades while train performance improves, but ask the user before changing the approved search contract.

## Required Outputs

- Optimization approval record or user-approved block/defer record.
- Search-space manifest, trial ledger, fold metrics, overfit frontier, best candidate/rejection manifest, and runtime report.
- Clear recommendation for Stage 33/35: freeze tuned TSMixer, reject tuned TSMixer, or keep only Stage 31 fixed TSMixer.

## Success Measurements

- Optimization was explicitly approved after Stage 31 evidence.
- Lockbox rows used during optimization equal zero.
- Trial ledger is complete and recomputable.
- Overfit flags are explicit and conservative.
- Tuned candidate is frozen or rejected from development evidence only.

## Blocking And User Questions

- Block and ask if Stage 31 evidence is missing, Stage 31 evidence is not promising, optimization approval is absent, search budget is unclear, tensor inputs changed, lockbox leakage is detected, or trial ledger is incomplete.
- Block and ask before deferring Stage 32, changing search space, reducing budget, changing objective, or carrying a tuned candidate forward.
- The agent must not continue to Stage 33 as if optimization was considered unless the user explicitly resolves Stage 32.

## Cascade Handling

- Stage 32 tuned or rejected status controls the TSMixer input available to Stage 33 ensemble and Stage 35 diagnostics.
- Any Stage 32 rerun invalidates Stage 33 ensemble, Stage 35 diagnostics, Stage 36 frontier, and Stage 39 claim-review references to TSMixer optimization.
- If Stage 32 is blocked or user-deferred, Stage 33 may use Stage 31 fixed TSMixer only if the user explicitly approves that path.

## Required Tests And Validation

- Search-space serialization and digest tests.
- Trial-ledger schema and objective-recomputation tests.
- Overfit flag and early-stop tests.
- No-lockbox-access tests.
- User-approval evidence check.

## Completion Criteria

- Tuned TSMixer is frozen, rejected, or user-deferred with explicit approval and downstream effects recorded.
- Silent deferral is not a valid completion state.

## Non-Claims

Optimization search results are not final claims, Stage 6 reinterpretation, comparability promotion, or trading output.
