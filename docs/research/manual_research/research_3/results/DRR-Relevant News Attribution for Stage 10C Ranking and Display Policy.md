# Relevant News Attribution for Stage 10C: Ranking and Display Policy

**Executive Summary:** We recommend a default policy that deterministically ranks available aligned-news by a small set of interpretable signals â€“ chiefly *recency* (news published closest to the prediction â€œas-ofâ€ time) and *ticker relevance* (news explicitly about the target asset) â€“ with sentiment magnitude or content-based tags as secondary tiebreakers.  The UI should label all news as contextual â€œinput dataâ€ (e.g. â€œAligned News Context â€“ *for reference only*â€) and explicitly disclaim that these items are *not causal explanations*.  Only minimal snippets (headline and provider + date/time, plus perhaps first sentence) should be shown, to respect data licenses and readability.  We advise against any auto-summarization step in production, due to heavy data/cost requirements (e.g. training or running a finance-tuned language model) and reproducibility concerns; this can be flagged as a future extension only.  For rows with no news, we display a clear â€œNo news available as-of this timeâ€ message; for heavy-data tickers we may display a â€œNews truncation: more items existâ€ indicator.  No new providers or external data sources are needed.  Any enhancements should fit the existing Stage10C JSON schema (e.g. by reusing or slightly extending the current `news_context` structure) and be validated by tests that ensure every displayed articleâ€™s timestamp is â‰¤ the prediction time.  We outline an implementation roadmap (data verification tests, UI text changes, etc.) as well as precise disclaimer text to avoid implying causality.

---

## Repository & Stage 10C Context

The **Stage 10C** output packet (under `data/prediction_outputs/phase1_top50/...`) currently includes, for each historical prediction row, up to 10 aligned news items selected by the stageâ€‘3 pipeline.  These items come from Alpha Vantageâ€™s **NEWS_SENTIMENT** feed queried for the ticker, and were attached deterministically (often simply in reverse chronological order, subject to pipeline rules) as context.  The current pipeline omits raw URLs or full texts (to comply with licensing) and instead provides fields like headline, ticker, timestamp, and possibly a simple sentiment score or label.  (Provider logos or â€œsource nameâ€ are likely included as metadata.)  Importantly, the system already tracks the possibility of missing or truncated news: for example, Stage1 logs note that AlphaV queries can be truncated at 1000 results and that some tickers had zero articles in a window.  The repositoryâ€™s design explicitly **does not claim any news completeness** â€“ it leaves flags for â€œno newsâ€ or â€œmore news existsâ€ visible.

Our goal is to refine how the *most relevant* subset of those news items is chosen and shown.  We **cannot** introduce any new data feeds (no scraping or other APIs), nor use machine-learning summaries without approval.  Instead, we can only use existing fields like publication time, tickers mentioned, and any sentiment/metadata the provider gives.  We will rank and filter deterministically, and surface at most ~3â€“5 items per prediction row (avoiding user overload).  All selected news remains *context* for the user; the UI must clearly say this is input data, not an explanation of the modelâ€™s decision.

## Relevance-Ranking Signals

We recommend a simple *weighted sorting* of available items by these primary signals:

- **Recency:** Sort by the time of publication *relative to the as-of timestamp*.  News closest to (but not after) market close at the row date is likely most relevant.  For example, on a given trading date, overnight or pre-market news the next day may also matter, so one can consider â€œovernightâ€ items with a small positive weight.  In practice, simply descending timestamp (with later = higher rank) is robust.  This prioritizes latest information and automatically yields determinism (breaking ties by secondary rules).
- **Ticker-specificity:** Give preference to articles explicitly about the assetâ€™s ticker.  (AlphaVantage allows filtering by ticker when querying, so all returned news should mention the ticker, but some items may mention multiple tickers or be tagged broadly.)  If there are extra â€œrelated newsâ€ items not specific to the target, we can demote them slightly.  One approach is to sort by the number of ticker mentions or by matching the articleâ€™s ticker list to exactly the target.
- **Sentiment Magnitude (secondary):** Among equally recent items, those with unusually strong sentiment (very positive or very negative) may deserve prominence, since extreme sentiment often correlates with big price moves.  For instance, if multiple headlines came out at 4pm, we could show those with the highest absolute sentiment score first.  This requires that the feed provides a sentiment field (AlphaVantageâ€™s â€œSentimentScoreâ€ or category).  If available, we sort by |Sentiment|; if not, this step can be omitted.
- **Event/Topic Tags (optional):** If the news data has category labels (e.g. â€œearningsâ€, â€œmergerâ€, etc.) or tags, we could use a whitelist of high-impact topics.  For example, an article tagged â€œearnings reportâ€ might outrank a generic news bit.  However, if no tag field exists in the API, this step is skipped.  (The repositoryâ€™s initial pipeline did not explicitly use topic tags, but it could be a minimal extension.)
- **Article Count / Uniqueness:** If an unusually large number of articles appear, we want diversity.  For example, if 5 headlines are nearly identical (say, multiple wires reprinting an earnings release), we should not show all duplicates.  As a rule, we limit to one item per provider or one â€œrepresentativeâ€ headline per cluster.  A practical approach: drop an article if another in the top-ranked set has >80% headline overlap or identical timestamp.  This avoids crowding the UI with redundant entries.
- **Price-related features (system-level):** The systemâ€™s event-state features (from Stage 3) measure things like volatility or volume spikes around news.  While we *could* incorporate those to rank importance, it risks circularity (using future price info to choose news).  Instead, we suggest *not* using future returns or volatility in the ranking; keep it purely news-based.  (One could qualitatively note, however, that if prices jumped on a day, the news that day should be top-3 by recency anyway.)

