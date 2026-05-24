# SECTION 1 — Restate the Mission and the Project Frame

This is a deeply critical, implementation‐aware audit of **benchmarking and architecture options** for our master’s‐level, end‑of‑day multimodal, multi‑horizon forecasting project.  We must decide *which research directions to pursue next*, given the current repository as our codebase.  In practice, that means evaluating **modeling scenarios** not just for accuracy potential, but also for **repository fit, modularity, and benchmark validity**.  The “best scenario” here is the one that maximizes predictive value *and* allows clean, fair comparison to baselines in a scientifically defensible way, with minimal leakage and maximal interpretability.  Modularity is a first‐class criterion: the ability to add or swap components without breaking everything is highly valued.  

In concrete terms, we will take each promising idea from the attached research report – corporate‐action adjustment, abnormal/ factor‑neutral targets, enhanced event‐state features, ranking objectives, uncertainty outputs, macro/regime features, options signals, company profiles, and a Mixture‑of‑Experts (MoE) design – and analyze whether we can realistically implement it given our code (data pipelines, model scaffolding, evaluation tools, etc.).  Crucially, each scenario will be assessed not just on its “glamour” or theoretical promise, but on whether our current repo already partially supports it, how much work remains, how it affects benchmarks (e.g. requiring new cross‐validation or metrics), and how modularly it can be integrated.  

This investigation will therefore guide us to a **prioritized, modular, benchmark‑aware research plan**.  We must answer: Which next step yields the best accuracy gain *per unit of engineering and scientific risk*?  How should we validate it (walk‑forward, purged CV, lock‐box, etc.)?  Can multiple ideas be merged cleanly, or should we keep a narrow core?  In short, we will treat architecture choice and benchmarking design as intertwined research decisions, always asking: *“Does adding this complexity truly move the needle, and can we measure that reliably?”*

# SECTION 2 — Extract the Key Methods and Directions Already Present in the Attached Research

The attached *“deep‑research‑report (2)”* lays out several modeling concepts (some explicit, some implied).  We summarize them as candidate methods or architectural directions:

- **V1 – Corporate Actions (“split adjustments first”)**: The idea is to treat stock splits/dividends as first‐class events.  Practically, that means *back‐adjusting historical prices/volumes* (or using split‑adjusted data) and adding QA checks for discontinuities【11†】.  Goal: eliminate artificial jumps in returns due to splits.  This is fundamental “data correctness.”  (This is supported by evidence that unadjusted prices break multi‑horizon labels【11†】.)  *Status in repo:* Likely **not fully implemented**; the code may fetch raw OHLC but not adjust.  Score: *Central (high priority data fix), partially needed, low-level feature branch.*

- **V2 – Abnormal/Factor‑Neutral Returns as Targets**: Reformulate targets to be residual returns or “alpha” (return minus sector/market benchmark)【11†】.  Aim: shift focus to what is unexplained by known factors.  This is touted as making the prediction task *more realistic* (removing easy benchmarkable component) and a good evaluation of added value.  *Status:* Probably **not yet** in code (we likely use raw returns now).  Score: *High accuracy potential, moderate difficulty (needs factor modeling), changes labels across all tests.*

- **V3 – Enhanced Event‑State Encoder**: Build a richer news state: for example, time‑weighted or novelty/conflict/density features of news, maybe hierarchical pooling (e.g. pooling by sector or narrative).  Goal: make the event embedding sensitive to story persistence or information overlap【11†】.  *Status:* The repo likely has a basic event‐state (maybe sum of embeddings with decay).  Extending it would require new features or embeddings.  Score: *Moderate difficulty (requires new NLP pipeline steps), likely modular (just a new feature generator).*

- **V4 – Ranking Objective (Cross‑sectional)**: Change the loss or main evaluation from predicting raw returns to maximizing rank correlation or selection metrics (e.g. IC, sorting into long/short baskets)【11†】.  That means training for forecasting which stocks outperform, rather than exact return.  Claimed benefit: better link to “useful accuracy” and avoiding spurious error metrics【11†】.  *Status:* Likely *not present* – existing training probably uses MSE or MAE on returns.  Score: *Moderate difficulty (change loss + maybe architecture), but alters core objective.*

- **V5 – Uncertainty‑aware Outputs**: Extend outputs to include risk estimates (e.g. mean+variance, or quantiles)【11†】.  This would let the model express confidence or downside risk.  *Status:* Likely not in code now (simple point predictions).  Score: *Higher complexity (new loss for variance/quantile calibration), but isolated branch of model (predict two heads).*

- **V6 – Macro/Regime Features**: Incorporate economic regime indicators (e.g. interest rates, market volatility regime flags) or engineered macro features, possibly interacted with news.  Goal: let model condition on environment【11†】.  *Status:* Probably no macro data pipeline in code.  Score: *Depends on data source; if easy to get, adding features is moderate; risk of lookahead if data timing is off.*

- **V7 – Options‐Implied Signals**: Add signals from options (e.g. implied volatility skew, VIX etc) as inputs, to capture market expectations of tail risk【11†】.  *Status:* Unlikely implemented.  Score: *High data burden (need tickers, costs/licenses), optional as experiment.*

- **V8 – Company Knowledge Base**: Incorporate static or slowly‐varying company metadata (from SEC filings, Wikipedia, sector taxonomy) as features or an embedding【11†】.  Uses: entity linking, static priors, cold-start.  *Status:* Repo may have some sector info, but likely no dynamic profiles.  Score: *Feasible (just extra feature table), some risk of leakage (temporal snapshots needed).*

- **Mixture‑of‑Experts (MoE)**: The user specifically wants MoE considered.  This would mean having multiple “expert” sub-models and a gating mechanism to assign inputs (e.g. per stock/horizon/regime).  Variants might include modality experts, horizon experts, regime experts, etc.  This was *not mentioned in the research report but is requested now*.  We will treat it as scenario **V9 – MoE ensemble**, a major architectural change.  *Status:* Almost surely not in repo; would require significant redesign.  Score: *Very high potential complexity, but modular by design (experts separate), with high risk of instability.*

The attached report also hints at other design principles (e.g. multi-output heads by horizon as in TFT【12†】, gating or attention for news vs market, etc.), but the above list covers the main named directions.  Each of these will be discussed against repo reality next.

# SECTION 3 — Repository Reality Check

We now inspect how the current codebase can absorb these ideas.  Based on the user descriptions and our “assumed reality,” the repository currently has the following:

