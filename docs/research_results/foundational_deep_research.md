RESEARCH EXPANSION FROM HTML CHAT COMPILATION: EVENT-STATE-DRIVEN FINANCIAL NEWS IMPACT PREDICTION ON STOCKS

Purpose of this second-order research pass

This document is a second-order, restart-grade research foundation for the thesis project. Its function is not to summarize previous notes. Its function is to reconstruct the project from the cleaned HTML chat compilation and the local repository archaeology, stress-test what survived conceptually, integrate broader literature, and turn that into a stricter basis for the next implementation cycle.

The most important change relative to a casual continuation is this: the project should now be treated as a scientific question with an implementation substrate, not as an open-ended engineering sandbox. The question is narrower than many earlier branches implied.

The real question is not whether a complex multimodal model can be made to outperform something weak on some slice. The real question is whether a temporally aggregated event-state representation of firm-related news adds stable, measurable value beyond conservative market-only baselines for end-of-day multi-horizon forecasting under leakage-aware, benchmark-comparable evaluation.

That is a much better thesis question than “predict stocks with AI”, better than “use more modalities”, and better than “invent clever features”. It is falsifiable, capable of producing an academically useful negative result, and well aligned with the strongest parts of the repository evidence.

Established from project materials:
- the project is end-of-day only
- the project is multi-horizon
- the project is multimodal market plus text
- the project prefers event-state over isolated article-effect framing
- the project is strongly concerned with leakage, split handling, and benchmark comparability

Supported by external literature or official documentation:
- financial ML results are fragile under poor evaluation design [P16] [P17] [P18] [P19] [P21]
- return-like or benchmark-relative targets are more defensible than raw price prediction [P26] [P27]
- multimodal gains depend heavily on alignment quality, not just model size [P8] [P9] [P13]

Plausible but unverified:
- some later extensions could add value if the core benchmark is already stable

Speculative and requiring future validation:
- broad claims that the project should evolve into a much richer knowledge-graph or expert-routing system soon

How the HTML compilation was interpreted and cleaned

The supplied HTML export was treated as a noisy reconstruction source, not as a document whose raw contents could be trusted literally. It contains four very different content classes.

True project-content evidence:
- direct user instructions about rigor, criticism, output style, and repository awareness
- repeated project identity statements about end-of-day forecasting, multi-horizon labels, multimodal market plus news modeling, and leakage discipline
- prior research continuations that pushed the project toward benchmark-first reasoning
- explicit derivative-feature debates, including warnings against feature inflation
- repeated insistence that the project is not intraday, not HFT, not a trading bot, and not raw price prediction

Duplicated or repeated content:
- repeated restatements of the same research prompt
- repeated mentions of the same legacy files and same project identity
- repeated continuation fragments after response truncation in the HTML conversation
- repeated attachment tiles and repeated references to the same local files

Page-export noise:
- CSS, JavaScript, cookie-banner styles, saved-browser metadata, locale metadata, UI labels, chrome, session scaffolding, and unrelated rendering artifacts
- account/session strings and other sensitive-looking export artifacts
- repeated navigation elements and file tiles unrelated to scientific content

Ambiguous fragments that required cautious interpretation:
- citations embedded by prior assistant turns in the exported chat, which were useful as leads but not automatically accepted as verified references
- partial assistant continuations cut off by streaming errors
- UI-generated file attachment tiles that indicated likely reading order or likely files, but not proof of implementation claims by themselves

The HTML was therefore used primarily for project intent reconstruction, not for implementation proof. Implementation proof was taken from local repository materials, especially the archived legacy snapshot and its theory, architecture, evaluation, testing, and guidebook documents.

Established from project materials:
- the local repo does not contain the specific HTML file under the searched tree, so the user-pasted HTML compilation became the primary reconstruction source for project history

Not evidenced in provided project materials.
- a locally stored canonical HTML file under the current active root tree

Plausible but unverified.
- some references embedded in the HTML by prior assistant turns may still be useful and correct, but they required independent checking before being treated as supporting literature

Reconstructed project identity from the HTML evidence

The HTML history does not support the interpretation that this is a generic financial forecasting project. The stable reconstructed identity is much narrower and much better.

Established from project materials:
- thesis-grade research project
- end-of-day forecasting only
- stock-level prediction using market history plus news-derived information
- multi-horizon outputs, especially 1-day, 5-day, 20-day, with 60-day as a possible later horizon
- event-state framing rather than isolated article sentiment or article-specific price impact
- target design centered on forward return-like quantities, especially excess or abnormal returns
- leakage-aware, walk-forward, benchmark-comparable evaluation
- modular repository structure with distinct data, features, split, model, and evaluation layers

Supported by repository evidence:
- `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/architecture_overview.md` defines the system goal as a thesis-grade end-of-day forecasting pipeline built around daily market data, aligned company news, optional company metadata, multi-horizon labels, market-only baselines, and a first multimodal market plus event-state model
- `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/evaluation_protocol.md` defines strict out-of-sample time evaluation, as-of-close alignment, frozen datasets, saved-prediction evaluation, and horizon-aware purge and embargo
- `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/data_layout.md` defines raw/interim/final separation, explicit adjusted-price tables, article embeddings, event-state tables, and final modeling panels
- `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/RESEARCH_DESIGN_old.md` explicitly rejects raw price prediction and centers evolving event-state plus market features for multi-horizon excess-return prediction

The active repository root currently functions primarily as a governance constitution and fresh-start shell. The actual first-pass implementation evidence is archived in the legacy snapshot. That distinction matters.

Supported by repository evidence:
- `LEGACY_DEPRECATION_SUMMARY.md` states that the old top-level project items were archived and the root was intentionally cleared for a true fresh start
- `deprecated_version/legacy_snapshot_20260402T115014Z/README.md` states that the snapshot is deprecated, frozen historical reference, and not the active implementation source of truth
- the active governance validator currently fails because `docs/agent/agent_log/Current_State.md` and `docs/agent/agent_log/Event_Ledger.ndjson` are missing, which confirms that the active root has governance philosophy but incomplete operational logging scaffolding

Reconstructed evolution of the project’s conceptual framing

The project appears to have evolved through four conceptual stages.

Stage 1: broad and underspecified financial-news prediction language.

The earliest framing is close to “financial news impact prediction on stocks”. This is intuitive but too weak. It invites naive sentiment thinking, underplays timing leakage, and does not sharply distinguish price levels from return-like targets.

Stage 2: event-driven multimodal forecasting with stronger scope boundaries.

The research design moved the project toward daily market data plus recent financial news, multi-horizon targets, and explicit market-neutral or excess-return logic. This is already much stronger than generic price forecasting.

Stage 3: event-state rather than isolated article-effects.

The strongest conceptual improvement was abandoning the idea that each article has a clean isolated market effect. The project instead started treating recent news as overlapping semantic flow summarized as an event state. This is a genuine theoretical sharpening, not mere terminology.

Stage 4: benchmark-first and leakage-first maturity.

The later prompts, audit-style continuations, and governance materials pushed the project toward a harder question: whether event-state information adds incremental value beyond disciplined market-only baselines under clean evaluation. This is the strongest version of the project and the one that should now govern implementation.

The main drift across the history was not toward nonsense, but toward too many attractive branches at once.

Weak or drifting tendencies included:
- derivative-style feature centrality
- architecture inflation
- broad modality inflation
- possible confusion between forecasting research and trading utility
- pressure to preserve every intellectually attractive idea instead of staging them

There is also one real methodological shift across historical materials that must be acknowledged explicitly.

Established from project materials:
- `RESEARCH_DESIGN_old.md` proposed an explicit embargoed news-alignment logic with a two-day-style separation between publication and prediction in some examples
- the current `evaluation_protocol.md` instead defines an as-of-close same-day information set: only articles available by market close on date t may be used for features on t, with after-hours and non-trading-day articles rolled forward

This is not a trivial wording difference. It means older hypothetical benchmark ideas and newer implementation-facing evaluation rules are not automatically comparable. Any experiment using the newer as-of-close policy is part of a different benchmark family than an earlier embargoed-news design.

Strongest stable ideas that survived across the HTML history

1. End-of-day only.

This survived every serious reframing and is one of the best project decisions. It sharply reduces data-timing ambiguity, avoids microstructure obsession, fits available provider quality, and is much more defensible for a Master’s thesis than intraday prediction.

2. Event-state over isolated article sentiment.

This is the project’s best conceptual contribution. It recognizes that financial information arrives as overlapping narrative flow. Aggregating recent news into an evolving state is more realistic than pretending each headline maps cleanly to one price effect.

3. Multi-horizon forecasting.

The project correctly recognizes that different information may matter at different delays. Immediate reaction, short drift, medium repricing, and longer narrative absorption do not collapse into one horizon without loss.

4. Return-like and benchmark-relative targets instead of price levels.

This is a critical maturity marker. Price-level prediction is weakly framed and easily misleading. Excess-return or residual-return style targets are more coherent for a thesis that asks about incremental informational value.

5. Split handling before labels.

