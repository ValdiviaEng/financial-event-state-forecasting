# Execution Flow

This document is the practical runbook for the current repository.

It is based on the current implemented code and the current project constraints described in:
- `README.md`
- `Complete_guidebook.txt`
- `execution_plan.txt`

Important scope note:
- This is the exact flow supported by the **current codebase**.
- Where the repository does **not** yet provide a dedicated CLI, this document uses explicit Python snippets that call implemented modules directly.
- The project does **not** use a SQL database. The storage layer is parquet/JSON/manifest based.

Important provider note:
- Twelve Data timings are heavily constrained by free-tier credits per minute.
- Finnhub timings are plan-dependent.
- SEC timings are usually fast and not the bottleneck.
- Hardware estimates below use an `Intel i9` + `RTX 5070 Ti` reference, but API-bound steps depend much more on provider rate limits than on CPU/GPU.

## 0. Current reality and constraints

Before running anything, keep these current limitations in mind:

- Market data comes from `Twelve Data`.
- News comes from `Finnhub`.
- Company KB comes from `SEC EDGAR`.
- Split-event sourcing is still manual/provider-agnostic in practice.
- There is **no dedicated CLI yet** for:
  - split-event ingestion,
  - adjusted-price batch generation across many tickers,
  - article embedding cache building,
  - event-state batch generation.
- Those steps are still fully supported, but currently require Python snippets.
- The current training flow does **not** require the company-KB branch unless you later add numeric `company_` features to the final panel.

## 1. One-time setup

### 1.1 Enter WSL and activate the recommended environment

```bash
cd ~/1_Projects/AA/event-state-forecasting
source ~/venvs/ai/bin/activate
```

- Estimated time: `< 5 seconds`

If you start from Windows Terminal / PowerShell:

```bash
wsl
cd /home/berserker/1_Projects/AA/event-state-forecasting
source ~/venvs/ai/bin/activate
```

- Estimated time: `< 10 seconds`

### 1.2 Install or refresh dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

- Estimated time: `2-10 minutes` if most packages are already present
- Estimated time: `10-25 minutes` on a fresh environment
- Notes:
  - `torch` and `sentence-transformers` dominate install time if not already present.
  - If your local CUDA/Torch setup differs, verify manually before changing PyTorch.

### 1.3 Create the canonical directory tree

```bash
make create-dirs
```

- Estimated time: `< 5 seconds`

### 1.4 Verify required local files exist

The current codebase expects these to exist already:
- `data/raw/universe/latest_universe_snapshot.csv`
- `data/raw/universe/pilot10.csv`
- local `.env`

Check them:

```bash
python - <<'PY'
from pathlib import Path

required = [
    Path('.env'),
    Path('data/raw/universe/latest_universe_snapshot.csv'),
    Path('data/raw/universe/pilot10.csv'),
]

missing = [str(path) for path in required if not path.exists()]
if missing:
    raise SystemExit(f"Missing required local files: {missing}")

print('Required local files are present.')
PY
```

- Estimated time: `< 5 seconds`

## 2. Pre-flight validation gates

These are the recommended checks before any real provider-backed work.

### 2.1 Tooling sanity checks

```bash
python -m compileall src
ruff check src tests
```

- Estimated time: `5-20 seconds`

### 2.2 Run all offline tests only

```bash
pytest tests -q --ignore=tests/integration
```

- Estimated time: `1-5 minutes`

### 2.3 Optional: run the fastest grouped checks first

```bash
pytest \
  tests/test_data_contracts.py \
  tests/test_text_normalization.py \
  tests/test_hashing.py \
  tests/test_news_deduplication.py \
  tests/test_dataset_integrity.py -q
```

- Estimated time: `10-40 seconds`

## 3. Prototype flow: pilot10, short-to-medium historical window, fast validation path

This is the recommended first real-data run path.

Recommended prototype choices:
- ticker universe: `data/raw/universe/pilot10.csv`
- market history: a bounded historical window first, or full backfill only for pilot10
- embedding backend: `hashing` first for end-to-end validation speed
- training: `ridge` baseline first, then the first multimodal model