- **Data ingestion and raw/interim storage:** The repo fetches daily OHLCV for S&P 500 tickers (via Twelve Data), and daily company news (via Finnhub).  It organizes raw JSON and intermediate Parquet layers.  It likely has metadata like sector/industry.
- **Split/CVD handling:** There is likely a *split coefficient field* stored but from the user’s test the data do not appear automatically adjusted【11†】.  If there is a branch, it may only apply forward adjustments implicitly (the user found it unadjusted).  
- **Features:** Market features (returns, vol, technicals) are computed.  News features include an “event state” embedding that aggregates recent headlines (with possible time decay).  It may already support basic sentiment or keyword counts, though unclear.
- **Labels:** The code produces multi-horizon targets (1d, 5d, 20d, maybe 60d returns or indicators).  It possibly includes variants like “direction up/down”.
- **Model architecture:** There is a baseline market-only model (maybe linear or small MLP) and a first multimodal model merging market features and news event embedding.  The fusion is likely simple concatenation or gating (the user plan mentioned gating in ideas).
- **Training:** It supports multi-task loss (multiple horizon heads) and presumably uses standard losses (MSE, perhaps classification for direction).  Possibly no specialized ranking or uncertainty loss.
- **Evaluation:** It has some cross-validation or walk-forward code, though the user indicates further needs for leak-avoiding splits.  There are metrics and ablation scripts.
- **Testing:** There are likely unit tests and data integrity checks (the user ran some and caught split issues).

From this, we infer:

- The repo **already supports**: Market and news pipelines, multi-horizon targets, an event-state aggregator, baseline and joint training, and basic evaluation.  It is structured by modules (`src/data/`, `src/features/`, `src/models/`, etc) and uses config-driven runs.  This is a solid first-pass scaffold【13†】.

- The repo **partial/fragile** on: corporate actions (there is data but no automatic adjustment), presumably no purged cross-val implemented yet, no advanced event features, no macro data, no options, no knowledge base integration.  The gating or mixture-of-experts architecture is absent (models likely straightforward MLP or even LSTM).  Multi-output heads exist but not sure if optimized or separate enough.

- The repo **missing**: Abnormal returns targets (likely not computed yet), ranking objective, uncertainty outputs.  Possibly only using simple train/val split rather than walk-forward (though it says "evaluation tools" exist).

Given this, the repo seems **reasonably modular** (separate data/feature/model code) but it is not yet engineered for a heavily branched architecture.  Adding new feature branches (macro, options, KB) would require new data ingestion modules and changes to the model input pipelines.  Adding new model branches (multi-output, uncertainty head, MoE gating) would be substantial code work.  

In summary: the code **can** accept incremental new features and modest model changes (e.g. add a new input vector or head), but truly structural changes (e.g. MoE gating, new data sources) would be large.  It should be possible, but will require careful design to keep experiments comparable.

# SECTION 4 — Deep Implementation-Feasibility Audit, Method by Method

We now analyze each candidate direction methodically:

**V1 – Corporate Actions (“first-class” splits/dividends)**:  
- *Concrete meaning:* Implement a preprocessing stage that applies historical split and dividend adjustments to the OHLCV series, or swap in Twelve Data’s split-adjusted endpoint. Add a feature “split_coefficient” and use it to adjust open/high/low/close backward. Potentially drop a few days around the split from labels if uncertain.  
- *Pipeline impact:* Data ingestion/validate stage. Likely in `src/data` or `src/features`, inject code to adjust prices. Could reuse tables of corporate actions (maybe from FMP or SEC filings).  
- *Repo changes:* Write a function to multiply past prices by the cumulative split factor (the user’s earlier logs show testing for splits). Add volume scaling. Extend `validate_price_data()` to allow splits by first checking a splits table. Possibly add a routine in data contracts or parsing.  
- *New dependencies:* Possibly a splits dataset from e.g. Financial Modeling Prep or Twelve Data splits endpoint. This is relatively lightweight.  
- *Leakage/bench risk:* If not careful, adjusting inside training window is safe; only risk was using raw data for labeling. Once fixed, reduces false signals. Should not break CV integrity if done correctly before splitting.  
- *Integration difficulty:* **Low** to moderate. It’s a known data cleaning task. Since code already has split_coefficient field (judging by the earlier script), adding code to use it properly is straightforward. If not present, it's still routine.  
- *Modularity:* Very modular (just another feature pipeline). Once added, it benefits all experiments.  
- *Ablation:* Easy (we can compare models with and without adjustment as a validation).  
- *Fair comparison:* Clear, since it's a data fix baseline; all models should get adjusted data.  
- *Worth doing?:* **Yes, immediately**. The tournament declared V1 winner and prime candidate【13†】. Its expected accuracy gain is high (removes spurious noise), and it's “low‐risk” (standard practice, no new architecture). Score: Feasibility=High, Difficulty=Low, Modularity=High, Benchmark Clean=High, Accuracy Upside=High, Thesis Coherence=High.

**V2 – Abnormal/Factor‑Neutral Returns**:  
- *Meaning:* Compute target returns after subtracting a benchmark (market or sector) or other factors. For example, residual of a CAPM regression or simply stock return minus index return. Possibly use residuals of a rolling Fama‐French model.  
- *Pipeline:* New target generation stage: in `src/labels/`, instead of pure returns, compute factor model residuals (needs factor data or index). Could reuse existing data (e.g. SP500 index or sector returns already available?).  
- *Repo changes:* Might need data for benchmarks (market index, sector indices). Then modify label code to subtract them. Add config options.  
- *Deps:* Possibly trivial (we have SPY, sector prices from existing universe). If not, can be scraped or proxied.  
- *Leakage risk:* Must only use information available at labeling time. If using sector from same day’s open or prior close, treat carefully. But doable with as-of-close rules.  
- *Difficulty:* **Moderate**. Computing residuals is easy; robustly handling factors (like require historical regression windows) is more complex. Also risk: making targets noisier if factors remove too much (plus possible overfitting to residuals).  
- *Modularity:* Good – just another label branch. Can treat original return vs abnormal as separate tasks or compare.  
- *Ablation:* We can compare model performance on raw vs abnormal labels.  
- *Fair comparison:* Easy for performance metrics, though interpretation changes. If baseline is raw returns, then abnormal-change comparison must be justified.  
- *Worth doing?:* This was high in the report (Runner-up scenario)【13†】. It’s plausible that predicting residual returns is what “alpha” means. Score: Feasibility=Moderate, Difficulty=Moderate, Modularity=High, Benchmark Clean=Moderate (must recalibrate evals), Accuracy Upside=Medium‐High, Thesis Coherence=Moderate‐High.