This is one of the strongest operational and scientific instincts in the whole repo. Once the project recognized that raw provider OHLCV could be unadjusted around splits, it correctly treated corporate-action handling as a blocker, not as a cleanup task.

6. Market-only baselines before multimodal claims.

This matters more than any later model detail. A multimodal model beating a weak baseline is not persuasive. A multimodal model beating a disciplined market-only baseline under the same frozen dataset is meaningful.

7. Reproducibility through layered storage and saved predictions.

The repo’s raw/interim/final separation, manifests, explicit adjusted-price tables, embedding cache tables, and saved-prediction evaluation philosophy are exactly the kinds of foundations a thesis-grade experimental system needs.

Weak, drifting, contradictory, or overextended ideas found in the HTML history

1. Derivative-like feature centrality.

This is the clearest case of an idea that sounds deeper than it currently is. There is little evidence in project materials that raw first- or second-derivative transforms over OHLCV should be thesis-core. Much of the useful content that derivative advocates want is already available more cleanly in returns, momentum, volatility, range, and benchmark-relative features.

2. Architecture expansion before scientific closure.

The repo’s current architecture overview explicitly says the multimodal model is intentionally simple and richer variants belong later. Any tendency to jump early toward stronger attention, graph reasoning, or expert routing is concept drift unless the core benchmark has already been settled.

3. Modality inflation.

Static metadata, dynamic profile text, broader mainstream news, sector graphs, and regime branches are all potentially relevant. But trying to make them co-equal with the core market plus event-state question would lower thesis clarity.

4. Pilot-result overreading.

Archived smoke artifacts exist, but they are tiny. The current archived evaluation summary references one prediction file, one target column, one split, and only a few rows. That is evidence that the path works, not evidence that the thesis question has been answered.

Supported by repository evidence:
- `reports/eval_stage14_baseline/evaluation_summary.json` shows only one evaluated prediction file, one target column, and row counts of three for ranking and regression summary tables
- `runs/baseline_stage14_eval_smoke/baseline_training_summary.json` shows one split, one model, horizon 1 only, with 6 train rows, 2 validation rows, and 4 test rows
- `runs/multimodal_stage13_smoke_fix/multimodal_training_summary.json` shows a similarly tiny smoke configuration

These smoke artifacts are scientifically useful only as plumbing proof.

5. Historical comparability ambiguity.

The project changed from older embargo-style news alignment ideas to a newer as-of-close same-day information set. That is a defensible evolution, but it means older imagined benchmark numbers in legacy theory documents are not directly comparable with current evaluation logic.

6. Active-governance shell treated as if it were an active implementation substrate.

The active root has strong governance files, but operationally it is incomplete. The validator failure proves that some required governance logging artifacts are missing. This matters because it means current active-root maturity is stronger in rules than in operational continuity.

Core theoretical concepts that now deserve formal definition

Event state.

Definition:
An event state is a temporally aggregated representation of the firm-specific information environment available by a defined as-of-close cutoff, constructed from recent relevant news and optionally enriched with scalar descriptors such as density, novelty, conflict, source dispersion, and persistence.

Why it matters:
This definition distinguishes the project from simplistic sentiment analysis and from article-level causal framing. It makes clear that the object being modeled is not a single article but a short-lived evolving semantic state.

As-of-close information set.

Definition:
All information that would have been available by the project’s standardized daily cutoff for date t. Under current repo policy, only articles available by market close on t may be used for feature construction on t; after-hours and non-trading-day articles roll to the next valid trading day.

Why it matters:
Without an explicit information-set definition, leakage claims are hand-wavy. This concept is part of the task definition itself.

Forward excess return.

Definition:
The stock’s forward return over horizon h minus the benchmark’s forward return over the same horizon.

Why it matters:
It isolates stock-specific performance from broad market drift and aligns the thesis with the question of incremental informational value rather than beta timing.

Abnormal return or factor-neutral residual return.

Definition:
A forward outcome or feature component after controlling for one or more benchmark or factor exposures.

Why it matters:
This is a stronger possible refinement than raw returns, but it introduces more assumptions and should therefore follow, not precede, the clean excess-return core.

Benchmark comparability.

Definition:
The condition under which two results may be interpreted as fair comparisons because they use the same universe, same date range, same split logic, same target definitions, same as-of rules, same missing-data rules, same metrics, and the same frozen dataset family.

Why it matters:
Many financial ML results fail not because models are bad, but because benchmark families drift while still being spoken of as if they were the same experiment.

Leakage.

Definition:
Any pathway by which future information, post-cutoff information, point-in-time violations, overlapping-label contamination, or downstream statistic fitting on holdout data enters evaluation or training illegitimately.

Why it matters:
Weak predictive signals in finance mean even small leakage can create highly persuasive but false apparent skill.

Modularity.

Definition:
The property that a pipeline or model family can be varied branch by branch without silently altering upstream data definitions, split logic, or evaluation rules.

Why it matters:
Good modularity enables clean ablations. Bad modularity creates hidden benchmark changes disguised as component swaps.

Thesis contribution.

Definition:
A thesis contribution is the strongest defensible knowledge claim or methodological asset that survives the full benchmark discipline. It is not the same as implementation breadth.

Why it matters:
This project is vulnerable to confusing repository richness with scientific contribution. The two must be kept distinct.

Full map of candidate target-design families

Family: Raw forward returns
Problem it tries to solve:
Provide the simplest direct forward outcome for regression.
Concept:
Predict the stock’s own future return over horizon h.
Common implementation styles:
Close-to-close simple returns, log returns, or scaled returns.
Best arguments in favor:
Simple, interpretable, easy to compute, strong baseline family.
Best arguments against:
Confounds stock-specific movement with broad market movement. May flatter results in trending regimes.
Benchmark implications:
Easy comparability if frozen. Weak at isolating incremental news value.
Leakage implications:
Standard future-window leakage risks only.
Modularity implications:
High. Fits current label module cleanly.
Thesis implications:
Useful as baseline target, but weaker than excess-return framing for the actual thesis question.
Current judgment:
Core baseline family, but not the strongest final primary target.

Family: Forward excess returns
Problem it tries to solve:
Separate stock-specific performance from market drift.
Concept:
Predict stock return relative to benchmark return over the same horizon.
Common implementation styles:
Subtract S&P 500 or SPY forward return, or another fixed benchmark series.
Best arguments in favor:
Much closer to the project’s stated hypothesis about incremental informational value beyond market-only signal.
Best arguments against:
Requires a benchmark series and consistent alignment; can be misused if benchmark definition drifts.
Benchmark implications:
Very strong if one benchmark is frozen and held constant.
Leakage implications:
Requires careful benchmark availability and alignment, but conceptually clean.
Modularity implications:
High, because the current label layer and data architecture already support benchmark-relative logic.
Thesis implications:
Strongest current primary target family.
Current judgment:
Core now.

Family: Abnormal or factor-neutral residual returns
Problem it tries to solve:
Isolate idiosyncratic movement more strongly than a single benchmark subtraction.
Concept:
Predict the residual part of returns unexplained by one or more risk factors.
Common implementation styles:
Residualization versus market, size, value, profitability, investment, or momentum factors.
Best arguments in favor:
Financially stronger framing for incremental informational value.
Best arguments against:
Introduces extra modeling assumptions, factor-estimation choices, and data dependencies.
Benchmark implications:
Creates a new benchmark family if adopted. Must be handled as an explicit target redesign.
Leakage implications:
Factor estimation and daily alignment must be point-in-time clean.
Modularity implications:
Moderate. Fits current repo with added factor-data ingestion, but adds complexity.
Thesis implications:
High-value extension if the core excess-return thesis is already stable.
Current judgment:
Strong next-step candidate, not core first-run default.

Family: Direction classification
Problem it tries to solve:
Simplify the prediction task to directional correctness.
Concept:
Predict whether forward excess return is positive or negative.
Common implementation styles:
Binary labels, BCE loss, class-balanced training.
Best arguments in favor:
Easy to understand, useful as secondary metric.
Best arguments against:
Throws away magnitude information; small directional edges can look bigger than they are; easy to overstate.
Benchmark implications:
Should be secondary, not the only core benchmark.
Leakage implications:
Same temporal risks as regression targets.
Modularity implications:
High.
Thesis implications:
Useful auxiliary lens, weak sole framing.
Current judgment:
Secondary only.

Family: Cross-sectional ranking targets
Problem it tries to solve:
Model relative ordering rather than exact value.
Concept:
Predict rank or top-vs-bottom ordering across the stock universe on each date.
Common implementation styles:
Rank correlation metrics, pairwise ranking losses, daily IC.
Best arguments in favor:
Often more stable and financially meaningful for stock selection than point forecasts.
Best arguments against:
Can obscure whether magnitudes are meaningful; less directly aligned with the project’s current return-regression core.
Benchmark implications:
Very important as a secondary evaluation family, especially if point regression is noisy.
Leakage implications:
Cross-sectional same-day leakage and filtering consistency must be watched carefully.
Modularity implications:
Moderate. Current metrics layer supports ranking, but ranking-first training would add another model family.
Thesis implications:
Strong next-step candidate for evaluation, not mandatory as primary training objective.
Current judgment:
Strong next-step candidate.

