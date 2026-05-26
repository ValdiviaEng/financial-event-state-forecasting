# Architecture Map

Status: active v1p0 architecture map

Updated: 2026-05-24

This map defines the v1p0 documentation, code, artifact, and validation layout. The first-slice smoke implementation and Stage 15-23 full-v1p0/XGBoost artifacts exist where recorded; later full-v1p0 stages remain prompt-planned until future execution evidence exists. v0p9 artifacts remain historical and must not be relabeled as v1p0.

## 1. Architecture Principles

| Principle | Decision |
| --- | --- |
| Version name | The next implementation version is `v1p0`. |
| Implementation state | v1p0 first-slice smoke code/configs/tests/artifacts and Stage 15-23 result-vault/config/search/final-evaluation artifacts exist; later full-v1p0 stages remain unimplemented until they have code, configs, artifacts, tests, and validation evidence. |
| First slice | Prioritize market lag features, sidecar registry, `market_lag_linear_v1`, `market_xgboost_v1_fixed`, diagnostics core, strata, and Stage 10C clarity. |
| Artifact discipline | All new outputs must be versioned and manifest-backed. |
| Deprecated boundary | `deprecated/v0p9/` and `deprecated/v0p7/` are reference-only. |
| Approval gates | No live provider calls, raw overwrites, Stage 6 reinterpretation, service/API/dashboard, trading outputs, or comparability promotion without explicit approval. |

## 2. v1p0 Folder And File Map

