# Deep Research Report: Daily/Weekly Data Refresh Design

**Status:** Research/Design only (no code execution, no data calls, no implementation). All provider-stack, universe, and non-claim constraints from Stage8 and Stage10C prompts are enforced throughoutã€3â€ L39-L47ã€‘ã€1â€ L2-L8ã€‘. In particular, default behavior is plan-only (no provider calls), no raw overwrites, top-50 universe, no benchmarks or fresh predictions producedã€3â€ L39-L47ã€‘ã€29â€ L15-L22ã€‘.

**Executive Summary:** We recommend a **plan-first, overlapping-window** refresh design with strict idempotency, explicit live execution gates, and thorough error handling. The system should use short-date boundary overlaps (e.g. â€œyesterday through todayâ€) for daily updates and week-long windows for weekly updates, ensuring late-arriving data is captured without silent duplication. The main safety principle is **provider-safety**: avoid hitting quotas and never leak secrets. The main tradeoff is between wider overlap (safer missing data capture but more duplicates) and minimal overlap (risk missing late data). The key implementation risk is managing partial data and retries under quotas. The main downstream invalidation risk is *silent stale artifacts*; we must emit explicit rebuild warnings for Stages 2â€“6 when raw data changes. For Stage 10C, the rule is: treat existing prediction packets as **historical only**; do not label them as forecasts, and do not regenerate them without a full Stage2â€“6 rebuildã€1â€ L2-L8ã€‘ã€29â€ L15-L22ã€‘.

We **must not claim** any provider completeness, fresh benchmark, live prediction, or trading signal. All â€œforecast_candidateâ€ semantics and any model-serving are beyond scopeã€1â€ L2-L8ã€‘ã€29â€ L15-L22ã€‘.

Below we document the current repository context, option comparisons, and detailed design recommendations including scripts, schemas, and policies.

---

## 1. Current Repository Interpretation

- **Existing Artifacts:** The repository already contains *plan-first* Stage 8 update scripts (`news_update_daily.py`, `news_update_weekly.py`, `OHLCV_daily_update.py`, `OHLCV_weekly_update.py`) and a shared helper `stage8_data_update_common.py`ã€31â€ L281-L290ã€‘. The guidebook confirms these scripts are **active and executable**ã€31â€ L281-L290ã€‘. They default to plan-only mode (no provider calls) and require `--execute` plus API keys for live runsã€31â€ L283-L292ã€‘ã€29â€ L55-L58ã€‘. The manifest and ledger design are partially implemented via the helper module.

- **Stage 8 Scope:** Stage 8 is **plan-first only** by defaultã€3â€ L39-L47ã€‘. It explicitly does **not** overwrite raw files without `--overwrite`, nor does it make live API calls unless approvedã€3â€ L39-L47ã€‘. It must not imply any fresh benchmark or predictionsã€3â€ L2-L8ã€‘ã€29â€ L15-L22ã€‘.

- **Stage 10C Scope:** Stage 10C has implemented *historical-prediction* output packets using existing Stage 5 saved predictionsã€1â€ L28-L36ã€‘. It does **not** support fresh forecasts or live inference. Existing Stage 10C outputs are **labeled historical** (e.g. `historical_prediction` vs any new `forecast_candidate`)ã€1â€ L28-L36ã€‘.

- **Protected Scope:** Per `ScopeDecisionLog.md`, the news provider is Alpha Vantage and OHLCV provider is Twelve Data; universe is frozen to approved top-50; SPY may appear only as already-approved supportã€5â€ L13-L16ã€‘ã€29â€ L15-L22ã€‘. We must not expand to top-100/500, change providers, or alter benchmark family without new approvalsã€5â€ L13-L16ã€‘ã€29â€ L15-L22ã€‘.

- **What Stage 8 Does:** Stage 8 scripts currently produce plan manifests indicating which raw files *would* be fetched, and optionally execute fetching into raw/ manifests if `--execute` is givenã€31â€ L281-L290ã€‘. They preserve existing files by default and note â€œskippedâ€ files in the manifestã€31â€ L283-L292ã€‘. They redact API keys and require explicit user acknowledgement for any destructive actionsã€31â€ L285-L293ã€‘ã€29â€ L55-L58ã€‘.

- **What Stage 8 Does NOT Do:** The system currently does **not** automatically merge or overwrite raw data (unless `--overwrite` is given)ã€3â€ L39-L47ã€‘. It does not generate any feature/label/model artifacts by itself. It does not assert that all available news is obtained, only that it requests new data within a window.

- **What Stage 10C Does/Does Not:** Stage 10C outputs are static packets from prior predictionsã€1â€ L28-L36ã€‘. It does not run new model inference or service. It remains â€œdiagnostic onlyâ€ for nowã€1â€ L37-L44ã€‘.

- **Key Limitations:** Consistent with documentation, no live inference or trading claims are madeã€1â€ L28-L36ã€‘ã€29â€ L15-L22ã€‘. No benchmark comparability is assumed by raw updatesã€5â€ L13-L16ã€‘. The current manifest design and scripts do not currently cover all corner cases (e.g. truncation refinement is unresolved)ã€11â€ L168-L174ã€‘.

*Evidence classification:* The above summary is **confirmed** by Stage8Prompt, Stage10CPrompt, UsageManual, and ScopeDecisionLogã€3â€ L39-L47ã€‘ã€1â€ L2-L8ã€‘ã€29â€ L15-L22ã€‘ã€5â€ L13-L16ã€‘. Any gaps (e.g. exact day-window logic) are plausible assumptions or unknown.

---

## 2. Scheduling Strategies (Daily vs Weekly)

We compare options for how update scripts choose date windows.

**Daily News Updates:**

- **Option 1: â€œCutoff to Todayâ€ (No Overlap).** Request news from *the day after the last manifest* up to end of today. This avoids duplicates but may miss late-day postings or delays.
- **Option 2: â€œYesterdayâ€“Todayâ€ (1-day Overlap).** Always request from yesterday through today. Ensures catching late news from yesterday; duplicates on yesterday can be detected by idempotency.
- **Option 3: â€œ2-Day Overlapâ€ (Safer but More Duplicates).** Query last 2 days (e.g. day before yesterday through today). Catches very late arrivals, but duplicates risk grows.
- **Option 4: â€œRolling Fixed Windowâ€ (e.g. 3 days daily).** Always last 3-day block. Similar tradeoff.

**Weekly News Updates:**

