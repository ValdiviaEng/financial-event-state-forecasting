Paper ID
- P03

Full citation
- Yao-Hung Hubert Tsai, Shaojie Bai, Paul Pu Liang, J. Zico Kolter, Louis-Philippe Morency, and Ruslan Salakhutdinov. 2019. Multimodal Transformer for Unaligned Multimodal Language Sequences. In Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics, 6558-6569. Association for Computational Linguistics. https://doi.org/10.18653/v1/P19-1656

Verification log
- Verification status: fully verified.
- Title, authors, venue, year, DOI, pages, and abstract align across ACL and DOI records.

Source 1
- ACL Anthology landing page
- https://aclanthology.org/P19-1656/

Source 2
- ACL Anthology PDF
- https://aclanthology.org/P19-1656.pdf

Source 3
- DOI landing page
- https://doi.org/10.18653/v1/P19-1656

Exact title
- Multimodal Transformer for Unaligned Multimodal Language Sequences

Authors
- Yao-Hung Hubert Tsai
- Shaojie Bai
- Paul Pu Liang
- J. Zico Kolter
- Louis-Philippe Morency
- Ruslan Salakhutdinov

Year
- 2019

Venue
- Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics

DOI
- 10.18653/v1/P19-1656

Stable links
- https://aclanthology.org/P19-1656/
- https://aclanthology.org/P19-1656.pdf
- https://doi.org/10.18653/v1/P19-1656

Research family
- Multimodal fusion
- Cross-modal attention
- Unaligned multimodal sequences

Why relevant to this project
- It is one of the clearest references for cross-modal attention when modalities are asynchronous or sampled at different rates.

Main problem addressed
- Modeling multimodal sequences when modalities are not naturally aligned and long-range cross-modal dependencies matter.

Inputs / modalities
- Natural language
- facial gestures
- acoustic behaviors

Target design
- Multimodal sequence prediction/classification tasks in non-finance domains.

Model family
- Transformer with directional pairwise cross-modal attention.

Evaluation design
- Evaluated on aligned and non-aligned multimodal sequence datasets against prior state-of-the-art methods.

Metrics
- Uncertain, verify manually.

Leakage / benchmark risks
- Does not address finance-specific time leakage.
- Alignment assumptions are central; careless borrowing into finance without strict timing rules would be dangerous.

Pros
- Strong conceptual reference for asynchronous multimodal fusion.
- Explicitly attacks non-alignment rather than assuming synchronized modalities.

Cons
- Domain is not finance.
- Not directly about forecasting financial returns.
- More expressive than what the current repo likely needs as a first serious baseline.

Repository-fit implications
- Best treated as an optional later fusion-family reference, not as the immediate architecture default.

Modularity implications
- Suggests a reusable cross-modal interaction block that could sit above branch encoders, but with materially higher benchmark burden than late or gated fusion.

What this paper supports
- Cross-modal attention for unaligned signals.
- The idea that modality alignment is a real design problem, not a mere preprocessing footnote.

What this paper does not support
- A claim that cross-attention is necessary for this thesis.
- Any finance-specific superiority claim.

Reproducibility notes
- ACL page provides stable metadata, abstract, DOI, and PDF.
- Full metric details should be taken from the PDF if a later implementation note depends on them.

Key literal quotes
- "two major challenges in modeling such multimodal human language time-series data exist: 1) inherent data non-alignment due to variable sampling rates for the sequences from each modality; and 2) long-range dependencies between elements across modalities."
- "we introduce the Multimodal Transformer (MulT) to generically address the above issues in an end-to-end manner without explicitly aligning the data."
- "At the heart of our model is the directional pairwise crossmodal attention"

Final usefulness rating
- medium
