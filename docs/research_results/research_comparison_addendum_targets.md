RESEARCH COMPARISON ADDENDUM: TARGET FAMILY COMPARISON

Purpose

This document extends `docs/research_results/research_comparison.md` without modifying it.

Its purpose is to compare target-design families in more detail than the master comparison file, using the same non-winner, profile-based methodology.

This file does not choose a final target.
It makes target families comparable on a broad, measurable basis.


SECTION 1. TARGET-SPECIFIC COMPARISON METHODOLOGY

Target families are special because they define the problem itself.

A target family does not merely change a metric.
It can change:
- what the model is allowed to learn
- how noisy the problem is
- how comparable old and new experiments remain
- what kinds of claims are academically defensible

For that reason, target families are scored using the master framework plus target-specific factors.

Scoring direction
- 1 = very unfavorable
- 2 = unfavorable
- 3 = mixed or conditional
- 4 = favorable
- 5 = very favorable

Target-specific measured factors

1. Alpha-isolation strength
- How well does the target isolate stock-specific information rather than broad market drift?

2. Economic interpretability
- How easy is it to explain what a good prediction means in economic terms?

3. Stationarity friendliness
- How stable is the target family relative to price-level alternatives?

4. Label-noise tolerance
- How resistant is the target to becoming dominated by micro-noise, benchmark noise, or reporting quirks?

5. Horizon compatibility
- How naturally does the family support 1d, 5d, 20d, and optional later horizons?

6. Benchmark comparability preservation
- If adopted, how easy is it to compare against prior or adjacent target families fairly?

7. Statistical evaluation clarity
- How easy is it to evaluate the target family with metrics that are both rigorous and interpretable?

8. Sample-efficiency friendliness
- Does the target family preserve enough usable rows and stable signal to be practical on moderate sample sizes?

9. Extension readiness
- How well does the target family support later ranking, uncertainty, or risk-oriented extensions without forcing redefinition of everything?

10. Repo-stage fit
- How well does it match the current repository’s architecture and current stage of development?

Grouped profile scores used here
- Scientific Value Score (SVS)
- Benchmark Integrity Score (BIS)
- Engineering Fit Score (EFS)
- Compatibility Score (COS)


SECTION 2. TARGET FAMILIES INCLUDED

This addendum compares the following target families:

- raw forward returns
- excess returns
- abnormal returns
- factor-neutral residual returns
- volatility-scaled returns
- directional sign targets
- thresholded directional targets
- ranking-first targets
- downside-event targets
- quantile / probabilistic targets


SECTION 3. DETAILED TARGET FAMILY PROFILES

Raw forward returns

Concept
- predict the stock’s own forward return over horizon h

Scores
- Alpha-isolation strength: 2
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 3
- Horizon compatibility: 5
- Benchmark comparability preservation: 5
- Statistical evaluation clarity: 5
- Sample-efficiency friendliness: 5
- Extension readiness: 4
- Repo-stage fit: 5
- SVS: 3.3
- BIS: 4.4
- EFS: 4.8
- COS: 4.7
- Confidence: 5

Comments
- strongest simple baseline family
- weak at separating stock-specific informational value from broad market movement
- can overstate learnability in trending regimes

Excess returns

Concept
- predict forward stock return minus forward benchmark return over the same horizon

Scores
- Alpha-isolation strength: 5
- Economic interpretability: 5
- Stationarity friendliness: 4
- Label-noise tolerance: 4
- Horizon compatibility: 5
- Benchmark comparability preservation: 4
- Statistical evaluation clarity: 4
- Sample-efficiency friendliness: 4
- Extension readiness: 5
- Repo-stage fit: 5
- SVS: 4.6
- BIS: 4.2
- EFS: 4.1
- COS: 4.3
- Confidence: 5

Comments
- strongest alignment with the project’s central question
- requires benchmark discipline
- likely the cleanest current main target family

Abnormal returns

Concept
- return adjusted relative to expected or benchmarked return under an event-study style framework

