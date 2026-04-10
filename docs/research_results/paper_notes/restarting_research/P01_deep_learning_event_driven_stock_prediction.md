Paper ID
- P01

Full citation
- Xiao Ding, Yue Zhang, Ting Liu, and Junwen Duan. 2015. Deep Learning for Event-Driven Stock Prediction. In Proceedings of the Twenty-Fourth International Joint Conference on Artificial Intelligence (IJCAI 2015), 2327-2333.

Verification log
- Verification status: verified with one metadata limitation.
- Title, authors, year, venue, and pages were confirmed from IJCAI and DBLP.
- DOI was not safely established from the verified sources used in this pass.
- Result: usable with a DOI uncertainty note.

Source 1
- IJCAI abstract page
- https://www.ijcai.org/Abstract/15/329

Source 2
- IJCAI PDF page
- https://www.ijcai.org/Proceedings/15/Papers/329.pdf

Source 3
- DBLP record
- https://dblp.org/rec/conf/ijcai/DingZLD15

Exact title
- Deep Learning for Event-Driven Stock Prediction

Authors
- Xiao Ding
- Yue Zhang
- Ting Liu
- Junwen Duan

Year
- 2015

Venue
- Proceedings of the Twenty-Fourth International Joint Conference on Artificial Intelligence (IJCAI 2015)

DOI
- Uncertain, verify manually.

Stable links
- https://www.ijcai.org/Abstract/15/329
- https://www.ijcai.org/Proceedings/15/Papers/329.pdf
- https://dblp.org/rec/conf/ijcai/DingZLD15

Research family
- Event-driven financial prediction
- News-to-market modeling
- Deep learning for stock movement prediction

Why relevant to this project
- It is one of the clearest early references for using text-derived events as predictive signals for stock movement.
- It helps justify why an event abstraction layer is conceptually better than raw sentiment alone.

Main problem addressed
- Predict stock price movement from news-derived event information while modeling both short-term and longer-term event effects.

Inputs / modalities
- Financial news text converted into extracted events.
- Historical stock-market information is part of the predictive setting.
- Exact full input schema is Uncertain, verify manually.

Target design
- Stock price movement prediction.
- Index and individual-stock prediction are both referenced in the verified abstract.

Model family
- Neural tensor network for event embedding.
- Deep convolutional neural network for price-movement prediction.

Evaluation design
- Compared against earlier baselines on index and stock prediction tasks.
- Includes market simulation according to the verified abstract.
- Full split protocol is Uncertain, verify manually.

Metrics
- Improvement over baselines is stated in the abstract.
- Market simulation profit capability is stated in the abstract.
- Exact metric names are Uncertain, verify manually.

Leakage / benchmark risks
- Event-to-date timing alignment is critical but not fully documented in the verified abstract.
- Train/test temporal design is not clear from the source snippets used here.
- The paper is historically important, but its evaluation hygiene should not be imported blindly.

Pros
- Strong early event representation idea.
- Explicitly connects event extraction with market prediction.
- Recognizes different event influences across time.

Cons
- Verified source snippets do not expose full leakage controls.
- Not a multimodal benchmark-clean paper by current standards.
- Event extraction quality can dominate downstream results.

Repository-fit implications
- Best fit is as conceptual support for the event-state branch, not as a direct architecture blueprint.
- Supports keeping event processing separate from downstream forecasting modules.

Modularity implications
- Encourages separate event extraction, event encoding, and downstream forecast modules.
- Compatible with a branch-based design where text/event processing is not entangled with baseline market preprocessing.

What this paper supports
- Using event abstractions from financial text.
- Deep models for event-informed market forecasting.

What this paper does not support
- That isolated article effects are the right final conceptual framing.
- That event-driven modeling automatically beats strong market-only baselines under modern leakage-safe evaluation.
- That graph, profile, or uncertainty branches are necessary.

Reproducibility notes
- Official IJCAI page and PDF are accessible.
- Bibliographic metadata are cleanly mirrored in DBLP.
- DOI remains unresolved in this verification pass and should not be fabricated.

Key literal quotes
- "We propose a deep learning method for event-driven stock market prediction."
- "First, events are extracted from news text, and represented as dense vectors, trained using a novel neural tensor network."
- "Second, a deep convolutional neural network is used to model both short-term and long-term influences of events on stock price movements."

Final usefulness rating
- high
