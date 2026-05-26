# v1p0 Stage 01 Reuse Versus Rewrite Audit

Status: completed audit; design evidence only

Updated: 2026-05-24

## Decision

The v1p0 first-slice implementation will rewrite minimal active code instead of importing v0p9 modules.

## Component Classification

| Component | v0p9 reference files | Classification | Reason | Compatibility requirement |
| --- | --- | --- | --- | --- |
| Version manifest and registry | `deprecated/v0p9/src/benchmark/registry.py`, `deprecated/v0p9/src/dataset/dataset_versioning.py` | rewrite | v1p0 requires explicit non-relabeling and sidecar registry contracts. | New v1p0 config smoke tests. |
| Market lag/rolling features | `deprecated/v0p9/src/features/market.py` | rewrite | v0p9 market features are same-row as-of-close only; v1p0 needs lag/rolling sidecar features. | Toy no-lookahead tests. |
| Split/label compatibility | `deprecated/v0p9/src/split/`, `deprecated/v0p9/src/features/labels.py` | reference-only | v0p9 logic remains useful for concepts but depends on old artifact names and Stage 4 contracts. | New row-key compatibility tests. |
| Lag-linear model | `deprecated/v0p9/src/models/training.py`, `deprecated/v0p9/src/models/market_baselines.py` | rewrite | v1p0 first slice only needs a narrow fixed baseline and saved-prediction schema. | Fold-local preprocessing and schema tests. |
| Fixed XGBoost model | no active v1p0 module; v0p9 uses sklearn market baselines | rewrite | Required venv `~/venvs/ai` provides `xgboost`; active code should still block honestly if dependency is absent elsewhere. | Dependency-aware test must either fit or block honestly. |
| Diagnostics and reporting | `deprecated/v0p9/src/evaluation/`, `deprecated/v0p9/src/stage10/` | rewrite | v1p0 diagnostics require first-slice caveats, strata, uncertainty, and report-fidelity checks. | Metric, strata, CI, and report tests. |

## Non-Claims

- This audit does not validate v0p9 code as v1p0-compatible.
- This audit does not move or reactivate archived code.
- Conceptual reuse does not count as code reuse.

## Result

Proceed with a minimal active v1p0 implementation under `src/event_state_forecasting/v1p0/`, with focused tests under `tests/v1p0/` and versioned configs under `configs/`.
