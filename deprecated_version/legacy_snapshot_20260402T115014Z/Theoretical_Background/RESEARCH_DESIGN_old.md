# COMPREHENSIVE RESEARCH DESIGN

## Event-Driven Multi-Modal Multi-Horizon Forecasting

**Version**: 1.0  
**Date**: 2026-03-05  
**Status**: Active Development  

---

## 1. PROBLEM FORMULATION

### 1.1 What We Are NOT Doing

**Price prediction** is the wrong framing because:
- Stock prices contain efficient market information
- Directly predicting prices assumes market inefficiency
- Noise overwhelms predictive signal in high-frequency regime
- Single-point price estimates are brittle and unreliable

### 1.2 What We ARE Doing

**Risk-adjusted return prediction** with the following perspective:

We model an **evolving event state** from temporal sequences of financial news, then use this state plus market features to predict **multi-horizon forward returns** (excess or residual returns).

The research hypothesis is:
> Recent aggregated information from financial news (the "event state") provides complementary predictive signal to market-only features for multi-horizon excess return prediction, particularly when news content density is high.

### 1.3 Core Conceptual Framing

#### Why Event State, Not Individual News Effects?

Financial news overlaps continuously:
- Multiple articles may discuss the same underlying event
- Individual article effects are entangled with market reaction
- Effects decay over time
- Sentiment from isolated articles is unstable

**Event State Alternative**:
- Aggregate recent embeddings using time decay
- Represents evolving semantic state of recent information
- Captures cumulative information effect
- More stable than isolated sentiment scores

#### Why Market-Neutral Returns?

- Market-only model captures systematic risk
- Multimodal model should improve residual (alpha) prediction
- Excess returns isolate the incremental value of news
- Prevents confounding by market regime

#### Why Multi-Horizon?

- Different information types matter at different horizons:
  - 1-day: Immediate market reaction, microstructure
  - 5-day: Sector/momentum effects
  - 20-day: Fundamental repricing
  - 60-day: Longer-term sentiment shifts
- Multi-task learning improves generalization
- Different trading strategies operate at different horizons

---

## 2. RESEARCH QUESTIONS AND HYPOTHESES

### Main Research Question (MRQ)

> Does an aggregated temporal event state computed from financial news headline embeddings improve multi-horizon excess return prediction beyond market-only features?

### Sub-Questions and Hypotheses

#### SQ1: Predictability of Excess Returns
**Question**: Can multi-horizon excess returns be predicted above chance from historical market features?

**Hypothesis (H1a)**: A properly regularized neural network trained on market features alone achieves R² > 0.05 on out-of-sample test set for at least one horizon.

**Why it matters**: Establishes that the prediction task is non-trivial but feasible.

---

#### SQ2: Incremental Value of News Signals
**Question**: Does adding news-derived event state improve prediction beyond market-only baseline?

**Hypothesis (H1b)**: Multimodal model achieves ΔR² ≥ 0.02 improvement on 5-day and 20-day horizons compared to market-only baseline (directional effect: H1b hypothesis is directional, not null).

**Hypothesis (H1c, Conservative)**: If H1b is not supported, check if news helps during high-news-density periods (interaction effect).

**Why it matters**: Core hypothesis - validates that news adds information.

---

#### SQ3: News Signal Stability and Generalization
**Question**: Does news signal remain stable in out-of-sample evaluation and across time periods?

**Hypothesis (H2a)**: Multimodal model maintains consistent ΔR² across walk-forward folds with coefficient of variation < 0.5.

