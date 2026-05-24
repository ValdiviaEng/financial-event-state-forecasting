# DeepResearch Chat Topic: Relevant News Attribution

Status: proposed deep-research chat prompt only. Do not execute repository code, scrape new providers, run LLMs, or approve implementation.

## Required Background Files To Read First

| File | Why |
| --- | --- |
| `ResearchTruth.md` | Current Alpha Vantage limitations, Stage 3 alignment, and Stage 10C non-claims. |
| `ScopeDecisionLog.md` | Provider-stack, relevant-news, and LLM approval boundaries. |
| `docs/Data_Separation_And_Overfitting_Control.md` | As-of availability and leakage controls. |
| `UsageManual.md` | Current aligned-news and Stage 10C artifact usage, inputs, and outputs. |
| `Stage10APrompt.md` | Research context for news display. |
| `Stage10BPrompt.md` | Relevant-news decision question and selected option. |
| `Stage10CPrompt.md` | Implemented deterministic news-context requirement. |
| Current Stage 10C packet under `data/prediction_outputs/phase1_top50/...` | Existing relevant-news context artifacts to treat as baseline evidence. |

## Repository Context

The current Stage 3 feature pipeline aligns Alpha Vantage news to same-day as-of-close rows and creates deterministic event-state features. Stage 10C now displays deterministic aligned-news context for top-10 historical prediction outputs, without URLs or LLM summaries. Provider-level article completeness is not claimed, and truncation/empty-feed flags must remain visible.

## Research Ask

Research deterministic ways to select and present the most relevant aligned news items for local prediction-output artifacts without claiming causal attribution or using unapproved local LLM summarization. Treat current Stage 10C aligned-news context as the baseline to improve, not as missing functionality.

## Questions

| Question | Desired answer |
| --- | --- |
| Relevance signal | Which available fields can rank news: recency, ticker match, provider sentiment, topic tags, article count, or event-state feature contribution? |
| Attribution limits | How should the UI distinguish model input context from causal explanation? |
| Text display | What minimal snippets or metadata should be shown while respecting provider limitations? |
| LLM option | What would be required for local summarization, and what GPU/reproducibility risks arise? |
| Missing news | How should no-news rows and truncation-risk rows be displayed? |
| Stage 10C compatibility | Which improvements fit current packet schemas, and which require new approved fields or validation? |
| Validation | How can tests ensure displayed news was available as-of the prediction date? |

## Desired Output

Return cited approaches, deterministic relevance refinements, optional LLM extension risks, schema suggestions, caveat wording, and validation checks. Do not recommend scraping a new provider or presenting displayed news as causal explanation without separate approval.