Scores
- Alpha-isolation strength: 5
- Economic interpretability: 5
- Stationarity friendliness: 4
- Label-noise tolerance: 3
- Horizon compatibility: 4
- Benchmark comparability preservation: 3
- Statistical evaluation clarity: 3
- Sample-efficiency friendliness: 3
- Extension readiness: 4
- Repo-stage fit: 3
- SVS: 4.2
- BIS: 3.2
- EFS: 3.0
- COS: 3.4
- Confidence: 4

Comments
- financially strong
- conceptually elegant
- can become benchmark-sensitive fast because the expected-return model itself becomes part of the target family

Factor-neutral residual returns

Concept
- residual forward outcome after neutralizing against market or factor exposures

Scores
- Alpha-isolation strength: 5
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 3
- Horizon compatibility: 4
- Benchmark comparability preservation: 3
- Statistical evaluation clarity: 3
- Sample-efficiency friendliness: 3
- Extension readiness: 5
- Repo-stage fit: 3
- SVS: 4.2
- BIS: 3.2
- EFS: 3.0
- COS: 3.5
- Confidence: 4

Comments
- strong later refinement
- creates additional dependence on factor data, residualization windows, and factor timing

Volatility-scaled returns

Concept
- return normalized by recent volatility or related scale estimate

Scores
- Alpha-isolation strength: 3
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 4
- Horizon compatibility: 4
- Benchmark comparability preservation: 3
- Statistical evaluation clarity: 4
- Sample-efficiency friendliness: 4
- Extension readiness: 4
- Repo-stage fit: 3
- SVS: 3.8
- BIS: 3.8
- EFS: 3.6
- COS: 3.8
- Confidence: 3

Comments
- plausible way to stabilize target scale across regimes
- not directly central to the current thesis question

Directional sign targets

Concept
- classify positive versus negative future movement

Scores
- Alpha-isolation strength: 2
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 3
- Horizon compatibility: 4
- Benchmark comparability preservation: 5
- Statistical evaluation clarity: 4
- Sample-efficiency friendliness: 5
- Extension readiness: 3
- Repo-stage fit: 4
- SVS: 3.1
- BIS: 4.5
- EFS: 4.6
- COS: 4.1
- Confidence: 4

Comments
- good secondary target family
- weak for magnitude-sensitive event-state claims

Thresholded directional targets

Concept
- classify only when future return exceeds a magnitude threshold

Scores
- Alpha-isolation strength: 3
- Economic interpretability: 3
- Stationarity friendliness: 3
- Label-noise tolerance: 4
- Horizon compatibility: 3
- Benchmark comparability preservation: 2
- Statistical evaluation clarity: 3
- Sample-efficiency friendliness: 2
- Extension readiness: 3
- Repo-stage fit: 2
- SVS: 3.1
- BIS: 2.8
- EFS: 2.6
- COS: 2.8
- Confidence: 3

Comments
- can be attractive if you want to focus on economically meaningful moves
- threshold choice itself becomes a benchmark-family decision
- easy to lose comparability and sample size quickly

Ranking-first targets

Concept
- predict cross-sectional ordering rather than exact numeric future returns

Scores
- Alpha-isolation strength: 4
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 4
- Horizon compatibility: 4
- Benchmark comparability preservation: 3
- Statistical evaluation clarity: 3
- Sample-efficiency friendliness: 3
- Extension readiness: 5
- Repo-stage fit: 3
- SVS: 4.0
- BIS: 3.3
- EFS: 3.1
- COS: 4.0
- Confidence: 4

Comments
- highly relevant for stock selection and ranking metrics
- changes the objective family enough that it should not silently replace regression-first core work

Downside-event targets

Concept
- classify whether a downside event occurs or model downside-sensitive outcomes

Scores
- Alpha-isolation strength: 3
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 3
- Horizon compatibility: 4
- Benchmark comparability preservation: 3
- Statistical evaluation clarity: 3
- Sample-efficiency friendliness: 3
- Extension readiness: 4
- Repo-stage fit: 3
- SVS: 3.6
- BIS: 3.2
- EFS: 3.1
- COS: 3.5