**Hypothesis (H2b)**: Market-neutral residuals from multimodal model have correlation with future residuals consistent with market-only model (i.e., signal doesn't degrade).

**Why it matters**: Tests generalization and robustness.

---

#### SQ4: News Effect Heterogeneity
**Question**: Does news signal vary by market condition, news density, or sector?

**Hypothesis (H3a)**: Multimodal advantage is largest during periods with high news volume (top quintile).

**Hypothesis (H3b)**: Multimodal advantage differs significantly across sectors (ANOVA p < 0.05).

**Why it matters**: Characterizes when the model is most valuable.

---

#### SQ5: Feature Ablations
**Question**: Which news features and aggregation methods are essential?

**Hypothesis (H4a)**: Exponential decay weighting (halflife=7 days) outperforms simple mean aggregation (ΔR² ≥ 0.01).

**Hypothesis (H4b)**: Dense embeddings outperform sentiment-only features (ΔR² ≥ 0.01).

**Hypothesis (H4c)**: Longer history (30 days) outperforms shorter (7 days) for longer horizons only.

**Why it matters**: Guides feature engineering decisions.

---

## 3. LITERATURE REVIEW GUIDANCE

### 3.1 Core Areas to Review

#### A. Multimodal Fusion in Finance
**Key Concepts**: Combining text and market data

**Foundational Papers**:
- Ding et al. (2015): "Deep learning for event-driven stock prediction" - *Propose deep model for news + prices, early work*
- Mohan et al. (2023): "Stock price prediction using LSTM..." - *Baseline comparison for multimodal approaches*

**Verify manually**: Recent survey papers on multimodal ML in finance (2023-2025)

**What to look for**:
- How to fuse text and tabular features
- Feature concatenation vs. attention-based fusion
- Handling temporal alignment

---

#### B. Financial News and Text Analysis
**Key Concepts**: News as predictive signal, sentiment analysis

**Established Methods**:
- Sentiment analysis for returns prediction (Tetlock 2007 - "Giving content to investor sentiment")
- Event detection from news (Groth & Muntermann 2011)
- Novelty in financial text (Mikolov et al. 2013 - general embeddings, but applied to finance)

**Verify manually**:
- Recent work on FinBERT or domain-specific embeddings
- Empirical evidence on news predictability (2020-2025)
- NewsStream and similar datasets

**What to look for**:
- How predictive are different news signals?
- Decline of information value over time
- Cross-sectional vs time-series variation

---

#### C. Time-Series Representation Learning
**Key Concepts**: Learning representations from sequential data

**Relevant Work**:
- Sentence-transformers literature (Reimers & Gupta 2019)
- Temporal aggregation methods
- Decay functions in finance (exponential decay for volatility forecasting)

**What to look for**:
- Pre-trained models suitable for financial text
- Embedding quality metrics
- Temporal pooling methods

---

#### D. Multi-Horizon Forecasting
**Key Concepts**: Predicting multiple time horizons simultaneously

**Key Papers**:
- Sorjamaa et al. (2007): "Methodology for long-term prediction..." - *Multi-horizon approaches*
- Lai et al. (2018): "A review of LSTM for forecasting..." - *Survey on RNNs for multi-step prediction*

**What to look for**:
- Shared representations across horizons
- Multi-task learning benefits
- Horizon-specific vs shared features

---

#### E. Leakage-Aware Financial Evaluation
**CRITICAL AREA**: Most common failure mode

**Key Concepts**:
- Look-ahead bias in financial ML
- Proper time-based validation
- Information leakage from features
- Embargo periods

**Essential Reading**:
- Leitch & Tanner (1991): "Economic forecast evaluation" - *Statistical testing for forecasts*
- Arnott et al. (2016): "How Can 'Big Data' Improve Financial Decision Making?" - *Discusses overfitting in finance*
- Any work on "temporal leakage" in ML

**Verify manually**: Recent papers on leakage in financial ML (2022-2025)

**What to look for**:
- Standard leakage prevention in walk-forward validation
- News embargo periods
- Feature lags
- Proper handling of microstructure

---

#### F. Multi-Task and Multi-Outcome Learning
**Key Concepts**: Learning shared representations for multiple targets

**Foundational Work**:
- Caruana (1997): "Multitask Learning" - *Classic multi-task learning*
- Ma et al. (2017): "Modeling task relationships..." - *Modern multi-task approaches*

**What to look for**:
- Weight sharing across tasks
- Task-specific vs shared layers
- Benefits of joint training

---

### 3.2 Literature Review Checklist

- [ ] **Understand:** Why news might be predictive (market reaction, information asymmetry, behavioral factors)
- [ ] **Understand:** Current SOTA on similar prediction tasks (if any papers exist)
- [ ] **Verify:** Embedding models used in financial NLP (FinBERT, etc.)
- [ ] **Verify:** Public datasets (if any) on news + prices (e.g., RavenPack, Refinitiv)
- [ ] **Review:** Statistical testing for forecasts (significance tests, directional tests)
- [ ] **Review:** Risk-adjusted return metrics (Sharpe, Sortino, etc.)
- [ ] **Document:** All cited papers with relevance explanation

---

## 4. DATASET DESIGN

### 4.1 Price Data

**Source**: Twelve Data (Free Tier / low-cost tier as available)

**Specification**:
- **Type**: Daily OHLCV (Open, High, Low, Close, Volume)
- **Adjusted**: Requested from provider, but local split handling is still required unless verified otherwise
- **Granularity**: Daily (EOD), no intraday
- **Time Coverage**: ~5-10 years (limited by free API)
- **Universe**: 30-100 liquid large-cap US stocks (S&P 500)

**Advantages**:
- Free / accessible with straightforward API usage
- Good daily OHLCV coverage for liquid US equities
- Easy to download
- Reliable for large-cap stocks

**Limitations**:
- **CRITICAL**: Credits-per-minute and requests-per-day limits still require throttling
- **CRITICAL**: Provider-side adjustment behavior must be verified; do not assume split-adjusted history
- No intraday data
- Requires explicit caching strategy
- May have gaps for delisted stocks

**Cleaning Protocol**:
1. Check data continuity (flag gaps > 5 trading days)
2. Detect outliers (returns > 10σ) → investigate or remove
3. Adjust for corporate actions (verify against other sources)
4. Remove tickers with < 3 years continuous data
5. Forward-fill only up to 1 day missing (drop longer gaps)

**Validation**:
- Compare closing prices with Yahoo Finance or other source on spot check
- Verify splits/dividends against company reports
- Log all cleaning decisions

---

### 4.2 Market Benchmark Data

**Source**: Twelve Data or Yahoo Finance (free fallback, if needed)

**Specification**:
- **Ticker**: ^GSPC (S&P 500 Index)
- **Granularity**: Daily
- **Use**: Market-neutral feature computation and label creation

**Optional Sector Data**:
- Sector ETFs (XLK, XLV, XLF, etc.) if sector analysis needed
- **Not critical** but useful for benchmarking

---

### 4.3 News Data

**Source**: Finnhub (Free Tier)

**Specification**:
- **Type**: Headline text only (not full articles)
- **Granularity**: Event timestamps (typically when published)
- **Coverage**: ~500k+ articles across covered tickers
- **Language**: English only

**Advantages**:
- Free tier available
- Covers major news sources
- Includes timestamps
- Easy API

**Limitations**:
- **CRITICAL**: Free tier has data retention limit (may lose older articles)
- **CRITICAL**: Rate limiting (60 calls/minute)
- Headline-only (no article body)
- May have duplicate articles from different sources
- No explicit sentiment/entities

**Collection Protocol**:
1. Fetch news in chunks (ticker-by-ticker, date-range-by-date-range)
2. Store raw JSON response with download timestamp
3. Deduplicate headlines (same content, different source)
4. Filter very short articles (< 5 words)
5. Validate timestamps and tickers
6. Log collection errors and missing data

**Data Quality Checks**:
- Verify timestamp formats and timezone
- Check ticker mapping (does "AAPL" in news match our AAPL in prices?)
- Spot-check articles with known events
- Log articles per ticker per day (detect anomalies)

---

### 4.4 Optional: Sentiment/Metadata

**Not critical for Phase 1** but useful for comparisons:
- Reuters Refinitiv (commercial, often available through institutions)
- Alternative data vendors: FactEur, AlternativeData.org
- Academic datasets: RavenPack (requires subscription)

**If including sentiment**:
- Use only as auxiliary validation (not main features)
- Don't rely on third-party sentiment (compute your own)
- Verify sentiment against actual returns (sanity check)

---

### 4.5 Universe Definition

**Selection Criteria**:
1. **S&P 500 constituents**: Ensure institutional relevance and news coverage
2. **Market cap** >= $10B: Avoid micro-cap noise and delisting risk
3. **Average daily volume** >= $1M: Ensure liquidity
4. **Data coverage** >= 90%: Require mostly complete historical data
5. **Final count**: Target 50 stocks (top ~10% by market cap)

**Implementation**:
```
1. Load S&P 500 constituents list
2. Fetch rolling volume from Twelve Data and verify any market-cap filter source manually
3. Apply filters
4. Check data availability (count trading days in date range)
5. Sort by market cap, select top N
6. Validate: tickers, dates, coverage
7. Save universe to reproducible list (use version control)
```

**Rationale**:
- Large caps have most news coverage (reduce missing data risk)
- Reduce microstructure noise
- Improve model stability
- Realistic for institutional use

---

### 4.6 Alignment and Leakage Prevention

#### News-to-Price Alignment

**Critical**: News published at time T cannot be used to predict price at time T or T+1.

**Protocol**:

```
News published: 2023-01-15 14:00 (2 PM ET)
Market close:   2023-01-15 16:00 (4 PM ET)
Embargo end:    2023-01-17 16:00 (2 days later, 4 PM ET)

Can use for predictions: 2023-01-18 onwards
```

**Implementation**:
1. Parse news timestamp (handle timezones)
2. For each price date T, include news from [T - embargo_days - lookback_days, T - embargo_days)
3. **Validate**: For every training observation, assert news_date + embargo_days <= price_date
4. Log any violations

---

## 5. LABEL DESIGN

### 5.1 Primary Labels: Forward Excess Returns

**Definition**:
$$r_i(t, h) = \text{forward_return}_i(t, h) - r_{\text{market}}(t, h)$$

Where:
- $r_i(t, h)$ = excess return for stock $i$ over horizon $h$ days starting at date $t$
- forward_return = $\frac{P_i(t+h) - P_i(t)}{P_i(t)}$ (simple returns)
- $r_{\text{market}}(t, h)$ = S&P 500 return over same period

**Horizons**: 1-day, 5-day, 20-day, optionally 60-day

**Why excess returns**:
- Isolate alpha (relative performance) from beta (market)
- Market-only model should capture beta
- Multimodal model can improve alpha prediction
- More stable and interpretable than raw returns

**Advantages**:
- Regression target (continuous)
- Directly interpretable (daily excess alpha)
- Suitable for MSE/Huber loss
- Compatible with ranking metrics

**Implementation**:
```python
def compute_excess_returns(prices_df, market_returns_series):
    stock_forward_returns = {}
    for horizon in [1, 5, 20]:
        stock_fwd = (prices_df['close'].shift(-horizon) / prices_df['close'] - 1)
        excess = stock_fwd - market_returns_series[horizon_days]
        stock_forward_returns[f'excess_{horizon}d'] = excess
    return stock_forward_returns
```

---

### 5.2 Secondary Labels: Direction Classification

**Definition**:
$$y_i(t, h) = \begin{cases} 1 & \text{if } r_i(t, h) > 0 \\ 0 & \text{otherwise} \end{cases}$$

**Use case**:
- Binary classification loss (BCE, focal loss if imbalanced)
- Directional accuracy metric
- Ranking evaluation

**Class balance**:
- Expected: ~50% class distribution (by construction)
- Check: Report class distribution per horizon
- If imbalanced: Use focal loss or sample weighting

---

### 5.3 Tertiary Labels: Ranking/Quantile

**Definition**:
For each date $t$, rank stocks by excess return within the universe:
$$\text{rank}_i(t) = \text{percentile of } r_i(t, h) \text{ within universe}$$

**Bins**:
- Top decile: 1 (best performers)
- Bottom decile: 0 (worst performers)
- Middle: NaN or separate class

**Use case**:
- Ranking metrics (Spearman, NDCG)
- Information ratio calculation
- Portfolio construction

---

### 5.4 Optional: Risk Labels

**Downside capture**: How much downside does stock capture when market goes down?

**Formula**:
$$\beta_{down} = \frac{\text{Cov}(r_i, r_m | r_m < 0)}{\text{Var}(r_m | r_m < 0)}$$

**Use case**:
- Understanding risk characteristics
- Auxiliary evaluation metric (not primary)
- Risk-stratified subgroup analysis

---

## 6. FEATURE ENGINEERING

### 6.1 Market Features (Primary: Market-Only Model)

#### OHLCV Transforms
```
Raw inputs: open, high, low, close, volume (daily)

Features:
1. Close-to-close returns (1d, 5d, 20d)
2. High-low range: (high - low) / open
3. Volume ratio: volume_t / mean(volume_last_20d)
4. Volatility: std(log returns, window=20)
5. Trend: (close - SMA_20) / SMA_20
```

**Implementation approach**:
- Compute on rolling windows
- All features use only past data (no look-ahead)
- Standardize before feeding to model
- Handle NaN: forward-fill up to 5 days, then drop

---

#### Technical Indicators (Optional, Phase 1.5)
```
RSI(14), MACD(12,26,9), Bollinger Bands, ATR(14)
```

**Caution**: Technical indicators are derived from past prices
- May introduce multicollinearity
- Should be regularized
- Include in ablation study: "with/without technical indicators"

---

#### Market Regime Features
```
1. S&P 500 return (1d, 5d): Context for stock return
2. Market volatility (VIX proxy): std(market returns, 20d)
3. Market momentum: (close - SMA_200) / SMA_200
```

**Rationale**: Stock behavior depends on market context

---

### 6.2 News Features (News-Only Model)

#### News Embeddings
```
1. Generate embeddings using sentence-transformers:
   - Model: all-MiniLM-L6-v2 (384-dim, fast)
   - or all-mpnet-base-v2 (768-dim, slower, higher quality)
   
2. Normalize to unit norm
```

**Why pre-trained embeddings**:
- Transfer learning from general English
- Captures semantic meaning without training
- Efficient computation
- Good generalization

---

#### Event State Aggregation
```
For each (date, ticker), aggregate recent news embeddings:

event_state(t, ticker) = Σ_i [ w_i * embedding_i ]

where:
- i indexes news articles
- w_i = exp(-λ * (t - t_i)) / Z  [exponential decay]
- λ = ln(2) / halflife  [decay rate]
- Z = normalization constant
- t_i = publication date
- lookback_days = 30 (max history to consider)
- halflife = 7 days (tunable parameter)
```

**Intuition**:
- Recent articles weighted more heavily
- Older articles gradually fade
- Halflife = 7 days means 7 days old gets 50% weight
- 30 days old gets ~5% weight

**Implementation**:
```python
def event_state_decay(embeddings, timestamps, reference_date, halflife=7):
    decay_lambda = np.log(2) / halflife
    days_ago = (reference_date - timestamps).days
    weights = np.exp(-decay_lambda * np.maximum(0, days_ago))
    weights /= weights.sum()
    return weights @ embeddings
```

---

#### Alternative Aggregation Methods (Ablation)

**1. Simple Mean (Baseline)**:
```
event_state = mean(embeddings in lookback window)
```
- No decay
- Equal weight to all articles
- Simpler interpretation

**2. Attention-Weighted (Optional, Advanced)**:
```
- Learn attention weights during model training
- More flexible but adds parameters
- Requires more data to avoid overfitting
```

---

### 6.3 Novelty and Importance Features (Optional)

**Novelty Score**:
- Recent articles similar to recent past = not novel
- Dissimilar articles = novel
- Compute: novelty_i = 1 - mean_similarity(embedding_i, last_N_embeddings)

**News Density**:
- Number of articles per day for ticker
- High density = market attention
- Use as weighting or separate feature

**These are OPTIONAL** - start without them, add if beneficial in ablation.

---

### 6.4 Feature Scaling

**Critical**: Fit scaler ONLY on training data

**Method**:
```
StandardScaler:
- X_scaled = (X - mean) / std
- Fit on train set
- Apply same transform to val, test
- Refit fresh for each walk-forward fold
```

**Implementation**:
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)
```

---

### 6.5 Feature Engineering Priority

#### MUST DO (Phase 1):
1. ✅ Forward returns (all horizons)
2. ✅ Market features: returns, volume ratio, volatility
3. ✅ News embeddings (pre-trained)
4. ✅ Event state aggregation (exponential decay)
5. ✅ Market regime: S&P returns, market vol
6. ✅ Proper scaling and NaN handling

#### STRONGLY RECOMMENDED (Phase 1.5):
7. ⭕ Technical indicators (test impact)
8. ⭕ Market-neutral residuals (regress stock on market)
9. ⭕ Sector features (if sector data available)

#### OPTIONAL (Phase 2+):
10. ⭕ Novelty scores (news dissimilarity)
11. ⭕ News density (article count)
12. ⭕ Sentiment scores (if using FinBERT)
13. ⭕ Topic modeling on news

---

## 7. MODEL ARCHITECTURE

### 7.1 Staged Development Plan

#### Stage 1: Simple Baselines (Sanity Check)
**Goal**: Establish that the task is non-trivial

- **Model A**: OLS regression on market features
  - Linear baseline, no hyperparameter tuning
  - Simple, interpretable
  - Expected R² ~ 0.03-0.05
  
- **Model B**: Mean return (constant prediction)
  - Trivial baseline
  - Should be beaten by any learner

**Deliverable**: Baseline metrics for comparison

---

#### Stage 2: Market-Only Neural Network (Market-Only Baseline)
**Goal**: Single modality, establish market signal strength

**Architecture**:
```
Input: Market features (D_m)
  ↓
