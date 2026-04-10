Paper ID
- P21

Full citation
- Zetao Zheng, Jie Shao, Jia Zhu, and Heng Tao Shen. 2023. Relational Temporal Graph Convolutional Networks for Ranking-Based Stock Prediction. In 2023 IEEE 39th International Conference on Data Engineering (ICDE). https://doi.org/10.1109/ICDE55515.2023.00017

Verification log
- Verification status: fully verified.
- DOI, DBLP, and OpenAlex align on title, authors, year, and venue.

Source 1
- DOI landing page
- https://doi.org/10.1109/ICDE55515.2023.00017

Source 2
- DBLP record
- https://dblp.org/rec/conf/icde/Zheng00S23

Source 3
- OpenAlex
- https://openalex.org/W4385284998

Exact title
- Relational Temporal Graph Convolutional Networks for Ranking-Based Stock Prediction

Authors
- Zetao Zheng
- Jie Shao
- Jia Zhu
- Heng Tao Shen

Year
- 2023

Venue
- 2023 IEEE 39th International Conference on Data Engineering (ICDE)

DOI
- 10.1109/ICDE55515.2023.00017

Stable links
- https://doi.org/10.1109/ICDE55515.2023.00017
- https://dblp.org/rec/conf/icde/Zheng00S23
- https://openalex.org/W4385284998

Research family
- Graph-aware stock prediction
- Ranking-first forecasting

Why relevant to this project
- It is a strong literal reference for graph plus ranking formulations in stock prediction.

Main problem addressed
- Improving ranking-based stock prediction with relational temporal graph convolution.

Inputs / modalities
- Temporal stock information
- explicit relational structure

Target design
- Ranking-based stock prediction.

Model family
- Relational temporal graph convolutional network.

Evaluation design
- Comparative ranking-based stock-prediction experiments.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Graph edges and relation timestamps must be point-in-time safe.
- Ranking-based back-tests require strong benchmark discipline.

Pros
- Strong direct relevance to later graph/ranking extensions.
- More recent than older graph-stock references.

Cons
- Higher engineering and benchmark complexity than the current core repo likely needs.

Repository-fit implications
- Better viewed as a later extension family after the basic market plus event-state benchmark is settled.

Modularity implications
- Requires clear separation between relation construction, temporal encoding, and ranking objective.

What this paper supports
- Relation-aware ranking as a legitimate future direction.

What this paper does not support
- Making graph/ranking the first main thesis identity.

Reproducibility notes
- Metadata are strong.
- Full graph construction and benchmark hygiene should be checked before any implementation borrowing.

Key literal quotes
- Uncertain, verify manually.

Final usefulness rating
- high
