RESEARCH COMPARISON METHODOLOGY AND COMPARATIVE MATRICES

Purpose

This document does not expand previous research narratives and does not replace any previous research file. It adds a comparison methodology layer.

Its purpose is to make the project’s major methods, techniques, and research directions comparable on a common basis without choosing favorites, selecting a final architecture, or collapsing the space into a recommendation memo.

The goal is not to decide what should win.
The goal is to define a fair and measurable way to compare:
- target families
- market feature families
- event representation families
- multimodal fusion families
- model families
- evaluation families
- extension families

This document is specifically designed for a repository that is already beyond a pure concept stage and has entered late foundation / early experimentation. The comparison framework therefore has to respect both:
- theoretical breadth
- repository-stage reality

No prior research document was edited to produce this file.


SECTION 1. CURRENT DEVELOPMENT STAGE AND WHY IT CHANGES HOW COMPARISON MUST BE DONE

Established from repository evidence
- the active root is primarily a governance constitution and fresh-start shell
- the real first-pass implementation evidence remains in the archived legacy snapshot
- the architecture overview states that the repository already has implemented:
  - provider clients
  - raw/interim/final separation
  - split handling
  - market features
  - event-state construction
  - final modeling panels
  - market-only baselines
  - a first multimodal model
  - evaluation and ablation tooling
- the implementation roadmap states that the repository is strong enough for pilot experiments, debugging, and methodological validation, but that the main remaining priorities are:
  - documentation hardening
  - reporting polish
  - selected multimodal extensions
  - manual external verification

Implication

This means comparison cannot be done as if every method is equally feasible, equally mature, or equally benchmarkable right now.

The framework therefore must measure at least two different things at once:
1. intrinsic scientific or methodological attractiveness
2. practical compatibility with the current repository stage

This is essential because some directions are strong in theory but weak in current repo fit, while others are modest in theory but very strong as immediate benchmark-clean comparators.


SECTION 2. GOVERNANCE CONSTRAINTS THAT THIS COMPARISON MUST RESPECT

This comparison methodology is constrained by AgentRules.md and related governance files.

Established from repository evidence
- theory must outrank design and code
- benchmark methodology changes are not minor; they require explicit review of comparability
- benchmark success claims require evidence
- modularity is mandatory
- contradictions must not be smoothed over
- the immutable task contract must not drift silently

Implications for this document
- this document must not produce a hidden overall winner
- this document must not convert descriptive scores into a recommendation ranking
- this document must keep benchmark comparability as a first-class measured attribute
- this document must score “repo-stage fit” separately from intrinsic scientific strength
- this document must treat broad feature or architecture grids as potentially benchmark-dangerous, not just expressive


SECTION 3. COMPARISON METHODOLOGY

3.1 Core principle

Every compared method or technique is profiled, not crowned.

The framework uses:
- explicit measurable attributes
- a consistent scoring direction
- explicit confidence levels
- explicit comments for unique traits, hardware needs, incompatibilities, or hidden costs

3.2 Scoring scale

All attribute scores use the same direction:

1 = very unfavorable
2 = unfavorable
3 = mixed / conditional / moderate
4 = favorable
5 = very favorable

Important rule:
For cost, burden, or risk-related dimensions, the scoring is inverted so that higher still means better.

Examples:
- Compute efficiency = 5 means low compute requirement
- Leakage safety = 5 means low leakage risk
- Added complexity burden = 5 means low added complexity

This uniform direction is required so different columns can be compared without confusion.

3.3 Confidence scale

Each method family also gets a confidence score.

1 = highly speculative, weak evidence base
2 = plausible but thin evidence or unclear repo fit
3 = moderate evidence, but still mixed or partially verified
4 = strong evidence from literature or repository, with manageable ambiguity
5 = strong support from both repository evidence and external literature, low ambiguity

3.4 Similarity rule

To avoid fake distinctions:
- if two methods differ by 0.3 or less on a group score, treat them as effectively similar on that dimension
- if they differ by 0.4 to 0.7, treat the difference as moderate
- if they differ by 0.8 or more, treat the difference as materially meaningful

If two compared methods are genuinely very close overall, this document will say so directly instead of inventing a hierarchy.


SECTION 4. MEASURED ATTRIBUTES

This framework uses 22 measured attributes.

Group A. Scientific and explanatory value

1. Predictive upside potential
- Question: how plausible is it that this family can add real predictive signal if implemented well?

2. Theoretical clarity
- Question: how cleanly defined and conceptually defensible is the family?

3. Explainability of results
- Question: how easy is it to trace from method choice to observed outcome and explain why it helped or failed?

4. Literature maturity
- Question: how established is this family in the literature, with enough references to study it seriously?

Group B. Benchmark integrity and result-comparison quality

5. Benchmark comparability preservation
- Question: if this family is added, how easy is it to keep results comparable to prior runs?

6. Ease of comparison of results
- Question: how easy is it to compare its outputs against other methods cleanly and interpretably?

