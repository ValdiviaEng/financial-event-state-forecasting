# v1p0 Stage 34 Prompt: Market Event Horizon Fusion

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Evaluate `event_market_horizon_fusion_v1`, the first serious market plus FinBERT event fusion candidate, while preserving the strong market hurdle and not masking missing TSMixer/ensemble evidence from Stage 31 through Stage 33.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for market/event fusion policy, sidecar registry, non-claim boundaries, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` Decision 35 for horizon-specific fusion.
- Read Stage 29 event representation gate, Stage 24 XGBoost review, Stage 33 ensemble evidence if completed, and `BenchmarkingStrategy.md`.
- If Stage 31 through Stage 33 are incomplete, ask the user whether to continue with independent market-event fusion while leaving the TSMixer/ensemble branch blocked or to pause and execute the missing branch.

## Required Inputs

- Stage 17 market feature sidecar.
- Stage 29 selected event representation and sidecar.
- Stage 23/24 market XGBoost hurdle evidence.
- Stage 33 ensemble evidence if available or user-approved status if unavailable.
- Stage 4 folds/split roles and Stage 3 labels.

## Methodology

- Confirm market and event feature artifacts are compatible by row, horizon, fold, split role, and label.
- Train horizon-specific regularized fusion models fold-locally.
- Preserve no-news, news-rich, truncation-risk, and article-count behavior explicitly.
- Save predictions, coefficients or feature importances where applicable, hyperparameters, runtime, and diagnostics.
- Compare against strong market-only hurdle and event-only representation tests.

## Required Outputs

- Fusion saved predictions, metrics, feature manifest, model-fit manifest, and market-hurdle delta table.
- Fusion report with classification, strata behavior, overfit notes, and non-claims.
- Explicit record of Stage 31-33 status and whether user approved proceeding without that branch.

## Success Measurements

- Market/event row alignment is exact and reproducible.
- Fusion model training is fold-local and lockbox-independent.
- Comparison uses a strong market hurdle, not a weak baseline.
- No-news and truncation-risk strata are measured and reported.

## Blocking And User Questions

- Block and ask if Stage 29 selection is ambiguous, row alignment fails, market hurdle evidence is missing, fusion config is unclear, or Stage 31-33 missing status has not been explicitly resolved for the continuous execution path.
- Block and ask before changing fusion model family, reducing horizons, dropping no-news/truncation strata, or continuing to Stage 35 with unresolved branch status.
- Do not use fusion evidence to imply event value before Stage 35 through Stage 39.

## Cascade Handling

- Stage 34 outputs feed Stage 35 diagnostics, Stage 36 frontier, Stage 37 report packet, and Stage 39 claim review.
- If Stage 34 is rerun or selected event representation changes, downstream fusion diagnostics and reports must be refreshed.
- If Stage 31 through Stage 33 are blocked but Stage 34 proceeds by user approval, later stages must mark the TSMixer/ensemble branch as explicitly unresolved or deferred by user decision.

## Required Tests And Validation

- Row alignment and one-to-one merge tests.
- No-news/truncation fusion behavior tests.
- Fold-local training and no-lockbox tests.
- Saved-prediction schema tests.
- Non-claim report wording tests.

## Completion Criteria

- Event-state value is assessed against a strong market hurdle with complete provenance and no unresolved branch-status ambiguity.

## Non-Claims

Fusion evidence must pass Stage 35 through Stage 39 before positive language, comparability promotion, Stage 6 reinterpretation, or trading use is allowed.
