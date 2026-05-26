# v1p0 Stage 29 Prompt: Event Representation Benchmark Gate

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Benchmark FinBERT event-representation variants against `event_hash_v0` using controlled saved-prediction and diagnostic flows, selecting a representation for later fusion only from development evidence.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for versioned-candidate treatment, event-feature boundaries, and non-claim policy.
- Read `docs/NextSteps_Brainstorming.md` for FinBERT ablation, diagnostic, and fusion sequencing decisions.
- Read Stage 28 aggregation manifests, `BenchmarkingStrategy.md`, and Stage 16 compatibility records.
- If representation-selection criteria or model-head policy is unclear, ask the user before running comparisons.

## Required Inputs

- Stage 28 sidecars and aggregation manifest.
- `event_hash_v0` reference features where available.
- Stage 3 labels and Stage 4 split roles.
- Approved simple event-only model heads or fusion-free tests.

## Methodology

- Select only approved simple model heads or approved fusion-free tests for representation comparison.
- Train fold-locally and never use lockbox results to select the representation.
- Save predictions, metrics, runtime, hyperparameters, fit diagnostics, and representation IDs.
- Compare representation behavior across no-news, news-rich, truncation-risk, article-count, and news-sparse strata.
- Select the downstream representation only from validation/development evidence and record lockbox non-use.

## Required Outputs

- Saved predictions and metrics by representation ID.
- Event representation gate manifest with selected representation, selection criteria, overfit diagnostics, strata summaries, and lockbox-use flag.
- Report explaining selected representation, rejected variants, blockers, and non-claims.

## Success Measurements

- Selection is reproducible from development metrics and documented criteria.
- Lockbox rows used for representation selection equal zero.
- Every compared representation has complete schema, metrics, and provenance.
- No-news/truncation behavior is explicitly measured.

## Blocking And User Questions

- Block and ask if Stage 28 sidecars are incomplete, model-head policy is ambiguous, representation metrics conflict with selection rules, or lockbox leakage is detected.
- Block and ask before selecting no representation, selecting by lockbox, reducing variants, changing selection criteria, or carrying a failed representation forward.
- Do not proceed to Stage 34 with an unvalidated or ambiguously selected event representation.

## Cascade Handling

- Stage 29 selected representation feeds Stage 34 market-event fusion and Stage 35 diagnostics.
- Any Stage 29 selection change invalidates Stage 34 through Stage 39 fusion evidence.
- If Stage 29 is blocked, Stage 34 event fusion and event-related claim review are blocked.

## Required Tests And Validation

- Representation registry tests.
- Saved-prediction schema tests.
- No-news row behavior tests.
- Strata diagnostic tests.
- Lockbox-zero selection tests.

## Completion Criteria

- A representation is selected only when it improves development evidence without hidden leakage or overfit signals, or the user resolves a blocked selection.

## Non-Claims

Event representation improvement claims require Stage 35 through Stage 39 review and cannot be inferred from this gate alone.
