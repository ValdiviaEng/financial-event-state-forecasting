# Twelve Data OHLCV 2010 Coverage And Split-Adjustment Review

Generated UTC: 2026-05-14T15:14:20.351297Z

## Authority

This is Stage 1 raw-data evidence only. It preserves the approved top-50 universe and Twelve Data OHLCV provider. It does not build a benchmark dataset, select a clean window, or choose a split-adjustment method.

## Coverage Summary

- Status: `complete_observed_life_with_late_start_limitations`
- Target window: `2010-01-01` to `2026-05-13`
- Top-50 full-window files present: `50/50`
- Support full-window files present: `1/1`
- Reference calendar: `SPY` with `4114` trading dates from `2010-01-04` to `2026-05-12`
- Top-50 complete from reference start: `45`
- Top-50 complete after late first available date: `5`
- Top-50 with post-first-date gaps: `0`
- Top-50 missing all dates: `0`
- Hard blockers: `none`

## Late-Start Tickers

These tickers start after the 2010 reference-calendar start in provider data but have no post-first-date gaps detected:

- `ABBV`: first `2013-01-02`, last `2026-05-12`
- `GEV`: first `2024-04-01`, last `2026-05-12`
- `META`: first `2012-05-18`, last `2026-05-12`
- `PLTR`: first `2020-09-30`, last `2026-05-12`
- `TSLA`: first `2010-06-29`, last `2026-05-12`

## Split-Adjustment Reference

Deprecated snapshot evidence was inspected as reference-only. It records a candidate method, but active-root method selection is still not made.

- Split events parquet rows: `1506`
- Split tickers in top-50/support: `43`
- Split date range: `1962-10-31` to `2026-02-10`
- Adjusted price files present in top-50/support: `51`

Deprecated method observed:

- fetch split events from Twelve Data splits when available with yfinance fallback
- normalize split factors to new_shares_per_old_share
- compute cumulative future split factors per historical row
- back-adjust OHLC prices by dividing by cumulative factor and volume by multiplying by cumulative factor
- skip events when local raw prices already appear split-adjusted
- optionally exclude rows around split dates

## Limitations

- This audit verifies raw OHLCV coverage and quality; it does not materialize a dataset or select a benchmark clean window.
- SPY is used only as a reference trading calendar and support ticker; this does not select the final excess-return reference series.
- Split-adjustment logic from the deprecated snapshot is reference-only until explicitly reintroduced into active-root design and approved if it changes data-cleaning contracts.
- Some current top-50 tickers begin after 2010 in provider data, likely due IPO, spin-off, listing, or provider-history limits; they are not counted as post-first-date missing rows: ABBV, GEV, META, PLTR, TSLA
- The requested end date was 2026-05-13, but the latest observed majority-calendar OHLCV date is 2026-05-12; rerun a refresh later if newer completed trading days are required.
- Raw OHLCV quality has 1 OHLC order anomaly; it is not a missing-entry blocker but requires a future cleaning/patch policy before dataset materialization.
