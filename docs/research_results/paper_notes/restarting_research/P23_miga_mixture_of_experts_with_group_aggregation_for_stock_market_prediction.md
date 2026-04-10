Paper ID
- P23

Full citation
- Zhaojian Yu, Yinghao Wu, Genesis Wang, and Heming Weng. 2024. MIGA: Mixture-of-Experts with Group Aggregation for Stock Market Prediction. arXiv:2410.02241.

Verification log
- Verification status: verified with venue-label differences and minor author-name normalization differences.
- arXiv, DBLP, and OpenAlex agree on the paper identity but index the venue differently as arXiv versus CoRR.

Source 1
- arXiv abstract page
- https://arxiv.org/abs/2410.02241

Source 2
- DBLP record
- https://dblp.org/rec/journals/corr/abs-2410-02241

Source 3
- OpenAlex
- https://openalex.org/W4403882607

Exact title
- MIGA: Mixture-of-Experts with Group Aggregation for Stock Market Prediction

Authors
- Zhaojian Yu
- Yinghao Wu
- Genesis Wang
- Heming Weng

Year
- 2024

Venue
- arXiv preprint
- DBLP indexes it under CoRR.

DOI
- 10.48550/arXiv.2410.02241

Stable links
- https://arxiv.org/abs/2410.02241
- https://dblp.org/rec/journals/corr/abs-2410-02241
- https://openalex.org/W4403882607

Research family
- Mixture-of-experts
- Stock prediction

Why relevant to this project
- It is one of the clearest recent finance-specific MoE references for the possibility of expert specialization in stock prediction.

Main problem addressed
- Improving stock-market prediction with MoE and group aggregation.

Inputs / modalities
- Stock-market predictive inputs.
- Exact modality structure is Uncertain, verify manually.

Target design
- Stock market prediction.

Model family
- Mixture-of-experts with group aggregation.

Evaluation design
- Preprint evaluation on stock-market prediction tasks.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- MoE systems are especially sensitive to benchmark complexity, hyperparameter search, and subgroup overfitting.
- This is a strong example of a family that can look attractive before the core benchmark is stable.

Pros
- Direct finance-specific MoE example.
- Useful for understanding what a later expert-routing extension would mean.

Cons
- Preprint only in this verification pass.
- High complexity relative to likely thesis ROI.

Repository-fit implications
- Best treated as a long-later extension family, not a near-term implementation target.

Modularity implications
- Requires clear expert-definition, routing logic, and evaluation separation, which is materially more complex than the current repo default.

What this paper supports
- Expert-routing as a legitimate family for stock prediction.

What this paper does not support
- That MoE should be introduced before the core market plus event-state benchmark is cleanly understood.

Reproducibility notes
- Preprint status means the final peer-reviewed form, if any, should be checked later.

Key literal quotes
- Uncertain, verify manually.

Final usefulness rating
- medium
