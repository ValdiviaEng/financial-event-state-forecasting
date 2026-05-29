# Project Definition

Status: active v1p0 project definition and XGBoost-only branch baseline

Updated: 2026-05-27

Primary sources: `AgentRules.md`, `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, `UsageManual.md`, `ExecutionPipeline.md`, current validated repository state, and the owner-approved v1p0 naming and XGBoost-only branch decisions.

## 1. Purpose

The active project is a local, artifact-driven financial event-state forecasting research system. The active implementation version is `v1p0`.

The long-running project objective remains testing whether aligned firm-news event-state information adds predictive value beyond market-only baselines for end-of-day, multi-horizon forward excess-return forecasting.

The current execution branch is narrower: close the strongest evidenced market-only model path around `market_xgboost_v2_frozen_final` before any further event/fusion, TSMixer, service, live forecast, or trading scope is reopened. This branch is XGBoost-only and non-claiming unless later evidence and approvals change that status.

`v1p0` components become implemented truth only when code, configs, artifacts, tests, validation records, and non-claim language exist for that component. Planned or historical components remain non-authoritative for active execution until revalidated under the current branch.

## 2. Authority And Source Basis

| Source | Role |
| --- | --- |
| `AgentRules.md` | Binding governance constitution and approval gates. Do not edit without explicit approval. |
| `docs/agent/AgentMemory.md` | Binding memory and event-ledger procedure. Do not edit without explicit approval. |
| `docs/agent/agent_log/Current_State.md` | Current operational memory, blockers, and active evidence pointers. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Append-only request, task, evidence, and reconciliation ledger. |
| `ArchitecturalDesignDecisions.md` | Active v1p0 architectural decision consolidation. |
| `docs/NextSteps_Brainstorming.md` | Retained v1p0 decision-history source; superseded by later implemented evidence where conflicts exist. |
| `ResearchTruth.md` | Current implemented/research truth and non-claims. |
| `Architecture_Map.md` | Active v1p0 architecture map and file-flow plan. |
| `ExecutionPipeline.md` | Current zero-to-benchmark execution sequence and approval gates. |
| `UsageManual.md` | Validated local v1p0 command and artifact usage reference. |
| `Complete_guidebook.txt` | Detailed v1p0 guidebook and intended implementation flow. |
| `deprecated/v0p9/docs/ScopeDecisionLog.md` | Preserved historical owner-approved decision log after manual deprecation. |
| `deprecated/v0p9/docs/ScopeDefinition.md` | Preserved older scope framing and contradiction inventory after manual deprecation. |

If this file conflicts with `AgentRules.md`, `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, or explicit owner approvals in the ledger, the higher-authority source wins and this file must be fixed.

## 3. Version Naming

The current implementation version is `v1p0` in plans, folders, manifests, docs, candidate artifact families, and validation records.

Do not relabel v0p9 artifacts as v1p0. v0p9 remains historical/completed state. Deprecated v0p9 docs and code live under `deprecated/v0p9/` where already preserved or manually moved by the user. The older root archive has been normalized to `deprecated/v0p7/`.

## 4. Current Repository State

The repository contains a completed historical v0p9 research state with materialized Stage 2 through Stage 6 benchmark artifacts, Stage 7C diagnostics, Stage 8 plan-first update tooling, and Stage 10C historical-prediction packet generation. Those artifacts remain implemented truth for v0p9 only unless explicitly reused through v1p0 compatibility gates.

The historical Stage 6 result remains `clean_null` and `limitation_bearing`. It must not be reinterpreted as positive, live, trading-relevant, or benchmark-comparable to future variants without explicit approval and comparability review.

The active v1p0 implementation has validated smoke commands, market feature sidecars, fixed market baselines, XGBoost search/frozen-final artifacts, XGBoost overfit review, and XGBoost block-bootstrap uncertainty evidence through Stage 25.

The current active model candidate is `market_xgboost_v2_frozen_final`. Stage 24 classifies it as `lockbox_reported_candidate` with promotion review recommended, and Stage 25 records supportive non-claiming uncertainty. `positive_claim_approved=false` remains in force.