Family: Downside or risk-sensitive targets
Problem it tries to solve:
Prioritize harmful outcomes or asymmetry in losses.
Concept:
Predict downside capture, downside event occurrence, or tail-sensitive targets.
Common implementation styles:
Binary downside labels, asymmetric losses, downside beta-like outcomes.
Best arguments in favor:
Risk-sensitive finance framing can be scientifically useful.
Best arguments against:
Secondary to the current thesis question; easy to proliferate target families prematurely.
Benchmark implications:
Creates additional complexity if used too early.
Leakage implications:
Same timing risks, plus threshold-design sensitivity.
Modularity implications:
Moderate.
Thesis implications:
Interesting extension after core claim is established.
Current judgment:
Extension.

Family: Distributional or probabilistic targets
Problem it tries to solve:
Predict uncertainty, not only point estimates.
Concept:
Model predictive distribution, quantiles, or calibrated probabilities.
Common implementation styles:
Quantile regression, Gaussian heads, conformal layers, classification probabilities.
Best arguments in favor:
Scientifically richer and better aligned with proper scoring rules.
Best arguments against:
Premature before point-prediction and ranking evidence are stable.
Benchmark implications:
Requires proper scoring rules and calibration diagnostics.
Leakage implications:
No extra timing leakage, but higher reporting burden.
Modularity implications:
Moderate to high.
Thesis implications:
Valuable later extension.
Current judgment:
Extension if time allows.

Full map of candidate market-feature families

Family: Conservative return family
Problem it tries to solve:
Encode basic recent price movement.
Concept:
Lagged returns, cumulative returns, simple and log returns.
Common implementation styles:
1d, 5d, 20d rolling returns.
Best arguments in favor:
Standard, interpretable, low-risk, strong baseline family.
Best arguments against:
Can be too coarse if used alone.
Benchmark implications:
Core benchmark family.
Leakage implications:
Low if computed strictly past-only.
Modularity implications:
Very high.
Thesis implications:
Mandatory base layer.
Current judgment:
Core now.

Family: Volatility and range family
Problem it tries to solve:
Encode uncertainty, dispersion, and price instability.
Concept:
Rolling volatility, high-low range, close-to-range, ATR-like daily proxies.
Common implementation styles:
20-day realized volatility proxies, normalized ranges.
Best arguments in favor:
Often stronger than fancier transforms for capturing regime and uncertainty.
Best arguments against:
Can overlap with momentum regimes or become redundant if too many variants are used.
Benchmark implications:
Strong and benchmark-clean.
Leakage implications:
Low under past-only rolling computation.
Modularity implications:
High.
Thesis implications:
Strong core market family.
Current judgment:
Core now.

Family: Momentum and reversal family
Problem it tries to solve:
Encode persistence and mean-reversion behavior.
Concept:
5d, 10d, 20d momentum; short-term reversal; rolling slope as trend proxy.
Common implementation styles:
Cumulative return windows, slope on log price, distance from moving averages.
Best arguments in favor:
Stronger and more interpretable than broad derivative proliferation.
Best arguments against:
Can lead to overcomplete technical feature bundles if left unconstrained.
Benchmark implications:
Very important comparator family against derivative proposals.
Leakage implications:
Low if frozen and past-only.
Modularity implications:
High.
Thesis implications:
Core market comparator family.
Current judgment:
Core now.

Family: Volume and liquidity family
Problem it tries to solve:
Capture attention, participation, and tradeability context.
Concept:
Volume surprise, turnover proxies, illiquidity ratios, price-volume interactions.
Common implementation styles:
Current volume relative to trailing average, signed volume shock, volume multiplied by return sign.
Best arguments in favor:
Highly relevant for news-response contexts because attention and liquidity mediate reaction.
Best arguments against:
Some proxies are noisy and data-specific.
Benchmark implications:
Strong comparator family, especially versus derivatives.
Leakage implications:
Low if past-only.
Modularity implications:
High.
Thesis implications:
Strong core-now market family.
Current judgment:
Core now.

Family: Benchmark-relative and residualized feature family
Problem it tries to solve:
Separate stock behavior from common market movement at the feature level.
Concept:
Relative return, rolling beta residuals, factor-like neutralization.
Common implementation styles:
Stock minus market window returns; residuals after simple market regression.
Best arguments in favor:
Very coherent with a thesis about incremental informational value.
Best arguments against:
Factor-neutral versions add extra estimation burden.
Benchmark implications:
Important for honest comparisons.
Leakage implications:
Benchmark/factor alignment must be point-in-time correct.
Modularity implications:
Moderate to high.
Thesis implications:
Potentially stronger than raw feature families once baseline is stable.
Current judgment:
Strong next-step candidate; partial core already through excess-return labels.

Family: Regime context family
Problem it tries to solve:
Condition feature usefulness on broader market state.
Concept:
Market volatility regime, market drawdown state, broad trend state.
Common implementation styles:
Recent benchmark volatility, benchmark momentum, simple bull/bear proxies.
Best arguments in favor:
Likely useful because news-response strength is rarely constant across regimes.
Best arguments against:
Can become an excuse for oversegmentation.
Benchmark implications:
Useful as subgroup analysis before becoming a modeling branch.
Leakage implications:
Low if built past-only.
Modularity implications:
High as contextual features; lower as model-routing logic.
Thesis implications:
Good second-wave addition.
Current judgment:
Strong next-step candidate.

Family: Technical indicator bundle
Problem it tries to solve:
Package common past-price transforms into standard indicators.
Concept:
RSI, MACD, Bollinger features, ATR, and many others.
Common implementation styles:
Indicator libraries or manual computations.
Best arguments in favor:
Convenient and familiar.
Best arguments against:
Often redundant, easy to overstuff, and can hurt interpretability.
Benchmark implications:
Should not dominate the first serious run.
Leakage implications:
Low if computed past-only; high risk of feature-bloat search.
Modularity implications:
High technically, but low scientific cleanliness if too broad.
Thesis implications:
Usually lower ROI than carefully chosen simple families.
Current judgment:
Attractive but risky if widened; not core.

Family: Derivative-like transforms
Problem it tries to solve:
Capture changes in motion or curvature beyond simple returns.
Concept:
First differences, second differences, rolling slopes, change-of-change transforms.
Common implementation styles:
Discrete derivatives on raw or transformed series.
Best arguments in favor:
Might encode trend change or acceleration.
Best arguments against:
Heavy redundancy, scale dependence, noise amplification, search risk.
Benchmark implications:
Must be treated as a constrained late-stage comparator family.
Leakage implications:
High sensitivity to split-adjustment integrity and normalization.
Modularity implications:
Easy to add technically, dangerous to overexpand scientifically.
Thesis implications:
Not strong enough for core status.
Current judgment:
Extension if time allows, possibly attractive but risky depending on breadth.

Full map of candidate event-representation families

Family: Pooled dense article embeddings
Problem it tries to solve:
Represent recent firm-specific semantic information compactly.
Concept:
Precompute article embeddings and pool them over time.
Common implementation styles:
Mean pooling, decay-weighted pooling, date-keyed aggregation.
Best arguments in favor:
Strong balance between semantics, reproducibility, and operational simplicity.
Best arguments against:
May miss event structure and source interactions.
Benchmark implications:
Excellent first event-state family.
Leakage implications:
Depends entirely on correct article timing and no-news handling.
Modularity implications:
Very high. Fits current repo directly.
Thesis implications:
Best default representation family.
Current judgment:
Core now.

Family: Sentiment-only or tone proxy family
Problem it tries to solve:
Simplify text into directional sentiment.
Concept:
Binary or scalar sentiment, polarity, or positive-negative counts.
Common implementation styles:
Finance lexicons, FinBERT sentiment head, simple heuristics.
Best arguments in favor:
Cheap and interpretable.
Best arguments against:
Too reductive for an event-state thesis; loses semantics, novelty, and conflict.
Benchmark implications:
Useful as coarse ablation comparator, not as core event-state representation.
Leakage implications:
Same timing constraints as other text features.
Modularity implications:
High.
Thesis implications:
Good weak-text baseline.
Current judgment:
Comparator only.

Family: Event-state scalar family
Problem it tries to solve:
Capture non-semantic structure in the recent news environment.
Concept:
Density, novelty, conflict, source dispersion, persistence, burstiness.
Common implementation styles:
Counts, similarity scores, entropy-like dispersion measures.
Best arguments in favor:
Directly aligned with event-state theory and often more interpretable than embedding dimensions.
Best arguments against:
Requires careful definitions; some scalars may be noisy or data-source specific.
Benchmark implications:
Strong ablation family to understand why event-state works or fails.
Leakage implications:
Must be computed from correctly aligned article sets only.
Modularity implications:
High.
Thesis implications:
Strong next-step family.
Current judgment:
Strong next-step candidate.

