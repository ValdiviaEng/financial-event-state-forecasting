# Stage 1 Universe And OHLCV Audit Addendum - 2026-05-14

Status: Stage 1 checklist addendum for universe provenance and Twelve Data OHLCV evidence. This report does not change the protected universe, does not create a benchmark dataset, and does not promote the entire deprecated snapshot.

## Authority

| Source | Role |
| --- | --- |
| `Stage1Prompt.md` | Stage 1 checklist source. |
| `docs/Detailed_Execution_Stages.md` | Granular Stage 1 requirements. |
| `ScopeDecisionLog.md` | Protected universe/provider decisions. |
| `ResearchTruth.md` | Active truth for Alpha Vantage news and Twelve Data OHLCV. |
| `docs/Data_Update_Strategy.md` | Raw data refresh and provider-call discipline. |

## Scope Preserved

| Area | Current Stage 1 scope |
| --- | --- |
| News provider | Alpha Vantage. |
| OHLCV provider | Twelve Data. |
| First benchmark universe | Approved top-50 liquid large-cap seed from `data/raw/universe/top50_slickcharts_2026-04-10.csv`. |
| OHLCV support ticker | `SPY` for excess-return benchmark support. |
| Horizons preserved | `1d`, `5d`, `10d`, `20d`, `60d`. |

## Checklist Result

| Stage 1 step | Status | Evidence |
| --- | --- | --- |
| Recover protected universe and provider decisions | Complete | Active docs preserve Alpha Vantage news and Twelve Data OHLCV. |
| Inventory top-50 universe rows and canonical tickers | Complete with provenance limitation | `50` tickers, no duplicates, `BRK.B` preserved. |
| Inventory Alpha Vantage canonical expected windows | Complete in original Stage 1 audit | `850` expected windows. |
| Compare expected Alpha Vantage windows with actual raw files | Complete in original Stage 1 audit | `850/850` present. |
| Parse canonical Alpha Vantage JSON payloads | Complete in original Stage 1 audit | `850` parsed, `0` parse failures. |
| Count Alpha Vantage feed rows by ticker/year | Complete in original Stage 1 audit | `209143` canonical feed rows. |
| Flag likely Alpha Vantage truncation | Complete in original Stage 1 audit | `92` likely truncated windows. |
| Flag Alpha Vantage empty feeds | Complete in original Stage 1 audit | `10` empty-feed windows. |
| Detect duplicate/non-canonical files | Complete in original Stage 1 audit | `8` non-canonical AAPL slice files excluded from canonical count. |
| Scan ledgers/logs for API-key-bearing URLs | Complete in original Stage 1 audit | `2` sensitive Alpha Vantage URL/key-pattern files; not shareable as-is. |
| Verify Twelve Data OHLCV state | Complete with limitations | Active raw path now has `50/50` top-50 plus SPY support full-window files back to 2010 where provider/listing history exists; deprecated raw/parquet remains reference-only fallback evidence. |
| Verify SEC support state | Recorded as not evidenced/not required unless later consumed | SEC remains static/company support only. |
| Write audit artifacts and update downstream evidence | Complete | Audit, backfill, coverage, and split-reference artifacts created. |

## Universe Findings

| Check | Result |
| --- | --- |
| Top-50 file | `data/raw/universe/top50_slickcharts_2026-04-10.csv`. |
| Top-50 count | `50`. |
| Duplicates | `0`. |
| Dotted ticker preservation | `BRK.B` present. |
| Top-100 consistency | Top-50 is exactly the first 50 rows of `data/raw/universe/top100_slickcharts_2026-04-10.csv`. |
| Deprecated copy consistency | Active and deprecated top-50 files match. |
| S&P 500 membership check | All 50 tickers appear in `data/raw/universe/sp500_snapshot_2026-03-19.csv`. |
| S&P 500 snapshot source | `wikipedia_sp500_components`, `https://en.wikipedia.org/wiki/List_of_S%26P_500_companies`, snapshot date `2026-03-19`. |
| Slickcharts raw source evidence | Not evidenced in repository materials. |

