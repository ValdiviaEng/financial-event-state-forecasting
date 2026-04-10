# Leakage‑Aware Benchmarking for a Multi‑Horizon Multimodal EOD Financial Forecasting Model

## Benchmarking problem restatement in research terms

**What is being benchmarked.** You are benchmarking the *out‑of‑sample generalization* of a supervised forecasting system that maps information available **as‑of the end of trading day \(t\)** (daily market features plus a news‑derived “event state,” and possibly auxiliary firm metadata) into predictions for **multiple forward horizons** (1, 5, 20, optionally 60 trading days). The object of interest is not the ability to “fit prices,” but whether the model provides **incremental predictive skill** over market‑only baselines under strict temporal causality constraints. citeturn2search5turn3search3

**What is not being benchmarked.** Benchmarking here should *not* be portrayed as: (i) a realistic trading PnL engine, (ii) an intraday execution simulator, or (iii) evidence of causal impact from individual news items. It is a forecast‑skill audit under noise, serial dependence, and non‑stationarity. citeturn2search5turn4search9

**What “good benchmarking” means in this context.** A defensible benchmark protocol must satisfy three constraints simultaneously:

1. **Temporal integrity:** training must occur strictly before testing in time (no training on future observations). Classical random k‑fold is inappropriate for time series because it breaks the IID assumption and can produce overly optimistic generalization estimates. citeturn2search5  
2. **Overlap integrity (multi‑horizon):** labels like \(y^{(20)}_t\) depend on future windows. If the training set contains samples whose label windows overlap the test window, you can get subtle leakage—even if all timestamps “look” ordered. This is one of the core motivations for **purging** and **embargoing** in financial ML. citeturn3search3turn3search4  
3. **Multiple‑testing integrity:** because financial prediction is weak and noisy, trying many variants and selecting the best can easily lead to **backtest overfitting** (illusory improvements). You need protocol discipline to prevent “research degrees of freedom” from inflating results. citeturn4search9turn4search5

**Why naive train/test thinking is insufficient.** A single split answers only one question: “How did my model do in this one regime and this one time window?” It does not reliably characterize sensitivity to regime shifts, provide stable estimates with confidence intervals, or support safe hyperparameter tuning without repeatedly “peeking” at the same recent test window. citeturn2search5turn4search9

## Critical evaluation of your proposed method: train up to time \(T\), test on the most recent unseen block

Your proposal is a **chronological holdout** (train on \([t_0, T]\), test on \((T, t_{\text{end}}]\)). This is a foundational technique and is consistent with the scikit‑learn guidance that you must evaluate time series on “future” observations rather than random folds. citeturn2search5

### Why it is a reasonable starting point

**Established value.** A blocked chronological holdout is a good approximation to the real operational constraint: you train on past data and deploy into the future. It also provides a clean “final exam” that is easy to explain in a thesis defense. citeturn2search5

**When it is especially useful.** It is most useful as a **final untouched test** (“lockbox”) that you never use for model selection. This reduces the risk of tuning to the test set and then reporting a biased estimate. The PBO literature makes the broader point that repeated selection over backtests can produce optimistic results; an untouched lockbox directly combats that behavior. citeturn4search9turn4search5

### What it captures well

- **Regime realism** for the final period (you learn whether the model still works “now”).
- **Operational plausibility** (you didn’t train on the future).
- **Failure visibility** (a model that “only works in older regimes” will be exposed). citeturn2search5turn4search9

### Weaknesses and failure modes

**Regime dependence and statistical fragility.** One final test block can be unrepresentative. If the period is unusually calm, unusually volatile, or dominated by a particular macro regime, your test result can be either unfairly pessimistic or unfairly optimistic. This is a core reason time‑series evaluation often uses **multiple rolling/expanding evaluations** rather than one split. citeturn2search5

**Wasted time variation.** A single holdout uses only a fraction of the timeline for evaluation. If your sample is limited (30–100 stocks, daily bars, several horizons), you will often want **more than one test window** to stabilize estimates. citeturn2search5

**Not enough by itself for multi‑horizon labels.** Even with a clean chronological split, overlapping horizons can cause leakage *within the training/validation machinery* if you do tuning, early stopping, or feature normalization incorrectly. This is exactly what purged/embargoed CV is designed to address. citeturn3search3turn3search4

