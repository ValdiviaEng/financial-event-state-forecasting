RESEARCH COMPARISON ADDENDUM: MODEL AND FUSION FAMILY COMPARISON

Purpose

This document extends `docs/research_results/research_comparison.md` without modifying it.

Its purpose is to compare model and fusion families in more detail while still refusing to select a winner.


SECTION 1. MODEL- AND FUSION-SPECIFIC COMPARISON METHODOLOGY

Model and fusion families are special because they create the strongest temptation to confuse sophistication with scientific value.

Additional measured factors used here

1. Expressive capacity
- how much complex cross-feature or cross-modal structure the family can in principle capture

2. Interpretability of internals
- how easy it is to understand what the model is doing internally

3. Attribution clarity
- how easy it is to explain whether a gain came from the method itself versus from hidden benchmark or data differences

4. Overfitting resistance
- how robust the family tends to be under moderate sample sizes and noisy targets

5. Hyperparameter sensitivity
- how much results depend on delicate tuning choices

6. Hardware dependency burden
- how much special hardware or long training time the family tends to need

7. Missing-modality robustness
- how well the family handles days or names with weak or absent text signal

8. Branch modularity
- how naturally the family fits the repo’s branch-based architecture


SECTION 2. FUSION FAMILY DETAILED PROFILES

Early concatenation
- Expressive capacity: 2
- Interpretability of internals: 4
- Attribution clarity: 5
- Overfitting resistance: 4
- Hyperparameter sensitivity: 4
- Hardware dependency burden: 5
- Missing-modality robustness: 3
- Branch modularity: 4
- Comments:
  - useful comparator
  - not likely the strongest long-term fusion family

Late fusion
- Expressive capacity: 4
- Interpretability of internals: 4
- Attribution clarity: 5
- Overfitting resistance: 4
- Hyperparameter sensitivity: 4
- Hardware dependency burden: 4
- Missing-modality robustness: 5
- Branch modularity: 5
- Comments:
  - one of the strongest benchmark-clean fusion families available

Gated fusion
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 4
- Overfitting resistance: 4
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 4
- Missing-modality robustness: 5
- Branch modularity: 5
- Comments:
  - very aligned with the idea that text matters conditionally, not uniformly

Residual fusion
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 4
- Overfitting resistance: 4
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 4
- Missing-modality robustness: 4
- Branch modularity: 4
- Comments:
  - especially elegant conceptually for “increment beyond market-only baseline”

Intermediate interaction fusion
- Expressive capacity: 4
- Interpretability of internals: 2
- Attribution clarity: 2
- Overfitting resistance: 3
- Hyperparameter sensitivity: 2
- Hardware dependency burden: 3
- Missing-modality robustness: 3
- Branch modularity: 3
- Comments:
  - strong expressive family but benchmark burden rises quickly

Cross-attention fusion
- Expressive capacity: 5
- Interpretability of internals: 2
- Attribution clarity: 2
- Overfitting resistance: 2
- Hyperparameter sensitivity: 2
- Hardware dependency burden: 2
- Missing-modality robustness: 3
- Branch modularity: 2
- Comments:
  - very interesting literature family
  - weak current-stage fit for a first serious benchmark

MoE / expert-routing fusion
- Expressive capacity: 5
- Interpretability of internals: 1
- Attribution clarity: 1
- Overfitting resistance: 2
- Hyperparameter sensitivity: 1
- Hardware dependency burden: 1
- Missing-modality robustness: 3
- Branch modularity: 2
- Comments:
  - highest complexity burden in this set
  - strong theoretical interest, weak current repo-stage suitability


SECTION 3. MODEL FAMILY DETAILED PROFILES

Linear regularized baselines
- Expressive capacity: 2
- Interpretability of internals: 5
- Attribution clarity: 5
- Overfitting resistance: 5
- Hyperparameter sensitivity: 5
- Hardware dependency burden: 5
- Missing-modality robustness: 5
- Branch modularity: 5
- Comments:
  - indispensable discipline floor

Tree-based tabular models
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 4
- Overfitting resistance: 4
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 4
- Missing-modality robustness: 4
- Branch modularity: 4
- Comments:
  - very strong comparator family if added carefully

Market-only MLP
- Expressive capacity: 4
- Interpretability of internals: 2
- Attribution clarity: 4
- Overfitting resistance: 3
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 4
- Missing-modality robustness: 5
- Branch modularity: 5
- Comments:
  - good nonlinear market-only comparator

Simple multimodal gated regressor
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 4
- Overfitting resistance: 3
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 4
- Missing-modality robustness: 4
- Branch modularity: 5
- Comments:
  - strongest current main multimodal family for the repo stage

Multi-task multi-horizon model
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 3
- Overfitting resistance: 3
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 3
- Missing-modality robustness: 4
- Branch modularity: 4
- Comments:
  - very relevant comparison family after the simpler baseline is understood

Ranking-first model
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 3
- Overfitting resistance: 3
- Hyperparameter sensitivity: 3
- Hardware dependency burden: 3
- Missing-modality robustness: 4
- Branch modularity: 4
- Comments:
  - meaningful but objective-family shift must stay explicit

Uncertainty-aware model
- Expressive capacity: 4
- Interpretability of internals: 3
- Attribution clarity: 3
- Overfitting resistance: 3
- Hyperparameter sensitivity: 2
- Hardware dependency burden: 2
- Missing-modality robustness: 4
- Branch modularity: 4
- Comments:
  - later branch only after deterministic core is stable