Family: Temporal article sequence family
Problem it tries to solve:
Model within-window article order rather than only pooled state.
Concept:
Keep article sequences and learn temporal weighting via attention or RNNs.
Common implementation styles:
Sequence encoders over article embeddings.
Best arguments in favor:
Potentially more expressive for narrative persistence and conflict resolution.
Best arguments against:
Adds complexity quickly and weakens comparability.
Benchmark implications:
Should come only after pooled event-state baseline is characterized.
Leakage implications:
Time ordering and article-window rules become more delicate.
Modularity implications:
Moderate.
Thesis implications:
Interesting later extension, not first serious representation.
Current judgment:
Attractive but risky.

Family: Event-type tagging family
Problem it tries to solve:
Add interpretable categorical structure to the news state.
Concept:
Tag articles as earnings, litigation, M&A, product, regulation, management, and so on.
Common implementation styles:
Heuristic tagging, weak supervision, classifier heads.
Best arguments in favor:
Very interpretable and potentially useful for heterogeneity analysis.
Best arguments against:
Requires additional labeling logic and may be noisy.
Benchmark implications:
Good extension if tags are stable.
Leakage implications:
Low if tagging uses only available article text.
Modularity implications:
Moderate to high.
Thesis implications:
Useful extension if time permits.
Current judgment:
Extension.

Family: Entity-linked relation-aware event graphs
Problem it tries to solve:
Represent events through linked companies, sectors, peers, or supply-chain relations.
Concept:
Build graph structure across firms and news-linked entities.
Common implementation styles:
Heterogeneous graphs, graph attention, peer-edge propagation.
Best arguments in favor:
Potentially powerful for spillovers and shared-event transmission.
Best arguments against:
High friction, high data burden, weak near-term benchmark cleanliness.
Benchmark implications:
Difficult to compare fairly against simpler systems.
Leakage implications:
High if relations or company profiles are not point-in-time safe.
Modularity implications:
Low to moderate under current repo maturity.
Thesis implications:
Likely beyond the optimal scope of the current restart.
Current judgment:
Attractive but risky.

Family: Static company metadata augmentation
Problem it tries to solve:
Add stable context such as sector, industry, exchange, or identity priors.
Concept:
Augment market plus event-state with slow-moving firm descriptors.
Common implementation styles:
Static feature branch or appended numeric/category features.
Best arguments in favor:
Likely low leakage and modest implementation friction.
Best arguments against:
Not central to the thesis question; can add little.
Benchmark implications:
Should be introduced only after core market plus event-state benchmark is stable.
Leakage implications:
Relatively low if static and correctly versioned.
Modularity implications:
High.
Thesis implications:
Good extension branch.
Current judgment:
Extension if time allows.

Full map of candidate multimodal fusion families

Family: Early concatenation
Problem it tries to solve:
Combine modalities simply.
Concept:
Concatenate market and event-state features before prediction layers.
Common implementation styles:
Single MLP over joined features.
Best arguments in favor:
Minimal, benchmark-clean, low friction.
Best arguments against:
May underuse modality-specific structure.
Benchmark implications:
Excellent simple comparator.
Leakage implications:
No special new leakage.
Modularity implications:
Very high.
Thesis implications:
Good baseline fusion family.
Current judgment:
Core comparator.

Family: Late fusion
Problem it tries to solve:
Let each modality learn separately before fusion.
Concept:
Separate encoders with final-level combination.
Common implementation styles:
Two-branch models with concatenated latent embeddings.
Best arguments in favor:
Strong modularity, good ablation cleanliness, easy interpretation.
Best arguments against:
May miss deeper cross-modal interaction.
Benchmark implications:
Very strong first serious multimodal family.
Leakage implications:
No special new leakage if branches are aligned.
Modularity implications:
Very high.
Thesis implications:
Excellent default fusion family.
Current judgment:
Core now.

Family: Gated fusion
Problem it tries to solve:
Condition the importance of news on context.
Concept:
Learn a gate that modulates the event-state branch relative to the market branch.
Common implementation styles:
Gating scalar or vector on latent features.
Best arguments in favor:
Conceptually aligned with conditional usefulness of news.
Best arguments against:
Slightly higher complexity and harder attribution than pure late concatenation.
Benchmark implications:
Still clean enough for core multimodal use if kept simple.
Leakage implications:
No extra timing leakage.
Modularity implications:
High.
Thesis implications:
Probably the best expressive first multimodal family under current repo maturity.
Current judgment:
Core now.

Family: Residual fusion
Problem it tries to solve:
Model the text branch as an increment over a market baseline.
Concept:
Treat market-only output as base prediction and news as residual corrector.
Common implementation styles:
Residual head or additive correction branch.
Best arguments in favor:
Beautifully aligned with the actual thesis question of incremental value beyond market-only features.
Best arguments against:
Needs careful design to keep training stable.
Benchmark implications:
Could be a very strong next-step variant if core results justify it.
Leakage implications:
No special new leakage.
Modularity implications:
High.
Thesis implications:
Strong next-step candidate.
Current judgment:
Strong next-step candidate.

Family: Cross-attention or deeper interaction fusion
Problem it tries to solve:
Learn richer interactions between modalities.
Concept:
Use attention or interaction layers between market and text representations.
Common implementation styles:
Cross-attention blocks, deeper latent interaction modules.
Best arguments in favor:
Potentially stronger expressiveness.
Best arguments against:
Harder benchmarking, more parameters, more overfitting risk.
Benchmark implications:
Should not precede simpler gated or late fusion.
Leakage implications:
No unique leakage, but more complex pipelines make debugging harder.
Modularity implications:
Moderate.
Thesis implications:
Interesting but not first-choice.
Current judgment:
Attractive but risky.

Family: Expert-routing or mixture-of-experts fusion
Problem it tries to solve:
Route different regimes or conditions to different submodels.
Concept:
Use experts specialized by regime, sector, or news intensity.
Common implementation styles:
Soft gating or hard routing among experts.
Best arguments in favor:
Could fit conditional signal structure.
Best arguments against:
High complexity, hard fairness, easy overfitting, weak current repo fit.
Benchmark implications:
Very difficult to benchmark cleanly without strong prior core results.
Leakage implications:
Indirect risk through oversegmentation and tuning complexity.
Modularity implications:
Lower under current maturity.
Thesis implications:
Poor immediate ROI.
Current judgment:
Probably not worth prioritizing soon.

Full map of candidate model families

Family: OLS, ridge, elastic net
Problem it tries to solve:
Establish whether conservative linear structure exists.
Concept:
Regularized linear prediction with transparent coefficients.
Common implementation styles:
Per-horizon regression or simple multi-output wrappers.
Best arguments in favor:
Strong discipline floor, easy interpretation, low compute.
Best arguments against:
May miss nonlinear interactions.
Benchmark implications:
Mandatory.
Leakage implications:
Low if evaluation is correct.
Modularity implications:
Very high.
Thesis implications:
Non-negotiable baseline family.
Current judgment:
Core now.

Family: Tree-based tabular models
Problem it tries to solve:
Capture nonlinear tabular interactions cheaply.
Concept:
Gradient boosting or similar models over market and pooled event features.
Common implementation styles:
XGBoost, LightGBM, CatBoost style baselines.
Best arguments in favor:
Often strong on tabular data; competitive benchmark family.
Best arguments against:
May complicate unified multi-horizon and saved-latent-branch comparison if the repo is currently MLP-oriented.
Benchmark implications:
Valuable baseline if added carefully.
Leakage implications:
No special new leakage.
Modularity implications:
Moderate.
Thesis implications:
Could strengthen baseline credibility.
Current judgment:
Strong next-step candidate.

Family: Market-only MLP
Problem it tries to solve:
Capture nonlinear structure in market features before adding text.
Concept:
Simple feedforward neural baseline on conservative market features.
Common implementation styles:
Dense layers, dropout, early stopping.
Best arguments in favor:
Already supported, simple, fair comparator to multimodal neural model.
Best arguments against:
Can still overfit on small panels.
Benchmark implications:
Excellent neural baseline.
Leakage implications:
Needs proper scaler fitting and temporal validation.
Modularity implications:
High.
Thesis implications:
Part of core comparator ladder.
Current judgment:
Core now.

Family: First multimodal gated regressor
Problem it tries to solve:
Test incremental value of event-state in a controlled neural setting.
Concept:
Separate market and event-state branches with simple gating or fusion.
Common implementation styles:
Two-branch MLP with concatenation or gating.
Best arguments in favor:
Directly aligned with thesis question and current repo maturity.
Best arguments against:
Still a learned nonlinear model that may obscure attribution unless paired with good baselines.
Benchmark implications:
This is the core multimodal family for the first serious run.
Leakage implications:
Standard temporal and scaling risks only.
Modularity implications:
High.
Thesis implications:
Best current main-model family.
Current judgment:
Core now.

