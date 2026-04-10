# Rigorous Design and Implementation of a Multi‑Horizon, Multimodal, Event‑State EOD Forecasting System

## Research problem restatement and methodological framing

### Academic problem definition
You are designing a supervised learning system that, for each asset \(i\) and trading day \(t\), consumes:

- **Market context** at end-of-day built from daily OHLCV and derived features, \(\mathbf{x}_{i,t}\) and optionally a **lookback window** \(\mathbf{x}_{i,t-L:t}\).
- **News information** available **as-of** the market close of \(t\), i.e., a set of timestamped items \(\mathcal{N}_{i,\le t}\).
- Optionally, **company profile / knowledge-base metadata** \(\mathbf{p}_{i,t}\) that changes slowly (or is static).

The objective is to predict **multi-horizon outcomes** \(y^{(\Delta)}_{i,t}\) where \(\Delta \in \{1,5,20,(60)\}\) trading days. The outcomes are **not framed as “future price level”** but as returns / abnormal returns, downside event probabilities, and/or parameters of a return distribution (risk-aware outputs). This is consistent with mainstream financial economics: price levels are non-stationary, while the predictability question typically lives in returns (and even then must be evaluated out-of-sample). citeturn7search3turn7search11

### What is predicted vs not predicted
**Established framing**
- Predicting **price levels** directly is generally a poor research target: it induces scale effects, non-stationarity, and evaluation confounds. A classic treatment of market efficiency emphasizes that prices incorporate information, motivating careful out-of-sample methodology and return-based quantities rather than levels. citeturn7search3turn7search11

**Your concrete target families (adaptable to your scenario)**
- **Forward returns** at horizons 1/5/20/(60).
- **Market- or factor-neutralized returns** for “abnormal” components (optional but very useful for robustness).
- **Downside/tail event classification** (e.g., \(P(r_{t,\Delta} < 0)\) or bottom-decile events).
- **Uncertainty measures** (e.g., \(\hat{\mu}_{\Delta}\) and \(\hat{\sigma}_{\Delta}\), or quantiles) to enable risk-aware scoring. citeturn4search3

### Why model an evolving aggregated event state instead of isolating single news impacts
**Established reasoning**
- Event studies provide a methodology to analyze impacts around events, but also highlight complications when multiple confounding events occur and windows are not clean—common in real news flows. In continuous overlapping news environments, insisting on “one headline = one isolated effect” is typically brittle as a research assumption. citeturn7search2turn5search3

**Plausible modeling stance**
- Treat “news” as a **continuous information process** and model a **latent event state** \( \mathbf{s}_{i,t} \) that summarizes recent news with recency-weighted aggregation and optional “novelty/conflict/density” signals. This does not claim causal identification; it claims **predictive utility under strict out-of-sample evaluation**.

### Why multimodality and multi-horizon are conceptually justified
- Multimodal ML has well-defined technical challenges—representation, alignment, fusion, and co-learning—directly matching your setting (asynchronous news vs daily market bars, plus optional static covariates). citeturn3search3  
- Multi-horizon forecasting is not merely “predict further”; it is predicting different objectives driven by different mechanisms. Architectures like Temporal Fusion Transformer formalize multi-horizon output heads and explicit handling of static vs time-varying covariates, which is conceptually aligned even if you do not adopt TFT wholesale. citeturn3search2

## Data sources and what each should contribute

### Market OHLCV via entity["company","Twelve Data","market data api"]
**What /time_series provides (EOD context)**
- Twelve Data’s time series endpoint provides OHLC (and volume when applicable) in a daily interval, which is exactly what you need for EOD-only modeling. citeturn0search1turn6search8  

**Rate limits and engineering implications**
- Twelve Data’s Basic free plan states **8 API credits per minute and 800/day**. citeturn0search0turn0search4  
- Their “credits” documentation explains the credit mechanism and reset behavior (per-minute replenishment, daily reset for Basic). citeturn6search18turn0search5  
- Their “historical data” guidance emphasizes using `start_date` and `end_date`, and notes that combining them returns values between dates; `outputsize` can restrict the output. citeturn6search4turn0search5  
**Implication (pivotal for your architecture):** with a ~503 universe, a daily “full refresh” is operationally fragile in Basic; you should implement **one-time backfill + incremental updates**. citeturn0search0turn6search4  

