RESTARTING THE RESEARCH: EVENT-STATE-DRIVEN FINANCIAL NEWS IMPACT PREDICTION ON STOCKS

SECTION 0. FILES LOADED AND FILES DEFERRED

Loaded files

Tier A governance and active-root files loaded
- ~/1_Projects/AA/event-state-forecasting/AgentRules.md
- ~/1_Projects/AA/event-state-forecasting/docs/agent/AgentAppendices.md
- ~/1_Projects/AA/event-state-forecasting/docs/agent/AgentCompliance.md
- ~/1_Projects/AA/event-state-forecasting/docs/agent/AgentGlossary.md
- ~/1_Projects/AA/event-state-forecasting/docs/agent/AgentMemory.md
- ~/1_Projects/AA/event-state-forecasting/docs/agent/AgentTemplates.md
- ~/1_Projects/AA/event-state-forecasting/scripts/validate_agent_governance.py
- ~/1_Projects/AA/event-state-forecasting/LEGACY_DEPRECATION_SUMMARY.md
Reason:
- needed to reconstruct the active truth hierarchy, contradiction rules, benchmark comparability discipline, and the real role of the current root

Tier A legacy theory and reconstruction files loaded
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/DEPRECATION_MANIFEST.txt
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/README.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/ChatGPT - HPC - Deep Learning - Foundational Research Instructions.html
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/architecture_overview.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/data_layout.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/evaluation_protocol.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/deep-research-report (2).md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/deep-research-report (5).md
Reason:
- highest marginal information gain for project identity, architecture, storage design, evaluation doctrine, and earlier research drift

Tier B files loaded after Tier A summary
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/ExecutionFlow.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/execution_plan.txt
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/implementation_roadmap.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Expanded_Testing.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/deep-research-report.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/deep-research-report (3).md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/deep-research-report (4).md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/RESEARCH_DESIGN_old.md
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/ROOT_TREE_BEFORE.txt
Reason:
- used only after Tier A ambiguities were identified; these files clarified sequencing, remaining implementation gaps, explicit thresholds, and practical limits

Tier C files loaded selectively
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Complete_guidebook.txt
Reason:
- needed to verify actual file-level maturity across major surfaces after documentation claims were already understood

Tier D repository surfaces inspected as directories
- configs/
- data/
- data/raw/
- data/interim/
- data/final/
- data/embeddings/
- data/kb/
- data/manifests/
- artifacts/
- reports/
- runs/
- src/
- src/cli/
- src/data/
- src/features/
- src/models/
- src/split/
- src/utils/
- tests/
- tests/integration/
- tests/results/
Reason:
- mandatory folder-structure reasoning required by the prompt; directory-level inspection provided structure without wasting context on exhaustive recursive reading

Representative Tier D files loaded
- src/data/corporate_actions.py
- src/data/modeling_dataset.py
- src/data/split_events_pipeline.py
- src/features/market_features.py
- src/features/event_state.py
- src/features/labels.py
- src/split/alignment_rules.py
- src/split/purged_embargo_splits.py
- src/models/baseline_models.py
- src/models/multimodal_models.py
- src/models/metric_registry.py
- tests/test_research_integrity.py
- tests/test_end_to_end_minipipeline.py
- tests/integration/test_live_twelvedata.py
- tests/integration/test_live_finnhub.py
- tests/results/Expanded_Testing_20260319T121411Z.md
- reports/eval_stage14_baseline/evaluation_summary.json
- reports/ablations_stage14/ablation_summary.json
- runs/baseline_stage14_eval_smoke/baseline_training_summary.json
- runs/multimodal_stage13_smoke_fix/multimodal_training_summary.json
Reason:
- enough representative implementation proof to validate maturity claims without loading the entire codebase blindly

Deferred files
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/project_extra_data.txt
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/Complete_Agent_Background.txt
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/requirements.txt
- ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/testing_commands.md
Reason:
- lower marginal information gain after the loaded theory, runbook, roadmap, and guidebook already resolved the main questions

Skipped files and surfaces
- any file ending with :Zone.Identifier
- HTML asset dump folders
- __pycache__/
- compiled .pyc files
- exhaustive recursive reading of all files under src/, tests/, reports/, runs/, data/, configs/, artifacts/
Reason:
- prompt explicitly instructed these to be ignored or deferred unless needed for a specific ambiguity

External literature loaded and triple-verified for paper-note inclusion
- Deep Learning for Event-Driven Stock Prediction
- FinBERT: Financial Sentiment Analysis with Pre-trained Language Models
- Multimodal Transformer for Unaligned Multimodal Language Sequences
- Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting
- Temporal Relational Ranking for Stock Prediction
- Multimodal Machine Learning: A Survey and Taxonomy
- The probability of backtest overfitting
- Comparing Predictive Accuracy
- Common risk factors in the returns on stocks and bonds
- Strictly Proper Scoring Rules, Prediction, and Estimation
- Heterogeneous graph knowledge enhanced stock market prediction
- Price Momentum and Trading Volume
- A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle
- Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles
Reason:
- these form a diverse, literal, source-verified paper set spanning event-driven forecasting, finance NLP, multimodal fusion, multi-horizon forecasting, ranking, factor-neutral targets, graph/knowledge augmentation, regime-awareness, uncertainty, and benchmark validity


SECTION 1. PURPOSE OF THIS RESTART DOCUMENT

This document exists to restart the research on a cleaner, stricter, broader, and more literature-grounded basis than the first implementation cycle. It is not a continuation note. It is not a winner-picking memo. It is not a shallow literature review. It is a restart-grade, repository-first theoretical foundation intended to support a new implementation cycle without losing conceptual truth.

The key reason a restart is justified is not lack of work. It is that the project accumulated multiple overlapping layers:
- early broad project intent
- several waves of deeper research
- an actual but archived first-pass implementation
- a newer governance shell that is stricter than the legacy system
- unresolved questions about targets, alignment, benchmark fairness, derivative-style features, and extension scope

This creates a familiar risk in thesis-scale financial ML work: a repository can become broad enough that engineering momentum hides scientific ambiguity. That is exactly what this restart document is supposed to prevent.

This document therefore has six purposes:
- reconstruct the project literally from the repository and local HTML history
- separate stable project identity from historical drift
- expose the full research space broadly, without choosing a final winner
- expose the implementation space and repository-fit space broadly
- expose the benchmark and leakage risk space broadly
- attach a verified paper-note system so future work can extend the literature base without relying on fuzzy remembered references

The purpose is not elegance.
The purpose is not to preserve every attractive idea.
The purpose is not to decide the final architecture now.
The purpose is to make the space explicit enough that future implementation decisions are informed, benchmark-clean, and hard to rationalize badly.


SECTION 2. GOVERNANCE BASIS AND EPISTEMIC RULES FOR THE RESTART

The active root introduces a much stronger governance layer than the legacy snapshot had. That matters because the project is no longer allowed to behave like an informal pile of research notes and scripts.