Family: Multi-task multi-horizon model
Problem it tries to solve:
Share information across horizons.
Concept:
One model with multiple horizon outputs.
Common implementation styles:
Shared trunk with horizon heads.
Best arguments in favor:
Efficient, coherent, possibly better generalization.
Best arguments against:
May slightly underperform horizon-specific models; can blur causal interpretation of gains.
Benchmark implications:
Good second-wave comparison after core benchmark is stable.
Leakage implications:
No unique leakage if targets are properly defined.
Modularity implications:
High.
Thesis implications:
Strong next-step architectural comparison.
Current judgment:
Strong next-step candidate.

Family: Ranking-first models
Problem it tries to solve:
Prioritize relative ordering across names.
Concept:
Learn cross-sectional ranking directly rather than point values.
Common implementation styles:
Pairwise ranking losses or listwise ranking objectives.
Best arguments in favor:
Financially meaningful for stock selection and supported by literature [P10] [P24] [P25].
Best arguments against:
Different objective family; should not replace core regression question too early.
Benchmark implications:
Strong secondary evaluation family; training use should come later.
Leakage implications:
Cross-sectional alignment and same-row filtering must be consistent.
Modularity implications:
Moderate.
Thesis implications:
Promising but should remain staged.
Current judgment:
Strong next-step candidate, especially for evaluation.

Family: Uncertainty-aware or probabilistic models
Problem it tries to solve:
Predict confidence and distribution, not just point forecasts.
Concept:
Probability or quantile outputs evaluated by proper scoring rules.
Common implementation styles:
Quantile heads, Gaussian heads, calibrated probabilities.
Best arguments in favor:
Scientifically richer and more honest for uncertain domains.
Best arguments against:
Higher reporting burden, and secondary to proving point-prediction usefulness.
Benchmark implications:
Requires proper scoring rules and calibration plots.
Leakage implications:
No special new leakage.
Modularity implications:
Moderate.
Thesis implications:
Good later extension, not core first-run need.
Current judgment:
Extension if time allows.

Family: Graph or relation-aware models
Problem it tries to solve:
Capture inter-firm spillovers and relation structure.
Concept:
Graph neural or heterogeneous graph models.
Common implementation styles:
Peer graphs, supply-chain graphs, sector graphs, event-entity graphs.
Best arguments in favor:
Potentially captures real spillovers absent from independent stock models.
Best arguments against:
High data and design burden, weak current repo fit, high benchmark risk.
Benchmark implications:
Poor near-term comparability with simpler baselines.
Leakage implications:
High if relations are not point-in-time safe.
Modularity implications:
Low to moderate.
Thesis implications:
Very risky at current maturity.
Current judgment:
Probably not worth prioritizing.

Full map of candidate implementation-technique families

Technique family: Frozen embeddings versus end-to-end fine-tuning
Conceptual logic:
Frozen encoders maximize reproducibility and keep text representation independent from forecast training; end-to-end fine-tuning may improve fit but increases complexity and variance.
Expected upside of frozen:
Stable, cheap, benchmark-clean.
Expected downside of frozen:
May underuse finance-specific nuances.
Expected upside of end-to-end:
Potentially better task-specific representation.
Expected downside of end-to-end:
Higher compute, harder fairness, lower reproducibility, weaker interpretability.
Leakage implications:
No direct extra leakage, but harder debugging can hide issues.
Compute implications:
Frozen is far cheaper.
Modularity implications:
Frozen strongly fits current repo; end-to-end weakens modularity.
Benchmark burden:
End-to-end creates a new benchmark family with many more degrees of freedom.
Thesis value:
Frozen is the correct current default.
Likely worth it:
Frozen yes, end-to-end later only.

Technique family: Offline cache-heavy pipelines versus train-time representation generation
Conceptual logic:
Compute expensive text features once, save them, and evaluate downstream models on frozen artifacts.
Expected upside:
Reproducibility, lower rerun cost, clean comparisons.
Expected downside:
Less flexibility for joint training.
Leakage implications:
Cleaner because feature generation can be audited independently.
Compute implications:
Much better for iterative experiments.
Modularity implications:
Excellent fit to current repo.
Benchmark burden:
Low and favorable.
Thesis value:
Very high because it supports defensible ablations.
Likely worth it:
Yes, absolutely.

Technique family: Deterministic feature pipelines versus train-time feature invention
Conceptual logic:
Explicit preprocessing creates stable, auditable features before training.
Expected upside:
Interpretability and comparability.
Expected downside:
May underuse richer representation learning.
Leakage implications:
Easier to audit.
Compute implications:
Efficient.
Modularity implications:
High.
Benchmark burden:
Lower.
Thesis value:
High.
Likely worth it:
Yes for current stage.

Technique family: Regression-first versus ranking-first versus risk-first formulations
Conceptual logic:
Choose primary objective according to thesis question.
Expected upside of regression-first:
Closer to excess-return thesis framing.
Expected downside:
Weak point fit can obscure relative skill.
Expected upside of ranking-first:
Often better aligned with stock selection.
Expected downside:
Changes the problem framing too early.
Expected upside of risk-first:
Richer risk interpretation.
Expected downside:
Secondary to core question.
Leakage implications:
Similar timing risks across all.
Benchmark implications:
These are different benchmark families and must not be quietly mixed.
Modularity implications:
Moderate.
Thesis value:
Regression-first primary, ranking as strong secondary, risk as extension.
Likely worth it:
Yes in staged order only.

Technique family: Raw targets versus benchmark-relative targets
Conceptual logic:
Choose whether to predict absolute movement or relative/idiosyncratic movement.
Expected upside of benchmark-relative:
Closer to the actual incremental-information thesis.
Expected downside:
Adds dependency on benchmark choice and alignment.
Leakage implications:
Requires benchmark correctness.
Benchmark burden:
A benchmark-relative target is a stronger, cleaner family but must be frozen consistently.
Modularity implications:
High if centralized in label layer.
Thesis value:
Very high.
Likely worth it:
Yes, core now.

Technique family: Static company metadata versus time-varying profile branches
Conceptual logic:
Use stable firm context first; only later consider dynamic descriptive company representations.
Expected upside of static:
Low leakage, low friction, modest context gain.
Expected downside of static:
Limited informational novelty.
Expected upside of time-varying:
Potentially richer context.
Expected downside:
Severe point-in-time risks and higher complexity.
Leakage implications:
Static low, time-varying high.
Benchmark burden:
Dynamic profile branch creates substantial comparability risk.
Modularity implications:
Static high, time-varying moderate to low.
Thesis value:
Static later; dynamic not yet.
Likely worth it:
Static maybe, dynamic not yet.

Deep critical investigation of derivative-like feature proposals

The derivative proposal must first be disambiguated. There is no single derivative family here.

Potential meanings include:
- raw first differences on raw OHLCV
- percentage changes or log differences
- rolling slopes over windows
- second differences on price-like variables
- curvature-like change-of-slope measures
- derivatives on transformed series such as log price, volatility, range, or volume surprise

These families are not equivalent scientifically.

The strongest general criticism is that ordinary return processing, momentum features, rolling slopes, volatility measures, and range-based proxies already capture the most defensible parts of “market motion”. What often remains after that is either redundant or noisy.

Window-by-window evaluation:

1-day window.

Conceptual meaning:
Immediate daily motion or immediate reversal.
What is defensible:
Return, log return, normalized gap, same-day range behavior.
What is weak:
Raw first differences on raw close, or raw second differences on daily close.
Why weak:
Scale dependence, noise amplification, high redundancy with standard returns.
Relation to event-state:
Could matter for immediate reaction, but the project’s end-of-day same-cutoff framing already means much of this is captured more cleanly by standard return/range features.
Judgment:
1-day derivative ideas are acceptable only when translated into standard normalized feature families. They are not a distinct core contribution.

5-day window.

Conceptual meaning:
Short drift or short trend after information arrival.
What is defensible:
5-day cumulative return, rolling slope, change in volume surprise, volatility change.
What is weak:
Raw curvature on daily OHLCV.
Why weak:
Still mostly overlaps with momentum and reversal families.
Relation to event-state:
More plausible than 1-day second-order ideas because short-horizon information absorption is genuinely delayed at times.
Judgment:
Reasonable narrow extension test, not core.

10-day window.

Conceptual meaning:
Short-to-medium trend persistence.
What is defensible:
Trend or slope-like transformed features.
Main problem:
Strong redundancy with momentum windows already considered standard.
Judgment:
Possible comparator, but not enough conceptual uniqueness for core status.

15-day window.

Conceptual meaning:
An intermediate trend window with weak direct theoretical justification.
Main problem:
Looks like search-space expansion more than a conceptually necessary horizon.
Judgment:
Low priority and easy to overfit through window shopping.

20-day window.

Conceptual meaning:
Approximate monthly trend and medium repricing context.
What is defensible:
20-day slope or trend-like transformed features on normalized series.
Best argument for value:
This window has clearer alignment with the project’s 20-day target.
Best argument against value:
It is still mostly a momentum/trend family by another name.
Judgment:
Worth a narrow later test only if it competes directly against momentum, range, and residualized features.

30-day window.

Conceptual meaning:
Longer narrative or regime context.
Best case:
May help longer horizons or regime conditioning.
Main problem:
If the core horizons are 1d, 5d, and 20d, 30d derivative logic may blur regimes and overlapping events without adding much.
Judgment:
Extension only.

