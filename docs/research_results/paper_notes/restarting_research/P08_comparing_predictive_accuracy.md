Paper ID
- P08

Full citation
- Francis X. Diebold and Roberto S. Mariano. 1995. Comparing Predictive Accuracy. Journal of Business & Economic Statistics, 13(3), 253-263. https://doi.org/10.1080/07350015.1995.10524599

Verification log
- Verification status: fully verified.
- Title, authors, venue, year, pages, and DOI align across RePEc services and Crossref.

Source 1
- IDEAS / RePEc record
- https://ideas.repec.org/a/bes/jnlbes/v13y1995i3p253-63.html

Source 2
- EconPapers record
- https://EconPapers.repec.org/RePEc:bes:jnlbes:v:13:y:1995:i:3:p:253-63

Source 3
- Crossref DOI metadata
- https://api.crossref.org/works/10.1080/07350015.1995.10524599

Exact title
- Comparing Predictive Accuracy

Authors
- Francis X. Diebold
- Roberto S. Mariano

Year
- 1995

Venue
- Journal of Business & Economic Statistics

DOI
- 10.1080/07350015.1995.10524599

Stable links
- https://doi.org/10.1080/07350015.1995.10524599
- https://ideas.repec.org/a/bes/jnlbes/v13y1995i3p253-63.html
- https://EconPapers.repec.org/RePEc:bes:jnlbes:v:13:y:1995:i:3:p:253-63

Research family
- Forecast comparison
- Econometric evaluation

Why relevant to this project
- It gives the classic statistical framework for comparing predictive accuracy between competing forecasting systems.

Main problem addressed
- Testing the null hypothesis that two competing forecasts are equally accurate.

Inputs / modalities
- Two forecast series and their realized forecast errors or loss differentials.

Target design
- No predictive target of its own; this is an evaluation test.

Model family
- Statistical test framework.

Evaluation design
- Proposes and studies tests of equal predictive accuracy.

Metrics
- Flexible loss functions.
- Exact metric family is determined by the user’s chosen loss.

Leakage / benchmark risks
- Useful only after the benchmark family itself is already clean.
- Does not protect against repeated tuning or multiple testing by itself.

Pros
- Canonical and widely recognized.
- Strong for final pairwise model comparison.

Cons
- Only answers relative forecast-accuracy questions.
- Does not address calibration, economic utility, or model-search overfitting alone.

Repository-fit implications
- Strong justification for a dedicated statistical-comparison layer after stored predictions are available.

Modularity implications
- Works best when evaluation is a separate module from model training, which fits the current repo well.

What this paper supports
- Formal comparison between competing predictive systems.

What this paper does not support
- Using noisy or repeatedly tuned benchmark families as if they were clean test objects.

Reproducibility notes
- Bibliographic metadata and abstract summary are stable through RePEc and Crossref.

Key literal quotes
- "The authors propose and evaluate explicit tests of the null hypothesis of no difference in the accuracy of two competing forecasts."
- "Asymptotic and exact finite sample tests are proposed, evaluated, and illustrated."

Final usefulness rating
- high