Dense(256) + ReLU + Dropout(0.2) + BatchNorm
  ↓
Dense(128) + ReLU + Dropout(0.2) + BatchNorm
  ↓
Dense(64) + ReLU + Dropout(0.2) + BatchNorm
  ↓
Output: [pred_1d, pred_5d, pred_20d]  (multi-horizon)
```

**Parameters**:
- Input size: ~15 market features
- Hidden: [256, 128, 64]
- Output: 3 (horizons)
- Total params: ~50k

**Training**:
- Optimizer: Adam(lr=0.001)
- Loss: Weighted MSE (emphasis on longer horizons)
- Epochs: 100
- Batch size: 32
- Early stopping: patience=15, monitor=val_loss

**Expected performance**:
- R² on test: 0.04-0.08 (market only)
- Direction accuracy: 51-55% (slightly better than random)

---

#### Stage 3: Multimodal Model (MAIN)
**Goal**: Test news signal, main hypothesis

**Architecture**:
```
Market Features (D_m=15)          News Embedding (D_n=384)
         ↓                                    ↓
Market Branch MLP              News Branch (Linear Proj)
  Dense(256) + ReLU               Dense(384→128) + ReLU
  Dense(128) + ReLU + Dropout     
         ↓                                    ↓
    Market Emb (128)           News Emb (128)
           ↓                        ↓
           └────────────┬──────────┘
                        ↓
              Fusion Module (Concat)
         Dense(256) + ReLU + Dropout
         Dense(128) + ReLU + Dropout
         Dense(64) + ReLU + Dropout
                        ↓
           Output: [pred_1d, pred_5d, pred_20d]
