# Event State Forecasting

End-of-day, multimodal, multi-horizon financial forecasting research codebase for a Master's-level thesis project.

## Status

This repository is now in the late foundation / early experimentation phase.

- The project structure, storage layout, and module boundaries are in place.
- Environment loading, provider clients, data contracts, and raw/interim/final dataset assembly are implemented.
- Split handling, market features, labels, embedding cache, event-state aggregation, and company-KB support are implemented.
- Market-only baselines, first-pass multimodal training, and first-pass evaluation/ablation tooling are implemented.
- The main remaining work is documentation hardening, richer evaluation/reporting, and later-stage research extensions.

The project is intentionally designed for:
- correctness,
- reproducibility,
- leakage safety,
- computational efficiency,
- and only then modeling sophistication.

## Project Identity

This project is **not**:
- a raw price-level prediction system,
- a trading bot,
- a high-frequency or intraday system.

This project **is**:
- an end-of-day research system,
- a multimodal, multi-horizon forecasting project,
- a temporal representation learning project,
- an event-state modeling project,
- a thesis-grade research codebase that must be academically defensible.

## Core Research Hypothesis

The central hypothesis is:

An aggregated temporal event state built from recent news, when combined with market data, can improve multi-horizon prediction of horizon-specific outcomes over market-only baselines.

Important modeling stance:
- The project explicitly avoids the assumption that one article maps cleanly to one isolated price effect.
- Financial news overlaps, narratives evolve, and market reactions are noisy and confounded.
- The project therefore models an evolving **event state**, not isolated article impacts.

## Research Problem Restatement

For each asset `i` and trading date `t`, the system should eventually consume:
- end-of-day market context from daily OHLCV and derived features,
- news available strictly **as of** the market close of `t`,
- optional company knowledge-base or profile information,
- and produce predictions for multiple forward horizons.

### What the project predicts

The project is intended to predict one or more of the following at horizons `1`, `5`, `20`, and optionally `60` trading days:
- forward returns,
- excess or abnormal returns,
- direction labels,
- downside risk labels,
- optional uncertainty-aware outputs such as scale or quantiles.

### What the project does not predict

The main thesis target is **not** future price level.

Why:
- price levels are non-stationary,
- scale differences distort evaluation,
- price-level prediction often hides weak methodology,
- return-based targets are more appropriate for rigorous financial ML evaluation.

## Why Event-State Modeling Instead of Isolated News Impact

The project chooses event-state modeling because:
- real-world news arrives continuously,
- several articles may describe the same underlying event,
- several distinct events may overlap in time,
- causal identification at the article level is methodologically fragile,
- predictive modeling is more honest when it treats recent information as a changing information state rather than as independent atomic events.

The event-state branch should therefore summarize recent article content over a lookback window with strict time alignment and a recency-aware aggregation rule.

## Why a Multimodal Setup Is Justified

The system is multimodal by design:
- numerical EOD market data,
- timestamped text data,
- optional firm metadata or profile information.

That means the project naturally belongs to multimodal ML and temporal representation learning, with the main challenges being:
- representation,
- asynchronous alignment,
- fusion,
- and out-of-sample generalization under noise.

## Why Multi-Horizon Forecasting Matters

This is not simply a “predict farther into the future” setup.

Different horizons can be driven by different mechanisms:
- `1d`: immediate reaction and short-term noise,
- `5d`: short-run drift or partial absorption,
- `20d`: medium-horizon repricing,
- `60d`: slower narrative or profile-related effects.

The project should therefore evaluate each horizon separately even when models share a common representation.

## Verified Current Project Context

The following should be treated as the current project reality.

### Market Data Source: Twelve Data

Verified current facts:
- provider: `Twelve Data`,
- plan context: Basic free tier,
- advertised credits: `8` per minute and `800` per day,
- `time_series` cost: `1` credit per symbol,
- daily bars use `interval=1day` and `outputsize=5000`,
- pilot symbols such as `AAPL`, `AMZN`, `BRK.B`, `BF.B`, `MSFT`, `NVDA` were successfully downloaded,
- stored market columns currently are:
  - `date`
  - `ticker`
  - `open`
  - `high`
  - `low`
  - `close`
  - `volume`
- example coverage for `AAPL` is roughly `2006-04-20` to `2026-03-05`.

