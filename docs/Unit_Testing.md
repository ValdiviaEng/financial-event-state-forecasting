# Unit Testing

Status: active-root unit-testing map. Focused executable tests now exist for approved Stage 2 through Stage 8 paths/claims plus Stage 10C prediction-output packet claims; remaining provider/utility/expansion tests remain comment-only scaffolds.

Governing refinement: `docs/Data_Separation_And_Overfitting_Control.md` defines the Option B data-separation and overfitting-control contract that future executable tests must enforce.

## Current State

- Active Python under `src/`, `scripts/`, and `tests/` compiles successfully in the latest Stage 10C validation pass.
- Active validators exist for governance, scaffold status, Stage 0-1, Stage 2, Stage 3, Stage 4, Stage 5, Stage 6, Stage 7, and Stage 10C completion.
- `tests/` contains executable Stage 2 through Stage 8 contract/update tests, executable Stage 10C packet tests, and comment-only planned tests for remaining provider/utility/expansion modules.
- Active Stage 6 metric contract tests exist at `tests/evaluation/test_metric_contracts.py`.
- Active Stage 8 raw-update script tests exist at `tests/ops/test_stage8_data_update_contract.py`.
- Active Stage 10C prediction-output packet tests exist at `tests/stage10/test_prediction_outputs_contract.py`.

## Remaining Future Unit Test Areas

- Provider, utility, and expansion-family scaffolds that remain comment-only.
- Any new feature/model branch approved after Stage 6.
- Any future one-command orchestration layer if explicitly approved.
- Any provider-ledger sanitization implementation if converted from scaffold to active code.

## Minimum Acceptance Rule

Any new active `src/` module must have file-level tests or a documented pending-test reason before its stage can be marked complete.

Current Stage 2 through Stage 8 and Stage 10C tests satisfy focused executable coverage for their approved stage claims only. Remaining comment-only tests record planned invariants for future work.
