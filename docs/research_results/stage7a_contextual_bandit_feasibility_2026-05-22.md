# Stage 7A Contextual-Bandit Feasibility Memo

Status: executed research-only Stage 7A memo. This memo does not implement a contextual-bandit layer, train a policy, mutate data, call providers, rerun benchmarks, reinterpret Stage 6, or approve Stage 7B/7C.

## Scope Checkpoint

Stage 7A was evaluated against the current completed Stage 6 repository state:

| Area | Current state |
| --- | --- |
| Protected target | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | Reproducible top-50 liquid large-cap set. |
| Providers | Twelve Data OHLCV, Alpha Vantage news, SEC static/company support only. |
| Alignment | Same-day as-of-close; after-hours and non-trading-day news roll forward. |
| Evaluation doctrine | Purged-plus-embargoed walk-forward development evaluation plus final untouched lockbox. |
| Current result | Stage 6 serious packet passed with result class `clean_null` and comparability `limitation_bearing`. |
| Current runtime boundary | Local CLI/artifact-driven research pipeline; no product API, live inference API, service, or dashboard. |

The current repository has no active contextual-bandit, reinforcement-learning, policy-gradient, DQN, PPO, actor-critic, LinUCB, logged-propensity, or bandit-policy implementation. Active implementation remains a supervised forecasting and benchmark-reporting pipeline through Stage 6.

## Evidence Base

Repository evidence used:

| Evidence | Relevant facts |
| --- | --- |
| Stage 3 feature/label artifact | `117750` rows, `471` as-of dates, `50` tickers, `46330` rows with aligned news, `71420` no-news rows, `59610` provider-truncation-risk rows. |
| Last 252 trading dates from Stage 3 | Start `2025-02-13`, `63000` rows, `16350` rows with news, `3270` ticker-date rows with news, `51960` provider-truncation-risk rows. |
| Last calendar-ish year from Stage 3 | Start `2025-02-14`, `251` dates, `62750` rows, `16340` rows with news, `3268` ticker-date rows with news. |
| Stage 4 split artifact | `9` development folds, final lockbox `2025-09-30` through `2026-02-13`, `1059750` split-assignment rows. |
| Stage 4 role/news counts | Validation has `47250` unique role rows with `5485` news rows; lockbox has `23750` unique role rows with `11815` news rows; train has `73500` unique role rows with `31730` news rows. |
| Stage 5 prediction artifact | `8` model IDs, `360` model-fit records, `360` preprocessing-fit records, `2088000` saved validation/lockbox prediction rows. |
| Stage 6 benchmark artifact | `800` metric rows, `800` ranking diagnostic rows, `800` paired-comparison rows, serious packet `passed`, result class `clean_null`, comparability `limitation_bearing`. |

External method references used:

| Source | Stage 7A use |
| --- | --- |
| Li et al., contextual-bandit news recommendation / LinUCB-style setting, `https://arxiv.org/abs/1003.0146` | Contextual action selection with observed context and delayed/partial reward framing. |
| Auer 2002 finite-time bandit confidence-bound analysis, `https://jmlr.csail.mit.edu/papers/v3/auer02a.html` | Exploration/exploitation and confidence-bound caution. |
| Dudik, Langford, Li doubly robust policy evaluation and learning, `https://arxiv.org/abs/1103.4601` | Offline policy evaluation requirements and missing-propensity blocker. |
| Bubeck and Cesa-Bianchi bandit regret survey, `https://arxiv.org/abs/1204.5721` | General regret/evaluation framing and limitations. |

## Feasibility Conclusion

Contextual bandits are conceptually appropriate only as a future experimental policy layer on top of the existing supervised artifact stack. They are not a direct upgrade to Stage 6 and cannot turn the Stage 6 `clean_null` result into a positive result.

The best scientific framing is: use Stage 3 features and/or Stage 5 saved predictions as context; define an action such as choosing a ticker, top-k basket, horizon, or abstain decision; reveal a delayed reward from frozen forward excess-return labels; evaluate under a predeclared historical replay protocol. This can test whether an adaptive decision policy uses the existing signals better than static ranking baselines, but it is a new policy/evaluation problem rather than the same supervised benchmark.