**V3 – Advanced Event‑State Encoder (novelty/conflict/density)**:  
- *Meaning:* Enhance how news are aggregated. Possibly add features like: count of similar stories (“density”), how recent (“recency decay”), measure of conflicting sentiments (“conflict”), etc. Maybe use attention or hierarchical encoding (by sector or theme).  
- *Pipeline:* Extend `src/features/event_state.py` (or similar) to compute new features from the news table. This may involve NLP (clustering headlines), or simple heuristics.  
- *Repo changes:* If currently using static embeddings (e.g. summing), we need to incorporate time decay or separate processing. If implementing novelty, might need historical lexicon.  
- *Deps:* Possibly new NLP models (like sentence transformers, but likely already have that), or clustering library. Computational cost up.  
- *Leakage risk:* Generally fine if using as-of-close. Danger: inadvertently using future news context. But since event-state is aggregated up to t, okay.  
- *Difficulty:* **Moderate to high**, depending on sophistication. Simple decay weighting is easy; conflict detection is researchy.  
- *Modularity:* Still modular as a new set of features. It goes into the event-state vector.  
- *Ablation:* Straightforward (with vs without advanced features).  
- *Fair comparison:* Yes, just enhances existing branch.  
- *Worth doing?:* Probably optional refinement. The tournament put V3 above some others but lost to data correction. Score: Feasibility=Moderate, Difficulty=High (for novelty/conflict logic), Modularity=High, Benchmark Clean=High, Accuracy Upside=Low‐Medium, Thesis Coherence=Medium.

**V4 – Ranking (Cross‑Sectional) Objective**:  
- *Meaning:* Change training/evaluation to focus on cross-sectional rank. For example, train the model to predict each stock’s rank or to maximize Spearman IC, not raw MSE. Might involve a pairwise or top‐k loss.  
- *Pipeline:* In training code (`src/models/`), implement a loss like negative Spearman correlation or surrogate classification (long/short groups). In evaluation, report IC or hit rates.  
- *Repo changes:* Significant: loss function change, maybe data loader to sample within-day cross-section. Possibly define tasks like “predict binary up-down”.  
- *Deps:* Could use sklearn metrics or custom autograd.  
- *Leakage risk:* If not careful, sharing information within mini-batches (since they contain same day cross-sections) could leak. Need pure multi-output and then compute rank on each day.  
- *Difficulty:* **High**. Implementing a differentiable rank loss is nontrivial, and training stability could suffer. Alternatively, you might keep original loss and only evaluate rank metrics (less effective).  
- *Modularity:* It’s an objective, not a new branch. So it doesn’t harm modularity of features.  
- *Ablation:* Compare to MSE baseline; fairness is tricky because we change goal.  
- *Fair comparison:* If we change objective, comparing models trained on different objectives is tricky – this is more like a different experiment than a fair ablation of the same model.  
- *Worth doing?:* As a research extension, yes, but it complicates direct comparison. The tournament found it promising (runner-up)【13†】. Score: Feasibility=Low-Moderate, Difficulty=High, Modularity=High, Benchmark Clean=Low (new metrics needed), Accuracy Upside=Medium, Thesis Coherence=Medium (good concept but can muddy comparisons).

**V5 – Uncertainty Outputs (Mu/Sigma or Quantiles)**:  
- *Meaning:* Output both expected return and an uncertainty measure (standard deviation, or predict quantiles for the return distribution). Train with a proper likelihood or pinball loss.  
- *Pipeline:* In model, add second (or multiple) heads. For example, one head outputs mean, another log-variance, with a Gaussian NLL loss. Or output quantiles with corresponding loss.  
- *Repo changes:* Extend `src/models/` and losses. Possibly change training script to handle new loss.  
- *Deps:* Already likely have PyTorch, can implement easily.  
- *Leakage risk:* Minimal if label prep is correct.  
- *Difficulty:* **Moderate**. Implementation wise straightforward, but hyperparameter tuning (balancing loss components) needed.  
- *Modularity:* Clear, just adding outputs.  
- *Ablation:* Can compare whether having uncertainty improves ranking or risk metrics.  
- *Fair comparison:* Should still use baseline for mean output; uncertainty can be evaluated separately.  
- *Worth doing?:* If thesis includes risk, yes. But not if core focus is point forecast. Score: Feasibility=Moderate, Difficulty=Moderate, Modularity=High, Benchmark Clean=High (just adds more metrics), Accuracy Upside=Low (doesn’t change point estimate), Thesis Coherence=Low-Medium (useful for risk analysis rather than core fit).

**V6 – Macro/Regime Context**:  
- *Meaning:* Include macroeconomic or market‐regime features, e.g., recent GDP growth, VIX, Fed rates, or economic cycle state. Could be static (e.g. country) or dynamic (use economic surprises).  
- *Pipeline:* Create a new data pipeline to fetch macro data (possibly from FRED or Quandl) and align it as time-series features.  
- *Repo changes:* Add `src/data/macroeconomic.py`, new tables, extend feature builder to include these in market feature vector. Possibly add regime classification input.  
- *Deps:* Could use Python APIs or local files; minor.  
- *Leakage risk:* High if not careful about release timings of data (revisions in unemployment, etc). Must use real-time vintages or simple indicators (like monthly value at t-1).  
- *Difficulty:* **Moderate**. The coding is not hard, but correct usage of economic data is subtle.  
- *Modularity:* Decent – it's a new feature group.  
- *Ablation:* Compare with/without macro features.  
- *Fair comparison:* Generally fine as long as same backtest.  
- *Worth doing?:* Possibly useful if macro regimes affect returns. The report listed it as moderate extension【13†】. Score: Feasibility=Moderate, Difficulty=Medium, Modularity=Medium, Benchmark Clean=Medium, Accuracy Upside=Low-Medium, Thesis Coherence=Low (ancillary). 