7. Leakage safety
- Question: how naturally resistant is the family to timing leakage, look-ahead risk, or hidden information contamination?

8. Reproducibility
- Question: how easy is it to reproduce the method’s outputs from frozen artifacts and clear configs?

9. Branch separability
- Question: can this family be isolated in one branch without silently changing upstream logic?

10. Ablation cleanliness
- Question: can this family be removed or swapped without causing ambiguous benchmark changes?

11. Evaluation burden friendliness
- Question: how easy is it to evaluate this family without inventing a large new metric or testing regime?

Group C. Engineering and operational fit

12. Accumulative compatibility
- Question: how easily can this family be implemented on top of other already-existing families without forcing redesign?

13. Implementation feasibility
- Question: how feasible is implementation in the current repository and project stage?

14. Added complexity burden
- Question: how low is the additional conceptual and implementation complexity it introduces?

15. Compute efficiency
- Question: how low are the compute requirements relative to the likely gain?

16. Data efficiency
- Question: how little extra data scale or special data sourcing does the family require?

17. Maintenance simplicity
- Question: how easy is it to maintain once added?

18. Debugging ease
- Question: how easy is it to localize failures and understand why the family misbehaved?

19. Scalability
- Question: how well can it scale from pilot subsets to larger universes or longer windows?

20. Repo-stage fit
- Question: how well does this family match the current repo stage rather than an imagined future repo?

21. Provider resilience
- Question: how independent is the family from fragile external provider behavior or missing special feeds?

22. Hyperparameter robustness
- Question: how unlikely is it to become a tuning lottery?


SECTION 5. GROUP SCORES AND HOW TO INTERPRET THEM

To keep the final comparative table readable, this document uses four grouped scores derived from the detailed attributes above.

Scientific Value Score (SVS)
- mean of:
  - Predictive upside potential
  - Theoretical clarity
  - Explainability of results
  - Literature maturity

Benchmark Integrity Score (BIS)
- mean of:
  - Benchmark comparability preservation
  - Ease of comparison of results
  - Leakage safety
  - Reproducibility
  - Branch separability
  - Ablation cleanliness
  - Evaluation burden friendliness

Engineering Fit Score (EFS)
- mean of:
  - Implementation feasibility
  - Added complexity burden
  - Compute efficiency
  - Data efficiency
  - Maintenance simplicity
  - Debugging ease
  - Repo-stage fit

Compatibility Score (COS)
- mean of:
  - Accumulative compatibility
  - Scalability
  - Provider resilience
  - Hyperparameter robustness

Important restriction
- There is intentionally no single overall score.
- A single overall score would push this document toward hidden winner-picking.
- The grouped profile is the correct output for a non-decision comparison framework.


SECTION 6. EVIDENCE STANDARDS FOR SCORING

Scores in this document are based on a combination of:
- repository evidence
- current architecture and implementation roadmap
- evaluation protocol and testing structure
- the verified paper-note set
- the broader restart investigations already present in `docs/research_results/`

When evidence is uneven:
- the score remains moderate rather than inflated
- comments explicitly mention uncertainty

When a method is strong in literature but weak in current repo fit:
- SVS may be high
- EFS and COS may be lower

When a method is modest in theory but very clean and easy to benchmark:
- BIS and EFS may be high even if SVS is not extreme


SECTION 7. TARGET FAMILY COMPARISON MATRIX

Compared families
- raw forward returns
- excess returns
- abnormal / factor-neutral residual returns
- directional classification targets
- ranking-first targets
- downside / risk-sensitive targets
- probabilistic / quantile targets

Target family profiles

Raw forward returns
- SVS: 3.3
- BIS: 4.3
- EFS: 4.7
- COS: 4.6
- Confidence: 5
- Comments:
  - very easy baseline
  - strong comparability
  - weaker fit to the project’s actual “incremental informational value” question because market drift remains inside the target

Excess returns
- SVS: 4.5
- BIS: 4.2
- EFS: 4.1
- COS: 4.1
- Confidence: 5
- Comments:
  - strongest alignment with current thesis framing
  - requires frozen benchmark discipline
  - already strongly supported by repo and design docs

Abnormal / factor-neutral residual returns
- SVS: 4.6
- BIS: 3.5
- EFS: 3.0
- COS: 3.1
- Confidence: 4
- Comments:
  - theoretically strong
  - adds factor-estimation and benchmark-definition burden
  - better treated as later extension or refinement rather than first serious target family

Directional classification targets
- SVS: 3.0
- BIS: 4.4
- EFS: 4.6
- COS: 4.4
- Confidence: 4
- Comments:
  - simple and easy to interpret
  - useful as secondary view
  - weaker as sole thesis target because it discards magnitude structure

Ranking-first targets
- SVS: 4.1
- BIS: 3.6
- EFS: 3.6
- COS: 3.5
- Confidence: 4
- Comments:
  - very relevant cross-sectionally
  - more benchmark-sensitive
  - better as strong next-step or secondary objective than immediate core target replacement