- **Option A: Calendar Week (Monâ€“Sun).** Scheduled on Monday (or next business day) covering previous full week. Aligns with natural week but may skip Monday if holiday.
- **Option B: Last7Days Overlap.** On each weekly run, fetch last 7 days (maybe Wedâ€“Tue if running Wed). Overlaps heavily but safe.
- **Option C: â€œLast Successful Weekâ€ from logs.** Compute last fetch boundary from manifest, request onward to today. Similar to daily Option 1 but at week cadence.

**Daily OHLCV Updates:**

- **Option I: Trading Days Only.** Request all trading days since last fetch. Typically â€œyesterday through todayâ€ if markets open. Skip weekends/holidays.
- **Option II: Calendar Days + Skip Non-trading.** Always fetch yesterdayâ€“today, but skip any known non-trading days (calendar aligned).
- **Option III: Overlap with Buffer (e.g. last 2 trading days).** Fetch last 2 trading days to handle holidays and late data.

**Weekly OHLCV Updates:**

- **Option X: Last 5 Trading Days.** E.g. on Monday fetch Fri-Wed. Accounts for weekends, ensures no gap.
- **Option Y: Calendar Week adjusted.** Fetch Mondayâ€“Friday of last calendar week. If holiday, detect missing date.
- **Option Z: Rolling 7-Day Window Overlap.** Always fetch last 7 calendar days but filter trading days.

**Edge Cases to Handle (Examples):**

- **Weekends/Holidays:** OHLCV: skip; News: fetch through Monday to include weekend news if any.
- **Market-close Timezone Ambiguity:** Define â€œtodayâ€ cutoff as market close local time (e.g. 4pm NYT), but requests in UTC. Avoid assuming 00:00 UTC aligns.
- **Late-arriving data:** If provider updates yesterdayâ€™s news today, overlapping window helps catch it. Avoid assuming timestamp == market-close.
- **Clock drift:** Allow short â€œgraceâ€ overlap (few hours) for intraday runs.
- **Duplicate Risk:** Manage via duplicate-detection (next section).

**Scheduling Recommendations:**

- **Daily News:** Use **â€œyesterday through todayâ€** by default (Option 2). This is conservative enough to catch late newsã€3â€ L39-L47ã€‘ã€31â€ L289-L296ã€‘ while only duplicating 1 day's data.
- **Weekly News:** Use **full 7-day window** (Option B) or calendar week with overlap. For example, if running each Monday, fetch previous Tuesdayâ€“Monday (7-day block). This covers weekend news and mid-week holidays.
- **Daily OHLCV:** Use **â€œyesterday through todayâ€** (Option I) but with logic to skip weekends/holidays. If executed on Monday, cover Fridayâ€“Monday.
- **Weekly OHLCV:** Fetch **last 5 trading days** or **7 calendar days** covering last week. A practical approach: on Monday run, fetch up to last Friday (including partial Monday if available).

**Example Recommendation:**
- Daily scripts default to `--start-date = manifest_last_date - 1 day`, `--end-date = today`, with a flag to treat weekends specially.
- Weekly scripts default to last 7 calendar days (or last 5 trading days), aligning with manifests.

This balances **completeness** vs **duplication**. Overlap of 1â€“2 days catches late news while allowing idempotent deduplication. Excess overlap (3+ days) adds complexity in deduplication and manifest size. Minimal overlap risks missing late items.

**Scheduling Options Comparison:**

| Option        | How it Works                              | Correctness (completeness) | Duplication Risk | Late-arrival tolerance | Implementation Complexity | Testing Ease | Recommended? | Why |
|---------------|-------------------------------------------|----------------------------|------------------|------------------------|--------------------------|--------------|--------------|-----|
| No Overlap (LastCutoffâ†’Today) | Set start = last manifest end + 1, end = today | May miss late-arrivals or run-late updates (low completeness) | Low (no overlap) | Poor (if provider lags, missed) | Simple (use manifest date) | Easy | Rejected | Too aggressive; misses dataã€3â€ L39-L47ã€‘. |
| 1-Day Overlap | Start = yesterday, End = today           | Good (catches yesterdayâ€™s late updates) | Moderate | Good | Moderate (need dedup) | Moderate | **Recommended** | Good balance; common strategy. |
| 2-Day Overlap | Start = day-before-yesterday, End = today | Very high completeness | High | Very good | Higher (dedup needed) | Moderate | Consider only if needed | Safe but more duplicates. |
| Weekly Anchored Calendar | Align to Monâ€“Sun, or Tueâ€“Mon depending | Good if aligned, but gaps on holidays | Low-mid | Medium (week recalc) | Medium (week logic) | Medium | Possible (with caution) | Intuitive but need holiday logic. |
| Last7Days (rolling) | Start = today-7, End = today           | Similar to 1â€“2 day overlap strategy | Moderate-high | Good | Easy (fixed window) | Easy | Recommended | Consistent window; simpler logic. |
| Monthly/quarterly | Larger batch (monthly)               | Highest completeness long-run | Highest duplication | Best for catching late items | Hard (large retries) | Hard | No for daily/weekly | Too coarse for frequent refreshes. |

*Evidence:* No direct repo evidence for specific window logic; choices are *inferred from design goals* (provider-safety, idempotency)ã€3â€ L39-L47ã€‘. We classify these as *â€œPlausible but unverifiedâ€*, requiring testing with actual data.

**Scheduling Edge Cases:**
- If **today is weekend/holiday**, for OHLCV skip or carry to next trading day. E.g. if Sunday, daily OHLCV does nothing (Empty run).
- If provider data for â€œyesterdayâ€ arrives late, our overlap catches it.
- **Partial data** (running before market close): design default to include current day (maybe partial), note in manifest. Could require config to decide (e.g. always â€œas-of yesterdayâ€ by default).
- **Timezones:** Convert all dates/times to UTC for requests, but interpret â€œas-of-closeâ€ (e.g. 4pm NY). Avoid assuming timestamps line up exactly.
- **No new data:** If nothing new (weekend news etc.), manifest should show 0 new files. Warn user â€œno new dataâ€; do not error.
- **Clock drift:** Compare local vs server time; allow small offset.

---

## 3. Duplicate Avoidance & Idempotency

Idempotency is critical: repeated runs must not re-download or corrupt data inadvertently.

**Plan Mode:** Should detect existing raw files and *not* plan them again. The plan manifest should mark existing targets as â€œskippedâ€ã€31â€ L289-L296ã€‘.

**Live Mode:** Before downloading each file, check if an identical file already exists. Options:
- Existence by filename (simple)
- Check content hash (more robust)
- Check provider timestamp/ID in previous manifest.

