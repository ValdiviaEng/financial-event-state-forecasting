# v1p0 Stage 40 Prompt: v1p0 Completion And Next-Scope Gate

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Close the full v1p0 implementation cycle only after every prior stage has completed evidence or explicit user-approved blocked/deferred status, documentation, tests, and non-claim compliance. Agent-created silent deferrals are not valid completion evidence.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for approval gates, non-claim boundaries, naming, comparability, and forbidden scopes.
- Read `docs/NextSteps_Brainstorming.md` for the full selected roadmap, especially Stage 31-33 TSMixer/ensemble expectations and deferred product/live/trading scope.
- Read Stage 15 through Stage 39 outputs, `docs/v1p0_first_slice/Stage_Completion_Register.md`, `docs/v1p0_final_sprint/Final_v1p0_Sprint_Report.md`, `ResearchTruth.md`, and `docs/agent/agent_log/Current_State.md`.
- If any stage status is unclear, ask the user before declaring completion.

## Required Inputs

- Stage 15 through Stage 39 result-vault manifests, reports, and validation outputs.
- Explicit user-approved statuses for blocked/deferred/skipped stages.
- Stage 39 final claim-review manifest and allowed language.
- Governance, registry, ledger, and test validation outputs.

## Methodology

- Mark each Stage 15 through Stage 39 prompt as completed, blocked, skipped, or deferred with evidence and responsible decision source.
- Verify all result-vault entries are complete, non-secret, and linked to their source artifacts.
- Verify every implemented component has tests and validation output.
- Verify every claim is backed by artifacts and user approvals where needed.
- Identify next-scope candidates, such as Stage 31-33 completion if unresolved, persisted inference packaging, live provider refresh, dashboard/API, trading/ranking outputs, provider expansion, publication packet, or v1p1.
- Ask the user before any next-scope expansion or before closing with unresolved critical branches.

## Required Outputs

- v1p0 completion manifest with every stage status, evidence path, validation output, and unresolved blocker/defer reason.
- Final completion report with claim boundary, branch completeness, next-scope gates, and non-claims.
- Operational-memory and ledger updates.

## Success Measurements

- Every Stage 15-39 status is backed by an artifact or explicit user decision.
- No critical stage is silently deferred by the agent.
- Governance validator, ledger parse, registry parse if relevant, selected tests, and result-vault completeness checks pass.
- Stage 39 allowed language is preserved exactly and not upgraded.

## Blocking And User Questions

- Block and ask if any critical stage lacks completed evidence or explicit user-approved blocked/deferred status.
- Block and ask if tests fail, governance validation fails, result-vault artifacts are missing, secrets are detected, or Stage 39 allowed language is ambiguous.
- Block and ask before closing v1p0 while Stage 31-33 or other roadmap-critical stages are unresolved.
- Do not continue to next-scope work without explicit approval.

## Cascade Handling

- Stage 40 is invalidated by any rerun or status change in Stage 15 through Stage 39.
- If Stage 40 closes with user-approved partial scope, future work must start from the recorded next-scope gate and must not treat missing branches as completed.
- Any future claim upgrade requires rerunning or revalidating the affected Stage 35 through Stage 39 evidence chain.

## Required Tests And Validation

- Governance validator.
- Ledger JSONL parse.
- Registry YAML parse where registries changed.
- Full selected test suite.
- Result-vault completeness and non-secret check.
- Documentation consistency and forbidden-claim wording checks.

## Completion Criteria

- v1p0 is complete only if all implemented work is validated, documented, claim-reviewed, and every blocked/deferred/skipped critical stage has explicit user approval.

## Non-Claims

Completion of v1p0 does not approve future live/product/trading scopes, positive benchmark claims, comparability promotion, Stage 6 reinterpretation, or publication language beyond Stage 39 allowed wording.
