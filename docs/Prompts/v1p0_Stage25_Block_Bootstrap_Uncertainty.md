# v1p0 Stage 25 Prompt: Block Bootstrap Uncertainty

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Implement and run block-bootstrap uncertainty evidence required before any final promotion beyond first-slice/date-clustered evidence, while preserving overfit-control and non-claim boundaries.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for uncertainty-as-diagnostic policy, non-claim boundaries, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` Decision 25 for the selected uncertainty suite.
- Read `BenchmarkingStrategy.md` Section 6, Stage 23 final predictions, and Stage 24 overfit review.
- If block unit, block length, resample count, or interpretation threshold is unclear, ask the user before running.

## Required Inputs

- Candidate and hurdle saved-prediction packets from Stages 19 and 23.
- Stage 24 candidate classification and overfit-frontier evidence.
- Split-role, horizon, fold, ticker, and as-of-date metadata needed for dependence-aware resampling.
- Metric definitions and primary-delta policy from `BenchmarkingStrategy.md`.

## Methodology

- Define block unit, block length, resample count, random seed, horizon handling, and small-sample fallback before computation.
- Compute uncertainty intervals for primary deltas and relevant metrics using moving/date blocks appropriate for temporal dependence.
- Compare block-bootstrap evidence with date-clustered intervals and record disagreements.
- Compute train-to-real-data generalization gaps where train predictions are available.
- Record runtime, seed, sample counts, failures, and limitations.

## Required Outputs

- Paired loss table, block-bootstrap interval table, date-clustered interval table, method-comparison table, and generalization-gap table.
- Uncertainty manifest with parameters, sample counts, seeds, runtime, and classification.
- Report explaining whether uncertainty supports, weakens, or blocks later claim review.

## Success Measurements

- Bootstrap output is deterministic for the recorded seed.
- Intervals cover all required horizons, split roles, metrics, and candidate/hurdle pairs or document blockers.
- Weak, unstable, or contradictory intervals are carried forward as blockers or limitations.
- The method does not create improvement where point estimates or intervals do not support it.

## Blocking And User Questions

- Block and ask if sample size is inadequate, block policy is ambiguous, Stage 24 overfit classification is unresolved, or interval output is incomplete.
- Block and ask before changing bootstrap method, reducing horizons, lowering resample counts materially, or interpreting weak intervals as positive evidence.
- Do not proceed to positive Stage 39 language when uncertainty evidence is weak or unstable.

## Cascade Handling

- Stage 25 uncertainty classifications feed Stage 35 diagnostics, Stage 36 frontier reporting, and Stage 39 claim review.
- Any Stage 25 rerun or method change invalidates downstream uncertainty references.
- If Stage 25 is blocked, Stage 39 cannot approve positive benchmark language.

## Required Tests And Validation

- Bootstrap determinism tests.
- Block-boundary and no-future-leakage tests.
- Interval monotonicity and coverage sanity tests.
- Small-sample fallback tests.
- Manifest/source-table consistency tests.

## Completion Criteria

- Bootstrap method, parameters, sample counts, limitations, and interpretation are recorded and reproducible.
- Promotion remains blocked if uncertainty evidence is weak, unstable, or overfit-contaminated.

## Non-Claims

Uncertainty intervals describe evidence strength; they do not create model improvement, positive claims, Stage 6 reinterpretation, or trading value.