### Best role for your method

**Plausible best practice recommendation:** treat the “most recent unseen block” as a **final lockbox test** (untouched until the end). Use other protocols (walk‑forward + purge/embargo) for model development and selection. citeturn3search3turn4search9

## Main benchmarking families for your project

Below are the major evaluation families most relevant to end‑of‑day, multi‑horizon financial ML, with a focus on what scientific question each answers and why they fail/succeed under your constraints.

### Single chronological holdout

**What it is.** One train period and one future test period. citeturn2search5  
**Best use.** Final lockbox; simple “deployed‑future” check. citeturn4search9  
**Weakness.** High variance; likely regime‑specific; insufficient for robust model selection unless you accept large uncertainty. citeturn2search5  
**Suitability by horizon.** Works for all horizons conceptually, but the longer the horizon, the more label overlap and fewer effective samples you have, increasing instability. citeturn3search3

### Rolling walk‑forward validation (fixed window)

**What it is.** Train on a rolling window of fixed length, test on the next block, repeat.  
**What it answers.** “How stable is the model when trained on recent history only?”  
**Strength.** Better regime coverage; more evaluation points; often more realistic if your production retrains regularly. citeturn2search5  
**Weakness.** If the window is too short, you may underfit slow effects; if too long, you may mix regimes.  
**Suitability by horizon.** Good for 1d/5d; still useful for 20d/60d but must handle overlap with purge/embargo more carefully. citeturn3search3

### Expanding‑window walk‑forward (growing history)

**What it is.** Train on an expanding set that keeps all past data; test on next block, repeat. This is conceptually similar to `TimeSeriesSplit` where training sets are supersets of previous ones. citeturn2search5  
**Strength.** Uses all history; often reduces variance; good if you believe learnable structure persists.  
**Weakness.** More vulnerable to regime shift if very old data becomes harmful; can also inflate compute.  
**Suitability by horizon.** Often reasonable across horizons, but again needs overlap control. citeturn3search3

### Rolling‑origin evaluation

**What it is.** A general forecasting evaluation pattern: repeatedly choose an “origin” time, train on history before it, forecast forward, compare to realized. Conceptually overlaps with walk‑forward; its benefit is clarifying that each evaluation point is “forecasting from this origin.” citeturn2search5  
**Strength.** Makes horizon‑specific evaluation natural (you score 1/5/20/60 forward from each origin).  
**Weakness.** Needs explicit policy for retraining frequency and overlap handling. citeturn3search3

### Purged and embargoed temporal cross‑validation

**What it is.** Cross‑validation adapted for financial labels that overlap in time. You **purge** training samples whose label windows overlap the validation window and impose an **embargo** buffer (removing samples immediately after the test window) to reduce leakage. This is explicitly described as necessary for financial CV (e.g., in López de Prado’s framework). citeturn3search3turn3search4  
**Strength.** One of the most defensible approaches for **hyperparameter tuning** and model selection when labels depend on future windows. citeturn3search3  
**Weakness.** Reduces effective data; can be more complex to explain; computationally heavier if you do many folds.  
**Suitability by horizon.** Especially important as horizons increase (20d/60d), because overlap windows become large. citeturn3search3turn3search4

### Combinatorial purged cross‑validation

**What it is.** A family of cross‑validation schemes designed to further reduce leakage and provide more robust overfitting detection by combining purged splits in a combinatorial way (various implementations exist in practice; often referenced as CPCV in the financial ML community). citeturn3search4  
**Use case.** When you want a more intensive overfitting audit than simple k‑fold or simple walk‑forward.  
**Uncertain, verify manually:** the “best CPCV variant” and exactly how much it improves reliability depends on implementation details and your sample size. Verification: implement a toy simulation to estimate bias/variance of score estimates vs simpler schemes, or consult primary text (book/paper) if accessible. citeturn3search3turn4search9

### Nested time‑series validation (model selection vs final assessment)