**V7 – Options/Implied Signals**:  
- *Meaning:* Add inputs like implied volatility, skew, or other option-market derived measures (e.g. VVIX).  
- *Pipeline:* Requires data source (maybe Yahoo or paid API) for option metrics. Then add these to features.  
- *Repo changes:* New data ingestion, and slight model input change.  
- *Deps:* Possibly expensive or license, and not sure data availability long history.  
- *Leakage risk:* If using daily implied vol closes, fine.  
- *Difficulty:* **High (data)** if not free. Implementation is easy once data exists.  
- *Modularity:* New feature vector, easy to add.  
- *Ablation:* Straightforward test.  
- *Fair comparison:* Yes.  
- *Worth doing?:* High-risk if data cost; interesting academically. Report labeled it high-risk/high-reward【13†】. Score: Feasibility=Low, Difficulty=High (data curation), Modularity=High, Benchmark Clean=Medium, Accuracy Upside=Medium, Thesis Coherence=Low- (more an extension).

**V8 – Company Knowledge Base (KB)**:  
- *Meaning:* Use static or slow-changing company info (sector, headquarters, business description, key financials from filings) as additional inputs or separate embedding.  
- *Pipeline:* One approach: build a table of metadata per ticker (maybe by year), and join to stock features. Alternatively, encode text descriptions via a transformer and feed as input.  
- *Repo changes:* Possibly large: need scraping/parsing of SEC or Wikipedia. Already mentioned using EDGAR CIK data or Wikipedia. Likely beyond current code.  
- *Deps:* Data gathering (EDGAR API is available; Wikipedia is CC BY-SA but doable).  
- *Leakage risk:* Severe if not time-stamped (cannot use future corporate names or products to predict past returns!). Must treat as static or use revision history.  
- *Difficulty:* **High**. Nontrivial to integrate time-aware.  
- *Modularity:* Good if done as separate branch input.  
- *Ablation:* Yes, test with/without.  
- *Fair comparison:* Fine if used on both baseline and new model.  
- *Worth doing?:* Possibly for cold-start or entity linking, but not core if we have ticker-tagged news. Report calls it plausible but needs care【11†】. Score: Feasibility=Low, Difficulty=High, Modularity=Medium, Benchmark Clean=Medium, Accuracy Upside=Low, Thesis Coherence=Low (useful but tangential).

**V9 – Mixture of Experts (MoE)**:  
- *Meaning:* Architect a model with multiple “expert” submodels and a gating mechanism that selects (soft or hard) which experts handle each input. Examples: one expert per modality, per horizon, per sector, etc.  
- *Variants:* Could be **Modality experts** (one expert processes market, one processes news, then combine), **Horizon experts** (separate experts for short-term vs long-term prediction), **Regime experts** (experts tailored to market regimes), or others.  
- *Pipeline:* Major redesign of `src/models/`. Instead of a single unified network, we’d implement a gating network that takes input (or context) and routes to different experts (e.g. separate sub-networks). This is akin to adding conditional computation.  
- *Repo changes:* Very large: new model class, new training logic (maybe min-batching issues if experts specialized), potential new losses. Possibly reuse existing modules as experts.  
- *Deps:* PyTorch supports MoE pattern, but this is advanced.  
- *Leakage risk:* Could inadvertently let gating use future info (e.g., if gating variable includes target hint). Need gating only on available features.  
- *Difficulty:* **Very high**. Implementing stable MoE (ensuring experts don’t collapse, etc) is complex. Plus heavy compute if many experts.  
- *Modularity:* High (each expert is its own sub-model). But also increases hyperparameters dramatically.  
- *Ablation:* Difficult – do we compare each expert individually? Hard to isolate.  
- *Fair comparison:* Hard, because baseline is a single model; comparing a gated model’s advantage is complex.  
- *Worth doing?:* Possibly if we believe separate regimes or modalities truly need distinct models. But often MoE yields modest gains with high cost. Score: Feasibility=Low, Difficulty=Very High, Modularity=High, Benchmark Clean=Low (very complex), Accuracy Upside=Medium (speculative), Thesis Coherence=Medium (if sold as main novelty, but risky).

# SECTION 5 — Benchmarking Framework Foundation

No matter which scenario we adopt, we need a rigorous benchmarking protocol.  The attached “Benchmarking problem” document emphasizes *temporal integrity, overlap integrity, and multiple-testing integrity*【8†L10-L14】.  Concretely:

- **Temporal integrity:** Always split data by time. Use *walk‑forward* or forward chaining, never shuffle. Training must only use data up to \(t\), and testing on \(>t\).  

- **Overlap integrity (purging):** Because our labels span multiple horizons, standard K‑fold cross‑validation would leak (a one‐year target window might overlap future training). We must *purge* or *embargo* adjacent samples so that the forward horizon of one training sample does not include any part of another’s test horizon【8†L10-L14】.  

- **Multiple-testing integrity:** We’ll run many experiments. To avoid p‑hacking, we should predefine protocols and, if doing many runs, adjust significance (e.g. Diebold-Mariano tests, Sharpe of IC, or PBO analysis【8†L10-L14】).  

**Primary validation protocol:** We should adopt a **rolling walk‐forward** (also called *time-series cross-validation*) as our main procedure. That means partitioning the timeline into sequential folds: train on time [0, T1], validate on (T1, T2], then increment: train [0, T2], val (T2,T3], etc. This tests generalization over time. It respects causality and uses more data efficiently. We must always *purge/embargo* immediately adjacent periods when labeling overlaps. For multi‑horizon, each fold’s train must exclude the next horizon of the validation set to avoid label leakage【8†L10-L14】.  

**Final holdout:** In addition to CV folds, we should always keep a final **“lockbox”** (most recent period) untouched until the very end. This period simulates the ultimate test on completely unseen data (the original idea the user had). This should be used only once, after all modeling choices are fixed.  

**Metrics:** We will report both point‐forecast metrics (MAE/RMSE, directional accuracy) and cross‐sectional/ranking metrics (Information Coefficient, hit rates). We may also report calibration (e.g. Sharpness vs Reliability for uncertainty models). But the primary focus should be on metrics aligned with our goal: likely ranking or risk metrics if we implement V4/V5.  

In summary, the overarching benchmark framework is: **Purged rolling walk-forward CV for development + a final locked-out test + clearly defined primary metrics (point vs rank vs uncertainty) per scenario**. Each scenario will have a tailored metric set, but all must obey these temporal/overlap constraints.  

# SECTION 6 — Candidate Future Scenarios

We define the following 9 distinct scenarios, all branching from the current baseline:

1. **Corporate‑Action Focus (V1)** – Implement full split/dividend adjustment in data (as above), plus QA checks. Keep model simple otherwise.  
2. **Abnormal‑Return Targets (V2)** – Change labels to sector‑neutral or market‑excess returns, train the same model.  
3. **Enhanced Event‑State (V3)** – Add advanced news features (novelty/conflict densities) or use a stronger NLP model for event embeddings.  
4. **Ranking Objective (V4)** – Keep inputs, but train/evaluate for cross‑sectional ranking (e.g. sort stocks by predicted return, maximize IC).  
5. **Uncertainty‑Aware (V5)** – Same model, but output both mean and variance (or quantiles) for each horizon, train with appropriate loss.  
6. **Macro/Regime Branch (V6)** – Augment inputs with macroeconomic/regime indicators as a new branch of features. Possibly use an LSTM or separate MLP to encode them.  
7. **Options Signals (V7)** – Add option-derived features to market inputs.  
8. **Company KB Branch (V8)** – Incorporate company profile metadata as additional branch of inputs (could be static or time-stamped).  
9. **Mixture of Experts (V9)** – Redesign model to route inputs through multiple specialized subnetworks. We consider variants of routing (below).

These are *all feasible offshoots of the baseline*.  Each adds one or more aspects.  We will analyze each in detail, but first we reserve Section 7 for the mandated deep dive on the MoE scenario (V9). 

# SECTION 7 — Mandatory Deep Dive on Mixture of Experts

**Why MoE is attractive:**  Mixture of Experts architectures promise a *modular* approach: multiple sub-models (experts) each specialized on a subset of data, potentially boosting accuracy.  In our project, MoE could align with the desire for modularity (“expert for event state, expert for market, etc.”).  If each expert captures different patterns (e.g. one excels at short-term news-driven moves, another at fundamentals), an MoE gating network could intelligently pick or weight them.  MoE also theoretically parallelizes well for modern ML.  

**Why MoE may be overkill/dangerous:** However, MoE greatly increases complexity.  It requires deciding *how* to split experts: by *modality* (e.g. one sub-model for market data, one for news), by *horizon* (short vs long), by *regime* (bull/bear), or some other signal.  Each gating introduces more parameters and risk of overfitting.  Moreover, interpreting which expert did what becomes hard.  The repository is not currently structured for this: there’s no gating logic or expert pool. Implementing MoE is heavy engineering, and benchmarking it fairly is tough (how do we attribute performance gains?).  

**Data scale:** MoE typically shines when massive data lets each expert learn truly distinct mappings. Our dataset (500 stocks × ~20 years of daily data) is modest by deep‑learning standards. It’s *plausible but unverified* that MoE will meaningfully improve accuracy here, especially given the complex interplay of features. Without huge data, experts risk "collapse" (all specializing on the same thing) or one dominating.  

**Current readiness:** The repo has separate branches (market vs news) but no gating. To do MoE, we’d need to dramatically refactor `src/models/`: build new modules, a gating network, and revise training.  This is feasible in principle, but fairly **low** on the current roadmap.  

**Benchmarking complexity:** A MoE model complicates evaluation. For fair comparison, baseline vs MoE have different structures; we would need identical train/test splits, but the model capacity differs. Also, hyperparameter tuning for MoE is larger.  It's easy to inadvertently overfit (many knobs).  

**Likely accuracy gain:** We remain skeptical. MoE might capture heterogeneity, but in a well-engineered simpler model we might already capture most patterns. If the prize is only marginal accuracy boost, it likely isn’t worth the overhead.  

**Variants to consider:** If one did try MoE, sensible choices are:
- **Modality experts:** E.g. one expert processes numerical market features, another processes event-state features, then fuse. This is like a soft gating between modalities. It’s somewhat redundant with simple concatenation, but could allow each expert to focus. However, the report’s V3 strategy suggests gating event vs market might help, but we could also achieve gating via attention without full MoE.  
- **Horizon experts:** Train separate subnetworks for each horizon group (short vs medium vs long), with a gating network (or fixed routing) by horizon. This aligns with multi-horizon idea. But we already use separate heads; we could just train separate models. MoE here is overkill – better is the existing multi-head approach.  
- **Regime experts:** If we tag each day as "bull/bear/neutral", have experts per regime. Then gating chooses by regime. The catch: assigning regime labels itself is tricky. This could be done (e.g. volatility breakout) but adds complexity.  
- **Sector/company experts:** Experts per sector or company cluster. This is akin to training separate model per sector (heavy on data, risk overfit small sectors).  
- **Event-density expert:** One expert for “high-news” days vs “low-news” days. Possibly interesting but ad hoc.

**Risks:** MoE notoriously suffers from expert collapse (all input always routed to one expert), load imbalance, and high variance. Without careful regularization, training can diverge. Each new gating choice is another tuning dimension.  

**Alternatives:** A simpler modular approach is a **parallel ensemble** or additive mixing without trainable gating (e.g. average predictions or weighted sum). Or one could use *mixture-of-sums* (tower models that join outputs). Another is **conditional computation**, e.g. use a simple switch instead of learned gating.

**Verdict on MoE:** We assess MoE as a *high‑risk, high‑complexity* option. It is attractive for modularity, but we doubt it will be a clean winner for accuracy here. The report’s guidance was cautious: it didn’t list MoE explicitly (suggesting it wasn’t a leading idea). We should probably **not make full MoE our core direction**; if anything, consider a small-scale ensemble or gating extension only after other priorities.  

Given the mandate, however, we include it as a scenario. We’ll consider 3 MoE variants below, but overall treat MoE as an “extension‐only” or “experimental” idea.

# SECTION 8 — Benchmarking Strategy, Case by Case

We now assign a tailored benchmarking protocol to each scenario (so that we can fairly assess its benefit). For brevity, we highlight key points:

- **Common foundation:** All scenarios use the **purged rolling walk-forward CV** described in Section 5.  For final evaluation, use a held-out last period (e.g. final year of data) that was not used in any CV. We ensure *temporal integrity and purge/embargo* in all cases.

- **V1 (Corporate Actions):** Use standard temporal CV. Since this is a data fix, the main evaluation is simply how other models improve when trained on corrected data. We should run baseline vs V1 baseline (market-only model) with both on a fixed CV to show benefit. No special metric changes.

- **V2 (Abnormal Targets):** We must re-evaluate all validation metrics in terms of the new target. For fairness, the baseline (market-only) should also be trained on abnormal returns (if V2 is main scenario). We might compare two branches: raw vs abnormal, but that doubles experiments. The CV protocol is same, but when purging, note that abnormal labels still overlap horizons the same way. Ranking metrics like IC might be more appropriate if residuals are more noisy.  
  - *Notes:* Possibly, perform a two-loop CV: one to tune factor regression window, one to test final.  

