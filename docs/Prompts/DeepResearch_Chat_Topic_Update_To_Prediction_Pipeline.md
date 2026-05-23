# DeepResearch Chat Topic: Update To Prediction Pipeline

Status: proposed deep-research chat prompt only. Do not execute repository code, call providers, change project scope, or approve implementation.

## Required Background Files To Read First

| File | Why |
| --- | --- |
| `ResearchTruth.md` | Current truth register through Stage 10C and active non-claims. |
| `ScopeDecisionLog.md` | Stage 8 and Stage 10B/10C approval boundaries. |
| `ExecutionPipeline.md` | Safe Stage 2-6 rebuild methodology after data or config changes. |
| `UsageManual.md` | Current local command usage, artifact interfaces, inputs/outputs, and artifact roots. |
| `docs/Data_Update_Strategy.md` | Refresh, invalidation, and provider-call constraints. |
| `Stage8Prompt.md` | Plan-first daily/weekly raw update tool boundary. |
| `Stage10APrompt.md` | Research-only update-to-prediction workflow analysis. |
| `Stage10BPrompt.md` | Decision topics and selected Stage 10C architecture constraints. |
| `Stage10CPrompt.md` | Implemented local packet boundary and current exclusions. |
| `data/manifests/stage10c_completion_validation_2026-05-23.json` | Current Stage 10C packet validation status. |

## Repository Context

This repo currently has a local CLI/artifact-driven Stage 2 through Stage 10C workflow for a top-50 event-state forecasting benchmark. Stage 6 produced a `clean_null` result with `limitation_bearing` comparability. Stage 8 added plan-first daily/weekly raw update scripts. Stage 10C added a local dated prediction-output packet from existing Stage 5 saved predictions, with static HTML plus CSV/Parquet artifacts, top-10 views, deterministic aligned-news context, and trajectory markers.

Current Stage 10C rows are `historical_prediction` rows from saved validation/lockbox predictions, not true fresh future inference. There is no live inference API, persisted fitted-model serving interface, dashboard, scheduled update-to-output job, or one-command daily update-to-prediction orchestrator.

Protected scope: target is forward excess returns; horizons are `1d`, `5d`, `10d`, `20d`, `60d`; universe is approved top-50; providers are Alpha Vantage news and Twelve Data OHLCV; evaluation uses purged-plus-embargoed walk-forward plus final untouched lockbox.

## Research Ask

Research best-practice designs for a future local daily/weekly update-to-prediction pipeline that starts from refreshed raw OHLCV/news data, rebuilds or reuses stage artifacts safely, and emits dated prediction outputs. Compare full rebuild, incremental rebuild, and persisted-model inference packaging against the current Stage 8 plus Stage 10C baseline.

## Questions

| Question | Desired answer |
| --- | --- |
| Orchestration pattern | What local CLI/runner pattern is safest and easiest to validate? |
| Artifact identity | How should dated output folders encode run date, data cutoff, dataset version, feature version, split version, model version, and row digest? |
| Incremental vs full rebuild | When is incremental scoring valid, and when must Stage 2 through Stage 6 be rebuilt? |
| Model packaging | What artifacts are needed for arbitrary new-row scoring beyond current saved predictions? |
| Stage 10C compatibility | How should future true forecast rows coexist with current `historical_prediction` packets without changing prior evidence? |
| Leakage controls | What checks prevent refreshed data from leaking future labels or lockbox feedback? |
| Validation | What tests and manifests should be mandatory before outputs are trusted? |

## Desired Output

Return a cited research memo with options, tradeoffs, recommended local-only architecture, validation checklist, implementation risks, and explicit non-claims. Do not recommend a user-facing web service, dashboard, trading execution system, live provider execution, or benchmark reinterpretation unless clearly marked out of current scope and approval-gated.