**What it is.** An outer temporal split for evaluation and an inner temporal split for hyperparameter tuning, ensuring the test set remains untouched. This is conceptually the cleanest separation between “tuning” and “final reporting.” citeturn2search5turn3search3  
**Strength.** Minimizes selection bias.  
**Weakness.** Compute heavy; can be too slow if you tune heavily.  
**Suitability by horizon.** Very good for thesis‑grade claims if compute permits. citeturn4search9

### Final locked recent holdout (lockbox test)

**What it is.** A final, recent test block that is not used at all until the end.  
**Strength.** Supports a strong thesis defense story: “This result was never used for tuning.” citeturn4search9  
**Weakness.** Still regime‑dependent; must be complemented by walk‑forward for stability. citeturn2search5

## Financial‑ML‑specific benchmarking risks and how to prevent them

### Look‑ahead bias

**Why it matters.** It can create dramatic false performance.  
**How it happens in your setting.** Most commonly through timestamp misalignment (news after market close being included in day‑\(t\) features) or through using information from within the label horizon during training.  
**Prevention.** Strict as‑of‑close alignment and purge/embargo where labels overlap. citeturn3search3turn3search4

### Overlapping‑label contamination

**Why it matters.** Even if your train dates are “earlier,” labels can overlap future windows; leakage can persist via shared future information.  
**Prevention.** Purging and embargo are designed specifically for this. citeturn3search3turn3search4

### Leakage through feature normalization

**Why it matters.** If you normalize using statistics computed on the full dataset (train + test), you leak distributional information from the future.  
**Prevention.** Fit normalization strictly on training data within each fold.  
**Uncertain, verify manually:** which normalization choices (per‑ticker vs global vs per‑fold) are best for your panel depends on whether your model is cross‑sectional and whether features are stationary. Verification: run ablations of normalization policies inside a purged walk‑forward framework.

### Text alignment / after‑hours news leakage

**Why it matters.** The problem is not the text itself but the temporal availability. Using after‑hours content for day‑\(t\) creates “future information” relative to the close.  
**Prevention.** Use an exchange calendar and strict cutoff policies; audit with random spot checks around earnings days (high incidence of after‑hours releases). citeturn3search3

### Corporate actions contamination (splits/dividends) distorting labels

**Why it matters.** A split or dividend adjustment error can appear as a huge return and dominate evaluation.  
**Prevention.** Ensure adjusted series or apply correct multipliers. A concrete example of split/dividend multipliers and the adjusted close concept (aligned to CRSP standards) is described by Yahoo’s documentation. citeturn8search0turn8search48

### Survivorship bias

**Why it matters.** Using only “current survivors” (e.g., current index constituents) overstates historical feasibility and can inflate performance.  
**Prevention.** Use historical constituent lists where possible; otherwise, declare this limitation explicitly. citeturn8search49turn8search1

### Selection bias from trying many experiments (backtest overfitting)

**Why it matters.** In finance, weak signals + many trials → high risk of picking a lucky model.  
**Prevention.** Keep a lockbox test untouched and constrain hyperparameter search; consider overfitting diagnostics such as CSCV/PBO‑style thinking. Bailey et al. explicitly argue that standard holdout can be unreliable in investment backtests and propose a framework for backtest overfitting (PBO). citeturn4search5turn4search9

## Metrics and what they really measure in your setting

### Regression metrics (MAE/RMSE/R²)

**What they capture.** Average error magnitude.  
**What they miss.** Directional usefulness, cross‑sectional ranking skill, and risk‑aware decision quality. In finance, where returns are noisy, absolute error can be a weak proxy for “usefulness.”  
**How they mislead.** A model can have marginally better RMSE but be useless for ranking, or vice versa.  
**Recommendation.** Report regression metrics per horizon, but do not make them the sole definition of success. citeturn2search5turn2search0

### Classification metrics (Accuracy / balanced accuracy / AUC / PR‑AUC)

**What they capture.** Ability to discriminate positive/negative events (e.g., up/down, downside events).  
**Pitfall.** Class imbalance can make accuracy meaningless; PR‑AUC can be more informative when positive events are rare.  
**Recommendation.** Use balanced accuracy or AUC/PR‑AUC for direction/downside tasks; always report base rates. citeturn5search3

### Probability quality metrics (Brier score, calibration curves)