Established from repository evidence
- AgentRules.md defines the mandatory dependency chain as Theory -> Design -> Code -> Tests and Benchmarks -> Update and Retraining Operations
- AgentRules.md explicitly forbids changing theory to match code, redefining benchmarks to rescue weak implementation, or allowing README text to override higher-level rules
- the governance layer requires explicit uncertainty language rather than smoothing uncertainty over
- benchmark comparability is treated as a tracked property, not a soft reporting preference

Supported by repository evidence
- AgentAppendices.md formalizes the layered governance structure
- AgentCompliance.md plus validate_agent_governance.py show that governance is partly machine-checked
- AgentGlossary.md makes benchmark comparability change, stale-risk, immutable task contract, and meaningful change into operational categories
- AgentMemory.md shows the project expects long-lived work with interruptions and handoffs, which is exactly the reality of thesis projects

The restart should therefore obey the following epistemic rules.

Rule 1: theory outranks implementation convenience
- if a branch is implemented but not theoretically central, its existence does not make it core

Rule 2: explicit uncertainty outranks smooth narrative
- if a provider behavior, paper detail, or repository capability is unclear, it must remain labeled rather than guessed

Rule 3: contradictions must stay visible
- older and newer docs do not always agree; those differences are evidence, not noise

Rule 4: benchmark families must be treated as real scientific objects
- changing targets, split sources, benchmark series, alignment policy, text variant, or no-news handling changes the benchmark family

Rule 5: active-root governance is philosophically authoritative but operationally incomplete
- the current validator still fails because active log files are missing
- therefore governance rules are strong, but most implementation truth still lives in the archived snapshot

Why this matters for the restart
- finance ML is unusually vulnerable to false progress through leakage, multiple testing, target drift, and architecture inflation
- the governance shell is therefore not overhead; it is a protection layer against exactly the kinds of mistakes this project is now at risk of making


SECTION 3. REPOSITORY STRUCTURE AND EVIDENCE MAP

The repository structure is not background scenery. It is one of the main evidence sources for understanding what the project really became.

Root-level governance files
- root-level governance and deprecation files show that the active root is now primarily a constitutional and fresh-start layer
- implication: the root is stronger as a rules system than as an implementation substrate

docs/agent/
- the distributed governance documents show that the project expects contradiction, stale-risk, approval gates, benchmark drift, and session continuity problems
- implication: this is a project built to survive multiple implementation passes, not a one-off coding assignment

deprecated_version/legacy_snapshot_20260402T115014Z/
- this is the real first-pass implementation body, preserved as a frozen archive
- implication: any serious repository-aware research must treat this as the main implementation evidence base

Theoretical_Background/
- contains architecture, data layout, evaluation protocol, implementation roadmap, older research design, deep-research reports, and project-origin HTML
- implication: this folder is the legacy theory-to-design backbone, not just a miscellaneous notes folder

configs/
- separate config files exist for project, data sources, dataset build, features, labels, baseline models, multimodal models, training, and evaluation
- implication: the project was already config-driven and modular, which supports clean ablations and branch-swapping

data/raw/
- provider-specific raw payload storage
- implication: immutable ingestion was part of the design; good for replayability and auditing

data/interim/
- canonical normalized prices, adjusted prices, split events, news articles, and quality reports
- implication: provider normalization and quality filtering were considered independent stages, not incidental preprocessing

data/final/
- final benchmark, event-state, and modeling-panel artifacts exist
- implication: the pipeline reached real final-panel generation, not only design notes

data/embeddings/
- article embedding cache exists
- implication: frozen text representation is a first-class architectural principle

data/kb/
- company KB, alias tables, and quality reports exist
- implication: static company context and identity reconciliation are already materially supported

data/manifests/
- manifests exist across market, split, news, KB, and panel layers
- implication: reproducibility and source-traceability are already structural design goals

artifacts/
- checkpoints, figures, tables, and panel artifacts exist
- implication: model outputs and analysis artifacts were intended to survive individual runs

reports/
- evaluation and ablation summaries exist
- implication: the project intended a formal report layer, though the visible summaries are still smoke-scale

runs/
- separate baseline and multimodal smoke runs exist
- implication: experiments were already operationalized as isolated run directories

src/cli/
- build and training/evaluation entry points exist for all major pipeline steps
- implication: the project is closer to a research platform than a notebook collection

src/data/
- clients, pipelines, quality checks, split handling, KB, and modeling dataset assembly exist
- implication: data engineering is one of the strongest implemented surfaces in the repo

src/features/
- separate modules exist for market features, labels, event state, news text, news embeddings, and company profile features
- implication: feature families are already modularized and therefore ablation-friendly

src/models/
- baseline models, multimodal models, training, calibration, statistical tests, ablation runner, and metric registry exist
- implication: the modeling layer is real and broad enough to support serious benchmark work, but not evidence that all model families are equally mature scientifically

src/split/
- alignment rules, walk-forward, purge/embargo, and leakage checks exist
- implication: temporal integrity is built as a first-class subsystem, which is one of the repo’s strongest signs of methodological seriousness

src/utils/
- config loading, hashing, IO, reproducibility, and time/calendar logic exist
- implication: the project values deterministic behavior and time-safe utilities

tests/
- broad offline tests exist across pipelines, features, models, evaluation, and integrity
- implication: the legacy snapshot is substantially more mature than a pure prototype

tests/integration/
- live provider tests exist and are opt-in
- implication: the project explicitly distinguishes offline confidence from provider-reality verification

tests/results/
- recorded testing results exist
- implication: manual testing outcomes were documented as artifacts, which is unusually good practice for thesis work

What this structure implies overall

Pipeline maturity
- moderate to high for a first-pass research system
- enough to support serious benchmark runs after stabilization, but not enough to justify broad claims without new controlled evidence

Modular decomposition
- strong
- especially good for market/event-state branch separation, split logic, and feature-family isolation

Evaluation assumptions
- explicitly time-ordered
- explicitly split-aware
- explicitly artifact-driven
- increasingly comparability-aware

Implementation style
- config-driven
- artifact-preserving
- manifest-backed
- CLI-oriented
- test-heavy

Benchmark surfaces
- real and promising
- but visible archived run artifacts are still smoke-sized and not thesis-grade empirical evidence

Compatibility of future extensions with current decomposition

Low-friction compatible
- event-state ablations
- ranking metrics and ranking-first secondary analysis
- static company metadata branch
- narrow derivative-family comparison
- uncertainty-aware outputs

Higher-friction compatible
- factor-neutral targets
- stronger frozen finance-domain encoders
- richer fusion variants

Low-compatibility or architecture-breaking for current maturity
- time-varying profile text branches
- graph-heavy redesign as immediate next step
- MoE as core architecture
- end-to-end large-model text training


SECTION 4. RECONSTRUCTION OF THE PROJECT’S ORIGINAL INTENT AND EVOLUTION

How the project began

The local HTML history and legacy research design show a project that began with broad “financial news impact prediction” language, but even early on it was already leaning toward:
- end-of-day rather than intraday scope
- a limited liquid-stock universe rather than market-wide unconstrained prediction
- multi-horizon forecasting
- market plus text multimodality
- return-style outcomes rather than price-level forecasting

