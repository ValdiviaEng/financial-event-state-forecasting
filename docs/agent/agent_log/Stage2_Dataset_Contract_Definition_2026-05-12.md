# Stage 2 Dataset Contract Definition - 2026-05-12

Status: Stage 2 contract and blocker artifact, updated with 2026-05-14 active raw OHLCV reconciliation. This document defines the planned canonical benchmark dataset contract and records why dataset materialization is blocked. It does not create a dataset, active config, executable test suite, feature pipeline, split runner, model, benchmark runner, or benchmark result.

## Authority

| Source | Role |
| --- | --- |
| `AgentRules.md` | Governance, source hierarchy, approval gates, evidence discipline, and benchmark-comparability protection. |
| `ScopeDecisionLog.md` | Protected provider, universe, target, horizon, alignment, evaluation, and artifact-packet decisions. |
| `ResearchTruth.md` | Current truth synthesis and unresolved provider completeness risks. |
| `ProjectDefinition.md` | Broad phase-1 project definition and non-implementation boundaries. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Option B row identity, split-role, preprocessing, metric, saved-prediction, contamination, and diagnostic contract. |
| `docs/db_Testing.md` | Dataset validation expectations. |
| `docs/Pipeline_Testing.md` | Pipeline gate order and completion rule. |
| `Stage2Prompt.md` | Stage 2 execution requirements. |
| Stage 1 artifacts | Raw audit dependency evidence and blockers. |

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
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Option B refinement | Split manifests, fold-local preprocessing, predeclared metrics, saved out-of-sample predictions, contamination blockers, and overfitting diagnostics. |

## Dependency Status

| Dependency | Stage 2 status |
| --- | --- |
| Stage 1 raw audit | Completed as audit evidence. |
| Top-50 universe | Available from `data/raw/universe/top50_slickcharts_2026-04-10.csv`. |
| Alpha Vantage raw canonical file coverage | Available and parseable at `850/850` canonical windows. |
| Alpha Vantage article completeness | Provider-level completeness is not claimed; current canonical corpus is accepted with visible truncation limitation flags under latest user instruction. |
| Alpha Vantage empty feeds | `10` empty-feed windows must remain explicit statuses, not row drops. |
| Twelve Data OHLCV | Active raw Twelve Data 2010 full-window files now cover the approved top-50 plus SPY support with no post-first-available-date gaps in `data/manifests/twelvedata_ohlcv_coverage_2010_audit_2026-05-14.json`; deprecated parquet salvage remains reference-only fallback evidence. |
| SEC support | Not evidenced; verify only if needed for the dataset contract. |
| Sensitive raw ledgers/logs | `2` sensitive files are identified and excluded from dataset artifacts; they remain blocked for commit/share/publication until sanitized or isolated. |
| Executable dataset tests | Not present; current `tests/` tree is comment-only. |

## Stage 2 Decision

Stage 2 can define the dataset contract and blocker record, but cannot build a materialized benchmark dataset.

Current blocker:

- Executable dataset validation tests do not exist yet.

Resolved or narrowed since the original artifact:

- Active raw Twelve Data 2010 evidence now supports top-50 plus SPY OHLCV coverage for input-readiness purposes; deprecated Twelve Data parquet evidence remains reference-only fallback evidence.
- Clean-window doctrine is documented in `ScopeDecisionLog.md` DQ-021, and OHLCV-derived candidate bounds are available.
- Alpha Vantage truncation remains a visible limitation rather than a blocking input under the latest user instruction; no provider-level article completeness claim is made.
- Sensitive Alpha Vantage ledgers/logs remain unsafe for commit/share/publication, but they are excluded from dataset artifacts.

## Canonical Dataset Storage Contract

Planned storage convention, inactive until implementation and tests are approved:

| Artifact | Planned path convention | Required role |
| --- | --- | --- |
| Dataset root | `data/datasets/phase1_top50/{dataset_version}/` | Versioned immutable dataset artifact directory. |
| Canonical panel table | `data/datasets/phase1_top50/{dataset_version}/benchmark_panel.{table_format}` | Materialized row universe with required identity, availability, and label fields. |
| Dataset manifest | `data/datasets/phase1_top50/{dataset_version}/dataset_manifest.json` | Source, coverage, clean-window, row-count, schema, limitation, and hash evidence. |
| Row-universe digest | `data/datasets/phase1_top50/{dataset_version}/row_universe_digest.json` | Stable sorted row-key digest used for branch equality checks. |
| Clean-window decision | `data/datasets/phase1_top50/{dataset_version}/clean_window_decision.json` | Selected or blocked clean-window evidence. |

`{table_format}` remains implementation-pending. No storage engine is selected by this artifact.

## Dataset Versioning Policy

Future materialized dataset versions must be stable identities derived from:

- benchmark family ID
- dataset schema version
- protected scope values
- top-50 universe file identity
- Stage 1 and provider source manifests
- clean-window decision record
- sorted row keys
- label horizon set
- manifest hash and row-universe digest
- known exclusions and limitations

