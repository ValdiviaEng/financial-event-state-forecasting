# v1p0 Stage 16 Prompt: Historical Artifact Compatibility Gate

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Verify whether later v1p0 candidates can consume existing Stage 2 through Stage 6 artifacts without silent drift, relabeling, or benchmark-family confusion. This is a hard compatibility gate, not a model run and not a benchmark-comparability promotion.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` before choosing any compatibility policy, especially implemented-truth, v1p0 design-truth, approval gates, naming, thin-slice boundary, comparability, and deprecated-material rules.
- Read `docs/NextSteps_Brainstorming.md` for the selected v1p0 roadmap, two-tier versioning, sidecar registry, benchmark-suite intent, TSMixer/FinBERT/ensemble sequencing, and deferred-scope decisions.
- Read `ResearchTruth.md` for artifact-backed Stage 2 through Stage 6 facts and non-claims.
- If these files conflict, preserve the stricter non-claiming interpretation and ask the user before proceeding.
- If a required decision is not found in these files, ask the user immediately and do not infer a policy.

## Required Inputs

- Stage 2 dataset manifest and row-universe digest.
- Stage 3 feature/label manifest and label contract.
- Stage 4 split manifest, fold map, split roles, and lockbox boundary.
- Stage 5 model/preprocessing/saved-prediction manifests if they are used as historical comparators.
- Stage 6 benchmark/reporting artifacts and comparator roster.
- Current `configs/v1p0_version_manifest.yaml` and `configs/feature_registry_v1p0.yaml` if they already exist.

## Methodology

- Resolve exact artifact roots before running any downstream stage.
- Compare row keys, row counts, ticker coverage, as-of-date coverage, horizon IDs, label IDs, fold IDs, split roles, no-news flags, truncation-risk flags, comparator IDs, and lockbox boundaries.
- Classify each historical input as `fully_compatible`, `versioned_candidate_input`, `not_comparable`, or `blocked` with a written reason.
- Verify that v0p9 or deprecated artifacts are not relabeled as v1p0 and are used only as reference/salvage material unless the active truth files explicitly authorize reuse.
- Record all compatibility risks before Stage 17, Stage 18, Stage 19, Stage 21, Stage 26, or any later candidate stage proceeds.

## Required Outputs

- Compatibility manifest in the result vault with artifact roots, digests, row counts, split coverage, horizon coverage, and classification.
- Human-readable compatibility report with blockers and allowed downstream usage.
- Registry or version-manifest update only if compatibility evidence is artifact-backed.
- Operational-memory and ledger entry if the stage is executed.

## Success Measurements

- Every required source artifact has a resolved path, digest, and compatibility classification.
- Row-key and split-role checks pass without unexplained missing or duplicated rows.
- Lockbox boundary is identical to the referenced benchmark contract when comparability is claimed.
- Any mismatch is promoted to `blocked` or `versioned_candidate_input`; it is never treated as a warning to ignore.

## Blocking And User Questions

- Block and ask the user if artifact roots are ambiguous, missing, stale, or contradictory.
- Block and ask the user before changing row universe, horizon set, provider stack, target family, clean-window policy, split policy, comparator roster, metric policy, benchmark-family label, or comparability classification.
- Block and ask the user before using deprecated/v0p9 material as active input unless the active truth files already approve that exact reuse.
- Do not continue to Stage 17 or later with an unresolved compatibility blocker.

## Cascade Handling

- If Stage 16 changes the selected artifact root, every downstream prompt must re-read the new manifest and update its source IDs.
- If Stage 16 classifies the chain as `versioned_candidate_input`, later reports must use versioned-candidate wording and must not compare as a direct Stage 6 continuation.
- If Stage 16 is blocked, Stage 17 through Stage 40 are blocked until the user resolves the compatibility decision.

## Required Tests And Validation

- Row-count, duplicate-key, horizon-coverage, fold-coverage, split-role, label-availability, and lockbox-boundary checks.
- Digest reproducibility checks for every referenced source artifact.
- Forbidden relabeling check for deprecated/v0p9 inputs.
- Governance validation and ledger JSONL parse after documentation/memory updates.

## Completion Criteria

- The compatibility report is complete enough for every later prompt to know exactly which historical artifacts it may consume.
- All blockers are either resolved by the user or remain blocking; no silent deferral or implicit compatibility is allowed.

## Non-Claims

This prompt does not create a new benchmark result, model improvement claim, Stage 6 reinterpretation, live forecast, trading signal, provider refresh, or benchmark-comparability promotion.