Universe limitation: the top-50/top-100 CSVs are internally consistent and match S&P 500 membership evidence, but the repository does not currently evidence the raw Slickcharts 2026-04-10 page/export or a Slickcharts collection script.

## Twelve Data Findings

| Check | Result |
| --- | --- |
| Active raw Twelve Data directory | `data/raw/twelvedata` now has `50/50` approved top-50 full-window raw payloads plus SPY support for requested window `2010-01-01` to `2026-05-13`. |
| Active raw parse failures | `0`. |
| Active raw quality blockers | `0` missing required rows, `0` non-positive OHLC rows, `0` negative volume rows. |
| Active raw missing-entry audit | `0` post-first-available-date gaps across top-50 against the majority trading calendar. |
| Active raw late-start tickers | `ABBV`, `GEV`, `META`, `PLTR`, `TSLA`; treated as listing/provider-history limitations, not post-first-date missing rows. |
| Active raw OHLC warning | `1` CVX row on `2023-06-05`; requires a future cleaning/patch policy before dataset materialization. |
| Active raw all-horizon candidate as-of range | `2024-04-01` to `2026-02-13` from current top-50 raw intersection and 60 trading-step label availability; not owner-selected. |
| Active raw latest observed majority-calendar date | `2026-05-12`; requested end `2026-05-13` returned no majority-calendar row. |
| Deprecated raw Twelve Data directory | `deprecated_version/legacy_snapshot_20260402T115014Z/data/raw/twelvedata`. |
| Deprecated raw coverage | `50/50` approved top-50 present for the same Stage 1 scope; SPY exists as support evidence but is not counted in the top-50 scope. |
| Deprecated raw parse failures | `0`. |
| Deprecated raw quality blockers | `0` missing required rows, `0` non-positive OHLC rows, `0` negative volume rows. |
| Deprecated raw OHLC warning | `1` CVX row on `2023-06-05`, outside the all-horizon candidate window. |
| Deprecated raw price intersection | `2024-04-01` to `2024-12-30`. |
| Deprecated raw all-horizon candidate as-of range | `2024-04-01` to `2024-10-03`. |
| Deprecated parquet salvage | Already verified as usable with limitations in `data/manifests/stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json`. |

Deprecated OHLCV collection code located:

