# v1p0 Stage 27 Prompt: FinBERT Article Embedding Cache

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Materialize article-level FinBERT embeddings and sentiment logits/probabilities using the frozen Stage 26 contract, preserving no-news/truncation limitations and offline cache reproducibility.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for artifact governance, live-call restrictions, and non-claim boundaries.
- Read `docs/NextSteps_Brainstorming.md` for FinBERT embedding/logit and ablation decisions.
- Read Stage 26 contract, `LearningStrategy.md`, `BenchmarkingStrategy.md`, and Alpha Vantage limitation records cited by `ResearchTruth.md`.
- If extraction scope, cache reuse, or failure policy is unclear, ask the user before running.

## Required Inputs

- Stage 26 frozen source/cache contract.
- Approved article corpus with article IDs, ticker, timestamp/as-of mapping, title/summary/body fields as selected, provider flags, no-news fields, and truncation-risk context.
- Local model/tokenizer cache or approved download path.
- Runtime environment with device, package versions, batch size, and memory budget.

## Methodology

- Read only the approved article text fields and normalization policy from Stage 26.
- Extract embeddings and sentiment logits/probabilities according to the frozen model/tokenizer revisions.
- Cache by article ID, text hash, model revision, tokenizer revision, and preprocessing config hash.
- Preserve article timestamp, ticker, provider flags, no-news behavior, and truncation-risk context.
- Record extraction runtime, device, batch size, memory notes, failures, skipped rows, cache hits, and cache misses.

## Required Outputs

- Article embedding cache with stable schema and one row per cached article/text-hash record.
- Cache manifest with row counts, embedding dimension, logits/probability fields, failures, skipped rows, runtime, and digest.
- Report explaining completeness, limitations, and downstream aggregation readiness.

## Success Measurements

- Cache rows match the approved article corpus after documented skips/failures.
- Embedding dimension and logit/probability fields match the frozen model contract.
- Re-reading the cache produces identical rows and digests.
- Provider completeness is not inferred from article-cache row counts.

## Blocking And User Questions

- Block and ask if model/tokenizer revisions differ from Stage 26, cache write/read fails, article timestamps are ambiguous, extraction coverage is incomplete beyond approved tolerances, or memory budget prevents completion.
- Block and ask before changing batch size in a way that changes outputs, dropping article fields, replacing the model, compressing embeddings, or skipping article groups.
- Do not proceed to Stage 28 if cache completeness is unknown or failures are unexplained.

## Cascade Handling

- Stage 27 cache digest feeds Stage 28 aggregation and all event/fusion downstream artifacts.
- Any Stage 27 rerun invalidates Stage 28 through Stage 29 and event/fusion parts of Stage 34 through Stage 40.
- If Stage 27 is blocked, Stage 28 through Stage 29 and event/fusion paths are blocked unless the user approves a non-FinBERT fallback.

## Required Tests And Validation

- Article-cache schema tests.
- Deterministic re-read and digest tests.
- Embedding dimensionality and logit/probability tests.
- Missing/empty article handling tests.
- No provider-completeness claim tests.

## Completion Criteria

- Article cache is complete enough for aggregation with explicit counts, or it is blocked and the user has resolved how to proceed.

## Non-Claims

Article embeddings do not imply event-state model improvement, provider completeness, benchmark improvement, or trading usefulness.
