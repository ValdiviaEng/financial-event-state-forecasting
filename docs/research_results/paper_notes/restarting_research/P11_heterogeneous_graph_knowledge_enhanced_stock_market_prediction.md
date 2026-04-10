Paper ID
- P11

Full citation
- Kai Xiong, Xiao Ding, Li Du, Ting Liu, and Bing Qin. 2021. Heterogeneous graph knowledge enhanced stock market prediction. AI Open, 2, 168-174. https://doi.org/10.1016/j.aiopen.2021.09.001

Verification log
- Verification status: fully verified.
- Title, authors, year, venue, pages, and DOI align across DOI, Crossref, and ScienceDirect.

Source 1
- DOI landing page
- https://doi.org/10.1016/j.aiopen.2021.09.001

Source 2
- Crossref DOI metadata
- https://api.crossref.org/works/10.1016/j.aiopen.2021.09.001

Source 3
- ScienceDirect article page
- https://www.sciencedirect.com/science/article/pii/S2666651021000243

Exact title
- Heterogeneous graph knowledge enhanced stock market prediction

Authors
- Kai Xiong
- Xiao Ding
- Li Du
- Ting Liu
- Bing Qin

Year
- 2021

Venue
- AI Open

DOI
- 10.1016/j.aiopen.2021.09.001

Stable links
- https://doi.org/10.1016/j.aiopen.2021.09.001
- https://www.sciencedirect.com/science/article/pii/S2666651021000243

Research family
- Graph-aware stock prediction
- Knowledge-enhanced finance modeling

Why relevant to this project
- It is a direct example of adding graph and knowledge structure to stock prediction from textual or semantic information.

Main problem addressed
- Improving stock-market prediction by modeling interactions among different-grained semantic units using a heterogeneous graph.

Inputs / modalities
- Financial text
- multi-grained information nodes derived from that text

Target design
- Stock market tendency prediction.

Model family
- Heterogeneous neural network over a heterogeneous graph.

Evaluation design
- Experimental comparison against baselines on the stock-prediction task.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Timestamp-safe graph construction is critical.
- The verified source snippet does not document detailed anti-leakage protocol.
- Relation-building itself can become a benchmark-family shift if introduced late.

Pros
- Strong direct relevance to graph-aware extensions.
- Moves beyond flat text representations.
- Open-access article path is available.

Cons
- Detailed benchmark protocol is not visible from the brief verified source pass.
- Graph construction adds data and implementation burden.

Repository-fit implications
- Best viewed as a later extension family after the core market plus event-state benchmark is stable.

Modularity implications
- Encourages separate modules for node construction, relation construction, graph encoding, and prediction.

What this paper supports
- Graph and knowledge augmentation as a legitimate stock-prediction family.
- Multi-granular text-derived structure as richer than pure pooled embeddings.

What this paper does not support
- That graph modeling should be introduced before the current repo’s core benchmark is settled.
- Any guarantee that graph complexity will pay off enough for this thesis.

Reproducibility notes
- Metadata are strong.
- Full graph specification and evaluation details should be taken from the article before implementation borrowing.

Key literal quotes
- "We propose constructing a heterogeneous graph with different-grained information nodes from financial text for the task."
- "A novel heterogeneous neural network is presented to aggregate multi-grained information."
- "Experimental results demonstrate that our proposed approach reaches higher performance than baselines."

Final usefulness rating
- high
