RESEARCH COMPARISON ADDENDUM: FEATURE FAMILY COMPARISON

Purpose

This document extends `docs/research_results/research_comparison.md` without modifying it.

Its purpose is to compare feature families in more detail, especially because feature inflation is one of the major risks of the project.

This file does not choose a final feature stack.
It defines a measurable way to compare feature families broadly.


SECTION 1. FEATURE-SPECIFIC COMPARISON METHODOLOGY

Feature families are compared using the master framework plus feature-specific factors.

Feature-specific measured factors

1. Signal plausibility
- how plausible it is that the family carries real predictive structure rather than pure transform noise

2. Explainability of effect
- how easy it is to explain why the family helped or hurt

3. Redundancy risk
- how likely it is that the family mostly duplicates stronger simpler families

4. Noise sensitivity
- how fragile the family is to market noise and scaling choices

5. Corporate-action sensitivity
- how much the family depends on very clean split-adjustment and price normalization

6. Temporal responsiveness
- how naturally the family can reflect short versus medium-horizon effects

7. Data dependency burden
- whether the family requires only current data or additional external inputs

8. Feature-bloat risk
- how easily the family explodes into many variants and search-space inflation

9. Accumulative compatibility
- how well it can be added on top of the conservative market branch without redefining it

10. Repo-stage fit
- how well it matches the current implemented structure


SECTION 2. FEATURE FAMILIES INCLUDED

- returns / log returns
- momentum / reversal
- volatility features
- range-based volatility features
- volume surprise and liquidity interactions
- benchmark-relative features
- residualized / factor-aware features
- regime-context features
- event-state scalar features
- sentiment-only text features
- pooled dense text embeddings
- finance-domain frozen text embeddings
- technical indicator bundle
- derivative-like transforms


SECTION 3. DETAILED FEATURE FAMILY PROFILES

Returns / log returns
- Signal plausibility: 5
- Explainability of effect: 5
- Redundancy risk: 4
- Noise sensitivity: 4
- Corporate-action sensitivity: 3
- Temporal responsiveness: 5
- Data dependency burden: 5
- Feature-bloat risk: 5
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - fundamental normalized primitives
  - should remain in any conservative market branch

Momentum / reversal
- Signal plausibility: 5
- Explainability of effect: 4
- Redundancy risk: 3
- Noise sensitivity: 4
- Corporate-action sensitivity: 3
- Temporal responsiveness: 5
- Data dependency burden: 5
- Feature-bloat risk: 4
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - likely stronger than most broad derivative families
  - keep window set disciplined

Volatility features
- Signal plausibility: 4
- Explainability of effect: 4
- Redundancy risk: 3
- Noise sensitivity: 4
- Corporate-action sensitivity: 3
- Temporal responsiveness: 4
- Data dependency burden: 5
- Feature-bloat risk: 4
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - strong risk-state family

Range-based volatility features
- Signal plausibility: 4
- Explainability of effect: 4
- Redundancy risk: 3
- Noise sensitivity: 4
- Corporate-action sensitivity: 3
- Temporal responsiveness: 4
- Data dependency burden: 5
- Feature-bloat risk: 4
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - better use of OHLC information than close-only curvature-style transforms

Volume surprise and liquidity interactions
- Signal plausibility: 5
- Explainability of effect: 4
- Redundancy risk: 3
- Noise sensitivity: 3
- Corporate-action sensitivity: 4
- Temporal responsiveness: 5
- Data dependency burden: 5
- Feature-bloat risk: 4
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - very relevant for news-response contexts

Benchmark-relative features
- Signal plausibility: 5
- Explainability of effect: 4
- Redundancy risk: 2
- Noise sensitivity: 4
- Corporate-action sensitivity: 3
- Temporal responsiveness: 4
- Data dependency burden: 4
- Feature-bloat risk: 4
- Accumulative compatibility: 4
- Repo-stage fit: 4
- Comments:
  - aligned with excess-return logic and central thesis question

Residualized / factor-aware features
- Signal plausibility: 5
- Explainability of effect: 4
- Redundancy risk: 2
- Noise sensitivity: 3
- Corporate-action sensitivity: 3
- Temporal responsiveness: 4
- Data dependency burden: 3
- Feature-bloat risk: 3
- Accumulative compatibility: 3
- Repo-stage fit: 3
- Comments:
  - strong theoretical branch, but heavier factor-data burden

Regime-context features
- Signal plausibility: 4
- Explainability of effect: 4
- Redundancy risk: 2
- Noise sensitivity: 3
- Corporate-action sensitivity: 4
- Temporal responsiveness: 4
- Data dependency burden: 3
- Feature-bloat risk: 3
- Accumulative compatibility: 4
- Repo-stage fit: 3
- Comments:
  - strong second-wave context family if kept simple

Event-state scalar features
- Signal plausibility: 5
- Explainability of effect: 5
- Redundancy risk: 2
- Noise sensitivity: 3
- Corporate-action sensitivity: 5
- Temporal responsiveness: 5
- Data dependency burden: 4
- Feature-bloat risk: 3
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - among the most thesis-aligned feature families

Sentiment-only text features
- Signal plausibility: 3
- Explainability of effect: 5
- Redundancy risk: 3
- Noise sensitivity: 3
- Corporate-action sensitivity: 5
- Temporal responsiveness: 4
- Data dependency burden: 4
- Feature-bloat risk: 5
- Accumulative compatibility: 5
- Repo-stage fit: 4
- Comments:
  - useful weak-text comparator, not likely sufficient core text family

