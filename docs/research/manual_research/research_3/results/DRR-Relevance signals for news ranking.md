# Relevance signals for news ranking
The available signals in the current pipeline are fairly limited.  News articles aligned to a ticker/date come with a **timestamp** and a **stage-3 article count**, but no built-in sentiment or topic scores.  In practice we can use:
- **Recency:** the articleâ€™s `published_timestamp` (or equivalently `minutes_since_latest_aligned_article`) to prefer fresher news.
- **Article count:** the feature `stage3_aligned_news_count` (total aligned articles that day) signals how much news exists. Rows with many articles might merit multiple snippets or a summary.
- **Ticker match:** by design all aligned articles already match the rowâ€™s ticker.
- *Not available:* AlphaVantage *sentiment* or *topic tags* are not extracted in Stage 3, so we cannot rank by sentiment without new processing. Likewise the event-state embedding has no interpretable â€œimportanceâ€ score per article.
Stageâ€¯10Bâ€™s decision memo explicitly recommended using aligned-news **recency** and **count** (and sentiment if it were available) as the relevance criteriaã€58â€ L33-L35ã€‘.  In implementation, one could sort the aligned articles by `published_timestamp` (descending) and take the top-N.  For example, we have `stage3_aligned_news_count` in the features and can use it to note how many articles exist (e.g. â€œshowing 3 of 5 articlesâ€).  The current code already outputs the first 3 IDs from `aligned_article_ids`, but one could deterministically pick those with the latest timestamps.

# Distinguishing context vs causal explanation in UI
The UI must emphasize that shown news items are **contextual inputs**, not explanations or trading advice.  In other words, label them as â€œrelevant news (context only)â€ and include clear disclaimers.  For example: *â€œThese headlines were present in the historical data for this stock and date. They are shown for context, **not as the cause of the forecast**.â€*  The Stageâ€¯10C non-claims policy requires messages like â€œNot trading adviceâ€ or â€œNo buy/sell signalâ€ã€15â€ L423-L431ã€‘.  We should carry over those non-claim labels in the UI.  Possible tactics: display a banner or footnote saying â€œForecast is a model output; this news is context, **not a recommendation**â€ (echoing `not_trading_advice`, `not_buy_sell_signal`, `not_price_target`ã€15â€ L423-L431ã€‘).  The Stageâ€¯10B claim guidelines likewise say *â€œno buy/sell/price-target claimâ€*ã€58â€ L33-L35ã€‘.  In short, use neutral phrasing and disclaimers (e.g. â€œContext news â€“ no causal inference impliedâ€) so users donâ€™t interpret the news as an explanation or advice.

# Text-snippet display
Only **minimal snippets and metadata** should be shown, in line with provider limits.  Practically, each news record should display its *title* and the beginning of its *summary*, both truncated to a short length (the code uses 240 chars with an ellipsisã€43â€ L759-L763ã€‘).  For example:

- **Title snippet:** e.g. â€œCompany XYZ announces Q2 earnings beat...â€ (clipped if too long).
- **Summary snippet:** e.g. â€œXYZ reported revenue of $1.2B, above expectations of $1.1B...â€ (first sentence or two, truncatedã€43â€ L759-L763ã€‘).
- **Timestamp:** optionally show the publish date/time (at least the date) for context.
- **Provider/source:** if needed, indicate â€œAlphaVantage Newsâ€ or similar, but **do not include article URLs or links**.  The output schema explicitly omits URLs (`url_included=False`) and the UI should not show a hyperlinkã€37â€ L51-L54ã€‘. This respects licensing by giving only excerpts, not full text or direct links.
- **Provider flags:** display the `no_news_flag` and `provider_truncation_risk_flag` (e.g. as icons or text badges).  For example, if `provider_truncation_risk_flag` is true, show a note like â€œ*(feed truncated â€“ more articles may exist)*â€ to indicate possible incompleteness.
- **Total count (optional):** if `stage3_aligned_news_count`> displayed items, the UI might say â€œ(showing 3 of X articles)â€.

In summary, use short, clipped text and metadata.  The Stageâ€¯10C outputs enforce this: they use a `clip_text()` helper to trim contentã€43â€ L759-L763ã€‘, and tests assert no URL column is presentã€37â€ L51-L54ã€‘.  We should mimic that approach in the UI.

# Local LLM summarization (optional)
A local summarization extension would require integrating an LLM (e.g. via Hugging Face or similar).  This has significant overhead: youâ€™d need a suitable model and sufficient compute.  For instance, a modest 7â€“8B parameter model (like Llama-2 7B or GPT-2 style) at FP16 can require 16+â€¯GB VRAM, but can be quantized to run on ~8â€¯GBã€52â€ L137-L146ã€‘.  Summarizing the 3â€“5 news snippets per row *might* fit on a high-end consumer GPU if quantized.  Larger models (13B+) would need multiple GPUs or high-memory cards.

Even then, generating summaries is **non-deterministic** by default.  LLM outputs can vary between runs (even with the same prompt and temperature=0) due to GPU floating-point nondeterminism and samplingã€51â€ L33-L41ã€‘.  Thus, using an LLM brings **reproducibility risks**: summaries may differ each time unless one pins the random seed and environment very tightly.  Moreover, local inference requires careful version control of the model weights and library.  In short, adding a summary step would mean new dependencies, hardware requirements, and stability challenges.