TSMixer evidence from Stage 18, Stage 30, Stage 31, and Stage 32 is historical diagnostic/rejection evidence for the current branch. The user selected an XGBoost-only path after Stage 31-32 and ad-hoc diagnostics, so TSMixer is not an active model input.

Stage 33 XGBoost+TSMixer ensemble and Stage 34 market-event fusion are cancelled for the current branch. Existing Stage 34 fusion remains historical `exploratory_only` evidence and must not feed the active XGBoost-only final review unless the user reopens that scope.

Older Stage 35 through Stage 40 packets remain historical non-claiming closeout evidence. A refreshed XGBoost-only Stage 35-40 closeout centered on Stage 21-25 evidence now exists for the active branch, with `positive_claim_approved=false` and `benchmark_comparability_promotion_approved=false` still in force.

## 5. v1p0 Objective

The v1p0 objective is to create a small, versioned, credible first implementation slice that strengthens market baselines and diagnostics while preserving leakage control, saved-prediction evaluation, explicit non-claims, artifact provenance, and benchmark comparability discipline.

The current XGBoost-only branch addresses the main near-term risk: the need for a stronger, better-diagnosed market-only hurdle before event-state or fusion claims are revisited. It should not expand into live forecasting, services, dashboards, trading signals, provider expansion, or broader architecture exploration.

The current branch-local closeout is complete as a non-claiming XGBoost-only packet around `market_xgboost_v2_frozen_final`, without consuming TSMixer, XGBoost+TSMixer ensemble, or market-event fusion as active candidates.

## 6. Protected Scientific Scope

| Area | Active definition |
| --- | --- |
| Mode | Local CLI/artifact-driven research system. |
| Objective | Test event-state incremental value beyond market-only baselines, with current branch closing the XGBoost-only market hurdle first. |
| Prediction frequency | End-of-day. |
| Target family | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| First benchmark universe | Reproducible top-50 liquid large-cap universe. |
| Market provider | Twelve Data. |
| News provider | Alpha Vantage. |
| Static/company support | SEC context only; static company metadata remains deferred unless approved. |
| News alignment | Same-day as-of-close, with after-hours and non-trading-day news rolled forward. |
| No-news policy | Keep rows and encode explicit empty event states plus no-news indicators. |
| Evaluation | Purged-plus-embargoed walk-forward development evaluation plus final untouched lockbox. |
| Claim basis | Saved out-of-sample predictions, manifests, diagnostics, and comparison summaries. |
| Current branch candidate | `market_xgboost_v2_frozen_final`. |
| Current branch claim status | Non-claiming; `positive_claim_approved=false`. |

## 7. Active v1p0 Evidence Map

| Stage or area | Current status | Active meaning |
| --- | --- | --- |
| Stages 00-14 | Smoke implemented | Toy-data first-slice evidence only. |
| Stage 15 | Completed current | Result-vault naming and metadata contract evidence. |
| Stage 16 | Completed/pre-hardening reviewed | Historical Stage 2-6 compatibility gate for v1p0. |
| Stage 17 | Completed/pre-hardening reviewed | Market lag/rolling feature sidecars. |
| Stage 18 | Completed current | Sequence tensors exist, but not active for the XGBoost-only branch. |
| Stage 19 | Completed/pre-hardening reviewed | Lag-linear and fixed-XGBoost saved predictions. |
| Stage 20 | Completed/pre-hardening reviewed | Diagnostic baseline gate. |
| Stage 21 | Completed/pre-hardening reviewed | XGBoost search-space and objective freeze. |
| Stage 22 | Completed/pre-hardening reviewed | Development-only XGBoost search; lockbox not used for selection. |
| Stage 23 | Completed/pre-hardening reviewed | Frozen-final XGBoost evaluation for `market_xgboost_v2_frozen_final`. |
| Stage 24 | Completed/pre-hardening reviewed | XGBoost overfit-frontier and conservative promotion review. |
| Stage 25 | Completed/pre-hardening reviewed | Block-bootstrap uncertainty and overfit-pressure review. |
| Stages 26-29 | Historical/non-active for branch | FinBERT contract/cache/aggregation/event representation evidence; not active for XGBoost-only closeout. |
| Stages 30-32 | Historical rejection evidence | TSMixer smoke/fixed/optimized evidence; tuned TSMixer rejected. |
| Stage 33 | Cancelled current branch | XGBoost+TSMixer ensemble is not active. |
| Stage 34 | Cancelled current branch | Market-event fusion is not active; old packet is `exploratory_only`. |
| Stages 35-40 | Completed current | Refreshed XGBoost-only closeout; positive claim and comparability promotion remain unapproved. |

