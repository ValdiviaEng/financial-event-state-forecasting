RESTARTING THE RESEARCH: LITERATURE EXPANSION ROUND 2

Purpose of this addendum

This file extends the previous restart literature expansion without modifying it. Its purpose is to broaden the verified literature coverage in four areas the user explicitly requested next:
- purge / embargo validation and broader out-of-sample benchmark methodology
- calibration and probabilistic forecasting
- more graph / regime / Mixture-of-Experts papers
- more event-driven finance papers

This addendum should be read together with:
- `docs/research_results/restarting_research_literature_expansion.md`
- `docs/research_results/paper_notes/restarting_research/`

Key repository-consistent insight

The new literature does not overturn the main restart conclusion. It reinforces it.

The project still looks strongest when framed around:
- end-of-day forecasting
- excess-return or similar benchmark-relative targets
- event-state rather than isolated article impact
- market-only versus multimodal comparison
- freeze-first, benchmark-clean evaluation

What the new paper wave adds

1. There is no clean standalone canonical paper for purged or embargo-style cross-validation in finance ML.

This matters because it would be easy to hallucinate one. The strongest literal source found remains de Prado’s 2018 book, and the closest paper-like source is his 2018 Journal of Portfolio Management article on why machine-learning funds fail. This strengthens, rather than weakens, the project’s need to speak cautiously and literally about purge and embargo methodology.

2. The calibration and uncertainty literature is richer than the current repo uses.

The first paper wave already added proper scoring rules and deep ensembles. This new wave adds:
- calibration and sharpness as separate ideas
- density-forecast testing
- a multi-horizon quantile-forecasting family

This broadens the uncertainty-aware branch substantially, but it still does not justify making uncertainty the first main thesis objective. It remains a later extension family because the core deterministic benchmark question is still unresolved.

3. The graph and regime literature continues to support extension status, not core status.

The new graph/ranking paper and the regime-shifting stock-return paper reinforce that both graph structure and regime structure are real research families. But they also reinforce how much extra benchmark burden and modeling burden those families introduce. That confirms the earlier classification: these families are valid, but later.

4. The event-driven literature continues to support event abstraction, not derivative centrality.

The added event-embedding and media-content papers strengthen the case for text-derived event abstraction and richer text-state reasoning. They do not strengthen the case for making derivative-style market transforms the central new contribution.

Detailed additional insights by family

Event-driven finance

Knowledge-Driven Event Embedding for Stock Prediction strengthens the historical event-driven finance line by showing that event abstraction can be enriched structurally rather than reduced to sentiment. Tetlock’s classic media-content paper reminds the project that text content matters, but also that text should not be reduced to crude polarity alone.

Implication for this thesis:
- preserve event-state identity
- do not collapse back into sentiment-only framing

Calibration and probabilistic forecasting

The new calibration papers make the following points clearer:
- proper scoring is not the same thing as calibration
- calibration is not the same thing as sharpness
- density forecast testing has its own methodological requirements
- multi-horizon quantile forecasting is a serious model family, not a decorative output trick

Implication for this thesis:
- probabilistic forecasting is a valid later branch
- but it should remain downstream of the core deterministic benchmark family

Graph / relation-aware and regime-aware families

The new graph-ranking paper confirms that relation-aware stock prediction remains a plausible and literature-supported path. The regime-shifting dynamic factor paper confirms that explicit regime-state modeling is also a real and modern finance direction.

Implication for this thesis:
- both families deserve to stay in the future-directions map
- neither family looks justified as the immediate core restart implementation target

Mixture-of-Experts

The MIGA paper confirms that finance-specific MoE work exists and is not just generic ML transplanted into markets. However, its presence does not improve the current ROI case for MoE in this project.

Implication for this thesis:
- MoE stays on the map
- but it remains a costly, high-benchmark-burden, late-stage idea

Purge / embargo methodology clarification

The most important clarification from this round is negative but useful:

No clean standalone canonical journal paper was found as the original or primary source for purged / embargoed cross-validation in finance ML.

The best literal source remains:
- Marcos López de Prado, Advances in Financial Machine Learning, 2018

The closest paper-like supporting source found is:
- The 10 Reasons Most Machine Learning Funds Fail, 2018

That means any future thesis language should avoid saying “as shown in the purge/embargo paper” unless that paper is explicitly found and verified later.

Important metadata caution discovered in this round

The regime-shifting stock-return paper `RSAP-DFM` has a DOI mismatch problem in the currently accessible metadata trail:
- IJCAI proceedings page and DBLP agree on the paper identity
- the DOI shown on the page resolves in Crossref to a different paper

Implication:
- do not trust the DOI yet
- keep the paper if useful, but mark it explicitly as:
  `Uncertain, verify manually.`

This is exactly why the triple-verification protocol matters.

Updated literature-state verdict after Round 2

The literature map is now broader and better balanced.

What became stronger after this round:
- event abstraction as a central text-side concept
- calibration and proper probabilistic evaluation as later-stage branches
- graph/ranking and regime-aware families as legitimate but later extensions
- the need for literal source caution around purge/embargo methodology

What did not change:
- the thesis should still not choose a final winner yet
- the derivative family still does not deserve core status
- the main question remains market-only versus market plus event-state under strict benchmark discipline
- the strongest immediate work is still benchmark freezing, not architecture expansion

Final addendum conclusion

This second literature wave makes the project broader in a useful way, but not looser.

It adds more diversity of methods, more literal references, and better coverage of calibration, regime, graph, and MoE families.
It does not justify widening the implementation prematurely.

So the broadened but still disciplined conclusion remains:

preserve breadth in the research map
preserve narrowness in the implementation sequence