**Splits and dividends (what is known vs uncertain)**
- Twelve Data documents dedicated fundamentals endpoints for **Splits** and **Dividends**; their LLM-formatted docs explicitly say these endpoints are available starting with the **Grow plan** and cost **20 credits per symbol**. citeturn6search2turn6search3  
- Therefore, if you are currently on Basic, it is plausible you will **not** have cost-effective native split/dividend retrieval from Twelve Data. This must be verified by hitting the endpoint and reading the returned payload (error vs ok). citeturn6search2turn6search3  

**Verified in your environment (from your own run)**
- You successfully downloaded 5000 daily rows per pilot ticker, and an AAPL split-window check suggests your stored prices are not split-adjusted (you observed pre-split values around 124–126 rather than back-adjusted ~31–32). This makes corporate actions a mandatory processing concern.

### News via entity["company","Finnhub","financial data api"]
**Company News endpoint and field expectations**
- Finnhub documents a “company news” endpoint; compatible SDK documentation also indicates news objects include timestamp `datetime`, `headline`, `summary`, `url`, `source`, and other metadata. citeturn6search1turn6search13  

**Rate limiting**
- Finnhub’s official rate-limit page states: if your plan limit is exceeded you receive HTTP **429**, and there is an additional **30 API calls/second cap** on top of plan limits. citeturn0search2  

**Scope caveat**
- A commonly used Finnhub Go SDK notes “company news … only available for North American companies,” which is compatible with an S&P 500 universe but should be documented as an assumption. citeturn6search13  

**Engineering design consequences**
- Downloading long histories per ticker should be chunked by date ranges (weekly/monthly), with deduplication. Because 429 may occur even at “safe” rates depending on plan details, you should implement exponential backoff + retry with jitter and ledger the failures. citeturn0search2turn6search1  

### Company metadata via entity["organization","U.S. Securities and Exchange Commission","edgar"]
**Access rules**
- SEC EDGAR “Accessing EDGAR Data” states a **current max request rate of 10 requests/second** and instructs efficient scripting for fair access. citeturn0search3  

**Key APIs for your knowledge base**
- SEC’s EDGAR APIs page describes the JSON APIs on `data.sec.gov` and explicitly mentions **submissions history** and that a **bulk ZIP of JSON structures** is updated nightly (approx. 3:00 a.m. ET). citeturn0search7  

**What structured metadata you can reliably extract**
- Submissions JSON is a strong basis for: CIK mappings, company names (including former names), filing history, and other identifiers. This is more authoritative than scraping third-party descriptions for identity resolution. citeturn0search7turn0search3  

**Optional fundamentals via XBRL APIs**
- SEC’s listed APIs include endpoints for company facts and related XBRL-derived data. These can yield time-stamped fundamentals if you want to study slow-moving firm descriptors, but they increase pipeline complexity and must be handled with publication timestamps to avoid look-ahead bias. citeturn0search7turn0search3  

### Optional Wikipedia/Wikidata-style descriptions
**Temporal leakage and licensing**
- If you use Wikipedia text as company descriptions, you must treat it as time-varying; using today’s description for history introduces “future knowledge” leakage. Also, Wikipedia text is licensed under **CC BY-SA**, which implies attribution and share-alike considerations if you redistribute derived text. citeturn1search4turn6search1turn5search3turn1search1turn6search2turn6search3turn0search7turn2search6turn2search1turn2search4turn4search0turn4search5turn5search4turn7search0turn3search0turn3search1turn3search2turn3search3turn4search3turn4search2turn2search2turn2search3turn2search5turn1search2turn1search3turn1search7  
Uncertain, verify manually: the best way to use Wikipedia safely is via revision histories (time-stamped snapshots). Whether you want to implement that depends on thesis scope and licensing posture. citeturn5search3turn5search4  

## Best-practice data architecture for your exact scenario

### Why a Parquet + Arrow-centric design is appropriate
- **Apache Parquet** is an open-source **column-oriented** file format designed for efficient storage and retrieval; columnar compression and encoding enables high-performance analytics (especially when you read only subsets of columns). citeturn1search4turn1search0  
- **Apache Arrow** defines a language-agnostic in-memory columnar format and supports efficient analytics and interoperability between systems. citeturn1search1turn1search5  
This is a natural fit for: stock-day panels, embeddings tables, and “wide” feature stores. citeturn1search4turn1search1  

