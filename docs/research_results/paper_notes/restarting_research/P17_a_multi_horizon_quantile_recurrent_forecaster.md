Paper ID
- P17

Full citation
- Ruofeng Wen, Kari Torkkola, Balakrishnan Narayanaswamy, and Dhruv Madeka. 2017. A Multi-Horizon Quantile Recurrent Forecaster. arXiv:1711.11053.

Verification log
- Verification status: verified with venue ambiguity.
- arXiv, DataCite, and OpenAlex agree on title, authors, year, and arXiv DOI.
- The arXiv page comments mention NIPS 2017 Time Series Workshop publication context, but the safest citation remains the arXiv record unless the workshop record is verified separately.

Source 1
- arXiv abstract page
- https://arxiv.org/abs/1711.11053

Source 2
- DataCite DOI record
- https://api.datacite.org/dois/10.48550/arXiv.1711.11053

Source 3
- OpenAlex
- https://openalex.org/W2773625660

Exact title
- A Multi-Horizon Quantile Recurrent Forecaster

Authors
- Ruofeng Wen
- Kari Torkkola
- Balakrishnan Narayanaswamy
- Dhruv Madeka

Year
- 2017

Venue
- Uncertain, verify manually.
- Safest verified status in this pass: arXiv preprint.

DOI
- 10.48550/arXiv.1711.11053

Stable links
- https://arxiv.org/abs/1711.11053
- https://api.datacite.org/dois/10.48550/arXiv.1711.11053
- https://openalex.org/W2773625660

Research family
- Multi-horizon forecasting
- Probabilistic forecasting

Why relevant to this project
- Directly relevant for quantile-based multi-horizon forecasting if the thesis later explores uncertainty-aware outputs.

Main problem addressed
- Forecasting multiple future horizons with quantile outputs in sequence settings.

Inputs / modalities
- Time-series inputs.
- Exact covariate breakdown is Uncertain, verify manually.

Target design
- Multi-horizon quantile forecasts.

Model family
- Recurrent forecasting model with quantile outputs.

Evaluation design
- Multi-horizon forecasting experiments.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Known-future and horizon-handling logic must be correct in any implementation.
- The note does not establish exact temporal benchmark details from the verified sources.

Pros
- Very relevant for uncertainty-aware, multi-horizon task design.
- More directly tied to probabilistic forecasting than generic uncertainty references.

Cons
- Venue status is less stable than a fully verified archival publication in this pass.
- Not finance-specific.

Repository-fit implications
- Good later extension if the project adds quantile or interval outputs.

Modularity implications
- Supports adding probabilistic heads without redefining the entire data pipeline.

What this paper supports
- Quantile-based multi-horizon forecasting as a legitimate design family.

What this paper does not support
- Immediate move away from the current deterministic core benchmark.

Reproducibility notes
- arXiv record is stable.
- If thesis citation standards require an archival venue, verify the workshop record separately.

Key literal quotes
- Uncertain, verify manually.

Final usefulness rating
- medium
