# Prompts

Status: active prompt archive for root-level prompt artifacts moved out of the repository root.

This folder contains reusable execution prompts, DeepResearch topic prompts, and guidebook/scaffold prompts. Prompt files are documentation artifacts only unless a stage-specific approval and execution record says otherwise.

Current v1p0 prompt execution/rerun status is tracked in `docs/Prompts/v1p0_Prompt_Status_Register.md`.

## v1p0 First-Slice Prompts

- `v1p0_Stage00_Governance_Context_Readiness.md` through `v1p0_Stage14_Integrated_Evidence_Review.md` mirror the active `ExecutionFlow.md` v1p0 first-slice plan.
- These prompts define objectives, inputs, outputs, smoke tests, completion criteria, and non-claims for future stage execution.
- Prompt existence does not mean code, configs, artifacts, benchmarks, reports, or approval gates have been executed.

## v1p0 Full-Implementation Prompts

- `v1p0_Stage15_Full_Run_Governance_And_Result_Vault.md` through `v1p0_Stage40_V1p0_Completion_And_Next_Scope_Gate.md` extend the first-slice plan into the remaining full v1p0 implementation plan.
- These prompts cover full-run governance, historical artifact compatibility, production feature sidecars, sequence windows, full historical baselines, XGBoost nested Optuna tuning, overfit-frontier review, block-bootstrap uncertainty, FinBERT cache and ablations, TSMixer, ensembles, market-event fusion, full diagnostics, report fidelity, documentation consistency, final claim review, and completion gating.
- They are planning prompts only. They do not execute code, train models, run benchmarks, create positive claims, call providers, mutate raw data, reinterpret Stage 6, or approve product/trading scope.
- Future execution must record results under `data/v1p0_full_results/` and preserve `benchmark_claim=false` until Stage 39 evidence and approvals allow different language.
- Stage 16 through Stage 40 prompts were hardened after audit to require explicit truth-source resolution from `ArchitecturalDesignDecisions.md` and `docs/NextSteps_Brainstorming.md`, stage-specific inputs/outputs, success measurements, cascade handling, tests, and mandatory block-and-ask behavior for unresolved decisions.
- Silent deferral is not valid for critical branches. If a prerequisite, compute budget, evidence artifact, decision, or downstream effect is unclear, the executor must stop and ask the user before continuing.
