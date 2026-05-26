# v1p0 Stage 33 Prompt: Market Ensemble Horizon Meta

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Evaluate `market_xgb_tsmixer_horizon_meta_v1`, a horizon-specific regularized meta-combiner, only after standalone XGBoost and TSMixer out-of-sample evidence exist. This stage must not be silently deferred or skipped because the ensemble rule was explicitly selected in the truth files.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for future market ensemble policy and standalone-model prerequisite.
- Read `docs/NextSteps_Brainstorming.md` Decisions 33 and 34 for always-explore ensemble policy and selected horizon-meta approach.
- Read Stage 24 XGBoost review and Stage 31 or Stage 32 TSMixer evidence.
- If standalone evidence is missing, ask the user whether to run the missing stage, use a user-approved narrower path, or defer the ensemble with full downstream consequences.

## Required Inputs

- Stage 24 XGBoost review and frozen XGBoost saved predictions.
- Stage 31 fixed multiseed TSMixer predictions or Stage 32 tuned TSMixer predictions/rejection evidence.
- Stage 4 folds/split roles and benchmark labels.
- Approved regularized horizon-meta combiner config and fold-local training policy.

## Methodology

- Confirm both standalone models have saved out-of-sample predictions and diagnostics.
- Train horizon-specific regularized meta-combiners fold-locally using development data only.
- Prevent meta-model leakage from validation feedback, lockbox feedback, or cross-fold target leakage.
- Record combiner coefficients, regularization parameters, training time, inference time, feature provenance, seed, and overfit diagnostics.
- Compare ensemble evidence against standalone XGBoost and standalone TSMixer by horizon, fold, split role, and strata.

## Required Outputs

- Ensemble saved predictions, metrics, coefficients, and model-fit manifests.
- Fold-local meta-training manifest proving no leakage.
- Stage 33 report comparing ensemble, XGBoost, and TSMixer evidence with non-claim wording.

## Success Measurements

- Both input model families have complete saved-prediction evidence before meta-training.
- Meta-combiner training is fold-local and lockbox-independent.
- Coefficients and regularization are reproducible from manifests.
- Ensemble comparison covers all approved horizons and relevant strata.

## Blocking And User Questions

- Block and ask if Stage 31/32 TSMixer predictions are missing, if XGBoost predictions are incomplete, if fold-local meta-training cannot be verified, or if ensemble config is ambiguous.
- Block and ask before deferring Stage 33, weakening to simple averaging, dropping horizons, using lockbox selection, or proceeding to Stage 35 without ensemble evidence.
- The agent must never record Stage 33 as deferred and continue to completion unless the user explicitly approves that deferral after seeing the impact.

## Cascade Handling

- Stage 33 outputs feed Stage 35 diagnostics, Stage 36 frontier, Stage 37 report packet, Stage 39 claim review, and Stage 40 completion status.
- If Stage 33 is blocked or user-deferred, Stage 35 through Stage 40 must label ensemble evidence as missing by user-approved decision, not as completed.
- Any Stage 33 rerun invalidates downstream ensemble diagnostics and claim review.

## Required Tests And Validation

- Fold-local meta-training tests.
- Horizon-specific split and no-lockbox tests.
- Coefficient/provenance manifest tests.
- Saved-prediction schema and row-coverage tests.
- Candidate-roster completeness tests for downstream diagnostics.

## Completion Criteria

- Ensemble evidence is compared against standalone models across horizons and strata, or the user explicitly resolves a blocker/defer decision.
- Silent deferral is not a valid completion state.

## Non-Claims

Ensemble output is not promoted without Stage 35 through Stage 39 diagnostic, uncertainty, overfit, and claim review.