Verified critical discovery:
- the stored series appears **not** to be split-adjusted,
- a check around `AAPL` on `2020-08-31` suggests pre-split prices remained near `124-126` instead of being back-adjusted near `31-32`.

Consequence:
- split and corporate-action handling is an open requirement,
- no serious label generation should trust raw OHLCV without resolving this issue.

### News Source: Finnhub

Verified current facts:
- provider: `Finnhub`,
- intended pipeline: company-news by ticker,
- timestamps should be normalized to UTC,
- later alignment must enforce strict EOD cutoff by exchange calendar,
- the system will store article-level records first, then aggregate them into event-state representations.

### SEC / Company Knowledge Base

Verified current direction:
- SEC-derived metadata is being considered for a company knowledge base,
- intended uses include:
  - better ticker-to-company mapping,
  - better firm descriptors,
  - cold-start support,
  - richer sector, business, and alias metadata.

Verified caution:
- company descriptions can leak future knowledge if used carelessly,
- any time-varying profile branch must use only information available up to the prediction date.

### Universe

Verified current facts:
- a current S&P 500 universe snapshot exists locally,
- it contains `503` rows,
- no duplicate tickers were found,
- dot tickers include `BF.B` and `BRK.B`,
- `pilot10.csv` exists and includes:
  - `AAPL`
  - `AMZN`
  - `BF.B`
  - `BRK.B`
  - `GOOGL`
  - `JPM`
  - `MSFT`
  - `NVDA`
  - `UNH`
  - `XOM`

### Software / Environment

Verified current facts:
- Linux environment,
- Python virtual environment available,
- dependencies installed through `pyproject.toml`,
- PyTorch should support CUDA if hardware is available,
- engineering priorities are reproducibility, speed, and maintainability.

## Data Sources and What Each Should Contribute

### 1. Twelve Data

Intended contribution:
- daily OHLCV market history.

Expected daily fields for this project:
- `date`
- `open`
- `high`
- `low`
- `close`
- `volume`

Benefits:
- works well for EOD-only research,
- simple symbol-based access,
- enough history for large-cap pilot work,
- manageable per-symbol request model.

Limitations:
- low free-tier daily quotas,
- split handling is unresolved on the current plan,
- full-universe daily refreshes are not practical on Basic,
- adjustment behavior must not be assumed.

Verified:
- `time_series`, `interval=1day`, `outputsize=5000`, and free-tier rate context.

Uncertain, verify manually:
- whether split or dividend endpoints are usable on the current plan,
- whether any provider-side adjustment flag changes the returned series in the exact way needed.

Concrete verification steps:
- hit split-related endpoints with the current plan and inspect the returned status,
- compare known split windows such as `AAPL 2020-08-31`, `TSLA 2020-08-31`, and `NVDA 2021-07-20` before trusting any adjusted flag.

### 2. Finnhub

Intended contribution:
- company-level news articles keyed by ticker and date range.

Recommended fields to store:
- `article_id`
- `ticker`
- `published_ts_utc`
- `headline`
- `summary`
- `source`
- `url`
- `image`
- `category`
- `related`
- `provider_id`

Benefits:
- ticker-scoped company news is a strong starting point,
- easier than full raw-web entity linking,
- natural fit for event-state construction.

Limitations:
- rate limits,
- possible duplicate or syndicated items,
- headline and summary quality vary by source,
- plan-specific throughput should not be assumed blindly.

Verified:
- company-news is the intended source and timestamps must be normalized to UTC.

Uncertain, verify manually:
- exact effective rate limits for the current plan,
- the long-run completeness of older article histories.

Concrete verification steps:
- run controlled chunk downloads and inspect rate-limit behavior and response headers,
- measure duplicate rates by URL and by hash of `(headline, datetime, source)`.

### 3. SEC EDGAR

Intended contribution:
- authoritative company identity and metadata,
- optional future profile branch,
- optional future entity-linking support if raw non-ticker-tagged news is added.

Recommended metadata to extract first:
- `cik`
- `ticker`
- `tickers`
- `exchanges`
- `name_current`
- `former_names`
- `sic`
- `sic_description`
- `business_address`
- `mailing_address`
- `entity_type`