```

**Key Points**:
- Separate branches for market and news
- Learn intermediate embeddings (128-dim)
- Fuse via concatenation
- Multi-task output (3 horizons)

**Parameters**:
- Market branch: ~55k
- News branch: ~50k
- Fusion: ~50k
- **Total**: ~155k

**Training**:
- Same optimizer/loss as baseline
- Regularization: L2=1e-4
- Dropout: 0.2 in all branches

**Expected improvement**:
- ΔR² >= 0.02 (if news is predictive)
- Or no improvement (if hypothesis false)

---

#### Stage 4: Optional Advanced Models (Phase 2+)
**Only if Phase 1 successful and time permits**:

- **Transformer-based**: Temporal encoder for news sequences
- **Attention fusion**: Learn to weight market vs news dynamically
- **Uncertainty quantification**: Predict intervals, not point estimates
- **Ensemble**: Multiple models with different seeds

**Decision rule**: Only add if complexity justified by performance gain

---

### 7.2 Loss Functions

#### Primary Loss: Weighted MSE

```python
loss = (1/N) * Σ_i [w_h * (y_i - pred_i)^2]

where:
- w_h = horizon weight: [0.3, 0.3, 0.4]  for [1d, 5d, 20d]
- Emphasize longer horizons (harder to predict)
- Differentiable, stable gradients
```

**Why**: Standard regression loss, stable, interpretable

---

#### Alternative: Huber Loss (Robustness)

```python
loss = {
    0.5 * (y - pred)^2           if |y - pred| <= δ
    δ * (|y - pred| - 0.5*δ)     otherwise
}

δ = 1.0  (tunable)
```

**Why**: Less sensitive to outliers than MSE
**When to use**: If return distribution has fat tails

---

### 7.3 Regularization

```
L2 weight decay: 1e-4
Dropout: 0.2 in all layers
Batch normalization: Normalize activations
Early stopping: patience=15, monitor=val_loss
```

**Rationale**:
- Prevent overfitting to small dataset
- Dropout: noise injection for regularization
- Batch norm: stabilize training, allow higher LR

---

## 8. TRAINING PROTOCOL

### 8.1 Time-Based Validation Strategy

**Critical Principle**: NO shuffling, preserve temporal order

#### Walk-Forward Validation

```
Historical data: 2016-2025 (10 years)

Fold 1:
  Train: [2016-01, 2020-06]
  Val:   [2020-07, 2020-12]
  Test:  [2021-01, 2021-12]

Fold 2:
  Train: [2016-01, 2021-06]
  Val:   [2021-07, 2021-12]
  Test:  [2022-01, 2022-12]

