RESEARCH COMPARISON ADDENDUM: EVENT REPRESENTATION COMPARISON

Purpose

This document extends `docs/research_results/research_comparison.md` without modifying it.

Its purpose is to compare event and text representation families in more detail than the master comparison file. This is especially important because the project’s conceptual identity depends heavily on how “event state” is represented.

This document does not choose a final event representation.
It creates a broad and measurable way to compare them.


SECTION 1. EVENT-REPRESENTATION-SPECIFIC COMPARISON METHODOLOGY

Event representation families need some category-specific factors beyond the master scoring system.

Additional measured factors used here

1. Semantic richness
- how much real semantic content the representation can preserve

2. Temporal faithfulness
- how naturally the representation respects the idea of an evolving recent-news state rather than one isolated event

3. Sparsity robustness
- how well the representation behaves when news is sparse, missing, uneven, or bursty

4. No-news handling clarity
- how easy it is to define and explain behavior on no-news dates

5. Source-noise robustness
- how resilient the representation is to duplicates, low-quality articles, or noisy source mixtures

6. Interpretability to thesis reader
- how easy it is to explain what the representation means conceptually

7. Aggregation simplicity
- how easy it is to aggregate the representation over time without introducing fragile design choices

8. Accumulative compatibility
- how easily the representation can coexist with the current market branch and later extension branches


SECTION 2. EVENT REPRESENTATION FAMILIES INCLUDED

- lexicon / sentiment-only event proxies
- headline-only dense embeddings
- headline-plus-summary dense embeddings
- finance-domain frozen embeddings
- event-state scalar family
- event-type tagging family
- topic-state family
- temporal article sequence family
- KB-augmented event-state family
- graph / entity-event representation family
- dynamic profile-conditioned event-state family


SECTION 3. DETAILED EVENT REPRESENTATION PROFILES

Lexicon / sentiment-only event proxies
- Semantic richness: 2
- Temporal faithfulness: 3
- Sparsity robustness: 4
- No-news handling clarity: 5
- Source-noise robustness: 3
- Interpretability to thesis reader: 5
- Aggregation simplicity: 5
- Accumulative compatibility: 5
- SVS: 2.8
- BIS: 4.3
- EFS: 4.7
- COS: 4.6
- Confidence: 4
- Comments:
  - very strong weak-text baseline
  - too reductive for the project’s core event-state identity

Headline-only dense embeddings
- Semantic richness: 3
- Temporal faithfulness: 4
- Sparsity robustness: 4
- No-news handling clarity: 4
- Source-noise robustness: 4
- Interpretability to thesis reader: 3
- Aggregation simplicity: 5
- Accumulative compatibility: 5
- SVS: 3.8
- BIS: 4.3
- EFS: 4.4
- COS: 4.4
- Confidence: 4
- Comments:
  - cheap semantic baseline
  - likely weaker than headline-plus-summary or finance-domain embeddings

Headline-plus-summary dense embeddings
- Semantic richness: 4
- Temporal faithfulness: 5
- Sparsity robustness: 4
- No-news handling clarity: 4
- Source-noise robustness: 4
- Interpretability to thesis reader: 3
- Aggregation simplicity: 5
- Accumulative compatibility: 5
- SVS: 4.2
- BIS: 4.4
- EFS: 4.4
- COS: 4.4
- Confidence: 5
- Comments:
  - strongest generic dense embedding default
  - very good match to the current repo stage

Finance-domain frozen embeddings
- Semantic richness: 5
- Temporal faithfulness: 5
- Sparsity robustness: 4
- No-news handling clarity: 4
- Source-noise robustness: 4
- Interpretability to thesis reader: 3
- Aggregation simplicity: 4
- Accumulative compatibility: 4
- SVS: 4.4
- BIS: 4.1
- EFS: 3.8
- COS: 3.9
- Confidence: 4
- Comments:
  - likely strongest frozen semantic family
  - slightly heavier integration and verification burden than generic dense embeddings

Event-state scalar family
- Semantic richness: 3
- Temporal faithfulness: 5
- Sparsity robustness: 5
- No-news handling clarity: 5
- Source-noise robustness: 4
- Interpretability to thesis reader: 5
- Aggregation simplicity: 4
- Accumulative compatibility: 5
- SVS: 4.3
- BIS: 4.5
- EFS: 4.2
- COS: 4.5
- Confidence: 4
- Comments:
  - strongest interpretable event-state family
  - especially valuable for explaining where and why the text branch helps

Event-type tagging family
- Semantic richness: 3
- Temporal faithfulness: 4
- Sparsity robustness: 3
- No-news handling clarity: 4
- Source-noise robustness: 3
- Interpretability to thesis reader: 5
- Aggregation simplicity: 4
- Accumulative compatibility: 4
- SVS: 3.8
- BIS: 4.0
- EFS: 3.7
- COS: 3.9
- Confidence: 3
- Comments:
  - useful if tagging quality is good
  - weakly supervised or heuristic tags can become brittle

Topic-state family
- Semantic richness: 4
- Temporal faithfulness: 4
- Sparsity robustness: 3
- No-news handling clarity: 3
- Source-noise robustness: 3
- Interpretability to thesis reader: 4
- Aggregation simplicity: 3
- Accumulative compatibility: 4
- SVS: 3.9
- BIS: 3.6
- EFS: 3.3
- COS: 3.6
- Confidence: 3
- Comments:
  - attractive way to compress recurring narratives
  - harder to benchmark cleanly than pooled embeddings plus scalars

