# v1p0 Stage 38 Prompt: Documentation Truth Consistency Audit

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Reconcile all active documentation after full v1p0 evidence exists, without upgrading claims beyond artifact support and without hiding blocked or user-deferred stages.

## Core Truth Sources

- Read `AgentRules.md`, `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `ProjectDefinition.md`, `Architecture_Map.md`, `Complete_guidebook.txt`, `UsageManual.md`, `BenchmarkingStrategy.md`, `VisualizationStrategy.md`, and the full v1p0 result vault.
- Treat `ArchitecturalDesignDecisions.md` and `docs/NextSteps_Brainstorming.md` as core design-truth sources when deciding whether a result is implemented truth, design truth, deferred scope, or blocked scope.
- If a doc update would change protected scope, delete/supersede active decisions, or promote claims, ask the user before editing.

## Required Inputs

- Full result-vault manifests through Stage 37.
- Stage 35/36/37 outputs and explicit missing-branch statuses.
- Current active root docs and operational memory.
- Governance validator expectations.

## Methodology

- Identify stale planning-only statements now superseded by implementation evidence.
- Update `ResearchTruth.md` only for confirmed truths backed by artifacts, tests, manifests, or explicit user decisions.
- Update `ArchitecturalDesignDecisions.md` only for actual durable decisions, not transient metrics or implementation results.
- Update `UsageManual.md` only for validated commands and artifacts.
- Update memory and ledger with stage status, blockers, non-claims, and validation evidence.
- Preserve distinctions among implemented truth, design truth, research synthesis, blocked scope, user-deferred scope, and non-claims.

## Required Outputs

- Documentation truth-audit manifest and report.
- Updated docs only where artifact-backed or user-approved.
- Operational-memory and ledger entries with validation evidence.
- List of unresolved stale-risk or approval-gated items.

## Success Measurements

- Every new truth claim references artifacts, tests, manifests, or explicit user decisions.
- Deferred or blocked stages remain labeled as such and are not normalized into completed evidence.
- Forbidden claim language is absent.
- Governance validator and ledger parse pass.

## Blocking And User Questions

- Block and ask if truth files conflict, if a proposed update changes protected scope, if evidence is insufficient, if Stage 31-33 or other critical statuses are unresolved, or if active decision files might be deleted/superseded.
- Block and ask before converting design truth to implemented truth without artifacts.
- Do not proceed to Stage 39 with documentation that masks blockers or claim limitations.

## Cascade Handling

- Stage 38 documentation state feeds Stage 39 final claim review and Stage 40 completion.
- Any post-Stage-38 artifact rerun requires a new truth audit or explicit stale marker.
- If Stage 38 is blocked, Stage 39 cannot approve positive language.

## Required Tests And Validation

- Governance validator.
- Ledger JSONL parse.
- Registry YAML parse where registries change.
- Stale path and forbidden-claim wording grep where practical.
- Source-evidence spot checks for new truth claims.

## Completion Criteria

- Docs distinguish implemented truth, design truth, research synthesis, blocked/user-deferred scope, and non-claims with no hidden claim upgrades.

## Non-Claims

Documentation reconciliation does not create benchmark evidence, comparability promotion, Stage 6 reinterpretation, or trading/product scope.