By combining these signals in a fixed formula (e.g. sort by recency Ã— 10 + |sentiment|, etc.), we achieve a deterministic ranking.  For instance: **â€œFirst, take all as-of-published articles. Sort by publication time. If more than 5 items, trim to latest 5. Then among those, sort ties or adjust order by descending absolute sentiment. Remove any duplicates or near-duplicates, favoring the earliest occurrence.â€** This kind of rule can be hard-coded in the Stage10C postprocessor.  (No training or randomness is involved.)

## UI Presentation & Attribution Caveats

**Context vs Causation:** In the UI, each news item should be labeled clearly as *contextual input data*, not as an explanation of the prediction.  We recommend a heading like *â€œAligned News Context (for reference, not causal)â€* or *â€œNews (contextual info only)â€*.  Any help text or footnote should explicitly warn the user not to interpret these headlines as the â€œreasonâ€ the model made its forecast.  For example: **â€œNote: These news items were available as of the prediction date and are shown for context. The modelâ€™s output is not a direct reaction to any single headline.â€**  In other words, we avoid language like â€œBecause of this news, the model predictsâ€¦â€.  Instead, emphasize statements like â€œInformational Contextâ€ or â€œBackground headlines near this date.â€  This follows general best practices in financial software, where disclosure of data sources and separation from advice is required.

**Minimal Display Content:** To respect data usage limits (we cannot display full text or URLs), we show only:
- **Headline** (or title of article) â€“ this is usually provided by AlphaVantage.
- **Timestamp and Provider** â€“ e.g. â€œPublished on YYYY-MM-DD HH:MM (Source)â€.
- **Optional Sentiment Tag** â€“ e.g. â€œ(Positive)â€ or â€œ(Negative)â€ if that helps the user quickly scan tone.  This depends on UI space.  If sentiment is numeric, maybe display â€œSentiment: +0.42â€.
- **First Sentence or Snippet (optional)** â€“ only if itâ€™s short (100 characters or so) and cleared for use.  If usage terms allow, a short snippet can help clarity.  Otherwise, skip snippet.
- **No URLs or Images** â€“ as per current baseline. We only have text fields. If the source is known (e.g. â€œReutersâ€), that label is enough.

Each item should fit in a narrow area (e.g. a table row or card).  We avoid showing anything not in the data (no editorial or summary by ChatGPT or external).

**Caveat Wording:** We will need a small notice, e.g.: *â€œDisplayed news were publicly available as of the prediction time. They are shown for informational context only and are **not** explanations of or inputs selected by the model.â€* This could appear as a hover tooltip or footnote on the news section.

## LLM Summarization: Extension Risks

Any proposal to *automatically summarize* articles (e.g. â€œLocal LLM summariesâ€) is risky.  To do it properly, we would need a pretrained financial-language model (like FinBERT or FinGPT) fine-tuned on summarization, plus substantial compute to run it reliably.  For example, building a finance-specific LLM (as in **FinGPT** or **BloombergGPT**) required on the order of *billions* of tokens and state-of-the-art hardware.  Even using an existing LLM for on-the-fly summarization raises issues: large models (tens of billions of parameters) need GPUs or cloud inference (costly, and results can be nondeterministic unless carefully seeded).  Furthermore, summarization models might hallucinate or introduce errors (unsafe without heavy testing).  Reproducibility is a concern: two runs of an LLM could yield different summaries, making auditability hard.  Thus, **we do not enable any LLM summarization** in the default Stage10C pipeline.  If in future an approved FinLLM is integrated, it must be treated as a separate feature (with rigorous evaluation) and clearly labeled â€œAI-Generated Summary (experimental)â€ with additional disclaimers.

