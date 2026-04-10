Paper ID
- P06

Full citation
- Tadas Baltrusaitis, Chaitanya Ahuja, and Louis-Philippe Morency. 2019. Multimodal Machine Learning: A Survey and Taxonomy. IEEE Transactions on Pattern Analysis and Machine Intelligence, 41(2), 423-443. https://doi.org/10.1109/TPAMI.2018.2798607

Verification log
- Verification status: verified with an online-first versus issue-year distinction.
- Print issue metadata align on 2019, while some index sources reflect an earlier online publication date.
- The safest formal citation uses the journal issue year 2019.

Source 1
- Crossref DOI metadata
- https://api.crossref.org/works/10.1109/TPAMI.2018.2798607

Source 2
- arXiv version
- https://arxiv.org/abs/1705.09406

Source 3
- OpenAlex DOI record
- https://api.openalex.org/works/https://doi.org/10.1109/tpami.2018.2798607

Exact title
- Multimodal Machine Learning: A Survey and Taxonomy

Authors
- Tadas Baltrusaitis
- Chaitanya Ahuja
- Louis-Philippe Morency

Year
- 2019

Venue
- IEEE Transactions on Pattern Analysis and Machine Intelligence

DOI
- 10.1109/TPAMI.2018.2798607

Stable links
- https://doi.org/10.1109/TPAMI.2018.2798607
- https://arxiv.org/abs/1705.09406
- https://ieeexplore.ieee.org/document/8269806/

Research family
- Multimodal machine learning survey
- Fusion taxonomy

Why relevant to this project
- It gives the best broad conceptual vocabulary for separating representation, alignment, fusion, translation, and co-learning in a multimodal thesis.

Main problem addressed
- The need for a richer multimodal taxonomy than simple early-fusion versus late-fusion language.

Inputs / modalities
- Multiple modalities in general; not tied to finance.

Target design
- Not a single predictive task; this is a survey and taxonomy paper.

Model family
- Survey paper, not a single model.

Evaluation design
- Literature synthesis and taxonomy construction.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Does not itself address temporal leakage or financial benchmark integrity.
- Useful for architectural framing, not for direct empirical claims.

Pros
- Strongest broad multimodal taxonomy.
- Very useful for organizing architecture families without premature winner-picking.

Cons
- Not finance-specific.
- Does not directly answer forecasting or benchmark questions.

Repository-fit implications
- Strong support for treating representation, alignment, and fusion as separate layers in the repository design.

Modularity implications
- Strongly supports branch separation and explicit fusion-family comparisons.

What this paper supports
- Using a principled multimodal taxonomy instead of ad hoc fusion language.

What this paper does not support
- Any claim that a specific multimodal family should win in this repository.

Reproducibility notes
- arXiv version is open and stable.
- Journal metadata are solid.

Key literal quotes
- "We go beyond the typical early and late fusion categorization and identify broader challenges that are faced by multimodal machine learning, namely: representation, translation, alignment, fusion, and co-learning."
- "This new taxonomy will enable researchers to better understand the state of the field and identify directions for future research."

Final usefulness rating
- high
