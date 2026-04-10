Paper ID
- P15

Full citation
- Xiao Ding, Yue Zhang, Ting Liu, and Junwen Duan. 2016. Knowledge-Driven Event Embedding for Stock Prediction. In Proceedings of COLING 2016, 2133-2142.

Verification log
- Verification status: fully verified.
- ACL Anthology, DBLP, and OpenAlex agree on title, authors, year, and venue.
- No DOI was established from the verified sources used in this pass.

Source 1
- ACL Anthology
- https://aclanthology.org/C16-1201/

Source 2
- DBLP
- https://dblp.org/rec/conf/coling/DingZLD16

Source 3
- OpenAlex
- https://openalex.org/W2575002693

Exact title
- Knowledge-Driven Event Embedding for Stock Prediction

Authors
- Xiao Ding
- Yue Zhang
- Ting Liu
- Junwen Duan

Year
- 2016

Venue
- COLING 2016

DOI
- Uncertain, verify manually.

Stable links
- https://aclanthology.org/C16-1201/
- https://dblp.org/rec/conf/coling/DingZLD16
- https://openalex.org/W2575002693

Research family
- Event-driven finance
- Event representation

Why relevant to this project
- It is one of the closest historical references to the project’s shift from generic sentiment toward event representation.

Main problem addressed
- Improving stock prediction by building knowledge-driven event embeddings from financial news.

Inputs / modalities
- Financial news text
- event-level structured representations

Target design
- Stock prediction from event information.

Model family
- Event embedding model with knowledge-driven structure.

Evaluation design
- Comparative prediction study on stock prediction tasks.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Event extraction timing and event-to-market alignment remain critical.
- The current note does not establish full leakage controls.

Pros
- Strong direct relevance to event-state/event representation design.
- Supports structured text abstraction rather than flat sentiment.

Cons
- Older event-driven framing may still be too close to isolated-event logic compared with this thesis’s broader event-state framing.

Repository-fit implications
- Supports maintaining a distinct event-state construction layer rather than folding text directly into the model with no structured intermediate representation.

Modularity implications
- Good fit for separate text normalization, event extraction or event encoding, and downstream forecast modules.

What this paper supports
- Event abstraction as a serious bridge between news and stock prediction.

What this paper does not support
- That event extraction alone is sufficient or superior to an event-state framing in this repo.

Reproducibility notes
- Metadata are strong.
- Full paper should be consulted for exact feature and benchmark details before implementation borrowing.

Key literal quotes
- Uncertain, verify manually.

Final usefulness rating
- high
