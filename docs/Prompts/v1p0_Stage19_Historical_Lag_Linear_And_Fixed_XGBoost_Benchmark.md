# v1p0 Stage 19 Prompt: Historical Lag-Linear And Fixed-XGBoost Benchmark

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Run full historical v1p0 `market_lag_linear_v1` and `market_xgboost_v1_fixed` baselines using the Stage 17 market feature sidecar, saved predictions, and fixed configurations, without tuning or lockbox feedback.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for thin-slice priority, versioned-candidate wording, non-claim boundaries, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for the selected weak-stack repair path, benchmark suite, XGBoost baseline choice, and hurdle-ladder intent.
- Read `BenchmarkingStrategy.md`, `LearningStrategy.md`, and Stage 16/17 manifests before fitting.
- If model roster, preprocessing policy, or saved-prediction scope is unclear, ask the user before training.

## Required Inputs

- Stage 16 compatibility manifest.
- Stage 17 market feature sidecar and feature manifest.
- Stage 3 labels and Stage 4 splits.
- Fixed lag-linear and fixed-XGBoost config from `configs/models_v1p0.yaml` or equivalent approved manifest.
- Required runtime environment, including `~/venvs/ai` when XGBoost is needed.

## Methodology

- Fit preprocessing and models fold-locally using training rows only.
- Save train predictions for diagnostics only, validation predictions for development evidence, and lockbox predictions only after fixed configs are frozen.
- Preserve row key, ticker, as-of date, horizon, fold, split role, target, prediction, model ID, feature ID, and config digest in every saved-prediction record.
- Record hyperparameters, seeds, runtime, dependency versions, feature IDs, fold IDs, row counts, failure modes, and skipped rows.
- Do not use lockbox metrics to change preprocessing, features, hyperparameters, or model roster.

## Required Outputs

- Saved predictions for `market_lag_linear_v1` and `market_xgboost_v1_fixed` or a blocker manifest for each missing model.
- Model fit manifests and preprocessing manifests.
- Result-vault report with row counts, runtime, config digests, dependency versions, and limitations.
- Registry update only after prediction schema and model dependency checks pass.

## Success Measurements

- Every expected model/horizon/fold/split-role combination has predictions or a documented blocker.
- Saved-prediction schema is stable and recomputable.
- Train/validation/lockbox roles are separated and provenance proves no lockbox tuning.
- Dependency failures are explicit blockers, not silent model omissions.

## Blocking And User Questions

- Block and ask if XGBoost or another required dependency is unavailable, if fixed configs are missing, if fold-local preprocessing cannot be verified, or if saved-prediction coverage is incomplete.
- Block and ask before substituting a different model, changing preprocessing, reducing horizons, skipping lockbox prediction generation, or changing the comparator roster.
- Do not continue to Stage 20 with partial baseline outputs unless the user explicitly approves a blocked/partial diagnostic run.

## Cascade Handling

- Stage 19 prediction IDs feed Stage 20 diagnostics, Stage 21 search design, Stage 22/23 hurdle comparisons, Stage 25 uncertainty, Stage 34 fusion comparisons, and Stage 35 through Stage 39 claim review.
- Any Stage 19 rerun invalidates downstream metrics and requires rerunning dependent diagnostics or marking them stale.
- If Stage 19 is blocked, Stage 20 through Stage 25 and any market-hurdle claims in Stage 34 through Stage 40 are blocked.

## Required Tests And Validation

- Fold-local preprocessing tests.
- Saved-prediction schema and row-key uniqueness tests.
- Deterministic seed/config digest tests.
- Lockbox no-tuning provenance tests.
- Train/validation/lockbox role separation tests.

## Completion Criteria

- Both baseline model IDs have complete manifests and saved predictions, or user-resolved blocker decisions are recorded.
- No positive result language appears before Stage 35 through Stage 39 diagnostics and claim review.

## Non-Claims

This prompt may create benchmark artifacts when executed, but it must not claim improvement, Stage 6 reinterpretation, comparability promotion, or trading usefulness.