Downside / risk-sensitive targets
- SVS: 3.8
- BIS: 3.7
- EFS: 3.5
- COS: 3.3
- Confidence: 3
- Comments:
  - meaningful for risk language
  - secondary to the central event-state question

Probabilistic / quantile targets
- SVS: 4.0
- BIS: 3.4
- EFS: 3.0
- COS: 3.1
- Confidence: 4
- Comments:
  - strong later extension family with serious methodological support
  - should not displace the deterministic core benchmark too early

Similarity notes
- Raw forward returns and directional classification are similar in Engineering Fit, but not in Scientific Value.
- Excess returns and abnormal / factor-neutral targets are similar in Scientific Value, but materially different in Engineering Fit and Benchmark Integrity.
- Ranking-first and probabilistic targets are both strong future directions, but for different reasons and with different burdens.


SECTION 8. MARKET FEATURE FAMILY COMPARISON MATRIX

Compared families
- returns / log returns
- momentum / reversal
- volatility / range
- volume / liquidity interactions
- benchmark-relative / residualized features
- regime-context features
- technical-indicator bundles
- derivative-like transforms

Returns / log returns
- SVS: 4.0
- BIS: 4.8
- EFS: 4.9
- COS: 4.8
- Confidence: 5
- Comments:
  - essential normalized baseline primitives
  - very strong comparability and debugging properties

Momentum / reversal
- SVS: 4.3
- BIS: 4.5
- EFS: 4.6
- COS: 4.5
- Confidence: 5
- Comments:
  - likely stronger than most derivative-like proposals
  - easy to add cleanly

Volatility / range
- SVS: 4.2
- BIS: 4.6
- EFS: 4.5
- COS: 4.4
- Confidence: 5
- Comments:
  - strong daily-bar information content
  - especially good alternative to close-only derivative families

Volume / liquidity interactions
- SVS: 4.4
- BIS: 4.4
- EFS: 4.2
- COS: 4.1
- Confidence: 4
- Comments:
  - highly relevant to information absorption and attention
  - often more event-relevant than abstract curvature transforms

Benchmark-relative / residualized features
- SVS: 4.5
- BIS: 3.9
- EFS: 3.6
- COS: 3.7
- Confidence: 4
- Comments:
  - theoretically strong
  - requires benchmark/factor discipline
  - aligns directly with the project’s core target logic

Regime-context features
- SVS: 4.0
- BIS: 3.8
- EFS: 3.5
- COS: 3.6
- Confidence: 4
- Comments:
  - likely useful as second-wave context
  - can become oversegmentation if pushed too early

Technical-indicator bundles
- SVS: 3.1
- BIS: 2.9
- EFS: 3.8
- COS: 2.8
- Confidence: 4
- Comments:
  - technically easy
  - scientifically risky because of redundancy and data-snooping style proliferation

Derivative-like transforms
- SVS: 2.8
- BIS: 2.6
- EFS: 3.7
- COS: 2.7
- Confidence: 4
- Comments:
  - technically easy to add
  - high redundancy risk
  - many versions are dominated by momentum, slope, volatility, and range families
  - broad second-order families are especially risky

Similarity notes
- Returns/log returns, momentum/reversal, and volatility/range are all strong and relatively similar on benchmark cleanliness.
- Technical bundles and derivative-like transforms are similar in being easy to generate but weak in benchmark discipline.
- Volume/liquidity and benchmark-relative features are both strong, but benchmark-relative features are a bit more burdensome operationally.


SECTION 9. EVENT REPRESENTATION FAMILY COMPARISON MATRIX

Compared families
- sentiment-only representation
- pooled dense embeddings
- finance-domain frozen embeddings
- event-state scalar family
- event-type tagging
- temporal article sequence encoders
- graph / entity-event representations
- static company metadata
- dynamic company profile text

Sentiment-only representation
- SVS: 2.8
- BIS: 4.3
- EFS: 4.7
- COS: 4.6
- Confidence: 4
- Comments:
  - cheap and interpretable
  - too reductive for the project’s event-state ambitions

Pooled dense embeddings
- SVS: 4.2
- BIS: 4.4
- EFS: 4.4
- COS: 4.3
- Confidence: 5
- Comments:
  - strongest current default text-state family for this repo stage
  - balances semantics with reproducibility

Finance-domain frozen embeddings
- SVS: 4.4
- BIS: 4.1
- EFS: 3.8
- COS: 3.9
- Confidence: 4
- Comments:
  - likely stronger semantically than generic dense embeddings
  - slightly higher integration and benchmark burden

Event-state scalar family
- SVS: 4.3
- BIS: 4.5
- EFS: 4.2
- COS: 4.5
- Confidence: 4
- Comments:
  - very strong for interpretability
  - directly aligned with event-state theory
  - especially useful for subgroup explanations