How the framing evolved

The project evolved through several strengthening steps.

Step 1:
move away from naive price prediction toward return-like targets.

Step 2:
move from generic news sentiment thinking toward event-driven or event-state thinking.

Step 3:
move from “text may help” toward “does text add value beyond strong market-only baselines?”

Step 4:
move from broad architecture ideation toward benchmark-first and leakage-first discipline.

What remained stable
- end-of-day scope
- multimodal market plus text framing
- multi-horizon ambition
- strong concern for leakage and split contamination
- strong interest in benchmark fairness

What expanded
- implementation reality expanded dramatically, from concept to full raw/interim/final layers, split handling, event-state construction, baseline and multimodal training, reports, runs, and tests
- theory expanded into many families: graph, profile, uncertainty, ranking, residual targets, derivative-like features, and MoE ideas

What drifted
- the main drift was breadth inflation
- some earlier deep-research materials moved too close to scenario tournaments and winner-picking before the benchmark family was fully stabilized
- derivative-like features repeatedly risked becoming more central than the actual thesis question warrants

What now looks central versus peripheral

Central
- excess-return-oriented multi-horizon EOD forecasting
- event-state framing
- split-safe labels
- market-only versus multimodal benchmark
- strict temporal alignment and saved-artifact evaluation

Peripheral or later
- static metadata branch
- uncertainty outputs
- derivative-family appendix tests
- graph or regime-specialized architectures
- dynamic profile branches


SECTION 5. CURRENT PROJECT IDENTITY

What the project is
- a thesis-grade EOD multimodal financial forecasting system
- a multi-horizon system
- a market plus event-state system
- a benchmarking-sensitive and leakage-aware research platform

What the project is not
- not raw price prediction
- not HFT or intraday
- not an execution or portfolio-management bot
- not a generic “finance LLM” project
- not an article-level causal event-study system

Strongest current academic framing

Temporal multimodal forecasting of horizon-specific stock excess returns using conservative market features and a leakage-safe event-state representation of recent company-related news.

Why this framing is strongest
- it matches the repo and the stronger later theory docs
- it supports clean negative, conditional, or positive results
- it gives the project a clear central benchmark question
- it avoids overstating causality or market efficiency claims


SECTION 6. CORE THEORETICAL CONCEPTS

Event state
- temporally aggregated recent information environment of a firm
- built from aligned news, not one article
- can include density, novelty, conflict, persistence, and source dispersion

Multimodality
- joint use of heterogeneous sources, especially market history and text-derived state
- optional static firm context later

Multi-horizon forecasting
- separate horizons reflect different economic mechanisms of reaction and repricing

Market-only baseline
- the main scientific reference class against which multimodal claims must be judged

Company, profile, or context information
- static firm descriptors or richer time-varying company context
- potentially useful, but secondary to the core market plus event-state question

Ranking versus regression versus risk prediction
- regression predicts numeric future returns or excess returns
- ranking predicts relative ordering across stocks
- risk prediction emphasizes downside or uncertainty

Temporal alignment
- all features on date t must be computable from the information set available by the official date-t cutoff

Leakage
- future or post-cutoff information entering training or evaluation illegitimately

Benchmark comparability
- the condition under which old and new results still belong to the same experimental family

Modularity
- the ability to change a branch without silently redefining data, labels, or evaluation meaning

Thesis contribution versus engineering expansion
- contribution is the strongest defensible surviving claim
- engineering expansion is additional code or modalities that may or may not support that claim


SECTION 7. CURRENT METHODS, TECHNIQUES, AND ARCHITECTURAL BRANCHES ALREADY PRESENT

Established by repo evidence

Data sourcing
- Twelve Data, Finnhub, SEC, and split-event paths are implemented through explicit clients and pipelines

Split handling
- split-events pipeline exists
- local adjustment logic exists
- quality diagnostics exist

Event-state branch
- aligned articles
- offline embedding cache
- daily state aggregation with news_count and optional density/novelty/conflict

Features
- conservative return, momentum, volatility, and volume families
- benchmark-relative return features

Baselines
- ridge and elastic net
- optional market-only MLP

Multimodal path
- market encoder
- event-state encoder
- simple gated fusion
- optional company-profile switch in model builder

Testing
- data contracts
- pipelines
- features
- splits
- research integrity
- live provider integration tests

Benchmarking support
- regression, classification, ranking metrics
- saved-prediction evaluation
- ablation summaries
- calibration/statistical test utilities

Documentation support
- architecture, data, evaluation, runbook, roadmap, testing, and guidebook layers all exist

Plausible but unverified
- full live historical usefulness of provider data at the intended final scale
- thesis-grade stability of archived model performance
- equal maturity of every branch that documentation names

Still aspirational
- dynamic profile branch as a mature trained modality
- graph/relation-aware forecasting
- MoE or expert routing
- end-to-end text fine-tuning
- large-scale final-universe benchmarking as a default first research step


SECTION 8. CURRENT ARCHITECTURE AND PIPELINE PROPOSAL

Raw stage
- fetch raw OHLCV
- fetch raw company-news payloads
- fetch or normalize split events
- fetch KB inputs from SEC where needed
- preserve raw payloads and ledgers

Interim normalization stage
- canonicalize prices
- canonicalize and align articles
- canonicalize split events
- run quality checks
- preserve adjusted-price branch separately

Feature stage
- build conservative market features from adjusted prices
- build embeddings from frozen text pipeline
- aggregate daily event states
- optionally build static KB features

Label stage
- build multi-horizon returns and excess returns from adjusted prices and benchmark forward returns

Final panel stage
- join everything into one ticker-date modeling panel
- write final parquet plus manifest

Split and model stage
- walk-forward folds
- purge and optional embargo
- train market-only baselines
- train first multimodal model

Evaluation stage
- save predictions per run and split
- evaluate against frozen labels
- compare models only inside the same frozen benchmark family

Retraining and update implications
- the architecture is compatible with incremental reruns
- but the thesis contribution should still be benchmark validity and event-state value, not automated retraining as a primary result


SECTION 9. DATA PROCESSING AND DATA CONTROL

What the project’s data processing logic should be
- raw payloads are immutable
- interim tables are canonical
- adjusted prices are separate from raw prices
- features are derived only from canonical validated tables
- final panels are versioned and manifest-backed

What data control rules matter most
- split handling before label generation
- strict article timestamp alignment
- deterministic article deduplication
- explicit no-news handling
- benchmark availability and alignment
- manifest traceability

How to think about split handling
- it is part of target validity, not a minor preprocessing step
- if split-event sourcing changes, the benchmark family changes

How to think about timestamp alignment
- text timing defines the legal information set for date t
- same-day post-close articles are not same-day information under the current policy

How to think about duplicate news
- duplicated articles can fake density, novelty, or agreement structure

Provider limitations
- Twelve Data quotas shape feasible live benchmark scale [D1]
- Finnhub company-news history is usable but must be verified per chosen window [D2]
- SEC KB support is real for static branch construction [D3]

Stale-risk
- any change to benchmark series, split source, text variant, target family, no-news handling, or event-state default is stale-risk for prior comparisons