Temporal article sequence family
- Semantic richness: 4
- Temporal faithfulness: 5
- Sparsity robustness: 3
- No-news handling clarity: 3
- Source-noise robustness: 3
- Interpretability to thesis reader: 2
- Aggregation simplicity: 2
- Accumulative compatibility: 3
- SVS: 4.1
- BIS: 3.1
- EFS: 2.8
- COS: 3.0
- Confidence: 3
- Comments:
  - richer sequence semantics
  - much harder to keep benchmark-clean than pooled state families

KB-augmented event-state family
- Semantic richness: 4
- Temporal faithfulness: 4
- Sparsity robustness: 4
- No-news handling clarity: 4
- Source-noise robustness: 4
- Interpretability to thesis reader: 4
- Aggregation simplicity: 3
- Accumulative compatibility: 4
- SVS: 4.0
- BIS: 3.9
- EFS: 3.6
- COS: 4.0
- Confidence: 3
- Comments:
  - strong future direction if static KB and entity resolution are stable
  - more realistic than full dynamic profile branches

Graph / entity-event representation family
- Semantic richness: 5
- Temporal faithfulness: 4
- Sparsity robustness: 3
- No-news handling clarity: 2
- Source-noise robustness: 3
- Interpretability to thesis reader: 2
- Aggregation simplicity: 1
- Accumulative compatibility: 2
- SVS: 4.0
- BIS: 2.8
- EFS: 2.3
- COS: 2.5
- Confidence: 3
- Comments:
  - potentially powerful
  - very high design and benchmark burden under current maturity

Dynamic profile-conditioned event-state family
- Semantic richness: 5
- Temporal faithfulness: 4
- Sparsity robustness: 4
- No-news handling clarity: 2
- Source-noise robustness: 3
- Interpretability to thesis reader: 2
- Aggregation simplicity: 1
- Accumulative compatibility: 2
- SVS: 3.9
- BIS: 2.0
- EFS: 2.0
- COS: 2.2
- Confidence: 2
- Comments:
  - attractive on paper
  - currently one of the most leakage-sensitive directions in the whole map


SECTION 4. EVENT REPRESENTATION COMPARATIVE TABLE

Representation family | SR | TF | SPR | NHC | SNR | ITR | AS | AC | SVS | BIS | EFS | COS | Comments
--------------------- | -- | -- | --- | --- | --- | --- | -- | -- | --- | --- | --- | --- | --------
Lexicon / sentiment-only | 2 | 3 | 4 | 5 | 3 | 5 | 5 | 5 | 2.8 | 4.3 | 4.7 | 4.6 | Useful weak-text comparator, not core event-state identity
Headline-only dense embeddings | 3 | 4 | 4 | 4 | 4 | 3 | 5 | 5 | 3.8 | 4.3 | 4.4 | 4.4 | Cheap semantic baseline
Headline-plus-summary dense embeddings | 4 | 5 | 4 | 4 | 4 | 3 | 5 | 5 | 4.2 | 4.4 | 4.4 | 4.4 | Strong current default
Finance-domain frozen embeddings | 5 | 5 | 4 | 4 | 4 | 3 | 4 | 4 | 4.4 | 4.1 | 3.8 | 3.9 | Strong later upgrade path
Event-state scalars | 3 | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 4.3 | 4.5 | 4.2 | 4.5 | One of the most thesis-aligned families
Event-type tagging | 3 | 4 | 3 | 4 | 3 | 5 | 4 | 4 | 3.8 | 4.0 | 3.7 | 3.9 | Useful if tags are trustworthy
Topic-state | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 4 | 3.9 | 3.6 | 3.3 | 3.6 | Attractive but harder to benchmark cleanly
Temporal article sequence | 4 | 5 | 3 | 3 | 3 | 2 | 2 | 3 | 4.1 | 3.1 | 2.8 | 3.0 | Richer, but less clean and heavier
KB-augmented event-state | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4.0 | 3.9 | 3.6 | 4.0 | Good future middle ground
Graph / entity-event | 5 | 4 | 3 | 2 | 3 | 2 | 1 | 2 | 4.0 | 2.8 | 2.3 | 2.5 | Powerful but high burden
Dynamic profile-conditioned | 5 | 4 | 4 | 2 | 3 | 2 | 1 | 2 | 3.9 | 2.0 | 2.0 | 2.2 | Very leakage-sensitive

Legend
- SR = Semantic richness
- TF = Temporal faithfulness
- SPR = Sparsity robustness
- NHC = No-news handling clarity
- SNR = Source-noise robustness
- ITR = Interpretability to thesis reader
- AS = Aggregation simplicity
- AC = Accumulative compatibility


SECTION 5. SIMILARITY NOTES FOR EVENT REPRESENTATIONS

- Headline-plus-summary dense embeddings and finance-domain frozen embeddings are close overall; the latter likely has more semantic upside while the former is slightly easier to standardize.
- Event-state scalars and pooled dense embeddings are complementary rather than competing. One offers semantic richness, the other offers interpretability and clearer causal-trace-style explanation.
- Graph/entity-event and dynamic profile-conditioned families are both strong in expressive ambition and weak in current benchmark cleanliness.


SECTION 6. NON-DECISION SUMMARY FOR EVENT REPRESENTATIONS

This addendum does not pick a final event representation.

What it shows clearly is:
- pooled dense embeddings plus event-state scalar enrichments are the strongest broad current families
- finance-domain frozen embeddings are a strong next-step semantic upgrade
- temporal article sequence and graph-heavy families remain real but comparatively costly
- dynamic profile-conditioned event-state remains one of the riskiest late directions