Planned version label shape:

| Version part | Meaning |
| --- | --- |
| `phase1_top50` | Approved first benchmark family. |
| `dataset_contract_v1` | Dataset schema contract version. |
| `{clean_window_id}` | Selected clean-window identifier after approval/validation. |
| `{source_digest}` | Digest over approved source manifests and provider evidence. |
| `{row_digest}` | Digest over sorted base row keys. |

No materialized dataset version is assigned in this Stage 2 artifact because no dataset was built.

## Row Identity Contract

Base dataset rows are unique at the benchmark row level:

| Field | Required status | Meaning |
| --- | --- | --- |
| `benchmark_family_id` | Required | Approved family identity, expected `phase1_top50`. |
| `dataset_version` | Required once materialized | Stable dataset identity. |
| `canonical_ticker` | Required | Repository ticker identity, including dotted tickers such as `BRK.B`. |
| `as_of_date` | Required | Prediction date for end-of-day row. |
| `prediction_timestamp` | Required | As-of-close prediction timestamp after alignment and calendar handling. |
| `horizon_id` | Required | One of `1d`, `5d`, `10d`, `20d`, `60d`. |
| `feature_availability_timestamp` | Required | Latest timestamp allowed to influence features. |
| `label_window_start` | Required | First future timestamp/date used by the horizon label. |
| `label_window_end` | Required | Final future timestamp/date used by the horizon label. |
| `row_status` | Required | `eligible`, `excluded`, or implementation-approved equivalent. |
| `exclusion_reason` | Nullable but required when excluded | Explicit reason for row removal from eligibility. |

Base-row uniqueness policy:

- unique key: `benchmark_family_id`, `canonical_ticker`, `as_of_date`, `horizon_id`
- duplicate base rows are fail-closed blockers
- null key fields are fail-closed blockers
- row equality checks must compare sorted unique keys and stable digest metadata

Fold-specific split records are separate from base-row uniqueness. When split manifests are materialized, their unique key is the base row key plus `fold_id` and split-role context.

## Option B Split-Eligibility Fields

The dataset or its companion split manifest must support these fields from the start:

| Field | Required status | Meaning |
| --- | --- | --- |
| `split_role` | Required once splits exist | `train`, `validation`, `development_test`, `embargoed`, `purged`, `lockbox`, or `excluded`. |
| `fold_id` | Required when fold-specific | Development fold identifier. |
| `lockbox_flag` | Required | Final untouched lockbox membership. |
| `purge_flag` | Required once splits exist | Row excluded by overlapping-label purge rule. |
| `embargo_flag` | Required once splits exist | Row excluded by embargo rule. |
| `split_exclusion_reason` | Required when split-excluded | Explicit reason for split-specific exclusion. |
| `preprocessing_fit_allowed` | Required once preprocessing exists | True only for active-fold training rows. |

Rows must have exactly one active evaluation role per fold context. Random time-shuffled assignment is forbidden for serious claims.

## No-News And Availability Contract

No-news days must stay in the row universe when market data and label feasibility allow the row.

Required availability fields:

| Field | Meaning |
| --- | --- |
| `market_data_available_flag` | Whether required OHLCV evidence exists for the row. |
| `news_provider_window_status` | Provider status for the relevant news window. |
| `aligned_news_count` | Count of aligned news items available as of the prediction timestamp. |
| `no_news_flag` | True when `aligned_news_count` is zero. |
| `empty_event_state_flag` | True when an explicit empty event state is used. |
| `provider_empty_feed_flag` | True when relevant raw provider window is an explicit empty feed. |
| `provider_truncation_risk_flag` | True when source news evidence is affected by likely truncation. |

No-news rows are not missing rows. Silent no-news row drops are benchmark blockers.

## Branch Row Equality Contract

Market-only and event-state branches must use identical base rows.

Required equality evidence:

- sorted base row-key file or equivalent manifest section
- row count by horizon
- row count by ticker
- row count by as-of date span
- stable row-universe digest
- missing/extra/duplicate/asymmetric row diagnostics

Any market-only versus event-state row drift blocks Stage 3 and all later benchmark claims.

## Dataset Manifest Schema

Future dataset manifests must include at least:

| Field family | Required contents |
| --- | --- |
| Identity | artifact type, schema version, dataset version, benchmark family ID, generated timestamp, generation command, code/config identity once applicable. |
| Protected scope | target family, horizons, universe ID/path, provider stack, alignment policy, no-news policy, evaluation doctrine, Option B contract reference. |
| Sources | universe file, OHLCV source manifests, news source manifests, Stage 1 audit manifest, SEC source manifests if used. |
| Coverage | date span, ticker count, expected/present provider windows, parse status, truncation status, empty-feed status, missing OHLCV status. |
| Clean window | selected window or blocked status, candidate windows, rejection reasons, approvals, limitations. |
| Rows and labels | total rows, rows by horizon, rows by ticker, label availability counts, excluded rows and reasons. |
| Availability | market/news availability indicators and no-news counts. |
| Separation | split-role fields, lockbox flag fields, fold fields, purge/embargo compatibility fields. |
| Hashes | source digests, row-universe digest, manifest digest, schema digest. |
| Limitations | unresolved provider completeness risks, credential safety status, implementation/test gaps. |
| Non-claims | explicit statement that dataset artifacts are not model or benchmark results. |