Event-type tagging
- SVS: 3.8
- BIS: 4.0
- EFS: 3.7
- COS: 3.9
- Confidence: 3
- Comments:
  - potentially interpretable
  - depends on reliable tagging quality

Temporal article sequence encoders
- SVS: 4.1
- BIS: 3.1
- EFS: 2.8
- COS: 3.0
- Confidence: 3
- Comments:
  - richer sequence semantics
  - higher complexity and harder clean comparison than pooled state

Graph / entity-event representations
- SVS: 4.0
- BIS: 2.8
- EFS: 2.3
- COS: 2.5
- Confidence: 3
- Comments:
  - conceptually rich
  - high design and benchmark burden
  - late extension only under current maturity

Static company metadata
- SVS: 3.3
- BIS: 4.4
- EFS: 4.2
- COS: 4.6
- Confidence: 4
- Comments:
  - modest likely upside
  - low leakage if frozen
  - strong extension candidate

Dynamic company profile text
- SVS: 3.9
- BIS: 2.1
- EFS: 2.0
- COS: 2.2
- Confidence: 2
- Comments:
  - attractive on paper
  - very high point-in-time and leakage burden
  - currently poor fit to the repo stage

Similarity notes
- Pooled dense embeddings and event-state scalar enrichments are similarly strong, but for different reasons: one for semantic power, one for interpretability.
- Static company metadata and sentiment-only text are similar in simplicity, but static metadata is cleaner as an extension because it is less reductive and less semantically brittle.


SECTION 10. FUSION FAMILY COMPARISON MATRIX

Compared families
- early concatenation
- late fusion
- gated fusion
- residual fusion
- intermediate learned interaction
- cross-attention fusion
- expert-routing / MoE fusion

Early concatenation
- SVS: 3.0
- BIS: 4.5
- EFS: 4.8
- COS: 4.7
- Confidence: 4
- Comments:
  - simple comparator
  - useful baseline but limited expressiveness

Late fusion
- SVS: 4.1
- BIS: 4.8
- EFS: 4.6
- COS: 4.7
- Confidence: 5
- Comments:
  - strongest benchmark-clean multimodal family under current repo stage

Gated fusion
- SVS: 4.4
- BIS: 4.4
- EFS: 4.1
- COS: 4.2
- Confidence: 5
- Comments:
  - especially aligned with conditional usefulness of text
  - slightly more complex than plain late fusion but still very repo-compatible

Residual fusion
- SVS: 4.5
- BIS: 4.3
- EFS: 3.9
- COS: 4.0
- Confidence: 4
- Comments:
  - conceptually excellent for “increment beyond market baseline” framing
  - not necessarily easier than gated fusion to implement cleanly

Intermediate learned interaction
- SVS: 4.0
- BIS: 3.4
- EFS: 3.1
- COS: 3.3
- Confidence: 3
- Comments:
  - expressive but harder to compare cleanly

Cross-attention fusion
- SVS: 4.2
- BIS: 3.0
- EFS: 2.7
- COS: 2.9
- Confidence: 4
- Comments:
  - strong literature support outside finance-specific baseline work
  - likely too much too early for this repo’s current core benchmark need

Expert-routing / MoE fusion
- SVS: 3.9
- BIS: 2.2
- EFS: 1.9
- COS: 2.0
- Confidence: 3
- Comments:
  - theoretically interesting
  - very weak current benchmark cleanliness and repo-stage fit

Similarity notes
- Late fusion and gated fusion are very close overall; the difference should not be exaggerated unless experiments show otherwise.
- Gated and residual fusion are also close scientifically, but residual fusion is a bit more abstract conceptually for implementation and debugging.


SECTION 11. MODEL FAMILY COMPARISON MATRIX

Compared families
- linear regularized baselines
- tree-based tabular models
- market-only MLP
- simple multimodal gated regressor
- multi-task multi-horizon model
- ranking-first model
- uncertainty-aware model
- graph-aware model
- Mixture-of-Experts model

Linear regularized baselines
- SVS: 3.5
- BIS: 4.9
- EFS: 4.9
- COS: 4.8
- Confidence: 5
- Comments:
  - mandatory discipline floor
  - not sufficient alone, but essential for clean comparison

Tree-based tabular models
- SVS: 4.0
- BIS: 4.2
- EFS: 3.8
- COS: 3.9
- Confidence: 4
- Comments:
  - strong possible addition if introduced carefully
  - not yet central in the current repo, but very relevant as a tabular comparator

Market-only MLP
- SVS: 4.0
- BIS: 4.3
- EFS: 4.3
- COS: 4.2
- Confidence: 5
- Comments:
  - strong nonlinear comparator already aligned with repo structure

Simple multimodal gated regressor
- SVS: 4.4
- BIS: 4.4
- EFS: 4.0
- COS: 4.1
- Confidence: 5
- Comments:
  - strongest current main multimodal family under repo maturity

