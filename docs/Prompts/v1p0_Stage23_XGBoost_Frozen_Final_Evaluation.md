# v1p0 Stage 23 Prompt: XGBoost Frozen Final Evaluation

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Evaluate the frozen XGBoost candidate after tuning is complete, using the approved benchmark protocol exactly once for final reporting and without changing the selected config after lockbox metrics are available.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for non-claim boundaries, comparability restrictions, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for hurdle-delta policy, overfit-control priority, and XGBoost search sequence.
- Read Stage 21 frozen objective config, Stage 22 search ledger, `BenchmarkingStrategy.md`, and `ResearchTruth.md`.
- If the frozen candidate digest or lockbox protocol is ambiguous, ask the user before evaluation.

## Required Inputs

- Stage 22 best-candidate manifest and frozen config digest.
- Stage 21 objective/search config digest.
- Stage 17 feature sidecar and Stage 4 split metadata.
- Stage 19 fixed baseline predictions for hurdle comparison.

## Methodology

- Verify the candidate was selected before lockbox evaluation.
- Fit/generate predictions using the frozen candidate exactly as recorded.
- Save train predictions for diagnostics, validation predictions for development context, and lockbox predictions for final reporting only.
- Compute metrics from saved predictions only and preserve all provenance.
- Do not alter preprocessing, hyperparameters, features, horizons, or candidate ID after seeing final metrics.

## Required Outputs

- Saved predictions for `market_xgboost_v2_frozen_final`.
- Metrics, model-fit manifest, frozen-config digest, runtime report, and result-vault manifest.
- Human-readable final-evaluation report with explicit non-claims.

## Success Measurements

- Frozen-config digest matches the Stage 22 selected candidate.
- Prediction schema and row coverage match the approved benchmark universe.
- Metrics recompute exactly from saved predictions.
- Lockbox evaluation is one-pass and not used for model selection or revision.

## Blocking And User Questions

- Block and ask if the frozen candidate is missing, digest checks fail, saved predictions are incomplete, metric recomputation fails, or any post-lockbox change is required.
- Block and ask before reducing horizons, altering lockbox handling, rerunning selection, or changing final-evaluation wording.
- Do not continue to Stage 24 with ambiguous final-evaluation provenance.

## Cascade Handling

- Stage 23 artifacts feed Stage 24 overfit review, Stage 25 uncertainty, Stage 34 comparisons, and Stage 35 through Stage 39 claim review.
- Any Stage 23 rerun invalidates Stage 24/25/35/36/39 outputs that referenced the old frozen-final predictions.
- If Stage 23 is blocked, Stage 24 through Stage 25 and tuned-XGBoost claim-review paths are blocked.

## Required Tests And Validation

- Frozen-config digest and provenance tests.
- No-lockbox-tuning tests.
- Saved-prediction schema and row-coverage tests.
- Metric-from-prediction recomputation tests.
- Result-packet completeness tests.

## Completion Criteria

- `market_xgboost_v2_frozen_final` exists only with complete frozen-candidate evidence and reproducible metrics.
- Any positive result language remains deferred to Stage 39.

## Non-Claims

Final evaluation artifacts alone do not authorize a positive conclusion, benchmark-comparability promotion, Stage 6 reinterpretation, or trading use.