Fold 3:
  Train: [2016-01, 2022-06]
  Val:   [2022-07, 2022-12]
  Test:  [2023-01, 2023-12]

Fold 4:
  Train: [2016-01, 2023-06]
  Val:   [2023-07, 2023-12]
  Test:  [2024-01, 2024-12]
```

**Advantages**:
- Realistic simulation of deployment
- No look-ahead bias
- Tests model robustness across time periods
- Realistic for financial applications

---

### 8.2 Hyperparameter Tuning

**Where**: On validation set ONLY

```
For each fold:
  1. Grid search hyperparameters on train+val data
     (Use early stopping on val set)
  2. Select best hyperparams
  3. Retrain on full train+val
  4. Evaluate on test set
  5. Record test metrics
6. Report mean and std across folds
```

**Hyperparameter ranges** (if tuning):
```
learning_rate: [0.0005, 0.001, 0.002]
batch_size: [16, 32, 64]
dropout: [0.1, 0.2, 0.3]
l2_weight: [1e-5, 1e-4, 1e-3]
```

**Default**: Use same hyperparams across all folds (simpler, reproducible)

---

### 8.3 Leakage Prevention Checklist

- [ ] News embargo enforced (embargo_days >= 2)
- [ ] All features computed using past data only
- [ ] Scaler fitted on train set only
- [ ] Test set date > val set date > train set date (no overlaps)
- [ ] Walk-forward dates logged and validated
- [ ] For each train observation: all features have dates < label date
- [ ] For each test prediction: uses only train+val dates

**Validation code**:
```python
# Check no leakage
assert (X_train.index.max() < X_val.index.min())
assert (X_val.index.max() < X_test.index.min())

# Check news embargo
assert ((news_date + timedelta(days=embargo_days)) <= price_date).all()

# Scaler from train only
scaler = StandardScaler()
scaler.fit(X_train)  # NOT X_train + X_val
```

---

## 9. EVALUATION PROTOCOL

### 9.1 Comprehensive Metrics

#### Regression Metrics (Primary)

| Metric | Formula | Interpretation | Target |
|--------|---------|-----------------|--------|
| MAE | Σ\|y - pred\| / N | Avg absolute error | Low |
| RMSE | √(Σ(y - pred)² / N) | Penalizes large errors | Low |
| R² | 1 - RSS/TSS | Variance explained | > 0.05 |
| Correlation | Cov(y, pred) / (σ_y * σ_pred) | Prediction monotonicity | > 0.15 |
| MAPE | Σ\|y - pred\| / \|y\| / N | % error (avoid near-zero) | Low |

**Use R² and Correlation as primary metrics**

---

#### Direction Metrics (Secondary)

| Metric | Formula | Use | Target |
|--------|---------|-----|--------|
| Accuracy | TP+TN / (TP+TN+FP+FN) | % correct direction | > 52% |
| Precision | TP / (TP+FP) | If predict up, correct? | > 50% |
| Recall | TP / (TP+FN) | Catch upside moves? | > 50% |
| F1 | 2 * P * R / (P+R) | Balanced metric | > 0.5 |

**Validation**: Balanced classes (~50% up/down), so accuracy ~ recall

---

#### Ranking Metrics (Tertiary)

| Metric | Formula | Use |
|--------|---------|-----|
| Spearman ρ | Rank correlation | Top/bottom picks work? |
| Info Ratio | mean(excess) / std(excess) | Risk-adj outperformance |
| Sharpe Ratio | mean(return) / std(return) | Return per unit risk |

---

#### Calibration Metrics (Optional)

| Metric | Formula | Use |
|--------|---------|-----|
| ECE | Σ \|conf - acc\| / n_bins | Overconfidence? |
| Brier Score | Σ(pred - y)² / N | Prob calibration |

---

### 9.2 Subgroup Analysis

#### By Horizon
```
Report metrics separately for:
- 1-day predictions
- 5-day predictions
- 20-day predictions

Question: Does news help more on certain horizons?
```

#### By News Density
```
Define quintiles of articles per stock-day:
- Very low news (Q1)
- Low news (Q2)
- Medium news (Q3)
- High news (Q4)
- Very high news (Q5)

Hypothesis: News signal stronger in Q4-Q5
```

#### By Sector (if data available)
```
Group stocks by sector (GICS):
- Financials, Tech, Healthcare, Energy, etc.

Test: Does multimodal advantage vary by sector?
Use ANOVA: H0: mean_delta_R2 is same across sectors
```

#### By Time Period
```
Split test set by year:
- 2021, 2022, 2023, 2024

Question: Is signal consistent across years?
Concern: Signal degrades in bear market? Specific to bull market?
```

---

### 9.3 Statistical Significance Testing

#### Paired Tests
```
For each test sample, compute:
- Error_baseline = |y - pred_baseline|
- Error_multimodal = |y - pred_multimodal|

Paired t-test:
- H0: E[Error_baseline - Error_multimodal] = 0
- H1: E[Error_baseline - Error_multimodal] > 0
- α = 0.05

Report:
- t-statistic
- p-value
- 95% CI on difference
```

---

#### Bootstrap Confidence Intervals
```
For metric M (e.g., R²):
1. Sample N observations with replacement (1000x)
2. Compute M on each sample
3. Report [2.5th, 50th, 97.5th] percentiles
```

---

### 9.4 Comparison Framework

#### Baseline Comparison

```
Metrics by model:

Model | R² (1d) | R² (5d) | R² (20d) | Accuracy | Runtime
------|---------|---------|----------|----------|--------
OLS   | 0.032   | 0.045   | 0.052    | 51.2%    | <1s
Market-Only MLP | 0.048 | 0.062 | 0.068 | 52.1% | 100ms
Multimodal | 0.068 | 0.082 | 0.088 | 53.5% | 150ms

ΔR² = Multimodal - Market-Only

ΔR² (1d) = 0.020 = 2.0 percentage point improvement
```

**Interpretation**:
- Positive ΔR² supports hypothesis
- Statistical significance via paired test
- Report p-value and 95% CI

---

## 10. ABLATION STUDIES AND EXPERIMENTS

### 10.1 Ablation Design

#### Ablation 1: Market-Only vs Multimodal

```
Model A: Market features only
         → R² = 0.062 (baseline)

Model B: Market + News (exponential decay)
         → R² = 0.082 (proposed)

ΔR² = +0.020 (20% relative improvement)

