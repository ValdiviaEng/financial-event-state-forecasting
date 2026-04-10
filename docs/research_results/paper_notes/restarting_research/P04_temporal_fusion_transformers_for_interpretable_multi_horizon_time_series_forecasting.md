Paper ID
- P04

Full citation
- Bryan Lim, Sercan O. Arik, Nicolas Loeff, and Tomas Pfister. 2021. Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. International Journal of Forecasting, 37(4), 1748-1764. https://doi.org/10.1016/j.ijforecast.2021.03.012

Verification log
- Verification status: fully verified.
- Title, authors, venue, DOI, and journal metadata align across publisher and DOI metadata.

Source 1
- Google Research publication page
- https://research.google/pubs/temporal-fusion-transformers-for-interpretable-multi-horizon-time-series-forecasting/

Source 2
- DOI landing page
- https://doi.org/10.1016/j.ijforecast.2021.03.012

Source 3
- Crossref query result for the exact bibliographic record
- https://api.crossref.org/works?query.bibliographic=%22Temporal%20Fusion%20Transformers%20for%20Interpretable%20Multi-horizon%20Time%20Series%20Forecasting%22&rows=1

Exact title
- Temporal Fusion Transformers for interpretable multi-horizon time series forecasting

Authors
- Bryan Lim
- Sercan O. Arik
- Nicolas Loeff
- Tomas Pfister

Year
- 2021

Venue
- International Journal of Forecasting

DOI
- 10.1016/j.ijforecast.2021.03.012

Stable links
- https://research.google/pubs/temporal-fusion-transformers-for-interpretable-multi-horizon-time-series-forecasting/
- https://doi.org/10.1016/j.ijforecast.2021.03.012
- https://api.crossref.org/works?query.bibliographic=%22Temporal%20Fusion%20Transformers%20for%20Interpretable%20Multi-horizon%20Time%20Series%20Forecasting%22&rows=1

Research family
- Multi-horizon forecasting
- Interpretable temporal modeling
- Attention and gating for time series

Why relevant to this project
- It is one of the strongest references for handling multi-horizon outputs with mixed covariates while preserving interpretability.

Main problem addressed
- Forecasting over multiple future horizons when static features, known-future inputs, and exogenous time series interact in complex ways.

Inputs / modalities
- Static covariates
- known future inputs
- exogenous time series

Target design
- Multi-horizon forecasting targets.

Model family
- Attention-based temporal architecture with gating and feature selection.

Evaluation design
- Multiple real-world datasets against existing baselines.
- Includes interpretability case studies.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Known-future inputs must be handled carefully.
- Temporal split design is crucial in forecasting settings, but exact protocol is not fully visible from the source snippets used here.

Pros
- Highly aligned with multi-horizon forecasting needs.
- Strong interpretability emphasis.
- Flexible handling of heterogeneous covariates.

Cons
- Heavier than the current repo’s first multimodal baseline.
- Not finance-specific.

Repository-fit implications
- Strong candidate family for later comparison once the current simpler multimodal system is benchmarked cleanly.

Modularity implications
- Encourages clear separation of static inputs, temporal features, selection mechanisms, and prediction heads.

What this paper supports
- Multi-horizon forecasting as a first-class problem.
- Gating and interpretability as valid design goals.

What this paper does not support
- That TFT should become the immediate default for this repo.
- That richer architecture should come before the core benchmark family is frozen.

Reproducibility notes
- Bibliographic metadata are solid.
- Full benchmark details should be extracted from the final journal text before implementation-specific claims are made.

Key literal quotes
- "Multi-horizon prediction problems often contain a complex mix of inputs -- including static covariates, known future inputs, and other exogenous time series -- without any prior information on how they interact with the target."
- "we introduce the Temporal Fusion Transformer (TFT) -- a novel attention-based architecture which combines high-performance multi-horizon forecasting with interpretable insights into temporal dynamics."
- "The TFT also utilizes specialized components for judicious selection of the relevant features"

Final usefulness rating
- high
