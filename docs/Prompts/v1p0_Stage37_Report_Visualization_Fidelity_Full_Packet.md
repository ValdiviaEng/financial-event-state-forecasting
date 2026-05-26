# v1p0 Stage 37 Prompt: Report And Visualization Fidelity Full Packet

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Create the final static report and visualization-ready packet for full v1p0 evidence, preserving source-table fidelity, branch-completeness status, and non-claim boundaries.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for non-claim policy, forbidden scopes, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` Stage 10C/report decisions, diagnostics decisions, and deferred live/product/trading scope.
- Read `VisualizationStrategy.md`, Stage 35 diagnostics, Stage 36 frontier report, and Stage 39 requirements.
- If report language would imply a claim not supported by evidence or approval, ask the user before writing it.

## Required Inputs

- Stage 35 diagnostic tables and candidate classifications.
- Stage 36 frontier/action tables.
- Stage 25 uncertainty evidence and Stage 39 claim-review prerequisites if available.
- Explicit status for missing, blocked, or user-deferred stages.

## Methodology

- Render per-horizon tables, hurdle-delta tables, strata tables, uncertainty tables, overfit-frontier tables, candidate roster, and caveat panels.
- Include static charts only if source-table fidelity tests exist.
- Use deterministic sorting, ranking, tie breaks, formatting, captions, and file naming.
- Show historical markers only; no projected price paths, fan charts, price targets, or trading signals.
- Ensure report values equal source CSV/Parquet/JSON tables and branch statuses are visible.

## Required Outputs

- Final report packet, source tables, chart-ready tables, manifest, and fidelity test results.
- Forbidden-wording/non-claim report checks.
- Caveat panel covering no-news/truncation limitations, missing branches, uncertainty, overfit, and claim-review status.

## Success Measurements

- Every rendered number traces to a source table and passes equality checks.
- Every missing/deferred branch is labeled with user-approved status or blocks completion.
- No report text implies positive benchmark improvement before Stage 39 approval.
- Report is deterministic across reruns.

## Blocking And User Questions

- Block and ask if source-table fidelity fails, Stage 35/36 status is incomplete, missing-branch wording is unresolved, or a proposed chart/report element implies live forecasting/trading/positive claims.
- Block and ask before excluding caveats, adding unsupported charts, changing ranking policy, or publishing positive language.
- Do not proceed to Stage 39 with a report packet that hides unresolved blockers.

## Cascade Handling

- Stage 37 report is the source-facing packet reviewed in Stage 39.
- Any Stage 35 or Stage 36 rerun requires Stage 37 report refresh.
- If Stage 37 is partial or blocked, Stage 39 cannot approve positive language.

## Required Tests And Validation

- Report/source table equality tests.
- Required caveat and branch-status tests.
- Forbidden wording tests.
- Accessibility/readability smoke tests.
- Deterministic ranking and formatting tests.

## Completion Criteria

- Report packet is source-faithful, caveated, and ready for Stage 39 claim review without hidden assumptions.

## Non-Claims

Visualization readiness does not create scientific claims, comparability promotion, Stage 6 reinterpretation, or trading output.
