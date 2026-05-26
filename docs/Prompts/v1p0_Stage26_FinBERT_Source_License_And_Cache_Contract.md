# v1p0 Stage 26 Prompt: FinBERT Source, License, And Cache Contract

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Select and freeze the pinned FinBERT source, tokenizer, license review, environment requirements, text-scope policy, and embedding-cache contract before extracting any article embeddings.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for FinBERT design truth, provider/live-call restrictions, artifact governance, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` Decisions 19 through 23 for FinBERT encoder choice, ablation suite, Hugging Face pinned source, embedding/logit policy, and diagnostics.
- Read `LearningStrategy.md`, `ResearchTruth.md`, and relevant raw-news limitation records.
- If model ID, revision, tokenizer, text scope, license acceptability, or download/cache policy is not already decided, ask the user before any extraction.

## Required Inputs

- Selected FinBERT model candidate list or explicit user-selected model ID.
- News/article corpus references already approved by prior stages.
- Local environment details, GPU/CPU availability, and cache directory policy.
- Existing no-news/truncation limitation records.

## Methodology

- Resolve exact Hugging Face model ID, model revision/hash, tokenizer ID, tokenizer revision/hash, and relevant config hash.
- Review model card, license metadata, and distribution caveats for research usage.
- Define article text normalization, selected text fields, text hash, provider metadata, cache key fields, and duplicate-handling policy.
- Define offline rerun requirements after cache materialization so later stages can reuse local artifacts without repeated external access.
- Record GPU/CPU environment, package versions, batch-size limits, and failure behavior.

## Required Outputs

- Source/cache contract manifest with model, tokenizer, revision, license notes, text-scope policy, cache keys, environment, and limitations.
- Report documenting user decisions, unresolved risks, and non-claim boundaries.
- Registry/version-manifest update only after the contract is frozen.

## Success Measurements

- Model and tokenizer revisions are immutable and reproducible.
- Cache keys uniquely identify article text, model revision, tokenizer revision, and preprocessing config.
- License and model-card caveats are explicitly recorded.
- No embedding extraction starts before contract freeze.

## Blocking And User Questions

- Block and ask if the model source, license status, text scope, cache path, or external-download policy is uncertain.
- Block and ask before substituting a different FinBERT model, changing text fields, compressing embeddings, adding providers, or making live provider calls.
- Do not proceed to Stage 27 with an unresolved contract or licensing ambiguity.

## Cascade Handling

- Stage 26 contract IDs feed Stage 27 cache, Stage 28 aggregations, Stage 29 representation selection, Stage 34 fusion, and Stage 35 through Stage 40 review.
- Any Stage 26 change invalidates downstream embedding and event-feature artifacts.
- If Stage 26 is blocked, Stage 27 through Stage 29 and event/fusion paths in Stage 34 through Stage 40 are blocked.

## Required Tests And Validation

- Cache-key determinism tests.
- Tokenizer/model revision capture tests.
- Offline-read path tests.
- No future-news leakage tests.
- Contract schema and registry dependency tests.

## Completion Criteria

- Source and cache contract are frozen with artifact-backed revisions and user decisions where needed.
- Downstream stages can run without choosing model source, text scope, or cache semantics.

## Non-Claims

This prompt does not call market/news providers, mutate raw data, produce embeddings, approve benchmark claims, or approve model-distribution claims.