## 3A. Prototype / smoke testing flow (no large external run required)

Run this if you want to validate the implemented system before committing API quota.

### 3A.1 Fast data correctness suite

```bash
pytest \
  tests/test_data_contracts.py \
  tests/test_text_normalization.py \
  tests/test_hashing.py \
  tests/test_news_deduplication.py \
  tests/test_dataset_integrity.py -q
```

- Estimated time: `10-40 seconds`

### 3A.2 Temporal safety suite

```bash
pytest \
  tests/test_alignment.py \
  tests/test_leakage.py \
  tests/test_walk_forward.py \
  tests/test_research_integrity.py -q
```

- Estimated time: `15-60 seconds`

### 3A.3 Modeling and evaluation suite

```bash
pytest \
  tests/test_baseline_training.py \
  tests/test_multimodal_training.py \
  tests/test_evaluation_tools.py \
  tests/test_ablation_runner.py -q
```

- Estimated time: `30-120 seconds`
- On CPU-only test paths the multimodal tiny-overfit test is the slowest part.

### 3A.4 Full synthetic end-to-end suite

```bash
pytest \
  tests/test_market_pipeline.py \
  tests/test_corporate_actions.py \
  tests/test_news_pipeline.py \
  tests/test_event_state.py \
  tests/test_modeling_dataset.py \
  tests/test_end_to_end_minipipeline.py -q
```

- Estimated time: `30-120 seconds`

## 3B. Prototype real-data end-to-end flow (pilot10)

This is the smallest realistic pipeline flow using your real providers.

### 3B.1 Dry-run market data build on pilot10

```bash
python -m src.cli.build_market_data \
  --pilot-file data/raw/universe/pilot10.csv \
  --start-date 2023-01-01 \
  --end-date 2024-12-31 \
  --max-symbols 10 \
  --dry-run
```

- Estimated time: `2-10 seconds`

### 3B.2 Build raw/interim market data for pilot10 + SPY benchmark

The current training/evaluation path benefits from a benchmark series. The easiest way is to append `SPY` explicitly.

```bash
python -m src.cli.build_market_data \
  --tickers AAPL,AMZN,BF.B,BRK.B,GOOGL,JPM,MSFT,NVDA,UNH,XOM,SPY \
  --start-date 2023-01-01 \
  --end-date 2024-12-31 \
  --max-symbols 11 \
  --run-label pilot_market_2023_2024
```

- Estimated time: `2-5 minutes`
- Main bottleneck: Twelve Data `8 credits/minute`
- One request per symbol for this CLI path

### 3B.3 Prepare split events for pilot tickers

Current codebase requirement:
- You must provide split events manually or from an audited secondary source.
- There is no dedicated split-event CLI yet.

Create a JSON file with canonical fields:

```bash
mkdir -p data/interim/split_events
python - <<'PY'
import json
from pathlib import Path

split_events = [
    {"ticker": "AAPL", "split_date": "2020-08-31", "split_factor": 4.0, "source": "audited_secondary_provider"},
    {"ticker": "NVDA", "split_date": "2021-07-20", "split_factor": 4.0, "source": "audited_secondary_provider"},
]

path = Path("data/interim/split_events/pilot_splits.json")
path.write_text(json.dumps(split_events, indent=2) + "\n", encoding="utf-8")
print(path)
PY
```

- Estimated time: `manual preparation + < 5 seconds to save`
- Uncertain, verify manually:
  - the correctness and completeness of the split list you provide

### 3B.4 Build split-adjusted price files for all pilot tickers and SPY

This uses the current implemented pipeline API directly.