- **V3 (Enhanced Event):** Use the same CV as baseline. Possibly add ablation: compare base event features vs enhanced features using the same training splits. Standard regression and ranking metrics. Bench remains unchanged except we should report if new features help on event-dense vs sparse periods.  

- **V4 (Ranking Objective):** Here the **validation protocol itself changes**. Instead of reporting RMSE, the primary metric should be cross-sectional Spearman R or IC on each test day. We still do walk-forward CV, but evaluation focuses on e.g. daily rank correlation and area-under-curve for classifying top deciles. We should also ensure raw target metrics are computed for comparison. For fairness, if comparing to a baseline trained on MSE, we might retrain the baseline with the same rank loss. In short, use a *pairwise or listwise ranking loss in training*, or at least evaluate ranking.  
  - *Important:* We must avoid “label leakage” from computing rank (no normalization on entire dataset). Use per-date ranks only.  

- **V5 (Uncertainty Outputs):** Validate both point-prediction quality and calibration. Use metrics like Continuous Ranked Probability Score (CRPS) or mean NLL on test. Possibly split evaluation: one version of CV for mean, another for sharpness. A sharp/flat CV can test calibration. We should still measure RMSE of mean for baseline comparability.  

- **V6 (Macro/Regime):** Standard CV. But we might want a “regime‐aware” test: e.g. ensure that each test fold contains different market regimes. We could stratify folds by volatility regimes if possible. Additionally, we should audit leakage: e.g. if using monthly macro data, ensure we do not use June data to predict May returns.  

- **V7 (Options):** Similar to macro: standard CV. If the data is available, maybe use a label shift test: e.g. test in periods with known volatility spikes. Otherwise normal rolling splits suffice.  

- **V8 (Company KB):** Standard CV. We should do an ablation where KB branch is added vs removed. If using textual embeddings, ensure not to train on future descriptions. Possibly align KB by year.  

- **V9 (MoE variants):** MoE requires caution: we should compare a MoE model vs a single-model baseline **with the same CV splits**. We must also check overfitting: perhaps use cross-validated hyperparameter search (nested CV) to tune expert count or gating temperature. This is heavy. If we do horizon experts, each fold trains multiple submodels.

In all cases, the **benchmark complexity** and *fairness* vary:
- The scenarios that simply add features or change labels (V1, V2, V3, V6, V7, V8) fit into the same CV framework with minimal change – they are easy to compare to the baseline.  
- Scenarios that change the objective or model structure (V4, V5, V9) require more care in defining metrics and comparisons. For V4, one might compare rank-optimized vs error-optimized models, which is not apples-to-apples; best is to try both objectives on both model types in a factorial design (but that multiplies experiments).  
- MoE (V9) is hardest: it has more hyperparameters (number of experts, gating) so may require nested tuning folds. Its comparison to baseline is trickiest.  

We assign, qualitatively, for each scenario:
- Benchmarking **complexity** (how much new procedure needed): low for V1, V3, V6, V7, V8; medium for V2, V5; high for V4, V9.  
- Fairness **ease**: high (easy) for V1, V3, V6, V7; medium for V2, V5; low (hard) for V4, V9.  
- Conclusion **robustness**: likely strong for V1, V4 (they define clear improvements) and weaker for V5, V8.  
- *In thesis defense*, V1 is a must (since everyone expects split-adjustment), V2/V4 debate is thematic, V9 is highest-risk plus story.

# SECTION 9 — Scenario‐by‐Scenario Feasibility Ledger

Below is a comparative summary of each scenario (scores out of 5, higher is more positive):

| Scenario                    | Core Idea                            | Accuracy Upside | Robustness Upside | Interpretability | Modularity | Repo Fit | Data Burden | Compute Burden | Leakage Risk | Bench Burden | Ablation Ease | Role            |
|-----------------------------|--------------------------------------|-----------------|-------------------|------------------|------------|----------|-------------|----------------|--------------|--------------|---------------|----------------|
| **V1: Corporate Actions**    | Split/dividend adjustment           | High (5)        | High (5)          | High (5)         | High (5)   | High (5) | Low (5)     | Low (5)        | Low (5)      | Low (5)     | Easy (5)      | Core (must)     |
| **V2: Abnormal Targets**    | Use excess/alpha returns           | Medium (3)      | Medium (3)        | Medium (3)       | High (4)   | Medium (3)| Low (4)    | Low (4)        | Medium (3)   | Medium (3)  | Moderate (3)  | Core/Strong Ext |
| **V3: Better Event State**  | Novelty/conflict/density features  | Low (2)         | Low (2)           | Medium (3)       | High (4)   | Medium (3)| Medium (3) | Medium (3)      | Low (4)      | Low (4)     | Moderate (3)  | Optional Ext    |
| **V4: Ranking Objective**   | Cross-sectional ranking loss       | Medium (3)      | Medium (3)        | Medium (3)       | High (4)   | Medium (3)| Low (4)    | Medium (3)      | High (2)     | High (2)    | Hard (2)      | Strong Ext      |
| **V5: Uncertainty Output**  | Output mean+variance or quantiles  | Low (2)         | Low (2)           | Low (2)          | High (4)   | Medium (3)| Low (4)    | Medium (3)      | Low (4)      | Low (4)     | Moderate (3)  | Optional Ext    |
| **V6: Macro/Regime**        | Macro indicators features          | Low (2)         | Low (2)           | Medium (3)       | High (4)   | Low (2)  | Medium (3) | Low (4)        | High (2)     | Low (4)     | Easy (5)      | Optional Ext    |
| **V7: Options Signals**     | Implied vol/skew features          | Medium (3)      | Medium (3)        | Low (2)          | High (4)   | Low (2)  | High (1)   | Medium (3)      | Low (4)      | Medium (3)  | Moderate (3)  | High-Risk Ext   |
| **V8: Company KB**          | Static/timed company profiles      | Low (2)         | Low (2)           | Medium (3)       | Medium (3) | Low (2)  | High (1)   | Low (4)        | High (2)     | Medium (3)  | Moderate (3)  | Optional Ext    |
| **V9: Mixture of Experts**  | Gated ensemble of subnetworks     | Medium (3)      | Low (2)           | Low (2)          | High (4)   | Low (2)  | Low (4)    | High (1)        | High (2)     | High (2)    | Hard (2)      | High-Risk Ext   |

