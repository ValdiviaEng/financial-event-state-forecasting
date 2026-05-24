# Stage 3 Feature And Label Pipeline Readiness - 2026-05-13

Status: Stage 3 dependency and blocker artifact, updated after 2026-05-14 active raw OHLCV and truncation-refinement reconciliation. This document records why feature and label implementation is blocked, and preserves the allowed feature/label contract boundaries for future work. It does not create market features, event-state features, labels, active config, executable tests, a split runner, a model, a benchmark runner, predictions, metrics, or a benchmark result.

## Authority

| Source | Role |
| --- | --- |
| `AgentRules.md` | Governance, truth hierarchy, approval gates, evidence discipline, and benchmark-comparability protection. |
| `ScopeDecisionLog.md` | Protected target, horizon, provider, universe, alignment, no-news, evaluation, and artifact-packet decisions. |
| `ResearchTruth.md` | Current truth synthesis and unresolved implementation risks. |
| `ProjectDefinition.md` | Broad phase-1 project definition and non-implementation boundaries. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Option B row identity, feature timestamp, label-window, row-equality, and contamination contract. |
| `docs/db_Testing.md` | Dataset and row-identity validation expectations. |
| `docs/Pipeline_Testing.md` | Pipeline gate order and completion rule. |
| `Stage3Prompt.md` | Stage 3 execution requirements and stop conditions. |
| Stage 2 artifacts | Dataset contract and explicit Stage 3 blockers. |

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
| No-news policy | Preserve rows with explicit empty event state and no-news indicators. |
| Event representation | Pooled dense embeddings plus scalar enrichments. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Option B refinement | Split manifests, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, contamination blockers, and overfitting diagnostics. |

## Dependency Status

| Dependency | Stage 3 status |
| --- | --- |
| Stage 2 contract artifact | Present at `docs/agent/agent_log/Stage2_Dataset_Contract_Definition_2026-05-12.md` and `data/manifests/stage2_dataset_contract_definition_2026-05-12.json`. |
| Materialized Stage 2 dataset artifact | Not evidenced in repository materials. Blocks feature and label artifact generation. |
| Dataset manifest and row-universe digest | Not evidenced in repository materials. Blocks row-equality validation. |
| Executable dataset tests | Not evidenced in repository materials. Current `tests/` tree remains comment-only. |
| Twelve Data OHLCV evidence | Active raw Twelve Data 2010 full-window files cover the approved top-50 plus SPY support with no post-first-available-date gaps in `data/manifests/twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json`; not a materialized Stage 2 dataset. |
| Clean historical benchmark window | Doctrine documented and active-raw OHLCV-derived all-horizon candidate is `2024-04-01` to `2026-02-13`; not owner-selected and not a materialized dataset clean-window record. |
| Alpha Vantage truncation policy/refinement | Current canonical news corpus is accepted with visible limitation flags under latest user instruction. Refinement still reports quarterly `planned=282`, `valid=22`, `missing=260`, `truncated=6`, `pending=260`; monthly `planned=16`, `valid=16`, `missing=0`, `truncated=12`, `pending=0`; latest plan reports budget remaining `19/25`. |
| Sensitive raw ledger/log handling | Identified and excluded from dataset artifacts; unresolved for commit/share/publication. |
| Exact excess-return benchmark reference series | Not evidenced as an active frozen implementation choice. Blocks executable label formulas. |
| Exact embedding model and scalar enrichment list | Not evidenced as active config. Blocks event-state implementation beyond high-level contract. |

## Stage 3 Decision

Stage 3 can record contracts and blockers, but cannot build feature or label artifacts.

Reasons:

- Stage 3 requires a versioned, manifest-backed Stage 2 dataset artifact; Stage 2 explicitly did not materialize one.
- Feature and label tests are still comment-only and cannot enforce as-of safety, news alignment, no-news retention, row equality, or label-window correctness.
- Stage 2 has OHLCV evidence and a candidate window, but it still has no versioned materialized dataset, row digest, or final clean-window record.
- Alpha Vantage provider-level article completeness is not claimed; future event-state artifacts must carry truncation and empty-feed limitation flags.
- The exact excess-return benchmark reference series is not frozen in active implementation/config evidence.
- Choosing an embedding model or scalar enrichment list now would silently extend the event-state contract beyond current active config evidence.

## Future Market Feature Contract

This contract is documentation-only until a materialized dataset and executable tests exist.

