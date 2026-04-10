Alpha Vantage CLI Usage

Purpose

This file records the Alpha Vantage news-download CLI commands added and used in the legacy snapshot, plus the important generated files and operational notes needed to continue the backfill safely.

Scope

- provider: Alpha Vantage
- endpoint: NEWS_SENTIMENT
- current use case: AAPL deep historical download and top-50/top-100 universe backfill preparation

Relevant environment variable

- `ALPHAVANTAGE_API_KEY`

Relevant source files added or updated

- `src/data/alphavantage_client.py`
- `src/data/alphavantage_backfill_utils.py`
- `src/cli/download_alphavantage_aapl_news.py`
- `src/cli/download_alphavantage_news_backfill.py`

Relevant frozen universe files added

- `data/raw/universe/top50_slickcharts_2026-04-10.csv`
- `data/raw/universe/top100_slickcharts_2026-04-10.csv`

Primary output locations

- raw provider directory:
  - `data/raw/alphavantage/`
- per-ticker raw files:
  - `data/raw/alphavantage/<TICKER>/news_sentiment__<start>__<end>.json`
- request ledger:
  - `data/raw/alphavantage/news_request_ledger.parquet`
- call classification logs:
  - `data/raw/alphavantage/call_status__<scope>.json`
- truncated-call logs:
  - `data/raw/alphavantage/truncated_calls__<scope>.json`

Command 1. Deep historical AAPL download

Use this to download Alpha Vantage NEWS_SENTIMENT history for AAPL year by year, stopping at the daily call limit or at the earliest available history.

```text
python -m src.cli.download_alphavantage_aapl_news --ticker AAPL --max-calls 25 --years-back 20 --sleep-seconds 15
```

Observed result from the executed run

- historical coverage reached back to `2010-01-05`
- newest visible item reached `2026-04-09`
- total successful calls before daily-limit stop: `24`
- total raw rows across downloaded files: `12,244`
- unique articles by `(title, time_published, url)`: `10,500`

Important note

- Alpha Vantage rejected requests earlier than `2010-01-01`
- some recent windows hit the `1000` row limit and are therefore truncated

Command 2. Rebuild AAPL status and truncation logs without spending new API calls

Use this after a previous AAPL run to classify existing windows and regenerate the status logs.

```text
python -m src.cli.download_alphavantage_aapl_news --ticker AAPL --max-calls 0
```

What this does

- does not call the API
- scans existing downloaded windows
- classifies each planned window as:
  - `already_done_complete`
  - `already_done_truncated`
  - or `pending`
- writes:
  - `data/raw/alphavantage/call_status__AAPL.json`
  - `data/raw/alphavantage/truncated_calls__AAPL.json`

Current truncated AAPL windows

- `2025-01-01 -> 2025-12-31`
- `2026-01-01 -> 2026-04-09`

Command 3. Backfill a frozen ticker universe

Use this to backfill Alpha Vantage news for a frozen universe file.

Top 50 example:

```text
python -m src.cli.download_alphavantage_news_backfill --universe-file "data/raw/universe/top50_slickcharts_2026-04-10.csv" --years-back 10 --max-calls 25 --sleep-seconds 15 --resume
```

Top 100 example:

```text
python -m src.cli.download_alphavantage_news_backfill --universe-file "data/raw/universe/top100_slickcharts_2026-04-10.csv" --years-back 10 --max-calls 25 --sleep-seconds 15 --resume
```

What this command does

- loads the explicit frozen universe CSV
- plans one yearly window per ticker for the requested horizon
- checks whether a call has already been done by looking at the expected raw JSON path
- classifies each window before making a new request
- skips already-downloaded windows by default
- records new requests in the provider ledger
- writes scope-level logs:
  - `data/raw/alphavantage/call_status__<scope>.json`
  - `data/raw/alphavantage/truncated_calls__<scope>.json`

Command 4. Force redownload of existing windows

Use only if you explicitly want to ignore the skip logic and redownload windows that already exist.

Top 50 example:

```text
python -m src.cli.download_alphavantage_news_backfill --universe-file "data/raw/universe/top50_slickcharts_2026-04-10.csv" --years-back 10 --max-calls 25 --sleep-seconds 15 --force-redownload
```

Warning

- this will spend API calls again for windows that already have raw files
- do not use unless there is a specific reason

Command 5. Daily-limit test run on the top-50 universe

This was attempted immediately after the AAPL historical run.

```text
python -m src.cli.download_alphavantage_news_backfill --universe-file "data/raw/universe/top50_slickcharts_2026-04-10.csv" --years-back 10 --max-calls 25 --sleep-seconds 15 --resume
```

Observed result

- stopped immediately on `NVDA`
- no new calls were made
- reason: Alpha Vantage daily free-tier quota was already exhausted by the previous AAPL run

Practical operational rule

- do not assume a new backfill can begin the same day after a large AAPL run
- use the classification-only rerun style or wait for the daily reset

How call classification works

For each planned `(ticker, time_from, time_to, sort, limit)` window:

- if the raw JSON file exists and has `rows < limit`
  - classify as `already_done_complete`
- if the raw JSON file exists and has `rows >= limit`
  - classify as `already_done_truncated`
- if the file does not exist
  - classify as `pending`
- if a new request succeeds and returns `rows < limit`
  - classify as `downloaded_complete`
- if a new request succeeds and returns `rows >= limit`
  - classify as `downloaded_truncated`
- if the API signals a daily/rate limit
  - classify as `rate_limited`
- if the request fails for another reason
  - classify as `request_failed`

How truncation logging works

Every run scope gets two JSON logs:

1. `call_status__<scope>.json`
- complete classification of all seen windows

2. `truncated_calls__<scope>.json`
- only the windows whose `rows_returned >= limit`
- use this file to decide what to split later into quarters or months

Recommended next-step workflow

1. Run or resume the yearly backfill for the chosen universe.
2. Inspect `call_status__<scope>.json`.
3. Inspect `truncated_calls__<scope>.json`.
4. Split only truncated windows into smaller windows later.
5. Do not redownload complete windows.

Important practical notes

- Alpha Vantage free tier is rate-limited and daily-limited.
- The current commands use a conservative `15` second sleep between calls.
- Some high-news windows for large-cap names will truncate at `1000` results.
- The current backfill scripts are raw-layer only; they do not yet normalize Alpha Vantage news into the existing interim news pipeline.

Current known generated files for AAPL

- `data/raw/alphavantage/AAPL/news_sentiment__2010-01-01__2010-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2011-01-01__2011-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2012-01-01__2012-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2013-01-01__2013-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2014-01-01__2014-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2015-01-01__2015-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2016-01-01__2016-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2017-01-01__2017-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2018-01-01__2018-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2019-01-01__2019-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2020-01-01__2020-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2021-01-01__2021-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2022-01-01__2022-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2023-01-01__2023-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2024-01-01__2024-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2025-01-01__2025-03-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2025-01-01__2025-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2025-04-01__2025-06-30.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2025-07-01__2025-09-30.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2025-10-01__2025-12-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2026-01-01__2026-01-31.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2026-01-01__2026-04-09.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2026-02-01__2026-02-28.json`
- `data/raw/alphavantage/AAPL/news_sentiment__2026-03-01__2026-03-31.json`

Summary

- already-done windows are now explicitly classified and skipped
- truncated windows are now written into a dedicated log file
- the root-level CLI usage and continuation workflow are now documented here