We recommend **content-hash + manifest check**:
- Always compute a hash (or metadata signature) of any existing raw file and compare with new data.
- The manifest can track *previous provider timestamps* or identifiers (e.g. news article ID) to detect duplicatesã€3â€ L39-L47ã€‘.
- For news, duplicate detection at *article-ID level* and for OHLCV at *ticker-date* level is needed.
- If a provider returns same content in different order (likely for news), sorting or canonicalizing JSON before hashing preserves deterministic comparisons (needs implementation)ã€31â€ L283-L291ã€‘.

**Repeated runs (same end-date):** Should yield identical plan; if nothing changed, plan manifest identical (deterministic). Live mode should simply skip existing files without error.

**After a failed run:** On a subsequent live run, only missing/failed files should be retried, not re-fetch all. The manifest should include status for each target (planned, skipped, done, failed) to resume safely.

**Duplicate Detection Levels:**
- **Raw-file level:** Check if file path exists and hash matches. Quick skip.
- **Article-ID level (news):** If same news item appears in multiple windows, use an ID key (from payload) to skip duplicates across files.
- **Ticker-Date level (OHLCV):** If price data already fetched for a date, skip re-fetch.
- **Manifest-level:** Use manifest entries to avoid planning whatâ€™s already done.

**Idempotency Invariants:**
1. **Plan determinism:** Given same manifest and inputs, plan manifest must be identical (deterministic order)ã€31â€ L281-L290ã€‘.
2. **No silent overwrite:** If `--overwrite` is not set, existing files are never modified or replaced.
3. **Same-run idempotency:** Running live mode again with no changes results in â€œall skippedâ€ (no network calls).
4. **Failure recovery:** If a file fails partway, retry it only next time, and mark failure in manifest.

**Failure-recovery Strategy:**
- On errors (timeout, partial payload), **do not** delete partial raw files. Mark them â€œfailedâ€ in manifest, log error.
- A subsequent run with `--execute` should detect incomplete/failed files (e.g. missing or flagged in manifest) and attempt to fetch them again if within end-date.

**Manifest Fields (for idempotency):**
- `planned_entries`: list of all requested items (ticker/date or article-id).
- `skipped_existing_entries`: targets not fetched due to existing files.
- `completed_entries`: successfully downloaded entries.
- `failed_entries`: targets that encountered errors.
- `ambiguous_empty_count/entries`: targets where provider returned no data (might not be an error).
- `duplicate_entries`: (optional) items skipped due to being detected duplicates.

Each entry record could include: ticker, date/article-id, target path, content hash, status.
In manifest, record counts of planned/skipped/completed/failed, as in Stage8Prompt recommendationsã€3â€ L39-L47ã€‘.

**Strategy Summary:** Always compute and record content hashes for raw files. Use manifest to track history. Only download if not present (or if `--overwrite`). Ensure ordering of manifest entries is deterministic (sort by ticker/date).

*Evidence:* The existing design mandates no overwrite by default and redaction of duplicatesã€31â€ L281-L290ã€‘. We cite Stage8Prompt (idempotency, no-overwrite)ã€3â€ L39-L47ã€‘. Specific dedup logic is â€œinferred from current designâ€ and best practices, not explicitly coded yet (Unknown).

---

## 4. Provider Quotas, Rate Limits, and Errors

We must **not hardcode** fragile quotas. Instead, use documented limits with fallbacks.

- **Alpha Vantage:** Free tier is *approximately* 5 calls/minute and 25 calls/day (Supported by external sourcesã€19â€ L232-L240ã€‘). Official docs mention 5/min, but users report 25/day limitã€19â€ L232-L240ã€‘.
- **Twelve Data:** Free tier appears to allow ~8 API calls/minute (as per community reports)ã€27â€ L287-L295ã€‘. Daily or monthly limits are unclear publicly; assume modest usage and handle 429s.
- **Exponential Backoff:** For rate-limit (HTTP 429), use a capped exponential backoff (e.g. start with 1s, doubling up to, say, 60s) with a small max retry count to avoid endless loops.
- **Script Flags:** Scripts should allow configuring `--max-calls`, `--sleep-seconds`, `--timeout-seconds`, `--max-tickers` to throttle usage. By default, `--max-calls=1` (plan only) and backoff=none (plan-only mode). Live mode requires explicit higher budgets.

**Errors & Retries:**
- **429 (Too Many Requests):** Likely rate-limit. Catch and **retry** after backoff. Represent as â€œrate limit exceededâ€ in manifest.
- **5xx / Timeout / Connection errors:** Possibly transient. Retry a few times (max ~3) with backoff, then fail.
- **Malformed JSON / Empty response:** If provider returns an error message in JSON, classify it (e.g. "Service error"). If truly empty (no articles/prices), treat as â€œno-dataâ€ rather than crash.
- **No-data vs Error:** A legitimate empty (e.g. no news returned) should be logged but not treated as failure. Only 5xx, timeouts, or explicit â€œlimit exceededâ€ messages should be failures.
- **Hide vs Expose:** **Avoid hiding errors**. Do not ignore 5xx permanently; bubble up to manifest. But allow limited retries so a blip doesnâ€™t abort the entire run.

**Manifest Error Fields:**
- `provider_error_summary`: e.g. counts of 429s, timeouts, parse errors.
- For each failed entry, record HTTP status, error code/message snippet (redacted).
- `rate_limit_policy` and `retry_policy` strings describing strategy used.

**Strategy Table:**

| Option              | How it Works                        | Correctness | Reproducibility | Secret-leakage Risk | Provider-safety (quota) | Ease of testing | Failure Behavior | Recommended? | Why |
|---------------------|-------------------------------------|-------------|-----------------|---------------------|-------------------------|-----------------|------------------|--------------|-----|
| **Fail-Fast:** Fail on first 429/5xx (no retry) | Quick feedback of limit hit or service issue | Low robustness (data lost) | Reproducible (no nondet retries) | N/A | High safety (avoids extra calls) | Easy (fail quick) | Terminates run, user must rerun | Rejected | Too brittle; likely to fail entire run for temporary issue. |
| **Limited Retry (preferred):** Few retries with backoff, then fail | On error, retry 2-3 times; record error if still failing | Moderate (some transient successes) | Partially non-deterministic (timing) | Low risk | Medium safety (some extra calls) | Moderate | Partial failures logged; run continues for other tickers | Recommended | Balances robustness and control. |
| **Aggressive Retry:** Unlimited / long-run retries on failure | Keep retrying until success or daily limit | High completeness if issue resolves | Very nondeterministic | Moderate (many calls) | High risk (could exhaust quota) | Hard | Very slow, may deadlock on persistent error | Rejected | Too risky (quota/excess time). |

