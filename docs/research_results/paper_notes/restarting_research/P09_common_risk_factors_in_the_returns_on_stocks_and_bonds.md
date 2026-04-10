Paper ID
- P09

Full citation
- Eugene F. Fama and Kenneth R. French. 1993. Common risk factors in the returns on stocks and bonds. Journal of Financial Economics, 33(1), 3-56. https://doi.org/10.1016/0304-405X(93)90023-5

Verification log
- Verification status: fully verified.
- ScienceDirect, Crossref, and OpenAlex agree on title, authors, year, journal, issue, pages, and DOI.

Source 1
- ScienceDirect publisher page
- https://www.sciencedirect.com/science/article/pii/0304405X93900235

Source 2
- Crossref DOI metadata
- https://api.crossref.org/works/10.1016/0304-405X(93)90023-5

Source 3
- OpenAlex DOI record
- https://api.openalex.org/works/https://doi.org/10.1016/0304-405x(93)90023-5

Exact title
- Common risk factors in the returns on stocks and bonds

Authors
- Eugene F. Fama
- Kenneth R. French

Year
- 1993

Venue
- Journal of Financial Economics

DOI
- 10.1016/0304-405X(93)90023-5

Stable links
- https://doi.org/10.1016/0304-405X(93)90023-5
- https://www.sciencedirect.com/science/article/pii/0304405X93900235
- https://linkinghub.elsevier.com/retrieve/pii/0304405X93900235

Research family
- Target design
- Factor models
- Finance baseline theory

Why relevant to this project
- It is one of the foundational references supporting market-relative and factor-neutral target design.

Main problem addressed
- Identifying common risk factors that explain stock and bond returns.

Inputs / modalities
- Stock returns
- bond returns
- market factor
- size
- book-to-market equity
- maturity and default risk factors

Target design
- Explaining average returns and common return variation.

Model family
- Empirical factor model.

Evaluation design
- Explanatory empirical analysis of factor structure.

Metrics
- Explanatory power for return variation and average returns.
- Exact full estimation summaries are Uncertain, verify manually.

Leakage / benchmark risks
- This is not a direct temporal-leakage paper.
- It is useful for framing better targets and baselines, not for validating modern ML train/test procedures.

Pros
- Canonical finance baseline reference.
- Very useful for motivating excess-return or residual-target framing.

Cons
- Not a multimodal forecasting paper.
- Explanatory factor model, not a direct event-state predictor.

Repository-fit implications
- Strongly supports adding market-relative or factor-aware baseline comparisons before making multimodal claims.

Modularity implications
- Suggests keeping factor or benchmark construction modular from higher-capacity models.

What this paper supports
- Benchmark-relative and factor-aware target design.
- Strong, disciplined market baselines.

What this paper does not support
- That factor models are enough to represent event-state effects.
- That factor-neutrality should replace the core excess-return benchmark immediately.

Reproducibility notes
- Publisher and metadata sources are clean.
- Full factor-construction details would need the full paper or official factor-library documentation.

Key literal quotes
- "This paper identifies five common risk factors in the returns on stocks and bonds."
- "Most important, the five factors seem to explain average returns on stocks and bonds."

Final usefulness rating
- high