First-order versus second-order.

First-order normalized transforms.

Best arguments in favor:
- can capture motion change in interpretable ways
- may complement event-state under short-to-medium horizons
- low friction technically

Best arguments against:
- much of this is already standard returns, momentum, or slope
- novelty may be mostly terminological

Current judgment:
Potentially worth a narrow late-stage comparison, especially if defined as normalized transforms or slopes rather than raw differences.

Second-order transforms.

Best arguments in favor:
- in principle can encode acceleration, curvature, or trend change

Best arguments against:
- daily equity data are noisy enough that second differences often amplify noise faster than they extract structure
- very sensitive to split-adjustment imperfections and normalization choices
- conceptually weak if the project’s main problem is already about event-state incremental value rather than market-feature invention
- large multiple-testing hazard if many windows and many transforms are tried

Current judgment:
Attractive but risky at best; often probably not worth prioritizing.

Benchmark implications of derivative experiments.

Derivative features are uniquely dangerous from a benchmark standpoint because they are easy to generate in many variants. The result is feature-lottery risk.

A fair derivative evaluation requires:
- fixed dataset family
- fixed split source
- fixed target family
- fixed windows chosen in advance
- direct comparison against stronger standard alternatives already present
- explicit reporting of whether derivative gains survive once standard momentum/range/volatility/liquidity features are included

Without that discipline, the derivative branch is benchmark-dangerous.

Stronger alternative feature families versus derivatives

1. Range-based volatility features.

Why stronger:
They directly encode daily uncertainty and price dispersion with clear financial meaning. They are more robust than raw curvature transforms and less likely to duplicate return features ambiguously.

2. Momentum and reversal features.

Why stronger:
They capture the most defensible part of what many derivative advocates want, but in a standard and interpretable form.

3. Volume surprise and liquidity interaction features.

Why stronger:
News effects often depend on attention and trading participation. Volume surprise, turnover, or price-volume interaction is more event-relevant than mathematically richer price derivatives.

4. Benchmark-relative and residualized features.

Why stronger:
They align more directly with the central research question: what news explains beyond broad market motion.

5. Regime context features.

Why stronger:
They explain when the same event-state should matter more or less. This is often more informative than adding curvature-like market transforms.

6. Event-state scalar families.

Why stronger:
Density, novelty, conflict, persistence, and source dispersion directly target the information mechanism under study, whereas derivatives mostly enrich the market branch.

7. Static firm context.

Why stronger in some cases:
If added later, static sector or industry identity may explain conditional differences more cleanly than derivative overengineering.

Bottom line:
If experimentation budget is limited, derivatives should lose priority to these families.

Evaluation and benchmark methodology map

The evaluation protocol should be treated as the scientific center of the thesis.

Core split design.

Established from project materials:
- all evaluation must be strictly out-of-sample in time
- walk-forward folds are the current default split family
- purge and optional embargo are horizon-aware
- alignment uses the official as-of-close rule
- final comparisons should be based on frozen datasets and stored predictions

This is exactly the right philosophy for this project.

Recommended benchmark ladder.

Step 1:
constant predictor and simple linear baselines.
Purpose:
Show the task is not being measured against trivial nonsense.

Step 2:
market-only serious baseline family.
Purpose:
Establish the core non-text skill floor.

Step 3:
first multimodal market plus event-state model.
Purpose:
Test the actual thesis question once under fair conditions.

Step 4:
event-state ablations.
Purpose:
Understand whether the event-state branch is real, conditional, or fragile.

Step 5:
narrow extensions.
Purpose:
Test optional additions only after the core answer is known.

Metrics map.

Primary metrics:
- out-of-sample R-squared
- Pearson and Spearman correlation
- MAE or RMSE as scale-dependent support metrics

Secondary metrics:
- direction accuracy and Brier score if directional outputs are used
- daily information coefficient and ICIR for cross-sectional ranking

Probabilistic metrics if and only if probabilistic outputs are introduced:
- proper scoring rules such as log score or CRPS [P22] [P23]
- calibration diagnostics [P22] [P23] [P11]

Forecast comparison tests.

Supported by external literature or official documentation:
- Diebold-Mariano for non-nested forecast comparison [P19]
- Clark-West for nested forecast settings [P20]
- Giacomini-White for conditional predictive ability [P21]

These are valuable for later thesis-strength reporting, especially when model differences are small.

Statistical restraint.

The legacy research design included thresholds such as market-only R-squared greater than 0.05 on at least one horizon, multimodal delta R-squared at least 0.02 on 5d and 20d, and coefficient of variation below 0.5 across folds. These are useful directional markers, not sacred thresholds. A modest but stable gain may be more scientifically valuable than a threshold-crossing gain that is fold-fragile.

What archived benchmark artifacts currently prove.

Established from project materials:
- the archived smoke artifacts prove that training, checkpointing, prediction export, evaluation, and ablation summary plumbing existed
- they do not prove thesis-level predictive validity because they are tiny, single-split, single-horizon smoke runs

Leakage, comparability, and scientific failure-mode map

Timing leakage.

Most dangerous source. Includes using articles after market close for same-day features, wrong timezone normalization, wrong rollover for weekends, and ambiguous publication timestamps.

Overlapping-label leakage.

Because the project predicts multi-horizon future outcomes, standard chronological splitting is not enough. Purging and possibly embargo are required to stop overlapping future windows from contaminating training.

Scaler-fit leakage.

Very common and often overlooked. Any feature scaler, encoder normalization, or residualization parameter fit on validation or test data invalidates the benchmark.

Corporate-action contamination.

Severe risk. Incorrect split handling can generate fake returns and make derivative-like transforms especially misleading.

Benchmark drift.

If target families, benchmark references, text variants, event-state defaults, or split rules change, the benchmark family changes. Failing to say that explicitly is a scientific failure mode.

Survivorship and universe leakage.

Using a current large-cap universe historically can bias results. The project already recognizes this risk through its emphasis on frozen universe snapshots.

Provider-revision and coverage drift.

Finnhub historical coverage and Twelve Data behavior depend partly on live provider realities. These should be treated as external constraints that require manual verification, not silent constants.

Implementation breadth illusion.

A mature-looking repo can still be testing a weak or poorly framed task. Engineering breadth is not empirical proof.

Multiple-testing illusion.

Every extra horizon, window, target, modality, and feature family increases search-space risk. Derivative-style features are especially vulnerable here because they make it easy to generate many superficially distinct but largely redundant variants.

Implementation-technique tradeoff analysis

Frozen embeddings versus end-to-end fine-tuning.

Tradeoff:
Frozen embeddings are benchmark-clean and operationally light; end-to-end fine-tuning is expressive but expensive and comparability-fragile.
Best current choice:
Frozen embeddings.

Late or gated fusion versus deeper interaction.

Tradeoff:
Late and gated fusion match the incremental-value hypothesis and preserve modularity; deeper cross-attention adds flexibility but weakens benchmark cleanliness.
Best current choice:
Late or gated fusion.

Excess-return targets versus factor-neutral residual targets.

Tradeoff:
Excess returns are simpler and strong enough now; factor-neutral residuals may be better eventually but add an extra layer of assumptions.
Best current choice:
Excess returns first, factor-neutral second.

Regression-first versus ranking-first.

Tradeoff:
Regression-first matches the current thesis framing; ranking-first can be more stable and financially relevant but changes the objective family.
Best current choice:
Regression-first primary, ranking as secondary evaluation and possible later objective.

Static metadata branch versus dynamic company profile.

Tradeoff:
Static metadata is low-risk and low-friction; dynamic profile branches are leakage-prone and harder to defend now.
Best current choice:
Static only later if core results justify it; dynamic not yet.

Offline artifact-driven evaluation versus notebook-state analysis.

Tradeoff:
Artifact-driven evaluation preserves reproducibility and auditability. Notebook-state analysis is convenient but dangerous.
Best current choice:
Artifact-driven evaluation only.

Modularity and repository-fit analysis

The repository fit is strongest when future work respects the modular boundaries already defined in the archived architecture overview and data layout.

Low-friction directions under the current repo design:
- conservative market-feature refinements
- event-state lookback and decay ablations
- ranking as secondary evaluation
- stronger reporting and comparison summaries
- static metadata branch
- narrow derivative-family appendix tests

Medium-friction directions:
- factor-neutral target refinements
- stronger frozen embedding comparisons
- ranking-first training objectives
- uncertainty-aware outputs

High-friction directions:
- time-varying company profile branch
- attention-based event-state sequence encoders
- large-scale tree-based benchmark additions if they require substantial new training orchestration

Architecture-breaking or near-architecture-breaking directions for the current maturity level:
- graph-aware heterogeneous relation systems as a near-term core branch
- mixture-of-experts as a core architecture
- end-to-end large financial language model fine-tuning
- full raw mainstream-news scraping and entity-linking as a co-equal core branch before the current event-state question is settled

