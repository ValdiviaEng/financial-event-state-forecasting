# Stage8Prompt

Status: executed on 2026-05-22 as local plan-first daily/weekly raw-data update scripts and tests. This prompt and the resulting scripts do not authorize live provider calls, raw overwrites, provider-completeness claims, benchmark reruns, prediction outputs, or trading signals.

## Mission

Design and, only after explicit execution approval, implement safe local scripts for daily or weekly Alpha Vantage news and Twelve Data OHLCV updates for the approved top-50 universe. The scripts must be plan-first, quota-aware, redaction-safe, manifest-backed, and compatible with the Stage 2 through Stage 6 rebuild process.

## Required Context To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Provider, secret, and destructive-action gates. |
| `docs/Data_Update_Strategy.md` | Refresh and invalidation rules. |
| `ExecutionPipeline.md` | Stagewise rebuild after data changes. |
| `UsageManual.md` | Current local command/artifact usage and inputs/outputs. |
| `ScopeDecisionLog.md` | Approved provider stack and top-50 universe. |
| `ResearchTruth.md` | Current provider limitations and non-claims. |
| `scripts/alphavantage_news_bucket_common.py` | Existing Alpha Vantage runner core. |
| `scripts/run_alphavantage_news_truncation_refinement_quarterly.py` | Existing truncation-refinement behavior. |
| `scripts/download_missing_twelvedata_ohlcv.py` | Existing Twelve Data plan/execute script. |
| `src/event_state_forecasting/data/providers/alphavantage_news.py` | Comment-only provider scaffold boundary. |
| `src/event_state_forecasting/data/providers/twelvedata_ohlcv.py` | Comment-only provider scaffold boundary. |
| `src/event_state_forecasting/ops/data_refresh.py` | Comment-only refresh/invalidation scaffold. |
| `tests/ops/` | Existing comment-only ops-test scaffold status. |

## Candidate Script Names

| Area | Candidate files |
| --- | --- |
| News updates | `scripts/news_update_daily.py`, `scripts/news_update_weekly.py`. |
| OHLCV updates | `scripts/OHLCV_daily_update.py`, `scripts/OHLCV_weekly_update.py`. |

The executor may recommend lowercase alternatives for consistency, but must ask before deviating from requested names.

## Functional Requirements

| Requirement | Required behavior |
| --- | --- |
| Plan-first | Default mode prints/writes a plan and performs no provider call. |
| Live mode | Requires explicit flags, environment key, rate limits, and redacted ledgers. |
| Raw preservation | Never overwrite existing raw files unless `--overwrite` is explicitly provided and documented. |
| Universe control | Defaults to approved top-50 only; top-100/top-500 remains separate benchmark-family work. |
| Dotted tickers | Preserve canonical storage names while using provider-specific request mapping only at the boundary. |
| Manifest | Write update plan/execution summary with changed files, skipped files, provider errors, and non-claims. |
| Invalidation | Produce a refresh impact note that tells the user which Stage 2 through Stage 6 artifacts need rebuild. |
| Secrets | Redact API keys from stdout, logs, and shareable ledgers. |

## Implementation Steps If Executed Later

| Step | Action | Output |
| --- | --- | --- |
| 1 | Reconfirm approval for Stage 8 implementation and whether live calls are allowed. | Approval checkpoint. |
| 2 | Inspect existing scripts to avoid duplicated provider logic. | Reuse plan. |
| 3 | Implement plan-only news update scripts. | Script files and tests. |
| 4 | Implement plan-only OHLCV update scripts. | Script files and tests. |
| 5 | Add live mode only with explicit flags and redaction. | Controlled live path. |
| 6 | Add tests for plan mode, no-overwrite behavior, ticker mapping, and redaction. | `tests/ops/` executable tests if approved. |
| 7 | Update docs, guidebook, and memory. | Discoverability and ledger evidence. |

## Validation Strategy

| Test | Required result |
| --- | --- |
| Plan-mode tests | No provider calls, correct planned requests, safe outputs. |
| Redaction tests | No API-key-bearing URLs in shareable outputs. |
| No-overwrite tests | Existing raw files are skipped by default. |
| Universe tests | Top-50 default is preserved. |
| Invalidation tests | Data changes produce rebuild/comparability warnings. |
| Existing suite | `python -m pytest "tests"` passes if executable code changes. |
| Governance | `python scripts/validate_agent_governance.py` passes. |
| Scaffold | `python scripts/validate_comment_only_scaffold.py` passes or is updated only for newly approved executable paths. |

## Stop Conditions

Stop and ask before live provider calls, overwriting raw files, changing provider stack, changing universe scope, changing benchmark comparability, committing/sharing raw ledgers, rotating keys, or treating updated raw data as a new benchmark result.

## Final Response Requirements

If executed later, report created scripts, plan/live behavior, manifest paths, validation outputs, provider-call status, redaction guarantees, and exact downstream rebuild requirements.