Multi-task multi-horizon model
- SVS: 4.2
- BIS: 3.9
- EFS: 3.7
- COS: 4.0
- Confidence: 4
- Comments:
  - very relevant later comparison family
  - should not replace the simpler core benchmark before it is understood

Ranking-first model
- SVS: 4.1
- BIS: 3.5
- EFS: 3.2
- COS: 3.4
- Confidence: 4
- Comments:
  - strong alternative objective family
  - more benchmark-sensitive than plain regression-first models

Uncertainty-aware model
- SVS: 4.0
- BIS: 3.2
- EFS: 2.9
- COS: 3.2
- Confidence: 4
- Comments:
  - scientifically valuable later
  - not the first question this project needs to answer

Graph-aware model
- SVS: 4.0
- BIS: 2.6
- EFS: 2.1
- COS: 2.4
- Confidence: 3
- Comments:
  - plausible later extension
  - high design burden and point-in-time relation risk

Mixture-of-Experts model
- SVS: 3.7
- BIS: 2.1
- EFS: 1.8
- COS: 2.0
- Confidence: 3
- Comments:
  - strong complexity with uncertain near-term payoff
  - poor current repo-stage fit

Similarity notes
- Tree-based tabular models and market-only MLP are relatively close overall, with trees somewhat cleaner interpretively and MLPs somewhat closer to the current neural stack.
- Graph and MoE models are similar in being conceptually interesting but weak in current benchmark cleanliness.


SECTION 12. EVALUATION FAMILY COMPARISON MATRIX

Compared families
- single chronological holdout
- walk-forward
- purged / embargoed walk-forward
- final lockbox holdout
- paired forecast comparison tests
- probabilistic scoring and calibration suite
- backtest-overfitting diagnostics

Single chronological holdout
- SVS: 2.8
- BIS: 2.9
- EFS: 4.8
- COS: 4.8
- Confidence: 5
- Comments:
  - easy but too fragile as the sole benchmark family

Walk-forward
- SVS: 4.3
- BIS: 4.3
- EFS: 4.1
- COS: 4.4
- Confidence: 5
- Comments:
  - core time-aware evaluation family

Purged / embargoed walk-forward
- SVS: 4.7
- BIS: 4.9
- EFS: 3.8
- COS: 4.0
- Confidence: 5
- Comments:
  - strongest current benchmark family for multi-horizon finance forecasting
  - slightly higher implementation burden, but worth it

Final lockbox holdout
- SVS: 4.0
- BIS: 4.5
- EFS: 3.7
- COS: 4.3
- Confidence: 4
- Comments:
  - highly valuable as a final reporting layer
  - not enough alone for model development

Paired forecast comparison tests
- SVS: 3.9
- BIS: 4.4
- EFS: 3.5
- COS: 4.1
- Confidence: 5
- Comments:
  - very useful after saved predictions are stable
  - secondary to clean split logic itself

Probabilistic scoring and calibration suite
- SVS: 4.0
- BIS: 4.1
- EFS: 3.1
- COS: 3.4
- Confidence: 4
- Comments:
  - only relevant once probabilistic outputs are added

Backtest-overfitting diagnostics
- SVS: 4.2
- BIS: 4.6
- EFS: 3.0
- COS: 3.6
- Confidence: 4
- Comments:
  - extremely valuable if the search space expands
  - more a governance and analysis layer than an everyday baseline metric family

Similarity notes
- Walk-forward and final lockbox are complementary, not competing.
- Walk-forward and purged walk-forward are similar in spirit, but the purge/embargo version is materially stronger for overlapping-label settings.


SECTION 13. EXTENSION FAMILY COMPARISON MATRIX

Compared families
- static company metadata branch
- dynamic company profile branch
- graph / relation-aware branch
- regime-aware branch
- uncertainty-aware output branch
- derivative-family appendix branch
- stronger frozen encoder branch
- end-to-end text fine-tuning branch

Static company metadata branch
- SVS: 3.4
- BIS: 4.3
- EFS: 4.2
- COS: 4.6
- Confidence: 4
- Comments:
  - strong low-risk extension
  - likely modest predictive upside

Dynamic company profile branch
- SVS: 3.9
- BIS: 2.0
- EFS: 1.9
- COS: 2.1
- Confidence: 2
- Comments:
  - attractive but timing-unsafe unless carefully engineered
  - poor current-stage fit

Graph / relation-aware branch
- SVS: 4.0
- BIS: 2.6
- EFS: 2.2
- COS: 2.5
- Confidence: 3
- Comments:
  - legitimate later direction
  - high relation-construction and benchmark burden

Regime-aware branch
- SVS: 4.1
- BIS: 3.3
- EFS: 3.1
- COS: 3.3
- Confidence: 4
- Comments:
  - likely useful for conditional analysis and later modeling
  - should start with simple contextual features, not heavy switching architectures