Supported by repository evidence:
- the architecture overview explicitly says the current multimodal model is intentionally simple
- the company-profile branch is not yet wired into model training
- richer multimodal ablations are listed as immediate next priorities only after current results are stable and reproducible

The active-root governance shell also matters. It introduces a stronger philosophy of theory-to-design-to-code-to-tests traceability and benchmark integrity, but it is operationally incomplete because the validator currently fails on missing active log files. That means the governance constitution is strong, yet the actual implementation evidence still lives in the archived snapshot.

Broader state-of-the-art map from external literature

Event-driven and event-representation literature.

Works such as Ding et al. [P1] and knowledge-driven event embedding [P2] show that event abstraction is a legitimate route for stock prediction. The key lesson for this project is not to copy older event extraction pipelines directly, but to recognize that richer event abstraction is a more appropriate conceptual basis than generic sentiment.

Financial NLP and domain text representation.

FinBERT [P5], finance-domain sentiment work [P4], BloombergGPT [P6], and FinGPT [P7] collectively support the idea that finance-specific text representations matter. The practical lesson for this thesis is more conservative than “use the biggest finance LLM”. The practical lesson is that domain-aware text encoding is valuable, but the best current tradeoff is still a frozen compact finance-aware encoder or dense embedding approach, not large-model fine-tuning.

Multimodal finance literature.

Recent multimodal finance papers [P8] [P9] show that text plus market data can help, but also that gains are highly contingent on alignment, modality quality, and clean fusion design. The lesson is not “more modalities always help”. The lesson is “multimodal benefit is conditional and must be benchmarked against strong unimodal baselines”.

Ranking and asset-selection literature.

Temporal relational ranking [P10] and the fundamental law of active management [P24] support using ranking metrics and perhaps ranking losses for cross-sectional relevance. The lesson for this project is that ranking should be taken seriously, especially as a secondary evaluation family, because weak point-forecast performance does not necessarily mean no usable cross-sectional skill.

Graph and relation-aware finance literature.

Graph-augmented stock prediction [P11] [P12] [P13] shows there is a real literature on peer and entity-relation structures. The lesson here is narrower: graph-aware methods are plausible extensions, but they are not currently the highest-ROI addition for this repo because relation-safe construction and fair benchmarking are still expensive.

Multi-horizon forecasting literature.

Temporal Fusion Transformers [P14] support shared multi-horizon learning as a legitimate architectural family. The lesson is not that TFT should replace the current repo immediately. The lesson is that multi-horizon heads and horizon-aware reasoning are academically sound and worth comparing against horizon-specific baselines.

Regime-awareness and MoE literature.

Hamilton [P15] supports the idea that regime dependence is real. Older finance MoE references [P16] show the conceptual plausibility of expert specialization. The lesson for this project is not to make regime routing or MoE the core. The lesson is that regime conditioning may matter, but modest contextual regime features are much more defensible right now than a full expert-routing architecture.

Evaluation and validity literature.

Lopez de Prado [P17], Bailey et al. [P18], Tashman [P19], Diebold-Mariano [P20], Clark-West [P21], Giacomini-White [P22], and Gneiting-Raftery [P23] collectively reinforce the most important non-model conclusion of this research pass: if evaluation is weak, the project fails scientifically no matter how attractive the architecture is.

Classification of research directions (core now / strong next / extension / attractive but risky / probably not worth prioritizing)

Core now.
- end-of-day, multi-horizon excess-return forecasting
- event-state-centered conceptual framing
- split-safe adjusted-price label construction
- strict as-of-close article alignment
- conservative market-feature branch
- frozen embeddings plus offline event-state construction
- market-only versus multimodal benchmark ladder
- walk-forward plus purge and embargo
- saved-prediction evaluation on frozen datasets

Strong next.
- event-state pooling ablations
- lookback-window ablations
- news-density and time-period heterogeneity analysis
- stronger ranking-based secondary evaluation
- multi-horizon versus single-horizon comparison
- benchmark-relative and residualized feature refinements
- stronger frozen embedding family comparison

Extension.
- static company metadata branch
- uncertainty-aware outputs
- one richer reporting and statistical comparison layer
- narrow derivative-family test conducted after core benchmark stability
- event-type tagging if cheap and clean

Attractive but risky.
- time-varying company profile branches
- attention-based event-state sequence pooling
- deeper multimodal interaction fusion
- broad derivative-family expansion
- early subgroup-specialized or regime-specialized model routing

Probably not worth prioritizing.
- end-to-end text fine-tuning before the core multimodal question is settled
- mixture-of-experts as near-term thesis core
- graph-aware core redesign before the current architecture is benchmarked thoroughly
- giant target-zoo expansion before one primary target family is stabilized
- full 503-name live benchmark as the first serious thesis family

Recommended research sequencing after this second-order pass

Phase 1: Freeze the serious benchmark family.
- freeze one curated serious universe file
- freeze split-source policy
- freeze benchmark series
- freeze text variant, event-state default, target family, and fold family
- verify live provider realities manually

Phase 2: Run the first serious thesis benchmark.
- constant and linear baselines
- market-only serious baseline
- first multimodal market plus event-state comparison
- saved-prediction evaluation
- fold stability, density subgroups, time-period stability

Phase 3: Understand the event-state branch.
- pooling ablations
- lookback ablations
- semantic representation comparison
- multi-horizon versus single-horizon comparison

Phase 4: Run controlled late extensions only.
- static metadata branch
- narrow derivative-family challenge test
- uncertainty-aware outputs if justified
- one stronger frozen embedding comparison if useful

Phase 5: Write the thesis around the surviving evidence.
- classify findings as robust, conditional, absent, or rejected
- explicitly separate core findings from extension findings
- keep derivative findings subordinate unless they prove unusually strong and stable, which is currently not the expected case

Scientific references and supporting literature

[P1]
Deep Learning for Event-Driven Stock Prediction
Xiao Ding, Yue Zhang, Ting Liu, Junwen Duan
2015
IJCAI 2015
Why it matters to this project: foundational event-driven stock prediction paper; supports event abstraction as a legitimate direction and helps justify why event structure matters more than raw sentiment.
Link: https://www.ijcai.org/Proceedings/15/Papers/329.pdf

[P2]
Knowledge-Driven Event Embedding for Stock Prediction
Xiao Ding, Yue Zhang, Ting Liu, Junwen Duan
2016
COLING 2016
Why it matters to this project: directly relevant precursor for event-state reasoning through event representation rather than simplistic sentiment.
Link: https://aclanthology.org/C16-1201/

[P3]
Giving Content to Investor Sentiment: The Role of Media in the Stock Market
Paul C. Tetlock
2007
The Journal of Finance
Why it matters to this project: classic reference on media content and market behavior; useful for historical context but weaker than event-state framing as a final conceptual basis.
Link: https://doi.org/10.1111/j.1540-6261.2007.01232.x

[P4]
Good debt or bad debt: Detecting semantic orientations in economic texts
Pekka Malo, Ankur Sinha, Pekka J. Korhonen, Jyrki Wallenius, Pyry Takala
2014
Journal of the Association for Information Science and Technology
Why it matters to this project: finance-domain text semantics matter; generic sentiment transfer is weak.
Link: https://doi.org/10.1002/asi.23062

[P5]
FinBERT: Financial Sentiment Analysis with Pre-trained Language Models
Dogu Araci
2019
CoRR / arXiv
Why it matters to this project: strongest compact finance-domain encoder reference for a thesis-scale text branch.
Link: https://arxiv.org/abs/1908.10063
Uncertain, verify manually: use the final preferred citation version if your thesis style requires a peer-reviewed successor.

[P6]
BloombergGPT: A Large Language Model for Finance
Shijie Wu, Ozan Irsoy, Steven Lu, Vadim Dabravolski, Mark Dredze, Sebastian Gehrmann, Prabhanjan Kambadur, David S. Rosenberg, Gideon Mann
2023
CoRR / arXiv
Why it matters to this project: strong evidence that finance-domain pretraining matters, but also a reminder that large-model strategies are likely too heavy for the current thesis scope.
Link: https://doi.org/10.48550/arXiv.2303.17564

[P7]
FinGPT: Open-Source Financial Large Language Models
Hongyang Yang, Xiao-Yang Liu, Christina Dan Wang
2023
CoRR / arXiv
Why it matters to this project: shows open finance-LLM directions, mostly as future context rather than near-term thesis default.
Link: https://doi.org/10.48550/arXiv.2306.06031

[P8]
Stock Movement and Volatility Prediction from Tweets, Macroeconomic Factors and Historical Prices
Shengkun Wang, Yangxiao Bai, Taoran Ji, Kaiqun Fu, Linhan Wang, Chang-Tien Lu
2023
IEEE BigData 2023
Why it matters to this project: relevant multimodal market plus text plus context example; supports heterogeneity-aware fusion thinking.
Link: https://doi.org/10.1109/BigData59044.2023.10386368

[P9]
Multi-modal Attention Network for Stock Movements Prediction
Shwai He, Shi Gu
2021
CoRR / arXiv
Why it matters to this project: useful as a fusion-family reference, though more as architecture inspiration than as immediate thesis-core evidence.
Link: https://arxiv.org/abs/2112.13593