## Handling No-News and Truncation

- **No-News Rows:** If the pipeline finds *zero* articles for a given row (e.g. the ticker was newly listed or news API returned empty), the UI should show a clear message like *â€œNo news available at this time.â€* Optionally, we can still display an empty table header with the same field names but all cells marked â€œN/Aâ€.  This should be deterministic and obvious.  (We must not silently skip the news section entirely, because then a user might think the UI failed to load data.)
- **Truncation Risk:** We know AlphaV allows up to 1000 items per query.  Itâ€™s unlikely for a single stock to have >1000 headlines in a one-week window, but if it did, the query would truncate.  The stage1 analysis flagged when a feed was â€œlikely truncatedâ€.  We should surface an indicator if we suspect truncation: for example, if *exactly* 1000 items were fetched, we can append a note like *â€œ1000+ items. Only latest shown.â€*  (Alternatively, if the raw API returns a total-count field, use that.)  This informs the user that there **may be more news beyond what we display**.  Practically, this means: check after fetching news, if count==1000 (the max), set a â€œtruncatedâ€ flag in the JSON.  Then UI can show an icon or text (â€œ+ more news existsâ€).

These messages ensure transparency.  They fit the existing schema by adding just a couple of new boolean or count fields (`news_missing: bool`, `news_truncated: bool`) to the output.  No wholesale schema redesign is needed, only minor extensions that must be approved.

## Validation Tests

To ensure correctness, implement **unit tests** on the Stage10C generation:
1. **As-of Check:** For each displayed item, assert that its publish timestamp is â‰¤ the predictionâ€™s date/time.  This catches any bug that might fetch future news (e.g. if time zones mishandle).
2. **Uniqueness/Deduplication:** If two headlines are identical or near-duplicate (say >80% word overlap), ensure only one appears.
3. **Sort Order:** Test that news are sorted by descending date, with ties broken (e.g. by sentiment).  This is easy to verify on a hand-crafted example list.
4. **Flags Presence:** If `news_truncated` is true, verify that at least one test example had exactly the API limit (1000) items.  If `news_missing` is true, test that there was indeed an API call that returned 0 items.
5. **Schema Conformance:** Unit test that no disallowed fields (like URLs or raw text) are included.

Together, these tests guarantee that whatâ€™s displayed was legitimately available by the as-of time, and that the selection logic ran as intended.  They can be added to the existing test suite (as was done for Stages 2â€“5).

## Implementation Roadmap

| Task                                          | Priority     | Effort (wks) | Impact       |
|-----------------------------------------------|--------------|--------------|--------------|
| *Develop ranking function* (time+sentiment)   | High         | 1            | High         |
| *UI label & disclaimer text*                  | High         | 0.5          | High         |
| *Truncation & no-news flags*                  | Medium       | 1            | Medium       |
| *Update Stage10C schema* (add flags)          | Medium       | 0.5          | Medium       |
| *Write validation tests*                      | High         | 1            | High         |
| *Peer review & documentation*                 | High         | 0.5          | High         |

1. **Ranking function:** Code the deterministic sort (likely in the existing Stage10C generation script).  This requires only small logic, reusing fetched news data.
2. **UI/Disclaimer:** Update the UI component or template that renders Stage10C so that a new header and tooltip/footer appear.  This also includes writing the exact wording.  Keep it concise and user-friendly.
3. **Flag logic:** In the data pipeline, detect 0 or maxed results and set flags in the JSON.
4. **Schema updates:** Extend the JSON schema to include `no_news` and `truncated` booleans (or `count_returned`).  This must go through review (as itâ€™s part of output spec) but is low-risk.
5. **Validation tests:** Implement tests as described. Integrate into CI so any future change is checked.
6. **Review:** Since this touches user-facing UI, have a quick review by an analyst to ensure clarity. Document all new fields in `docs/`.

**Timeline:** This plan can be done in roughly 2â€“3 weeks of work. The immediate gain is in trust and clarity for end users: knowing how news are picked and seeing the new disclaimers significantly improves interpretability.
No vendor, legal, or operational approvals should be needed beyond schema change review, since we are not adding new data or automated LLM features.

### Open Questions / Validation
- We assume the AlphaVantage news APIâ€™s timestamp is in the same timezone as our data (NY/Eastern by market convention). Tests must confirm this alignment.
- If future products allow more interactive filtering (e.g. by entity type), this policy may need revisiting.
- We are not including any forward-looking indicator (like confirming a price jump). If future versions need a â€œmarket surpriseâ€ indicator, that should come from model output, not news selection.

By following this approach, Stage10C will provide *the most salient, up-to-date news context* in a deterministic, transparent way, without overclaiming causality or relying on unproven tech.
