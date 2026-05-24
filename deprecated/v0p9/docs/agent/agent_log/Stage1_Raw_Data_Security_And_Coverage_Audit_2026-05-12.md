# Stage 1 Raw Data Security And Coverage Audit - 2026-05-12

Status: Stage 1 audit artifact, supplemented by `docs/agent/agent_log/Stage1_Universe_And_OHLCV_Audit_2026-05-14.md`. This report documents raw-state evidence for the approved top-50 phase-1 benchmark family. It does not create a benchmark dataset, active config, executable test suite, model, benchmark runner, or benchmark result.

## Authority

| Source | Role |
| --- | --- |
| `AgentRules.md` | Governance, evidence discipline, approval gates, no unsupported claims. |
| `ScopeDecisionLog.md` | Provider stack, universe, target, horizon, evaluation, and benchmark-family decisions. |
| `ResearchTruth.md` | Current raw coverage and truncation truth. |
| `ProjectDefinition.md` | Raw-data role and non-claims. |
| `docs/db_Testing.md` | Required raw and dataset checks. |
| `docs/Data_Update_Strategy.md` | Refresh, rollback, and ledger policy. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Downstream split, row, preprocessing, prediction, and diagnostic contracts. |
| `Stage1Prompt.md` | Stage 1 execution requirements. |

## Protected Decisions Preserved

| Area | Preserved value |
| --- | --- |
| Target family | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| First universe | Reproducible top-50 liquid large-cap universe. |
| OHLCV provider | Twelve Data. |
| News provider | Alpha Vantage. |
| SEC role | Static/company support only. |
| Alignment | Same-day as-of-close with after-hours and non-trading-day roll-forward. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Option B refinement | Split manifests, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, contamination blockers, and overfitting diagnostics. |

## Audit Summary

| Check | Result |
| --- | --- |
| Universe file | `data/raw/universe/top50_slickcharts_2026-04-10.csv`. |
| Universe rows | 50 tickers plus header. |
| Dotted tickers preserved | `BRK.B` present. |
| Expected Alpha Vantage canonical windows | 850 (`50` tickers x `17` year/current windows). |
| Present canonical windows | 850. |
| Missing canonical windows | 0. |
| Parsed canonical payloads | 850. |
| Parse failures | 0. |
| Canonical feed rows | 209143. |
| Likely truncated windows | 92. |
| Empty-feed windows | 10. |
| Top-50 non-canonical news files | 8 AAPL slice files retained for traceability and excluded from canonical coverage. |
| Non-top-50 news payload files in active raw Alpha Vantage tree | 0. |
| Credential-risk files found | 2 files contain Alpha Vantage URL or API-key patterns. |
| Twelve Data OHLCV raw evidence | Updated by `Stage1_Universe_And_OHLCV_Audit_2026-05-14.md` and `TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md`: active raw top-50 plus SPY support Twelve Data OHLCV now has full-window files for `2010-01-01` to `2026-05-13`, with no post-first-available-date gaps and five late-start ticker limitations; deprecated raw/parquet evidence remains reference-only fallback. |
| SEC support raw evidence | Not evidenced in repository materials. Verification step: add or identify approved SEC support artifacts if Stage 2 requires them, then rerun provider-evidence checks. |

## Alpha Vantage Coverage

Canonical coverage matches the current merge manifest and daemon summary:

| Evidence | Value |
| --- | --- |
| `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json` expected canonical windows | 850. |
| `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json` final canonical windows | 850. |
| `data/raw/alphavantage/daemon_summary_top50_only_forward.json` completed requests | 850. |
| `data/raw/alphavantage/daemon_summary_top50_only_forward.json` pending requests | 0. |

Raw file coverage is complete for the approved top-50 Alpha Vantage corpus, but provider-level article completeness is not complete because 92 windows hit the provider `limit=1000` pattern.

## Truncation-Risk Report

Likely truncation is inferred when a canonical payload has `feed` length `1000`, matching the configured Alpha Vantage `limit=1000` evidence in the top-50 daemon summary. This is a provider-limit risk, not proof of article completeness.

| Year/window | Likely truncated windows |
| --- | ---: |
| 2021 | 3 |
| 2022 | 3 |
| 2024 | 2 |
| 2025 | 41 |
| 2026 current | 43 |

Stage 2 must not select a clean benchmark window or claim dataset readiness until truncation is refined, avoided by clean-window selection, or accepted by explicit limitation policy with approval where required.

## Empty-Feed Report

The audit found 10 explicit empty-feed canonical windows. These must remain explicit data statuses and must not become silent row drops.

