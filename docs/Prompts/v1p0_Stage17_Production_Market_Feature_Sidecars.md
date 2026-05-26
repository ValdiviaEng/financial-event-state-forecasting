# v1p0 Stage 17 Prompt: Production Market Feature Sidecars

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Materialize full historical market lag/rolling feature sidecars for v1p0 from the Stage 16-approved artifact chain, preserving row identity and as-of safety without mutating historical artifacts.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for v1p0 naming, thin-slice boundary, sidecar registry, versioned-candidate treatment, and approval gates.
- Read `docs/NextSteps_Brainstorming.md` Decisions 29 and 30 for two-tier windows and hybrid sidecar registry policy.
- Read `BenchmarkingStrategy.md` and `LearningStrategy.md` for model/hurdle expectations and leakage discipline.
- If the feature policy is unclear or conflicts with the truth files, ask the user before building features.

## Required Inputs

- Stage 16 compatibility manifest with approved Stage 2 through Stage 4 artifact roots.
- `configs/market_features_v1p0.yaml` and `configs/feature_registry_v1p0.yaml`.
- Historical OHLCV/support market inputs approved by the Stage 16 chain.
- Existing row keys, ticker IDs, as-of dates, horizon IDs, fold IDs, split roles, labels, no-news flags, and truncation-risk flags needed downstream.

## Methodology

- Build only as-of-safe market features using data available at or before each row's as-of close.
- Use the selected two-tier market windows: returns `1d/5d/10d/20d/60d`, volatility `5d/20d/60d`, volume ratios `5d/20d/60d`, high-low range `5d/20d`, drawdown `20d/60d`, and market-relative returns where leakage-safe.
- Fit any imputation, scaling, or feature-selection policy fold-locally in downstream model stages, not globally in the sidecar.
- Preserve one-to-one row alignment with Stage 4 split rows unless a user-approved versioned-candidate branch explicitly changes row semantics.
- Update feature registry mappings only after validation passes.

## Required Outputs

- Market feature parquet or equivalent sidecar with stable row keys and feature columns.
- Feature manifest with source artifact IDs, feature list, row counts, null counts, digest, build time, and leakage-test results.
- Registry entry mapping model IDs to the exact feature sidecar.
- Result-vault report describing limitations and downstream dependencies.

## Success Measurements

- Row count and key set match the Stage 16-approved split universe exactly unless a user-approved versioned-candidate branch says otherwise.
- All feature timestamps are as-of-safe and no future rows are read.
- Null policy is explicit by feature and by split role.
- Registry update is reproducible from the generated manifest and digest.

## Blocking And User Questions

- Block and ask if approved market input files are missing, row identity changes, feature windows differ from the truth files, or leakage tests fail.
- Block and ask before adding new providers, new target semantics, new horizons, new feature families outside the selected policy, or any raw-data overwrite.
- Do not proceed to Stage 19, Stage 34, or downstream diagnostics with unvalidated feature sidecars.

## Cascade Handling

- Any feature-column, row-count, null-policy, or digest change invalidates Stage 19 and later model predictions and requires those stages to be rerun or explicitly blocked.
- If Stage 17 is blocked, Stage 19 through Stage 25 and market portions of Stage 34 through Stage 40 are blocked.
- If Stage 17 changes feature semantics, Stage 18 sequence-window contracts must re-read the new feature manifest before materializing tensors.

## Required Tests And Validation

- No-lookahead tests at ticker/date level.
- Row-count and row-key compatibility tests against Stage 4 splits.
- Null-policy and feature-list tests.
- Manifest digest reproducibility tests.
- Registry schema and model-dependency tests.

## Completion Criteria

- Market sidecar artifacts, manifests, registry entries, and validation outputs are complete, reproducible, and compatible with the approved row universe.
- All downstream assumptions affected by the sidecar are recorded before continuing.

## Non-Claims

Feature sidecars are not model evidence, benchmark improvement evidence, Stage 6 reinterpretation, or trading output.
