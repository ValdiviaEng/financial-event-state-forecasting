# v1p0 Stage 21 Prompt: XGBoost Search Space And Objective Freeze

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Define and freeze the nested XGBoost search space, objective, budgets, and overfit safeguards before any hyperparameter search starts. This stage creates search-contract evidence only.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for v1p0 candidate naming, comparability boundaries, non-claim policy, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` Decisions 14 through 18 for XGBoost, nested Optuna, aggressive-but-controlled overfit policy, hurdle delta, composite guarded objective, horizon weights, and balanced RMSE/MAE.
- Read Stage 20 diagnostics and `BenchmarkingStrategy.md` before freezing any objective.
- If objective components, search budget, stop rules, or overfit penalties are not found in the truth files or Stage 20 evidence, ask the user before freezing.

## Required Inputs

- Stage 20 baseline diagnostic gate output with tuning-readiness classification.
- Stage 19 fixed baseline predictions and metrics.
- `configs/xgboost_search_v1p0.yaml` or proposed search config.
- Runtime/dependency availability for XGBoost and Optuna under the approved environment.

## Methodology

- Define `market_xgboost_v2_nested_optuna_candidate` search-space boundaries before running any trials.
- Define phases: random trials, Optuna TPE trials, local refinement, freeze, and final evaluation.
- Define the guarded hurdle-delta objective using horizon weights `30/25/20/15/10` and balanced RMSE/MAE components.
- Define penalties for one-sided gains, train-validation gap, horizon instability, fold instability, excessive complexity, and failure modes where appropriate.
- Define early-stop, budget-exhaustion, failed-trial, and overfit-frontier criteria.
- Freeze the config digest and objective digest before Stage 22 starts.

## Required Outputs

- Frozen search-space config and objective config with digests.
- Result-vault manifest recording budget, seeds, sampler settings, stop rules, candidate ID, and dependency versions.
- Human-readable freeze report explaining why the objective and budget match the truth files.

## Success Measurements

- Objective recomputes deterministically from input metrics.
- Horizon weights and penalty terms match the approved decision record.
- Search budget is explicit and feasible under the runtime environment.
- Lockbox access is impossible by config and by test.

## Blocking And User Questions

- Block and ask if Stage 20 did not clearly permit tuning, if Optuna/XGBoost availability is missing, if budget is infeasible, or if objective policy is ambiguous.
- Block and ask before changing horizon weights, objective components, trial counts, sampler type, candidate ID, metric policy, or lockbox treatment.
- Do not proceed to Stage 22 with an unfrozen or partially frozen search contract.

## Cascade Handling

- Stage 21 config digests must be carried into Stage 22 trial ledgers and Stage 23 frozen evaluation.
- Any Stage 21 change invalidates all Stage 22 and Stage 23 artifacts derived from older configs.
- If Stage 21 is blocked, Stage 22 through Stage 25 and XGBoost-tuning sections of Stage 35 through Stage 40 are blocked.

## Required Tests And Validation

- Objective deterministic recomputation tests.
- Horizon-weight and penalty-term tests.
- No-lockbox-access tests.
- Search-space serialization and config-digest tests.
- Governance validation after registry or manifest updates.

## Completion Criteria

- The search-space and objective are frozen with artifact-backed digests and no unresolved decision gaps.
- Stage 22 can run without making new objective or budget decisions.

## Non-Claims

Search-space definition is not tuning evidence, benchmark evidence, promotion evidence, Stage 6 reinterpretation, or trading output.
