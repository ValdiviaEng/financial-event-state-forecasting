# v1p0 Stage 36 Prompt: Accuracy And Overfit Frontier Report

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Summarize how accuracy changes as model/search complexity increases, identify the practical boundary where true overfitting begins, and explicitly account for missing or user-deferred candidate branches.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for non-claim policy, uncertainty-as-diagnostic framing, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for aggressive-but-controlled optimization, TSMixer strategy, ensemble policy, and fusion sequencing.
- Read Stage 22 XGBoost search ledger, Stage 32 TSMixer optimization ledger if completed, Stage 35 diagnostic battery, and `BenchmarkingStrategy.md`.
- If overfit frontier inputs or candidate roster status are incomplete, ask the user before producing a full frontier report.

## Required Inputs

- Stage 35 diagnostic classifications and candidate roster.
- Stage 22 trial ledger and Stage 24 XGBoost overfit review.
- Stage 31/32 TSMixer evidence or explicit user-approved blocked/deferred status.
- Stage 33 ensemble evidence and Stage 34 fusion evidence where completed.

## Methodology

- Compile train, validation, and final metrics by trial, candidate, horizon, fold, split role, and complexity proxy.
- Identify regions where training performance improves while validation/final performance decreases, destabilizes, or depends on a narrow horizon.
- Compare fixed, tuned, neural, ensemble, and fusion candidates only where evidence exists.
- Record training time, inference time, hyperparameter count, parameter count, compute notes, and failure modes.
- Recommend stop, simplify, regularize, rerun, block, or pass-to-claim-review actions for each candidate.

## Required Outputs

- Accuracy/overfit frontier tables and manifest.
- Candidate action table with conservative recommendations.
- Report explicitly listing completed, blocked, and user-deferred branches.

## Success Measurements

- Frontier data is traceable to saved predictions, trial ledgers, and Stage 35 diagnostics.
- Complexity metrics and overfit classifications are defined for every included candidate.
- Missing Stage 31-33 evidence cannot be mistaken for completed neural/ensemble evidence.
- Recommendations are bounded by uncertainty and overfit findings.

## Blocking And User Questions

- Block and ask if Stage 35 is incomplete, if candidate roster status is unresolved, if complexity metrics are missing, or if overfit classification rules are ambiguous.
- Block and ask before excluding branches, changing overfit thresholds, recommending promotion for incomplete evidence, or continuing to Stage 39 with unresolved frontier gaps.
- Do not infer that missing TSMixer/ensemble evidence is unimportant; ask or mark it as user-resolved partial scope.

## Cascade Handling

- Stage 36 recommendations feed Stage 37 report wording and Stage 39 claim review.
- Any Stage 36 rerun or candidate-roster change invalidates downstream final-report and claim-review language.
- If Stage 36 is partial, Stage 39 and Stage 40 must preserve partial/frontier limitation wording.

## Required Tests And Validation

- Frontier table schema tests.
- Overfit classification and candidate action consistency tests.
- Runtime/complexity aggregation tests.
- Missing-branch status tests.
- Source-table fidelity checks.

## Completion Criteria

- Accuracy optimization is bounded by explicit overfit evidence and branch-completeness status, not intuition or silent omission.

## Non-Claims

This report informs claim review but does not make final claims, approve comparability promotion, reinterpret Stage 6, or support trading outputs.