Point-in-time discipline
- applies to news timestamps, benchmark series, factor data, and any future dynamic profile or macro branch


SECTION 10. BLIND SPOTS, FAILURE MODES, AND CRITICAL RISKS

Leakage channels
- same-day post-close news leakage
- overlap leakage from multi-horizon labels
- scaler-fit leakage
- future profile leakage
- benchmark or factor timing leakage

Corporate actions contamination
- raw unadjusted prices create false returns
- derivative-like transforms worsen this if not normalized and adjusted

Benchmark invalidation triggers
- universe changes
- target changes
- benchmark series changes
- split-source changes
- alignment-rule changes
- event-state default changes

Regime dependence
- text and event-state may help only in some regimes or horizons

Survivorship issues
- static modern universes used historically can bias results

Text timing errors
- timezone errors
- publication vs ingestion-time confusion
- weekend and holiday mapping errors

Feature redundancy
- indicator overload and derivative proliferation can create large redundant spaces

More-data-versus-more-signal confusion
- more modalities and more transforms can raise complexity faster than true predictive value

Modularity that harms comparability
- branch additions that quietly alter upstream row selection or targets are not clean extensions

Architecture complexity masking weak labels
- the project’s biggest danger is to overbuild before the core target and benchmark family are fully stabilized


SECTION 11. TESTING METHODOLOGIES AND VALIDATION PHILOSOPHY

Unit logic
- contract checks
- split math
- label math
- text normalization and hashing
- event-state aggregation logic

Data-contract tests
- canonical schema enforcement
- manifest validation

Pipeline checks
- market pipeline
- split pipeline
- news pipeline
- KB pipeline
- final modeling dataset build

Benchmark validation
- walk-forward split construction
- purge and embargo logic
- research-integrity checks for row-universe equality across comparable runs

Walk-forward philosophy
- strict time ordering is the default evaluation philosophy

Purge and embargo reasoning
- overlapping future windows make simple chronological splits insufficient for multi-horizon tasks

Lockbox logic
- a final untouched recent block is still desirable even if model development uses walk-forward evaluation

What should count as acceptable evidence
- frozen dataset
- saved predictions
- fold-level results
- benchmark-family traceability
- no unresolved integrity blocker affecting the reported result


SECTION 12. BENCHMARKING PHILOSOPHY AND CURRENT BENCHMARK INTERPRETATION

What should be benchmarked
- market-only task learnability
- incremental value of event state
- stability across folds and time
- marginal value of later extensions versus the frozen core benchmark family

How fairness should be maintained
- hold universe, target, split source, benchmark series, text variant, event-state default, fold protocol, and missing-data rules fixed

What kinds of metrics matter
- regression: R-squared, MAE, RMSE, Pearson, Spearman
- ranking: daily IC, ICIR
- classification: AUC, PR-AUC, Brier, direction accuracy
- probabilistic: proper scoring rules only when probabilistic outputs exist

When comparability is preserved versus broken
- preserved when all core benchmark-family components are frozen
- broken when targets, universes, split sources, or alignment policies drift

What benchmark results are interpretable now
- smoke runs prove pipeline operability
- broad tests prove nontrivial maturity
- visible archived performance summaries do not yet prove thesis-grade predictive validity

What benchmark claims should be treated cautiously
- old theoretical thresholds as if they were archival achievements
- any strong claim based only on smoke-scale runs
- any provider-coverage assumption not manually rechecked


SECTION 13. DEEP INVESTIGATION OF DERIVATIVE-BASED FEATURE IDEAS

SUBSECTION 13.1. Clarifying what derivative could mean here

Possible meanings
- discrete first differences
- percentage changes
- log returns
- rolling slopes
- local trend estimates
- second differences
- curvature-like transforms
- derivatives on smoothed series
- derivatives on transformed OHLCV rather than raw OHLCV

Main clarification
- if derivative means normalized first-change or rolling slope, much of it already belongs to standard market-feature families
- if derivative means raw second-order transforms on OHLCV, then novelty is not enough to justify centrality

SUBSECTION 13.2. Evaluating derivative families across windows

1 day
- likely meaning: immediate motion or reversal
- noise risk: low to moderate for normalized first-order, high for second-order
- overlap: extremely high with returns and short-horizon reversal features
- event-state relation: mostly short-horizon only
- interpretability: good only when normalized
- leakage/comparability: technically clean if frozen, but easy to overstate as “new”
- more useful for: short horizon
- first vs second order: first-order only

5 days
- likely meaning: short trend or short drift
- noise risk: moderate for normalized first-order, high for second-order
- overlap: very high with 5-day momentum and slope
- event-state relation: plausible for delayed information absorption
- interpretability: acceptable for slope/cumulative normalized change
- leakage/comparability: benchmark-danger appears if many windows are tried opportunistically
- more useful for: 5-day and maybe 20-day horizons
- first vs second order: first-order plausible, second-order weak

10 days
- likely meaning: short-to-medium trend persistence
- noise risk: moderate for slopes, high for raw curvature
- overlap: high with moving average distance and momentum
- event-state relation: plausible but not unique
- interpretability: moderate
- leakage/comparability: acceptable only if predeclared and narrow
- more useful for: medium horizons
- first vs second order: first-order only unless strong support appears

15 days
- likely meaning: intermediate trend without strong natural timescale justification
- noise risk: secondary issue; the bigger issue is weak motivation
- overlap: high with adjacent momentum windows
- event-state relation: unclear
- interpretability: relatively weak
- leakage/comparability: high window-shopping danger
- more useful for: unclear
- first vs second order: neither clearly justified

20 days
- likely meaning: one-month trend or medium repricing context
- noise risk: manageable for normalized slope, high for second-order curvature
- overlap: high with 20-day momentum and benchmark-relative trend
- event-state relation: strongest derivative-window conceptual match to the project’s 20-day horizon
- interpretability: decent for slope/trend
- leakage/comparability: must compete against stronger standard alternatives
- more useful for: medium horizons
- first vs second order: first-order transformed family plausible

30 days
- likely meaning: longer narrative or regime context
- noise risk: lower for smoothed first-order trend, still high for second-order raw curvature
- overlap: strong with longer trend and regime context families
- event-state relation: maybe relevant for 20-day or optional 60-day tasks
- interpretability: moderate
- leakage/comparability: easy to inflate search space
- more useful for: medium-to-longer horizons
- first vs second order: first-order transformed family only has a plausible case

SUBSECTION 13.3. Comparison against stronger alternatives

Simple returns
- stronger baseline primitive than raw price differences

Log returns
- stronger normalized continuous-change family than raw derivatives

Momentum
- usually captures the main useful content of rolling derivative or slope ideas

Rolling volatility
- stronger risk-state family than price curvature

Range-based measures
- stronger daily-bar use than close-only transforms [P42] [P43] [P44]

Shock indicators
- more directly meaningful than vague curvature in many cases

Trend or slope features
- often the most defensible derivative-like family

Reversal features
- more transparent than second-order raw transforms