We classify **Limited Retry** as recommended. It avoids silent data loss but caps API usage. For each failed fetch, manifest logs the failure; run continues with other tickers.

*Evidence:* Official docs warn of rate-limits but do not detail error codesã€19â€ L232-L240ã€‘. Retry design follows general best practices and the scriptsâ€™ existing design (the guidebook mentions redacted ledger and rate-limit control in `stage8_data_update_common.py`ã€31â€ L283-L291ã€‘).

---

## 5. Raw Preservation & No-Overwrite Policy

Raw payloads must be **immutable** once written (unless explicitly overwritten with care)ã€3â€ L39-L47ã€‘.

- **Path Convention:** Store raw AlphaVantage news as `data/raw/alphavantage/{ticker}/{YYYYMMDD_HHMMSS}.json` (timestamp of retrieval) or `{ticker}/{YYYY-MM-DD}.json`. OHLCV as `data/raw/twelvedata/{ticker}/{date}.json`. Including a timestamp or hash in filename prevents collisions.
- **Naming Schema:** Use canonical ticker names (dotted tickers stored as filenames or with underscore)ã€3â€ L39-L47ã€‘.
- **Raw ID:** For example, `ticker_AAPL__2025-12-01T17:00:00Z.json` or include content hash suffix.
- **Manifests vs Executions:** Keep separate: a plan manifest (metadata) and an execution manifest. If executing, write new manifest or append to plan.
- **Collisions:** If a new fetch target corresponds to an existing file path (by name) but different content, *do not overwrite* unless `--overwrite`. Instead:
  - If `--overwrite` **not** given: skip and log â€œskipped-existingâ€. Manifest note.
  - If `--overwrite`: either refuse (stop with error), or backup old file (e.g. rename to `.bak` with timestamp) before writing. Better: require explicit flag and warn user, but if allowed, create a backup copy with clear suffix and log it.

- **Metadata in Files:** Preserve source URL (without API key). Eg, `source: "https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey=REDACTED&tickers=AAPL..."` in manifest, not raw. In raw file, we may not need to store URL.
- **Redact Secrets:** In any saved URLs or parameters, remove API key valuesã€29â€ L53-L58ã€‘. E.g. `https://api.twelvedata.com/time_series?symbol=AAPL&apikey=XXXXXXXX` => redact.

- **Shareable ledgers:** The request ledger should avoid storing full URLs with keys (see next section). Raw manifests may store query params minus key.

- **Hashing:** Compute and store a hash (SHA256) of each raw file after download. Keep it in manifest for change detection.

*Output Summary:*
  - Use immutable raw file naming by ticker+datetime or content-hash.
  - Default is skip-existing; `--overwrite` needs careful user override (backup old, log).
  - Always remove keys from stored URLsã€29â€ L53-L58ã€‘ã€31â€ L283-L291ã€‘.

*Evidence:* Stage8Prompt explicitly requires â€œraw preservation, no overwrite unless `--overwrite`â€ã€3â€ L39-L47ã€‘. The guidebook notes no-overwrite default and redacted ledgersã€31â€ L281-L290ã€‘. We follow those rules.

---

## 6. Redaction, Secrets, and Shareable Ledgers

**Allowed in stdout:** Only non-sensitive info. **Forbidden:** API keys, tokens, `.env` file paths or contents.

- **Stdout:** Should never show raw URLs with keys, or any environment variables. Only summary of actions.
- **Committed Manifests:** Never include raw URLs with keys. If source/endpoint must be noted, omit `apikey` (or use placeholder). E.g. `"url": "https://...&apikey=REDACTED"`. Instead, include a separate field `"params":{"apikey":"<redacted>","function":"NEWS_SENTIMENT",...}`.
- **Shareable Ledgers:** The raw request ledger (JSONL) should never contain full URLs with keys. It may log endpoint and query parameters in a JSON object with the key value replaced by `"<REDACTED>"` or omitted.
- **.env files:** Never appear in logs or manifests. If a path to .env is printed, redact actual path (just mention `.env`).

**Redaction Technique:**
- Strip or replace any regex matching `apikey=[^&]+` or `token=`.
- Split query strings into JSON with `"api_key": "<REDACTED>"`.
- For logged requests, use provider aliases (e.g. "AlphaVantage") not URLs where possible.

**Retrofitting:** For existing ledgers that may contain keys, consider a one-time migration to redact. Future runs must produce *freshly* redacted logs.

**Separate Logs:** Keep a private debug log (not committed) that can contain full unredacted info for debugging. The shareable ledger (committed) must have keys redacted.

**Testing Redaction:**
- A unit test should scan sample URLs/ledgers to ensure no API keys leak (e.g. regex check on output files).
- Print a warning if writing a manifest that includes sensitive values.

**User Warning:** On sharing logs or manifests, explicitly print:
> **Warning:** Do not share this file without removing API keys. Sensitive fields are redacted, but double-check for secrets.

*Evidence:* Stage8Prompt specifies â€œRedact API keys from stdout, logs, ledgersâ€ã€3â€ L43-L47ã€‘ and UsageManual warns against committing keysã€29â€ L53-L58ã€‘. Our design follows these (Supported by repository rules).

---

## 7. Manifest Schema Design

We propose a comprehensive manifest JSON schema. Example fields (with types and description):

