Paper ID
- P12

Full citation
- Charles M.C. Lee and Bhaskaran Swaminathan. 2000. Price Momentum and Trading Volume. The Journal of Finance, 55(5), 2017-2069. https://doi.org/10.1111/0022-1082.00280

Verification log
- Verification status: fully verified.
- DOI, title, authors, year, journal, issue, and page range align across publisher metadata and RePEc.

Source 1
- DOI landing page
- https://doi.org/10.1111/0022-1082.00280

Source 2
- Crossref DOI metadata
- https://api.crossref.org/works/10.1111/0022-1082.00280

Source 3
- IDEAS / RePEc record
- https://ideas.repec.org/a/bla/jfinan/v55y2000i5p2017-2069.html

Exact title
- Price Momentum and Trading Volume

Authors
- Charles M.C. Lee
- Bhaskaran Swaminathan

Year
- 2000

Venue
- The Journal of Finance

DOI
- 10.1111/0022-1082.00280

Stable links
- https://doi.org/10.1111/0022-1082.00280
- https://ideas.repec.org/a/bla/jfinan/v55y2000i5p2017-2069.html

Research family
- Feature engineering
- Momentum and liquidity

Why relevant to this project
- It gives strong support for price-volume interactions as serious and interpretable market features, often stronger than derivative-like price transforms.

Main problem addressed
- Understanding how past trading volume helps explain momentum continuation and reversal.

Inputs / modalities
- Past trading volume
- turnover
- price momentum
- future returns
- earnings surprises

Target design
- Return continuation and reversal analysis.

Model family
- Empirical finance / econometric analysis.

Evaluation design
- Cross-sectional empirical study linking past volume and momentum to future behavior.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- The paper is not a modern leakage-control paper, but its logic assumes careful historical alignment of volume, returns, and announcement timing.

Pros
- Canonical support for volume-based feature families.
- Strong alternative to derivative centrality.
- Helps explain horizon dependence of momentum.

Cons
- Not a multimodal architecture paper.
- Not directly about textual information.

Repository-fit implications
- Strong support for giving the market branch a serious volume-surprise and liquidity component before spending attention on derivative-style transforms.

Modularity implications
- Volume-based features are easy to isolate as a separate feature family and benchmark cleanly.

What this paper supports
- Price-volume interaction features as meaningful market context.
- A stronger alternative to broad derivative-feature emphasis.

What this paper does not support
- That volume alone solves the forecasting problem.
- Any direct claim about news/event-state fusion.

Reproducibility notes
- Metadata are stable.
- Full portfolio-construction details should come from the article itself if reused in thesis exposition.

Key literal quotes
- "This study shows that past trading volume provides an important link between 'momentum' and 'value' strategies."
- "Past trading volume also predicts both the magnitude and persistence of price momentum."
- "Collectively, our findings show that past volume helps to reconcile intermediate-horizon 'underreaction' and long-horizon 'overreaction' effects."

Final usefulness rating
- high