```bash
python - <<'PY'
import json
from collections import defaultdict
from pathlib import Path

from src.data.price_pipeline import MarketPricePipeline
from src.utils.config_loader import load_project_settings

settings = load_project_settings()
pipeline = MarketPricePipeline.from_settings(settings)

split_events = json.loads(Path("data/interim/split_events/pilot_splits.json").read_text(encoding="utf-8"))
by_ticker = defaultdict(list)
for event in split_events:
    by_ticker[event["ticker"]].append(event)

tickers = ["AAPL","AMZN","BF.B","BRK.B","GOOGL","JPM","MSFT","NVDA","UNH","XOM","SPY"]
for ticker in tickers:
    events = by_ticker.get(ticker, [])
    result = pipeline.build_adjusted_prices_for_ticker(
        ticker,
        split_events=events,
        adjustment_source="audited_secondary_provider",
        missing_split_policy="warn_return_raw",
    )
    print(result["ticker"], result["rows_written"])
PY
```

- Estimated time: `10-60 seconds`
- Bottleneck: local parquet read/write, not GPU

### 3B.5 Dry-run Finnhub company-news build on pilot10

```bash
python -m src.cli.build_news_data \
  --pilot-file data/raw/universe/pilot10.csv \
  --start-date 2024-01-01 \
  --end-date 2024-03-31 \
  --chunk-days 30 \
  --max-symbols 10 \
  --dry-run
```

- Estimated time: `2-10 seconds`

### 3B.6 Build raw/interim Finnhub news for pilot10

```bash
python -m src.cli.build_news_data \
  --pilot-file data/raw/universe/pilot10.csv \
  --start-date 2024-01-01 \
  --end-date 2024-03-31 \
  --chunk-days 30 \
  --max-symbols 10 \
  --run-label pilot_news_q1_2024
```

- Estimated time: `2-20 minutes`
- Uncertain, verify manually:
  - actual Finnhub throughput on your current plan
  - exact article counts by ticker/date range

### 3B.7 Optional: build a pilot SEC KB

This is not required for current default baseline or default multimodal training, but it is useful to have.

Create a pilot CIK list file if needed:

```bash
mkdir -p data/raw/sec
cat > data/raw/sec/pilot_ciks.txt <<'EOF'
0000320193
0001018724
0001067983
0001067983
0001652044
0000019617
0000789019
0001045810
0000731766
0000104169
EOF
```

- Estimated time: `manual file creation + < 5 seconds`

Then dry-run or real build:

```bash
python -m src.cli.build_company_kb --cik-file data/raw/sec/pilot_ciks.txt --dry-run
```

- Estimated time: `2-10 seconds`

```bash
python -m src.cli.build_company_kb --cik-file data/raw/sec/pilot_ciks.txt --run-label pilot_kb
```

- Estimated time: `5-30 seconds`

### 3B.8 Build a prototype embedding cache using the fast hashing backend

This is the fastest way to validate the end-to-end pipeline.

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd

from src.features.news_embeddings import build_article_embedding_cache, write_embedding_cache

news_dir = Path("data/interim/news_articles")
frames = [pd.read_parquet(path) for path in sorted(news_dir.glob("*.parquet"))]
articles = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

cache = build_article_embedding_cache(
    articles.to_dict(orient="records"),
    model_id="hashing",
    embedding_dim=32,
    text_variant="headline_plus_summary",
)

output_path = Path("data/embeddings/article_embeddings__hashing.parquet")
write_embedding_cache(cache, output_path)
print(output_path)
PY
```

- Estimated time: `5-30 seconds`

### 3B.9 Build prototype event states from the cache

Important current implementation detail:
- if you want event states for **all market dates**, not only dates with articles, pass `feature_dates` from adjusted price history.

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd

from src.features.event_state import build_daily_event_states

news_frames = [pd.read_parquet(path) for path in sorted(Path("data/interim/news_articles").glob("*.parquet"))]
news = pd.concat(news_frames, ignore_index=True) if news_frames else pd.DataFrame()

embeddings = pd.read_parquet("data/embeddings/article_embeddings__hashing.parquet")

price_frames = [
    pd.read_parquet(path)
    for path in sorted(Path("data/interim/adjusted_prices_daily").glob("*.parquet"))
    if path.stem != "SPY"
]
prices = pd.concat(price_frames, ignore_index=True) if price_frames else pd.DataFrame()
feature_dates = sorted(pd.to_datetime(prices["date"]).dt.date.unique().tolist())

event_states = build_daily_event_states(
    news.to_dict(orient="records"),
    embeddings,
    model_id="hashing",
    lookback_days=20,
    decay_half_life_days=5,
    feature_dates=feature_dates,
)

output_path = Path("data/final/event_states_daily__hashing.parquet")
output_path.parent.mkdir(parents=True, exist_ok=True)
event_states.to_parquet(output_path, index=False)
print(output_path)
PY
```