- `schema_version` (string) â€“ manifest schema identifier. **Mandatory**.
- `created_at_utc` (ISO datetime) â€“ creation timestamp. **Mandatory**.
- `provider` (string) â€“ e.g. `"AlphaVantage"`.
- `endpoint` (string) â€“ e.g. `"NEWS_SENTIMENT"` or `"time_series"`.
- `cadence` (string) â€“ `"daily"` or `"weekly"`.
- `execute` (bool) â€“ whether this was a live execution.
- `approved_live_execution` (string or bool) â€“ git hash or note of approval.
- `approved_overwrite` (string or bool) â€“ approval note if overwrite happened.
- `universe_source` (string) â€“ e.g. `"data/universe/top50.csv"`.
- `universe_digest` (string) â€“ hash of universe CSV.
- `ticker_count` (int) â€“ how many tickers attempted.
- `support_tickers` (array) â€“ e.g. `["SPY"]` if used.
- `start_date`, `end_date` (ISO date) â€“ request window.
- `request_window_policy` (string) â€“ description of how `start_date` was chosen (e.g. "yesterday-overlap").
- `planned_count` (int), `skipped_existing_count`, `completed_count`, `failed_count`, `ambiguous_empty_count` (ints).
- `planned_entries`, `skipped_existing_entries`, `completed_entries`, `failed_entries`, `ambiguous_empty_entries`: lists of entry records. Each entry might be an object with keys: `ticker`, `date_or_id`, `target_path`, `status`, and possibly `notes` or `error` fields.
- `raw_write_policy` (string) â€“ e.g. `"no-overwrite"`.
- `overwrite_policy` (string) â€“ e.g. `"explicit-flag"`.
- `secret_policy` (string) â€“ e.g. `"apikey-redaction"`.
- `rate_limit_policy`, `retry_policy` (string) â€“ descriptions.
- `provider_error_summary` (string or object) â€“ count of 429s, etc.
- `changed_raw_files`, `changed_raw_file_hashes` (list of filenames and new hashes) â€“ track any overwritten files if applicable.
- `unchanged_raw_files` (list) â€“ files skipped.
- `newest_provider_timestamp`, `oldest_provider_timestamp` â€“ if available from payload metadata.
- `refresh_impact_note` (string) â€“ textual summary e.g. â€œStage2â€“Stage6 must rebuild (dataset changed)â€.
- `stage2_to_stage6_invalidation` (bool or list) â€“ which stages stale.
- `stage7c_invalidation` (bool) â€“ if 7C diagnostics invalid.
- `stage10c_historical_packet_warning` (string) â€“ e.g. â€œStage10C outputs are historicalâ€ if needed.
- `benchmark_non_claims`, `prediction_non_claims`, `trading_non_claims`, `provider_completeness_non_claims` (strings) â€“ standardized non-claim text from docs.

**Plan-mode vs Live-mode:**
- Plan-mode manifest excludes execution details (no completed_count, no ledger path) but includes planned_entries.
- Live-mode manifest includes actual `completed_count`, `skipped_existing_count`, etc.
- Mandatory fields (plan): schema_version, created_at_utc, provider, endpoint, cadence, approved_live_execution=false, approved_overwrite=false, universe_source/digest, ticker_count, start_date, end_date, planned_count, planned_entries, raw_write_policy.
- Mandatory fields (live): all above plus executed flags true, completed/skipped/failed counts, and error summary.

**Deterministic fields:**
- schema_version, provider, endpoint, universe_source/digest, start/end dates, request window policy, planned_entries (assuming sorted), ticker_count.
- Non-deterministic: execution times, newest/oldest provider timestamps (depend on data), maybe order of failed entries if timing differences.
- If a field is missing that is critical (e.g. `start_date`, `end_date`), the script should abort â€“ those block rebuilds.

Example (YAML-like) manifest skeleton:

```
schema_version: "1.0"
created_at_utc: "2026-05-23T19:12:00Z"
provider: "AlphaVantage"
endpoint: "NEWS_SENTIMENT"
cadence: "daily"
execute: false
approved_live_execution: false
approved_overwrite: false
universe_source: "configs/universe_top50.csv"
universe_digest: "abc123..."
ticker_count: 50
support_tickers: ["SPY"]
start_date: "2026-05-21"
end_date: "2026-05-23"
request_window_policy: "yesterday-through-today with weekend skip"
planned_count: 48
skipped_existing_count: 0
completed_count: 0
failed_count: 0
ambiguous_empty_count: 0
planned_entries:
  - {ticker: "AAPL", date: "2026-05-22", target: "data/raw/alphavantage/AAPL/20260522.json"}
  - ...
skipped_existing_entries: []
completed_entries: []
failed_entries: []
raw_write_policy: "immutable"
overwrite_policy: "no-overwrite by default"
secret_policy: "redact-apikey"
rate_limit_policy: "max_calls=5 per minute default"
retry_policy: "retries=3, backoff=exp capped at 60s"
provider_error_summary: {}
changed_raw_files: []
changed_raw_file_hashes: []
unchanged_raw_files: []
newest_provider_timestamp: "2026-05-22T23:50:00Z"
oldest_provider_timestamp: "2026-05-21T00:15:00Z"
refresh_impact_note: "Dataset changed: re-run Stages2-6"
stage2_to_stage6_invalidation: true
stage7c_invalidation: true
stage10c_historical_packet_warning: "No fresh forecasts; historical only"
benchmark_non_claims: "Data changes do not produce a new benchmark"
prediction_non_claims: "No new predictions generated"
trading_non_claims: "No trading signals or price targets"
provider_completeness_non_claims: "Provider news coverage not guaranteed"
```

*Evidence:* Many fields are drawn from Stage8Prompt requirements (counts, entries, policies)ã€3â€ L39-L47ã€‘. Non-claim fields echo UsageManual non-claimsã€29â€ L15-L22ã€‘. The schema is **inferred** from requirements (Plausible) and existing manifest patterns.

---

## 8. Request Ledger Design

We suggest using **JSONL (one JSON object per line)** for the request ledger for ease of appending and parsing. Each entry should include:

- `timestamp` (UTC ISO) of request start/end.
- `provider` and `endpoint` (no key).
- `params` (object) including all query parameters with keys **excluded** or redacted (e.g. `"apikey":"<REDACTED>"`).
- `status_code` (int), `response_type` (â€œjsonâ€/â€œcsvâ€), `response_path` (file written).
- `content_hash` (SHA256) of response body (or `null` if no content).
- `content_size` (bytes).
- `error_code` and `error_message` if any (short summary, redacted).

Example safe entry (redacted):

```json
{"timestamp": "2026-05-23T19:12:15Z",
 "provider": "AlphaVantage",
 "endpoint": "NEWS_SENTIMENT",
 "params": {"tickers": "AAPL,MSFT", "limit": 50, "apikey": "<REDACTED>"},
 "status_code": 200,
 "response_type": "json",
 "response_path": "data/raw/alphavantage/AAPL/20260523.json",
 "content_hash": "f3a5...","content_size": 34567}
```

**Failed request example:**

```json
{"timestamp": "2026-05-23T19:13:10Z",
 "provider": "TwelveData",
 "endpoint": "TIME_SERIES",
 "params": {"symbol": "SPY", "interval": "1min", "apikey": "<REDACTED>"},
 "status_code": 429,
 "error": "API limit exceeded",
 "attempts": 1}
```

Fields forbidden in ledger: full URLs with API keys, OAuth tokens, raw response content. Allowed only in **private debug logs**: full error stack traces, full raw JSON for inspection.