Uncertainty-aware output branch
- SVS: 4.0
- BIS: 3.2
- EFS: 2.9
- COS: 3.1
- Confidence: 4
- Comments:
  - useful later
  - secondary to deterministic core benchmark

Derivative-family appendix branch
- SVS: 2.9
- BIS: 2.8
- EFS: 3.6
- COS: 3.0
- Confidence: 4
- Comments:
  - acceptable narrow appendix branch
  - should remain narrow, comparative, and late

Stronger frozen encoder branch
- SVS: 4.2
- BIS: 3.9
- EFS: 3.6
- COS: 3.8
- Confidence: 4
- Comments:
  - strong later extension with better ROI than end-to-end fine-tuning

End-to-end text fine-tuning branch
- SVS: 4.3
- BIS: 2.4
- EFS: 1.8
- COS: 2.0
- Confidence: 3
- Comments:
  - high theoretical upside
  - very poor current-stage fit and benchmark cleanliness

Similarity notes
- Static metadata and stronger frozen encoders are both solid extension families, but static metadata is cleaner while stronger frozen encoders may have more upside.
- Derivative appendix and regime-aware branch are both acceptable later, but for different reasons; regime-aware work is more conceptually central than derivative work.


SECTION 14. MEASUREMENT METHODOLOGY SUMMARY BY CATEGORY

The previous sections already applied the framework. This section states the meta-interpretation clearly.

Target families are mainly judged by:
- theoretical clarity
- benchmark comparability preservation
- leakage safety
- repo-stage fit

Feature families are mainly judged by:
- predictive upside potential
- explainability of results
- redundancy risk as reflected in benchmark integrity scores
- accumulative compatibility with the conservative market branch

Event representations are mainly judged by:
- semantic strength
- explainability
- timing safety
- modularity

Fusion families are mainly judged by:
- benchmark cleanliness
- branch separability
- added complexity burden
- conditional-signal modeling value

Model families are mainly judged by:
- scientific upside
- benchmark burden
- implementation feasibility
- repo-stage fit

Evaluation families are mainly judged by:
- benchmark integrity
- ease of comparison of results
- leakage safety

Extension families are mainly judged by:
- whether they improve understanding beyond the core benchmark
- how much they threaten comparability
- whether they are accumulatively compatible or architecture-breaking


SECTION 15. FINAL CONDENSED COMPARATIVE TABLE

Interpretation rule for this final table
- it is a condensed profile table
- it is not a winner ranking
- if two rows are close, read them as close

Columns
- SVS = Scientific Value Score
- BIS = Benchmark Integrity Score
- EFS = Engineering Fit Score
- COS = Compatibility Score
- Conf = Confidence

