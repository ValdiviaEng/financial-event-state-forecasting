# Stage 7B Contextual-Bandit Decision Draft

Status: executed draft-only Stage 7B decision comparison. This memo's options were later answered in `ScopeDecisionLog.md`; the memo remains historical draft evidence, not the active execution record. This memo itself did not approve a contextual-bandit protocol, implement code, train a policy, mutate data, call providers, rerun benchmarks, reinterpret Stage 6, execute Stage 7C, or change benchmark comparability.

## Current Repo Context

Stage 7B is being drafted after completed Stage 6 and executed research-only Stage 7A.

| Area | Current state |
| --- | --- |
| Active project mode | Local CLI/artifact-driven research system only; no user-facing API, service, dashboard, live inference product, or trading system. |
| Protected objective | Test event-state incremental value beyond market-only baselines. |
| Protected target | Forward excess returns. |
| Protected horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Protected universe | Reproducible top-50 liquid large-cap set. |
| Protected providers | Twelve Data OHLCV, Alpha Vantage news, SEC static/company support only. |
| Protected alignment | Same-day as-of-close; after-hours and non-trading-day news roll forward. |
| Protected evaluation doctrine | Purged-plus-embargoed walk-forward development evaluation plus final untouched lockbox. |
| Stage 3 artifact | `117750` rows, `471` as-of dates, `46330` rows with aligned news, `71420` no-news rows, `59610` provider-truncation-risk rows. |
| Stage 4 artifact | `9` monthly development folds, lockbox `2025-09-30` through `2026-02-13`, `1059750` split-assignment rows. |
| Stage 5 artifact | Frozen roster `phase1_top50_pragmatic_broader_sklearn_v1`, `8` model IDs, `2088000` saved validation/lockbox prediction rows. |
| Stage 6 artifact | Serious packet `passed`, result class `clean_null`, comparability `limitation_bearing`, `800` metric rows, `800` ranking diagnostic rows, `800` paired-comparison rows. |
| Stage 7A result | Contextual bandits are feasible only as a future experimental policy layer on frozen Stage 3 features and/or Stage 5 predictions; not a Stage 6 result upgrade. |
| Existing bandit/RL implementation | Not evidenced in repository materials. Search during Stage 7A found no active contextual-bandit/RL implementation. |

## Rules And Context Files Read

| File | Active Stage 7B relevance |
| --- | --- |
| `Stage7BPrompt.md` | Defines Stage 7B mission, decisions, required matrix columns, non-implementation boundary, and final response expectations. |
| `docs/research_results/stage7a_contextual_bandit_feasibility_2026-05-22.md` | Supplies Stage 7A feasibility conclusion, action/reward/evaluation options, blockers, and Stage 7B handoff. |
| `Stage7APrompt.md` | Confirms Stage 7A was research-only and did not approve Stage 7B/7C or implementation. |
| `Stage6Prompt.md` | Confirms Stage 6 result class, comparability, artifact packet, and stop conditions. |
| `AgentRules.md` | Requires approval gates, truth hierarchy, benchmark integrity, and decision matrices for serious design choices. |
| `docs/agent/AgentTemplates.md` | Requires at least 3 options and 0-10 scoring across 6 mandatory categories plus exactly 4 context-specific categories for approval-path decisions. |
| `docs/agent/AgentMemory.md` | Requires request/task/event logging, evidence, drift checkpoints, and reconciliation. |
| `docs/agent/AgentResearchWorkflows.md` | Requires repository-first research, additive research files, distinction between repo fit and scientific attractiveness, and no hidden winner selection. |
| `ScopeDecisionLog.md` | Owns protected scope and now receives pending/unanswered Stage 7B draft decisions. |
| `ResearchTruth.md` | Records active truth, Stage 2-6 materialization, current limitations, and non-claims. |
| `ProjectDefinition.md` | Defines phase-1 local artifact-driven project boundary and non-product scope. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Defines lockbox, fold-local preprocessing, saved-prediction, metric, and contamination blockers. |
| `docs/Benchmark_Testing.md` | Defines serious-run comparability rules, invalidation triggers, and Stage 6 `clean_null`/`limitation_bearing` status. |
| `configs/models.yaml` | Records frozen Stage 5 roster, feature sets, saved-prediction schema, and no-metric claim policy. |
| `configs/evaluation.yaml` | Records frozen Stage 6 metric/result policy, selected market-hurdle policy, and lockbox policy. |
| `docs/Execution_Plan.md`, `docs/Detailed_Execution_Stages.md`, `Complete_guidebook.txt` | Current stage status and discoverability context. |

## Scoring Notes

Scoring scale: `0` to `10`, higher is better for every scored category.

Mandatory categories:

| Category | Meaning in this Stage 7B draft |
| --- | --- |
| Accuracy | Expected ability to produce useful, scientifically interpretable policy evidence. |
| Complexity | Lower implementation and conceptual burden scores higher. |
| Compute Intensity | Lower compute and operational burden scores higher. |
| Security | Lower credential, provider, publication, and sensitive-artifact risk scores higher. |
| Compatibility | Better fit with current Stage 2-6 artifacts and protected phase-1 definitions scores higher. |
| Governance | Better auditability, lockbox discipline, approval safety, and benchmark-integrity fit scores higher. |

Context-specific categories:

| Category | Meaning |
| --- | --- |
| Scientific Validity | Whether the option can support a defensible research claim. |
| Leakage Safety | Lower risk of future-label, lockbox, preprocessing, or selected-on-results leakage scores higher. |
| Comparability Preservation | Better preservation of Stage 6 boundaries, or clearer new-family separation, scores higher. |
| Data Readiness | Better fit to already materialized Stage 3, Stage 4, and Stage 5 artifacts scores higher. |

Known evidence limits:

- No logged historical actions or propensities exist, so real-policy IPW/DR off-policy evaluation claims are blocked.
- Alpha Vantage provider-level article completeness is not claimed.
- Stage 6 lockbox data cannot be used for Stage 7 design iteration.
- Any news-days-only protocol changes the evaluated row population and is not directly comparable to Stage 6 all-row evidence.

## Decision Bundle Options

These are bundle-level paths. They are not approved choices.

| Option | Brief explanation | Accuracy | Complexity | Compute Intensity | Security | Compatibility | Governance | Scientific Validity | Leakage Safety | Comparability Preservation | Data Readiness | User value | Draft recommendation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| Option A: Development-only research diagnostic | Use development folds only, keep lockbox out, compare all-row and news-days diagnostics, use frozen Stage 3/5 contexts, top-k reward-delay-correct replay, and mandatory baselines. | 7 | 7 | 8 | 9 | 8 | 9 | 8 | 9 | 8 | 8 | High for safe Stage 7 learning without damaging Stage 6. | Recommended draft path, pending owner approval. |
| Option B: New Stage 7 benchmark family | Define a separate contextual-bandit benchmark family, ideally after approved data update/new holdout, with its own lockbox and result policy. | 8 | 4 | 5 | 8 | 5 | 7 | 8 | 7 | 6 | 5 | High for later claim-bearing work, but too heavy for immediate draft. | Keep as future path, pending owner approval. |
| Option C: Last-year news-days-only sandbox | Use recent one-year/news-bearing rows, likely including current lockbox, as a sandbox with explicit non-comparability and no development claims. | 5 | 6 | 7 | 8 | 4 | 4 | 5 | 3 | 3 | 7 | High for intuition, weak for governed decisions. | Not recommended for protocol selection; diagnostic only if approved later. |

Option notes:

| Option | Main pros | Main cons |
| --- | --- | --- |
| Option A | Preserves Stage 6 lockbox; uses existing artifacts; lowest governance risk; can compare all-row vs news-days behavior without making a Stage 6-comparable claim for news-days. | Less recent than a literal last-year replay; smaller effective sample after reward delays; cannot claim deployment-style policy performance. |
| Option B | Honest route if a contextual-bandit result should become claim-bearing; can create a fresh holdout and predeclared protocol. | Requires new benchmark-family approval, more docs/tests/code, likely data update, and comparability separation from Stage 6. |
| Option C | Closest to the user's original last-year/news-days-only intuition; easy to understand. | Overlaps current lockbox, changes row population, concentrates provider-truncation risk, and cannot be used for design iteration without new benchmark-family approval. |

## Pending Decision Drafts

All decisions below are pending and unanswered in `ScopeDecisionLog.md`. The recommended choices are draft recommendations only.