A last-year, news-days-only daily replay is feasible as a diagnostic design idea, but not as a directly comparable continuation of Stage 6. It filters out many no-news rows, changes the decision population, concentrates provider-truncation risk, and overlaps heavily with the Stage 6 final lockbox if the final year is interpreted literally. It must be treated as a separate benchmark family or predeclared diagnostic with no Stage 6 comparability claim.

## Candidate Contexts

| Context source | Feasibility | Notes |
| --- | --- | --- |
| Stage 3 market features | Feasible. | Preserves current feature artifact semantics and can support market-only bandit baselines. |
| Stage 3 event-state features | Feasible with limitations. | Includes deterministic event-state vectors and news/no-news/truncation flags; Alpha Vantage completeness remains limitation-bearing. |
| Stage 5 saved model predictions | Feasible for policy-on-predictions. | Useful for supervised-ranking baselines and bandit contexts; must not refit models using lockbox feedback. |
| Raw news text | Not recommended for Stage 7A path. | Would expand scope beyond current deterministic feature artifacts and invite provider/text-processing decisions. |
| Stage 6 metrics/results | Not a policy context. | Metrics are reporting evidence, not daily decision-state inputs. |

## Candidate Action Spaces

| Action space | Feasibility | Scientific cost |
| --- | --- | --- |
| Choose one ticker per day per horizon | High. | Simplest contextual-bandit mapping, but noisy and sensitive to single-name idiosyncrasy. |
| Choose top-k equal-weight basket per day per horizon | High. | More stable than one ticker; reward can average realized forward excess returns. |
| Choose horizon-specific rank rule | Medium. | Allows horizon selection but mixes decision targets unless predeclared carefully. |
| Choose model or feature branch for ranking | Medium. | Treats model selection as action; risks becoming post-Stage-6 result mining if not separated. |
| Choose abstain/cash | Medium. | Requires explicit reward baseline, e.g. zero excess return, and careful non-trading-profitability wording. |
| Choose weights/portfolio allocation | Low for first pass. | Converts the task toward trading/portfolio evaluation, requiring costs, constraints, liquidity, risk, and stronger governance. |

The most conservative Stage 7B option is a top-k basket policy per fixed horizon using frozen Stage 3/Stage 5 contexts and frozen forward-excess-return labels. It preserves the target family better than portfolio-allocation language.

## Reward Options

| Reward | Feasibility | Governance note |
| --- | --- | --- |
| Realized forward excess return for chosen ticker/horizon | High. | Directly preserves Stage 3 label semantics; no trading-profitability claim. |
| Mean realized forward excess return for chosen top-k basket | High. | Stabilizes single-name noise while preserving target semantics. |
| Rank-normalized realized forward excess return within date/horizon | Medium. | Reduces scale instability but changes the reward from the original numeric target. |
| Directional hit or top-quantile hit | Medium-low. | Easier for bandit reward, but changes the supervised target into classification/ranking. |
| Realized trading profit after costs | Not appropriate for first Stage 7 path. | Requires separate trading protocol, transaction-cost assumptions, and stronger claims than Stage 6 supports. |
| Utility/risk-adjusted portfolio reward | Not appropriate for first Stage 7 path. | Requires portfolio/risk benchmark family and explicit owner approval. |

The preferred research-safe reward family is forward excess return, either single-ticker or equal-weight top-k average. It should be reported as historical label reward, not investable profit.

## Daily Update Replay Design

In a historical replay, daily update should mean the policy updates only after rewards become observable for the relevant horizon. For a `20d` horizon, a decision made on date `t` cannot update from that action until roughly `t+20` trading days, and purge/embargo logic must prevent future-label leakage. Updating immediately on the next calendar day with future forward returns would leak labels.

Safe replay requirements:

| Requirement | Reason |
| --- | --- |
| Predeclare action space, reward, eligible dates, context columns, and update cadence before viewing policy results. | Prevents metric shopping and post-result design changes. |
| Respect horizon-specific reward delay. | Prevents using future returns before they are known. |
| Fit any preprocessing or context normalization only on history available at that replay date. | Preserves train-fold-only discipline. |
| Keep Stage 6 lockbox out of design iteration. | Preserves final lockbox integrity. |
| Report news-days-only diagnostics separately from all-row Stage 6 evidence. | Prevents silent comparability drift. |

## News-Days-Only Filter Risk

News-days-only replay is scientifically interesting because it focuses the policy on dates where event-state features should matter most. It is also a major comparability break.

Risks:

| Risk | Consequence |
| --- | --- |
| Dropping no-news rows changes the row population. | Results no longer answer the Stage 6 all-row benchmark question. |
| News arrival is not random. | The filter may condition on event intensity, volatility, firm attention, or provider coverage. |
| Alpha Vantage truncation risk remains high. | A news-days-only subset may overrepresent provider-limited windows and does not prove article completeness. |
| Daily action availability changes. | Some dates/tickers disappear, affecting random and market-only baselines. |
| Selection can leak design intent if tuned after result inspection. | The subset must be predeclared before evaluation. |

Conclusion: news-days-only should be allowed only as a separate diagnostic or new benchmark family, never as if it were comparable to Stage 6 all-row evidence.

## Last-Year And Lockbox Risk

The user's last-year idea maps to roughly `2025-02-13` onward in the current Stage 3 artifact. That window has enough rows for a diagnostic replay, including about `3270` news-bearing ticker-date rows in the last 252 trading dates. However, the current Stage 4 lockbox is `2025-09-30` through `2026-02-13`, so a last-year replay overlaps the final untouched Stage 6 lockbox.

Hard rule: Stage 6 lockbox data cannot be used for contextual-bandit design iteration, hyperparameter selection, reward choice, action-space choice, or protocol selection. If the user wants a last-year replay that includes the current lockbox, the repo needs an explicitly approved new benchmark family/protocol and must stop treating that evaluation as a continuation of the Stage 6 lockbox claim.

Safer alternatives for Stage 7B comparison:

| Alternative | Benefit | Cost |
| --- | --- | --- |
| Development-only replay before lockbox | Preserves Stage 6 lockbox for any future final read. | Less recent data; fewer news rows. |
| Nested replay inside development folds | Better separation between policy design and evaluation. | More complex and fewer effective samples. |
| New Stage 7 benchmark family with its own lockbox | Honest if last-year evaluation is the priority. | Breaks direct Stage 6 comparability and requires approval. |
| Pure diagnostic using lockbox with no tuning and no claim | Can illustrate behavior but not optimize decisions. | Cannot be used to choose the final Stage 7 protocol. |

## Offline Evaluation Limits

The current repository has supervised labels and saved predictions. It does not have logged historical actions from a behavior policy or logged action propensities.

| Offline evaluation method | Fit to current repo | Limitation |
| --- | --- | --- |
| Full-information historical simulation | Feasible if all action rewards are known from labels. | This is simulated decision replay, not off-policy evaluation of a real logged policy. |
| Replay evaluation of logged actions | Not feasible for real historical behavior. | No logged action stream exists. |
| Inverse propensity weighting | Blocked for real logged-policy claims. | No behavior-policy propensities exist. |
| Doubly robust evaluation | Blocked for standard logged-policy claims. | Requires propensities and a reward model; current artifacts lack logged propensities. |
| Randomized simulated logger | Feasible only as a new predeclared simulation. | Simulated propensities support internal experiments, not real historical deployed-policy claims. |

For Stage 7B, the honest wording is `historical full-information bandit-style replay` or `simulated contextual-bandit policy evaluation`, not `validated offline policy evaluation of a deployed behavior policy`.

## Baseline Requirements

Before any bandit value claim, Stage 7B/7C would need baseline families that match the exact action/reward/date protocol:

| Baseline | Why required |
| --- | --- |
| Random eligible ticker or random eligible top-k | Establishes chance performance under the filtered eligible set. |
| Epsilon-random policy | Separates exploration mechanics from learned context value. |
| Market-only supervised ranking | Tests whether event-state context adds anything beyond OHLCV-derived features. |
| Stage 5 supervised prediction ranking | Tests whether a bandit policy beats direct use of the existing supervised predictions. |
| Static best historical validation rule | Detects if adaptive updating is unnecessary. |
| Abstain/cash baseline if abstain is allowed | Prevents abstain reward from being unanchored. |

Any baseline using Stage 5 predictions must use only predictions/features that would be available at that replay date and must not reselect the Stage 5 roster after Stage 6 result inspection.

## Feasibility Matrix

| Option | Feasibility | Main blocker or risk | Stage 7B priority |
| --- | --- | --- | --- |
| Development-only top-k contextual-bandit replay using Stage 3 features and forward-excess-return reward | Medium-high | Smaller sample after respecting folds and reward delays. | High. |
| Development-only policy-on-Stage-5-predictions replay | Medium-high | Must avoid post-Stage-6 model-selection leakage. | High. |
| Last-year news-days-only replay including current lockbox | Medium technically, low governance fit | Lockbox reuse and comparability break. | Compare only if framed as new benchmark family. |
| All-row daily replay preserving no-news rows | Medium | More comparable to Stage 6, but less focused on news-event days. | High as a comparator to news-days-only. |
| Logged-propensity IPW/DR off-policy evaluation | Low | Missing logged propensities and behavior actions. | Low unless a simulated logger is predeclared. |
| Trading-profit contextual bandit | Low | Requires trading protocol, costs, risk controls, and new claims. | Not recommended. |

## Hard Blockers

| Blocker | Blocks |
| --- | --- |
| No logged behavior actions or propensities. | Standard IPW/DR off-policy evaluation claims for a real logged policy. |
| Current Stage 6 lockbox must remain untouched for design iteration. | Last-year policy tuning if it overlaps `2025-09-30` through `2026-02-13`. |
| News-days-only changes the evaluated row population. | Direct comparability to Stage 6 all-row benchmark. |
| Alpha Vantage provider completeness is not claimed. | Any claim that news-driven policy behavior reflects complete news coverage. |
| No current bandit/RL implementation exists. | Any statement that the repo already trains or evaluates contextual-bandit policies. |
| Stage 6 result policy is frozen. | Any attempt to reinterpret `clean_null` as positive due to Stage 7A research. |

## Stage 7B Decision Handoff

Stage 7B should compare, without implementing, these decisions:

| Decision | Options to compare |
| --- | --- |
| Benchmark family | Development-only diagnostic, new Stage 7 benchmark family, or lockbox-free protocol-design study. |
| Eligible rows | All rows, news-days-only, or paired all-row plus news-days-only diagnostics. |
| Action space | Single ticker, top-k basket, horizon-specific rank choice, model-choice action, or abstain-enabled action. |
| Reward | Single-name forward excess return, top-k average forward excess return, rank-normalized reward, or hit-based reward. |
| Context | Stage 3 market/event-state features, Stage 5 saved predictions, or combined frozen feature-plus-prediction context. |
| Update cadence | Reward-delay-correct daily updates, weekly updates, fold-boundary updates, or no online updates. |
| Evaluation | Full-information historical replay, nested development replay, simulated randomized logger, or new predeclared benchmark family. |
| Baselines | Random, epsilon-random, market-only ranking, supervised prediction ranking, static validation rule, and abstain baseline if relevant. |

Stage 7B should not ask for code approval until these choices are scored and the lockbox/comparability consequences are explicit.

## Non-Claims

- This memo does not claim a contextual bandit will improve accuracy or ranking performance.
- This memo does not claim trading profitability, executable strategy readiness, or investable portfolio performance.
- This memo does not claim provider-level Alpha Vantage article completeness.
- This memo does not change the Stage 6 `clean_null` result class or `limitation_bearing` comparability classification.
- This memo does not approve Stage 7B, Stage 7C, implementation, policy training, provider calls, data updates, benchmark reruns, or visualization work.