Volume-price interactions
- often more relevant to information absorption than derivative novelty [P12]

Smoothed curvature proxies
- closest honest second-order family, but still weakly central

Factor-neutral residuals
- stronger because they align with incremental-value logic [P09] [P39]

Regime features
- stronger because they explain conditional usefulness directly

SUBSECTION 13.4. Hard critique

Strongest argument in favor
- a narrow normalized derivative-like family might capture change-of-motion information that complements event state on 5d and 20d horizons

Strongest argument against
- most useful derivative-like information is already contained in simpler, stronger, and more benchmark-clean families such as returns, momentum, slope, range, and liquidity interactions

Best narrow case where derivatives are worth testing
- late-stage appendix experiment using a very small, predeclared family of normalized first-order or slope-like transforms on transformed series

Best case where they are a distraction
- early in the restart, before the main market-only versus event-state benchmark family is stabilized, or when expanded into large grids of windows and transform definitions

Should the derivative proposal be core, strong extension, optional experiment, or probably rejected?
- core: no
- strong extension: maybe, but only for a narrow normalized first-order family if later evidence supports it
- optional experiment: yes
- probably rejected: broad second-order and raw-derivative grids are already close to this classification


SECTION 14. ALTERNATIVE FEATURE DIRECTIONS THAT MAY BE BETTER THAN DERIVATIVE FEATURES

Alternative: momentum and reversal families
- accuracy potential: medium to high
- complexity: low
- leakage risk: low
- benchmark burden: low
- modularity: high
- repo fit: very high
- thesis defensibility: high
- core judgment: stronger than derivatives now

Alternative: range-based volatility families
- accuracy potential: medium to high
- complexity: low to medium
- leakage risk: low
- benchmark burden: low
- modularity: high
- repo fit: high
- thesis defensibility: high
- core judgment: stronger than derivatives now

Alternative: volume surprise and liquidity interactions
- accuracy potential: medium to high
- complexity: low to medium
- leakage risk: low
- benchmark burden: low
- modularity: high
- repo fit: high
- thesis defensibility: high
- core judgment: stronger than derivatives now

Alternative: benchmark-relative and residualized market features
- accuracy potential: medium to high
- complexity: medium
- leakage risk: medium if benchmark or factor timing is mishandled
- benchmark burden: medium
- modularity: moderate to high
- repo fit: moderate to high
- thesis defensibility: very high
- core judgment: stronger than derivatives for the actual thesis question

Alternative: regime-context features
- accuracy potential: medium
- complexity: medium
- leakage risk: medium
- benchmark burden: medium
- modularity: moderate
- repo fit: moderate
- thesis defensibility: good as a second-wave addition
- core judgment: usually stronger than curvature-style features

Alternative: event-state scalar enrichments
- accuracy potential: medium to high
- complexity: medium
- leakage risk: low if article timing is correct
- benchmark burden: low to medium
- modularity: high
- repo fit: high
- thesis defensibility: very high because these features are directly tied to the project’s main concept
- core judgment: much stronger than derivative-family centrality


SECTION 15. FULL STATE-OF-THE-ART MAP FOR THE RESEARCH PROBLEM

Family: event-driven stock forecasting
Problem it tries to solve
- convert textual or structured event information into predictive market signals
Core idea
- explicit events matter for market reactions
Common implementation styles
- event extraction, event embeddings, event-conditioned predictors
Main strengths
- interpretable event structures
Main weaknesses
- event extraction becomes a bottleneck
- often too close to article-isolation thinking
Main benchmarking difficulties
- hard to separate event extraction quality from predictor quality
Relevance to event-state forecasting
- high historically, but event-state framing is a more realistic generalization

Family: event-state forecasting
Problem it tries to solve
- represent recent firm-related information flow as a state rather than an isolated event
Core idea
- recent overlapping news creates a short-lived information environment
Common implementation styles
- pooled embeddings, decay-weighted state, density/novelty/conflict scalars
Main strengths
- theoretically coherent and highly compatible with EOD scope
Main weaknesses
- many lookback and pooling choices must be disciplined
Main benchmarking difficulties
- risk of small design degrees of freedom becoming hidden benchmark drift
Relevance
- central family for this thesis

Family: financial NLP
Problem it tries to solve
- represent finance-domain language more accurately than generic sentiment systems
Core idea
- finance-domain language needs domain-aware semantics
Common implementation styles
- finance-domain encoders, lexicon baselines, frozen dense embeddings, fine-tuned transformers
Main strengths
- strong semantic capacity
Main weaknesses
- can become compute-heavy quickly
Main benchmarking difficulties
- text variant and encoder choice can silently redefine the problem
Relevance
- very high, especially for the event-state branch

Family: multimodal market-plus-text forecasting
Problem it tries to solve
- combine historical market context and textual information coherently
Core idea
- price history and textual information are complementary but heterogeneous
Common implementation styles
- early, intermediate, or late fusion; gated or residual fusion; cross-attention
Main strengths
- closest direct match to the project’s overall thesis question
Main weaknesses
- alignment quality dominates gains
Main benchmarking difficulties
- weak baselines can make multimodal gains look larger than they are
Relevance
- very high

Family: multi-horizon forecasting
Problem it tries to solve
- predict outcomes at multiple future delays without pretending one horizon is enough
Core idea
- different horizons encode different financial mechanisms
Common implementation styles
- independent models, shared-trunk multi-output models, TFT-like architectures, quantile recurrent models
Main strengths
- directly aligned with the project
Main weaknesses
- harder evaluation and larger design space
Main benchmarking difficulties
- horizon-specific wins can be hidden by pooled reporting
Relevance
- very high

Family: target-design families
Problem it tries to solve
- define the forecast object appropriately
Core idea
- target choice often matters more than architecture
Common implementation styles
- raw returns, excess returns, abnormal returns, ranking targets, downside targets, probabilistic targets
Main strengths
- target design determines whether the project is scientifically coherent
Main weaknesses
- easy source of benchmark drift
Main benchmarking difficulties
- changing target family silently changes the problem
Relevance
- extremely high

Family: feature-engineering families
Problem it tries to solve
- encode market state and event-state context in learnable form
Core idea
- not all engineered features are equally informative or defensible
Common implementation styles
- returns, momentum, volatility, range, liquidity, derivative-like transforms, regime features, event-state scalars
Main strengths
- can make the problem easier without large models
Main weaknesses
- high redundancy risk
Main benchmarking difficulties
- large search spaces create false discoveries
Relevance
- very high

Family: ranking-first formulations
Problem it tries to solve
- predict relative rather than absolute performance
Core idea
- many financial decisions depend more on ordering than exact level
Common implementation styles
- pairwise ranking, listwise losses, IC-based evaluation
Main strengths
- often more stable and financially interpretable
Main weaknesses
- changes the primary task framing
Main benchmarking difficulties
- cross-sectional sampling and filtering must be very consistent
Relevance
- high, but likely secondary or later primary

