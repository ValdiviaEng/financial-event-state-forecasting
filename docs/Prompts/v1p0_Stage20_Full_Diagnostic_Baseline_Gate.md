# v1p0 Stage 20 Prompt: Full Diagnostic Baseline Gate

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Evaluate full historical lag-linear and fixed-XGBoost baseline outputs before any tuning or heavier model work begins, and decide whether Stage 21 XGBoost search is justified or blocked by data/model issues.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for implemented-truth separation, non-claim boundaries, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for performance-and-credibility priority, all-core diagnostics, stratified metrics, and overfit-control expectations.
- Read `BenchmarkingStrategy.md`, `VisualizationStrategy.md`, `ResearchTruth.md`, and Stage 19 prediction manifests.
- If diagnostic policy or decision threshold is unclear, ask the user before tuning begins.

## Required Inputs

- Complete Stage 19 saved-prediction packets or user-approved partial/blocker records.
- Stage 4 split metadata and Stage 3 labels.
- Stage 17 feature manifest for feature-family provenance.
- No-news, news-rich, truncation-risk, article-count, and related strata fields where available.

## Methodology

- Compute primary metrics by model, horizon, fold, split role, and relevant strata.
- Compute train-vs-validation gaps where train predictions exist.
- Compute fold dispersion, horizon stability, one-sided improvement flags, residual diagnostics, and failure notes.
- Compare each candidate against its appropriate hurdle, preserving versioned-candidate wording.
- Record whether tuning is allowed, blocked, or requires user clarification.

## Required Outputs

- Diagnostic tables and manifest under the result vault.
- Baseline gate report with metric summaries, overfit/stability notes, strata findings, and tuning-readiness classification.
- Explicit downstream decision: `proceed_to_stage21`, `blocked`, or `ask_user`.

## Success Measurements

- Metrics recompute exactly from saved predictions.
- Every model/horizon/fold/split role is represented or has a documented blocker.
- Overfit/stability and strata diagnostics are complete enough to decide whether Stage 21 search should proceed.
- Provider completeness is not claimed from no-news/truncation strata.

## Blocking And User Questions

- Block and ask if Stage 19 outputs are incomplete, metric recomputation fails, train/validation split roles are ambiguous, or diagnostics reveal severe instability that conflicts with continuing tuning.
- Block and ask before narrowing metrics, excluding horizons, dropping strata, or moving to Stage 21 with incomplete diagnostics.
- Do not treat diagnostic warnings as ignorable if they affect tuning, claim review, or comparability.

## Cascade Handling

- Stage 20 determines whether Stage 21 search-space freeze can proceed.
- If Stage 20 changes diagnostic policy, Stage 21 objective and later Stage 35/36 reports must inherit the new policy.
- If Stage 20 is blocked, Stage 21 through Stage 25 and XGBoost-related parts of Stage 35 through Stage 40 are blocked.

## Required Tests And Validation

- Metric recomputation tests from saved predictions.
- Train-gap, fold-dispersion, and horizon-stability tests.
- Strata bucket consistency tests.
- No provider-completeness claim tests.
- Result-vault manifest completeness checks.

## Completion Criteria

- Diagnostics are complete, reproducible, and clear enough to justify, block, or request user approval for XGBoost tuning.
- Any overfit or instability signal is explicitly recorded before Stage 21.

## Non-Claims

Diagnostic pass is not a promotion claim, positive benchmark claim, provider-completeness claim, Stage 6 reinterpretation, or trading signal.