## Clean-Window Decision Record

The clean-window doctrine is selected by `ScopeDecisionLog.md` DQ-021: use a shorter verified overlapping clean historical window rather than maximum history. This artifact still does not create a materialized dataset clean-window record.

OHLCV-derived candidate from `data/manifests/stage2_deprecated_ohlcv_salvage_audit_2026-05-13.json`:

| Candidate field | Value |
| --- | --- |
| Price intersection across top-50 plus SPY | `2024-04-01` to `2024-12-30`. |
| All-horizon as-of candidate | `2024-04-01` to `2024-10-03`. |
| End-date driver | 60-trading-step forward-label availability across top-50 plus SPY. |

Earlier news-only candidate classes remain historical context from the first Stage 2 pass:

Candidate status based on Stage 1 evidence only:

| Candidate class | News evidence status | Selection status |
| --- | --- | --- |
| `2010-01-01` to `2020-12-31` | No Stage 1 likely truncation by year; includes the 10 explicit empty-feed windows from early years. | Not selected; OHLCV, label, split, and listing feasibility not evidenced. |
| `2016-01-01` to `2020-12-31` | No Stage 1 likely truncation and no Stage 1 empty-feed windows by year. | Not selected; OHLCV, label, split, and universe feasibility not evidenced. |
| `2021-01-01` to `2024-12-31` | `8` likely truncated Alpha Vantage windows by Stage 1 year summary. | Blocked until truncation policy/refinement is resolved. |
| `2025-01-01` to current | `84` likely truncated Alpha Vantage windows by Stage 1 year summary. | Blocked until truncation policy/refinement is resolved. |
| Full raw span `2010` to current | Complete canonical raw file coverage, but unresolved truncation after 2020 and no OHLCV evidence. | Blocked. |

The OHLCV-derived candidate supersedes the earlier OHLCV-absence blocker, but final dataset materialization still requires executable dataset validation and a concrete dataset version record.

## Required Executable Tests

These tests are required before Stage 2 can claim dataset-readiness implementation:

| Test family | Required blocker behavior | Current status |
| --- | --- | --- |
| Schema contract tests | Missing row keys, timestamps, horizons, label windows, split fields, dataset version, or manifest fields fail closed. | Not executable; scaffold comments only. |
| Universe tests | Top-50 parsing is deterministic; dotted tickers are preserved. | Not executable; scaffold comments only. |
| Panel tests | No-news rows are retained; missing market dates or duplicate rows fail closed. | Not executable; scaffold comments only. |
| Row-universe tests | Missing, extra, duplicate, or asymmetric branch rows fail closed. | Not executable; scaffold comments only. |
| Manifest tests | Missing source, version, coverage, limitation, and hash fields fail closed. | Not executable; future test file needed. |
| Split-eligibility tests | Split-role exclusivity, lockbox flags, purge/embargo fields, and fold IDs are enforceable. | Not executable; scaffold comments only. |

## Generated Artifacts

| Artifact | Role |
| --- | --- |
| `docs/agent/agent_log/Stage2_Dataset_Contract_Definition_2026-05-12.md` | Human-readable dataset contract, clean-window blocker, and Stage 3 blocker record. |
| `data/manifests/stage2_dataset_contract_definition_2026-05-12.json` | Machine-readable Stage 2 contract and blocker manifest. |

## Stage 3 Blockers

Stage 3 must not start feature/label implementation until these blockers are resolved or explicitly handled by approved stage rules:

- Twelve Data OHLCV raw evidence remains absent.
- Clean historical benchmark window is not selected.
- Alpha Vantage truncation policy/refinement remains unresolved.
- Sensitive raw ledger/log handling remains unresolved for commit/share/publication.
- Dataset builder and executable dataset validation tests do not exist.
- No materialized dataset manifest, row-universe digest, or row counts exist.

## Validations

| Check | Result |
| --- | --- |
| Governance validation | `VALIDATION PASSED`. |
| Stage 2 artifact consistency check | `STAGE2_ARTIFACT_CHECK PASSED`. |
| Comment-only scaffold validation | `COMMENT_ONLY_VALIDATION PASSED`. |

## Non-Claims

- This artifact does not create a materialized benchmark dataset.
- This artifact does not select a clean historical window.
- This artifact does not create executable tests.
- This artifact does not implement a dataset builder or CLI.
- This artifact does not create features, labels, splits, models, predictions, metrics, a benchmark runner, or benchmark result.