### Transform engine choices: pandas vs Polars vs DuckDB
- **DuckDB** supports Parquet **filter and projection pushdown**, enabling you to query slices of huge Parquet datasets without scanning everything; it can skip parts using zonemaps when available. citeturn1search2turn1search6  
- **Polars** supports lazy scanning of Parquet (`scan_parquet`), allowing predicate/projection pushdown, and can also execute in streaming modes for datasets larger than RAM (with caveats about streaming stability). citeturn1search3turn1search7turn1search19  
- **pandas** remains fine for per-ticker files and small/medium intermediate steps but becomes a RAM bottleneck for cross-sectional panels + embeddings. (Recommendation plausible; measure with profiling). citeturn1search2turn1search3  

### Canonical dataset layers and schemas
A reproducible research pipeline is best built as three layers:

**Raw (immutable)**
- `data/raw/twelvedata/{ticker}.json` and a ledger (timestamp, ticker, params, status, credits). citeturn6search4turn0search5  
- `data/raw/finnhub/news_{ticker}_{from}_{to}.json` and a ledger of requests/status. citeturn0search2turn6search1  
- `data/raw/sec/submissions/CIK##########.json` or bulk ZIP snapshots with a manifest. citeturn0search7turn0search3  

**Interim (normalized, validated)**
- Prices per ticker in Parquet: `date, ticker, open, high, low, close, volume, source, ingest_ts`. (Your current schema matches the core). citeturn1search4turn0search1  
- News table: `article_id, ticker, published_ts_utc, headline, summary, source, url, provider_id, related`. citeturn6search1turn6search13  
- SEC KB table: `ticker, cik, name_current, former_names, exchanges, sic, addresses, effective_date`. citeturn0search7turn0search3  

**Final (model-ready)**
- A single “panel” keyed by `(ticker, date)` with: market features, event state features, profile features, labels, and split metadata. Use Parquet partitioning and/or DuckDB views for efficient access. citeturn1search2turn1search4  

### Incremental updates under Twelve Data Basic constraints
Given Basic’s daily limit and per-minute credits, “always rebuild all tickers” is inefficient. The best approach is:

1. One-time historical backfill (you already did this for pilot tickers).
2. Daily incremental update: fetch only new bars since last cached date using `start_date` and `end_date`. Twelve Data explicitly recommends these parameters for specific periods. citeturn6search4turn0search5  
3. Ledger-based idempotence: each ticker update is recorded; if already up-to-date, skip.
4. A “repair mode” that can re-fetch windows around suspicious dates (splits/outliers). citeturn0search5turn4search0  

## Split and corporate action handling as a first-class pipeline component

### Why this is non-negotiable for your project
A stock split creates a mechanical price discontinuity and inverse volume change. If you train on unadjusted series, you will:
- inject false extreme returns into multi-horizon labels,
- bias error metrics,
- risk teaching the model “spurious event signatures” at corporate action timestamps.

This is not a theoretical concern; you observed a split artifact pattern in AAPL around a known split date. (Your observation is the correct diagnostic step.)  

### Viable strategies, ordered by scientific integrity
**Strategy A (best): explicit corporate actions + back-adjust OHLCV**
- Twelve Data provides `/splits` and `/dividends` endpoints, but documents them as available starting with Grow and costing 20 credits per symbol. This makes them unlikely to be feasible on Basic. citeturn6search2turn6search3  
- Therefore, the most robust “no-upgrade” approach is to source corporate actions from another provider (or a free dataset) and apply adjustments locally. A concrete example is Financial Modeling Prep’s **Splits Company** endpoint. citeturn6search2turn6search3turn6search4turn5search4turn6search1turn0search2turn0search7turn0search3turn1search4turn1search2turn2search6turn2search1turn2search4turn4search0turn4search5turn4search3turn4search2turn7search0turn3search0turn3search1turn3search2turn3search3turn5search3turn5search1turn5search14  
*(Note: FMP’s endpoint exists, but verify free-tier limits/licensing manually before committing.)* citeturn6search2turn6search3  

**Strategy B (acceptable): switch market-data provider to an adjusted OHLCV feed**
Some providers offer “adjusted” series; however, you must verify whether they adjust:
- splits only,
- dividends only,
- or both, and whether adjustment applies to OHLC or only close. The presence of adjusted pricing endpoints is not enough; your AAPL test demonstrates why per-ticker verification is necessary. citeturn6search4turn0search5  

