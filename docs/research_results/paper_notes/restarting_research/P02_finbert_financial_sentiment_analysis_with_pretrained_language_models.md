Paper ID
- P02

Full citation
- Dogu Araci. 2019. FinBERT: Financial Sentiment Analysis with Pre-trained Language Models. CoRR abs/1908.10063.

Verification log
- Verification status: verified with a venue-status ambiguity.
- Title, author, year, and arXiv/CoRR status were confirmed.
- The PDF also states it is an MSc thesis submission, so the safest venue label is not a journal or conference claim.

Source 1
- arXiv abstract page
- https://arxiv.org/abs/1908.10063

Source 2
- arXiv PDF
- https://arxiv.org/pdf/1908.10063

Source 3
- DBLP record
- https://dblp.org/rec/journals/corr/abs-1908-10063

Exact title
- FinBERT: Financial Sentiment Analysis with Pre-trained Language Models

Authors
- Dogu Araci

Year
- 2019

Venue
- CoRR / arXiv preprint
- The PDF states it is also an MSc thesis submission.
- Uncertain, verify manually.

DOI
- 10.48550/arXiv.1908.10063

Stable links
- https://arxiv.org/abs/1908.10063
- https://arxiv.org/pdf/1908.10063
- https://dblp.org/rec/journals/corr/abs-1908-10063

Research family
- Financial NLP
- Domain-adapted language models
- Financial sentiment analysis

Why relevant to this project
- It is one of the most practical references for why finance-specific text encoders are preferable to generic sentiment tools when building a text branch.

Main problem addressed
- General-purpose NLP models underperform on finance-specific sentiment due to specialized vocabulary and limited labeled data.

Inputs / modalities
- Financial text.

Target design
- Sentiment classification on financial sentiment datasets.

Model family
- BERT-based pretrained language model adapted to finance.

Evaluation design
- Evaluated on two financial sentiment datasets.
- Studies the effect of smaller training sets and partial fine-tuning.

Metrics
- The abstract states improvement on every measured metric.
- Exact metric names are Uncertain, verify manually.

Leakage / benchmark risks
- Domain pretraining and fine-tuning corpus boundaries matter.
- It is not a forecasting paper, so importing performance claims directly into stock prediction would be invalid.

Pros
- Finance-domain language modeling is directly relevant to the repository’s text branch.
- Shows that domain adaptation can outperform generic sentiment baselines.
- Practical for frozen finance-aware embeddings.

Cons
- Single-modality sentiment paper, not a multimodal forecasting paper.
- Does not itself justify forecasting gains.
- Venue status is less clean than a standard archival journal or conference paper.

Repository-fit implications
- Strong support for a frozen finance-domain encoder or finance-aware embedding backend.
- Best used upstream of event-state construction rather than as the final model itself.

Modularity implications
- Cleanly supports a modular NLP stage that feeds embeddings or sentiment features into downstream event-state and forecasting branches.

What this paper supports
- Using domain-adapted language representations for financial text.
- Avoiding generic off-the-shelf sentiment models as the only text representation.

What this paper does not support
- Direct claims that finance-domain text models guarantee stock-prediction gains.
- End-to-end multimodal architecture choices.
- Graph, ranking, or uncertainty design decisions.

Reproducibility notes
- arXiv sources are public and stable.
- DBLP confirms bibliographic metadata.
- The exact preferred venue citation format should be checked against committee expectations.

Key literal quotes
- "Financial sentiment analysis is a challenging task due to the specialized language and lack of labeled data in that domain."
- "We introduce FinBERT, a language model based on BERT, to tackle NLP tasks in the financial domain."
- "FinBERT outperforms state-of-the-art machine learning methods."

Final usefulness rating
- high