- Estimated time: `10-60 seconds`

### 3B.10 Build combined adjusted-price and benchmark files for the final panel

The current final-panel CLI expects one adjusted-price file and one optional benchmark file, so you must combine per-ticker outputs first.

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd

adj_dir = Path("data/interim/adjusted_prices_daily")
adj_frames = [pd.read_parquet(path) for path in sorted(adj_dir.glob("*.parquet")) if path.stem != "SPY"]
adjusted = pd.concat(adj_frames, ignore_index=True)
adjusted_path = Path("data/final/adjusted_prices__pilot10.parquet")
adjusted.to_parquet(adjusted_path, index=False)

benchmark = pd.read_parquet(adj_dir / "SPY.parquet")[["date", "close"]].copy()
benchmark_path = Path("data/final/benchmark_SPY__pilot10.parquet")
benchmark.to_parquet(benchmark_path, index=False)

print(adjusted_path)
print(benchmark_path)
PY
```

- Estimated time: `5-20 seconds`

### 3B.11 Build the final modeling panel

```bash
python -m src.cli.build_modeling_dataset \
  --adjusted-prices-path data/final/adjusted_prices__pilot10.parquet \
  --benchmark-path data/final/benchmark_SPY__pilot10.parquet \
  --event-state-path data/final/event_states_daily__hashing.parquet \
  --dataset-version pilot10_hashing_v1
```

- Estimated time: `10-60 seconds`

### 3B.12 Train the first market-only baseline

```bash
python -m src.cli.train_market_baseline \
  --panel-path data/final/modeling_panel__pilot10_hashing_v1.parquet \
  --models ridge \
  --horizons 1,5,20 \
  --train-window 252 \
  --validation-window 63 \
  --test-window 63 \
  --max-splits 1 \
  --run-id baseline_pilot10_hashing_v1
```

- Estimated time: `10-60 seconds`
- If you add `elastic_net`, expect `20-90 seconds`

### 3B.13 Train the first multimodal model

```bash
python -m src.cli.train_multimodal_model \
  --panel-path data/final/modeling_panel__pilot10_hashing_v1.parquet \
  --horizons 1,5,20 \
  --train-window 252 \
  --validation-window 63 \
  --test-window 63 \
  --max-splits 1 \
  --run-id multimodal_pilot10_hashing_v1 \
  --device cuda
```

- Estimated time: `1-10 minutes`
- On your `RTX 5070 Ti`, this should usually be GPU-fast because the event-state branch is already precomputed.

### 3B.14 Evaluate both runs

```bash
python -m src.cli.evaluate_experiments \
  --panel-path data/final/modeling_panel__pilot10_hashing_v1.parquet \
  --run-summary runs/baseline_pilot10_hashing_v1/baseline_training_summary.json \
  --horizons 1,5,20 \
  --output-dir reports/eval_baseline_pilot10_hashing_v1
```

- Estimated time: `5-20 seconds`

```bash
python -m src.cli.evaluate_experiments \
  --panel-path data/final/modeling_panel__pilot10_hashing_v1.parquet \
  --run-summary runs/multimodal_pilot10_hashing_v1/multimodal_training_summary.json \
  --horizons 1,5,20 \
  --output-dir reports/eval_multimodal_pilot10_hashing_v1
