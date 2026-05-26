# v1p0 Stage 24 Prompt: XGBoost Overfit Frontier And Promotion Review

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Decide whether XGBoost tuning improved real generalization or crossed into overfitting by comparing search history, train metrics, validation metrics, final evaluation evidence, complexity, and strata behavior.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for non-claim policy, versioned-candidate language, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for aggressive accuracy optimization with overfit control.
- Read Stage 20 diagnostics, Stage 22 trial ledger, Stage 23 frozen evaluation packet, and `BenchmarkingStrategy.md`.
- If promotion thresholds or candidate classes are ambiguous, ask the user before classifying.

## Required Inputs

- Stage 22 trial ledger, fold metrics, score components, and selected-candidate manifest.
- Stage 23 frozen-final predictions and metrics.
- Stage 19 fixed-hurdle predictions and Stage 20 diagnostics.
- Any train metrics needed for overfit frontier analysis.

## Methodology

- Tabulate the overfit frontier: complexity/search depth versus train, validation, and final metrics.
- Identify points where training performance improves while validation/final performance degrades or becomes unstable.
- Compare fixed baseline versus tuned candidate across horizons, folds, split roles, and strata.
- Classify the candidate conservatively as `blocked`, `exploratory_only`, `development_candidate`, `lockbox_reported_candidate`, or `promotion_review_candidate`.
- Record required follow-up if overfitting, instability, or evidence gaps are detected.

## Required Outputs

- Overfit-frontier table and candidate-classification manifest.
- Promotion-review report with explicit evidence, caveats, and non-claim wording.
- Follow-up blocker list if uncertainty or diagnostics are insufficient.

## Success Measurements

- Classification is reproducible from documented thresholds and artifact evidence.
- Overfit evidence includes train, validation, and final/lockbox context where available.
- Candidate is not upgraded solely because lockbox metrics look favorable.
- Evidence gaps are blockers or limitations, not hidden omissions.

## Blocking And User Questions

- Block and ask if Stage 22 or Stage 23 artifacts are incomplete, overfit metrics conflict, classification thresholds are not defined, or a positive/promotion decision is being considered.
- Block and ask before changing candidate classes, relaxing overfit criteria, or treating lockbox results as selection evidence.
- Do not proceed to Stage 25 or Stage 39 promotion language with unresolved overfit concerns.

## Cascade Handling

- Stage 24 classification controls how Stage 25 uncertainty and Stage 35/36 diagnostics frame the tuned XGBoost candidate.
- If Stage 24 is rerun or reclassified, all downstream claim-review artifacts must be refreshed or marked stale.
- If Stage 24 is blocked, promotion language remains blocked and Stage 25 must run only as diagnostic uncertainty if user-approved.

## Required Tests And Validation

- Overfit-frontier table schema tests.
- Candidate-classification rule tests.
- No result-language promotion before Stage 39 tests.
- Source-metric reproducibility checks.

## Completion Criteria

- Overfitting evidence is explicit, conservative, and artifact-backed.
- Candidate classification is documented and does not approve positive claims by itself.

## Non-Claims

This prompt may recommend later review but does not approve positive claims, comparability promotion, Stage 6 reinterpretation, or trading use.