**What they capture.** Whether predicted probabilities mean what they say (e.g., “70% chance of downside” actually happens ~70% of the time).  
**Why this matters.** If your project produces uncertainty‑aware outputs, calibration becomes a central scientific quality dimension. Proper scoring rules are the theoretically correct way to evaluate probabilistic forecasts; Gneiting & Raftery formalize strictly proper scoring rules and why they matter. citeturn2search1turn2search3  
**Concrete measurement.** Reliability diagrams / calibration curves are a standard tool; scikit‑learn documents calibration curves and their binning tradeoffs (larger bins need more data). citeturn5search1turn5search0

### Ranking metrics (IC, rank correlation, top‑k hit rate)

**What they capture.** Skill at ordering stocks cross‑sectionally for a given day/horizon.  
**Why they can matter more than RMSE.** Many financial uses are ranking‑based (allocate more to top assets), and ranking skill can be statistically detectable even when point prediction is weak.  
**Uncertain, verify manually:** the best ranking metric depends on your ultimate scoring rule (top‑k selection vs continuous weighting). Verification: run a metric sweep and check consistency across time folds and regimes; ensure that ranking metrics are computed in a leakage‑safe manner (per date, out‑of‑sample). citeturn4search9

## What should be the true primary benchmark objective?

This is not purely a technical choice; it’s a thesis‑claim choice.

**Established methodological point.** Different metrics answer different scientific questions; therefore your primary benchmark objective must match your thesis claim. A model can be weak on RMSE but useful for ranking, and vice versa. citeturn2search0

### A defensible priority ordering for your project

**Plausible recommendation (common in financial ML):**
1. **Cross‑sectional ranking skill** (per horizon and per day) as a core “usefulness” measure.  
2. **Return prediction metrics** (MAE/RMSE/correlation) as secondary, mainly to contextualize.  
3. **Probabilistic calibration** if your outputs are uncertainty‑aware or downside‑probabilities (this becomes primary if your thesis is “risk‑aware forecasting”). citeturn2search1turn5search1turn4search9

### Raw returns vs abnormal/excess returns

**Plausible but not guaranteed.** Abnormal or factor‑neutral targets can make the problem “more aligned” with news information (less dominated by market beta). But they can also be noisier, and computing them correctly requires point‑in‑time factor data discipline.  
**Uncertain, verify manually:** whether abnormal returns improve detectability for your particular universe and horizon mix must be validated experimentally with purged walk‑forward and a lockbox. citeturn3search3turn4search9

## Tournament of eight benchmarking strategies

I’ll define eight distinct benchmarking strategies and run an elimination‑style tournament. The tournament criterion is “accuracy quality” meaning: realism of the estimate for true out‑of‑sample performance, leakage safety, and stability (not “best numeric score,” which would be circular).

### The eight candidates

**B1: Single recent chronological holdout (your idea).**  
Train on past, test on newest block. citeturn2search5

**B2: Rolling walk‑forward (fixed length training window), no purge/embargo.**  
Better regime coverage but still vulnerable to horizon overlap leakage if labels overlap. citeturn2search5

**B3: Expanding walk‑forward (TimeSeriesSplit‑style), no purge/embargo.**  
Uses expanding training sets; same overlap issue remains. citeturn2search5

**B4: Rolling walk‑forward + purge/embargo.**  
Explicitly addresses label overlap leakage. citeturn3search3turn3search4

**B5: Expanding walk‑forward + purge/embargo.**  
Same as B4 but with expanding training history. citeturn2search5turn3search3

**B6: Nested temporal validation (inner purged/embargo splits) + final lockbox holdout.**  
Clean separation: inner for tuning, outer for evaluation, and final lockbox untouched. citeturn3search3turn4search9

**B7: Cross‑sectional ranking‑focused benchmark design (per‑date ranking metrics) with walk‑forward.**  
You benchmark the *same splits* but your primary evaluation is ranking‑skill rather than return‑error. citeturn4search9

**B8: Multi‑objective benchmark suite: regression + ranking + calibration (proper scoring rules) under purge/embargo walk‑forward + lockbox.**  
This is not “one metric,” it’s an evaluation architecture. Scoring‑rules theory supports this when probabilistic forecasts matter. citeturn2search1turn5search1turn3search3