| Pending ID | Decision | Options compared | Scientific validity | Leakage risk | Comparability impact | Implementation complexity | Data requirements | User value | Draft recommendation | Pending status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S7B-DQ-001 | Stage 7 purpose | Research diagnostic only; separate benchmark family; later production-style policy prototype | Diagnostic supports limited research claims; separate family supports stronger future claims; production prototype is premature. | Diagnostic is safest; separate family depends on fresh protocol; production prototype invites hidden scope expansion. | Diagnostic preserves Stage 6; separate family is explicitly non-comparable; production prototype is not phase-1 comparable. | Diagnostic low/medium; separate family high; production high. | Existing Stage 3/4/5 enough for diagnostic; separate family may need new holdout; production needs new infra. | Clarifies whether Stage 7 is learning, claim-bearing, or product-like. | Research diagnostic only. | Pending/unanswered. |
| S7B-DQ-002 | Evaluation segment | Development folds only; new post-lockbox holdout after approved data update; separate sandbox using copied historical rows | Development-only is valid for design; new holdout is strongest later; sandbox is illustrative only. | Development-only protects current lockbox; new holdout can be safe if predeclared; sandbox risks accidental lockbox tuning. | Development-only preserves Stage 6; new holdout is new family; sandbox is not comparable. | Development-only medium; new holdout high; sandbox low/medium. | Development-only uses existing splits; new holdout needs approved data/update; sandbox uses copied rows. | Determines whether results can guide later work safely. | Development folds only for Stage 7B/7C draft. | Pending/unanswered. |
| S7B-DQ-003 | Row filter | All rows; news-days only with explicit non-comparability; two-track all-row plus news-days diagnostic | All rows best preserves Stage 6 question; news-days isolates event days; two-track shows both. | All rows safest; news-days risks selected subset; two-track is safe if predeclared. | All rows closest to Stage 6; news-days not comparable; two-track separates claims. | All rows medium; news-days low; two-track medium/high. | All rows use all Stage 3 rows; news-days uses news flags; two-track uses both. | Shows whether policy behavior depends on news availability. | Two-track: all-row primary diagnostic plus news-days secondary non-comparable diagnostic. | Pending/unanswered. |
| S7B-DQ-004 | Time span | Last 1 year sandbox; full clean window replay; development-only rolling replay | Development-only rolling replay best balances validity and leakage control. | Last-year overlaps lockbox; full clean window can leak if not fold-safe; development-only rolling is safest. | Last-year not comparable if lockbox used; full clean window needs careful role split; development-only preserves Stage 6. | Last-year low; full clean window medium; development-only rolling medium. | Last-year has recent rows; full clean window uses all Stage 3; development-only uses Stage 4 folds. | Determines sample size and practical realism. | Development-only rolling replay. | Pending/unanswered. |
| S7B-DQ-005 | Action space | Choose one ticker per day; choose top-k basket; choose horizon-specific model/rank; choose abstain/cash | Top-k basket is more stable than single ticker and less scope-expanding than allocation. | Single ticker noisy; top-k manageable; horizon/model choice risks post-Stage-6 selection; abstain requires extra reward definition. | Top-k preserves target semantics; model-choice may mine Stage 6; abstain changes policy meaning. | Single ticker low; top-k medium; model/rank medium; abstain medium/high. | Top-k needs labels and eligible rows; abstain needs zero/cash reward convention. | Directly maps predictions to decision-style diagnostics. | Top-k equal-weight basket per fixed horizon. | Pending/unanswered. |
| S7B-DQ-006 | Reward | Forward excess return by horizon; rank-normalized reward; sign hit; cost-adjusted exploratory diagnostic only | Forward excess return preserves current target; rank/hit change target semantics; cost-adjusted is trading-adjacent. | Forward excess return safest; rank/hit can hide target drift; cost-adjusted invites trading claims. | Forward excess return best preserves Stage 6 target family; others create new diagnostics/families. | Forward return low; rank/hit medium; cost-adjusted high. | Forward return labels already exist; cost-adjusted requires cost assumptions. | Determines whether Stage 7 remains scientifically connected to Stage 3/6. | Mean forward excess return of selected top-k basket by horizon. | Pending/unanswered. |
| S7B-DQ-007 | Algorithm class | LinUCB; Thompson sampling; epsilon-greedy regression; non-bandit supervised ranking baseline | Epsilon-greedy regression is simple and transparent; LinUCB/Thompson are credible but more assumptions; supervised ranking is mandatory baseline, not bandit. | All need delayed-reward discipline; complex methods add tuning risk. | Epsilon-greedy and LinUCB can be separate Stage 7 branch; supervised ranking remains closest to Stage 5. | Epsilon-greedy medium; LinUCB medium/high; Thompson high; supervised baseline low. | All use existing features/predictions; no propensities unless simulated logger is defined. | Shows whether adaptivity adds value beyond supervised ranking. | Epsilon-greedy regression as first bandit, with supervised ranking as mandatory baseline. | Pending/unanswered. |
| S7B-DQ-008 | Context | Stage 3 features only; Stage 5 predictions as context; combined feature and prediction context | Combined context is most informative if frozen; Stage 5 predictions alone are simpler; Stage 3 alone tests raw context. | Combined context requires careful fold-time availability; predictions alone lowest preprocessing risk. | Combined remains a new policy layer; predictions alone best leverages existing artifacts. | Stage 3 medium; Stage 5 predictions low/medium; combined medium/high. | Existing Stage 3 features and Stage 5 predictions exist; no raw news required. | Determines whether policy learns from features, model scores, or both. | Combined frozen Stage 3 features plus Stage 5 predictions, with an ablation for predictions-only. | Pending/unanswered. |
| S7B-DQ-009 | Baselines | Market-only policy; event-state supervised ranker; random policy; no-news abstain policy | All are needed to avoid overclaiming bandit value. | Baselines are safe if predeclared and fold-local; no-news abstain needs explicit reward. | Baselines preserve interpretability and guard against false Stage 7 positives. | Random low; market/event ranker medium; abstain medium. | Uses Stage 3 features, Stage 5 predictions, and no-news flags. | Essential for deciding whether bandit adaptation adds anything. | Require random, epsilon-random, market-only ranking, Stage 5 supervised ranking, static validation rule, and abstain baseline if abstain is approved. | Pending/unanswered. |
| S7B-DQ-010 | Output status | Research artifact only; saved policy diagnostics; future executable Stage 7C docs; no trading signal | Saved diagnostics are useful without product claims; research-only is safest; trading signal is out of scope. | Research/diagnostics safe; executable docs require approval; trading signal unsafe. | Research/diagnostics do not alter Stage 6; executable docs define future branch; trading signal not comparable. | Research low; diagnostics medium; Stage 7C docs medium; trading high. | Existing artifacts enough for design docs; implementation needs tests. | Determines what the repo can do next without overclaiming. | Saved policy diagnostics as future design target; no trading signal. | Pending/unanswered. |