Category | Method / Family | SVS | BIS | EFS | COS | Conf | Comments
-------- | --------------- | --- | --- | --- | --- | ---- | --------
Target | Raw forward returns | 3.3 | 4.3 | 4.7 | 4.6 | 5 | Strong baseline, weaker incremental-information alignment
Target | Excess returns | 4.5 | 4.2 | 4.1 | 4.1 | 5 | Strongest alignment with current thesis identity
Target | Abnormal/factor-neutral | 4.6 | 3.5 | 3.0 | 3.1 | 4 | Strong theory, heavier factor-data burden
Target | Directional classification | 3.0 | 4.4 | 4.6 | 4.4 | 4 | Good secondary view, weak sole target
Target | Ranking-first | 4.1 | 3.6 | 3.6 | 3.5 | 4 | Strong cross-sectional family, more benchmark-sensitive
Target | Probabilistic / quantile | 4.0 | 3.4 | 3.0 | 3.1 | 4 | Good later extension
Feature | Returns / log returns | 4.0 | 4.8 | 4.9 | 4.8 | 5 | Non-negotiable normalized primitives
Feature | Momentum / reversal | 4.3 | 4.5 | 4.6 | 4.5 | 5 | Strong and likely better than broad derivatives
Feature | Volatility / range | 4.2 | 4.6 | 4.5 | 4.4 | 5 | Strong daily-bar state family
Feature | Volume / liquidity | 4.4 | 4.4 | 4.2 | 4.1 | 4 | Especially relevant for information absorption
Feature | Benchmark-relative / residualized | 4.5 | 3.9 | 3.6 | 3.7 | 4 | Strong alignment with alpha-style framing
Feature | Regime-context | 4.0 | 3.8 | 3.5 | 3.6 | 4 | Good conditional layer, not early main branch
Feature | Technical indicator bundles | 3.1 | 2.9 | 3.8 | 2.8 | 4 | Easy but benchmark-dangerous if widened
Feature | Derivative-like transforms | 2.8 | 2.6 | 3.7 | 2.7 | 4 | Narrow later test only; broad versions risky
Representation | Sentiment-only | 2.8 | 4.3 | 4.7 | 4.6 | 4 | Good weak-text comparator, too reductive as core
Representation | Pooled dense embeddings | 4.2 | 4.4 | 4.4 | 4.3 | 5 | Strong current default family
Representation | Finance-domain frozen embeddings | 4.4 | 4.1 | 3.8 | 3.9 | 4 | Strong later upgrade over generic dense embeddings
Representation | Event-state scalar family | 4.3 | 4.5 | 4.2 | 4.5 | 4 | Very interpretable and thesis-aligned
Representation | Temporal article sequence | 4.1 | 3.1 | 2.8 | 3.0 | 3 | Richer, but heavier and harder to compare
Representation | Graph/event-entity representation | 4.0 | 2.8 | 2.3 | 2.5 | 3 | Legitimate later extension, high burden
Representation | Static company metadata | 3.3 | 4.4 | 4.2 | 4.6 | 4 | Low-risk extension
Representation | Dynamic company profile text | 3.9 | 2.1 | 2.0 | 2.2 | 2 | Attractive but highly leakage-sensitive
Fusion | Early concatenation | 3.0 | 4.5 | 4.8 | 4.7 | 4 | Simple comparator only
Fusion | Late fusion | 4.1 | 4.8 | 4.6 | 4.7 | 5 | Very strong benchmark-clean default family
Fusion | Gated fusion | 4.4 | 4.4 | 4.1 | 4.2 | 5 | Very aligned with conditional text usefulness
Fusion | Residual fusion | 4.5 | 4.3 | 3.9 | 4.0 | 4 | Conceptually elegant for incremental-value framing
Fusion | Intermediate interaction | 4.0 | 3.4 | 3.1 | 3.3 | 3 | Richer but benchmark-heavier
Fusion | Cross-attention | 4.2 | 3.0 | 2.7 | 2.9 | 4 | Strong literature, weak current-stage fit
Fusion | Expert-routing / MoE | 3.9 | 2.2 | 1.9 | 2.0 | 3 | Attractive, but currently weak on fit and cleanliness
Model | Linear regularized | 3.5 | 4.9 | 4.9 | 4.8 | 5 | Mandatory discipline floor
Model | Tree-based tabular | 4.0 | 4.2 | 3.8 | 3.9 | 4 | Strong comparator if added carefully
Model | Market-only MLP | 4.0 | 4.3 | 4.3 | 4.2 | 5 | Good nonlinear baseline family
Model | Simple multimodal gated regressor | 4.4 | 4.4 | 4.0 | 4.1 | 5 | Strong current main multimodal family
Model | Multi-task multi-horizon | 4.2 | 3.9 | 3.7 | 4.0 | 4 | Strong second-wave comparison family
Model | Ranking-first model | 4.1 | 3.5 | 3.2 | 3.4 | 4 | Good later alternative objective family
Model | Uncertainty-aware model | 4.0 | 3.2 | 2.9 | 3.2 | 4 | Later extension, not first-run core
Model | Graph-aware model | 4.0 | 2.6 | 2.1 | 2.4 | 3 | High burden relative to current maturity
Model | Mixture-of-Experts | 3.7 | 2.1 | 1.8 | 2.0 | 3 | Strong complexity, weak near-term fit
Evaluation | Single holdout | 2.8 | 2.9 | 4.8 | 4.8 | 5 | Simple but too weak alone
Evaluation | Walk-forward | 4.3 | 4.3 | 4.1 | 4.4 | 5 | Core temporal evaluation family
Evaluation | Purged / embargoed walk-forward | 4.7 | 4.9 | 3.8 | 4.0 | 5 | Strongest current benchmark family
Evaluation | Final lockbox | 4.0 | 4.5 | 3.7 | 4.3 | 4 | Important final reporting layer
Evaluation | Paired forecast tests | 3.9 | 4.4 | 3.5 | 4.1 | 5 | Strong after saved predictions exist
Evaluation | Calibration / probabilistic scoring suite | 4.0 | 4.1 | 3.1 | 3.4 | 4 | Only relevant once probabilistic outputs exist
Evaluation | Backtest-overfitting diagnostics | 4.2 | 4.6 | 3.0 | 3.6 | 4 | Valuable when search space expands
Extension | Static company metadata | 3.4 | 4.3 | 4.2 | 4.6 | 4 | Clean low-risk extension
Extension | Dynamic company profile | 3.9 | 2.0 | 1.9 | 2.1 | 2 | High leakage and timing burden
Extension | Graph / relation branch | 4.0 | 2.6 | 2.2 | 2.5 | 3 | Legitimate but late
Extension | Regime-aware branch | 4.1 | 3.3 | 3.1 | 3.3 | 4 | Better as modest context before heavy regime modeling
Extension | Uncertainty-aware outputs | 4.0 | 3.2 | 2.9 | 3.1 | 4 | Later branch only
Extension | Derivative appendix branch | 2.9 | 2.8 | 3.6 | 3.0 | 4 | Narrow and late only
Extension | Stronger frozen encoder | 4.2 | 3.9 | 3.6 | 3.8 | 4 | Good later strengthening branch
Extension | End-to-end text fine-tuning | 4.3 | 2.4 | 1.8 | 2.0 | 3 | High upside, weak current fit