Comments
- important if the thesis later pivots partly toward risk
- currently secondary to the main event-state question

Quantile / probabilistic targets

Concept
- predict conditional quantiles or distributions instead of a single point estimate

Scores
- Alpha-isolation strength: 3
- Economic interpretability: 4
- Stationarity friendliness: 4
- Label-noise tolerance: 4
- Horizon compatibility: 5
- Benchmark comparability preservation: 3
- Statistical evaluation clarity: 3
- Sample-efficiency friendliness: 3
- Extension readiness: 5
- Repo-stage fit: 2
- SVS: 4.0
- BIS: 3.3
- EFS: 2.8
- COS: 4.0
- Confidence: 4

Comments
- strong later branch if uncertainty becomes important
- requires proper scoring rules and more careful communication


SECTION 4. TARGET FAMILY COMPARATIVE TABLE

Columns
- AIS = Alpha-isolation strength
- EI = Economic interpretability
- SF = Stationarity friendliness
- LNT = Label-noise tolerance
- HC = Horizon compatibility
- BCP = Benchmark comparability preservation
- SEC = Statistical evaluation clarity
- SEF = Sample-efficiency friendliness
- ER = Extension readiness
- RSF = Repo-stage fit

Target family | AIS | EI | SF | LNT | HC | BCP | SEC | SEF | ER | RSF | Comments
------------- | --- | -- | -- | --- | -- | --- | --- | --- | -- | --- | --------
Raw forward returns | 2 | 4 | 4 | 3 | 5 | 5 | 5 | 5 | 4 | 5 | Strong baseline, weak alpha isolation
Excess returns | 5 | 5 | 4 | 4 | 5 | 4 | 4 | 4 | 5 | 5 | Best current fit to the thesis question
Abnormal returns | 5 | 5 | 4 | 3 | 4 | 3 | 3 | 3 | 4 | 3 | Strong theory, heavier benchmark burden
Factor-neutral residual returns | 5 | 4 | 4 | 3 | 4 | 3 | 3 | 3 | 5 | 3 | Excellent later refinement, not simplest now
Volatility-scaled returns | 3 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 3 | Plausible stabilizing target variant
Directional sign | 2 | 4 | 4 | 3 | 4 | 5 | 4 | 5 | 3 | 4 | Useful secondary target family
Thresholded direction | 3 | 3 | 3 | 4 | 3 | 2 | 3 | 2 | 3 | 2 | Threshold choice adds benchmark drift risk
Ranking-first | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 5 | 3 | Strong later family, not silent replacement
Downside-event | 3 | 4 | 4 | 3 | 4 | 3 | 3 | 3 | 4 | 3 | Useful risk-side extension
Quantile / probabilistic | 3 | 4 | 4 | 4 | 5 | 3 | 3 | 3 | 5 | 2 | Strong later branch requiring extra evaluation care


SECTION 5. SIMILARITY NOTES FOR TARGETS

- Abnormal returns and factor-neutral residual returns are genuinely very close overall. If one is preferred later, that preference should come from practical factor-data and benchmark-construction details, not from pretending they are conceptually worlds apart.
- Raw returns and directional sign are also closer than they first appear in engineering simplicity, but they diverge strongly in scientific usefulness for the current thesis.
- Ranking-first and quantile/probabilistic targets are both strong future directions, but they answer different questions and should not be treated as substitutes.


SECTION 6. NON-DECISION SUMMARY FOR TARGETS

This addendum does not select a target.

What it does show clearly is:
- excess returns have the strongest combined fit to the current thesis identity and repository stage
- abnormal and factor-neutral residual targets are strong but more burdensome
- directional and downside families are useful secondaries, not clean replacements
- thresholded directional targets are relatively weak on comparability
- ranking-first and probabilistic targets are serious later families, not immediate defaults

The main value of this document is that these statements are now measurable and comparable rather than intuitive.
