# v1p0 Stage 30 Prompt: TSMixer Sequence Dataset And Smoke

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Implement the pure PyTorch TSMixer dataset/model smoke path using Stage 18 sequence-window artifacts. This stage proves only that the validated sequence tensors and minimal model can run; it must not replace Stage 31 multiseed benchmark evidence.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for pure PyTorch TSMixer, standalone-first strategy, and deferred-contract limits.
- Read `docs/NextSteps_Brainstorming.md` Decisions 31 and 32 for TSMixer library and strategy decisions.
- Read Stage 18 sequence-window artifacts, `LearningStrategy.md`, and `BenchmarkingStrategy.md`.
- If Stage 18 tensors are missing or smoke scope is unclear, ask the user before running; do not improvise from tabular data.

## Required Inputs

- Stage 18 validated sequence-window tensors and manifest.
- Stage 4 fold/split metadata and Stage 3 labels.
- Fixed smoke architecture/config, seed, batch size, and runtime budget.
- PyTorch runtime environment details.

## Methodology

- Define a minimal pure PyTorch TSMixer architecture and fixed smoke parameters.
- Load Stage 18 tensors by fold without future leakage and verify tensor shape against the manifest.
- Run tiny training only after dataset shape, forward-pass, and deterministic seed tests exist.
- Save smoke predictions, loss trace, runtime, parameter count, seed, device, and failure modes.
- Do not evaluate full benchmark performance or tune hyperparameters in this stage.

## Required Outputs

- Smoke prediction packet and smoke manifest.
- Dataset/model validation report with shape checks, forward pass, seed, runtime, and parameter count.
- Clear statement that Stage 31 remains required for fixed multiseed benchmark evidence.

## Success Measurements

- Smoke data comes from Stage 18 tensors, not a substitute tabular frame.
- Forward pass, tiny training, deterministic seed, and saved-prediction schema checks pass.
- Runtime and parameter count are recorded.
- Failure modes are explicit if smoke does not run.

## Blocking And User Questions

- Block and ask if Stage 18 tensors do not exist, sequence shapes mismatch, PyTorch is unavailable, memory/runtime budget is insufficient, or smoke config is unclear.
- Block and ask before substituting tabular data, reducing tensor coverage, changing model family, or recording smoke-only evidence as a benchmark.
- Do not continue to Stage 31 unless Stage 30 smoke passes or the user explicitly resolves the failure.

## Cascade Handling

- Stage 30 validates the path into Stage 31 but does not satisfy Stage 31 evidence requirements.
- If Stage 30 is blocked, Stage 31 through Stage 33 are blocked.
- If Stage 18 tensors change, Stage 30 must be rerun before Stage 31.

## Required Tests And Validation

- Dataset shape and dtype tests.
- Model forward-pass tests.
- Fold-local normalization consistency tests.
- Deterministic seed tests.
- Tiny training smoke and saved-prediction schema tests.

## Completion Criteria

- TSMixer smoke path is stable on Stage 18 tensors and ready for fixed multiseed historical evaluation.
- Any inability to run smoke is a blocker that requires user resolution.

## Non-Claims

TSMixer smoke success is not benchmark evidence, model promotion evidence, Stage 6 reinterpretation, or trading value.
