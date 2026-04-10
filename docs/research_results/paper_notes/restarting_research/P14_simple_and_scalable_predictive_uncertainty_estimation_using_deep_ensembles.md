Paper ID
- P14

Full citation
- Balaji Lakshminarayanan, Alexander Pritzel, and Charles Blundell. 2017. Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles. In Advances in Neural Information Processing Systems 30, 6402-6413.

Verification log
- Verification status: verified with a DOI ambiguity.
- NeurIPS proceedings and DBLP agree on the final publication.
- A preprint DOI exists for the arXiv version, but the final proceedings paper does not have a clearly established separate DOI from the verified sources used here.

Source 1
- arXiv abstract page
- https://arxiv.org/abs/1612.01474

Source 2
- NeurIPS proceedings abstract page
- https://proceedings.neurips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html

Source 3
- DBLP record
- https://dblp.org/rec/conf/nips/Lakshminarayanan17.html

Exact title
- Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles

Authors
- Balaji Lakshminarayanan
- Alexander Pritzel
- Charles Blundell

Year
- 2017

Venue
- Advances in Neural Information Processing Systems 30

DOI
- Uncertain, verify manually.

Stable links
- https://arxiv.org/abs/1612.01474
- https://proceedings.neurips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html
- https://dblp.org/rec/conf/nips/Lakshminarayanan17.html

Research family
- Uncertainty-aware prediction
- Deep ensembles

Why relevant to this project
- It is one of the most practical references for adding predictive uncertainty without redesigning the entire architecture around full Bayesian deep learning.

Main problem addressed
- Estimating predictive uncertainty in deep learning with a simple, scalable ensemble strategy.

Inputs / modalities
- Uncertain, verify manually.

Target design
- Classification and regression uncertainty estimation.

Model family
- Deep ensembles.

Evaluation design
- Classification and regression benchmarks.
- Includes dataset-shift evaluation and a large-scale experiment according to the verified snippets.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Uncertainty estimation does not solve leakage or benchmark drift.
- Ensemble performance can still be overstated if all members share the same flawed benchmark family.

Pros
- Practical and modular.
- Easier to add than full Bayesian forecasting machinery.
- Useful for later uncertainty-aware extensions.

Cons
- Not finance-specific.
- Verified source snippets here do not establish the full calibration metric set.

Repository-fit implications
- Fits well as a later wrapper around an already stable neural forecasting family.

Modularity implications
- Strongly modular, because base predictors and ensemble aggregation can remain separate layers.

What this paper supports
- Deep ensembles as a sensible uncertainty-aware extension family.

What this paper does not support
- That uncertainty modeling should precede solving the core deterministic benchmark question.
- Any finance-specific superiority claim.

Reproducibility notes
- Proceedings and DBLP metadata are strong.
- Preprint and proceedings versions should not be conflated casually if the final citation format matters.

Key literal quotes
- "We propose an alternative to Bayesian NNs that is simple to implement, readily parallelizable, requires very little hyperparameter tuning, and yields high quality predictive uncertainty estimates."
- "we demonstrate that our method produces well-calibrated uncertainty estimates which are as good or better than approximate Bayesian NNs."
- "We demonstrate the scalability of our method by evaluating predictive uncertainty estimates on ImageNet."

Final usefulness rating
- high
