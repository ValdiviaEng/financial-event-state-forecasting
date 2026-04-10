Paper ID
- P19

Full citation
- Tilmann Gneiting, Fadoua Balabdaoui, and Adrian E. Raftery. 2007. Probabilistic Forecasts, Calibration and Sharpness. Journal of the Royal Statistical Society Series B: Statistical Methodology, 69(2), 243-268. https://doi.org/10.1111/j.1467-9868.2007.00587.x

Verification log
- Verification status: verified with minor venue-string formatting differences only.

Source 1
- DOI landing page
- https://doi.org/10.1111/j.1467-9868.2007.00587.x

Source 2
- Crossref DOI metadata
- https://api.crossref.org/works/10.1111/j.1467-9868.2007.00587.x

Source 3
- OpenAlex search result
- https://api.openalex.org/works?search=Probabilistic%20Forecasts%20Calibration%20and%20Sharpness

Exact title
- Probabilistic Forecasts, Calibration and Sharpness

Authors
- Tilmann Gneiting
- Fadoua Balabdaoui
- Adrian E. Raftery

Year
- 2007

Venue
- Journal of the Royal Statistical Society Series B: Statistical Methodology

DOI
- 10.1111/j.1467-9868.2007.00587.x

Stable links
- https://doi.org/10.1111/j.1467-9868.2007.00587.x
- https://api.crossref.org/works/10.1111/j.1467-9868.2007.00587.x
- https://api.openalex.org/works?search=Probabilistic%20Forecasts%20Calibration%20and%20Sharpness

Research family
- Calibration
- Probabilistic forecasting

Why relevant to this project
- It is one of the strongest references for evaluating predictive distributions, especially if the thesis later adds uncertainty-aware outputs.

Main problem addressed
- The relationship between calibration and sharpness in probabilistic forecasting.

Inputs / modalities
- Predictive distributions and realized outcomes.

Target design
- Probabilistic forecast quality.

Model family
- Statistical evaluation framework.

Evaluation design
- Theoretical and methodological analysis.

Metrics
- Calibration and sharpness concepts are central.
- Exact full metric set in this note is Uncertain, verify manually.

Leakage / benchmark risks
- Helps evaluate probabilistic outputs honestly, but does not solve data leakage or benchmark drift.

Pros
- Strong conceptual basis for uncertainty-aware evaluation.
- Natural companion to proper scoring rules.

Cons
- Not a forecasting architecture paper.
- Only useful once probabilistic outputs actually exist.

Repository-fit implications
- Supports a future calibration and uncertainty-evaluation module.

Modularity implications
- Strong support for separating prediction generation from probability evaluation diagnostics.

What this paper supports
- Calibration and sharpness as central uncertainty-quality concepts.

What this paper does not support
- That uncertainty-aware modeling should replace the deterministic benchmark core now.

Reproducibility notes
- Metadata are stable.

Key literal quotes
- Uncertain, verify manually.

Final usefulness rating
- high