```

- Estimated time: `5-20 seconds`

### 3B.15 Run the first ablation-style comparison

```bash
python -m src.cli.run_ablations \
  --run-summaries runs/baseline_pilot10_hashing_v1/baseline_training_summary.json,runs/multimodal_pilot10_hashing_v1/multimodal_training_summary.json \
  --partition test \
  --metric-name rmse \
  --output-dir reports/ablations_pilot10_hashing_v1
```

- Estimated time: `5-20 seconds`

## 4. Full experiment flow: larger subset, real embeddings, full training

This is the recommended path for a serious experiment.

Recommended current scale:
- `30-100` stocks, not all `503`, unless you intentionally accept heavy API time and quota usage
- real sentence-transformer embeddings instead of hashing backend
- multiple splits instead of one split

Important current recommendation from the README and execution plan:
- do **not** jump straight to 503-name live runs before validating a smaller real-data subset
- Twelve Data Basic makes large refreshes quota-bound
- Finnhub throughput remains plan-dependent

## 4A. Prepare the experiment universe file

If you already have a curated 30-100 ticker list, save it as a CSV under `data/raw/universe/experiment50.csv` with a `ticker` column.

If you want to simply use the existing full snapshot file directly, you may pass:
- `data/raw/universe/latest_universe_snapshot.csv`

For a curated experiment subset, the file should look like:

```csv
ticker
AAPL
AMZN
BRK.B
BF.B
MSFT
NVDA
...
```

- Estimated time: `manual preparation`

## 4B. Build market data for the experiment universe + SPY

Example for a curated 50-name subset plus SPY over a deeper range:

```bash
python -m src.cli.build_market_data \
  --universe-file data/raw/universe/experiment50.csv \
  --start-date 2018-01-01 \
  --end-date 2025-12-31 \
  --max-symbols 50 \
  --run-label experiment50_market_2018_2025
```

- Estimated time: `8-20 minutes`
- Main bottleneck: Twelve Data Basic credits/minute
- If you truly use `100` names, estimate `15-35 minutes`
- If you truly use the full current `503` names, estimate at least `~63 minutes` for one-time backfill requests and expect very heavy daily quota use

Then fetch benchmark separately if it was not included in your universe file:

```bash
python -m src.cli.build_market_data \
  --tickers SPY \
  --start-date 2018-01-01 \
  --end-date 2025-12-31 \
  --max-symbols 1 \
  --run-label benchmark_spy_2018_2025
```

- Estimated time: `1-2 minutes`

## 4C. Prepare full split events

Current repository requirement:
- you still need an audited split-event file
- there is still no dedicated live split-event CLI

Recommended file:
- `data/interim/split_events/experiment50_splits.json`

Required schema per row:

```json
{
  "ticker": "AAPL",
  "split_date": "2020-08-31",
  "split_factor": 4.0,
  "source": "audited_secondary_provider"
}
```

- Estimated time: `manual / provider-dependent`
- Uncertain, verify manually:
  - completeness of split coverage for your full ticker subset

## 4D. Build adjusted prices for the experiment universe

```bash
python - <<'PY'
import json
from collections import defaultdict
from pathlib import Path

from src.data.price_pipeline import MarketPricePipeline
from src.utils.config_loader import load_project_settings

settings = load_project_settings()
pipeline = MarketPricePipeline.from_settings(settings)

split_events = json.loads(Path("data/interim/split_events/experiment50_splits.json").read_text(encoding="utf-8"))
by_ticker = defaultdict(list)
for event in split_events:
    by_ticker[event["ticker"]].append(event)

tickers = [
    path.stem for path in sorted(Path("data/interim/prices_daily").glob("*.parquet"))
]

for ticker in tickers:
    events = by_ticker.get(ticker, [])
    result = pipeline.build_adjusted_prices_for_ticker(
        ticker,
        split_events=events,
        adjustment_source="audited_secondary_provider",
        missing_split_policy="warn_return_raw",
    )
    print(result["ticker"], result["rows_written"])
