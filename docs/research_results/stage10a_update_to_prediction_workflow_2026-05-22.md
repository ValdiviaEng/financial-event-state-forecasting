# Stage 10A Update-To-Prediction And Visualization Research

Status: executed 2026-05-22 as research-only. This memo proposes a future local, artifact-driven update-to-prediction and visualization workflow. It does not implement code, call providers, mutate raw data, create prediction outputs, create visualization artifacts, expose a user-facing service/API, produce trading signals, reinterpret Stage 6, or change benchmark comparability.

## 1. Governing Boundary

Stage 10A is constrained by `AgentRules.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`, `ExecutionPipeline.md`, `UsageManual.md`, `docs/Data_Update_Strategy.md`, `Stage8Prompt.md`, `docs/Data_Separation_And_Overfitting_Control.md`, `configs/models.yaml`, and `configs/evaluation.yaml`.

Protected facts preserved here:

| Area | Preserved constraint |
| --- | --- |
| Target | Forward excess returns only. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | Approved top-50 family only unless separately approved. |
| Providers | Alpha Vantage news, Twelve Data OHLCV, SEC static/company support only. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Current result | Stage 6 remains `clean_null` with `limitation_bearing` comparability. |
| Deployment boundary | Local CLI/artifact-driven research only; no user-facing service/API/dashboard. |

## 2. Current Capability Assessment

| Capability | Current evidence | Stage 10A conclusion |
| --- | --- | --- |
| Raw daily/weekly refresh planning | Stage 8 scripts exist in plan-first mode. | Suitable as the raw-update entry point after explicit live-call approval if live execution is needed. |
| One-command update-to-prediction orchestrator | `ExecutionPipeline.md` says no single approved full-pipeline command exists. | Not evidenced in repository materials. Future work would need a new local orchestrator or explicit manual stage sequence. |
| Stage 2 through Stage 6 rebuild | Stagewise CLIs and validators exist. | Suitable for validated historical benchmark-style rebuilds after approved data changes. |
| Persisted fitted-model serving | `UsageManual.md` says this is absent. | Not evidenced in repository materials. Required for true arbitrary new-row scoring without rerunning training. |
| Current Stage 5 saved predictions | Saved predictions exist for validation and lockbox roles only. | Useful for extracting historical out-of-sample predictions, not enough by itself for fresh unlabeled forecast rows. |
| Visualization layer | No active visualization output exists. | Not evidenced in repository materials. Future Stage 10C must implement and validate from scratch if approved. |

Important blocker: the current Stage 5 contract writes saved predictions for `validation` and `lockbox` split roles only, and `configs/models.yaml` forbids `train`, `purged`, `embargoed`, and `excluded` roles. A future dated forecast packet needs either an approved new `forecast`/`prediction` role or a separate inference artifact design that does not pretend unlabeled future rows are benchmark rows.

## 3. Workflow Options

| Option | Description | Strengths | Risks | Stage 10A assessment |
| --- | --- | --- | --- | --- |
| Full Stage 2-6 rebuild | Refresh raw data if approved, rebuild Stage 2 through Stage 6, then read Stage 5/6 artifacts. | Maximum consistency with current validators, row digests, configs, and comparability records. | Mostly historical/evaluation-oriented; does not solve arbitrary same-day forecast scoring if future labels are unavailable. | Recommended as the benchmark-safe rebuild path, not as the whole future prediction-output solution. |
| Refresh plus full Stage 2-5 rebuild and prediction extraction | Use Stage 8 refresh, rebuild Stage 2 through Stage 5, extract latest saved predictions into a dated packet. | Keeps output tied to known artifacts and model roster. | Current saved predictions are split-bound evaluation artifacts, not a forecast-serving API. It may only work for historical rows with known split roles. | Acceptable only as a historical out-of-sample prediction packet unless Stage 10B approves a new forecast role/design. |
| Persisted inference package | Save fitted models, preprocessors, feature schema, and config hashes, then score feature-only rows for a cutoff date. | Correct direction for local dated forecasts without requiring future labels. | Requires new model packaging, feature-only row construction, strict train-only preprocessing records, no-leakage checks, and new tests. | Best long-term local architecture, but not currently evidenced and requires Stage 10B/10C approval. |
| Incremental update/scoring | Reuse unchanged artifacts and update only changed rows/features. | Potentially faster. | High stale-risk around row digests, labels, split boundaries, preprocessing fits, and provider-limitation flags. | Not recommended for first implementation. Defer until full rebuild and inference-package semantics are validated. |