Pooled dense text embeddings
- Signal plausibility: 5
- Explainability of effect: 3
- Redundancy risk: 2
- Noise sensitivity: 4
- Corporate-action sensitivity: 5
- Temporal responsiveness: 5
- Data dependency burden: 4
- Feature-bloat risk: 4
- Accumulative compatibility: 5
- Repo-stage fit: 5
- Comments:
  - strongest current semantic text family for this repo stage

Finance-domain frozen text embeddings
- Signal plausibility: 5
- Explainability of effect: 3
- Redundancy risk: 2
- Noise sensitivity: 4
- Corporate-action sensitivity: 5
- Temporal responsiveness: 5
- Data dependency burden: 4
- Feature-bloat risk: 4
- Accumulative compatibility: 4
- Repo-stage fit: 4
- Comments:
  - likely stronger text semantics, slightly heavier integration burden

Technical indicator bundle
- Signal plausibility: 3
- Explainability of effect: 3
- Redundancy risk: 1
- Noise sensitivity: 3
- Corporate-action sensitivity: 3
- Temporal responsiveness: 4
- Data dependency burden: 5
- Feature-bloat risk: 1
- Accumulative compatibility: 3
- Repo-stage fit: 4
- Comments:
  - technically easy, scientifically risky if expanded beyond a tiny set

Derivative-like transforms
- Signal plausibility: 2
- Explainability of effect: 2
- Redundancy risk: 1
- Noise sensitivity: 2
- Corporate-action sensitivity: 2
- Temporal responsiveness: 4
- Data dependency burden: 5
- Feature-bloat risk: 1
- Accumulative compatibility: 3
- Repo-stage fit: 4
- Comments:
  - narrow first-order transformed variants are more plausible than raw or broad second-order families
  - broad derivative programs are benchmark-dangerous


SECTION 4. FEATURE FAMILY COMPARATIVE TABLE

Feature family | SP | EE | RR | NS | CAS | TR | DDB | FBR | AC | RSF | Comments
-------------- | -- | -- | -- | -- | --- | -- | --- | --- | -- | --- | --------
Returns / log returns | 5 | 5 | 4 | 4 | 3 | 5 | 5 | 5 | 5 | 5 | Core normalized primitives
Momentum / reversal | 5 | 4 | 3 | 4 | 3 | 5 | 5 | 4 | 5 | 5 | Strong, disciplined windows matter
Volatility features | 4 | 4 | 3 | 4 | 3 | 4 | 5 | 4 | 5 | 5 | Strong risk-state family
Range-based volatility | 4 | 4 | 3 | 4 | 3 | 4 | 5 | 4 | 5 | 5 | Better OHLC use than close-only transforms
Volume / liquidity interactions | 5 | 4 | 3 | 3 | 4 | 5 | 5 | 4 | 5 | 5 | Very relevant to news-response dynamics
Benchmark-relative features | 5 | 4 | 2 | 4 | 3 | 4 | 4 | 4 | 4 | 4 | Strong alpha-aligned family
Residualized / factor-aware | 5 | 4 | 2 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | Strong but heavier extension
Regime-context features | 4 | 4 | 2 | 3 | 4 | 4 | 3 | 3 | 4 | 3 | Strong later context family
Event-state scalars | 5 | 5 | 2 | 3 | 5 | 5 | 4 | 3 | 5 | 5 | One of the most thesis-aligned families
Sentiment-only text | 3 | 5 | 3 | 3 | 5 | 4 | 4 | 5 | 5 | 4 | Good weak-text comparator only
Pooled dense embeddings | 5 | 3 | 2 | 4 | 5 | 5 | 4 | 4 | 5 | 5 | Strong current semantic text default
Finance-domain frozen embeddings | 5 | 3 | 2 | 4 | 5 | 5 | 4 | 4 | 4 | 4 | Strong likely upgrade path
Technical indicator bundle | 3 | 3 | 1 | 3 | 3 | 4 | 5 | 1 | 3 | 4 | Easy to overexpand and duplicate signal
Derivative-like transforms | 2 | 2 | 1 | 2 | 2 | 4 | 5 | 1 | 3 | 4 | Narrow late test only

Legend
- SP = Signal plausibility
- EE = Explainability of effect
- RR = Redundancy risk, higher means lower redundancy risk
- NS = Noise sensitivity, higher means lower sensitivity
- CAS = Corporate-action sensitivity, higher means lower sensitivity
- TR = Temporal responsiveness
- DDB = Data dependency burden, higher means lower burden
- FBR = Feature-bloat risk, higher means lower bloat risk
- AC = Accumulative compatibility
- RSF = Repo-stage fit


SECTION 5. SIMILARITY NOTES FOR FEATURES

- Volatility and range-based volatility are very similar overall. Range-based features may be a slightly better use of OHLC bars, but the difference should not be exaggerated.
- Pooled dense embeddings and finance-domain frozen embeddings are also similar overall. The more finance-specific family has slightly stronger theoretical upside but also slightly higher burden.
- Technical-indicator bundles and derivative-like transforms are similar in being easy to generate but risky to overexpand. If both are used, they should be treated as challenge families against stronger conservative baselines, not as core identities.


SECTION 6. NON-DECISION SUMMARY FOR FEATURES

This addendum does not pick a final feature stack.

What it shows clearly is:
- conservative market feature families are stronger than they may look
- event-state scalar enrichments are among the most thesis-aligned feature families available
- volume/liquidity interactions are strong and likely better prioritized than broad derivative-style transforms
- derivative-like families only make sense as narrow late comparisons and not as central restart drivers
