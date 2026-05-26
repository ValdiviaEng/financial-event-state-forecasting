# v1p0 Stage 22 Prompt: XGBoost Nested Random And Optuna Search

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Execute the approved nested XGBoost hyperparameter search inside development data only, recording complete trial evidence for accuracy, runtime, failure modes, and overfitting without lockbox feedback.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for approval gates, v1p0 candidate boundaries, non-claim policy, and comparability restrictions.
- Read `docs/NextSteps_Brainstorming.md` for the selected nested Optuna path and aggressive overfit-control requirement.
- Read Stage 21 frozen search-space/objective config and `BenchmarkingStrategy.md` before starting trials.
- If Stage 21 and the truth files disagree, stop and ask the user before running or resuming search.

## Required Inputs

- Stage 21 frozen search-space and objective configs with digests.
- Stage 17 feature sidecars and Stage 19 baseline predictions.
- Development-only folds from Stage 4.
- XGBoost/Optuna runtime dependencies and approved compute budget.

## Methodology

- Run Phase 1 random trials, Phase 2 Optuna TPE trials, and Phase 3 local refinement only within the frozen Stage 21 budget.
- Use purged/nested temporal development folds and never inspect lockbox performance during search.
- Save every trial's hyperparameters, objective components, fold metrics, train metrics, validation metrics, predictions or prediction references, runtime, memory notes, failure reason, and seed.
- Track overfit frontier signals during search without changing the frozen objective unless the user explicitly approves a new Stage 21 freeze.
- Select the best candidate only from development evidence and freeze it for Stage 23.

## Required Outputs

- Trial ledger with one row per attempted trial and explicit status.
- Fold metrics, score components, prediction index, failure ledger, and best-candidate manifest.
- Result-vault report explaining budget use, failed trials, overfit signals, and final frozen candidate selection.

## Success Measurements

- Every budgeted trial is completed, failed with a recorded reason, or user-approved as stopped early.
- Best-candidate selection is reproducible from the trial ledger.
- Lockbox rows used during search equal zero.
- Failed or interrupted trials do not silently disappear from the ledger.

## Blocking And User Questions

- Block and ask if Stage 21 config is missing, lockbox leakage is detected, dependencies fail, budget cannot complete, resume state is inconsistent, or trial outputs are incomplete.
- Block and ask before changing budget, search space, objective, sampler, early-stop criteria, or candidate selection rule.
- Do not proceed to Stage 23 with a partially searched or non-reproducible candidate unless the user explicitly approves a blocked/limited path.

## Cascade Handling

- Stage 22 best-candidate digest feeds Stage 23 final evaluation and Stage 24 overfit review.
- Any Stage 22 rerun or search-space change invalidates downstream frozen-final and uncertainty artifacts.
- If Stage 22 is blocked, Stage 23 through Stage 25 and tuned-XGBoost portions of Stage 35 through Stage 40 are blocked.

## Required Tests And Validation

- Trial ledger schema and row-count tests.
- Nested split isolation and lockbox-zero tests.
- Objective recomputation tests from saved trial evidence.
- Interrupted-run resume and failed-trial recording tests.
- Best-candidate reproducibility tests.

## Completion Criteria

- Search ledger is complete and reproducible, with a development-selected candidate frozen for Stage 23 or a user-resolved blocker.

## Non-Claims

Best development-search score is not a final benchmark improvement claim, Stage 6 reinterpretation, comparability promotion, or trading signal.