Recommended Stage 10B default: approve a local-only dated prediction artifact design that starts with a conservative full-rebuild-or-explicit-inference-package path, not an incremental shortcut.

## 4. Candidate Dated Output Artifact

Proposed root:

```text
data/prediction_outputs/phase1_top50/<run_date>__cutoff_<data_cutoff>__src_<raw_digest>__rows_<row_digest>__stage5_<model_digest>__prediction_outputs_v1/
```

Proposed files:

| File | Purpose |
| --- | --- |
| `prediction_output_manifest.json` | Run date, data cutoff, source artifact roots, config hashes, row digest, model roster, generation mode, validation status, and non-claims. |
| `predictions.parquet` | Normalized prediction rows for all approved horizons and selected model outputs. |
| `top10_by_horizon.parquet` | Per-horizon top-10 forecast candidates after deterministic ranking. |
| `cross_horizon_summary.parquet` | Optional cross-horizon rank aggregation diagnostic. |
| `relevant_news.parquet` | Deterministically selected aligned news rows used for display context. |
| `trajectory_points.parquet` | Last-month observed context, historical out-of-sample predictions where available, and future forecast markers. |
| `limitations.json` | Provider truncation flags, no-news flags, late-start OHLCV flags, CVX patch note, clean-null caveat, and serving-mode limitations. |
| `report.html` | Optional offline static report generated from the packet. |
| `report_assets/` | Optional static CSS/PNG assets if Stage 10C approves static HTML output. |

The `generation_mode` field should be one of:

| Mode | Meaning |
| --- | --- |
| `historical_saved_predictions` | Extracted from existing Stage 5 saved predictions for validation/lockbox rows only. |
| `full_rebuild_saved_predictions` | Generated after a clean Stage 2-5 rebuild, still using approved split roles. |
| `approved_inference_package` | Generated by a future persisted model/preprocessor package for feature-only forecast rows. |

## 5. Prediction Row Schema Proposal

| Column | Required meaning |
| --- | --- |
| `prediction_run_id` | Stable identifier derived from output folder fields. |
| `run_date` | Local generation date. |
| `data_cutoff_date` | Maximum provider data date allowed for inputs. |
| `as_of_date` | Forecast as-of date. |
| `canonical_ticker` | Approved top-50 ticker. |
| `horizon_id` | One of `1d`, `5d`, `10d`, `20d`, `60d`. |
| `model_id` | Model producing the prediction. |
| `branch` | `market_only` or `event_state`. |
| `predicted_forward_excess_return` | Numeric forecast in the current target units. |
| `rank_within_horizon` | Deterministic rank for the same horizon and model/view policy. |
| `rank_policy_id` | Identifier for ranking tie-break rules. |
| `dataset_version` | Source Stage 2 artifact version if applicable. |
| `feature_artifact_version` | Source Stage 3 feature artifact version if applicable. |
| `split_artifact_version` | Source Stage 4 split artifact version if applicable. |
| `stage5_artifact_version` | Source model artifact version if applicable. |
| `raw_data_digest` | Digest of raw/provider inputs used by the packet. |
| `row_digest` | Digest of rows scored or extracted. |
| `provider_truncation_risk_flag` | Alpha Vantage limitation flag propagated to output rows. |
| `provider_empty_feed_flag` | Empty-feed limitation flag propagated to output rows. |
| `no_news_flag` | Stage 3 no-news state propagated to output rows. |
| `late_start_ohlcv_flag` | Ticker-level OHLCV history limitation flag where applicable. |
| `output_status` | `historical_prediction`, `forecast_candidate`, or `diagnostic_only`. |
| `claim_status` | Must state `not_trading_advice` and `not_benchmark_result` for Stage 10 outputs. |

