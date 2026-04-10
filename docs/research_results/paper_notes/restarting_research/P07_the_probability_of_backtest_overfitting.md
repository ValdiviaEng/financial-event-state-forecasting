Paper ID
- P07

Full citation
- David H. Bailey, Jonathan M. Borwein, Marcos Lopez de Prado, and Qiji Jim Zhu. 2017. The probability of backtest overfitting. The Journal of Computational Finance, 20(4), 39-69. https://doi.org/10.21314/JCF.2016.322

Verification log
- Verification status: verified with an online-first versus issue-date year discrepancy.
- Publisher page shows first-published 2016 and issue placement in 2017.
- For citation clarity, the journal issue year 2017 is used here.

Source 1
- Risk.net publisher page
- https://www.risk.net/journal-of-computational-finance/technical-paper/2471206/the-probability-of-backtest-overfitting

Source 2
- Crossref title query / DOI metadata
- https://api.crossref.org/works?query.title=The%20probability%20of%20backtest%20overfitting&rows=5

Source 3
- OpenAlex DOI record
- https://api.openalex.org/works/https://doi.org/10.21314/jcf.2016.322

Exact title
- The probability of backtest overfitting

Authors
- David H. Bailey
- Jonathan M. Borwein
- Marcos Lopez de Prado
- Qiji Jim Zhu

Year
- 2017

Venue
- The Journal of Computational Finance

DOI
- 10.21314/JCF.2016.322

Stable links
- https://doi.org/10.21314/JCF.2016.322
- https://www.risk.net/journal-of-computational-finance/technical-paper/2471206/the-probability-of-backtest-overfitting
- https://escholarship.org/uc/item/4w1110bb

Research family
- Financial ML evaluation
- Backtest overfitting
- Multiple-testing risk

Why relevant to this project
- It is one of the clearest warnings against exactly the kind of feature, target, and architecture search drift that this project is vulnerable to.

Main problem addressed
- Estimating how likely a selected backtest or strategy specification is overfit to historical data.

Inputs / modalities
- Historical strategy or model performance across in-sample and out-of-sample partitions.

Target design
- Probability of backtest overfitting rather than a forecasting target.

Model family
- Statistical evaluation framework using combinatorially symmetric cross-validation.

Evaluation design
- General framework plus illustrative examples.

Metrics
- Probability of backtest overfitting.
- Performance degradation and loss probability ideas are also discussed in the verified summary sources.

Leakage / benchmark risks
- This paper is itself about benchmark and selection risk.
- It is directly relevant whenever many candidate pipelines are compared on the same historical sample.

Pros
- Directly applicable to the thesis process itself.
- Gives a rigorous language for resisting feature and model lottery behavior.

Cons
- Not an architecture paper.
- Does not tell you what model to use; only how not to fool yourself in model search.

Repository-fit implications
- Strong case for keeping model-family exploration constrained and transparently logged.
- Suggests that later broad derivative or architecture grids should be treated with skepticism.

Modularity implications
- Supports separating candidate-generation from evaluation and comparison logic.

What this paper supports
- Overfitting-aware benchmark interpretation.
- Skepticism toward large search spaces and attractive late-stage tuning.

What this paper does not support
- Any claim that a strong single backtest is enough.
- Any argument that the repo should run broad tournaments before freezing benchmark families.

Reproducibility notes
- Metadata are well verified.
- Open-access route exists through eScholarship.

Key literal quotes
- "We propose a general framework to assess the probability of backtest overfitting (PBO)."
- "We show that CSCV produces reasonable estimates of PBO for several useful examples."

Final usefulness rating
- high
