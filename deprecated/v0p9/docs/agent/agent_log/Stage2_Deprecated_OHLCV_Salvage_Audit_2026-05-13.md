# Stage 2 Deprecated OHLCV Salvage Audit - 2026-05-13

Status: active evidence audit for deprecated Twelve Data OHLCV parquet salvage. This report does not promote the deprecated snapshot to active truth, copy data into active raw paths, build a benchmark dataset, create executable tests, or create a benchmark result.

## Authority

| Source | Role |
| --- | --- |
| `AgentRules.md` | Governance, source hierarchy, approval gates, and evidence discipline. |
| `ScopeDecisionLog.md` | Protected provider, universe, target, horizon, clean-window doctrine, and evaluation decisions. |
| `ResearchTruth.md` | Active truth and archive/reference-only boundary. |
| `ProjectDefinition.md` | Phase-1 provider and dataset responsibilities. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/` | Reference-only source inspected for salvage evidence. |

## Result

The deprecated snapshot contains usable Twelve Data parquet evidence for Stage 2 market-data input readiness, with limitations.

Machine-readable evidence: `data/manifests/stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json`.

Audit command:

```powershell
python scripts/audit_deprecated_ohlcv_salvage.py --write --strict
```

Observed result: `status: usable_as_salvage_evidence_with_limitations`.

## Evidence Summary

| Item | Result |
| --- | --- |
| Deprecated database files | No `.db`, `.sqlite`, or `.duckdb` database was evidenced during inspection. |
| Raw price parquet branch | `deprecated_version/legacy_snapshot_20260402T115014Z/data/interim/prices_daily/*.parquet`. |
| Adjusted price parquet branch | `deprecated_version/legacy_snapshot_20260402T115014Z/data/interim/adjusted_prices_daily/*.parquet`. |
| Source values | `twelve_data` in checked top-50 plus SPY price branches. |
| Top-50 coverage | `50/50` present in both raw and adjusted price branches. |
| SPY coverage | Present. |
| Checked ticker count | `51` including top-50 plus SPY. |
| Duplicate ticker-date rows | `0` in checked branches. |
| Null required OHLCV rows | `0` in checked branches. |
| Non-positive OHLC rows | `0` in checked branches. |
| Negative volume rows | `0` in checked branches. |
| Full-span OHLC order warnings | `1` CVX row on `2023-06-05`, outside the derived all-horizon candidate window. |
| Candidate-window OHLC order warnings | `0`. |

## Split And Adjustment Evidence

| Item | Result |
| --- | --- |
| Split events parquet | `deprecated_version/legacy_snapshot_20260402T115014Z/data/interim/split_events/split_events.parquet`. |
| Split events rows | `1506`. |
| Split event tickers | `360` unique event tickers; `43` overlap top-50 plus SPY. |
| Split request ledger | `deprecated_version/legacy_snapshot_20260402T115014Z/data/raw/split_events/split_event_request_ledger.parquet`. |
| Split request ledger coverage | `504` unique tickers; top-50 plus SPY request coverage evidenced. |
| Adjusted branch split-factor changes | `NFLX` has `501` rows with non-one cumulative split factor. |

## Clean-Window Candidate

The owner decision in `ScopeDecisionLog.md` DQ-021 selects a shorter verified overlapping clean historical window doctrine. The concrete candidate below is derived from audited OHLCV and 60-trading-step label feasibility; it is not a materialized dataset clean-window record.

| Field | Value |
| --- | --- |
| Full top-50 plus SPY price intersection | `2024-04-01` to `2024-12-30`. |
| All-horizon as-of candidate | `2024-04-01` to `2024-10-03`. |
| End-date driver | 60-trading-step forward-label availability across top-50 plus SPY. |
| Shortest history driver | `GEV`, first available on `2024-04-01`. |
| 60d base rows if selected | `6500` top-50 ticker-date rows. |

## Limitations

- Raw Twelve Data payload files under active `data/raw/twelvedata/` are still absent; this audit verifies deprecated parquet-derived price history.
- The deprecated snapshot remains reference-only. This audit reintroduces specific OHLCV evidence, not the whole archive.
- The all-horizon candidate window is not a materialized dataset version or benchmark run.
- Alpha Vantage news completeness and event-state construction are handled separately by the Stage 2 readiness gate.
- Sensitive Alpha Vantage raw ledgers/logs are not commit/share/publication-safe and were not included in this OHLCV audit output.

## Non-Claims

- No materialized benchmark dataset was created.
- No feature, label, split, model, prediction, metric, or benchmark result was created.
- No entire deprecated snapshot was promoted to active truth.
- No sensitive raw ledger or log was sanitized or cleared for commit/share/publication.