The prediction packet must not include actual future realized returns for rows whose label windows have not elapsed.

## 6. Visualization Options

| Option | Description | Strengths | Risks | Stage 10A recommendation |
| --- | --- | --- | --- | --- |
| Static HTML plus CSV/Parquet | Single offline report with tables and lightweight plots backed by versioned data files. | Portable, auditable, no service boundary, easy to archive. | Requires exact data-report consistency tests. | Recommended default for Stage 10B. |
| PNG/CSV bundle only | Static image exports plus machine-readable tables. | Very low runtime complexity. | Less interactive and easier for tables/images to drift if not generated from one manifest. | Useful secondary export. |
| Notebook | Research notebook reading the packet. | Convenient exploration. | Harder to treat as stable artifact; execution order and environment can drift. | Development-only, not primary output. |
| Local dashboard | Local interactive app. | Better exploration. | Can resemble service/API scope, adds dependency and security burden. | Not recommended for first Stage 10C; require explicit approval if revisited. |

Static HTML is the safest first visualization because it remains local and artifact-driven without creating a service/API/dashboard scope.

## 7. Top-10 View Design

Required views:

| View | Contents | Caveat |
| --- | --- | --- |
| Per-horizon top 10 | Top 10 tickers per horizon, prediction value, rank, model ID, provider flags, no-news flag, and relevant-news count. | Forecast candidates only, not buy recommendations. |
| Cross-horizon consensus | Rank aggregation across `1d`, `5d`, `10d`, `20d`, and `60d`. | Diagnostic ranking only; horizons have different meanings and must not be collapsed into a trading score. |
| Model comparison | Optional side-by-side event-state model versus selected market hurdle. | Must display Stage 6 clean-null caveat prominently. |
| Limitation board | Rows with truncation risk, no-news, empty-feed, late-start OHLCV, or CVX patch lineage. | Limitations must be visible before any interpretation. |

Ranking tie-break proposal:

| Step | Tie-break |
| --- | --- |
| 1 | Higher `predicted_forward_excess_return`. |
| 2 | Lower provider limitation burden. |
| 3 | Higher aligned-news count where event-state model is selected. |
| 4 | Alphabetical `canonical_ticker` for deterministic final tie-break. |

The top-10 view should avoid words like buy, sell, long, short, trade, profit, target price, or recommendation unless a later explicit approval changes output status.

## 8. Relevant News Selection

Default deterministic selection should use Stage 3 aligned news rows only. It should not call providers, scrape articles, or run local LLM summarization.

Proposed ranking for display context:

| Priority | Signal |
| --- | --- |
| 1 | Same canonical ticker and available as of the forecast row. |
| 2 | Most recent article timestamp before the as-of-close cutoff. |
| 3 | Provider relevance score or ticker relevance field if present. |
| 4 | Provider topic tags if present. |
| 5 | Provider sentiment fields as metadata only, not as causal explanation. |

Required display caveats:

| Situation | Required wording |
| --- | --- |
| No aligned news | `No aligned Alpha Vantage news was available for this row under the current alignment rule.` |
| Truncation risk | `Provider-level article completeness is not claimed for this ticker/window.` |
| News shown | `Displayed news is input context, not proof of causal attribution.` |
| Optional future LLM summaries | `Not approved in Stage 10A; would require reproducibility, GPU/latency, prompt-stability, and source-text licensing review.` |

## 9. Prediction Trajectory Graph Design

Recommended static graph structure:

| Panel | Quantity | Rule |
| --- | --- | --- |
| Price/return context | Last month observed close or realized simple return. | Historical only; no projected price path. |
| Historical prediction markers | Prior out-of-sample predictions where realized labels already exist. | Align by prediction `as_of_date` and `horizon_id`. |
| Future forecast markers | Current predicted forward excess return per horizon. | Plot as markers at horizon endpoints or separate horizon lanes; do not connect as a realized future line. |
| Limitation overlays | No-news/truncation/empty-feed flags. | Visible flag badges or footnotes. |

Graph validation must verify that each marker uses the correct as-of date, horizon endpoint, model ID, and prediction value. Future realized returns must be absent until the label window has elapsed and the row is reclassified as historical.

## 10. Validation Checklist For Future Stage 10C

| Validation area | Required check |
| --- | --- |
| Manifest identity | Output folder fields match manifest fields and source artifact roots. |
| Row universe | All rows use approved top-50 tickers unless a new benchmark family is approved. |
| Horizon set | Only `1d`, `5d`, `10d`, `20d`, and `60d` appear. |
| Data cutoff | No news/OHLCV after `data_cutoff_date` is consumed. |
| Feature availability | Displayed news existed before the row as-of-close cutoff. |
| Model provenance | Every prediction maps to a model/preprocessor/config hash or Stage 5 saved-prediction row. |
| Rank determinism | Recomputing ranks from `predictions.parquet` reproduces `top10_by_horizon.parquet`. |
| Static report consistency | HTML tables and charts exactly match the packet data. |
| Non-claim enforcement | Report contains clean-null, limitation-bearing, provider-completeness, and not-trading-advice caveats. |
| Service boundary | No network listener, API server, credential use, or provider call is started by report generation. |

## 11. Stage 10B Decision Topics

Stage 10B should ask the owner to approve or reject these before development:

| Decision ID | Topic | Default recommendation |
| --- | --- | --- |
| S10B-DQ-001 | Output purpose | Local dated forecast-candidate artifact only, not trading advice or a service. |
| S10B-DQ-002 | Generation mode | Start with static artifact packet design; approve persisted inference package only if true future scoring is required. |
| S10B-DQ-003 | Model scope | Use `event_state_gated_fusion` plus selected market hurdle comparison by horizon; preserve full model metadata. |
| S10B-DQ-004 | Forecast row role | Add a new non-benchmark `forecast_candidate` role only after explicit design approval. |
| S10B-DQ-005 | Visualization format | Static HTML plus CSV/Parquet packet as primary; PNG optional; notebook development-only; no local dashboard initially. |
| S10B-DQ-006 | Top-10 ranking policy | Per-horizon top 10 with deterministic tie-breaks and visible limitation flags. |
| S10B-DQ-007 | Relevant news method | Deterministic aligned-news selection only; no LLM summarization by default. |
| S10B-DQ-008 | Trajectory graph | Historical observed context plus separate forecast markers; no projected price path. |
| S10B-DQ-009 | Validation bar | Require manifest, row, rank, report-consistency, cutoff, and non-claim tests before outputs are trusted. |
| S10B-DQ-010 | Sensitive artifacts | No raw API-key-bearing ledgers or provider secrets in prediction/report packets. |

## 12. Non-Claims

- Stage 10A did not implement update-to-prediction code.
- Stage 10A did not run Stage 8 live provider calls.
- Stage 10A did not mutate raw data.
- Stage 10A did not rebuild Stage 2 through Stage 6.
- Stage 10A did not create prediction output files or visualization files.
- Stage 10A did not create a live inference API, dashboard, web service, or user-facing service boundary.
- Stage 10A did not create buy/sell, long/short, trading-profitability, or price-target claims.
- Stage 10A did not reinterpret the Stage 6 `clean_null` result or promote Stage 7C diagnostics.

## 13. Recommended Next Step

Execute Stage 10B as a decision-matrix stage. Stage 10B should turn the decision topics above into explicit owner approvals before any Stage 10C development starts.