| Requirement | Future enforcement |
| --- | --- |
| Row keys | Features must preserve `benchmark_family_id`, `dataset_version`, `canonical_ticker`, `as_of_date`, and `horizon_id` where horizon-specific rows exist. |
| Availability | Every feature row must record `feature_availability_timestamp`. |
| As-of rule | Market features may use only information available at or before the prediction timestamp. |
| Future OHLCV | Future OHLCV used for label windows must not enter feature fields. |
| Missing data | Missing OHLCV must produce explicit row status or exclusion reason, not silent imputation or row drift. |
| Branch equality | Market-only and event-state branches must share the same base row universe. |

## Future News Alignment Contract

This contract preserves the approved alignment policy without implementing it.

| Case | Required future behavior |
| --- | --- |
| Same trading day at or before market close | Eligible for that as-of-close prediction row if the article timestamp is available by prediction timestamp. |
| Same trading day after market close | Roll forward to the next valid trading date; do not assign backward to the closed prediction row. |
| Non-trading day article | Roll forward to the next valid trading date. |
| Timestamp uncertainty | Fail closed or record explicit exclusion/uncertainty reason; do not silently include future information. |
| Provider status | Preserve truncation, empty-feed, and provider-message status in feature manifests. |

## Future Event-State Contract

This contract records approved boundaries only; it does not select an embedding model.

| Component | Required future behavior |
| --- | --- |
| Dense representation | Use pooled dense embeddings only after an explicit model ID, text preprocessing policy, pooling policy, and artifact metadata are recorded. |
| Scalar enrichments | Use only scalar enrichments that are available as of prediction timestamp and documented in a resolved config. |
| Article references | Preserve aligned article IDs or stable references sufficient for audit. |
| Provider limitations | Carry provider truncation and empty-feed flags into manifests. |
| Row equality | Event-state artifacts must not create or drop rows relative to the dataset row universe. |

## Future No-News Contract

| Requirement | Future enforcement |
| --- | --- |
| No-news retention | Rows with zero aligned articles remain eligible when market and label data are otherwise available. |
| Indicators | `aligned_news_count=0`, `no_news_flag=true`, and `empty_event_state_flag=true` or active equivalents must be present. |
| Empty provider feed | Provider empty-feed windows must be recorded separately from ordinary no-news rows. |
| Truncation risk | Rows affected by likely truncated provider evidence must carry explicit limitation flags. |

## Future Label Contract

This contract preserves the approved target family and horizons but does not implement labels.

| Requirement | Future enforcement |
| --- | --- |
| Target family | Forward excess returns only unless explicit approval changes the target family. |
| Horizons | Exactly `1d`, `5d`, `10d`, `20d`, and `60d` for phase 1. |
| Label windows | Every label row must record `label_window_start` and `label_window_end`. |
| Benchmark reference | A fixed benchmark reference series must be selected and documented before executable label generation. |
| Endpoint handling | Rows lacking full future label windows must be explicitly excluded or marked unavailable; no silent horizon drop. |
| Leakage boundary | Label-window data must not influence feature construction, preprocessing, split selection, or model fitting. |

## Required Future Executable Tests

| Test family | Required blocker behavior | Current status |
| --- | --- | --- |
| Market feature tests | Future OHLCV leakage and missing-data drift fail closed. | Not executable; scaffold comments only. |
| News alignment tests | Same-day, after-hours, and non-trading-day behavior match approved policy. | Not executable; scaffold comments only. |
| Event-state tests | Event-state rows preserve row universe and carry aligned article metadata. | Not executable; scaffold comments only. |
| No-news tests | No-news rows are retained and encoded explicitly. | Not executable; scaffold comments only. |
| Label tests | All approved horizons have correct label windows and forward excess-return fields. | Not executable; scaffold comments only. |
| Row equality tests | Market-only, event-state, and label artifacts share the required row keys. | Not executable; scaffold comments only. |

## Generated Artifacts

| Artifact | Role |
| --- | --- |
| `docs/agent/agent_log/Stage3_Feature_Label_Pipeline_Readiness_2026-05-13.md` | Human-readable Stage 3 dependency, blocker, and future contract record. |
| `data/manifests/stage3_feature_label_pipeline_readiness_2026-05-13.json` | Machine-readable Stage 3 blocker manifest. |

## Stage 4 Readiness

Stage 4 is not ready. It requires Stage 3 feature and label artifacts, row-equality evidence, feature availability timestamps, label windows, and executable validation outputs. None are present.

## Non-Claims

- This artifact does not create market feature artifacts.
- This artifact does not create event-state feature artifacts.
- This artifact does not create label artifacts.
- This artifact does not create executable tests.
- This artifact does not create a final clean-window record for a materialized dataset version.
- This artifact does not select an exact excess-return benchmark reference series.
- This artifact does not select an embedding model or scalar enrichment list.
- This artifact does not create splits, models, predictions, metrics, a benchmark runner, or benchmark result.