Family: risk-oriented and uncertainty-aware formulations
Problem it tries to solve
- express confidence, downside, or full distribution rather than only point estimates
Core idea
- uncertain domains benefit from distributional prediction
Common implementation styles
- quantile heads, deep ensembles, MC dropout, calibrated classification probabilities
Main strengths
- stronger scientific honesty under uncertainty
Main weaknesses
- more reporting and calibration burden
Main benchmarking difficulties
- requires proper scoring rules and careful calibration assessment
Relevance
- moderate to high as a later extension

Family: company profile and context augmentation
Problem it tries to solve
- add stable or slowly changing firm context
Core idea
- firms differ structurally and that context can improve generalization or conditioning
Common implementation styles
- static metadata, industry/sector codes, dynamic profile text, KB features
Main strengths
- static context is low risk and may help modestly
Main weaknesses
- dynamic context is leakage-prone
Main benchmarking difficulties
- time-varying profiles can silently break point-in-time realism
Relevance
- moderate

Family: relation-aware and graph-aware methods
Problem it tries to solve
- capture spillovers and inter-firm relations
Core idea
- stocks do not move independently; peers, sectors, and shared events matter
Common implementation styles
- peer graphs, concept graphs, supply-chain graphs, graph attention, temporal graph nets
Main strengths
- potentially strong for spillover effects
Main weaknesses
- high engineering and benchmark burden
Main benchmarking difficulties
- relation definition and point-in-time safety are hard
Relevance
- interesting later, not near-term core

Family: regime-aware systems
Problem it tries to solve
- adapt to changing market states
Core idea
- the same signal may matter differently across regimes
Common implementation styles
- simple regime features, latent-state models, regime-conditioned heads
Main strengths
- likely realistic and useful
Main weaknesses
- can become an excuse for post-hoc slicing
Main benchmarking difficulties
- regime boundaries themselves can be tuned opportunistically
Relevance
- high as second-wave analysis, moderate as model branch

Family: modular architecture families
Problem it tries to solve
- keep research manageable and ablation-friendly
Core idea
- branch separation and frozen artifacts support fair comparison
Common implementation styles
- separate feature branches, late fusion, saved-artifact pipelines, config-driven families
Main strengths
- strong fit to thesis-grade reproducibility
Main weaknesses
- can sometimes underuse expressive interactions
Main benchmarking difficulties
- less about leakage, more about resisting unnecessary coupling
Relevance
- very high

Family: Mixture-of-Experts and expert-routing alternatives
Problem it tries to solve
- route different kinds of cases to different predictors
Core idea
- conditional specialization
Common implementation styles
- regime experts, sector experts, gated experts
Main strengths
- could fit conditional signal structure
Main weaknesses
- high complexity and multiple-testing burden
Main benchmarking difficulties
- difficult attribution and fairness
Relevance
- low near-term, maybe later exploration only

Family: benchmark methodology families
Problem it tries to solve
- decide what constitutes fair evidence
Core idea
- in finance ML, benchmark design is part of the science, not a wrapper around it
Common implementation styles
- walk-forward, purged walk-forward, final lockbox, ranking plus regression metrics, proper scoring rules
Main strengths
- determines credibility of every later claim
Main weaknesses
- stricter methods reduce apparent performance and effective sample size
Main benchmarking difficulties
- temptation to relax discipline when results are weak
Relevance
- central


SECTION 16. METHODOLOGY FAMILIES AND IMPLEMENTATION FAMILIES

Symbolic event-state versus embedding-based event-state

Symbolic event-state
- conceptual logic: represent recent information through structured event tags, sentiment, counts, or categories
- common implementations: event extraction, sentiment tags, category counts, weakly supervised event types
- strengths: high interpretability, low compute, easy ablation
- weaknesses: lower semantic richness, brittle tag quality
- likely repo fit: moderate to high
- benchmarking burden: low
- interpretability: high
- accuracy potential: low to medium unless tagging is strong

Embedding-based event-state
- conceptual logic: represent recent information through dense semantic vectors pooled across time
- common implementations: frozen sentence/document embeddings, finance-domain dense encoders, pooled article vectors
- strengths: strong semantics, already repo-aligned, modular
- weaknesses: lower direct interpretability
- likely repo fit: very high
- benchmarking burden: low to medium
- interpretability: medium
- accuracy potential: medium to high

Early fusion versus intermediate fusion versus late fusion

Early fusion
- conceptual logic: join modalities immediately
- strengths: simple implementation
- weaknesses: weak for asynchronous or noisy modalities
- likely repo fit: high technically
- benchmarking burden: low
- interpretability: medium
- accuracy potential: low to medium

Intermediate fusion
- conceptual logic: partially encode modalities before interaction
- strengths: richer cross-modal learning
- weaknesses: more tuning and attribution difficulty
- likely repo fit: moderate
- benchmarking burden: medium
- interpretability: medium to low
- accuracy potential: medium to high

Late fusion
- conceptual logic: keep branches separate as long as possible
- strengths: clean ablations, strong modularity, high benchmark cleanliness
- weaknesses: may underuse deeper interactions
- likely repo fit: very high
- benchmarking burden: low
- interpretability: high
- accuracy potential: medium to high

Shared-encoder versus branch-based fusion

Shared-encoder
- strengths: parameter sharing, possibly better sample efficiency
- weaknesses: blur modality-specific structure, harder attribution
- repo fit: moderate
- benchmark burden: medium
- interpretability: lower

Branch-based
- strengths: strong modularity, clear ablations, excellent fit to current repo
- weaknesses: may need explicit fusion logic to capture interactions
- repo fit: very high
- benchmark burden: low
- interpretability: high

Ranking-first versus regression-first versus risk-first

Regression-first
- strengths: best fit to current thesis framing
- weaknesses: weak point-fit can hide useful ranking skill
- repo fit: high
- benchmark burden: low
- interpretability: high

Ranking-first
- strengths: financially meaningful for cross-sectional selection
- weaknesses: changes main problem framing
- repo fit: moderate
- benchmark burden: medium
- interpretability: medium

Risk-first
- strengths: richer risk-aware language
- weaknesses: secondary to current core question
- repo fit: moderate
- benchmark burden: medium to high
- interpretability: medium to high

Market-neutral targets versus raw targets

Raw targets
- strengths: simple and traditional baseline
- weaknesses: confound broad market moves
- repo fit: already present but not strongest framing

Market-neutral targets
- strengths: closer to the real incremental-information question
- weaknesses: extra assumptions and benchmark dependencies
- repo fit: moderate to high via excess-return logic, lower for full factor-neutralization

Static company context versus dynamic context

Static context
- strengths: low leakage, low friction, interpretable
- weaknesses: likely modest predictive value
- repo fit: high

Dynamic context
- strengths: richer information
- weaknesses: timing and leakage danger
- repo fit: low to moderate for now

Modular branch design versus tightly coupled design

Modular branch design
- strengths: branch separability, swappability, clean ablations, benchmark cleanliness
- weaknesses: can underuse interactions if too conservative
- repo fit: excellent

Tightly coupled design
- strengths: potentially richer interactions
- weaknesses: attribution difficulty, benchmark burden, lower maintainability
- repo fit: weaker at current maturity