Benefits:
- authoritative source for identity metadata,
- useful for ticker reconciliation and profile priors,
- suitable foundation for a future company KB.

Limitations:
- filing text parsing is more complex than metadata ingestion,
- profile text introduces leakage risks if not time-indexed,
- not all attractive fields are equally easy to extract cleanly.

Verified:
- SEC fair-access style user-agent handling is required,
- submissions JSON is the first endpoint family to implement.

Uncertain, verify manually:
- exact fields needed for a yearly time-indexed profile table,
- how much useful firm-description text can be extracted cheaply and safely for this thesis scope.

Concrete verification steps:
- inspect several real submissions JSON payloads for pilot firms,
- design the profile branch only after confirming which fields are stable and timestamp-safe.

### 4. Optional Wikipedia / Wikidata / Other Descriptive Sources

Potential contribution:
- extra aliases,
- general descriptions,
- background sector or business descriptors,
- future entity-linking support.

Benefits:
- potentially helpful for entity linking and cold start,
- easy to conceptualize.

Limitations:
- temporal leakage risk is high,
- licensing and redistribution issues matter,
- scraping and revision-history handling adds complexity.

Recommendation:
- postpone this until the main pipeline is correct,
- do not use current descriptions for historical periods unless time indexing is explicitly handled.

Uncertain, verify manually:
- licensing, revision-history workflow, and whether this is worth the scope cost for the thesis.

## Best-Practice Data Architecture

The project should use a layered architecture with immutable raw inputs and deterministic derived datasets.

### Storage layers

#### Raw
- immutable provider dumps,
- request ledgers,
- ingestion metadata.

Examples:
- `data/raw/twelvedata/...`
- `data/raw/finnhub/...`
- `data/raw/sec/...`

#### Interim
- normalized prices,
- normalized articles,
- split tables,
- company KB tables,
- adjusted prices.

#### Final
- market features,
- event-state features,
- optional profile features,
- label tables,
- final merged panel datasets.

#### Embeddings
- article-level embeddings,
- text hashes,
- model metadata,
- optional cached event-state vectors.

#### Runs and artifacts
- resolved configs,
- metrics,
- predictions,
- checkpoints,
- figures,
- tables,
- manifests.

### Canonical schemas to implement

#### Prices
- `date`
- `ticker`
- `open`
- `high`
- `low`
- `close`
- `volume`
- `source`
- `ingest_ts`
- optional adjusted columns later

#### News
- `article_id`
- `ticker`
- `published_ts_utc`
- `headline`
- `summary`
- `source`
- `url`
- `provider_id`
- `category`
- `related`

#### Split events
- `ticker`
- `split_date`
- `split_factor`
- `source`
- `ingest_ts`

#### Embeddings
- `article_id`
- `model_id`
- `embedding_dim`
- `embedding`
- `text_hash`
- `embed_ts`

#### Event state
- `ticker`
- `date`
- `state_vector`
- `news_count`
- `novelty`
- `conflict`
- `density`
- `lookback_days`
- `decay_half_life_days`

#### Company KB
- `ticker`
- `cik`
- `name_current`
- `former_names`
- `exchanges`
- `sic`
- `sic_description`
- `business_address`
- `mailing_address`
- `effective_date`
- `source`

#### Labels
- `ticker`
- `date`
- forward returns by horizon,
- excess returns by horizon,
- direction labels by horizon,
- downside labels by horizon,
- optional uncertainty targets.

### File format and processing choices

Recommended storage format:
- Parquet for most canonical tables.

Recommended processing roles:
- `pandas`: small and medium transformations, quick prototyping,
- `polars`: lazy and scalable columnar transformations,
- `duckdb`: large joins, filtered reads, and panel assembly over Parquet,
- `pyarrow`: storage and schema interoperability.

### Incremental update strategy

This is critical for Twelve Data Basic.

Recommended policy:
- backfill once,
- then refresh only missing dates with `start_date` and `end_date`,
- keep a request ledger per ticker,
- add a repair path for suspicious windows,
- never silently replace raw data without leaving a trace.

## Split / Corporate Action Handling

This is one of the most important components in the entire project.

### Why split handling matters

If splits are ignored:
- labels become mechanically corrupted,
- error metrics become misleading,
- ranking results become contaminated,
- model behavior around split dates can become meaningless.

