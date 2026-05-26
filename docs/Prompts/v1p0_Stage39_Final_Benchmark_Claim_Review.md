# v1p0 Stage 39 Prompt: Final Benchmark Claim Review

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Determine the allowed final result language for v1p0 after diagnostics, uncertainty, overfit, report-fidelity, and documentation-truth evidence exists, with explicit handling of any blocked or user-deferred stages.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for approval gates, benchmark-comparability restrictions, Stage 6 non-reinterpretation, and forbidden scopes.
- Read `docs/NextSteps_Brainstorming.md` for the selected roadmap, TSMixer/ensemble/fusion expectations, and deferred live/product/trading scope.
- Read `BenchmarkingStrategy.md`, `ResearchTruth.md`, Stage 35 diagnostic battery, Stage 36 overfit frontier report, Stage 37 report packet, and Stage 38 documentation audit.
- If claim language, comparability, or missing-branch interpretation is unclear, ask the user before approving any language.

## Required Inputs

- Stage 35 candidate classifications and roster completeness status.
- Stage 36 overfit frontier and candidate action recommendations.
- Stage 25 uncertainty evidence and any additional uncertainty tables.
- Stage 37 report packet and Stage 38 truth audit.
- Explicit user-approved status for any blocked/deferred critical stage.

## Methodology

- Classify the result as positive, conditional-positive, clean-null, limitation-bearing, blocked, exploratory-only, or conditional non-claim using artifact evidence.
- Review comparability against historical Stage 6 and v1p0 candidate-family definitions.
- Confirm uncertainty evidence includes required date-clustered and block-bootstrap support before any promotion.
- Confirm overfit evidence does not undermine the proposed claim.
- Confirm report language matches source evidence, branch completeness, and user approvals.
- Ask the user before any claim upgrade or comparability promotion.

## Required Outputs

- Final claim-review manifest with allowed language, forbidden language, result classification, comparability classification, and approval status.
- Claim-review report citing supporting artifacts and limitations.
- User-question record if positive claim or comparability promotion is possible but not already approved.

## Success Measurements

- Final language is traceable to Stage 35-38 evidence and user approvals.
- Positive claim is not approved when evidence is mixed, incomplete, overfit-contaminated, or missing critical branches.
- Benchmark-comparability promotion is never inferred without explicit approval.
- Missing Stage 31-33 evidence is treated as a limitation/blocker unless user-approved otherwise.

## Blocking And User Questions

- Block and ask if Stage 35-38 evidence is incomplete, uncertainty is weak, overfit concerns remain, branch status is unresolved, or any claim upgrade/comparability promotion is contemplated.
- Block and ask before converting non-claim language to positive language.
- Do not use favorable lockbox metrics alone to approve a positive claim.

## Cascade Handling

- Stage 39 allowed language controls Stage 40 completion docs and all public-facing summaries.
- Any rerun of Stage 25 or Stage 35-38 invalidates Stage 39 claim review.
- If Stage 39 is blocked or non-claiming, Stage 40 must preserve that limitation and cannot close as positive/publication-ready.

## Required Tests And Validation

- Claim-language forbidden wording tests.
- Comparability classification tests.
- Result-summary source fidelity tests.
- Non-claim preservation tests.
- Approval-evidence checks for any upgraded language.

## Completion Criteria

- Final language is evidence-backed, conservative, and explicitly approved where protected gates require approval.

## Non-Claims

No positive claim is allowed if evidence is mixed, incomplete, overfit-contaminated, missing critical branches, or not explicitly approved.
