# Implementation Decisions

Status: active-root design decision ledger. Decisions here are constrained by `ScopeDecisionLog.md` and `ResearchTruth.md`. This file records approved direction, the 2026-05-07 scaffold status, approved Stage 2 through Stage 8 plus Stage 10C conversions, and known open design decisions; it does not authorize benchmark-family changes.

## Approved Decisions

| ID | Decision | Status | Evidence |
| --- | --- | --- | --- |
| ID-001 | Rebuild in the active root; use the archived snapshot only as reference/salvage material. | Approved | `ScopeDecisionLog.md`, `LEGACY_DEPRECATION_SUMMARY.md` |
| ID-002 | Phase 1 is a narrow event-state incremental-value benchmark, not a broad platform. | Approved | `ScopeDecisionLog.md`, `ResearchTruth.md` |
| ID-003 | Use forward excess returns for the first serious target family. | Approved | `ScopeDecisionLog.md` |
| ID-004 | Support horizons `1d`, `5d`, `10d`, `20d`, and `60d`. | Approved | `ScopeDecisionLog.md` |
| ID-005 | Use same-day as-of-close news alignment with after-hours and non-trading-day roll-forward. | Approved | `ScopeDecisionLog.md` |
| ID-006 | Use top-50 liquid large-cap universe for the first serious benchmark family. | Approved | `ScopeDecisionLog.md`, `data/raw/universe/top50_slickcharts_2026-04-10.csv` |
| ID-007 | Use Twelve Data for OHLCV, Alpha Vantage for news, and SEC for static/company support only. | Approved | `ScopeDecisionLog.md` |
| ID-008 | Encode no-news rows as explicit empty event states with no-news indicators. | Approved | `ScopeDecisionLog.md` |
| ID-009 | Default event-state representation is pooled dense embeddings plus scalar enrichments. | Approved | `ScopeDecisionLog.md` |
| ID-010 | Default multimodal fusion family is simple gated fusion. | Approved | `ScopeDecisionLog.md` |
| ID-011 | Serious claims require purged-plus-embargoed walk-forward and final untouched lockbox. | Approved | `ScopeDecisionLog.md` |
| ID-012 | Every serious benchmark emits dataset, manifest, config, folds, predictions, metrics, and comparison summary artifacts. | Approved | `ScopeDecisionLog.md` |
| ID-015 | Option B data-separation refinement is adopted: explicit split manifests, train-fold-only preprocessing, predeclared metrics, saved out-of-sample predictions, and overfitting diagnostics are mandatory for serious comparisons. | Approved | `docs/Data_Separation_And_Overfitting_Control.md` |

## Current Active Implementation Decisions

- Active code currently lives under `scripts/` and the approved Stage 2 through Stage 7C plus Stage 10C paths under `src/event_state_forecasting/`.
- Alpha Vantage raw ingestion/backfill is handled by standalone top-50 and bucket scripts.
- Canonical top-50 Alpha Vantage raw file coverage is complete at 850/850 after the 2026-05-06 raw merge.
- Existing raw destination files were not overwritten during the raw merge.
- Raw request ledgers are not safe to commit or share while they contain provider request URLs with API-key material.
- Approved Stage 2 dataset, Stage 3 feature/label, Stage 4 split/packet, Stage 5 model/preprocessing/saved-prediction, and Stage 6 evaluation/reporting paths are active implementation.
- Approved Stage 7C contextual-bandit diagnostics, Stage 8 plan-first raw update scripts/tests, and Stage 10C local prediction-output packet generation are active implementation for their scoped non-benchmark/non-live claims.
- Remaining scaffold files document future responsibilities, inputs, outputs, dependencies, validation expectations, limitations, and blind spots, but they are not active implementation.
- `docs/Data_Separation_And_Overfitting_Control.md` owns the Option B validation-design contract; Stage 2 through Stage 7C enforce the portions already converted, with train-validation gap explicitly blocked because Stage 5 saved no train predictions. Stage 10C consumes existing saved predictions and does not alter the benchmark contract.
- Active Stage 3 through Stage 7 config files and executable Stage 2 through Stage 8 plus Stage 10C tests are evidenced; current Stage 6 result class is `clean_null` and comparability is `limitation_bearing`.

## Comment-Only Scaffold Decision

- ID-013: Create the active-root scaffold under `src/event_state_forecasting/`, `configs/`, and `tests/` as comment-only files. Status: approved by user request and executed as structural documentation only. Evidence: `StructuralFolderMapPrompt.md`; `src/event_state_forecasting/`; `configs/`; `tests/`.
- ID-014: Keep scaffold files non-runnable until detailed implementation contracts and tests are approved. Status: active constraint for all paths not explicitly converted in Stage 2 through Stage 8 or Stage 10C. Evidence: generated scaffold file headers, `scripts/validate_comment_only_scaffold.py`, and approved executable-path exemptions.

## Open Design Decisions Before Broader Coding

- Preserve Stage 6 metric contracts, ranking diagnostics, overfitting diagnostic report, comparison-summary schema, and lockbox-reporting rules unless explicit approval authorizes a comparability-reviewed change.
- Define the truncation-refinement path for the 92 likely truncated Alpha Vantage canonical windows.
- Define sanitization behavior for provider request ledgers before raw logs can be committed or published.
- Convert remaining comment-only evaluation, reporting, provider, utility, and expansion scaffold contracts into executable implementation only after detailed design and validation gates are approved.

## Non-Decisions

- Top-100/top-500 news collection scripts do not make those universes comparable to the first top-50 benchmark family.
- Complete raw top-50 file coverage does not prove provider-level article completeness or positive result validity.
- Historical archived modules do not become active code until intentionally reintroduced through active design and implementation work.
- Remaining comment-only scaffold files are not active code and do not prove provider, operations, utility, or expansion-family readiness.
- Overfitting diagnostics support interpretation but do not authorize metric shopping, lockbox tuning, or benchmark-family changes.