SECTION 16. INTERPRETING THE FINAL TABLE WITHOUT TURNING IT INTO A WINNER LIST

How to read the table correctly

1. Look horizontally first, not vertically.
- each row is a profile
- the question is not “who wins?”
- the question is “what kind of method is this?”

2. Compare within category before comparing across categories.
- targets should be compared first against targets
- feature families against feature families
- fusion families against fusion families
- evaluation families against evaluation families

3. Use group scores to detect tradeoff shape.
- high SVS + low EFS often means theoretically strong but currently heavy
- high BIS + high EFS often means benchmark-clean and practical, even if not maximally expressive
- high COS means it is easy to build incrementally on top of other pieces

4. Respect similarity.
- if two methods are close, keep them close
- do not force a hierarchy where the framework does not show one

5. Do not convert this into a final recommendation map automatically.
- this document is a comparison methodology, not a final solution proposal


SECTION 17. DETAILED SUMMARY OF WHAT THIS COMPARISON FRAMEWORK SHOWS

The comparison framework makes several things much clearer.

First, target design is one of the most decisive axes in the project.
Excess returns and factor-aware targets score much better scientifically than raw price-oriented thinking, even if they are slightly more burdensome operationally.

Second, conservative market feature families are stronger than they may look.
Returns, momentum, volatility, range, and liquidity features are not “boring”. In this framework they are strong because they combine predictive plausibility, benchmark cleanliness, explainability, and repo fit better than many fancier alternatives.

Third, event-state scalar enrichments and pooled dense embeddings are both strong, but for different reasons.
Pooled dense embeddings are semantically powerful and repo-compatible. Event-state scalar features are more interpretable and better for causal-trace-like explanation of why the text branch may help.

Fourth, late and gated fusion families are the strongest current multimodal comparison families.
They score well because they preserve benchmark cleanliness and align well with the thesis question of whether text adds value beyond market-only features.

Fifth, graph and MoE families are not nonsensical, but they are currently expensive in exactly the wrong dimensions.
Their main weakness is not lack of theoretical appeal. Their weakness is benchmark burden, repo-stage fit, and clean comparability.

Sixth, uncertainty-aware outputs are scientifically respectable but structurally late.
The framework treats them as real but secondary until the deterministic core benchmark is settled.

Seventh, the derivative-family result is now measurable rather than intuitive.
It does not score terribly in pure feasibility because it is easy to add. It scores poorly in Scientific Value, Benchmark Integrity, and Compatibility because it is highly redundant, easy to expand irresponsibly, and weakly central to the thesis question. This is the most useful outcome of the framework for the derivative debate.


SECTION 18. LIMITATIONS OF THIS COMPARISON DOCUMENT

This document is broad and measurable, but it still has limits.

1. It is a profile framework, not an empirical tournament.
- real benchmark results can still move some scores later

2. Some families have stronger literature support than repo support.
- graph, regime, and MoE examples exist in literature, but current repo-stage fit remains weaker

3. Some families have stronger repo support than literature novelty.
- conservative feature families and saved-prediction evaluation are not novel, but they score strongly because they are robust and fitting for this thesis

4. Some source metadata remain imperfect.
- where that happened, uncertainty has been preserved explicitly in the corresponding paper notes

5. No overall score was created.
- this is intentional
- adding one would create false precision and would encourage hidden winner-picking


SECTION 19. WHAT THIS DOCUMENT SHOULD BE USED FOR

Use this document to:
- compare families fairly without forcing a final choice
- identify where two methods are truly similar
- detect when a method is attractive in theory but poor in current repo fit
- detect when a method is benchmark-clean even if not flashy
- keep later research or implementation discussions grounded in measurable tradeoffs rather than taste

Do not use this document to:
- announce a final winner
- collapse broad categories into one “best method”
- ignore the benchmark-family constraints already defined by governance and prior research


SECTION 20. FINAL COMPARISON CONCLUSION

This comparison framework shows that the project can now compare its methods and techniques on a much fairer basis than before.

The important shift is not that one technique now clearly wins.
The important shift is that the project no longer needs to talk about methods only in vague prose.

Now the project can ask:
- is this family theoretically clear?
- is it easy to compare fairly?
- is it leakage-safe?
- is it reproducible?
- is it accumulatively compatible with the current repository?
- is it easy to debug and maintain?
- is it likely to be benchmark-clean?
- is it likely to inflate complexity faster than understanding?

That is a much stronger position than before.

And it is especially important because the current repo stage is no longer pure ideation. It is advanced enough that the biggest danger is not lack of options. The biggest danger is choosing or expanding without a stable way to compare.

This document is the comparison layer intended to solve that problem without turning the research into a premature winner-take-all exercise.