If pursued (and only after explicit approval), one would have to add fields to the schema (e.g. a new `llm_summary` column and set `llm_summary_used=True`).  But without approval, the UI must stick to static snippets.  (Stageâ€¯10B explicitly said any LLM summary is â€œoptional futureâ€ã€58â€ L33-L35ã€‘, so itâ€™s not in Stage10C.)

# Handling missing or truncated news
Rows may have *no aligned articles* or a *truncated feed*.  UI should handle both gracefully:
- **No-news rows:** If `no_news_flag=True` (no articles aligned), display a clear message such as **â€œNo relevant news for this dateâ€**.  You could also leave the news area blank with a note.  This aligns with the design decision to explicitly flag empty event statesã€41â€ L1-L4ã€‘.
- **Truncated feeds:** If `provider_truncation_risk_flag=True`, indicate that the feed may be incomplete.  For example, add a tiny notice like â€œNews feed truncated (1000-item limit reached)â€ or a tooltip.  This makes the data limitation visible.  (Indeed, the Stageâ€¯3 manifest notes that â€œprovider truncation-risk flags are preservedâ€ã€57â€ L69-L76ã€‘.)

In practice, if there are few articles but the truncation flag is on, it means AlphaVantage stopped at 1000, so there might be more unseen articles.  The UI note alerts the user.  Conversely, if no-news flag is on, simply show no items.  Both cases should use clear text or icons to avoid confusion.

# StageÂ 10C schema compatibility
Most simple improvements can use the **existing packet schema**.  For example, resorting articles by date or displaying the count uses current fields (`published_timestamp`, `stage3_aligned_news_count`).  The existing output `relevant_news_context.parquet` already includes `title_snippet`, `summary_snippet`, `no_news_flag`, `provider_truncation_risk_flag`, etc.ã€37â€ L51-L54ã€‘.  We can leverage these without schema changes.  For instance, sorting by `published_timestamp` or showing the count in the UI requires no new data fields.

However, adding new content *would* require schema changes and new validation.  In particular:
- **Sentiment or topics:** Not available; would require extending the Stage3 alignment to extract sentiment scores or topic tags into aligned_news. That would add new columns (and new approval).
- **LLM summaries:** To display an LLM-generated summary, weâ€™d need a new field (e.g. `llm_summary_text`) and to set `llm_summary_used`. This is a substantive schema change.
- **Additional snippets:** If we wanted more than 3 items per row, that constant would be raised in code. (Currently NEWS_ITEMS_PER_ROW=3.) Increasing it is a code change but fits the schema: the output can simply have more rows per prediction row if allowed.
- **Provider name:** If one wanted to label â€œSource: AlphaVantageâ€ per snippet, that could be added as metadata, but itâ€™s not in the schema now. It would require a new column or text.
In summary, basic ranking/display tweaks fit the existing fields; anything beyond that (sentiment, longer summaries, etc.) would need new approved fields. All proposed changes should respect the Stage10 scope (no unapproved provider calls or LLMs).

# Validation checks for â€œas-ofâ€ availability
We must ensure that **no future news leaks in**.  Validation tests should verify that every displayed article was indeed available on or before the prediction date.  Concretely:
- **Timestamp check:** For each row in `relevant_news_context`, its `published_timestamp` (converted to date) should be â‰¤ the rowâ€™s `as_of_date`.  No article should have a publish date after the forecast date.
- **Ticker/date match:** Every articleâ€™s ticker should match the rowâ€™s ticker and `aligned_as_of_date` (which Stage10 carries implicitly).  This ensures correct alignment.
- **No-news consistency:** Whenever `no_news_flag` is true in the event-state features, the relevant-news table should have one (empty) context record with `context_status="no_aligned_news"`. Conversely, if articles exist, `no_news_flag` should be false.  (Stageâ€¯3 guarantees explicit empty statesã€41â€ L1-L4ã€‘.)
- **Truncation flag preservation:** The outputâ€™s `provider_truncation_risk_flag` should equal the input feature flag.  In other words, flagged rows remain flagged in the context.  (As the manifest notes, truncation flags are simply preservedã€57â€ L69-L76ã€‘.)

Tests can implement these checks on the packet files.  For example, reading `relevant_news_context.parquet` and confirming `published_timestamp` â‰¤ `as_of_date` for all rows, and comparing flags to the original `event_state_features` inputs.  Passing these validations ensures the UI only shows news that was legitimately available in the historical feed.

**Sources:** Internal design docs and code (StageÂ 10 prompts and pipeline)ã€58â€ L33-L35ã€‘ã€15â€ L423-L431ã€‘ã€37â€ L51-L54ã€‘ã€43â€ L759-L763ã€‘ã€57â€ L69-L76ã€‘ã€51â€ L33-L41ã€‘ provide the above guidelines. They emphasize using deterministic fields (recency, count), avoiding causal language, respecting provider content limits, and treating truncation/no-news flags explicitly.