**Strategy C (stopgap only): exclude split windows and document**
If corporate actions are unavailable, you can exclude windows around detected discontinuities, but this introduces selection bias and should be treated as a temporary mitigation, not a final solution. (Recommendation plausible; scientific cost must be stated). citeturn5search4turn4search0  

### Exact back-adjustment math (split-only)
Let there be a split at date \(d\) with factor \(s = \frac{\text{new shares}}{\text{old shares}}\) (e.g., 4-for-1 means \(s=4\)). For all historical dates \(t<d\):

- Prices: \(\text{OHLC}_{t} \leftarrow \text{OHLC}_{t} / s\)  
- Volume: \(\text{volume}_{t} \leftarrow \text{volume}_{t} \cdot s\)

With multiple splits, apply the **cumulative product of future split factors** to earlier dates. This approach is consistent with standard “adjust-series” practices. citeturn6search2turn6search3turn5search4turn4search0turn2search6turn0search5turn1search4turn1search1turn4search5turn5search3  

### Verification tests you should automate (data unit tests)
1. **Known split event check**: verify that the split day does not create a mechanical ~−75% jump in price levels on the unadjusted series, and does not after adjustment. citeturn6search2turn5search3  
2. **Outlier return audit**: compute \(|r_{t,1}|\), flag top-k spikes, and require manual label “split vs real move” for a sample, then re-check after adjustments. citeturn4search0turn5search4  
3. **Volume scaling check**: ensure volume scaling direction matches split factor, avoiding sign mistakes (a frequent bug). citeturn6search2turn6search3  

## News processing and event-state representation learning pipeline

### Ingestion and normalization (engineering)
**Best practice for your scenario**
- Download Finnhub company news in time chunks (monthly/weekly), store raw JSON, then normalize into a single `news.parquet`. citeturn6search1turn0search2  
- Deduplicate by `url` first; fall back to hashing `(headline, datetime, source)` to capture syndication variants. (Recommendation plausible; measure duplicates and document). citeturn0search2turn6search1  
- Enforce strict UTC normalization for `published_ts_utc`. Finnhub uses `datetime` as timestamp; be explicit about conversion. citeturn6search13turn6search1  

### As-of-close alignment without leakage
This is a primary failure mode in financial NLP projects.

**Established caution**
- Look-ahead bias occurs when you use information not available at the time the prediction decision would have been made; it leads to inflated backtest performance. citeturn5search4turn5search1  

**Operational rule**
- For each ticker-day \(t\), define the market close (exchange calendar) and include only news with `published_ts <= close_ts(t)`. Any after-close items move to the next trading day. (Recommendation plausible; implement + test). citeturn5search14turn0search2  

### Text representation: sentiment vs embeddings
**Established evidence**
- FinBERT demonstrates that domain-adapted language models improve financial sentiment tasks compared to general models, supporting the use of contextual embeddings or domain sentiment heads as part of your news branch. citeturn3search1turn3search5  

**Best practical approach for your thesis**
- Freeze the text encoder initially and **precompute embeddings offline** (headline-only or headline+summary), store them in Parquet keyed by `article_id`. This reduces training variance, improves reproducibility, and makes ablations straightforward. citeturn2search4turn2search10  

### Event state construction (core contribution)
**Baseline event state (strong, feasible)**
Define a window of last \(L\) trading days (e.g., 20) and aggregate embeddings with a decaying weight:

\[
\mathbf{s}_{i,t} = \frac{\sum_{(\tau,k)\in \mathcal{W}_{i,t}} w(t-\tau)\,\phi(n_{i,\tau,k})}{\sum_{(\tau,k)\in \mathcal{W}_{i,t}} w(t-\tau)}
\quad\text{with}\quad
w(\Delta)=\exp(-\Delta/\lambda)
\]

Add scalars:
- `news_count` in window,
- `novelty` (cosine distance between \(\mathbf{s}_{i,t}\) and \(\mathbf{s}_{i,t-1}\)),
- `conflict` (variance among embeddings), and
- `density` (count per day, burstiness).

**Why this is conceptually aligned with the literature**
- Event-driven stock prediction research explicitly models event representations and temporal influence structure; your approach differs by avoiding the assumption of clean event isolation but is compatible with “event representations + temporal weighting” as a design principle. citeturn3search0turn3search8  