### Quarterfinals

**Match A: B1 vs B2**  
Winner: **B2** (rolling walk‑forward).  
Reason: B1 is too variance‑heavy and regime‑dependent to serve as the main benchmark. B2 provides multiple evaluation windows and better stability. citeturn2search5

**Match B: B3 vs B4**  
Winner: **B4** (walk‑forward + purge/embargo).  
Reason: B3 addresses temporal order but not overlapping‑label leakage; B4 directly addresses the key financial‑ML failure mode for multi‑horizon labels. citeturn3search3turn3search4

**Match C: B5 vs B7**  
Winner: **B7** if your thesis claim emphasizes “useful cross‑sectional forecasting,” otherwise **B5**.  
Under your “accuracy is king” requirement (accurate estimate of useful predictive skill), ranking is often the most meaningful objective in noisy returns. I advance **B7**, with the caveat that you still need purge/embargo splitting underneath. citeturn4search9turn3search3

**Match D: B6 vs B8**  
Winner: **B6** (nested temporal validation + lockbox).  
Reason: B8 is attractive but can become over‑complex and increases the risk of “metric shopping” unless strictly constrained. B6 is the cleanest methodology for selection vs final reporting. citeturn4search9turn3search3

### Semifinals

**Semifinal 1: B2 vs B4**  
Winner: **B4**.  
Reason: B2 increases coverage but leaves a major leakage path open for your multi‑horizon labels. B4 is the minimum defensible walk‑forward design in financial ML settings where labels overlap. citeturn3search3turn3search4

**Semifinal 2: B7 vs B6**  
Winner: **B6**, narrowly.  
Reason: B7 defines what you measure (ranking), but B6 defines the cleanest separation of model selection from final evaluation. In practice, you can include ranking metrics inside B6; therefore B6 dominates as a framework. citeturn4search9turn3search3

### Final

**Final: B4 vs B6**  
Winner: **B6 (nested temporal validation + final lockbox holdout)**.  
Reason: It combines the core leakage protections (purge/embargo) with the most defensible research separation between tuning and final results. It directly addresses the multi‑testing/backtest‑overfitting concern by preserving an untouched final evaluation set. citeturn4search9turn3search3

### Tournament results summary

- **Overall winner:** B6 (nested temporal validation + final lockbox holdout). citeturn4search9turn3search3  
- **Runner‑up:** B4 (walk‑forward + purge/embargo). citeturn3search3turn3search4  
- **Best low‑risk / high‑confidence:** B4 + lockbox (a simplified B6 if compute is limited). citeturn3search3  
- **Best high‑risk / high‑reward:** B8 (multi‑objective suite) if you can pre‑register metrics and avoid cherry‑picking; otherwise it becomes fragile. citeturn2search1turn4search9  
- **Best if thesis must stay narrow:** B4 as main protocol + one final lockbox block. citeturn3search3turn2search5  
- **Best if you can afford elaborate protocol:** B6 with carefully defined primary metrics and a strict lockbox. citeturn4search9turn3search3

## Best final benchmarking architecture for your thesis

### Must do

**A: “Main” protocol: walk‑forward with purge/embargo (B4/B5).**  
This is the core defense against overlap contamination that becomes especially important for 20d/60d horizons. citeturn3search3turn3search4

**B: “Final” protocol: locked recent holdout (lockbox).**  
Reserve the most recent block as untouched. Report final tables primarily from this lockbox, but contextualize with walk‑forward averages and variability. citeturn4search9

**C: “Model selection” protocol: nested time‑series tuning (B6) or minimal safe alternative.**  
If you can afford it, tune within inner purged splits, not on the lockbox. If you cannot afford nested evaluation, constrain tuning, freeze hyperparameters early, and keep the lockbox untouched. citeturn3search3turn4search9

### Strongly recommended

**D: Report performance per horizon, not only aggregated.**  
Because drivers differ by horizon, aggregated scores hide failure modes. TFT‑style multi‑horizon thinking underscores that horizons should be evaluated separately even if the model shares representation. citeturn3search3turn3search2