Question: Is improvement statistically significant?
Test: Paired t-test on residuals, p < 0.05?
```

**Insight**: Core hypothesis test

---

#### Ablation 2: Decay Strategy

```
Model A: Exponential decay (halflife=7 days)
         → R² = 0.082

Model B: Simple mean (no decay)
         → R² = 0.078

Model C: Linear decay (weight = 1 - days_ago/lookback)
         → R² = 0.079

Best practice: Decay matters slightly, exponential wins
```

**Insight**: Validates time-decay hypothesis

---

#### Ablation 3: Embedding Type

```
Model A: Dense embeddings (384-dim, all-MiniLM)
         → R² = 0.082

Model B: Sentiment only (binary up/down)
         → R² = 0.058

Model C: Sentiment + novelty scores
         → R² = 0.065

Result: Dense embeddings >> simple sentiment
```

**Insight**: Semantic information > explicit sentiment

---

#### Ablation 4: Lookback Window

```
Model A: 7-day lookback
         → R²(1d)=0.065, R²(5d)=0.078, R²(20d)=0.080

Model B: 14-day lookback
         → R²(1d)=0.065, R²(5d)=0.080, R²(20d)=0.085

Model C: 30-day lookback (proposed)
         → R²(1d)=0.068, R²(5d)=0.082, R²(20d)=0.088

Result: Longer window helps longer horizons
```

**Insight**: Event state needs sufficient history

---

#### Ablation 5: Single Horizon vs Multi-Horizon

```
Model A: Three separate models (one per horizon)
         → R² = [0.070, 0.085, 0.090]

Model B: Single multi-task model
         → R² = [0.068, 0.082, 0.088]

Result: Multi-task slightly underperforms separate
        (but shares parameters, faster)
```

**Trade-off**: Parameter sharing vs horizon-specific specialization

---

#### Ablation 6: Market Neutralization

```
Model A: Raw returns (not market-neutral)
         → Pred returns rather than excess returns
         → R² on prediction ≈ 0.15-0.20 (artificially high)

Model B: Excess returns (market-neutral, proposed)
         → R² on excess returns ≈ 0.08
         → Isolates alpha contribution

Key insight: Market predictability is easier!
Must use excess returns for honest evaluation
```

---

### 10.2 Experimental Plan (Nice-to-Have)

If time permits after core experiments:

#### Experiment 1: Sentiment vs Embeddings Hybrid
```
Model A: Pure embeddings
Model B: Embeddings + sentiment scores as separate features
Model C: Sentiment used to weight embeddings

Which works best?
```

---

#### Experiment 2: Attention-Based Fusion
```
Standard: Concatenate embeddings
Advanced: Learn attention weights for market vs news

Does learned weighting improve?
```

---

#### Experiment 3: Transfer Learning
```
Question: Do pre-trained embeddings generalize well?
Test: Train model with fine-tuned embeddings vs frozen