## Draft Bundle If Later Approved

If a future owner decision chooses the conservative path, the coherent draft bundle would be:

| Dimension | Draft choice |
| --- | --- |
| Purpose | Research diagnostic only. |
| Evaluation segment | Development folds only; keep the current Stage 6 lockbox out of design iteration. |
| Row filter | Two-track diagnostic: all-row primary diagnostic plus news-days-only secondary non-comparable diagnostic. |
| Time span | Development-only rolling replay using Stage 4 fold boundaries and reward-delay-correct updates. |
| Action space | Top-k equal-weight basket per fixed horizon. |
| Reward | Mean realized forward excess return of selected top-k basket by horizon. |
| Algorithm | Epsilon-greedy regression as first bandit, with supervised ranking as mandatory non-bandit baseline. |
| Context | Frozen combined Stage 3 features plus Stage 5 predictions, with predictions-only ablation. |
| Baselines | Random, epsilon-random, market-only ranking, Stage 5 supervised ranking, static validation rule, and abstain baseline only if abstain is approved. |
| Output | Saved policy diagnostics only; no trading signal and no Stage 6 reinterpretation. |

This bundle remains pending/unanswered. It is not approved by this memo.

## Non-Approval List

The following are not approved by this Stage 7B draft:

- Contextual-bandit or reinforcement-learning implementation.
- Policy training or historical replay execution.
- Stage 7C documentation integration as an approved protocol.
- Use of the current Stage 6 lockbox for protocol design, tuning, reward selection, action-space selection, or debugging.
- Treating news-days-only results as directly comparable to Stage 6 all-row results.
- Logged-policy IPW or doubly robust claims without logged actions and propensities.
- Trading-profitability, buy/sell, portfolio, cost-adjusted primary evidence, or investable-signal claims.
- Provider changes, universe changes, target changes, horizon changes, metric/result-policy changes, or benchmark-comparability changes.
- Live provider calls, data mutation, benchmark reruns, or visualization/product work.

## Blocker List

| Blocker | Impact |
| --- | --- |
| Missing logged behavior actions and propensities | Blocks real-policy IPW/DR off-policy evaluation claims. |
| Current Stage 6 lockbox boundary `2025-09-30` through `2026-02-13` | Blocks last-year design iteration unless a new benchmark family/protocol is approved. |
| News-days-only filtering changes row population | Blocks direct comparability to Stage 6 all-row evidence. |
| Alpha Vantage provider-level article completeness not claimed | Blocks claims that news-conditioned decisions reflect complete news coverage. |
| No current contextual-bandit/RL implementation | Blocks any claim that the repo already trains or evaluates bandit policies. |
| Stage 6 result policy frozen | Blocks using Stage 7 draft to reinterpret Stage 6 `clean_null`. |

## ScopeDecisionLog Pending Entries

The pending Stage 7B decisions are recorded in `ScopeDecisionLog.md` as `S7B-DQ-001` through `S7B-DQ-010`. Their status is `Pending/Unanswered`. The decision log entries intentionally preserve recommendations as drafts only.

## Final Non-Claims

- This memo does not claim contextual-bandit performance.
- This memo does not claim improved accuracy, improved ranking, or trading profitability.
- This memo does not create a new benchmark result.
- This memo does not change Stage 6 `clean_null` or `limitation_bearing`.
- This memo does not approve the draft recommended bundle.