### Why raw OHLCV breaks multi-horizon labels

A stock split introduces a large mechanical price jump and inverse volume jump.
If the series is not adjusted, forward returns can include false extreme moves that are not true economic returns.

### Recommended strategy order

1. **Best**: obtain explicit split events and back-adjust locally.
2. **Acceptable**: use already adjusted data only after manual verification.
3. **Temporary mitigation only**: exclude split windows and document the limitation.

### Current implementation path

- The current codebase is implemented around explicit local back-adjustment.
- The split-event source is currently treated as provider-agnostic through `src/data/split_events_client.py`.
- Until direct Twelve Data split access is verified on the active plan, the working assumption is:
  - use an audited secondary split-event source or audited local import,
  - normalize those events locally,
  - generate adjusted prices as a separate dataset branch.

### Back-adjustment math

For a split on date `d` with factor `s = new_shares / old_shares`:

For each date `t < d`:
- `open`, `high`, `low`, `close` are divided by `s`,
- `volume` is multiplied by `s`.

With multiple splits:
- apply the cumulative product of all future split factors to each earlier date.

### What must be tested

- known split dates no longer produce mechanical return spikes,
- volume adjustment direction is correct,
- top absolute returns are audited before and after adjustment,
- labels derived from adjusted prices differ materially from raw-label versions where expected.

### Current project risk

Verified risk:
- the current Twelve Data price history appears unadjusted at least for the tested `AAPL` split window.

Uncertain, verify manually:
- whether the current plan can provide split events directly,
- whether a secondary provider is needed.

## Company Knowledge Base / Profile Branch

The company KB idea is logically sound, but its importance depends on scope.

### Where it helps most

- entity linking for future raw mainstream news,
- cold-start support for newly added firms,
- static priors such as sector, SIC, exchange,
- potentially longer-horizon forecasting if carefully designed.

### Where it is less essential

- baseline experiments that already use ticker-scoped Finnhub company news,
- early market-only vs event-state comparisons.

### Recommended branch strategy

Start with:
- static identity and metadata branch only.

Postpone until later:
- time-varying descriptive profile branch,
- any profile-text embeddings.

Why:
- a time-varying profile branch is possible but leakage-sensitive,
- it adds complexity before the main event-state pipeline is proven.

## News Processing and Event-State Modeling

### Recommended article pipeline

1. Download company news by ticker and date chunk.
2. Preserve raw payloads.
3. Normalize timestamps to UTC.
4. Clean headline and optional summary text conservatively.
5. Deduplicate by URL first and by text-hash fallback second.
6. Precompute article embeddings offline.
7. Build per-ticker, per-date event-state features.

### EOD cutoff rule

This is mandatory:
- for a given prediction date `t`, only articles available by market close on `t` may enter that day's features,
- after-hours news must roll forward to the next valid trading day,
- all cutoff logic should be exchange-calendar-aware.

### Embedding strategy

Recommended first version:
- use precomputed dense embeddings,
- use headline plus summary when available,
- keep the text encoder frozen at first,
- cache embeddings by article hash.

Why not embed in the training loop:
- too expensive,
- harder to reproduce,
- harder to ablate,
- unnecessary for the initial thesis-grade system.

### Event-state pooling

Recommended baseline:
- recency-weighted aggregation over a fixed lookback window,
- plus scalar features such as:
  - `news_count`,
  - `novelty`,
  - `conflict`,
  - `density`.

Recommended realistic advanced extension later:
- attention-based pooling with strict ablation control.

## Market Feature Branch

The market branch should stay conservative.

Recommended initial features:
- simple returns,
- log returns,
- rolling volatility,
- rolling momentum,
- intraday range proxies from OHLC,
- volume ratios or rolling volume surprises,
- benchmark-relative features.

Optional later features:
- carefully selected technical indicators,
- factor-neutralized residual inputs,
- sector-relative context.

Avoid early feature bloat.

## Labels and Multi-Horizon Tasks

### Main target recommendation

Recommended primary target:
- forward excess return or abnormal return by horizon.

Recommended secondary targets:
- direction labels,
- downside-risk labels.

Optional later targets:
- uncertainty-aware targets such as predicted scale or quantiles.

### Label construction rules