| File | Role |
| --- | --- |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/data/twelve_data_client.py` | Twelve Data `time_series` client. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/data/price_pipeline.py` | Raw payload, interim parquet, quality report, and request-ledger pipeline. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/cli/build_market_data.py` | Historical market-data ingestion CLI. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/cli/build_adjusted_prices.py` | Historical split-adjusted price CLI. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/configs/data_sources.yaml` | Historical config confirms `market_data.provider: twelve_data`. |

Historical contradiction: deprecated `configs/data_sources.yaml` lists `news_data.provider: finnhub`. This is historical-only and is superseded by active scope, which uses Alpha Vantage for news.

## Blocking Actions

| Area | Blocking action |
| --- | --- |
| Universe scope wording | Confirm whether “top S&P 500 OHLCV” means the approved top-50 plus SPY, or a full S&P 500 universe as a new benchmark family. |
| Universe provenance | Provide raw Slickcharts 2026-04-10 source/export evidence, or approve recording the missing raw source as an accepted provenance limitation. |
| Active raw Twelve Data residency | Resolved: user approved quota; `50/50` top-50 plus SPY support full-window active raw payloads downloaded. |
| Split adjustment | Deferred decision: deprecated split-event and split-adjustment method is verified as reference-only; no active-root method was selected. |
| Deprecated OHLCV evidence | Keep specific deprecated Twelve Data raw/parquet evidence limitation-flagged; do not promote the full archive. |
| SEC support | Keep absent/not required unless a later dataset contract consumes SEC static/company fields. |
| Credential safety | Do not commit/share raw provider ledgers/logs until sanitized or isolated; rotate exposed keys if publication/commit is planned. |

## Questions For User

No open Stage 1 execution questions remain. The user confirmed Stage 1 stays top-50 only, top-50 completeness is sufficient despite missing raw Slickcharts source evidence, and Twelve Data quota may be spent for active top-50 OHLCV.

## Generated Artifacts

| Artifact | Role |
| --- | --- |
| `scripts/audit_stage1_universe_ohlcv.py` | Stage 1 universe and OHLCV audit script. |
| `data/manifests/stage1_universe_ohlcv_audit_2026-05-14.json` | Machine-readable universe/OHLCV audit manifest. |
| `scripts/download_missing_twelvedata_ohlcv.py` | Plan/execute script for missing active Twelve Data raw OHLCV entries. Defaults to plan-only. |
| `data/manifests/twelvedata_missing_ohlcv_download_plan_2026-05-14.json` | Current missing-entry manifest; now reports `0` missing top-50 entries after downloads. |
| `data/manifests/twelvedata_top50_ohlcv_download_execution_2026-05-14.json` | Safe execution summary for the approved top-50 Twelve Data raw downloads. |
| `scripts/audit_twelvedata_ohlcv_coverage.py` | Active raw 2010 coverage and reference-only split-adjustment audit script. |
| `data/manifests/twelvedata_top50_spy_ohlcv_backfill_2010_2026-05-14.json` | Safe execution summary for the remaining 2010 backfill calls after one test call. |
| `data/manifests/twelvedata_top50_spy_ohlcv_backfill_2010_completion_2026-05-14.json` | Plan-mode proof that `0` 2010 full-window top-50/SPY entries remain missing. |
| `data/manifests/twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json` | Machine-readable 2010 coverage and split-reference audit. |
| `docs/agent/agent_log/TwelveData_OHLCV_2010_Coverage_And_Splits_2026-05-14.md` | Human-readable 2010 coverage and split-reference audit. |

## Validation Evidence

| Command | Result |
| --- | --- |
| `python -m py_compile scripts/audit_stage1_universe_ohlcv.py scripts/download_missing_twelvedata_ohlcv.py` | Passed with no output. |
| `python scripts/audit_stage1_universe_ohlcv.py --write` | `status: completed_with_limitations`; hard blockers `none`. |
| `python scripts/download_missing_twelvedata_ohlcv.py --execute --max-symbols 1 --sleep-seconds 0` | Test download succeeded for `1/1`. |
| `python scripts/download_missing_twelvedata_ohlcv.py --execute --sleep-seconds 8` | Remaining downloads succeeded for `49/49`. |
| `python scripts/download_missing_twelvedata_ohlcv.py --write` | `status: planned_only`; `planned_count: 0` after downloads. |
| `python scripts/download_missing_twelvedata_ohlcv.py --start-date 2010-01-01 --end-date 2026-05-13 --include-spy --execute --max-symbols 1 --sleep-seconds 0` | 2010 backfill test download succeeded for `1/1`. |
| `python scripts/download_missing_twelvedata_ohlcv.py --start-date 2010-01-01 --end-date 2026-05-13 --include-spy --execute --sleep-seconds 8` | Remaining 2010 backfill downloads succeeded for `50/50`. |
| `python scripts/download_missing_twelvedata_ohlcv.py --start-date 2010-01-01 --end-date 2026-05-13 --include-spy --write` | `planned_count: 0` after 2010 full-window backfill. |
| `python scripts/audit_twelvedata_ohlcv_coverage.py --write --strict` | `status: complete_observed_life_with_late_start_limitations`; hard blockers `none`. |

## Non-Claims

- Live Twelve Data downloads were executed only for approved top-50 active raw OHLCV payloads plus SPY support evidence.
- No benchmark dataset was created.
- No clean-window selection was finalized.
- No active split-adjustment method or OHLCV anomaly patch policy was selected.
- No feature, label, split, model, metric, or benchmark result was created.
- No provider-level Alpha Vantage article completeness is claimed.
- No entire deprecated snapshot was promoted to active truth.