*Evidence:* The design follows secure logging best practices and Stage8 requirements (redacted ledgers)ã€3â€ L43-L47ã€‘ã€31â€ L283-L291ã€‘.

---

## 9. Invalidation & Rebuild Semantics

After a raw update, we must warn which downstream artifacts are stale.

**Principle:** Any change to raw data implies that **Stages 2â€“6 must be rerun** to maintain integrityã€3â€ L39-L47ã€‘ã€11â€ L166-L174ã€‘. Stage 7C diagnostics also become historical.

- **Stage 2:** Stale whenever any raw ticker-date is added/changed (news or OHLCV) because dataset rows may change.
- **Stage 3:** Stale if Stage 2 changed, or new news might affect features/labels (e.g. a new event date).
- **Stage 4â€“6:** All stale because new data violates the previously saved benchmark packet.
- **Stage 7C:** Diagnostics tied to old data become outdated; warn that they are historical (no live trading).
- **Stage 10C:** *Always* historical. If raw data changed, existing Stage10C outputs are stale. We should label them `historical_prediction` and *not* call them forecasts.

**Distinctions:**
- **Raw news vs OHLCV change:** Both invalidate the dataset. Possibly, new news might not change dataset rows if it falls outside labels windows, but we assume safe side: rebuild.
- **Universe unchanged:** If only news added (no new tickers), still Stage2 (dataset) changes due to more features/labels.
- **No change run:** If live run resulted in 0 changed files, minimal warnings: maybe â€œNo data changed; existing artifacts remain valid.â€

**Warning Texts (examples):**

- *Plan-only:*
  > **Plan OK:** Data-update plan generated. No data fetched. **No downstream changes yet.** Running this plan live later may require rebuilding Stages 2â€“6.

- *Live run, files changed:*
  > **Update Applied:** Fetched X news and Y price files. **Stage 2â€“6 are now stale.** Rebuild pipeline from Stage 2 (dataset) to incorporate new data. Stage 7C diagnostics are now historical only (no live signals). Stage 10C outputs are historical predictions; do not interpret them as fresh forecasts.

- *Live run, no changes:*
  > **No New Data:** No new raw files were fetched. Existing artifacts remain valid. No stages need rebuilding.

- *Partial failure:*
  > **Partial Update:** Some data could not be fetched (see manifest for errors). **Stage 2â€“6 incomplete.** You must rerun after resolving errors or data will be missing.

- *Raw overwrite (with flag):*
  > **WARNING:** Raw overwrite enabled. Existing files will be replaced. This is **destructive**. Confirm approval. Overwritten data may break reproducibility.

- *Quota exhaustion (if e.g. some files skipped):*
  > **Rate Limit Hit:** Provider rate-limit encountered. Some tickers may not have been updated. You may need to adjust throttle flags and retry.

**Invalidation Matrix (illustrative):**

| Condition                   | Stage 2 | Stage 3 | Stage 4 | Stage 5 | Stage 6 | Stage 7C       | Stage 10C | Required Warning                          |
|-----------------------------|:-------:|:-------:|:-------:|:-------:|:-------:|:-------------:|:---------:|:-----------------------------------------|
| **Plan-only run**           | No      | No      | No      | No      | No      | No            | No        | *â€œPlan created; no downstream effects.â€*  |
| **Live, no files changed**  | No      | No      | No      | No      | No      | No            | No        | *â€œNo new data; no rebuild needed.â€*       |
| **Live, news changed**      | Yes     | Yes     | Yes     | Yes     | Yes     | Yes (stale)   | Yes (stale)| *â€œNews added: rebuild Stages2â€“6. 7C/10C historic.â€* |
| **Live, OHLCV changed**     | Yes     | Yes     | Yes     | Yes     | Yes     | Yes (stale)   | Yes (stale)| *â€œPrices added: rebuild Stages2â€“6. 7C/10C historic.â€* |
| **Live, news & OHLCV changed** | Yes  | Yes     | Yes     | Yes     | Yes     | Yes           | Yes       | *â€œData added: rebuild Stages2â€“6. 7C/10C historic.â€* |
| **Partial live run**        | Partial | Partial | Partial | Partial | Partial | Possibly stale | Possibly historical | *â€œPartial fetch: incomplete data; rebuild only after fix.â€* |
| **Failed live run**        | No (incomplete) | No | No | No | No | No | No | *â€œRun failed; no changes applied.â€* |
| **Raw overwrite**           | Yes     | Yes     | Yes     | Yes     | Yes     | Yes           | Yes       | *â€œData overwritten: rebuild everything.â€* |
| **Universe file changed**   | Yes     | Yes     | Yes     | Yes     | Yes     | Yes           | Yes       | *â€œUniverse changed: rebuild pipeline.â€*  |
| **Provider stack changed**  | Yes     | Yes     | Yes     | Yes     | Yes     | Yes           | Yes       | *â€œProvider change: rebuild all stages.â€*  |
| **Support ticker changed**  | Yes     | Yes     | Yes     | Yes     | Yes     | Yes           | Yes       | *â€œSupport ticker updated: rebuild all stages.â€* |
| **Clean-window changed**    | Yes     | Yes     | Yes     | Yes     | Yes     | Yes           | Yes       | *â€œClean window updated: rebuild all stages.â€* |

(*Yes* = artifact stale).

*Evidence:* The Stage8 design mandates a â€œrefresh impact noteâ€ of which stages need rebuildã€3â€ L43-L47ã€‘. The matrix rules come from ExecutionPipeline logic and Stage 8 prompt languageã€3â€ L43-L47ã€‘. Stage10C prompt explicitly requires marking packets as historical if upstream changes happenã€1â€ L2-L8ã€‘.

---

## 10. Stage 10C Compatibility Rules

- **Historical Only:** Any existing Stage 10C outputs (packets) remain strictly *historical predictions*ã€1â€ L28-L36ã€‘. Do not label them as "forecasts" or imply real-time use, because no new model inference has run with updated data.
- **Packet Metadata:** In the Stage 8 manifest or in an index file, flag each Stage 10C packet with the Stage 5 (saved-predictions) cutoff date it was derived from. This allows detecting staleness (if raw data has a later date than that cutoff, the packet is outdated).
- **No Auto-Regeneration:** If raw data is refreshed, do **not** trigger Stage 10C pipeline automatically. Future prediction packets require a full rebuild of features/models (Stages 2â€“6) on new data, then fresh inference (future scope).
- **Differentiating Semantics:** Keep using `role="historical_prediction"` for these outputsã€1â€ L28-L36ã€‘. Reserve any `forecast_candidate` label for truly new forecasts (requires separate approval and model retraining).
- **Manifest Flag:** Add a manifest field, e.g. `raw_data_cutoff_used`, for Stage 10C packet. Stage 8 refresh manifest can compute if newer raw file date > cutoff; if so, flag the 10C packet as stale.
- **Staleness Reaction:** When validating Stage 10C (`validate_stage10c_completion.py`), if it sees raw-data stamps beyond packetâ€™s cutoff, emit a warning: *â€œWarning: Raw data is newer than saved predictions. Current outputs are historical; to generate new forecasts, rebuild from Stage 2.â€*