- use adjusted prices whenever possible,
- respect the exact EOD cutoff used for features,
- handle missing horizons near the end of each series explicitly,
- keep label generation separate from feature engineering,
- document raw-return and adjusted-return variants for sensitivity analysis.

## Model Architecture Options

### Must-do baseline models

- ridge or elastic net,
- market-only MLP.

### Must-do main multimodal model

Recommended first main model:
- market encoder,
- event-state encoder,
- concatenation with gating,
- per-horizon output heads.

### Strongly recommended extension

- optional company-profile branch with static metadata only.

### Optional ambitious extension

- richer temporal encoders,
- uncertainty-aware output heads,
- attention pooling over news,
- end-to-end text fine-tuning only after baseline correctness is proven.

## GPU / CUDA / Efficient Training Design

Recommended engineering stance:
- CPU for raw ETL, normalization, joins, and many Parquet operations,
- GPU where it matters most:
  - article embedding precomputation,
  - neural model training,
  - optional calibration or uncertainty workflows if large enough.

Recommended first implementation choices:
- plain PyTorch instead of Lightning,
- mixed precision as an optional optimization,
- pinned memory and non-blocking transfers when helpful,
- one GPU first,
- distributed training only if clearly justified later.

Recommended workflow:
- precompute article embeddings offline,
- precompute or cache daily event states,
- keep training batches focused on the final panel rather than on raw token sequences.

## Evaluation, Validation, and Ablations

The project must use rigorous time-aware evaluation.

### Required validation strategy

- walk-forward validation,
- purge for overlapping forward-label windows,
- embargo where needed,
- no train/test leakage through scalers or feature normalization.

### Metrics to support

Regression:
- MAE,
- RMSE,
- `R^2`,
- Pearson and Spearman correlation.

Classification:
- AUC,
- PR-AUC,
- Brier score.

Ranking:
- daily information coefficient,
- ICIR,
- cross-sectional rank correlation.

### Core ablations

- market-only vs multimodal,
- split-adjusted labels vs raw labels,
- no-decay vs decay event-state pooling,
- embeddings vs sentiment-only,
- with-profile vs without-profile,
- single-horizon vs multi-horizon training.

## Common Failure Modes to Prioritize Against

Highest priority risks:
- look-ahead leakage,
- overlapping-label contamination,
- split/corporate-action mishandling,
- survivorship bias from a current index snapshot,
- timezone and market-close errors,
- duplicated news,
- train/test normalization leakage,
- temporal leakage from company descriptions,
- data snooping and too many unchecked variants,
- backtest overfitting,
- weak conclusions from short or regime-specific samples.

The codebase is structured so that these risks can eventually be tested explicitly rather than discussed only in prose.

## Software Engineering Plan

The repository is organized around a serious research-codebase workflow.

### Source layout

- `src/data/`: provider clients, pipelines, contracts, corporate actions, dataset assembly
- `src/features/`: market features, text normalization, embeddings, event state, labels, company features
- `src/models/`: baselines, multimodal models, losses, dataloaders, trainer, inference, statistical tests
- `src/split/`: walk-forward, purge/embargo, alignment rules, leakage checks
- `src/cli/`: thin orchestration commands
- `src/utils/`: config loading, paths, logging, I/O, reproducibility, time helpers

### Environment handling

- secrets live in local `.env`,
- `.env.example` is the public template,
- the implemented config loader reads local `.env` without printing secret values,
- required variables fail fast if missing.

### Testing plan

The `tests/` directory is organized around future high-risk checks:
- data contracts,
- corporate actions,
- alignment,
- leakage,
- labels,
- event state,
- walk-forward splits.

### Run tracking

Each future run should store:
- resolved configs,
- run metadata,
- dataset references,
- predictions,
- metrics,
- artifacts.

### Notebook policy

Notebooks are allowed for exploration and visualization only.
They should not become the source of truth for the production pipeline.

## Roadmap

Recommended implementation order:

1. Finalize config loading and provider clients.
2. Finalize market data ingestion and incremental updates.
3. Solve split handling and adjusted-price generation.
4. Build normalized interim price and news tables.
5. Build market features and labels.
6. Build article embeddings and event-state features.
7. Add SEC knowledge-base support.
8. Build final modeling panels.
9. Train market-only baselines.
10. Train multimodal models.
11. Run ablations and reporting.

## Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

or

```bash
pip install -e .
```

### 3. Create your local environment file

```bash
cp .env.example .env
```

Important:
- `.env` is local and private,
- it should never be committed,
- `src/utils/config_loader.py` is designed to use the local `.env` file by default.

### 4. CUDA note

If you need a CUDA-specific PyTorch build, verify the correct installation command from the official PyTorch installation selector before changing the local environment.

## Current Implemented Components

Already implemented at a minimal usable level:
- local `.env` loading and validation,
- project path resolution,
- YAML config loading,
- shared runtime utilities for:
  - logging setup,
  - JSON/Parquet/manifest I/O,
  - reproducibility metadata and seeding,
- canonical data contracts and schema validation helpers,
- the first executable automated test suite for data contracts,
- universe snapshot loading and validation helpers,
- provider-hardening utilities for:
  - Twelve Data,
  - Finnhub,
  - SEC EDGAR,
  - split-event normalization,
- executable smoke-style tests for data contracts and provider client hardening,
- incremental market-data planning, quality checks, and raw/interim market pipeline support,
- a working market-data CLI dry-run path for update planning and manifest-ready execution,
- split-adjustment math, diagnostics, and adjusted-price writing support,
- executable corporate-action tests,
- timezone, trading-calendar, and as-of-close alignment utilities,
- normalized news text selection and deterministic hashing helpers,
- canonical news ingestion pipeline and CLI dry-run path,
- executable alignment and news-pipeline tests,
- static SEC company-KB pipeline support with canonical company rows, ticker/CIK mappings, and alias tables,
- executable company-KB pipeline tests,
- conservative market feature builders from adjusted prices,
- multi-horizon label generation with excess-return, direction, and downside targets,
- executable label and Stage 8 leakage tests,
- offline article embedding cache support with deterministic hashing-based embeddings,
- daily event-state aggregation with recency weighting, novelty/conflict/density support, and no-news fallback,
- executable event-state tests,
- final modeling-panel assembly with manifest generation and optional event-state/company-feature joins,
- executable modeling-dataset assembly tests,
- walk-forward split generation, horizon-aware purged splits, and reusable leakage-check utilities,
- executable walk-forward and Stage 11 leakage tests,
- market-only baseline model factories for ridge, elastic net, and optional market MLP,
- baseline training, prediction export, checkpoint writing, and run metadata support,
- executable baseline training smoke tests,
- first multimodal market + event-state regressor with gating fusion,
- multimodal dataloader, training, checkpointing, and prediction export support,
- executable multimodal training smoke tests,
- regression/ranking evaluation helpers, calibration utilities, and statistical comparison helpers,
- ablation-summary generation and evaluation/report CLIs,
- executable evaluation and ablation smoke tests,
- thin provider clients for:
  - Twelve Data,
  - Finnhub,
  - SEC EDGAR.

Not yet implemented:
- richer multimodal architecture variants beyond the first gated fusion model,
- optional company-profile modeling branch in training,
- richer calibration/report generation extensions,
- broader statistical comparison coverage and thesis-ready reporting polish,
- broader leakage checks around full end-to-end experiment workflows.

## Must-Do Now

- finalize and test market ingestion against pilot symbols,
- implement canonical data contracts,
- implement incremental market-data updates,
- solve split-event sourcing and adjustment,
- build normalized Finnhub article tables.

## Strongly Recommended Next

- implement article embedding cache,
- implement event-state aggregation,
- build adjusted-price labels,
- implement walk-forward plus purge/embargo logic,
- benchmark market-only baselines before multimodal training.

## Optional Extensions

- static company-profile branch,
- time-varying profile branch,
- sentiment-only baseline branch,
- mainstream raw-news ingestion with entity linking,
- uncertainty-aware or distributional heads,
- multi-GPU training if clearly needed.

## Highest-Risk Unresolved Issues

- unresolved split-event sourcing on the current Twelve Data plan,
- exact adjustment behavior of provider-side price options,
- exact current Finnhub plan throughput and historical completeness,
- survivorship bias if only a current universe snapshot is used historically,
- potential leakage if profile text is introduced without time indexing.

## Final Principle

If a design choice improves apparent performance but weakens leakage safety,
reproducibility, or scientific defensibility, this project should reject it.