[P10]
Temporal Relational Ranking for Stock Prediction
Fuli Feng, Xiangnan He, Xiang Wang, Cheng Luo, Yiqun Liu, Tat-Seng Chua
2019
ACM Transactions on Information Systems
Why it matters to this project: strong reference for ranking-first formulations and relation-aware stock prediction.
Link: https://doi.org/10.1145/3309547

[P11]
Relational Temporal Graph Convolutional Networks for Ranking-Based Stock Prediction
Zetao Zheng, Jie Shao, Jia Zhu, Heng Tao Shen
2023
ICDE 2023
Why it matters to this project: graph-and-ranking reference for later extension analysis.
Link: https://doi.org/10.1109/ICDE55515.2023.00017

[P12]
Heterogeneous graph knowledge enhanced stock market prediction
Kai Xiong, Xiao Ding, Li Du, Ting Liu, Bing Qin
2021
AI Open
Why it matters to this project: supports knowledge-augmented finance modeling, but also highlights the extra data-design burden of graph systems.
Link: https://doi.org/10.1016/j.aiopen.2021.09.001

[P13]
Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting
Bryan Lim, Sercan Omer Arik, Nicolas Loeff, Tomas Pfister
2021
International Journal of Forecasting
Why it matters to this project: strongest general multi-horizon architecture reference and very relevant to horizon-specific output design.
Link: https://doi.org/10.1016/j.ijforecast.2021.03.012

[P14]
A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle
James D. Hamilton
1989
Econometrica
Why it matters to this project: foundational regime-switching reference; useful for modest regime conditioning, not as a reason to overbuild regime models.
Link: https://doi.org/10.2307/1912559

[P15]
Stock Market Prediction by a Mixture of Genetic-Neural Experts
Giuliano Armano, Andrea Murru, Fabio Roli
2002
International Journal of Pattern Recognition and Artificial Intelligence
Why it matters to this project: conceptual MoE-in-finance reference, mainly useful to show that expert routing is an old idea and not automatically high ROI now.
Link: https://doi.org/10.1142/S0218001402001861

[P16]
Advances in Financial Machine Learning
Marcos Lopez de Prado
2018
Wiley
Why it matters to this project: core source for purge/embargo logic and general financial-ML evaluation discipline.
Link: https://www.wiley.com/en-us/Advances+in+Financial+Machine+Learning-p-9781119482086

[P17]
The probability of backtest overfitting
David H. Bailey, Jonathan M. Borwein, Marcos Lopez de Prado, Qiji Jim Zhu
2016
The Journal of Computational Finance
Why it matters to this project: strongest warning against specification mining and attractive but fragile result selection.
Link: https://doi.org/10.21314/JCF.2016.322

[P18]
Out-of-sample tests of forecasting accuracy: an analysis and review
Leonard J. Tashman
2000
International Journal of Forecasting
Why it matters to this project: foundational source on rolling-origin and out-of-sample evaluation.
Link: https://doi.org/10.1016/S0169-2070(00)00065-0

[P19]
Comparing Predictive Accuracy
Francis X. Diebold, Roberto S. Mariano
1995
Journal of Business and Economic Statistics
Why it matters to this project: standard forecast-comparison test for non-nested predictive models.
Link: https://doi.org/10.1080/07350015.1995.10524599

[P20]
Approximately normal tests for equal predictive accuracy in nested models
Todd E. Clark, Kenneth D. West
2007
Journal of Econometrics
Why it matters to this project: useful when comparing richer models against nested simpler baselines.
Link: https://doi.org/10.1016/j.jeconom.2006.05.023

[P21]
Tests of Conditional Predictive Ability
Raffaella Giacomini, Halbert White
2006
Econometrica
Why it matters to this project: valuable for regime-conditional or subgroup-conditional predictive comparisons.
Link: https://doi.org/10.1111/j.1468-0262.2006.00718.x

[P22]
Strictly Proper Scoring Rules, Prediction, and Estimation
Tilmann Gneiting, Adrian E. Raftery
2007
Journal of the American Statistical Association
Why it matters to this project: foundational for evaluating probabilistic forecasts honestly.
Link: https://doi.org/10.1198/016214506000001437

[P23]
Probabilistic Forecasts, Calibration and Sharpness
Tilmann Gneiting, Fadoua Balabdaoui, Adrian E. Raftery
2007
Journal of the Royal Statistical Society Series B
Why it matters to this project: useful if the thesis later adds uncertainty-aware outputs or calibration claims.
Link: https://doi.org/10.1111/j.1467-9868.2007.00587.x

[P24]
The fundamental law of active management
Richard C. Grinold
1989
The Journal of Portfolio Management
Why it matters to this project: links cross-sectional ranking skill to practical value, supporting rank-based evaluation as a serious secondary family.
Link: https://doi.org/10.3905/jpm.1989.409211

[P25]
Empirical Asset Pricing via Machine Learning
Shihao Gu, Bryan Kelly, Dacheng Xiu
2018
NBER Working Paper 25398
Why it matters to this project: important modern asset-pricing benchmark reference and reminder that noisy returns require disciplined large-sample evaluation.
Link: https://doi.org/10.3386/w25398
Uncertain, verify manually: use the later journal version if your thesis committee prefers it.

[P26]
Common risk factors in the returns on stocks and bonds
Eugene F. Fama, Kenneth R. French
1993
Journal of Financial Economics
Why it matters to this project: core factor-neutral framing reference for abnormal or residual-return targets.
Link: https://doi.org/10.1016/0304-405X(93)90023-5

[P27]
The Performance of Mutual Funds in the Period 1945-1964
Michael C. Jensen
1968
The Journal of Finance
Why it matters to this project: classical alpha or abnormal-return framing reference.
Link: https://doi.org/10.1111/j.1540-6261.1968.tb00815.x

[D1]
Pricing for Individual
Twelve Data
Current official documentation
Official pricing and usage guidance
Why it matters to this project: confirms current free-tier quota framing, endpoint credit interpretation, and access constraints that shape practical experiment scale.
Link: https://twelvedata.com/pricing

[D2]
API Documentation: Company News Endpoint
Finnhub
Current official documentation
Official API endpoint documentation
Why it matters to this project: defines company-news source shape and supports the repo’s firm-news ingestion branch.
Link: https://finnhub.io/docs/api/company-news
Uncertain, verify manually: exact historical coverage and plan-dependent retention for the intended research window.

[D3]
EDGAR Application Programming Interfaces (APIs)
U.S. Securities and Exchange Commission
Current official documentation
Official SEC documentation
Why it matters to this project: supports the company knowledge-base branch and clarifies that submissions JSON and company facts are available without API keys.
Link: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

[D4]
Data Library
Kenneth R. French Data Library
Current official data resource
Official factor and research-return data library
Why it matters to this project: supports factor-neutral and benchmark-relative extensions with widely used research factors and portfolio data.
Link: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

Final brutally honest verdict

The project is now in a better state than the first rewrite captured, but the improvement does not come from having more ideas. It comes from finally being able to say what the project should refuse to become.

What this project is really about now:
It is about testing, under strict end-of-day and leakage-aware conditions, whether an aggregated recent-news event state contributes anything beyond conservative market-only baselines for multi-horizon excess-return forecasting.

What the project should refuse to become:
- a generic price-prediction project
- a trading-bot thesis disguised as forecasting research
- an architecture zoo
- a multimodal everything-bagel
- a feature-proliferation exercise driven by elegance instead of evidence

Whether the derivative family deserves serious attention, narrow testing, postponement, or rejection:
Serious core attention: no.
Narrow controlled testing: yes, later.
Postponement: yes, absolutely until the core benchmark family is stable.
Broad early adoption: no.
Likely ultimate status: either extension-only or rejected, unless it survives strong standard comparator families.

Where the strongest remaining gains are more likely to come from:
Much more likely from target clarity, alignment discipline, benchmark fairness, and sharper event-state design than from architectural novelty. If there is a meaningful gain available here, it is more likely to be unlocked by getting the problem definition and evaluation exactly right than by chasing larger models.

What the single most dangerous next mistake would be:
Letting benchmark drift occur while still speaking as if the results all belonged to the same experiment family.

What should absolutely not be implemented next:
- end-to-end text fine-tuning
- time-varying company profile branches
- graph or expert-routing cores
- broad derivative-window grids
- full live-universe first-pass thesis benchmarks

Whether the thesis should stay broad or become narrower:
It should become narrower. Not because narrowness is elegant, but because breadth is currently the biggest threat to scientific defensibility.

What would make this a strong Master’s thesis rather than just a large engineering project:
Not the number of files, not the number of branches, not the presence of multimodal buzzwords. What would make it strong is a defensible benchmark ladder, explicit leakage control, honest handling of conditional or negative results, and a clear answer to whether event-state information actually helps beyond market-only baselines.

The cleanest operating rule after this second-order pass is unchanged, but it now has much stronger evidentiary backing:

freeze first, verify second, benchmark third, interpret fourth, extend last.