*Evidence:* Stage10CPrompt stresses preserving old packets as historical onlyã€1â€ L28-L36ã€‘. Stage10B/10C decisions explicitly forbid treating them as live forecastsã€1â€ L1-L8ã€‘. Our rules follow that policy (Supported by repository docs).

---

## 11. Approval Gates & Stop Conditions

Per AgentRules and Scope decisions, the following **must** remain gated:

| Action                                     | Allowed?                      | Approval Required?       | Stop Behavior                             |
|--------------------------------------------|-------------------------------|--------------------------|-------------------------------------------|
| Live provider calls (`--execute`)          | **No** (by default)           | Yes (explicit flag + approval) | Refuse to proceed without `--execute` plus log statement. |
| Raw overwrites (`--overwrite`)             | **No** (default off)          | Yes                      | Abort run with error unless `--overwrite` plus approval. |
| Changing providers (news/OHLCV APIs)       | **Never in Stage8**           | Yes (new Stage scope)    | Stop, user must re-init scope.           |
| Universe expansion (beyond top50)          | **No**                        | Yes (ScopeDecision)      | Stop with message; update requires new benchmark policy. |
| Including SPY as data member (new)         | **No**                        | Yes                      | Stop; SPY only allowed as existing support. |
| Changing SEC role or data                  | **No** (static only)          | Yes                      | Stop; out of scope for raw refresh.       |
| Benchmark-family changes/comparisons       | **No**                        | Yes                      | Stop; refresh alone is not a new benchmark run. |
| Rebuilding Stages 2â€“6 automatically        | **No (auto)**                 | Yes (per pipeline rules)| Stop; user must run Stage2-6 CLIs explicitly after review. |
| Stage6 reinterpretation                    | **No**                        | Yes                      | Stop; Stage6 outputs are fixed for current data. |
| Stage7C final training                     | **No**                        | Yes                      | Stop; cannot produce live signal.         |
| Stage10C inference packaging               | **No**                        | Yes                      | Stop; only historical output allowed.     |
| New `forecast_candidate` semantics         | **No** (not yet used)         | Yes                      | Stop; not allowed without new approval.   |
| New service/API/dashboard endpoints        | **No** (CLI only)             | Yes                      | Stop; out of scope.                      |
| Trading/buy-sell signals                   | **No**                        | Yes                      | Stop; explicitly disallowed (non-claim).  |
| Sharing raw ledgers/logs with secrets      | **Never**                     | N/A                      | Stop; warn user, abort shareable output.  |

**Stop Behavior:** On encountering an unauthorized condition, the script should exit with a non-zero status and a clear message referencing the needed approval (per Stage8 `Stop Conditions`)ã€3â€ L73-L75ã€‘.

*Evidence:* AgentRules and Stage8Prompt list these gates explicitlyã€3â€ L73-L75ã€‘ã€14â€ L99-L108ã€‘. We label them clearly (Confirmed in governance docs).

---

## 12. Threat Model (Summary)

Key threats and mitigations:

- **Secret Leakage:** Raw logs or manifests containing API keys. *Mitigation:* Strict redaction policy (no keys in shared outputs)ã€3â€ L43-L47ã€‘ã€29â€ L53-L58ã€‘.
- **Silent Overwrite:** Accidentally replacing raw data. *Mitigation:* No-overwrite default, explicit flag with backups, manifest logging of overwritesã€3â€ L39-L47ã€‘.
- **Partial Failures:** Some tickers fail mid-run, leading to incomplete data. *Mitigation:* Log partial failures, do not remove old data, alert user, require re-run to fill gaps.
- **Quota Exhaustion:** Blindly hitting rate limits stopping execution. *Mitigation:* Throttle controls, backoff strategy, cap `--max-calls` (by default 1 per ticker)ã€31â€ L283-L292ã€‘.
- **Duplicate Data:** Fetching the same article twice (if overlap windows). *Mitigation:* Idempotency checks (hashes, entry IDs).
- **Stale Artifacts:** Forgetting to rebuild after data change. *Mitigation:* Explicit invalidation warnings, block downstream use until rebuild.
- **False Benchmark Refresh:** Treating raw refresh as a new benchmark run. *Mitigation:* Non-claim disclaimers in manifests, no automatic metrics calculation.
- **False Prediction Refresh:** Confusing Stage10C historical output for new forecast. *Mitigation:* Packet-warning templates (â€œhistorical onlyâ€)ã€1â€ L28-L36ã€‘.
- **Overclaim of Completeness:** Assuming all news covered by provider. *Mitigation:* Non-claims stating â€œno completeness guaranteeâ€ in manifests.
- **Timezone Ambiguity:** Misaligning local vs UTC. *Mitigation:* Define explicit UTC windows, document policy, use known market close cutoff.
- **Non-determinism:** Random ordering or timing differences. *Mitigation:* Always sort manifest entries by key (ticker/date), use fixed seeds for any random order.
- **Universe Drift:** Accidentally adding/removing tickers. *Mitigation:* Never modify universe file without approval; always load from approved source.
- **Downstream stale Stage10C:** Stage10C outputs used as if live. *Mitigation:* Packet metadata and validation to prevent misinterpretation.

Each threat above should be addressed in code and documentation (and unit tests).

---

## 13. Failure-Mode Analysis (Examples)

- **Network Failure (AlphaVantage timeout):** Could happen anytime. Likelihood moderate; damage moderate (missing data). Detected by HTTP timeout/error. Retrying limited times can recover. Manifest records failure. Warning to user â€œprovider error â€“ incomplete update.â€ Unit test: simulate `requests.get` timeout and assert it is recorded.

- **Rate-limit (HTTP 429):** Occurs if calls too frequent. Likely under heavy load. Missing data or skipping. Mitigation: backoff and limited retries; eventual â€œfailedâ€ log. Warning: â€œAPI rate limit reached; try slower pace.â€ Test: mock a 429 response on first call.

