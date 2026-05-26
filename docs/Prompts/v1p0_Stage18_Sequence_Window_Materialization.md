# v1p0 Stage 18 Prompt: Sequence Window Materialization

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Create the sequence-window contract and materialized tensors required for the pure PyTorch `market_tsmixer_v1` path. Stage 18 is not optional for Stage 30 through Stage 33 execution; if it cannot be completed, those later stages must be blocked until the user explicitly resolves the issue.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for the TSMixer pure-PyTorch decision, standalone-first strategy, sequence-window contract, and deferred-contract boundaries.
- Read `docs/NextSteps_Brainstorming.md` Decisions 29, 31, and 32 for two-tier windows, pure PyTorch, fixed-then-multiseed discipline, and nested optimization only after promising standalone evidence.
- Read `LearningStrategy.md` and `BenchmarkingStrategy.md` for temporal-model and benchmark discipline.
- If window length, feature set, padding, normalization, or budget policy is not specified in the truth files, ask the user before materializing or skipping.

## Required Inputs

- Stage 16 compatibility manifest.
- Stage 17 market feature sidecar and manifest.
- Stage 4 split roles and fold IDs.
- Stage 3 labels and horizon metadata.
- Approved compute/storage constraints if full tensor materialization may be expensive.

## Methodology

- Define sequence versions for `20d` and `60d` contexts first, with `126d` only if explicitly approved or already documented by the truth files.
- Specify tensor dimensions as `row_key x window_length x feature_count`, plus masks for missing history and optional metadata tables.
- Use only historical observations available before or at the row's as-of close; never include target-window data.
- Define padding and missing-history handling before writing tensors.
- Define fold-local normalization fit on training data only, with validation and lockbox transformed by fold-local parameters.
- Materialize tensors only after contract, storage estimate, and tests pass.

## Required Outputs

- Sequence-window contract manifest with version, feature columns, window lengths, dtype, shape rules, padding policy, normalization policy, row-key mapping, and digests.
- Materialized sequence tensors or a user-approved blocked record explaining why tensors could not be built.
- Validation report with shape, coverage, missing-history, leakage, and storage-footprint results.

## Success Measurements

- Every Stage 4 row intended for TSMixer has a one-to-one tensor index or an explicit exclusion reason.
- Tensor shapes and dtypes match the manifest exactly.
- Fold-local normalization is proven not to use validation or lockbox statistics.
- Storage and runtime are recorded and fit the approved execution budget.

## Blocking And User Questions

- Block and ask if Stage 17 features are unavailable, sequence semantics are ambiguous, memory/disk budget is unknown, leakage tests fail, or tensor coverage is incomplete.
- Block and ask before recording Stage 18 as skipped/deferred in a continuous run; the user must decide whether to pause, reduce scope, allocate compute, or explicitly defer Stage 30 through Stage 33.
- Do not proceed to Stage 30, Stage 31, Stage 32, or Stage 33 with tabular substitutes masquerading as sequence tensors.

## Cascade Handling

- Any Stage 18 feature-list, window-length, padding, or normalization change invalidates Stage 30 smoke evidence and Stage 31 through Stage 33 TSMixer/ensemble evidence.
- If Stage 18 is blocked, Stage 30 through Stage 33 are blocked; Stage 34 through Stage 40 may continue only after the user explicitly approves continuing with a partial non-TSMixer branch.
- If Stage 18 is rerun, downstream TSMixer artifacts must carry the new sequence artifact ID.

## Required Tests And Validation

- Shape, dtype, row-key, and horizon-coverage tests.
- No-future-row leakage tests.
- Fold-local normalization tests.
- Missing-history, padding, and mask tests.
- Digest and storage-footprint reproducibility checks.

## Completion Criteria

- Stage 18 is complete only when sequence tensors and contracts are materialized and validated, or when the user explicitly chooses a blocked/deferred path after being asked.

## Non-Claims

Sequence windows do not prove TSMixer quality, benchmark improvement, Stage 6 reinterpretation, or trading value.