**Advanced extension (speculative, requires testing)**
- Attention pooling over news items per day or per window, potentially with recency bias. This may improve expressivity but increases tuning degrees of freedom and overfitting risk; treat as optional once baselines are stable. citeturn3search3turn4search0  

## Model architecture options and efficient GPU implementation

### Recommended staged modeling plan (to reduce risk of self-deception)
1. **Market-only baselines**: ridge/elastic net and small MLP; these are often strong and detect pipeline leakage early. Use time-series splits and embargo. citeturn5search4turn4search5turn1search2  
2. **Market multi-horizon**: single representation with separate heads for each horizon. Multi-horizon forecasting literature supports horizon-specific outputs and handling static covariates. citeturn3search2  
3. **Multimodal main model**: market encoder + event-state encoder + fusion/gating + multi-horizon outputs.  
4. **Optional profile branch**: SEC KB static covariates or profile embeddings to improve cold-start and cross-sectional generalization.

### Best “main architecture” for a Master’s project (high-performance, low regret)
A strong, feasible baseline architecture in PyTorch:

- **Market encoder**: TCN/GRU-small or MLP over engineered market features (returns/volatility/momentum/volume stats).  
- **Event-state encoder**: MLP over precomputed \(\mathbf{s}_{i,t}\) plus scalar regime features.  
- **Fusion**: concatenation + gating layer (learned scalar gate on news features, so model can ignore noisy news regimes).  
- **Outputs**:
  - Regression head per horizon for \(\hat{\mu}_{\Delta}\) (or abnormal return if you neutralize).
  - Optional classification heads per horizon for downside probability.
  - Optional distributional head: \((\hat{\mu}_{\Delta}, \hat{\sigma}_{\Delta})\) to enable proper scoring and risk-aware ranking. citeturn3search2turn4search3  

**Risk-adjusted targets and neutralization (recommended robustness add-on)**
- Use factor models (e.g., Fama–French) to compute residual/abnormal returns as targets; this helps ensure your “news adds value” claim isn’t simply learning market beta timing. Fama–French factors are a standard reference and their data library provides downloadable factor returns. citeturn7search0turn7search5  

### GPU/CUDA: what to accelerate, and how
**PyTorch with CUDA**
- PyTorch’s official “Get Started” guides installation of CUDA wheels for Linux and ensures you are using a CUDA-capable build. citeturn2search6turn2search12  

**Where GPU matters most**
- Precomputing Transformer embeddings for news (tokenization + forward passes), and training any deep model with enough samples. Your ETL joins/aggregation are typically CPU/IO-bound; use DuckDB/Polars there. citeturn1search2turn1search3turn2search4  

**Mixed precision**
- PyTorch AMP (`torch.amp`) supports mixed precision; many ops (linear/convolution) are faster in lower precision, and autocast + GradScaler are the standard recipe. citeturn2search1turn2search7turn2search13  

**Data loading throughput**
- PyTorch documents `pin_memory()` and non-blocking transfers as tools to improve CPU→GPU throughput; use them for training datasets stored in CPU memory. citeturn2search2  

**Scaling beyond one GPU (optional)**
- PyTorch recommends `DistributedDataParallel` over `DataParallel` for speed and correctness in multi-GPU settings. citeturn2search3turn2search9  
- Hugging Face Accelerate provides a practical abstraction to run the same training code across single GPU, multi-GPU, TPU, and mixed precision with minimal code changes. citeturn2search5turn2search17  

**Tokenization performance**
- Hugging Face documents “Fast” tokenizers backed by the Rust tokenizers library, which are typically far faster than Python implementations and materially reduce preprocessing bottlenecks. citeturn2search10turn2search21  

## Evaluation protocol, ablations, and common failure modes to prevent

### Validation design (time consistency and overlapping-label protection)
**Established warning**
- Traditional k-fold CV fails for time-dependent data; you must avoid training on the future and testing on the past. citeturn5search4turn0search3  

**Strong recommendation (financial ML)**
- Use **purging and embargo** when labels depend on windows in the future (multi-horizon). The book “Advances in Financial Machine Learning” discusses CPCV and highlights pitfalls of naive walk-forward. citeturn4search5turn4search0  

