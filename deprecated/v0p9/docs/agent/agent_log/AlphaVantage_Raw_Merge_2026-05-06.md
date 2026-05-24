# Alpha Vantage Raw Merge - 2026-05-06

## Scope
- Request ID: `R-2026-05-06-0002`
- Task ID: `T-2026-05-06-0002`
- Source: `data/raw_zip/raw/alphavantage`
- Destination/canonical raw DB: `data/raw/alphavantage`
- Universe: `data/raw/universe/top50_slickcharts_2026-04-10.csv`

## Merge Policy
- Copied only missing canonical top-50 yearly/current `NEWS_SENTIMENT` JSON payloads.
- Did not overwrite existing destination files.
- Did not copy request ledgers, summaries, or `Zone.Identifier` artifacts from `raw_zip`.
- Preserved overlapping source files in `data/raw_zip/` for traceability.

## Result
- Canonical windows before merge: 452/850
- Missing windows copied: 398
- Copy errors: 0
- Canonical windows after merge: 850/850
- Missing windows after merge: 0
- Refreshed runner summary: `data/raw/alphavantage/daemon_summary_top50_only_forward.json` now reports `completed_request_count: 850` and `pending_request_count: 0`.
- Complete tickers: 50/50
- Parse errors after merge: 0
- Total feed rows across canonical windows: 209143
- Likely truncated canonical windows (`feed` rows >= 1000): 92
- Empty-feed canonical windows: 10
- Non-canonical news payload files still present in destination: 8
- Overlapping raw/raw_zip canonical paths skipped: 77
- Overlapping paths with different file hashes: 77

## Completion Status
- Canonical top-50 ticker/year file coverage is complete: `850/850`.
- Provider-level article completeness is still limited by Alpha Vantage `limit=1000` truncation risk where windows hit 1000 rows.
- This merge completes file coverage for the approved top-50 raw corpus, not benchmark readiness or leakage-controlled model evaluation.

## Copied Windows By Ticker
- `AMAT`: 17
- `AXP`: 17
- `C`: 17
- `CSCO`: 17
- `GE`: 17
- `GEV`: 17
- `GS`: 17
- `HD`: 17
- `IBM`: 17
- `INTC`: 17
- `KLAC`: 17
- `KO`: 17
- `LIN`: 17
- `LRCX`: 17
- `MCD`: 17
- `MRK`: 17
- `MS`: 17
- `PG`: 7
- `PLTR`: 17
- `PM`: 17
- `RTX`: 17
- `TMUS`: 17
- `UNH`: 17
- `WFC`: 17

## Evidence
- Machine-readable manifest: `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json`
- Merge report: `docs/agent/agent_log/AlphaVantage_Raw_Merge_2026-05-06.md`
- Canonical raw DB path: `data/raw/alphavantage`
- Refreshed runner summary: `data/raw/alphavantage/daemon_summary_top50_only_forward.json`
- Verification command: `python scripts/run_alphavantage_news_top50_only_standalone.py --plan --skip-seed-migration`