Does fine-tuning help or hurt?
```

---

## 11. EXPECTED OUTCOMES AND REALISTIC ASSESSMENT

### 11.1 Likely Outcomes

#### Scenario 1: News Signal is Strong (Best Case)
**Conditions**:
- Market is inefficient for large-cap stocks
- Headlines contain predictive information
- News effect is rapid (affects 1-5 day returns)

**Expected Results**:
- ΔR² ≥ 0.02 on 5-day and 20-day returns
- Direction accuracy ≥ 2-3% better than random
- Information ratio ≥ 0.3 (if used for ranking)
- Effect persists across walk-forward folds

**Probability**: ~30-40% (optimistic but plausible)

**Interpretation**: News does add predictive value

---

#### Scenario 2: Modest Improvement (Realistic)
**Conditions**:
- Market is mostly efficient, but news provides marginal edge
- Effect is noisier, requires careful feature engineering
- Improvement only on specific horizons or conditions

**Expected Results**:
- ΔR² ≈ 0.01 (small but consistent)
- Direction accuracy ≈ 0.5% better (marginal)
- Effect statistically significant but economically small
- Improvement strongest in high news-density periods

**Probability**: ~40-50% (most likely)

**Interpretation**: News helps slightly; useful for research but not actionable alone

---

#### Scenario 3: No Signal (Weak Case)
**Conditions**:
- Market fully efficient; prices immediately reflect news
- Headlines are too sparse or contain little economic info
- Multimodal complexity adds noise without benefit

**Expected Results**:
- ΔR² ≈ 0 (multimodal ≈ market-only)
- No statistically significant difference
- Multimodal overfits without improving generalization

**Probability**: ~15-25% (pessimistic but possible)

**Interpretation**: News alone doesn't predict returns; need additional signals

---

### 11.2 Honest Assessment of Prior Patterns

**From literature on news and returns**:

1. **Papers claiming success typically show**:
   - R² improvements of 1-3% (excess returns)
   - Direction accuracy 51-55% (modest edge)
   - Often focus on specific regimes (earnings announcements, mergers, etc.)

2. **Common pitfalls**:
   - Lookahead bias (using news that wasn't available at prediction time)
   - Survivorship bias (only successful stocks)
   - Data snooping (tuning model to specific stocks/periods)
   - Ignoring transaction costs and implementation

3. **This project risks**:
   - Small dataset (50 stocks, ~10 years)
   - Limited news coverage (Finnhub headlines only)
   - Single information source (no analyst reports, earnings calls, etc.)
   - Free API rate limits

---

### 11.3 Realistic Targets by Phase

#### Phase 1 (Baseline + Simple Multimodal)
**Conservative expectation**:
- Market-only R²: 0.04-0.08
- Multimodal ΔR²: -0.01 to +0.02 (wide range, might hurt)
- **Decision point**: Does multimodal beat baseline?

**Acceptable outcome**: ΔR² ≥ 0.005 and statistically significant

---

#### Phase 2 (Refinement + Ablations)
**If Phase 1 positive**:
- Optimize embedding model, decay function, horizon weights
- Expected improvement: ΔR² += 0.01
- Total: ΔR² ≥ 0.015

---

#### Final (Advanced + Uncertainty)
**If Phase 2 succeeds**:
- Add uncertainty quantification, attention, calibration
- Expected: ΔR² ≥ 0.02, Sharpe ≥ 0.5
- Thesis-quality results

---

## 12. FAILURE MODES AND THREATS TO VALIDITY

### 12.1 Technical Risks

#### Look-Ahead Bias
**Risk**: Using information not available at prediction time

**Mitigation**:
- ✅ Embargo period (2-day minimum)
- ✅ Verify news dates < prediction dates
- ✅ Unit tests for leakage
- ✅ Walk-forward validation (no test on train data)

**Test**: Run leakage detection code on small sample by hand

---

#### Data Quality Issues
**Risk**: Misaligned or corrupted data

**Mitigation**:
- ✅ Compare price data with alternative source (Yahoo, etc.)
- ✅ Verify splits/dividends against company filings
- ✅ Check for outliers (>10σ returns)
- ✅ Log all data cleaning decisions

---

#### Insufficient Data
**Risk**: 50 stocks × 10 years × 20 trading days/month ≈ 120K observations
Small by ML standards

**Mitigation**:
- ✅ Use regularization (dropout, L2 weight decay)
- ✅ Smaller model (avoid overfitting)
- ✅ Walk-forward validation (realistic test)
- ✅ Report confidence intervals (bootstrap)

---

### 12.2 Statistical Risks

#### Multiple Testing Problem
**Risk**: If running many experiments, some will appear significant by chance

**Mitigation**:
- ✅ Pre-register primary hypothesis (H1b)
- ✅ Bonferroni correction if many tests
- ✅ Report p-values and confidence intervals
- ✅ Distinguish "preregistered" vs "exploratory" findings

---

#### Survivorship Bias
**Risk**: Using only stocks still listed today (no bankruptcies)

**Mitigation**:
- ✅ Acknowledge in limitations
- ✅ If data available, include delisted stocks (via historical list)
- ✅ Report results separately for different time periods

---

#### Regime Dependence
**Risk**: Signal works only in specific market conditions (bull market, low vol, etc.)

**Mitigation**:
- ✅ Analyze results per year (includes different regimes)
- ✅ Subgroup by volatility, market return
- ✅ Report where signal works and doesn't

---

### 12.3 Methodological Risks

#### Feature Leakage
**Risk**: Feature computation uses future information

**Mitigation**:
- ✅ All features computed using [t-window, t] data only
- ✅ Unit tests verify no future dates used
- ✅ Scaler fit on train only
- ✅ Code review and documentation

---

#### Hyperparameter Tuning on Test Set (Implicit Leakage)
**Risk**: Tuning hyperparams based on test performance

**Mitigation**:
- ✅ Tune only on validation set
- ✅ Report final hyperparams before running test
- ✅ Use cross-validation on training set, not test

---

#### Model Selection Bias
**Risk**: Choosing model that overfits to data

**Mitigation**:
- ✅ Simple, interpretable models (avoid unnecessary complexity)
- ✅ Regularization by default
- ✅ Test on held-out test set before publication
- ✅ Report test set size and period

---

### 12.4 Noise and Weak Labels

#### Noisy Targets
**Risk**: Returns are noisy; signal-to-noise ratio may be very low

**Mitigation**:
- ✅ Accept small R² (0.05-0.10 is respectable)
- ✅ Use ensemble methods if needed (multiple seeds)
- ✅ Focus on information ratio (risk-adjusted metric)
- ✅ Compare to baselines honestly

---

#### Weak News Signal
**Risk**: Finnhub headlines alone may not contain enough info

**Mitigation**:
- ✅ Combine with other sources (if available)
- ✅ Use full articles (not just headlines) later
- ✅ Consider analyst ratings, earnings data
- ✅ Accept limitation in thesis

---

### 12.5 Reproducibility Risks

#### Non-Deterministic Training
**Risk**: Model trained twice gives slightly different results

**Mitigation**:
- ✅ Set random seed
- ✅ Disable CUDA non-determinism if possible
- ✅ Log all random seed values
- ✅ Report mean and std across seeds (3-5 runs)

---

#### Missing Documentation
**Risk**: Code/methods unclear; others can't reproduce

**Mitigation**:
- ✅ Comprehensive docstrings
- ✅ README with exact reproduction steps
- ✅ Configuration files (YAML) with all hyperparams
- ✅ Unit tests
- ✅ Saved checkpoints and predictions

---

## 13. IMPLEMENTATION ROADMAP

### Phase 0: Setup (Week 1)
- [ ] Create project structure (DONE)
- [ ] Set up environment (Python, PyTorch, etc.)
- [ ] Implement utility functions (logging, I/O, reproducibility)
- [ ] Write unit test infrastructure

**Deliverable**: Runnable project skeleton

---

### Phase 1: Data Pipeline (Weeks 2-3)

#### 1a. Data Collection
- [ ] Implement Twelve Data client (with caching, rate limiting)
- [ ] Implement Finnhub client (with caching, rate limiting)
- [ ] Download price data for 50 stocks, 2016-2025
- [ ] Download news for same tickers and period
- [ ] Validate data (no obvious errors)

**Sanity checks**:
- [ ] Price data has no NaN (or explained missing)
- [ ] News tickers match price tickers
- [ ] Dates are reasonable (2016-2025)

---

#### 1b. Data Cleaning
- [ ] Implement price cleaning (outlier detection, split handling)
- [ ] Implement news cleaning (deduplication, length filtering)
- [ ] Create universe validation (coverage checks)
- [ ] Create test data report (stats per ticker)

**Deliverable**: `data/interim/prices.parquet`, `data/interim/news.parquet`

---

#### 1c. Feature Engineering
- [ ] Implement market features (returns, volatility, regime)
- [ ] Implement news embedding (sentence-transformers)
- [ ] Implement event state aggregation (exponential decay)
- [ ] Implement label creation (forward returns, excess returns)
- [ ] Create feature matrix

**Deliverable**: `data/final/features.parquet`, `data/final/labels.parquet`

---

#### 1d. Alignment & Leakage Prevention
- [ ] Implement embargo logic
- [ ] Create walk-forward splits
- [ ] Validate no leakage (automated tests)
- [ ] Log alignment report

**Deliverable**: `data/final/splits.pkl` (fold indices), leakage test report

---

### Phase 2: Baseline Models (Week 4)

#### 2a. OLS Baseline
- [ ] Implement linear regression
- [ ] Evaluate on test set
- [ ] Report metrics (R², MAE, etc.)

---

#### 2b. Market-Only MLP
- [ ] Implement MLP architecture
- [ ] Training loop with validation
- [ ] Early stopping, checkpointing
- [ ] Evaluate on test set

**Metrics to report**:
```
R² per horizon, direction accuracy, correlation
```

---

#### 2c. Baseline Report
- [ ] Comparison table: OLS vs MLP
- [ ] Confidence intervals (bootstrap)
- [ ] Statistical tests
- [ ] Interpretation

**Deliverable**: `reports/baseline_analysis.md`

---

### Phase 3: Multimodal Model (Weeks 5-6)

#### 3a. Architecture Implementation
- [ ] Implement market branch
- [ ] Implement news branch
- [ ] Implement fusion module
- [ ] Test forward pass (dummy inputs)

---

#### 3b. Training
- [ ] Set up training loop (walk-forward)
- [ ] Implement metrics computation
- [ ] Training with early stopping
- [ ] Save best model

---

#### 3c. Evaluation
- [ ] Compute all metrics per fold
- [ ] Compute metrics per horizon
- [ ] Subgroup analysis (news density, sector, etc.)
- [ ] Comparison vs baselines

**Deliverable**: `reports/multimodal_evaluation.md`

---

### Phase 4: Ablation Studies (Week 7)

#### 4a. Core Ablations
- [ ] Market vs Multimodal (hypothesis test)
- [ ] Decay vs No-Decay
- [ ] Dense embeddings vs Sentiment

---

#### 4b. Sensitivity Analysis
- [ ] Lookback window (7 vs 14 vs 30 days)
- [ ] Decay halflife (3 vs 7 vs 14 days)
- [ ] Horizon weights

**Deliverable**: `reports/ablations.md`

---

### Phase 5: Statistical Testing & Reporting (Week 8)

#### 5a. Significance Tests
- [ ] Paired t-tests (multimodal vs baseline)
- [ ] Bootstrap confidence intervals
- [ ] Effect sizes

---

#### 5b. Figures
- [ ] Prediction scatter plots (pred vs actual)
- [ ] R² comparison (horizons)
- [ ] Direction accuracy stacked bar
- [ ] Residuals distribution

---

#### 5c. Tables
- [ ] Main results table
- [ ] Subgroup results
- [ ] Ablation results
- [ ] Computational cost

**Deliverable**: Multiple publication-quality figures/tables

---

### Phase 6: Thesis/Paper Writing (Week 9-10)

- [ ] Problem formulation (this doc + refinement)
- [ ] Literature review summary
- [ ] Methods (data, features, models)
- [ ] Results (main + ablations)
- [ ] Discussion (what we learned)
- [ ] Limitations
- [ ] Conclusion

---

### Timeline Summary

```
Weeks 1-3: Data (collection, cleaning, engineering)
Weeks 4-5: Baselines + Multimodal
Week 6-7: Ablations + Testing
Weeks 8-10: Writing + Final experiments
```

**Contingency**: If data collection slow, start with subset of tickers

---

## 14. FINAL REPORT STRUCTURE

### Thesis Outline

#### 1. Introduction
- Hook: Financial forecasting, news as signal
- Gap: Existing work has limitations (leakage, limited scope)
- Thesis: Propose multimodal approach with news event state
- Contributions: 
  * Rigorous design avoiding look-ahead bias
  * Multi-horizon framework
  * Ablations validating design choices

---

#### 2. Background
- Efficient market hypothesis and news
- Prior work on news + returns
- Text representation learning
- Multi-task learning

---

#### 3. Problem Formulation
- Why not pure price prediction?
- Definition of excess returns
- Multi-horizon prediction setup

---

#### 4. Data
- Prices (Twelve Data)
- News (Finnhub)
- Universe (50 stocks, S&P 500)
- Cleaning protocol
- **Table**: Data summary (# stocks, years, # observations)

---

#### 5. Methods
- **Market features**: OHLCV, technical, regime
- **News features**: Embeddings, event state aggregation
- **Model architecture**: Market branch, news branch, fusion
- **Training**: Walk-forward, early stopping, regularization
- **Evaluation**: Metrics, subgroups, statistical tests

---

#### 6. Results
- **Main**: Multimodal vs baselines (R², direction, correlation)
- **Subgroups**: By horizon, news density, sector, year
- **Ablations**: Decay, embeddings, lookback, etc.
- **Significance**: p-values, 95% CIs

---

#### 7. Discussion
- Interpretation: Does news help? When?
- Generalization: Results consistent across periods?
- Comparison with priors: Realistic vs optimistic outcomes?
- Limitations: Data, method, evaluation

---

#### 8. Limitations
- Limited to large-cap US stocks
- Headline-only news (not articles)
- 10 years of data (specific era, not all regimes)
- No transaction costs or implementation
- Single information source

---

#### 9. Future Work
- Extend to other assets (international, crypto, commodities)
- Incorporate richer news (full articles, metadata)
- Add other signals (earnings, analyst ratings)
- Real-world deployment (cost-aware optimization)

---

#### 10. Conclusion
- Summary of findings
- Implications for research
- Open questions

---

### Appendices

- **A**: Data summary statistics
- **B**: Feature definitions
- **C**: Architecture details (diagrams, parameter counts)
- **D**: Hyperparameter settings
- **E**: Full results tables
- **F**: Code (on GitHub)

---

## 15. FINAL CHECKLIST

### Before Starting Implementation

- [ ] Review and finalize Problem Formulation (Section 1)
- [ ] Confirm Research Questions and Hypotheses (Section 2)
- [ ] Plan Literature Review (Section 3)
- [ ] Finalize Data Sources and Cleaning (Section 4)
- [ ] Define Labels Precisely (Section 5)
- [ ] Plan Feature Engineering (Section 6)
- [ ] Sketch Model Architectures (Section 7)
- [ ] Document Training Protocol (Section 8)
- [ ] List Evaluation Metrics (Section 9)
- [ ] Plan Ablation Experiments (Section 10)

---

### During Implementation

- [ ] Log all data cleaning decisions
- [ ] Unit tests for leakage
- [ ] Random seed logging
- [ ] Checkpoints of trained models
- [ ] Prediction files saved
- [ ] Metrics logged per fold

---

### Before Final Report

- [ ] Run full pipeline (data → eval) end-to-end
- [ ] Reproduce results 3x with different seeds
- [ ] Write comprehensive README
- [ ] Generate all figures and tables
- [ ] Write methods section
- [ ] Interpret results honestly
- [ ] Discuss limitations

---

## KEY PRINCIPLES

1. **Honesty First**: Report what actually happened, not what you hoped
2. **Leakage Paranoia**: Assume you're leaking info until proven otherwise
3. **Simple First**: Start with baselines before complexity
4. **Walk Forward Always**: Time-series needs time-based validation
5. **Document Everything**: Future you will thank present you
6. **Test Publicly**: Show results on test set you haven't touched

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-05  
**Status**: Ready for Implementation

