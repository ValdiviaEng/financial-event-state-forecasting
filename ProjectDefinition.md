# Project Definition

Status: active v1p0 project definition and sanitization baseline

Updated: 2026-05-24

Primary sources: `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, current validated repository state, and the owner-approved v1p0 naming decision.

## 1. Purpose

The active project is a local, artifact-driven financial event-state forecasting research system. The next implementation version is `v1p0`.

`v1p0` is a versioned implementation path focused on improving performance and credibility while preserving benchmark discipline. Individual v1p0 components become implemented only when code, configs, artifacts, tests, and validation records exist for that component.

The project remains focused on testing whether aligned firm-news event-state information adds predictive value beyond market-only baselines for end-of-day, multi-horizon forward excess-return forecasting.

## 2. Authority And Source Basis

| Source | Role |
| --- | --- |
| `AgentRules.md` | Binding governance constitution and approval gates. Do not edit without explicit approval. |
| `docs/agent/AgentMemory.md` | Binding memory and event-ledger procedure. Do not edit without explicit approval. |
| `docs/agent/agent_log/Current_State.md` | Current operational memory, blockers, and active evidence pointers. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Append-only request, task, evidence, and reconciliation ledger. |
| `ArchitecturalDesignDecisions.md` | Active v1p0 architectural decision consolidation. |
| `docs/NextSteps_Brainstorming.md` | Important retained v1p0 decision-history source. |
| `deprecated/v0p9/docs/ScopeDecisionLog.md` | Preserved historical owner-approved decision log after manual deprecation. |
| `deprecated/v0p9/docs/ScopeDefinition.md` | Preserved older scope-framing and contradiction inventory after manual deprecation. |
| `ResearchTruth.md` | Current implemented/research truth and non-claims. |
| `Architecture_Map.md` | Active v1p0 architecture map and file-flow plan. |
| `Complete_guidebook.txt` | Detailed v1p0 guidebook and intended implementation flow. |

If this file conflicts with `AgentRules.md`, `ArchitecturalDesignDecisions.md`, `ResearchTruth.md`, or explicit owner approvals in the ledger, the higher-authority source wins and this file must be fixed.

## 3. Version Naming

From this point forward, the next implementation version is named `v1p0` in plans, folders, manifests, docs, candidate artifact families, and validation records.

Do not relabel v0p9 artifacts as v1p0. v0p9 remains historical/completed state. Deprecated v0p9 docs and code live under `deprecated/v0p9/` where already preserved or manually moved by the user. The older root archive has been normalized to `deprecated/v0p7/`.

## 4. Current Repository State

The repository contains a completed historical v0p9 research state with materialized Stage 2 through Stage 6 benchmark artifacts, Stage 7C diagnostics, Stage 8 plan-first update tooling, and Stage 10C historical-prediction packet generation. Those artifacts remain implemented truth for v0p9 only.

The current Stage 6 result remains `clean_null` and `limitation_bearing`. It must not be reinterpreted as positive, live, trading-relevant, or benchmark-comparable to future variants without explicit approval.

The active `src/event_state_forecasting/**` v0p9 implementation is being deprecated outside this document's control. Do not move or generate code until imports, tests, and the planned v1p0 structure are understood.

## 5. v1p0 Objective

The v1p0 objective is to create a small, versioned, credible first slice that strengthens the weak model stack while preserving leakage control, saved-prediction evaluation, explicit non-claims, artifact provenance, and benchmark comparability discipline.

The first slice should address the main near-term risk: underpowered market baselines, same-row or weak market features, weak text/event representation, and shallow fusion. It should not expand into live forecasting, services, dashboards, trading signals, provider expansion, or broad architecture exploration.

## 6. Protected Scientific Scope

| Area | Active definition |
| --- | --- |
| Mode | Local CLI/artifact-driven research system. |
| Objective | Test event-state incremental value beyond market-only baselines. |
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

## 7. v1p0 First Slice

The first v1p0 slice should be intentionally narrow.

| Deliverable | Definition |
| --- | --- |
| `v1p0` version manifest | Defines benchmark-family version and component versions without relabeling v0p9 artifacts. |
| v1p0 feature registry | Sidecar registry mapping model variants to feature artifacts. |
| Market lag/rolling features | Versioned tabular sidecar features for stronger market baselines. |
| Sequence-window contract | Manifest or placeholder contract for later TSMixer work. |
| `market_lag_linear_v1` | Temporal sanity baseline. |
| `market_xgboost_v1_fixed` | Honest stronger market hurdle before tuning. |
| `market_xgboost_v2_nested_optuna_candidate` | Frozen search-space/objective candidate for later development-only Stage 22 tuning. |
| Diagnostics core | Train-gap capability where train predictions exist, strata, and first uncertainty evidence. |
| Stage 10C clarity refactor | Report wording, per-horizon tables, deterministic news context, caveats, and fidelity tests. |

The first slice may document TSMixer, FinBERT, nested Optuna, and ensemble contracts. Stage 21 freezes the XGBoost search contract, Stage 22 records development-only search evidence, and Stage 23 records frozen-final evaluation artifacts. None of these stages authorizes promotion language or full GPU/text/fusion expansion.

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

## 9. Out Of Scope For v1p0 First Slice

| Item | Status |
| --- | --- |
| Live provider calls | Not approved. |
| Raw overwrites or hidden data mutation | Not approved. |
| Hidden Stage 2 through Stage 6 reruns | Not approved. |
| Stage 6 reinterpretation | Not approved. |
| Persisted inference package | Deferred and approval-gated. |
| New `forecast_candidate` semantics | Deferred and approval-gated. |
| Service/API/dashboard | Deferred/rejected for current phase. |
| Trading signals, buy/sell outputs, price targets, portfolio advice | Not approved. |
| LLM summaries | Rejected for first implementation. |
| Provider expansion | Deferred. |
| Relabeling v0p9 artifacts as v1p0 | Forbidden. |

## 10. Sanitization Baseline

Before modeling work, active docs should be sanitized so they describe v1p0 planning rather than the old Stage 10C usage surface.

| File | v1p0 role |
| --- | --- |
| `ProjectDefinition.md` | This file; broad v1p0 project definition. |
| `ArchitecturalDesignDecisions.md` | Active v1p0 decision consolidation. |
| `Architecture_Map.md` | Root architecture map with folder/file purpose, inputs, outputs, dependencies, owner stage, and validation expectations. |
| `UsageManual.md` | Barebones v1p0 placeholder/manual skeleton until v1p0 outputs exist. |
| `Complete_guidebook.txt` | Detailed v1p0 guidebook and intended file-flow map. |
| `docs/NextSteps_Brainstorming.md` | Retained important decision-history source. |
| `deprecated/v0p9/docs/ScopeDecisionLog.md` and `deprecated/v0p9/docs/ScopeDefinition.md` | Preserved manually deprecated decision sources; active planning should use `ArchitecturalDesignDecisions.md`. |

## 11. Approval Gates

Explicit approval remains required before changing target family, horizon set, provider stack, universe, alignment policy, evaluation protocol, comparator ladder, benchmark comparability, live-provider behavior, raw overwrite policy, output status, trading semantics, or governance files.

Edits to `AgentRules.md` or `docs/agent/Agent*.md` require explicit user approval.

## 12. Maintenance Rule

Update this file whenever the v1p0 architecture map, implementation evidence, protected-scope decisions, or active truth files change materially. Do not use this file to bypass approval gates or claim implementation before validated artifacts exist.