Expert-routed versus non-expert modularity

Non-expert modularity
- strengths: clearer, easier to compare, more reproducible
- weaknesses: less adaptivity
- repo fit: excellent

Expert-routed modularity
- strengths: could model conditional usefulness
- weaknesses: high benchmark burden, high complexity, low current ROI
- repo fit: low to moderate now

Deterministic outputs versus uncertainty-aware outputs

Deterministic outputs
- strengths: simple, current-default compatible, easier benchmark comparisons
- weaknesses: weaker uncertainty characterization

Uncertainty-aware outputs
- strengths: stronger scientific reporting and risk awareness
- weaknesses: added calibration and scoring burden
- repo fit: moderate later, not core first-run need


SECTION 17. FUTURE DIRECTIONS LANDSCAPE WITHOUT CHOOSING A WINNER

Highly aligned and low-friction
- event-state pooling ablations
- lookback-window ablations
- news-density and time-period heterogeneity analysis
- stronger ranking evaluation
- static company metadata branch
- richer report-generation and run-comparison layers

Highly aligned but high-friction
- factor-neutral target families
- stronger frozen finance-domain encoders
- uncertainty-aware outputs with proper scoring rules
- residual-fusion architecture family

Promising but benchmark-sensitive
- ranking-first training objectives
- regime-conditioned market or event-state features
- derivative-family appendix tests
- event-type tagging

Modular but uncertain value
- calendar and earnings-season context features
- static company KB enrichments
- novelty/conflict scalar enrichments beyond the default set

Architecturally interesting but likely risky
- cross-attention fusion for asynchronous modalities
- event-state sequence encoders with learned attention
- graph-aware relation propagation
- time-varying profile branches

Theoretically attractive but possibly low ROI
- MoE or expert-routing systems
- broad derivative grids
- full raw mainstream-news expansions before the current text branch is settled

Worth studying later
- options-implied signals
- macro release-aware branches with point-in-time vintage control
- dynamic profile representations if a true time-indexed source is available

Probably not worth prioritizing soon
- monolithic multimodal transformers as the first serious baseline
- giant indicator bundles
- giant target-zoo expansion
- large live-universe benchmarking before smaller serious benchmarks are stable


SECTION 18. WHAT SHOULD NOW BE TREATED AS CORE, EXTENSION, OPTIONAL, OR REJECT

Core now
- EOD excess-return multi-horizon framing
- event-state concept
- split-safe adjusted-price label discipline
- strict as-of-close alignment
- conservative market feature family
- frozen embeddings plus offline event-state construction
- market-only versus multimodal benchmark ladder
- walk-forward plus purge and embargo
- saved-prediction evaluation

Strong next-step candidate
- event-state pooling ablations
- lookback ablations
- density and time-period heterogeneity analysis
- ranking evaluation and maybe ranking-first secondary objectives
- stronger finance-domain frozen encoder comparison
- benchmark-relative or residualized feature refinements

Extension if time allows
- static company metadata branch
- uncertainty-aware outputs
- event-type tagging
- narrow derivative-family comparison
- richer report-generation and statistical comparison layer

Attractive but risky
- time-varying company profile branches
- attention-based event-state sequences
- deeper multimodal interaction fusion
- graph-aware stock-relation models
- broad derivative expansions
- regime-routed models and small MoE variants

Probably not worth pursuing soon
- end-to-end text fine-tuning now
- MoE as near-term thesis core
- graph-heavy redesign before the core benchmark is settled
- giant target-zoo expansion now
- full 503-name live benchmark as first serious run

Reject
- returning to price-level prediction
- using raw unadjusted OHLCV labels for serious work
- preserving derivative elegance as if it were evidence
- treating pilot or smoke artifacts as final proof


SECTION 19. RECOMMENDED RESEARCH SEQUENCING AFTER THE RESTART

First
- freeze the serious benchmark family
- verify live provider realities and split behavior
- freeze target, universe, benchmark, text variant, event-state default, and fold policy

Second
- run one serious market-only versus market plus event-state benchmark family
- classify the result honestly as robust, conditional, absent, or inconclusive

Third
- run event-state design ablations while keeping the benchmark family frozen

Fourth
- only then allow controlled narrow extensions, including the derivative-family challenge test

Fifth
- assemble the thesis narrative around the strongest surviving evidence, not the most elegant idea


SECTION 20. SCIENTIFIC REFERENCES AND SUPPORTING LITERATURE

[R1]
AgentRules.md
Why it matters: defines the truth hierarchy and benchmark-integrity rules now governing the restart.
Link: ~/1_Projects/AA/event-state-forecasting/AgentRules.md

[R2]
LEGACY_DEPRECATION_SUMMARY.md
Why it matters: confirms the active root is a fresh-start shell and the legacy snapshot is the main archaeological evidence layer.
Link: ~/1_Projects/AA/event-state-forecasting/LEGACY_DEPRECATION_SUMMARY.md

[R3]
deprecated_version/legacy_snapshot_20260402T115014Z/README.md
Why it matters: confirms the snapshot is frozen historical reference, not active implementation source of truth.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/README.md

[R4]
architecture_overview.md
Why it matters: strongest concise architecture source for implemented boundaries and later extensions.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/architecture_overview.md

[R5]
data_layout.md
Why it matters: strongest concise source for data layering, adjusted-price separation, embeddings, KB, and manifests.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/data_layout.md

[R6]
evaluation_protocol.md
Why it matters: strongest concise source for current benchmark philosophy, as-of-close policy, walk-forward, purge, and metric families.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/evaluation_protocol.md

[R7]
RESEARCH_DESIGN_old.md
Why it matters: main legacy theory source for target design, hypotheses, and staging.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/RESEARCH_DESIGN_old.md

[R8]
ExecutionFlow.md
Why it matters: strongest practical source for what the codebase can actually do, where provider constraints matter, and what should not be attempted too early.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/ExecutionFlow.md

[R9]
implementation_roadmap.md
Why it matters: concise retrospective of what is implemented and what remains intentionally postponed.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/implementation_roadmap.md

[R10]
Expanded_Testing.md
Why it matters: documents the test stack and thus the real maturity of the first-pass pipeline.
Link: ~/1_Projects/AA/event-state-forecasting/deprecated_version/legacy_snapshot_20260402T115014Z/Expanded_Testing.md

[P01]
Deep Learning for Event-Driven Stock Prediction
Xiao Ding, Yue Zhang, Ting Liu, Junwen Duan
2015
IJCAI 2015
Why it matters: foundational event-driven prediction reference and historical anchor for moving from raw news toward event abstraction.
Link: https://www.ijcai.org/Abstract/15/329

[P02]
FinBERT: Financial Sentiment Analysis with Pre-trained Language Models
Dogu Araci
2019
Uncertain, verify manually.
Why it matters: strong finance-domain text representation reference; useful for the text branch but metadata require care because the arXiv version is also an MSc thesis artifact.
Link: https://arxiv.org/abs/1908.10063

