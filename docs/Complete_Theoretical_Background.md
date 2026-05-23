# Complete Theoretical Background

Status: minimum active-root theory skeleton, created 2026-05-06 from `ScopeDecisionLog.md`, `ResearchTruth.md`, and current repository evidence. This file is active theory truth, but it is not a benchmark result and does not claim benchmark readiness.

## Scientific Objective

Phase 1 tests whether aligned firm-news event-state features add predictive value beyond market-only baselines for end-of-day, multi-horizon, forward excess-return forecasting.

The accepted thesis is benchmark-first, not product-first. A robust positive result, a conditional positive result, or a clean null result can all be valid phase-1 outcomes if produced under the approved leakage-controlled benchmark protocol.

## Accepted Hypotheses

- H1: Recent aligned firm-news, represented as event-state features, may add incremental predictive value over market-only baselines for forward excess returns.
- H0: Event-state features may add no reliable incremental value after market-only baselines and leakage controls are enforced.
- H2: Any apparent incremental value must be evaluated across the approved horizon set and cannot be accepted from a single convenient metric or split.

## Active Scope Constraints

- Target family: forward excess returns.
- Horizons: `1d`, `5d`, `10d`, `20d`, and `60d`.
- Universe: reproducible top-50 liquid large-cap universe for the first serious benchmark.
- Provider stack: Twelve Data for OHLCV, Alpha Vantage for financial news, and SEC for static/company support only.
- News alignment: same-day as-of-close, with after-hours and non-trading-day articles rolled forward.
- Evaluation: purged-plus-embargoed walk-forward for development and final untouched lockbox for reporting.
- Option B validation refinement: strict data separation, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, and overfitting diagnostics.
- Runtime boundary: local CLI/artifact-driven research system only.

## Rejected Or Deferred Scope

- Phase 1 is not a trading bot, API, dashboard, user-facing service, or permission-management product.
- Static company metadata and KB features are deferred to phase 2.
- Uncertainty-aware outputs are deferred to a later extension.
- Graph-heavy cores, MoE, dynamic profiles, end-to-end text fine-tuning, broad derivative grids, and first-pass full live-universe benchmarking are out of phase 1 until the core benchmark is stable.
- Later top-100, top-500, or broader-universe runs are separate benchmark families unless explicitly approved otherwise.

## Methodology Constraints

- No serious result may be claimed without reproducible dataset, split, prediction, metric, and comparison artifacts.
- No serious result may be claimed if train/validation/lockbox row separation, purge/embargo accounting, fold-local preprocessing, metric predeclaration, saved out-of-sample predictions, or overfitting diagnostics are missing or violated.
- No-news rows remain in the row universe and must be represented by explicit empty event states plus no-news indicators.
- Raw file coverage is not equivalent to provider-level article completeness, feature completeness, or benchmark readiness.
- Alpha Vantage windows that hit the provider response limit must remain flagged as truncation risk until refined or explicitly accepted as a limitation.
- Provider changes, universe changes, target changes, horizon changes, alignment changes, or evaluation changes are benchmark-family changes and require explicit approval.

## Theory-To-Design Consequences

- The dataset builder must preserve a market-only row universe and add event-state features without dropping no-news rows.
- Label generation must support all approved horizons and use forward excess returns.
- Split generation must support purging, embargoing, walk-forward folds, and a final lockbox boundary.
- Benchmark runners must produce comparable market-only and event-state model outputs on identical rows and splits.
- Artifact manifests must record data versions, provider coverage status, feature contracts, split definitions, preprocessing-fit boundaries, model configs, saved predictions, metrics, and overfitting diagnostics.

## Current Unresolved Theory/Validation Questions

- The exact clean historical benchmark window must still be selected from verified overlap across OHLCV, news, labels, and split feasibility.
- The policy for 92 likely truncated Alpha Vantage top-50 canonical windows remains unresolved.
- The final comparator roster implied by the broadened mandatory ladder still needs design-level freezing.
- Option B data-separation and overfitting-control requirements are documented but not yet executable.
- Provider-reality checks for Alpha Vantage coverage and Twelve Data OHLCV adequacy remain mandatory before serious claims.

## Evidence Pointers

- `ScopeDecisionLog.md`
- `ResearchTruth.md`
- `docs/Data_Separation_And_Overfitting_Control.md`
- `docs/agent/agent_log/Project_Audit_2026-05-06.md`
- `docs/agent/agent_log/AlphaVantage_Raw_Merge_2026-05-06.md`
- `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json`