- **Accuracy Upside:** V1 is highest because split issues can hugely skew labels. V2/V4/V7 may give modest gains.  
- **Robustness Upside:** Data cleanliness (V1) and rank-based loss (V4) improve robustness. Others less.  
- **Interpretability:** V1 cleanly improves signal; V4’s predictions are easily interpreted as ranks; uncertainty (V5) helps interpret confidence. MoE (V9) lowers interpretability.  
- **Modularity:** New data branches (V1, V2, V3, V6, V7, V8) are modular; MoE is modular but complex; V4/V5 are objectives, not branches (high modularity for code).  
- **Repo Fit:** V1 is easiest to fit (we have price data); V2/V5 moderate; V6/V7 need new data, V8 heavy; V9 hardest.  
- **Data Burden:** V7/V8 require significant new data. Others reuse existing (or add minor static data).  
- **Compute Burden:** V9 is huge; others small.  
- **Leakage Risk:** V4/V9 high (new losses, experts), V2 medium (if factor usage leaks), V6/V8 (if not time-stamped).  
- **Benchmark Burden:** V4/V9 high (new metrics/training), V2/5 medium, others low.  
- **Ablation Ease:** V1, V3, V6, V7 easy (just add feature, compare), V4/V9 hard (comparing different training processes).  
- **Role:** We label V1 and V2/V4 as core or strong extensions. V3/V5/V6/V8 as optional, V7/V9 as high-risk.

# SECTION 10 — Tournament of Scenarios

We now pit the scenarios against each other in bracket matches (accuracy first, then other criteria):

- **Quarterfinal A: V1 (Corp. Acts) vs V3 (Better Event State).**  
  **Winner: V1.**  Reason: V1 fixes fundamental label noise – universally beneficial. V3’s novelty features are sophisticated but likely incremental. If MoE were here, V1 still beats it.  
  *Loser V3:* Still useful (modular improvement) but not as impactful as data correctness.

- **Quarterfinal B: V2 (Abnormal Target) vs V6 (Macro/Regime).**  
  **Winner: V2.**  Reason: Reformulating targets often yields a clear “alpha” focus. Macro (V6) adds context, but likely lower predictive lift and higher risk of data issues.  
  *Loser V6:* May still help (include as extension), but less core to forecasting skill.

- **Quarterfinal C: V4 (Ranking) vs V5 (Uncertainty).**  
  **Winner: V4 (Ranking).**  Reason: If our aim is “accuracy in decision-making,” ranking/loss aligns with ultimate use (portfolios). Uncertainty (V5) adds nice calibration but is secondary for predictive quality.  
  *Loser V5:* Useful for risk reporting, but real returns and ranking come first.

- **Quarterfinal D: V7 (Options) vs V8 (Company KB).**  
  **Winner: V7 (Options).**  Reason: Options data, while costly, directly encode market expectations and may capture tail risk unseen in fundamentals. Company KB (V8) is broad but not directly return-predictive in our framing.  
  *Loser V8:* Could help static priors, but likely an extension at best.

Next, we incorporate **V9 (MoE)** into a semifinal as a wildcard. Suppose we match:

- **Wildcard Semi: V9 (MoE) vs the strongest losing quarter (V5).**  
  **Winner: V9.**  Reason: If we must choose between MoE and uncertainty branch, MoE has higher “accuracy potential” (theoretically) though both are risky. However, this is a toss-up. We’ll say MoE wins this matchup, but only by a narrow margin and **only** if data scale justifies it.  
  *Loser V5:* Falls out – we still implement basic uncertainty possibly later, but MoE edges it in this context.

Now semifinal round with winners:

- **Semifinal 1: V1 vs V2.**  
  **Winner: V1.**  Both are important, but corporate actions (data fix) is a prerequisite (otherwise residual target uses flawed data). V1 safeguards everything.  
  *Loser V2:* Remains strong (abnormal returns is intellectually neat) but secondary to having correct base data.

- **Semifinal 2: V4 vs V9.**  
  **Winner: V4.**  The ranking approach provides a clear conceptual gain with moderate effort, whereas MoE carries too many dangers. V4 yields a simpler, interpretable focus on useful performance; V9 is too complex and untested.  
  *Loser V9:* Even if some accuracy boost, the interpretability hit is too high.

Finally, the **Grand Final: V1 vs V4.**  
**Champion: V1 (Corporate Actions First-Class).**  Rationale: Ensuring correct price series is the foundation. V4 (ranking objective) is the best second choice, but ranking without accurate data is moot. The report likewise crowned V1 the top priority【13†】.  

**Runner-up:** V4.  Because it directly targets useful forecasting quality, especially for portfolio decisions.  

**Best low-risk/high-confidence:** V1, V4 (these two align with core thesis and have clear implementation paths).  

**Best high-risk/high-reward:** V7 (options signals) if data can be obtained, or V9 (MoE) if we had infinite resources.  

**Best if thesis must remain narrow:** Focus only on V1 (and possibly V4) – fix splits and test a modest ranking metric on top of market+news.  

**Best if thesis can expand moderately:** Combine V1+V4 (data fix + ranking objective) as core, adding V2 (abnormal labels) and V5 (uncertainty) as complementary checks/appendix. Possibly mention V3 (event features) as future work.

# SECTION 11 — Unified Pipeline Discussion

*Could* we incorporate “everything” into one gigantic pipeline?  In theory, yes: we could have one model that uses split-adjusted prices, abnormal returns target, an MoE with various experts for each scenario, multi-head outputs for horizons, gating by regime, plus company profiles, macro, options, uncertainty output, etc. This “kitchen sink” model would literally have all features and design choices.  

**Advantages:** If done *perfectly*, it might squeeze out every ounce of signal: the shared model could learn synergies (e.g. gate differently in high volatility vs calm periods, use news vs market adaptively, etc.). A unified approach can maximize accuracy if enough data and careful regularization exist.  It also avoids the risk of cherry-picking separately trained model ensembles.  

**Disadvantages:** However, this is overwhelmingly complex. Interpretability and ablations become nightmare: any observed effect might come from a tangled web of interactions. The thesis narrative would suffer: it’s hard to claim one coherent contribution when your method is an opaque giant. Testing and debugging would be hard. Benchmarking such a model is much less clear-cut, since the baseline must handle all those inputs too. It also massively increases the chance of leakage or overfitting – more moving parts means more ways to cheat. The report explicitly warns that over-expansion dilutes scientific clarity【13†】.  