| Window | Status |
| --- | --- |
| `BRK.B:2015` | Empty feed. |
| `ABBV:2010` | Empty feed. |
| `PLTR:2010` | Empty feed. |
| `PLTR:2011` | Empty feed. |
| `PLTR:2012` | Empty feed. |
| `PLTR:2013` | Empty feed. |
| `GEV:2010` | Empty feed. |
| `LIN:2011` | Empty feed. |
| `LIN:2013` | Empty feed. |
| `LIN:2014` | Empty feed. |

## Duplicate And Non-Canonical Files

The active top-50 canonical set has no duplicate canonical paths and no missing canonical files. The audit found 8 top-50 non-canonical AAPL slice files:

| File | Handling |
| --- | --- |
| `data/raw/alphavantage/AAPL/news_sentiment__2025-01-01__2025-03-31.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2025-04-01__2025-06-30.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2025-07-01__2025-09-30.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2025-10-01__2025-12-31.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2026-01-01__2026-01-31.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2026-01-01__2026-04-09.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2026-02-01__2026-02-28.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |
| `data/raw/alphavantage/AAPL/news_sentiment__2026-03-01__2026-03-31.json` | Retain for traceability; exclude from canonical 850-window count unless a future approved refinement adopts sliced windows. |

## Credential-Risk Report

The credential scan intentionally reports only file paths and counts. No secrets were printed.

| File | Lines | Alpha Vantage URL lines | API-key pattern lines | Status |
| --- | ---: | ---: | ---: | --- |
| `data/raw/alphavantage/news_request_ledger.jsonl` | 473 | 448 | 435 | Sensitive; do not commit, share, or publish as-is. |
| `runs/logs/alphavantage_news_daemon.log` | 66 | 10 | 0 | Sensitive URL-bearing log; do not commit, share, or publish as-is. |

No destructive action, key rotation, file relocation, or sanitization was performed because Stage 1 requires user approval before destructive or credential-handling changes. Recommended next action is to sanitize or isolate these artifacts and rotate any exposed provider key before commit, sharing, or publication.

## Clean-Window Input Summary

Stage 2 can use this audit as raw-state input, but clean-window selection remains blocked by provider evidence and policy decisions.

| Input area | Stage 2 status |
| --- | --- |
| Top-50 universe | Available and deterministic from `top50_slickcharts_2026-04-10.csv`. |
| Alpha Vantage news raw files | Canonical top-50 file coverage complete and parseable. |
| Alpha Vantage provider completeness | Blocked by 92 likely truncated windows. |
| Empty-news handling | 10 explicit empty-feed windows must be retained as explicit no-news/empty-feed status. |
| Twelve Data OHLCV | Updated by `Stage1_Universe_And_OHLCV_Audit_2026-05-14.md` and `TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md`: active raw top-50 plus SPY support coverage is present for the requested 2010 full-window backfill; all-horizon candidate as-of range from active raw intersection is `2024-04-01` to `2026-02-13`; final materialized clean-window record remains a Stage 2 output. |
| SEC support | Not evidenced in repository materials. Verification step: add or identify approved SEC artifacts only if required by the Stage 2 contract. |
| Raw credential safety | Blocked for sharing/commit/publication until sensitive ledgers/logs are sanitized, isolated, or otherwise handled with approval. |

## Generated Artifacts

| Artifact | Role |
| --- | --- |
| `docs/agent/agent_log/Stage1_Raw_Data_Security_And_Coverage_Audit_2026-05-12.md` | Human-readable raw audit, credential-risk report, truncation-risk report, and clean-window input summary. |
| `data/manifests/stage1_raw_security_coverage_audit_2026-05-12.json` | Machine-readable Stage 1 audit manifest. |
| `docs/agent/agent_log/Stage1_Universe_And_OHLCV_Audit_2026-05-14.md` | Universe and Twelve Data OHLCV addendum. |
| `data/manifests/stage1_universe_ohlcv_audit_2026-05-14.json` | Machine-readable universe/OHLCV addendum manifest. |
| `docs/agent/agent_log/TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md` | Active raw Twelve Data 2010 coverage and split-reference audit. |
| `data/manifests/twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json` | Machine-readable active raw Twelve Data 2010 coverage audit manifest. |

## Validations

| Check | Result |
| --- | --- |
| Universe/count/coverage/parse/truncation/empty/credential computation | Completed with repository-local PowerShell audit. |
| Stage 1 artifact consistency check | `STAGE1_ARTIFACT_CHECK PASSED`. |
| Governance validation | `VALIDATION PASSED`. |
| Comment-only scaffold validation | `COMMENT_ONLY_VALIDATION PASSED`. |

## Non-Claims

- This audit does not prove provider-level Alpha Vantage article completeness.
- This audit does not create a clean historical benchmark window.
- This audit does not create a materialized benchmark dataset.
- This audit does not create executable tests.
- This audit does not create a model, benchmark runner, or benchmark result.