**E: Include at least one statistical comparison tool for “model vs baseline.”**  
Diebold–Mariano provides a framework for testing whether differences in predictive accuracy (under a chosen loss) are statistically distinguishable, given serial correlation and non‑Gaussian errors. citeturn2search0turn2search2

### Optional (but valuable if you claim uncertainty or risk)

**F: Calibration and proper scoring rules for probabilistic outputs.**  
If you predict probabilities (direction/downside) or predictive distributions, proper scoring rules are the theoretically correct evaluation tools; reliability diagrams help diagnose miscalibration. citeturn2search1turn5search1turn5search0

## Unified strategy discussion: should you combine benchmarking strategies?

**Yes, but only in a disciplined “layered framework,” not a messy hybrid.** Combining strategies is feasible and often best practice if you enforce clear role separation:

- **Development loop:** walk‑forward + purge/embargo (many folds) for stable estimates and ablations. citeturn3search3turn3search4  
- **Model selection:** nested temporal tuning if compute allows; otherwise minimal tuning and early freezing. citeturn4search9turn3search3  
- **Final claim:** lockbox only; never touched during development. citeturn4search9

### Advantages of combining strategies

- **Robustness to regime shifts** by sampling multiple folds rather than depending on one final period. citeturn2search5  
- **Leakage protection** for multi‑horizon labels via purging/embargo. citeturn3search3turn3search4  
- **Stronger thesis defensibility** because you can cleanly say what was used for tuning vs final reporting. citeturn4search9  
- **Reduced “lucky period” risk** by showing distributions of results rather than one score. citeturn2search5

### Disadvantages and how they can backfire

- **Protocol complexity** increases the chance of accidental misuse (“we tuned on the lockbox without realizing”). citeturn4search9  
- **Compute burden** increases, which can push people into shortcuts (reducing folds, reusing results incorrectly). citeturn2search5  
- **More degrees of freedom** can inadvertently invite cherry‑picking (especially if you define too many metrics as “primary”). The PBO perspective warns that selection over many trials can inflate apparent performance. citeturn4search9turn4search5

### Feasibility verdict

A combined approach is feasible for a Master’s thesis **if** you constrain it to:  
(1) one primary protocol (purged walk‑forward),  
(2) one final lockbox,  
(3) a small, pre‑declared set of primary metrics per task/horizon,  
(4) and strict separation of selection vs reporting. citeturn4search9turn3search3

## Final recommendation and brutally honest verdict

**Is your original idea good?** Yes—as the **final lockbox test**, not as your only benchmark. citeturn2search5turn4search9

**Is it enough by itself?** No. It is too regime‑dependent and does not address multi‑horizon overlap contamination or multiple‑testing pressures during model development. citeturn3search3turn4search9

**Best primary benchmarking method.** Purged/embargoed walk‑forward validation (rolling or expanding), with horizon‑aware labeling and evaluation. citeturn3search3turn3search4

**Best final holdout method.** A locked recent holdout block (“lockbox”) used exactly once at the end. citeturn4search9

**Best overall strategy for this thesis.**  
- Develop and compare models with **purged/embargoed walk‑forward** as the main evaluation engine. citeturn3search3turn3search4  
- Use **nested temporal validation** for tuning if computationally feasible; otherwise limit tuning and freeze early. citeturn4search9  
- Report final headline results on a **recent untouched lockbox**, with walk‑forward distributions as supporting evidence. citeturn2search5turn4search9  
- If you predict probabilities/uncertainty, include calibration/proper scoring rules as first‑class outcomes. citeturn2search1turn5search1

**Most dangerous mistake you could make next.** Using the newest block repeatedly for tuning or decisions (“peeking”), or ignoring horizon overlap and reporting inflated results from leakage. citeturn3search3turn4search9

**What you should absolutely not do.** Random k‑fold cross‑validation, or any evaluation that mixes time order or fails to control label overlap for multi‑horizon tasks. citeturn2search5turn3search3

**Guiding philosophy for the strongest academically defensible evaluation.**  
Your evaluation must be engineered as a *scientific instrument* with: (i) strict temporal causality, (ii) overlap control, (iii) separation of selection vs final reporting, and (iv) explicit accounting for the risk of backtest overfitting under multiple trials. citeturn3search3turn4search9turn4search5