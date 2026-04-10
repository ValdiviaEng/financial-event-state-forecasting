Paper ID
- P10

Full citation
- Tilmann Gneiting and Adrian E. Raftery. 2007. Strictly Proper Scoring Rules, Prediction, and Estimation. Journal of the American Statistical Association, 102(477), 359-378. https://doi.org/10.1198/016214506000001437

Verification log
- Verification status: fully verified.
- Title, authors, venue, year, pages, and DOI align across Crossref and OpenAlex; supporting title query confirms the same article.

Source 1
- Crossref DOI metadata
- https://api.crossref.org/works/10.1198/016214506000001437

Source 2
- OpenAlex DOI record
- https://api.openalex.org/works/https://doi.org/10.1198/016214506000001437

Source 3
- Crossref title query
- https://api.crossref.org/works?query.title=Strictly%20Proper%20Scoring%20Rules,%20Prediction,%20and%20Estimation&rows=3

Exact title
- Strictly Proper Scoring Rules, Prediction, and Estimation

Authors
- Tilmann Gneiting
- Adrian E. Raftery

Year
- 2007

Venue
- Journal of the American Statistical Association

DOI
- 10.1198/016214506000001437

Stable links
- https://doi.org/10.1198/016214506000001437
- http://www.tandfonline.com/doi/abs/10.1198/016214506000001437
- https://api.openalex.org/works/https://doi.org/10.1198/016214506000001437

Research family
- Proper scoring rules
- Probabilistic evaluation

Why relevant to this project
- It is the strongest foundational reference for how to evaluate probabilistic forecasts honestly if the thesis later adds uncertainty-aware outputs.

Main problem addressed
- How probabilistic forecasts should be scored and estimated using strictly proper scoring rules.

Inputs / modalities
- Predictive distributions and realized outcomes.

Target design
- Probabilistic prediction quality rather than a forecasting target family.

Model family
- Statistical framework, not a predictive architecture.

Evaluation design
- Theoretical treatment plus examples.

Metrics
- Logarithmic score
- spherical score
- pseudospherical score
- quadratic score
- continuous ranked probability score
- energy score
- interval score

Leakage / benchmark risks
- Proper scoring solves metric alignment, not data leakage or benchmark drift.

Pros
- Foundational and rigorous.
- Directly useful if probabilistic forecasting enters the thesis.

Cons
- Not useful for choosing the core deterministic architecture by itself.

Repository-fit implications
- Strong justification for exposing scoring-rule selection cleanly in the evaluation layer if uncertainty outputs are added.

Modularity implications
- Supports separation between prediction generation and evaluation/scoring modules.

What this paper supports
- Proper scoring rules for probabilistic outputs.
- Better calibration-aware evaluation.

What this paper does not support
- Any claim that proper scoring alone makes a benchmark clean.
- Any argument for using probabilistic outputs before the core deterministic benchmark is understood.

Reproducibility notes
- Metadata are strong.
- Full theorem and derivation details should come from the publisher version if used heavily in thesis text.

Key literal quotes
- "Scoring rules assess the quality of probabilistic forecasts, by assigning a numerical score based on the predictive distribution and on the event or value that materializes."
- "Proper scoring rules encourage the forecaster to make careful assessments and to be honest."

Final usefulness rating
- high