## 8. v1p0 Non-Implementation Boundary

This definition does not claim that every v1p0 component exists. A v1p0 component becomes implemented truth only after all of the following exist:

| Requirement | Evidence needed |
| --- | --- |
| Code or config | Active file paths, reviewed imports, and no accidental dependence on deprecated code. |
| Artifact contract | Versioned output roots, schemas, manifests, and provenance fields. |
| Tests | Focused unit/contract tests and any required validators. |
| Execution evidence | Command output or validation summary recorded in memory. |
| Non-claims | Explicit limitations and comparability status. |
| Memory | `Current_State.md` and `Event_Ledger.ndjson` updated with evidence pointers. |

Historical, exploratory, rejected, stale, or cancelled artifacts must not be promoted into active branch inputs without an explicit branch decision and updated validation.

## 9. Out Of Scope For The Current Branch

| Item | Status |
| --- | --- |
| Live provider calls | Not approved. |
| Raw overwrites or hidden data mutation | Not approved. |
| Hidden Stage 2 through Stage 6 reruns | Not approved. |
| Stage 6 reinterpretation | Not approved. |
| Positive benchmark-improvement language | Not approved. |
| Benchmark-comparability promotion | Not approved. |
| TSMixer as active model input | Closed for current branch unless explicitly reopened. |
| XGBoost+TSMixer ensemble | Cancelled for current branch unless explicitly reopened. |
| Market-event fusion as active closeout input | Cancelled for current branch unless explicitly reopened. |
| Persisted inference package | Deferred and approval-gated. |
| New `forecast_candidate` semantics | Deferred and approval-gated. |
| Service/API/dashboard | Deferred/rejected for current phase. |
| Trading signals, buy/sell outputs, price targets, portfolio advice | Not approved. |
| LLM summaries | Rejected for first implementation. |
| Provider expansion | Deferred. |
| Relabeling v0p9 artifacts as v1p0 | Forbidden. |

## 10. Execution References

Use `ExecutionPipeline.md` for the ordered zero-to-benchmark command flow:

| Execution need | Primary reference |
| --- | --- |
| Environment setup | `ExecutionPipeline.md` Section 4. |
| Raw artifact audit and update planning | `ExecutionPipeline.md` Section 5. |
| Stage 2 local dataset creation | `ExecutionPipeline.md` Section 5.3. |
| Stage 3 preprocessing and labels | `ExecutionPipeline.md` Section 6. |
| Stage 4 split/packet preparation | `ExecutionPipeline.md` Section 6. |
| Stage 5 historical model training | `ExecutionPipeline.md` Section 7. |
| Stage 6 historical benchmark reporting | `ExecutionPipeline.md` Section 7. |
| Active v1p0 XGBoost training/evaluation | `ExecutionPipeline.md` Section 8. |
| Command inventory and artifact roots | `UsageManual.md`. |

## 11. Approval Gates

Explicit approval remains required before changing target family, horizon set, provider stack, universe, alignment policy, evaluation protocol, comparator ladder, benchmark comparability, live-provider behavior, raw overwrite policy, output status, trading semantics, or governance files.

Edits to `AgentRules.md` or `docs/agent/Agent*.md` require explicit user approval.

## 12. Maintenance Rule

Update this file whenever the active v1p0 branch, implementation evidence, protected-scope decisions, execution path, or active truth files change materially. Do not use this file to bypass approval gates or claim implementation before validated artifacts exist.