- **Duplicate Filenames:** If raw path scheme collides (e.g. re-run same day). Risk low if we use timestamps. If happens without overwrite flag: script will skip file (idempotent). If overwrite flag: replaced file, record in manifest. User warned of destructive action. Test: create dummy file, run without overwrite, expect skip.

- **Late-Arriving News:** If news for T given on day D arrives on D+1, then a no-overlap schedule misses it. Severity: high (miss data). Overlap schedule catches it. Detection: comparing date fields in manifest vs current content. Prevention: use overlap strategy.

- **Manifest Write Failure:** Disk full or permission error. The script must abort before silent data loss. Rare, but verify file creation. Test: simulate read-only filesystem, expect error message.

- **Secret Leak in Log:** If redaction fails, logs contain key. Impact high. Detection by test scanning for patterns. Prevent by regex removal of keys. We include redaction tests.

*(More failure modes can be itemized similarly; each should have detection and prevention plans as above.)*

---

## 14. Testing Plan

We propose tests for all critical functionality. Example entries:

| Test Name                         | Type       | Purpose                                        | Fixture                         | Expected Result                                  | Catches                  | Required? |
|-----------------------------------|------------|------------------------------------------------|---------------------------------|--------------------------------------------------|--------------------------|-----------|
| `test_plan_mode_no_network_calls` | Unit       | Ensure plan mode makes no HTTP calls.          | `--execute=False`             | Plan manifest printed, no ledger file created    | Accidentally running live| Yes       |
| `test_skip_existing_file`         | Unit       | Existing raw file is not re-downloaded.        | Place dummy raw for AAPL/2026-05-22 | Plan shows skip; live mode still skips with no overwrite. | Overwriting data by bug| Yes       |
| `test_duplicate_article_detect`   | Unit       | Duplicate news by ID is caught.               | Two entries with same article ID  | Only one file planned/downloaded                 | Duplicates in news      | Yes       |
| `test_idempotent_manifest_order`  | Unit       | Manifest entries sorted deterministically.    | Random ticker order input         | Manifest entries sorted by ticker/date           | Nondet manifest order   | Yes       |
| `test_rate_limit_retry_logic`     | Mock       | Handle HTTP 429 with retry/backoff.           | Mock HTTP 429 then 200           | One retry then success recorded in manifest error summary. | Retry code missing     | Yes       |
| `test_redaction_on_ledger`        | Unit       | No API keys appear in JSONL ledger.           | Ledger entry with real URL       | All `apikey` fields are "<REDACTED>"             | Secret leakage         | Yes       |
| `test_no_overwrite_without_flag`   | CLI        | Overwrite requires flag.                     | Existing file, run without `--overwrite` | Script exits or skips, no file change           | Unintentional overwrite | Yes       |
| `test_manifest_schema_validation` | Unit       | Manifest contains mandatory fields.           | Example manifest JSON            | Validator passes, missing field raises error     | Schema drift           | Yes       |
| `test_request_ledger_schema`      | Unit       | JSONL ledger fields format.                  | Example JSONL lines              | All entries parsed with expected keys           | Format errors in ledger | Yes       |
| `test_idempotency_repeat_run`     | CLI        | Repeat same live run yields no changes.        | Run live twice with same data     | 2nd run manifest shows 0 new files               | Duplicate downloads    | Yes       |
| `test_SPY_support_ticker_handling`| Unit       | SPY only used as support (OHLCV) not added.   | Universe exclude SPY; include-spy flag | SPY prices fetched only if `--include-spy`; SPY not added as universe. | Wrong universe change | Yes |
| `test_universe_preservation`      | Unit       | Universe file not modified.                   | Universe CSV read                | No changes to universe; script errors if asked beyond top-50 | Universe drift         | Yes       |
| `test_refresh_impact_note`        | Unit       | Correct note given when data changed.         | New data in run                   | Manifest has â€œStage2-6 staleâ€ note              | Missing warning text    | Yes       |
| `test_stage10c_stale_warning`     | Unit       | Warn if raw newer than Stage5 cutoff.        | Raw date > saved preds date       | Output â€œhistorical onlyâ€ warning on CLI          | Forget stale flag     | Yes       |
| `test_approval_gate_stop`         | CLI        | Running live without approval fails.          | No `--execute` flag              | Exit code non-zero, message about approval needed. | Bypassing flag        | Yes       |

Each test should specify required input data (e.g. sample raw dir), expected manifest content, etc. All tests are required before approving implementation.

---

## 15. Open Questions

**Blocking:**
- Exact daily/weekly windows policy: Should weekends be included for news? Need final decision from domain expert.
- Twelve Data free daily quota: Official value unknown. We should verify or ask for subscription level.
- How to handle partial-day news: e.g. if run at 3pm, include same-day? Confirm expectation.

**Important but not Blocking:**
- Overwrite behavior: Should we automatically backup old raw files or just abort?
- Retry defaults: Number of retries and delays.
- SPY support: Confirm if including SPY (flag) is needed for price ratios or volume context.

**Future Enhancement:**
- Adaptive schedule based on actual news volume or Slack metrics.
- Dashboard for monitoring provider usage.
- Automatic incremental dataset build on minor news addition (once approved).

**Out of Scope:**
- Live streaming or webhooks for news/price updates.
- Changing the top-50 universe (explicitly disallowed)ã€5â€ L13-L16ã€‘.
- Using LLM or external summarization for news.

---

## 16. Final Recommendation

We recommend implementing **plan-first, overlapping window refresh scripts** as above. The key next approval checkpoint is for *live execution and overwrite behavior* â€“ no live calls or destructive actions should be permitted without explicit user flags and recorded approval (stop conditions above). The implementation boundary is the existing CLI/artifact model: only scripts and manifests change. Non-claims to include in all outputs: no new benchmark or predictions, no trading signals, no completeness guaranteesã€29â€ L15-L22ã€‘ã€3â€ L39-L47ã€‘. The highest-risk issue is ensuring **idempotent deduplication**: we must robustly detect duplicates (by content-hash or IDs) and test it thoroughly.

**Non-Claims (must be explicitly stated):**
- *No provider calls* in plan mode; live calls only with explicit approval.
- *No raw overwrites* without `--overwrite`.
- *No benchmark or prediction* outputs are generated by data refresh.
- *No Stage 6 reinterpretation.*
- *Stage 10C outputs are historical only,* not fresh forecasts.
- *No trading signals or profitability metrics.*
- *No completeness guarantee* on news coverage.

Implementing these guardrails ensures we stay within approved scopeã€3â€ L39-L47ã€‘ã€1â€ L28-L36ã€‘.