Given modularity vs clarity tradeoff, the verdict is **to *avoid* a single monolithic super-pipeline**. Instead, we keep a “narrow core” implementation (e.g. V1+V4) and treat others as separate controlled extensions. Those extensions can be turned on/off cleanly for ablation.  For example, we might have flags in the code: `use_split_adjustment`, `use_ranking_loss`, `use_event_density`, etc. This maintains modularity: each branch can be disabled to measure its effect. But we will not force all branches active at once.  

**Unified model benefits** (in abstract): better shared learning, easier incremental addition, potential cold-start improvements (e.g. add KB or macro as needed).  
**Unified model downsides**: scope explosion, harder to defend, more leak risk, more hyperparameters.  

The strong advice is to **preserve a focused core model and only add one major extension at a time**.  This is both engineering-sensible (easier testing) and scientifically cleaner.  The final winner (V1) should be integrated first; V4 (ranking) can be layered as a training objective on the same model. Other ideas (especially MoE) should remain optional add-ons.

# SECTION 12 — Best Benchmarking Architecture for Comparing All Serious Scenarios

Given all scenarios, our overall benchmarking architecture must accommodate them:

- **Main development benchmark:** Rolling purged CV (as described) on training data. This is used for tuning and comparing candidate ideas. It yields performance distributions (e.g. foldwise metrics).
- **Model-selection benchmark:** Possibly nested CV when large new hyperparameters are added (e.g. MoE or factor models). But at least, we should do CV grid-search for core parameters.  
- **Final untouched test:** Keep the last 1–2 years of data completely separate as a lockbox. After selecting the final approach, train on all pre-lockbox data and report metrics on the holdout.  

For **scenario comparison**, the same CV protocol works: evaluate each scenario on the *same* splits so we can compare their score distributions. When objectives differ (like V4), we align by ranking metrics.  

For **ablation studies**, use the same CV splits but train baseline vs +feature scenario, etc. We should ensure like-with-like: e.g. when comparing V2 (abnormal targets) we might also run the base model on raw targets to show difference.  

For **thesis tables/figures**:
- Provide results per horizon (1d,5d,20d) using metrics (RMSE, MAE, IC) for each scenario vs baseline.  
- Show ranking metrics (IC, top-k precision) prominently if V4 is used.  
- If uncertainty (V5) used, include calibration plots or Sharpness vs Reliability.  
- Perhaps a grouped bar chart of CV performance for each scenario.  
- Possibly a small PBO analysis chart if many models tested (to illustrate overfitting risk).  

For **MoE specifically**, we would likely not include it in final claims unless it truly dominated; it may get its own line in an ablation table. The benchmark protocol itself (walk-forward CV) stays the same, but we must emphasize complexity and instability in the text.

# SECTION 13 — Final Selection of the Best Scenario to Implement Next

**Best scenario:** **V1 – Corporate Actions First.** We select the corporate-action adjustment as our immediate next step. This choice is based on multiple factors:

- It is **already evidenced by the repo** to be needed (the user’s data was unadjusted) and trivial to justify scientifically.  
- It is **easy to implement** with minimal risk: it fixes a known data issue, requires no new predictive modeling, and yields immediate benefit by cleaning labels.  
- It is **highly modular and benchmark-safe**: we simply transform the existing dataset. All experiments (baseline vs new models) will now be on an apples-to-apples improved dataset. This clarifies future comparisons (no more hidden split-boost artifacts)【11†】.  
- It carries **no confusion**: every methodology review stresses price adjustment as a prerequisite. It strengthens the thesis foundation (analysis is accurate) and satisfies the “accuracy first” criterion with virtually no drawback.  

We will implement V1 fully before major modeling gambits. 

Second best: **V4 – Ranking Loss/Objective**, as a close runner-up. Once the data is clean, changing to a ranking‐focused objective is our next most compelling move for pure predictive utility (especially in finance tasks). But because it complicates comparison, we do it *after* V1.  

**MoE vs Narrow:** We will not choose a full MoE as next. It’s high-risk and would distract from simpler gains. The results above show V9 losing out. Instead, we might incorporate modular ideas from it later (e.g. gating between market/news if a clear need arises, but not yet).  

In summary, **implement corporate-actions adjustment immediately**, then consider adding a ranking objective on top. Treat other extensions as separate experiments rather than core next steps.

# SECTION 14 — Brutally Honest Final Verdict

1. **Best scenario to implement next:** V1 – Corporate actions adjustment.  
2. **Why it’s best:** It’s a necessary data fix with immediate accuracy benefit and zero controversial tradeoff【13†】.  
3. **Best overall benchmarking strategy:** Rolling purged walk‑forward CV plus a final locked holdout, as detailed above.  
4. **Best benchmarking for scenario comparison:** Use the same purged CV splits for all scenarios, measuring both point and ranking metrics. Ensure identical folds so results are comparable.  
5. **Is Mixture of Experts worth it?** No, **not as a core approach**. It’s too complex for limited data and hard to benchmark. Possibly as a future extension if simpler attempts fail.  
6. **If yes, when?** Only consider MoE *after* simpler methods (V1–V5) are exhausted and if a clear signal of heterogeneous behavior emerges. It would be a late extension, not an immediate priority.  
7. **If no, why not?** MoE adds enormous engineering and benchmarking complexity with questionable accuracy gain. It conflicts with our modular vs clarity goals.  
8. **Most modular strong candidate (not MoE):** V4 (Ranking objective) – it changes the loss but keeps the pipeline intact, so it’s conceptually modular in design and clean to toggle. V3 (event features) is also modular.  
9. **Most dangerous next mistake:** Ignoring split/dividend adjustments (V1) – that would corrupt all results. Also, **using static company descriptions without time-safeguards (V8)** is a big leakage trap, or jumping into MoE too soon.  
10. **What not to do:** Do **not** rush to MoE or to merge all branches at once. Do **not** adopt a ranking objective before cleaning data, and do **not** do naive CV that leaks.  
11. **Do before large expansion:** Strengthen data hygiene (split adjust, alignment checks) and benchmark discipline (purge/embargo tests) first. Show that market-only baselines are properly validated.  
12. **Strongest clean thesis version:** A model trained on **adjusted prices**, using *walk-forward evaluation*, predicting return (or abnormal return) and optimized partly for ranking accuracy, with modular event-state incorporation. This core is clear, reproducible, and can yield a defendable improvement over market-only baseline. 

In short, **fix the data (V1), validate rigorously, then add one innovative twist at a time (like V4)**. Keep the architecture as simple as possible, only widening it once the fundamentals are rock solid.  This will ensure the thesis is strong, results believable, and experiments manageable.