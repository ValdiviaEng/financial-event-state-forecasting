# v1p0 Stage 28 Prompt: FinBERT Aggregation Ablations

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Build versioned event-level FinBERT aggregation sidecars before fusion modeling, preserving article-count, no-news, truncation-risk, and cache-provenance evidence for later diagnostics.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for sidecar registry, versioned-candidate, and non-claim policy.
- Read `docs/NextSteps_Brainstorming.md` Decision 21 for the selected FinBERT ablation suite.
- Read Stage 27 article-cache manifest, `LearningStrategy.md`, and Stage 16/17 row-universe records.
- If aggregation variants, compression/projection, article inclusion windows, or no-news behavior are uncertain, ask the user before building sidecars.

## Required Inputs

- Stage 27 article embedding cache and manifest.
- Stage 3/4 row keys, labels, split roles, horizons, and as-of dates.
- Existing `event_hash_v0` reference where available.
- Feature registry and version manifest.

## Methodology

- Build `event_finbert_mean_v1`, `event_finbert_recency_v1`, `event_finbert_topk_v1`, and `event_finbert_count_recency_v1` unless the user approves a narrower set.
- Preserve `event_hash_v0` as a baseline reference, not as a replacement for FinBERT evidence.
- Include only as-of-safe articles for each row and record the article-selection policy.
- Record aggregation parameters, article counts, empty/no-news behavior, truncation flags, feature columns, feature digests, and cache digest provenance.
- Do not compress or project embeddings unless the method is specified by the prompt/truth files or explicitly approved by the user.

## Required Outputs

- One sidecar per aggregation variant with stable row keys and feature columns.
- Aggregation manifest with variant definitions, cache digest, row counts, article-count statistics, no-news behavior, truncation flags, and feature digests.
- Registry entries mapping variants to downstream model candidates.

## Success Measurements

- Every sidecar is one-to-one compatible with the approved row universe or has explicit user-approved exclusions.
- As-of article inclusion can be audited from timestamps and row keys.
- No-news rows have deterministic neutral/empty-state behavior.
- Feature registry references exactly the generated sidecar digests.

## Blocking And User Questions

- Block and ask if Stage 27 cache is incomplete, aggregation semantics are unclear, sidecar row alignment fails, compression/projection is needed but not approved, or no-news behavior is ambiguous.
- Block and ask before dropping variants, changing article inclusion windows, changing embedding dimensions, or updating registry mappings after validation failure.
- Do not proceed to Stage 29 with incomplete or unvalidated event sidecars.

## Cascade Handling

- Stage 28 sidecar digests feed Stage 29 representation benchmark and Stage 34 fusion.
- Any Stage 28 rerun invalidates Stage 29, Stage 34, and event/fusion diagnostics in Stage 35 through Stage 40.
- If Stage 28 is blocked, Stage 29 and Stage 34 event/fusion paths are blocked.

## Required Tests And Validation

- Aggregation determinism tests.
- As-of-safe article inclusion tests.
- No-news empty-state tests.
- Row-key compatibility tests.
- Feature registry mapping and digest tests.

## Completion Criteria

- Every aggregation sidecar is manifest-backed, registry-mapped, and compatible with labels/splits, or user-resolved blockers are recorded.

## Non-Claims

Feature ablation sidecars are not model evidence, benchmark improvement evidence, Stage 6 reinterpretation, or trading output.