Graph-aware model
- Expressive capacity: 5
- Interpretability of internals: 2
- Attribution clarity: 2
- Overfitting resistance: 2
- Hyperparameter sensitivity: 2
- Hardware dependency burden: 2
- Missing-modality robustness: 3
- Branch modularity: 2
- Comments:
  - high design burden around relations and point-in-time safety

Mixture-of-Experts model
- Expressive capacity: 5
- Interpretability of internals: 1
- Attribution clarity: 1
- Overfitting resistance: 2
- Hyperparameter sensitivity: 1
- Hardware dependency burden: 1
- Missing-modality robustness: 3
- Branch modularity: 2
- Comments:
  - very strong complexity with weak current-stage justification


SECTION 4. MODEL AND FUSION COMPARATIVE TABLE

Method / family | EC | II | AC | OFR | HS | HDB | MMR | BM | SVS | BIS | EFS | COS | Comments
--------------- | -- | -- | -- | --- | -- | --- | --- | -- | --- | --- | --- | --- | --------
Early concatenation | 2 | 4 | 5 | 4 | 4 | 5 | 3 | 4 | 3.0 | 4.5 | 4.8 | 4.7 | Clean comparator only
Late fusion | 4 | 4 | 5 | 4 | 4 | 4 | 5 | 5 | 4.1 | 4.8 | 4.6 | 4.7 | Strong benchmark-clean default
Gated fusion | 4 | 3 | 4 | 4 | 3 | 4 | 5 | 5 | 4.4 | 4.4 | 4.1 | 4.2 | Strong conditional-usefulness family
Residual fusion | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 4 | 4.5 | 4.3 | 3.9 | 4.0 | Elegant incremental-value framing
Intermediate interaction | 4 | 2 | 2 | 3 | 2 | 3 | 3 | 3 | 4.0 | 3.4 | 3.1 | 3.3 | More expressive, less clean
Cross-attention | 5 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 4.2 | 3.0 | 2.7 | 2.9 | Strong literature, weak current-stage fit
MoE / expert-routing fusion | 5 | 1 | 1 | 2 | 1 | 1 | 3 | 2 | 3.9 | 2.2 | 1.9 | 2.0 | Attractive but very costly
Linear regularized baseline | 2 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 3.5 | 4.9 | 4.9 | 4.8 | Non-negotiable benchmark floor
Tree-based tabular | 4 | 3 | 4 | 4 | 3 | 4 | 4 | 4 | 4.0 | 4.2 | 3.8 | 3.9 | Strong alternative comparator family
Market-only MLP | 4 | 2 | 4 | 3 | 3 | 4 | 5 | 5 | 4.0 | 4.3 | 4.3 | 4.2 | Good nonlinear market benchmark
Simple multimodal gated regressor | 4 | 3 | 4 | 3 | 3 | 4 | 4 | 5 | 4.4 | 4.4 | 4.0 | 4.1 | Best current main multimodal family
Multi-task multi-horizon model | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4.2 | 3.9 | 3.7 | 4.0 | Strong later comparison family
Ranking-first model | 4 | 3 | 3 | 3 | 3 | 3 | 4 | 4 | 4.1 | 3.5 | 3.2 | 3.4 | Objective-family shift must stay explicit
Uncertainty-aware model | 4 | 3 | 3 | 3 | 2 | 2 | 4 | 4 | 4.0 | 3.2 | 2.9 | 3.2 | Valuable later, not core-first
Graph-aware model | 5 | 2 | 2 | 2 | 2 | 2 | 3 | 2 | 4.0 | 2.6 | 2.1 | 2.4 | High relation and benchmark burden
Mixture-of-Experts model | 5 | 1 | 1 | 2 | 1 | 1 | 3 | 2 | 3.7 | 2.1 | 1.8 | 2.0 | Highest complexity burden here

Legend
- EC = Expressive capacity
- II = Interpretability of internals
- AC = Attribution clarity
- OFR = Overfitting resistance
- HS = Hyperparameter sensitivity, higher means lower sensitivity
- HDB = Hardware dependency burden, higher means lower burden
- MMR = Missing-modality robustness
- BM = Branch modularity


SECTION 5. SIMILARITY NOTES FOR MODELS AND FUSION

- Late fusion and gated fusion are genuinely close. If later benchmark results show tiny differences, they should be treated as similar rather than forced into a hierarchy.
- Linear baselines and market-only MLPs are complementary rather than substitutes: one is the discipline floor, the other is the nonlinear comparator.
- Graph-aware and MoE families are similar in being conceptually rich but currently poor in benchmark cleanliness and repo-stage fit.


SECTION 6. NON-DECISION SUMMARY FOR MODELS AND FUSION

This addendum does not select a final architecture.

What it shows clearly is:
- the strongest current repo-compatible multimodal families are late, gated, and possibly residual fusion
- the strongest benchmark-discipline floor remains linear regularized baselines, with tree-based or MLP market baselines as serious comparators
- graph and MoE families remain on the map, but they score poorly on the dimensions that matter most at the current repo stage
- cross-attention and richer interaction families are valid later comparisons, but they are not benchmark-clean enough to become the immediate default without stronger evidence
