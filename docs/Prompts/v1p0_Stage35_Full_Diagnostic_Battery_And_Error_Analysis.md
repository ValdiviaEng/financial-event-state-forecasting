# v1p0 Stage 35 Prompt: Full Diagnostic Battery And Error Analysis

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Run the full diagnostic battery across all completed v1p0 candidates before any claim review, while explicitly surfacing missing, blocked, or user-deferred candidates instead of silently omitting them.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for non-claim policy, benchmark-family treatment, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` for all-core diagnostics, stratified metrics, overfit control, TSMixer, ensemble, and fusion sequencing.
- Read `BenchmarkingStrategy.md`, `ResearchTruth.md`, and candidate packets from Stages 19, 23, 29, 31/32, 33, and 34 as available.
- If candidate roster completeness is uncertain, ask the user before running partial diagnostics.

## Required Inputs

- Saved-prediction and metric packets from all completed candidate stages.
- Explicit user-approved blocked/deferred records for any missing critical stage, especially Stage 31 through Stage 33.
- Stage 25 uncertainty evidence, Stage 24 overfit review, and Stage 34 fusion evidence if available.
- Strata fields for no-news, news-rich, truncation-risk, article-count, and news-sparse analysis.

## Methodology

- Compute primary metrics, ranking diagnostics, train gaps, fold dispersion, horizon stability, and positive-horizon rates.
- Compute no-news, news-rich, truncation-risk, article-count, and news-sparse strata.
- Compute failure notes by ticker, date, fold, horizon, model, feature family, and candidate branch.
- Compare every candidate against the appropriate hurdle and record missing-candidate status.
- Classify each candidate conservatively using artifact evidence and explicit limitation notes.

## Required Outputs

- Full diagnostic tables, candidate roster, classification table, strata tables, failure notes, and manifest.
- Diagnostic report that lists completed, blocked, and user-deferred stages separately.
- Downstream readiness statement for Stage 36 and Stage 39.

## Success Measurements

- Every expected candidate is either diagnosed or listed with a blocker/user-defer decision.
- Metrics recompute from saved predictions and match source tables.
- Strata and horizon diagnostics cover all available candidates.
- Conservative classifications preserve uncertainty, overfit, and missing-branch limitations.

## Blocking And User Questions

- Block and ask if candidate roster is incomplete without explicit user-approved status, if metrics fail to recompute, if Stage 31-33 are missing and not user-resolved, or if a critical branch is silently absent.
- Block and ask before excluding candidates, changing hurdles, reducing diagnostic scope, or proceeding to Stage 36/39 with partial evidence.
- Do not let a partial diagnostic battery appear as a full-v1p0 diagnostic battery.

## Cascade Handling

- Stage 35 classifications feed Stage 36 frontier, Stage 37 reporting, Stage 39 claim review, and Stage 40 completion.
- Any new or rerun candidate invalidates the Stage 35 candidate roster and downstream summaries.
- If Stage 35 is partial by user approval, Stage 39 and Stage 40 must preserve partial-evidence wording.

## Required Tests And Validation

- Metric recomputation tests.
- Strata consistency tests.
- Hurdle comparison tests.
- Candidate roster completeness tests.
- Non-claim report and missing-branch wording tests.

## Completion Criteria

- Every candidate has a conservative diagnostic classification or an explicit user-resolved blocker/defer status.
- Stage 35 is not complete if critical stages are silently missing.

## Non-Claims

Diagnostic tables alone do not approve positive claims, comparability promotion, Stage 6 reinterpretation, or trading use.