PY
```

- Estimated time: `1-10 minutes`

## 4E. Build Finnhub news for the experiment universe

```bash
python -m src.cli.build_news_data \
  --universe-file data/raw/universe/experiment50.csv \
  --start-date 2023-01-01 \
  --end-date 2025-12-31 \
  --chunk-days 30 \
  --max-symbols 50 \
  --run-label experiment50_news_2023_2025
```

- Estimated time: `10-90 minutes`
- Uncertain, verify manually:
  - exact Finnhub plan throughput
  - article counts across symbols and ranges

For `100` names, estimate `20 minutes to several hours`, depending mostly on provider limits and response volume.

## 4F. Optional: build SEC KB for the experiment universe

If you have a CIK list file:

```bash
python -m src.cli.build_company_kb \
  --cik-file data/raw/sec/experiment50_ciks.txt \
  --run-label experiment50_kb
```

- Estimated time: `10-120 seconds`

## 4G. Build a real embedding cache with the configured sentence-transformer model

Important current implementation detail:
- `build_article_embedding_cache()` currently requires you to provide the true `embedding_dim`.
- For `sentence-transformers/all-MiniLM-L6-v2`, use `384`.
- If you change the model, verify the true output dimension manually first.

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd

from src.features.news_embeddings import build_article_embedding_cache, write_embedding_cache

news_dir = Path("data/interim/news_articles")
frames = [pd.read_parquet(path) for path in sorted(news_dir.glob("*.parquet"))]
articles = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

cache = build_article_embedding_cache(
    articles.to_dict(orient="records"),
    model_id="sentence-transformers/all-MiniLM-L6-v2",
    embedding_dim=384,
    text_variant="headline_plus_summary",
    batch_size=256,
    device="cuda",
)

output_path = Path("data/embeddings/article_embeddings__all-MiniLM-L6-v2.parquet")
write_embedding_cache(cache, output_path)
print(output_path)
PY
```

- Estimated time: `5-30 minutes` for a medium experiment subset on `RTX 5070 Ti`
- Could be much longer if article volume is high

## 4H. Build event states for all market dates in the experiment set

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd

from src.features.event_state import build_daily_event_states

news_frames = [pd.read_parquet(path) for path in sorted(Path("data/interim/news_articles").glob("*.parquet"))]
news = pd.concat(news_frames, ignore_index=True) if news_frames else pd.DataFrame()

embeddings = pd.read_parquet("data/embeddings/article_embeddings__all-MiniLM-L6-v2.parquet")

price_frames = [
    pd.read_parquet(path)
    for path in sorted(Path("data/interim/adjusted_prices_daily").glob("*.parquet"))
    if path.stem != "SPY"
]
prices = pd.concat(price_frames, ignore_index=True) if price_frames else pd.DataFrame()
feature_dates = sorted(pd.to_datetime(prices["date"]).dt.date.unique().tolist())

event_states = build_daily_event_states(
    news.to_dict(orient="records"),
    embeddings,
    model_id="sentence-transformers/all-MiniLM-L6-v2",
    lookback_days=20,
    decay_half_life_days=5,
    feature_dates=feature_dates,
)

output_path = Path("data/final/event_states_daily__all-MiniLM-L6-v2.parquet")
output_path.parent.mkdir(parents=True, exist_ok=True)
event_states.to_parquet(output_path, index=False)
print(output_path)
PY
```

- Estimated time: `1-10 minutes`

## 4I. Build combined adjusted-price and benchmark files for the full panel

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd

adj_dir = Path("data/interim/adjusted_prices_daily")
adj_frames = [pd.read_parquet(path) for path in sorted(adj_dir.glob("*.parquet")) if path.stem != "SPY"]
adjusted = pd.concat(adj_frames, ignore_index=True)
adjusted_path = Path("data/final/adjusted_prices__experiment50.parquet")
adjusted.to_parquet(adjusted_path, index=False)

benchmark = pd.read_parquet(adj_dir / "SPY.parquet")[["date", "close"]].copy()
benchmark_path = Path("data/final/benchmark_SPY__experiment50.parquet")
benchmark.to_parquet(benchmark_path, index=False)

print(adjusted_path)
print(benchmark_path)
PY
```