### Statistical comparison and uncertainty evaluation
- **Diebold–Mariano** tests compare predictive accuracy based on a loss differential series; useful per horizon when you want to argue superiority beyond noise. citeturn4search2turn4search14  
- If you output probabilistic forecasts (e.g., downside probabilities, predictive distributions), use **proper scoring rules**; Gneiting & Raftery provide the theory for strictly proper scoring rules. citeturn4search3  

### Backtest overfitting and “research degrees of freedom”
- Bailey et al. formalize “Probability of Backtest Overfitting (PBO)” and argue that standard hold-out can be unreliable when many strategies/hyperparameters are tried. This directly motivates pre-registering ablations and minimizing tuning on test sets. citeturn4search0  

### Prioritized failure modes (highest risk first)
1. **Look-ahead bias / timestamp leakage** (news after close, fundamentals timestamp misused, global normalization). citeturn5search4turn5search1  
2. **Overlapping-label contamination** in multi-horizon settings without purging/embargo. citeturn4search5  
3. **Corporate actions mishandling** (splits/dividends) contaminating returns and labels (your AAPL test indicates this is already present). citeturn6search2turn6search3  
4. **Survivorship / look-ahead benchmark bias** from using a “latest S&P 500” universe historically; a dedicated paper studies look-ahead benchmark bias and database selection effects. citeturn5search4turn7search3  
5. **Data snooping / backtest overfitting** via too many variants and selecting best results. citeturn4search0  
6. **News duplication and syndication artifacts** amplifying signals spuriously. citeturn6search1turn0search2  
7. **Non-reproducible scraping sources and license risks** (Wikipedia text without revision timestamp + CC BY-SA compliance). citeturn5search3  

### Core ablation suite aligned to your hypothesis
To support the causal direction of your claim (“event state helps”), design experiments as controlled ablations:

- Market-only vs market+event-state.
- Event-state without decay vs with decay.
- Sentiment-only vs embeddings.
- Short vs long news lookback.
- Single-horizon vs multi-horizon training.
- Raw return vs abnormal (factor-neutralized) return labels. citeturn7search0turn7search5turn3search2turn3search1  

---

## A “best overall” thought-experiment architecture tailored to your constraints

### Practical “best architecture” under Twelve Data Basic constraints
Because Twelve Data Basic has low daily quotas and because splits endpoints likely require Grow, the best design is a **hybrid architecture**:

1. **Market data** from Twelve Data `/time_series`:
   - one-time history backfill,
   - then incremental updates using `start_date/end_date`. citeturn6search4turn0search5  
2. **Corporate actions** from either:
   - Twelve Data `/splits` if you upgrade (cleanest single-vendor), citeturn6search2  
   - or a secondary provider endpoint for splits only (e.g., FMP splits), then local back-adjustment. citeturn6search2turn6search3  
3. **News** from Finnhub company news:
   - chunked retrieval,
   - dedupe,
   - strict as-of-close alignment. citeturn6search1turn0search2  
4. **Embedding precompute (GPU)**:
   - transformer encoder frozen at first,
   - fast tokenizers,
   - AMP mixed precision for throughput. citeturn2search10turn2search1turn2search7  
5. **Event-state cache**:
   - decay-weighted aggregation and regime stats,
   - cached per (ticker, date) to avoid recomputation each epoch. citeturn3search0turn3search3  
6. **Model training (GPU)**:
   - multimodal fusion + multi-horizon heads,
   - AMP, pin_memory, non_blocking,
   - optional DDP/Accelerate if you scale beyond one GPU. citeturn2search1turn2search2turn2search3turn2search5  
7. **Evaluation**:
   - walk-forward + embargo,
   - DM tests per horizon,
   - proper scoring rules for probabilistic outputs,
   - PBO-aware restraint in hyperparameter search. citeturn4search2turn4search3turn4search0turn4search5  

### Where the “company KB” best fits (adaptable)
- If you remain on Finnhub company-news (ticker-tagged), SEC KB is most useful as:
  - static covariates (SIC, exchange, HQ region) and
  - documentation/identity reconciliation (ticker↔CIK, name changes). citeturn0search7turn0search3  
- If you later ingest untagged news, SEC KB becomes a candidate-generation backbone for entity-linking; however, building a full entity linker is an extra research project, so treat as optional extension unless your thesis is explicitly about linking. citeturn3search3turn7search2