# v1p0 Stage 31 Prompt: TSMixer Fixed Multiseed Benchmark

Status: see `docs/Prompts/v1p0_Prompt_Status_Register.md`; prompt text is the current execution spec and stage status is tracked centrally.

## Objective

Evaluate `market_tsmixer_v1` with fixed parameters and multiple seeds on the validated Stage 18 sequence tensors before any TSMixer optimization. This is a critical benchmark stage and must not be silently deferred by the agent.

## Core Truth Sources

- Read `ArchitecturalDesignDecisions.md` for pure PyTorch TSMixer, standalone-first strategy, and the rule that nested optimization occurs only after promising standalone evidence.
- Read `docs/NextSteps_Brainstorming.md` Decisions 31 and 32, especially the selected path: smoke/default tiny parameters, fixed/multiseed discipline, then nested optimization only if evidence shows promise.
- Read Stage 18 sequence-window artifacts, Stage 30 smoke evidence, `BenchmarkingStrategy.md`, and `LearningStrategy.md`.
- If compute budget, number of seeds, fixed config, or success threshold is not found in the truth files or prior manifests, ask the user before running or deferring.

## Required Inputs

- Stage 18 validated sequence tensors and manifest.
- Stage 30 successful smoke manifest.
- Fixed TSMixer architecture/config, seed list, training epochs, early-stop policy, batch size, optimizer, and runtime budget.
- Stage 4 folds/split roles and Stage 3 labels.
- Hurdle metrics from Stage 19 and/or Stage 23 for later comparison.

## Methodology

- Freeze the fixed TSMixer config before historical evaluation.
- Train across approved development folds and multiple seeds using fold-local preprocessing/normalization only.
- Save train predictions for diagnostics, validation predictions for development evidence, and final/lockbox predictions only after the fixed config is frozen and without using lockbox to alter the model.
- Record seed-level metrics, fold metrics, runtime, device, parameter count, convergence/failure notes, and saved-prediction digests.
- Compare against the appropriate market hurdle without weakening the hurdle or selecting seeds from lockbox outcomes.

## Required Outputs

- Seed-level saved predictions and metrics for `market_tsmixer_v1_fixed_multiseed` or equivalent approved ID.
- Fixed config manifest, model-fit manifest, seed ledger, runtime/compute report, and blocker ledger if failures occur.
- Stage 31 report deciding whether evidence is promising enough to ask about Stage 32 optimization.

## Success Measurements

- Every approved seed/fold/horizon/split-role combination has predictions or an explicit failure record.
- Multiseed dispersion, median/mean performance, worst-seed behavior, train-validation gaps, and runtime are measured.
- Seed selection and model config are independent of lockbox feedback.
- Evidence is sufficient to classify Stage 32 as `ask_user_for_optimization`, `do_not_optimize`, or `blocked`.

## Blocking And User Questions

- Block and ask if Stage 18 tensors are missing, Stage 30 smoke failed, seed count/budget is unclear, fixed config is missing, PyTorch/GPU resources are insufficient, or full historical multiseed execution cannot complete.
- Block and ask before deferring Stage 31, reducing seed count, reducing horizons, shortening the historical window, changing architecture, changing optimizer, or continuing to Stage 32/33 without multiseed evidence.
- The agent must never write a Stage 31 deferred record and continue execution unless the user explicitly chooses that deferral after being told the downstream impact.

## Cascade Handling

- Stage 31 evidence is a hard prerequisite for Stage 32 TSMixer optimization and Stage 33 XGB+TSMixer ensemble.
- If Stage 31 is blocked or user-deferred, Stage 32 and Stage 33 are blocked unless the user explicitly approves a narrower downstream path.
- Stage 35 through Stage 40 must report Stage 31 status accurately and must not treat missing TSMixer evidence as completed benchmark evidence.

## Required Tests And Validation

- Multiseed manifest and seed-ledger tests.
- Saved-prediction schema and row-coverage tests.
- Seed reproducibility tests.
- No-lockbox-tuning tests.
- Runtime/resource and failure-recording tests.

## Completion Criteria

- TSMixer standalone evidence is sufficient to decide whether nested optimization is justified, or the user has resolved a blocker explicitly.
- Silent deferral is not a valid completion state.

## Non-Claims

Multiseed evidence must pass Stage 35 through Stage 39 before any positive claim, comparability promotion, Stage 6 reinterpretation, or trading use.