- Estimated time: `10-60 seconds`

## 4J. Build the final modeling panel for the experiment set

```bash
python -m src.cli.build_modeling_dataset \
  --adjusted-prices-path data/final/adjusted_prices__experiment50.parquet \
  --benchmark-path data/final/benchmark_SPY__experiment50.parquet \
  --event-state-path data/final/event_states_daily__all-MiniLM-L6-v2.parquet \
  --dataset-version experiment50_minilm_v1 \
  --event-state-version minilm_v1
```

- Estimated time: `30-180 seconds`

## 4K. Run the full non-live validation suite before training

```bash
pytest tests -q --ignore=tests/integration
```

- Estimated time: `2-8 minutes`

This is your current “go/no-go” gate before training.

## 4L. Train market-only baselines

Start with `ridge`, then add `elastic_net`, then optionally `market_mlp`.

```bash
python -m src.cli.train_market_baseline \
  --panel-path data/final/modeling_panel__experiment50_minilm_v1.parquet \
  --models ridge,elastic_net \
  --horizons 1,5,20 \
  --train-window 504 \
  --validation-window 126 \
  --test-window 126 \
  --max-splits 3 \
  --run-id baseline_experiment50_minilm_v1
```

- Estimated time: `2-15 minutes`
- Mostly CPU-bound for sklearn baselines

If you also want `market_mlp`:

```bash
python -m src.cli.train_market_baseline \
  --panel-path data/final/modeling_panel__experiment50_minilm_v1.parquet \
  --models market_mlp \
  --horizons 1,5,20 \
  --train-window 504 \
  --validation-window 126 \
  --test-window 126 \
  --max-splits 3 \
  --run-id mlp_experiment50_minilm_v1
```

- Estimated time: `5-25 minutes`
- On `RTX 5070 Ti`, this should be manageable, but dataset size and epochs matter.

## 4M. Train the multimodal model

```bash
python -m src.cli.train_multimodal_model \
  --panel-path data/final/modeling_panel__experiment50_minilm_v1.parquet \
  --horizons 1,5,20 \
  --train-window 504 \
  --validation-window 126 \
  --test-window 126 \
  --max-splits 3 \
  --run-id multimodal_experiment50_minilm_v1 \
  --device cuda
```

- Estimated time: `15-90 minutes`
- Main drivers:
  - row count
  - split count
  - epochs until early stopping
  - event-state dimensionality

## 4N. Evaluate the stored predictions

```bash
python -m src.cli.evaluate_experiments \
  --panel-path data/final/modeling_panel__experiment50_minilm_v1.parquet \
  --run-summary runs/baseline_experiment50_minilm_v1/baseline_training_summary.json \
  --horizons 1,5,20 \
  --output-dir reports/eval_baseline_experiment50_minilm_v1
```

- Estimated time: `10-60 seconds`

```bash
python -m src.cli.evaluate_experiments \
  --panel-path data/final/modeling_panel__experiment50_minilm_v1.parquet \
  --run-summary runs/multimodal_experiment50_minilm_v1/multimodal_training_summary.json \
  --horizons 1,5,20 \
  --output-dir reports/eval_multimodal_experiment50_minilm_v1
```

- Estimated time: `10-60 seconds`

## 4O. Generate ablation comparison tables

```bash
python -m src.cli.run_ablations \
  --run-summaries runs/baseline_experiment50_minilm_v1/baseline_training_summary.json,runs/multimodal_experiment50_minilm_v1/multimodal_training_summary.json \
  --partition test \
  --metric-name rmse \
  --output-dir reports/ablations_experiment50_minilm_v1
```

- Estimated time: `5-20 seconds`

## 5. Optional live provider verification flow

Run only when you want to validate real external provider behavior.

Set the flag first:

```bash
export RUN_LIVE_API_TESTS=true
```

- Estimated time: `< 1 second`

Run the live suites individually:

```bash
pytest tests/integration/test_live_twelvedata.py -q
```

- Estimated time: `30-120 seconds`

