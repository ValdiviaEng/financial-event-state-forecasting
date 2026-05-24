# Data Update Strategy

Status: active-root operations guide through Stage 8 plan-first raw-data update scripts. It governs data refresh discipline and points to `ExecutionPipeline.md` for clean stagewise rebuilds; it does not authorize benchmark-family changes or live provider calls by itself.

Governing refinement: `docs/Data_Separation_And_Overfitting_Control.md` requires data updates to preserve row identity, split manifests, preprocessing-fit boundaries, saved-prediction comparability, and overfitting-diagnostic auditability.

## Current Data State

- Top-50 Alpha Vantage canonical raw file coverage is complete at 850/850 after merging `data/raw_zip/raw/alphavantage` into `data/raw/alphavantage`.
- Provider-level article completeness remains limited-risk because 92 windows likely hit the Alpha Vantage response limit.
- `scripts/run_alphavantage_news_truncation_refinement_quarterly.py` now validates actual quarterly files, downloads missing quarterly slices, and creates monthly follow-up requests when a quarterly slice still returns the provider limit.
- `scripts/run_alphavantage_news_truncation_refinement_standalone.py` embeds the Stage 1 likely-truncated window list for portable standard-library-only execution on another machine; it supports `--order reverse` / `--reverse` for last-entry-to-first downloading.
- Active raw Twelve Data OHLCV full-window files now exist for the approved top-50 plus SPY support for `2010-01-01` to `2026-05-22`; the latest coverage audit reports no post-first-available-date gaps and records late-start ticker and CVX OHLC-anomaly limitations.
- Stage 8 plan-first update scripts now exist for daily/weekly Alpha Vantage news and Twelve Data OHLCV: `scripts/news_update_daily.py`, `scripts/news_update_weekly.py`, `scripts/OHLCV_daily_update.py`, and `scripts/OHLCV_weekly_update.py`. Default mode writes a manifest only and performs no provider calls.
- Top-51+ data collection exists operationally but is not part of the first serious benchmark family unless approved.

## Refresh Rules

- Preserve canonical ticker names in storage, including dotted tickers like `BRK.B` and `BF.B`.
- Normalize provider request symbols only at the provider boundary when required.
- Preserve raw provider payloads and truncation flags.
- Do not overwrite existing raw files without an explicit merge policy and manifest.
- Do not commit or share API-key-bearing raw request ledgers.
- Use Stage 8 update scripts in plan mode first. Live mode requires explicit approval, `--execute`, provider API key availability, `--max-calls`/rate-limit controls, and redacted ledgers.
- Use truncation-refinement plan mode before live downloads; live refinement calls consume Alpha Vantage quota and can still produce provider-limit flags if a monthly slice returns `limit` rows. For remote portable runs, prefer `python run_alphavantage_news_truncation_refinement_standalone.py --plan --order reverse` first.

## Benchmark Invalidation Rules

Refreshing data invalidates prior benchmark comparability if it changes rows, labels, feature availability, provider coverage, universe membership, split boundaries, or target/horizon definitions.

Refreshing data also invalidates prior Option B comparability if it changes split-role assignments, purge/embargo accounting, lockbox membership, preprocessing-fit inputs, saved-prediction row keys, metric definitions, or overfitting diagnostic inputs.

After approved data changes, rebuild Stage 2 through Stage 6 using `ExecutionPipeline.md` and treat the previous Stage 6 `clean_null` packet as historical evidence until the new packet is validated and comparability is reviewed.

## Rollback Rules

- Prefer additive manifests over destructive edits.
- Keep pre-merge raw files unless a reviewed cleanup plan exists.
- If a refresh corrupts coverage or schema, restore from the prior manifest-backed raw state and record the correction in the interaction log.

## Open Operations Decisions

- Ledger URL sanitization and API-key rotation workflow.
- Truncation-refinement cadence and request-window subdivision policy.
- Clean historical window reselection policy after material raw OHLCV/news coverage changes.
- Exact operational policy for preserving or invalidating split manifests, preprocessing-fit manifests, and saved predictions after refreshes beyond the current Stage 6 packet.
- Active-root split-adjustment and OHLCV anomaly patch policy; deprecated split-adjustment code is reference-only until reintroduced through active design and approved where required.