[P03]
Multimodal Transformer for Unaligned Multimodal Language Sequences
Yao-Hung Hubert Tsai, Shaojie Bai, Paul Pu Liang, J. Zico Kolter, Louis-Philippe Morency, Ruslan Salakhutdinov
2019
ACL 2019
Why it matters: canonical cross-modal attention reference for unaligned multimodal sequences.
Link: https://aclanthology.org/P19-1656/

[P04]
Temporal Fusion Transformers for interpretable multi-horizon time series forecasting
Bryan Lim, Sercan Omer Arik, Nicolas Loeff, Tomas Pfister
2021
International Journal of Forecasting
Why it matters: strongest multi-horizon forecasting family reference and highly relevant architecture baseline.
Link: https://doi.org/10.1016/j.ijforecast.2021.03.012

[P05]
Temporal Relational Ranking for Stock Prediction
Fuli Feng, Xiangnan He, Xiang Wang, Cheng Luo, Yiqun Liu, Tat-Seng Chua
2019
ACM Transactions on Information Systems
Why it matters: key ranking-first and relation-aware stock prediction reference.
Link: https://doi.org/10.1145/3309547

[P06]
Multimodal Machine Learning: A Survey and Taxonomy
Tadas Baltrusaitis, Chaitanya Ahuja, Louis-Philippe Morency
2019
IEEE Transactions on Pattern Analysis and Machine Intelligence
Why it matters: strongest general multimodal taxonomy for this thesis.
Link: https://doi.org/10.1109/TPAMI.2018.2798607

[P07]
The probability of backtest overfitting
David H. Bailey, Jonathan M. Borwein, Marcos Lopez de Prado, Qiji Jim Zhu
2016 online / 2017 issue-date ambiguity
The Journal of Computational Finance
Why it matters: strongest warning against multiple-testing illusion in finance.
Link: https://doi.org/10.21314/JCF.2016.322
Uncertain, verify manually: use the exact year convention preferred by your thesis style guide.

[P08]
Comparing Predictive Accuracy
Francis X. Diebold, Roberto S. Mariano
1995
Journal of Business and Economic Statistics
Why it matters: standard forecast-comparison test for competing predictive models.
Link: https://doi.org/10.1080/07350015.1995.10524599

[P09]
Common risk factors in the returns on stocks and bonds
Eugene F. Fama, Kenneth R. French
1993
Journal of Financial Economics
Why it matters: standard factor and target-neutralization framing.
Link: https://doi.org/10.1016/0304-405X(93)90023-5

[P10]
Strictly Proper Scoring Rules, Prediction, and Estimation
Tilmann Gneiting, Adrian E. Raftery
2007
Journal of the American Statistical Association
Why it matters: foundational proper-scoring reference for probabilistic or uncertainty-aware extensions.
Link: https://doi.org/10.1198/016214506000001437

[P11]
Heterogeneous graph knowledge enhanced stock market prediction
Kai Xiong, Xiao Ding, Li Du, Ting Liu, Bing Qin
2021
AI Open
Why it matters: direct graph-and-knowledge extension reference.
Link: https://doi.org/10.1016/j.aiopen.2021.09.001

[P12]
Price Momentum and Trading Volume
Charles M.C. Lee, Bhaskaran Swaminathan
2000
The Journal of Finance
Why it matters: strong support for price-volume interaction features as serious alternatives to derivative-style ideas.
Link: https://doi.org/10.1111/0022-1082.00280

[P13]
A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle
James D. Hamilton
1989
Econometrica
Why it matters: foundational regime-switching reference for regime-aware thinking.
Link: https://doi.org/10.2307/1912559

[P14]
Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles
Balaji Lakshminarayanan, Alexander Pritzel, Charles Blundell
2017
Advances in Neural Information Processing Systems 30
Why it matters: practical uncertainty-estimation reference for later predictive-uncertainty branches.
Link: https://proceedings.neurips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html

[D1]
Pricing for Individual
Twelve Data
Official pricing documentation
Why it matters: confirms quota and request constraints shaping feasible benchmark scale.
Link: https://twelvedata.com/pricing

[D2]
API Documentation: Company News Endpoint
Finnhub
Official API documentation
Why it matters: defines the shape of the firm-news source used by the project.
Link: https://finnhub.io/docs/api/company-news

[D3]
EDGAR Application Programming Interfaces (APIs)
U.S. Securities and Exchange Commission
Official documentation
Why it matters: supports the static company KB branch and filing-derived context.
Link: https://www.sec.gov/search-filings/edgar-application-programming-interfaces

[D4]
Kenneth R. French Data Library
Kenneth R. French
Official data resource
Why it matters: provides practical factor-return resources for factor-neutral target extensions.
Link: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html


SECTION 21. FINAL RESEARCH-STATE CONCLUSION WITHOUT FINAL SELECTION

What the project should now be about at its core
- a disciplined test of whether aligned recent-news event states add value beyond conservative market-only baselines for end-of-day multi-horizon excess-return forecasting

Whether the derivative idea appears worth serious attention
- yes, but only narrowly and later
- not as the core restart driver
- only after strong standard alternatives are already in the benchmark family

What the strongest unresolved theoretical questions are
- does market-only learning show stable out-of-sample skill under the final serious benchmark family?
- does the event-state branch add robust, conditional, weak, or no value beyond that baseline?
- which event-state design choices matter most?
- are ranking and regression telling the same or different stories?
- does any derivative-like family survive fair comparison against momentum, range, volatility, and liquidity alternatives?

What the most dangerous next mistakes would be
- benchmark drift hidden as continuity
- architecture inflation before the core claim is settled
- overclaiming weak or unstable gains
- skipping live provider verification
- using extensions to avoid resolving the central comparison

What should definitely not be done next
- do not make derivatives the next main axis
- do not add end-to-end text fine-tuning now
- do not add dynamic company-profile branches now
- do not jump to graph or MoE cores now
- do not use a giant live universe as the first serious thesis benchmark

What should be stabilized before any new implementation starts
- benchmark family
- target family
- split-source policy
- benchmark series
- text variant
- event-state default
- fold protocol
- saved-artifact reporting packet
- provider reality checks

What parts of the state of the art appear most relevant to event-state forecasting specifically
- event abstraction and event-state aggregation
- finance-domain text representation
- late and gated multimodal fusion
- multi-horizon forecasting families
- ranking metrics and rank-based evaluation
- purge/embargo time-aware evaluation
- factor-neutral and excess-return framing
- conditional heterogeneity analysis

What parts of the prior project history should be preserved versus discarded

Preserve
- return-style task framing
- event-state concept
- split-safe adjustment discipline
- strict alignment culture
- baseline-first architecture
- artifact- and manifest-driven evaluation

Discard or demote
- price-level drift
- architecture-for-its-own-sake
- derivative elegance as evidence
- extension inflation before the core benchmark is settled
- smoke artifacts as final proof

Final nonfinal conclusion

The right next move is not to select the winner now. The right next move is to freeze the serious benchmark family, verify the remaining provider and split realities, run the core market-only versus event-state benchmark once correctly, and only then widen the space through controlled ablations and late-stage extensions.

The project is broad enough already.
The next phase should make it truer, not bigger.