```bash
pytest tests/integration/test_live_finnhub.py -q
```

- Estimated time: `30-120 seconds`
- Uncertain, verify manually: response time and article availability depend on plan and date window

```bash
pytest tests/integration/test_live_sec.py -q
```

- Estimated time: `10-60 seconds`

Run them together:

```bash
pytest tests/integration -q
```

- Estimated time: `1-5 minutes`

## 6. Recommended execution order in practice

### For prototyping / smoke validation

1. Activate env
2. Install requirements
3. `make create-dirs`
4. `compileall` + `ruff`
5. `pytest tests -q --ignore=tests/integration`
6. Market CLI dry-run
7. News CLI dry-run
8. KB CLI dry-run
9. Build small real pilot market/news data
10. Create manual split file
11. Build adjusted prices
12. Build hashing embeddings
13. Build event states
14. Build final panel
15. Train `ridge`
16. Train first multimodal model
17. Evaluate both
18. Run ablation comparison

### For full model training

1. Activate env
2. Install requirements
3. Validate universe file(s)
4. Run the full offline suite
5. Build market data for chosen experiment subset + SPY
6. Build or audit split-event file
7. Build adjusted prices
8. Build news data
9. Optional KB build
10. Build sentence-transformer embedding cache
11. Build event states for all market dates
12. Concatenate adjusted-price and benchmark files
13. Build final panel
14. Run offline suite again
15. Train baselines
16. Train multimodal model
17. Evaluate predictions
18. Generate ablation tables
19. Optionally run live provider tests after or before the experiment, not during critical training loops

## 7. Current exact limitations you must account for

These are important because this document is intentionally aligned to the **current implementation**, not to a hypothetical future repo.

- There is no dedicated CLI yet for split-event ingestion.
- There is no dedicated CLI yet for embedding-cache generation.
- There is no dedicated CLI yet for event-state generation.
- There is no automatic universe-to-CIK resolution CLI.
- The company-KB branch is optional and not yet part of the default training flow.
- The final modeling panel builder expects a single adjusted-price parquet file, so multi-ticker adjusted prices must be concatenated first.
- For real sentence-transformer embeddings, you must supply the correct `embedding_dim` manually in the current embedding-cache API.

## 8. Sanity checkpoints you should not skip

Before trusting results, confirm all of the following:

```bash
pytest tests -q --ignore=tests/integration
```

- Estimated time: `2-8 minutes`

Check final panel uniqueness manually if desired:

```bash
python - <<'PY'
import pandas as pd

panel = pd.read_parquet('data/final/modeling_panel__pilot10_hashing_v1.parquet')
dupes = int(panel.duplicated(subset=['ticker', 'date']).sum())
print({'rows': len(panel), 'duplicate_ticker_date_rows': dupes})
PY
```

- Estimated time: `5-15 seconds`

Check that predictions are joinable:

```bash
python - <<'PY'
import pandas as pd

panel = pd.read_parquet('data/final/modeling_panel__pilot10_hashing_v1.parquet')
preds = pd.read_parquet('runs/baseline_pilot10_hashing_v1/predictions/split_0__ridge.parquet')
joined = preds.merge(panel[['ticker','date','y_excess_ret_1']], how='left', on=['ticker','date'])
print({'prediction_rows': len(preds), 'joined_rows': len(joined), 'missing_labels': int(joined['y_excess_ret_1'].isna().sum())})
PY
```

- Estimated time: `5-15 seconds`

## 9. Final guidance

- Use the **prototype flow first**.
- Do not jump directly to a full `503`-ticker live run on Twelve Data Basic unless you explicitly accept the quota/time cost.
- Treat split-event sourcing as a controlled audited step, not an afterthought.
- Prefer hashing embeddings for fast end-to-end debugging, then switch to your real sentence-transformer run once the pilot flow is stable.
- Keep the final evaluation on stored predictions only.

If you follow the order above, you will be aligned with the current implemented repository and the methodology described in `README.md`, `Complete_guidebook.txt`, and `execution_plan.txt`.
