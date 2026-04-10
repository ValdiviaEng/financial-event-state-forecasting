Paper ID
- P05

Full citation
- Fuli Feng, Xiangnan He, Xiang Wang, Cheng Luo, Yiqun Liu, and Tat-Seng Chua. 2019. Temporal Relational Ranking for Stock Prediction. ACM Transactions on Information Systems, 37(2), Article 27, 1-30. https://doi.org/10.1145/3309547

Verification log
- Verification status: fully verified.
- Journal publication metadata, DOI, and arXiv preprint reference align across the three sources used.

Source 1
- arXiv abstract page
- https://arxiv.org/abs/1809.09441

Source 2
- DBLP record
- https://dblp.org/rec/journals/tois/FengHWLLC19

Source 3
- DOI landing page
- https://doi.org/10.1145/3309547

Exact title
- Temporal Relational Ranking for Stock Prediction

Authors
- Fuli Feng
- Xiangnan He
- Xiang Wang
- Cheng Luo
- Yiqun Liu
- Tat-Seng Chua

Year
- 2019

Venue
- ACM Transactions on Information Systems

DOI
- 10.1145/3309547

Stable links
- https://arxiv.org/abs/1809.09441
- https://doi.org/10.1145/3309547
- https://dblp.org/rec/journals/tois/FengHWLLC19

Research family
- Ranking-first stock prediction
- Relation-aware forecasting
- Graph-temporal stock modeling

Why relevant to this project
- It is directly relevant for the ranking family and for relation-aware extensions to stock forecasting.

Main problem addressed
- Existing stock-prediction methods often optimize point prediction rather than investment ranking and often ignore relations among stocks.

Inputs / modalities
- Stock temporal data
- relation network among stocks or companies

Target design
- Ranking stocks by expected return.

Model family
- Relational stock ranking with temporal graph convolution.

Evaluation design
- Historical back-testing on stock-market datasets against prior approaches.

Metrics
- Return ratio is explicitly referenced in the verified abstract.
- Exact full metric suite is Uncertain, verify manually.

Leakage / benchmark risks
- Historical back-testing is inherently vulnerable to survivorship bias, look-ahead bias, and relation timestamp leakage if poorly implemented.
- This paper is useful, but its back-testing assumptions should not be imported without scrutiny.

Pros
- Strongly aligned with the ranking family.
- Recognizes that stocks should not always be treated independently.
- Financially realistic in objective framing.

Cons
- Relation construction may be difficult and data-intensive.
- Back-test cleanliness matters enormously.

Repository-fit implications
- Useful as a later extension if the project moves from pure regression into ranking evaluation or relation-aware modeling.

Modularity implications
- Suggests separate modules for temporal encoding, relation structure, and ranking objective.

What this paper supports
- Ranking-first formulations as serious alternatives to pure regression.
- Relation-aware stock prediction as a legitimate extension family.

What this paper does not support
- That relation-aware modeling should be the first priority before the core market plus event-state question is settled.
- That back-testing alone is sufficient evidence without strong leakage control.

Reproducibility notes
- Bibliographic metadata are stable.
- Full back-test hygiene should be checked in the full paper before any implementation borrowing.

Key literal quotes
- "most existing deep learning solutions are not optimized towards the target of investment, i.e., selecting the best stock with the highest expected revenue."
- "they largely treat the stocks as independent of each other."
- "The key novelty of our work is the proposal of a new component in neural network modeling, named Temporal Graph Convolution"

Final usefulness rating
- high