| Path | Purpose and intent | Objectives | Expected inputs | Expected outputs | Data/artifact types | Dependencies | Owner stage/prompt | Validation or smoke test expectation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `ProjectDefinition.md` | Broad v1p0 project definition. | Define scope, non-claims, first-slice boundary, and naming. | `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, operational memory. | Updated project truth summary. | Markdown truth/design doc. | Governance rules and owner approvals. | Sanitization stage. | Manual review plus governance validation. |
| `ArchitecturalDesignDecisions.md` | Active v1p0 architectural decision consolidation. | Preserve decisions and reconciliation notes. | `docs/NextSteps_Brainstorming.md`, plus preserved deprecated copies of `ScopeDecisionLog.md` and `ScopeDefinition.md`. | v1p0 design truth. | Markdown decision artifact. | Source priority rules. | Manual review plus memory logging. |
| `Architecture_Map.md` | Root architecture map. | Map folders/files, expected flow, owners, and validation. | v1p0 project definition and decisions. | Active architecture map. | Markdown architecture doc. | `ProjectDefinition.md`. | Manual review; references updated after move. |
| `UsageManual.md` | Local usage manual for validated v1p0 smoke paths. | Document only real v1p0 commands and preserve non-claims. | Validated v1p0 smoke command evidence. | Safe command catalog. | Markdown manual. | `ProjectDefinition.md`, validation output. | Ensure no benchmark/trading/live claims. |
| `Complete_guidebook.txt` | Detailed v1p0 repository guidebook. | Describe file connections and intended implementation flow. | Architecture map, project definition, decisions. | Detailed guidebook. | Text/Markdown guide. | `Architecture_Map.md`. | Manual review plus grep for stale architecture path. |
| `ResearchTruth.md` | Implemented and research truth. | Preserve v0p9 implemented truth and v1p0 non-claims. | Validated artifact evidence and decisions. | Truth table/addenda. | Markdown truth doc. | Governance and evidence. | Only update with evidence-backed statements. |
| `docs/NextSteps_Brainstorming.md` | Important retained v1p0 decision-history source. | Preserve detailed brainstorming and roadmap history. | Prior manual research and decisions. | Retained decision-history doc. | Markdown decision log. | User instruction to keep active in `docs/`. | No move by agent. |
| `deprecated/v0p9/docs/ScopeDecisionLog.md` | Preserved owner decision log. | Preserve protected-scope history after manual deprecation. | Historical approvals. | Deprecated historical decision source. | Markdown decision log. | User manual deprecation. | Reference only; active planning uses `ArchitecturalDesignDecisions.md`. |
| `deprecated/v0p9/docs/ScopeDefinition.md` | Preserved older decision questionnaire. | Preserve stale/resolved context after manual deprecation. | Restart-era scope evidence. | Deprecated historical scope source. | Markdown scope ledger. | User manual deprecation. | Reference only; active planning uses `ArchitecturalDesignDecisions.md`. |
| `docs/` | Supporting documentation area. | Hold theory, testing, execution, prompts, research, and operational docs not promoted to root. | Active decisions and validated state. | Supporting docs. | Markdown docs. | Root truth files. | Stale docs must be preserved before removal. |
| `docs/Prompts/` | Prompt archive. | Preserve stage prompts and future prompt workflows. | Historical prompts and v1p0 prompt updates. | Prompt files. | Markdown prompt artifacts. | Active truth files. | Prompt files do not approve implementation. |
| `docs/Prompts/v1p0_Stage00_*.md` through `docs/Prompts/v1p0_Stage14_*.md` | v1p0 first-slice execution prompt suite. | Provide stage-by-stage execution contracts, inputs, outputs, tests, completion criteria, and non-claims. | `ExecutionFlow.md`, `ArchitecturalDesignDecisions.md`, strategy docs, active truth docs. | Prompt instructions for future execution. | Markdown prompt artifacts. | v1p0 strategy and execution-flow docs. | Stage 00 through Stage 14. | Prompts are planning artifacts only until executed with evidence. |
| `docs/Prompts/v1p0_Stage15_*.md` through `docs/Prompts/v1p0_Stage40_*.md` | v1p0 full-implementation prompt suite. | Plan remaining serious benchmark, tuning, diagnostics, overfit-frontier, FinBERT, TSMixer, ensembles, fusion, reporting, and claim-review stages. | `ExecutionFlow.md`, `docs/NextSteps_Brainstorming.md`, `ArchitecturalDesignDecisions.md`, strategy docs. | Prompt instructions for future execution. | Markdown prompt artifacts. | First-slice evidence and active truth stack. | Stage 15 through Stage 40. | Prompt existence is not implementation or benchmark evidence. |
| `docs/v1p0_first_slice/` | v1p0 first-slice execution evidence notes. | Record audit and integrated smoke evidence without promoting benchmark claims. | Stage prompt outputs and validation results. | Stage evidence Markdown files. | Markdown evidence docs. | `ExecutionFlow.md`, tests, smoke script. | Stage 01 and Stage 14. | Evidence notes must cite tests and blockers. |
| `docs/v1p0_first_slice/Stage_Completion_Register.md` | v1p0 per-stage completion register. | Mark Stage 00 through Stage 14 completion based on current evidence. | Stage prompts, tests, smoke script, memory. | Detailed completion matrix. | Markdown evidence doc. | `docs/v1p0_first_slice/Stage14_Evidence_Review.md`. | Must preserve non-claims. |
| `docs/v1p0_final_sprint/Final_v1p0_Sprint_Report.md` | v1p0 final-sprint evidence record. | Record ordered testing, benchmarking, diagnostics, report fidelity, visualization readiness, documentation consistency, and prompt status. | v1p0 tests, smoke artifacts, docs, memory. | Final sprint report. | Markdown evidence doc. | Stage register, smoke script, tests. | Must not promote positive benchmark claims. |
| `docs/research/` | Manual research archive. | Preserve research synthesis and external/manual investigation outputs. | Manual research files. | Research archive. | Markdown/PDF/notes as applicable. | Research workflow rules. | Research support only; no final approvals. |
| `docs/research_results/` | Prior research result notes. | Preserve historical research memos and comparisons. | Stage research outputs. | Research memos. | Markdown research docs. | `ResearchTruth.md`. | Do not treat as implementation truth. |
| `docs/agent/` | Governance appendices. | Preserve agent governance and memory rules. | Governance docs. | Binding appendices. | Markdown governance docs. | Explicit user approval required for edits. | Governance validator. |
| `docs/agent/agent_log/` | Operational memory and event ledger. | Track requests, tasks, evidence, blockers, and stale-risk. | Agent actions and validation evidence. | `Current_State.md`, `Event_Ledger.ndjson`. | Markdown and NDJSON. | `docs/agent/AgentMemory.md`. | Governance validator and JSONL parse. |
| `src/event_state_forecasting/v1p0/` | Active v1p0 first-slice and XGBoost-search helper package. | Implement versioning, registry, market lag features, lag-linear modeling, fixed XGBoost smoke modeling, diagnostics, strata, uncertainty, static reporting, frozen XGBoost search-objective helpers, and Stage 22 ledger/prediction contract helpers. | v1p0 configs and toy/smoke/search frames. | Python helpers. | Python code. | `configs/*_v1p0.yaml`, tests, required venv `~/venvs/ai`. | Stages 02-13 smoke execution and Stage 21-22 search validation. | `source ~/venvs/ai/bin/activate && python -m pytest tests/v1p0`. |
| `configs/` | v1p0 config root plus historical configs. | Hold versioned component and run configs. | v1p0 manifests and model/feature decisions. | YAML/JSON configs. | Config artifacts. | Source modules and validators. | Schema/contract tests before use. |
| `tests/v1p0/` | v1p0 smoke-test root. | Hold focused tests for new v1p0 behavior. | Code/config contracts. | Unit, contract, smoke, and validation tests. | Python test files. | Source modules and fixtures. | Tests must pass before implementation claims. |
| `scripts/run_v1p0_first_slice_smoke.py` | v1p0 local smoke command. | Generate toy-data first-slice outputs with non-claim summary. | v1p0 configs and source modules. | Smoke CSV/HTML/JSON outputs. | Python script. | `src/event_state_forecasting/v1p0/`. | No live calls; no raw writes. |
| `data/raw/` | Historical and future raw-data area. | Preserve raw inputs and provider limitations. | Provider payloads and manifests. | Raw files and summaries. | CSV, JSON, Parquet, ledgers. | Provider approval gates. | No raw overwrite or live call without approval. |
| `data/manifests/` | Manifest evidence area. | Store version, provenance, validation, and run records. | v1p0 commands and validators. | JSON manifests. | JSON. | Artifact-producing stages. | Manifest schema checks. |
| `data/features/` | Future v1p0 feature sidecar outputs. | Store market lag/rolling and later event/text features. | Stage 2/3 style inputs and configs. | Versioned feature artifacts. | Parquet plus manifests. | Feature registry. | Row identity and leakage checks. |
| `data/models/` | Future v1p0 model outputs. | Store saved predictions, model manifests, preprocessing records. | Feature artifacts, splits, configs. | Prediction artifacts and model records. | Parquet/JSON. | Split and feature artifacts. | Saved-prediction and fold-local checks. |
| `data/benchmark_runs/` | Future v1p0 evaluation outputs. | Store metrics, diagnostics, strata, uncertainty, and summaries. | Saved predictions and labels. | Benchmark-report packets. | Parquet/CSV/JSON/HTML. | Model outputs and validators. | Comparability and diagnostic checks. |
| `data/prediction_outputs/` | Future output packet area if approved. | Store local readable outputs only after output semantics are approved. | Saved predictions or future approved inference package. | Static packets and reports. | CSV/Parquet/HTML/JSON. | Stage 10C-style contracts. | Non-claim and fidelity tests. |
| `data/v1p0_first_slice_smoke/` | v1p0 smoke artifact area. | Store toy-data outputs from the first-slice smoke command. | `scripts/run_v1p0_first_slice_smoke.py`. | Smoke features, predictions, diagnostics, report, and summary. | CSV/HTML/JSON. | v1p0 configs and modules. | Not benchmark evidence. |
| `data/v1p0_full_results/` | Full-v1p0 result-vault area. | Store executed Stage 15-21 packets and future experiment, tuning, benchmark, diagnostic, runtime, and overfit-frontier result packets. | Stage 15 through Stage 40 runs. | Run manifests, hyperparameters/search spaces, metrics, diagnostics, uncertainty, reports, logs. | JSON/CSV/Parquet/HTML/logs. | `ExecutionFlow.md`, full prompt suite. | Each packet must carry non-claims; no result claim from folder existence. |
| `runs/logs/` | Runtime log area. | Hold local run logs and command evidence. | Script/CLI runs. | Logs. | Text logs. | Scripts and CLIs. | Must not expose secrets in shared artifacts. |
| `deprecated/v0p9/` | v0p9 archive. | Preserve superseded docs/code without relabeling. | v0p9 files. | Reference-only archive. | Mixed docs/code/data snapshots. | User-approved/manual moves. | Not active truth. |
| `deprecated/v0p7/` | older archive. | Preserve older historical snapshot. | Legacy archive content. | Reference-only archive. | Mixed historical files. | Normalized archive layout. | Not active truth. |

## 3. Intended v1p0 Flow

| Step | Flow | Inputs | Outputs | Validation |
| --- | --- | --- | --- | --- |
| 1 | Sanitize active docs. | Current docs and v1p0 decisions. | Consistent project definition, architecture map, usage skeleton, guidebook. | Governance validator, ledger parse, manual path grep. |
| 2 | Freeze v1p0 naming. | Owner instruction. | `v1p0` names in plans/manifests/docs. | No relabeling of v0p9 artifacts. |
| 3 | Define first-slice manifests. | `ArchitecturalDesignDecisions.md`. | Version manifest and feature registry design. | Schema review before code. |
| 4 | Define market feature sidecars. | Existing benchmark row contracts and market data. | Lag/rolling sidecar contract. | Row identity, leakage, and horizon checks. |
| 5 | Implement first market baselines. | Feature sidecars, splits, configs. | `market_lag_linear_v1`, `market_xgboost_v1_fixed` predictions. | Saved-prediction and fold-local preprocessing tests. |
| 6 | Add diagnostics core. | Predictions, labels, strata flags. | Train-gap where available, strata, uncertainty evidence. | Diagnostic validators. |
| 7 | Improve Stage 10C clarity. | Existing packet lessons and v1p0 outputs when available. | Caveated reports and fidelity tests. | Report/data consistency tests. |
| 8 | Execute full-v1p0 prompt plan only after approval. | First-slice evidence and Stage 15 result-vault contract. | Serious run artifacts under `data/v1p0_full_results/`. | Stage 15-40 tests, diagnostics, overfit review, and claim review. |

## 4. Dependency Direction

| Higher layer | Constrains |
| --- | --- |
| Governance docs | All task behavior and approval gates. |
| `ArchitecturalDesignDecisions.md` | v1p0 architecture and first-slice choices. |
| `ProjectDefinition.md` | Scope, non-claims, and naming. |
| `Architecture_Map.md` | File and folder responsibilities. |
| `Complete_guidebook.txt` | Detailed implementation flow and file connections. |
| `ExecutionFlow.md` | Ordered v1p0 first-slice and full-implementation prompt plan. |
| `docs/Prompts/v1p0_Stage00_*.md` through `docs/Prompts/v1p0_Stage14_*.md` | Per-stage execution instructions; no implementation claim by themselves. |
| `docs/Prompts/v1p0_Stage15_*.md` through `docs/Prompts/v1p0_Stage40_*.md` | Full-v1p0 future execution prompts; no implementation claim by themselves. |
| Configs | Code behavior only after configs are active and tested. |
| Tests and validators | Implementation claims. |
| Artifacts and manifests | Result claims. |

## 5. Completion Rule

No v1p0 component is implemented merely because it appears in this map. Implementation requires code/configs, artifacts where applicable, tests, validation output, and memory updates.
