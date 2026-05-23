# Scope Definition

## 1. Purpose
This document is a decision-ready scope ledger for the repository in its current post-archive state. It is meant to be used before any new implementation work resumes, so the owner can decide what the active project is, what the archived snapshot is allowed to influence, and which benchmark family will govern future claims. Facts in this document are classified as `Confirmed`, `Inferred`, `Contradicted`, or `Unknown`; research text was not promoted to truth unless current repository evidence also supports it. Where sources disagree or appear stale, the disagreement is exposed instead of silently resolved. The goal is to turn the repository's existing governance, archived design, code evidence, research syntheses, and paper notes into a smaller set of explicit owner decisions.

## 2. Source Inventory
| Source path | Source type | Why it matters | Reliability notes |
| --- | --- | --- | --- |
| `AgentRules.md` | `AgentRules` | Defines binding truth hierarchy, approval gates, contradiction handling, and benchmark comparability rules. | Highest-authority governance source for repository behavior. |
| `docs/agent/AgentAppendices.md` | `Agent doc` | Defines appendix loading order and which supporting docs are binding for this task. | High reliability for governance structure; not theory truth. |
| `docs/agent/AgentMemory.md` | `Agent doc` | Defines continuity, evidence, and interaction-log rules. | High reliability for operational governance only. |
| `docs/agent/AgentGlossary.md` | `Agent doc` | Defines canonical meanings of stale-risk, approval gate, benchmark comparability change, and related terms. | High reliability for terminology. |
| `docs/agent/AgentTemplates.md` | `Agent doc` | Defines required record structures for approvals, contradictions, evidence, and comparison records. | High reliability for record format, not substance. |
| `docs/agent/AgentResearchWorkflows.md` | `Agent doc` | Defines additive research rules, triple-verification, and no-winner comparison discipline. | High reliability for research-method constraints. |
| `docs/agent/AgentCompliance.md` | `Agent doc` | Defines what governance structure the validator must enforce. | High reliability for mechanical governance expectations. |
| `docs/agent/agent_log/Current_State.md` | `Agent doc` | Shows the currently approved task contract in the active root. | Reliable for current task history; not theory or product truth. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | `Agent doc` | Authoritative log of request and approval history for the active root. | Reliable for event history; not design truth. |
| `docs/research_results/foundational_deep_research.md` | `docs/research_results` | Strongest restart-era narrowing of the thesis question and design priorities. | Medium reliability; synthesis-heavy and partly historical, so evidence must be rechecked. |
| `docs/research_results/restarting_research.md` | `docs/research_results` | Broad repository-first restart reconstruction of project identity, scope, and risks. | Medium reliability; useful synthesis, but some claims are now stale. |
| `docs/research_results/restarting_research_literature_expansion.md` | `docs/research_results` | Extends restart research with broader literature and verified paper-note links. | Medium reliability; literature-backed but still synthesis, not owner approval. |
| `docs/research_results/restarting_research_literature_expansion_round2.md` | `docs/research_results` | Adds calibration, graph, regime, MoE, and purge/embargo source-caution findings. | Medium reliability; includes explicit uncertainty notes that must be preserved. |
| `docs/research_results/research_comparison.md` | `docs/research_results` | Defines the non-winner comparison framework across targets, features, representations, models, evaluation, and extensions. | Medium reliability; comparison framework, not final decision authority. |
| `docs/research_results/research_comparison_addendum_*.md` | `docs/research_results` | Category-specific measurable comparisons for targets, features, models, evaluation, event representations, extensions, and repo fit. | Medium reliability; useful tradeoff mapping, not final truth. |
| `docs/research_results/research_comparison_master_index.md` | `docs/research_results` | Shows intended reading structure for the comparison layer. | Medium reliability; index only. |
| `docs/research_results/logs/*.md` | `docs/research_results` | Preserve provenance of what research files were created and why. | Low-to-medium reliability for truth; high usefulness for detecting stale assumptions. |
| `docs/research_results/paper_notes/restarting_research/*.md` | `docs/research_results` | Triple-verified literature notes backing selected methodological and architectural claims. | Medium-to-high reliability for metadata and bounded support statements; several files explicitly retain uncertainty. |
| `docs/research_results/bkup/*.md` | `docs/research_results` | Historical duplicate research versions that reveal drift, stale claims, and citation inconsistencies. | Low reliability for current truth; valuable mainly as stale/contradictory evidence. |
| `LEGACY_DEPRECATION_SUMMARY.md` | `supporting file` | Confirms the root was intentionally cleared and the old implementation was archived wholesale. | High reliability for current repository state. |
| `scripts/validate_agent_governance.py` | `supporting file` | Mechanically defines active governance requirements; validates whether research claims about missing log files are still true. | High reliability for current governance structure. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/README.md` | `supporting file` | Confirms the snapshot is deprecated and reference-only. | High reliability for legacy-snapshot status. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/DEPRECATION_MANIFEST.txt` | `supporting file` | Records exactly what moved into the archived snapshot. | High reliability for archive scope. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/architecture_overview.md` | `supporting file` | Best concise statement of implemented legacy architecture and its explicit limitations. | High reliability for archived design intent and implemented module map. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/data_layout.md` | `supporting file` | Defines legacy storage layers, canonical tables, manifests, and adjusted-price separation. | High reliability for archived data architecture. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/evaluation_protocol.md` | `supporting file` | Defines out-of-sample evaluation, as-of-close alignment, purge/embargo, and metric families. | High reliability for archived evaluation doctrine. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/implementation_roadmap.md` | `supporting file` | Confirms what the legacy snapshot considered implemented versus intentionally deferred. | High reliability for archived implementation stage. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/RESEARCH_DESIGN_old.md` | `supporting file` | Largest older theory/design source; still important for hypotheses, targets, and older alignment examples. | Medium-to-high reliability; valuable but partly contradicted by later protocol. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/features/{labels.py,event_state.py}` | `supporting file` | Direct code evidence for horizons, target columns, event-state construction, and optional scalar enrichments. | High reliability for archived implemented behavior. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/split/{alignment_rules.py,purged_embargo_splits.py}` | `supporting file` | Direct code evidence for as-of-close alignment and purged/embargoed walk-forward logic. | High reliability for archived implemented behavior. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/data/corporate_actions.py` | `supporting file` | Direct code evidence for split normalization and local adjusted-price generation. | High reliability for archived implemented behavior. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/src/models/{baseline_models.py,multimodal_models.py}` | `supporting file` | Direct code evidence for baseline pipelines, simple multimodal gating, and optional company-profile branch. | High reliability for archived implemented behavior. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/reports/.../evaluation_summary.json` and `runs/.../*_training_summary.json` | `supporting file` | Show the currently visible empirical artifacts are smoke-scale only. | High reliability for current artifact size; low value for predictive claims. |
| `deprecated_version/legacy_snapshot_20260402T115014Z/tests/results/Expanded_Testing_20260319T121411Z.md` | `supporting file` | Provides the strongest historical evidence of broad legacy test execution and its then-open issues. | Medium reliability; historical run record, not current rerun proof. |

## 3. Theoretical Truth Baseline
| Truth ID | Statement | Classification | Evidence | Confidence score | Notes |
| --- | --- | --- | --- | ---: | --- |
| T-001 | The active repository root is currently a governance-first restart shell plus an archived legacy snapshot; it does not contain active-root `src/`, `configs/`, `tests/`, `README.md`, or `ExecutionFlow.md`. | Confirmed | Root directory listing; `LEGACY_DEPRECATION_SUMMARY.md` | 96 | This is current-state truth, not legacy-state truth. |
| T-002 | The archived legacy snapshot is explicitly deprecated, frozen, and not the active implementation source of truth. | Confirmed | `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`; `DEPRECATION_MANIFEST.txt` | 98 | Owner could later override this, but no such override is evidenced. |
| T-003 | The archived legacy snapshot still contains a real first-pass end-to-end research system with code, configs, data layers, runs, reports, and tests. | Confirmed | Legacy snapshot root directory listing; `architecture_overview.md`; `implementation_roadmap.md` | 96 | Archived implementation evidence exists even though it is not active truth. |
| T-004 | The legacy system goal is thesis-grade end-of-day forecasting using daily market data, aligned company news, optional company metadata, multi-horizon labels, market-only baselines, and a first multimodal market + event-state model. | Confirmed | `architecture_overview.md` | 94 | High-level archived design truth. |
| T-005 | The legacy design rejects raw price prediction and frames the problem as evolving event state plus market features for forward excess or residual returns. | Confirmed | `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md` cross-check | 95 | Supported directly in legacy theory, not just later synthesis. |
| T-006 | Legacy code builds 1, 5, 20, and 60-day labels for raw returns, excess returns, direction, and downside. | Confirmed | `src/features/labels.py` | 97 | Code-evidenced archived behavior. |
| T-007 | Legacy code builds daily event states from aligned articles and embeddings, with configurable lookback and decay, and can emit novelty, conflict, and density features. | Confirmed | `src/features/event_state.py` | 96 | Code-evidenced archived behavior. |
| T-008 | The implemented legacy alignment policy is as-of-close same-day: articles available by market close on date `t` may be used on `t`, while after-hours and non-trading-day articles roll forward. | Confirmed | `evaluation_protocol.md`; `src/split/alignment_rules.py` | 97 | This is the strongest implemented alignment evidence in the repo. |
| T-009 | An older legacy design document still contains a more conservative embargo-style example that delays use of published news by roughly two days. | Contradicted | `RESEARCH_DESIGN_old.md` alignment example; `evaluation_protocol.md`; `src/split/alignment_rules.py` | 95 | Historical methodology sources disagree; they are not silently reconcilable. |
| T-010 | Purged and embargoed walk-forward splitting is implemented and horizon-aware in the archived code. | Confirmed | `evaluation_protocol.md`; `src/split/purged_embargo_splits.py` | 96 | Strong archived benchmark-integrity evidence. |
| T-011 | Corporate-action handling and local adjusted-price generation are implemented and treated as label-validity infrastructure in the archived codebase. | Confirmed | `architecture_overview.md`; `src/data/corporate_actions.py` | 96 | Split safety is not only theoretical. |
| T-012 | The currently visible empirical artifacts are smoke-scale only and do not support thesis-level predictive claims. | Confirmed | `reports/eval_stage14_baseline/evaluation_summary.json`; `runs/baseline_stage14_eval_smoke/baseline_training_summary.json`; `runs/multimodal_stage13_smoke_fix/multimodal_training_summary.json` | 98 | Evidence is operational plumbing, not scientific closure. |
| T-013 | The active governance layer now has the required interaction-log files and currently passes the repository's governance validator. | Confirmed | `docs/agent/agent_log/Current_State.md`; `docs/agent/agent_log/Event_Ledger.ndjson`; `scripts/validate_agent_governance.py`; validator run output on 2026-04-10 | 98 | This invalidates older “missing log files” claims. |
| T-014 | Several research documents and logs that describe the validator as failing because active log files are missing are now stale. | Contradicted | `restarting_research.md`; `foundational_deep_research.md`; research logs; current validator run | 98 | Staleness is current and material. |
| T-015 | A historical 2026-03-19 legacy test run recorded broad coverage (`101 passed`, `1 failed`, `3 passed`, `1 skipped`) but not a fully green offline suite. | Confirmed | `tests/results/Expanded_Testing_20260319T121411Z.md` | 90 | This is historical run evidence, not current rerun proof. |
| T-016 | That historical NaN-related ridge-baseline failure is not clean current truth for the archived snapshot because `baseline_models.py` already includes median imputation in the sklearn pipelines. | Contradicted | `tests/results/Expanded_Testing_20260319T121411Z.md`; `src/models/baseline_models.py` | 72 | Either the report predates a later fix or the report analyzed a different code state. |
| T-017 | The archived multimodal architecture was intentionally kept simple, and the company-profile branch was optional rather than mature core functionality. | Confirmed | `architecture_overview.md`; `src/models/multimodal_models.py` | 94 | Important for extension-scope decisions. |
| T-018 | The research-comparison layer is intentionally profile-based and explicitly avoids final winner selection. | Confirmed | `research_comparison.md`; `research_comparison_addendum_*.md`; `AgentResearchWorkflows.md` | 95 | Comparison scores are not active approvals. |
| T-019 | The currently approved active task contract in the root concerns governance/research-workflow integration, not active implementation scope or product scope. | Confirmed | `docs/agent/agent_log/Current_State.md`; `Event_Ledger.ndjson` | 92 | No active owner-approved implementation contract is evidenced. |
| T-020 | Historically selected provider families are Twelve Data for market data, Finnhub for company news, and SEC EDGAR for KB/context support. | Confirmed | `RESEARCH_DESIGN_old.md`; `architecture_overview.md`; `restarting_research*.md` | 90 | Historical provider choice is clear even if future choice is still open. |
| T-021 | Exact current provider-plan adequacy, split-event completeness, and historical coverage quality for the intended future benchmark are not evidenced and still require manual verification. | Unknown | `implementation_roadmap.md`; `tests/results/Expanded_Testing_20260319T121411Z.md`; multiple paper/source notes marked “Uncertain, verify manually.” | 90 | This is materially important missing evidence. |
| T-022 | Benchmark comparability is a first-class scientific and governance constraint across the active governance layer and the restart-era research layer. | Confirmed | `AgentRules.md`; `AgentGlossary.md`; `evaluation_protocol.md`; `research_comparison.md` | 98 | This is one of the strongest recurring truths in the repository. |
| T-023 | No active-root document currently defines the final approved post-restart architecture, benchmark family, deployment mode, security boundary, or phase-1 scope. | Unknown | Root directory listing; `Current_State.md`; absence of active design docs required by `AgentRules.md` Section 7 | 94 | This is the main reason owner decisions are still required. |
| T-024 | Backup research files and several paper notes explicitly contain lower-trust or unresolved metadata, so research artifacts do not all deserve equal authority. | Confirmed | `docs/research_results/bkup/*.md`; `S01_purge_embargo_validation_source_note.md`; `P02`, `P14`, `P17`, `P22`, `P23` paper notes | 90 | Research trust must remain graded, not flattened. |

## 4. What Appears Already Decided
| Decision | Why it appears already decided | Evidence references | Confidence |
| --- | --- | --- | ---: |
| The project is not a raw price-prediction, intraday, HFT, or trading-bot project. | This framing is repeatedly rejected in legacy theory and restart research, and no active source overrides it. | `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md` | 95 |
| End-of-day scope is the intended temporal scope. | It is repeated in legacy design, archived architecture, and restart syntheses without contrary active evidence. | `architecture_overview.md`; `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md` | 95 |
| Event-state framing is preferred over isolated article-effect or sentiment-only framing. | This is stated in the main legacy design and reinforced across restart and comparison documents. | `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `research_comparison_addendum_event_representations.md` | 94 |
| Market-only baselines must precede multimodal claims. | It is explicit in legacy theory, restart syntheses, and comparison logic. | `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `research_comparison.md` | 96 |
| Benchmark comparability and leakage control are hard gates, not optional reporting details. | Both governance and archived evaluation protocol treat them as structural requirements. | `AgentRules.md`; `AgentGlossary.md`; `evaluation_protocol.md` | 98 |
| The active root should not silently treat the archived snapshot as active truth. | Deprecation materials explicitly mark the snapshot as reference-only, and the root was intentionally cleared. | `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`; `DEPRECATION_MANIFEST.txt` | 97 |
| Frozen-artifact, manifest-backed, saved-prediction evaluation is the preferred experimental style if legacy design is reused. | The archived architecture and data/evaluation docs all point in that direction. | `architecture_overview.md`; `data_layout.md`; `evaluation_protocol.md` | 93 |
| The first multimodal architecture should remain simple if salvaged from the legacy design. | The archived architecture explicitly says the current multimodal model is intentionally simple and richer variants belong later. | `architecture_overview.md`; `implementation_roadmap.md`; `multimodal_models.py` | 91 |
| Research-comparison artifacts are not final architecture approvals. | The research workflow appendix and the comparison files explicitly forbid hidden winner-picking. | `AgentResearchWorkflows.md`; `research_comparison.md`; `research_comparison_master_index.md` | 95 |
| Active implementation cannot responsibly resume without recreating active theory/design documents or explicitly deciding not to. | `AgentRules.md` names required layered design files, but they are absent at the active root after archival. | `AgentRules.md`; root directory listing; `LEGACY_DEPRECATION_SUMMARY.md` | 93 |

## 5. Open Design And Scope Questions

### DQ-001: Should the active project resume as a greenfield rebuild with selective legacy salvage, reactivate the archived snapshot as the active baseline, or ignore the snapshot and start from zero?

- Decision type: `Architecture`
- Why this decision exists: The active root was intentionally cleared, but the archived snapshot still contains substantial design and code evidence.
- What the current research already tells us: The root is supposed to be a true fresh start, while the snapshot is valuable as historical evidence and selective salvage material.
- Evidence references: `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`; `DEPRECATION_MANIFEST.txt`; `architecture_overview.md`
- What is still unknown: Whether the owner wants continuity of implementation, continuity of ideas only, or near-total restart.
- Why this matters now: Every later scope and architecture decision depends on what “active baseline” means.
- Consequence of delaying the decision: New design work may silently assume the wrong authority layer.
- Default options:
  - Option A: Rebuild at the active root and salvage legacy code or ideas only deliberately.
  - Option B: Promote the archived snapshot back to the active implementation baseline.
  - Option C: Start from zero and treat the snapshot as background reading only.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 7 | 82 |
| Option B | 4 | 5 | 6 | 7 | 4 | 44 |
| Option C | 5 | 4 | 8 | 6 | 6 | 47 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 10
  - Urgency (`1-10`): 10
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 8
  - Cross-cutting effect (`1-10`): 10

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 82
- Rationale: It matches the explicit deprecation policy while still preserving the archived snapshot as a rich evidence base and salvage source.
- Final owner decision needed: Confirm whether the archived snapshot is reference-only, salvageable implementation substrate, or the active baseline to reactivate.
- Blocking status: `Blocking`

### DQ-002: What is the canonical phase-1 project objective: a narrow test of event-state incremental value over market-only baselines, a broader multimodal forecasting platform, or an architecture-comparison program?

- Decision type: `Product Scope`
- Why this decision exists: The research corpus narrows strongly toward one thesis question, but no active owner-approved implementation contract currently encodes that scope.
- What the current research already tells us: The strongest restart conclusion is the narrow incremental-value question, and the comparison layer explicitly avoids selecting a wider winner program.
- Evidence references: `foundational_deep_research.md`; `restarting_research*.md`; `research_comparison.md`; `Current_State.md`
- What is still unknown: Whether the owner wants the narrow thesis question to govern the rebuild or only to inform a broader platform.
- Why this matters now: It determines what counts as core, extension, and out-of-scope work.
- Consequence of delaying the decision: Scope drift will continue to look like legitimate exploration.
- Default options:
  - Option A: Narrow phase-1 scope to the event-state-versus-market-only thesis question.
  - Option B: Rebuild a broader multimodal forecasting platform with multiple parallel thesis questions.
  - Option C: Prioritize an architecture comparison program before stabilizing one question.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 7 | 82 |
| Option B | 4 | 4 | 7 | 6 | 6 | 45 |
| Option C | 2 | 3 | 8 | 7 | 6 | 34 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 10
  - Urgency (`1-10`): 9
  - Evidence gap (`1-10`): 3
  - Irreversibility (`1-10`): 9
  - Cross-cutting effect (`1-10`): 10

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 85
- Rationale: The narrow objective is the most repeated, most defensible, and best aligned with the repository's strongest evidence and warnings.
- Final owner decision needed: Confirm the phase-1 objective in one sentence that future design and code must obey.
- Blocking status: `Blocking`

### DQ-003: Which target family should define the first serious benchmark: forward excess returns, raw forward returns, or factor-neutral residual returns?

- Decision type: `Data Model`
- Why this decision exists: Target choice changes the scientific question, comparability rules, and interpretation of any future improvement.
- What the current research already tells us: Excess returns are the strongest recurring recommendation; raw returns are useful baseline family; factor-neutral residuals are a heavier later refinement.
- Evidence references: `RESEARCH_DESIGN_old.md`; `src/features/labels.py`; `research_comparison_addendum_targets.md`; `foundational_deep_research.md`
- What is still unknown: Which family the owner wants to freeze as the canonical active target family.
- Why this matters now: Architecture, metrics, benchmark series, and evaluation claims all depend on it.
- Consequence of delaying the decision: Any early experiment may become non-comparable with later work.
- Default options:
  - Option A: Use forward excess returns as the primary target family.
  - Option B: Use raw forward returns as the primary target family and treat excess returns as analysis only.
  - Option C: Use factor-neutral residual returns as the primary target family from the start.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 6 | 80 |
| Option B | 6 | 6 | 3 | 4 | 8 | 67 |
| Option C | 7 | 7 | 7 | 6 | 5 | 61 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 10
  - Urgency (`1-10`): 9
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 8
  - Cross-cutting effect (`1-10`): 9

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 80
- Rationale: It best matches the repo's recurring “incremental value beyond market-only signal” framing without the heavier burden of factor-neutral target engineering.
- Final owner decision needed: Approve one primary target family for the first serious benchmark.
- Blocking status: `Blocking`

### DQ-004: What horizon set is in scope for the first serious benchmark: `1/5/20`, `1/5/20/60`, or a smaller subset?

- Decision type: `Data Model`
- Why this decision exists: Legacy code supports `1/5/20/60`, but research repeatedly centers `1/5/20` and treats `60` as later or optional.
- What the current research already tells us: Multi-horizon is core, but the narrower restart focus most often emphasizes `1`, `5`, and `20` day horizons.
- Evidence references: `src/features/labels.py`; `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md`
- What is still unknown: Whether `60d` is part of phase 1 or an extension horizon.
- Why this matters now: Horizon count affects label availability, split purge size, evaluation, and model complexity.
- Consequence of delaying the decision: Data preparation and evaluation policy stay under-specified.
- Default options:
  - Option A: Freeze `1d`, `5d`, and `20d` as the core phase-1 horizons.
  - Option B: Freeze `1d`, `5d`, `20d`, and `60d` from the start.
  - Option C: Freeze a smaller subset such as `1d` and `5d` only.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 7 | 82 |
| Option B | 6 | 6 | 6 | 6 | 5 | 56 |
| Option C | 5 | 5 | 3 | 5 | 8 | 60 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 7
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 6

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 72
- Rationale: It captures the most repeated core horizons while avoiding the added data-thinning and evaluation burden of treating `60d` as phase-1 core.
- Final owner decision needed: Confirm the exact horizon list for the first frozen benchmark family.
- Blocking status: `Important`

### DQ-005: Which news-alignment policy should be canonical for future work: the implemented as-of-close same-day rule, the older embargo-style delay rule, or two explicitly separate benchmark families?

- Decision type: `Workflow`
- Why this decision exists: Historical design documents disagree on when news becomes legally usable for prediction.
- What the current research already tells us: The implemented legacy policy is as-of-close same-day, but older theory still contains a more conservative delayed-use example.
- Evidence references: `evaluation_protocol.md`; `src/split/alignment_rules.py`; `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`
- What is still unknown: Which policy the owner wants to treat as active truth going forward.
- Why this matters now: This is a benchmark-family-defining rule and a direct leakage-control decision.
- Consequence of delaying the decision: Every later experiment risks belonging to an ambiguous benchmark family.
- Default options:
  - Option A: Canonicalize the as-of-close same-day rule.
  - Option B: Canonicalize a delayed embargo-style rule after publication.
  - Option C: Preserve both as distinct benchmark families and never compare them as one family.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 6 | 80 |
| Option B | 4 | 5 | 5 | 5 | 4 | 47 |
| Option C | 6 | 4 | 8 | 7 | 5 | 47 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 10
  - Urgency (`1-10`): 9
  - Evidence gap (`1-10`): 7
  - Irreversibility (`1-10`): 8
  - Cross-cutting effect (`1-10`): 10

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 78
- Rationale: It is the strongest implemented and evaluation-protocol-backed rule, but confidence is reduced because an older competing theory example still exists in-repo.
- Final owner decision needed: Approve one canonical alignment rule or explicitly approve parallel benchmark families.
- Blocking status: `Blocking`

### DQ-006: What exact benchmark family must be frozen before serious implementation resumes?

- Decision type: `Testing`
- Why this decision exists: The research corpus repeatedly says future work must “freeze first,” but the active root does not yet define the frozen benchmark family.
- What the current research already tells us: Universe, target family, benchmark series, text variant, event-state default, split policy, metrics, and missing-data handling all materially affect comparability.
- Evidence references: `foundational_deep_research.md`; `restarting_research.md`; `evaluation_protocol.md`; `AgentRules.md`; `AgentGlossary.md`
- What is still unknown: The exact chosen values for each benchmark-family component.
- Why this matters now: The first serious benchmark is the foundation for every later claim and ablation.
- Consequence of delaying the decision: Early experiments are likely to become unusable or incomparable.
- Default options:
  - Option A: Freeze one narrow serious benchmark family before coding or reruns.
  - Option B: Keep multiple benchmark families open during early build-out.
  - Option C: Delay freezing until after exploratory experiments reveal what is promising.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 3 | 4 | 6 | 81 |
| Option B | 3 | 4 | 7 | 7 | 6 | 41 |
| Option C | 2 | 3 | 5 | 8 | 8 | 40 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 10
  - Urgency (`1-10`): 10
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 9
  - Cross-cutting effect (`1-10`): 10

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 84
- Rationale: It is the most repeated methodological conclusion across governance and restart research and is the cleanest defense against benchmark drift.
- Final owner decision needed: Approve the full frozen benchmark packet or delegate its explicit drafting as the next step.
- Blocking status: `Blocking`

### DQ-007: What universe should define the first serious benchmark: a fixed medium liquid large-cap subset, the full large-cap universe, or only a tiny pilot subset?

- Decision type: `Data Model`
- Why this decision exists: Earlier design targeted roughly 50 large-cap stocks, while later research warns against using a giant live universe as the first serious benchmark.
- What the current research already tells us: Large caps are easier for coverage and liquidity; smoke-scale subsets are too small; full live-universe benchmarking is discouraged early.
- Evidence references: `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md`; smoke training summaries
- What is still unknown: The exact phase-1 universe size, membership rule, and whether historical membership matters.
- Why this matters now: Universe choice affects provider load, survivorship risk, sample size, and generalization claims.
- Consequence of delaying the decision: Data collection, coverage checks, and benchmark freezing cannot be completed cleanly.
- Default options:
  - Option A: Freeze a medium liquid large-cap subset around 50 names with explicit rules.
  - Option B: Use the full current large-cap or S&P 500 universe immediately.
  - Option C: Stay with a tiny pilot subset for the first serious benchmark.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 5 | 6 | 78 |
| Option B | 4 | 4 | 8 | 7 | 4 | 39 |
| Option C | 3 | 3 | 2 | 4 | 9 | 52 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 7

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 70
- Rationale: It best matches the older design target and later warnings against both smoke-only and giant live-universe early benchmarking.
- Final owner decision needed: Approve the phase-1 universe size, membership source, and survivorship policy.
- Blocking status: `Important`

### DQ-008: Which external data stack is in scope for phase 1: legacy provider set only, legacy providers plus factor-library support, or a broader multi-provider expansion now?

- Decision type: `Integration`
- Why this decision exists: Provider choices drive target feasibility, cost, quotas, and operational complexity.
- What the current research already tells us: Legacy design and implementation centered on Twelve Data, Finnhub, and SEC; factor-library support is a real later option; broader expansions are repeatedly marked risky.
- Evidence references: `RESEARCH_DESIGN_old.md`; `architecture_overview.md`; `implementation_roadmap.md`; paper/source note `S01`; `P09`; `D4` references inside research docs
- What is still unknown: Whether the owner wants factor data or broader data sources in phase 1.
- Why this matters now: Provider scope constrains data pipelines, benchmarks, and schedule.
- Consequence of delaying the decision: Data architecture may overbuild for unused providers or underbuild for target choices that need them.
- Default options:
  - Option A: Phase 1 uses Twelve Data, Finnhub, and SEC only.
  - Option B: Phase 1 adds factor-library support now but defers broader data expansions.
  - Option C: Phase 1 also adds macro, options, or broader news providers.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 5 | 7 | 81 |
| Option B | 7 | 7 | 5 | 5 | 6 | 66 |
| Option C | 3 | 2 | 8 | 8 | 5 | 31 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 7
  - Cross-cutting effect (`1-10`): 7

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 74
- Rationale: It matches the strongest existing implementation evidence and keeps phase-1 complexity aligned with the narrow thesis question.
- Final owner decision needed: Approve the exact provider/data-source scope for phase 1 and note what is deferred.
- Blocking status: `Important`

### DQ-009: What event-representation family should be the active default: pooled dense embeddings plus scalar enrichments, pooled dense embeddings only, or sentiment-only text features as the main representation?

- Decision type: `Architecture`
- Why this decision exists: Event representation is the main conceptual differentiator of the project and a major source of branch sprawl.
- What the current research already tells us: Pooled dense embeddings and event-state scalars are the strongest current families; sentiment-only is useful as a weak baseline but not as core identity.
- Evidence references: `src/features/event_state.py`; `research_comparison_addendum_event_representations.md`; `research_comparison_addendum_features.md`; paper notes `P01`, `P15`, `P16`
- What is still unknown: Whether phase 1 should default to a semantic-only event state or a semantic-plus-structured event state.
- Why this matters now: It affects data contracts, model inputs, ablations, and interpretability claims.
- Consequence of delaying the decision: Text-side implementation will drift between incompatible representation families.
- Default options:
  - Option A: Use pooled dense embeddings and include scalar enrichments as the default event-state package.
  - Option B: Use pooled dense embeddings only and treat scalars as later ablations.
  - Option C: Use sentiment-only text features as the primary text representation.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 5 | 6 | 78 |
| Option B | 8 | 8 | 4 | 4 | 7 | 76 |
| Option C | 4 | 4 | 2 | 5 | 9 | 57 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 7
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 7

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 66
- Rationale: It best matches the event-state thesis identity and the current archived implementation hooks, but pooled embeddings only remains a close and credible simpler fallback.
- Final owner decision needed: Approve the default event-state representation for the first serious benchmark.
- Blocking status: `Important`

### DQ-010: Which multimodal fusion family should be the phase-1 default: simple gated fusion, late fusion, or residual fusion?

- Decision type: `Architecture`
- Why this decision exists: The archived code implements gating, while comparison research says late and gated fusion are close and both strong.
- What the current research already tells us: Late fusion is slightly cleaner for benchmarking; gated fusion is highly aligned with conditional usefulness of text; residual fusion is elegant but less directly evidenced in-code.
- Evidence references: `src/models/multimodal_models.py`; `architecture_overview.md`; `research_comparison_addendum_models.md`; `research_comparison.md`
- What is still unknown: Which of the close leading fusion families the owner wants to standardize first.
- Why this matters now: It affects model interfaces, ablations, and how “text adds value” is operationalized.
- Consequence of delaying the decision: The active model branch may drift while still claiming to test the same question.
- Default options:
  - Option A: Keep simple gated fusion as the phase-1 default.
  - Option B: Use plain late fusion as the benchmark-clean default.
  - Option C: Use residual fusion as the first active multimodal default.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 5 | 6 | 78 |
| Option B | 8 | 8 | 4 | 4 | 7 | 76 |
| Option C | 7 | 8 | 6 | 6 | 6 | 67 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 7
  - Urgency (`1-10`): 7
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 8

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 60
- Rationale: It is the strongest code-evidenced default and remains research-consistent, though late fusion is close enough that the owner should treat this as a real choice.
- Final owner decision needed: Approve the first active fusion default and whether the runner-up becomes a mandatory ablation.
- Blocking status: `Important`

### DQ-011: What benchmark model ladder is mandatory before any higher-complexity branch is considered?

- Decision type: `Testing`
- Why this decision exists: The repository repeatedly insists on strong baselines before multimodal or extension claims.
- What the current research already tells us: Linear regularized baselines are non-negotiable, market-only neural baselines are strong comparators, and a simple multimodal model is the first serious text-side test.
- Evidence references: `implementation_roadmap.md`; `architecture_overview.md`; `baseline_models.py`; `multimodal_models.py`; `research_comparison_addendum_models.md`
- What is still unknown: Exactly which models must be present before the owner considers the benchmark ladder complete.
- Why this matters now: It prevents weak-baseline wins and reduces architecture inflation.
- Consequence of delaying the decision: Later results may be hard to trust because the comparator set was under-specified.
- Default options:
  - Option A: Require linear baselines, a market-only MLP, and one simple multimodal model.
  - Option B: Require linear baselines and jump directly to multimodal comparison.
  - Option C: Add tree-based and multi-task families immediately to the mandatory ladder.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 5 | 6 | 78 |
| Option B | 4 | 4 | 3 | 6 | 8 | 53 |
| Option C | 6 | 5 | 8 | 7 | 5 | 50 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 9
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 8

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 74
- Rationale: It is the smallest ladder that still preserves baseline discipline and clean incremental-value interpretation.
- Final owner decision needed: Approve the mandatory pre-extension comparator ladder.
- Blocking status: `Important`

### DQ-012: What final evaluation protocol should govern serious claims: purged-plus-embargoed walk-forward plus a lockbox, simpler walk-forward only, or something lighter?

- Decision type: `Testing`
- Why this decision exists: Evaluation doctrine is one of the strongest sources of both scientific strength and historical contradiction in the repo.
- What the current research already tells us: Walk-forward is core, purging and often embargo are strongest for overlapping horizons, and a final untouched lockbox is strongly advised.
- Evidence references: `evaluation_protocol.md`; `purged_embargo_splits.py`; `research_comparison_addendum_evaluation.md`; `foundational_deep_research.md`; `restarting_research.md`
- What is still unknown: Which exact combination the owner wants as the claim-bearing evaluation family.
- Why this matters now: It defines what future benchmark results can legally mean.
- Consequence of delaying the decision: Experimental results will arrive before their evidentiary standard is fixed.
- Default options:
  - Option A: Use purged-plus-embargoed walk-forward for model development and add a final untouched lockbox for reporting.
  - Option B: Use walk-forward without mandatory purge/embargo or lockbox.
  - Option C: Use a lighter single-holdout or similarly weak protocol for phase 1.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 6 | 5 | 5 | 75 |
| Option B | 7 | 7 | 4 | 5 | 7 | 69 |
| Option C | 2 | 2 | 2 | 7 | 8 | 41 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 10
  - Urgency (`1-10`): 9
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 8
  - Cross-cutting effect (`1-10`): 10

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 78
- Rationale: It best matches both the strongest archived protocol and the restart research's explicit warnings about overlapping-label contamination and final reporting bias.
- Final owner decision needed: Approve the exact evaluation family that will define “serious” benchmark evidence.
- Blocking status: `Blocking`

### DQ-013: What should count as primary success metrics, and is ranking secondary or co-primary?

- Decision type: `Testing`
- Why this decision exists: The repo supports regression, classification, and ranking metrics, but the research warns that these families answer different questions.
- What the current research already tells us: Regression-first best matches the current thesis framing; ranking is a serious secondary lens; probabilistic metrics should wait unless probabilistic outputs exist.
- Evidence references: `evaluation_protocol.md`; `RESEARCH_DESIGN_old.md`; `research_comparison_addendum_targets.md`; `research_comparison_addendum_evaluation.md`; `P05`; `P08`; `P10`
- What is still unknown: Whether the owner wants ranking to remain secondary or elevate it to co-primary status.
- Why this matters now: It changes what “improvement” means and which model families are worth building first.
- Consequence of delaying the decision: Metrics may be reported opportunistically instead of according to scope.
- Default options:
  - Option A: Keep regression metrics primary and ranking metrics secondary but mandatory.
  - Option B: Make ranking-first evaluation primary from the start.
  - Option C: Make probabilistic scoring or calibration primary now.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 7 | 80 |
| Option B | 7 | 7 | 6 | 5 | 6 | 65 |
| Option C | 4 | 4 | 8 | 7 | 5 | 41 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 7

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 72
- Rationale: It preserves the current thesis framing while still respecting the repo's repeated warnings that weak point-fit can hide real ranking signal.
- Final owner decision needed: Approve the primary metric family and the exact role of ranking metrics in claim-making.
- Blocking status: `Important`

### DQ-014: Should static company metadata or KB features enter phase 1, or stay as a phase-2 extension?

- Decision type: `Data Model`
- Why this decision exists: The archived repo already has a KB layer and optional company-profile model hook, but research treats static metadata as secondary to the core benchmark.
- What the current research already tells us: Static metadata is one of the cleaner extensions; dynamic profile branches are much riskier and later.
- Evidence references: `architecture_overview.md`; snapshot `data/kb/` presence; `multimodal_models.py`; `research_comparison_addendum_extension_branches.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- What is still unknown: Whether the owner wants phase 1 to answer only the market-plus-event-state question or also include static company context.
- Why this matters now: It affects final-panel schema, ablation design, and the meaning of the first serious benchmark.
- Consequence of delaying the decision: Static context may drift into the core benchmark without explicit approval.
- Default options:
  - Option A: Keep static company metadata out of phase 1 and treat it as phase-2 extension.
  - Option B: Include static company metadata in the default phase-1 panel and model.
  - Option C: Exclude company metadata entirely from near-term scope.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 8 | 3 | 4 | 8 | 82 |
| Option B | 5 | 5 | 5 | 5 | 7 | 56 |
| Option C | 3 | 3 | 2 | 4 | 9 | 52 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 6
  - Urgency (`1-10`): 5
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 5
  - Cross-cutting effect (`1-10`): 6

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 70
- Rationale: It best preserves a clean answer to the core question while keeping a low-friction extension available immediately afterward.
- Final owner decision needed: Approve whether static company context is phase-1 default, phase-1 ablation, or phase-2 only.
- Blocking status: `Important`

### DQ-015: Are uncertainty-aware outputs in scope for phase 1, a later extension, or a primary objective shift?

- Decision type: `Testing`
- Why this decision exists: The repo has calibration and uncertainty hooks, and the research corpus maps a real uncertainty literature branch, but repeatedly defers it.
- What the current research already tells us: Uncertainty-aware outputs are legitimate but later; deterministic benchmarking still appears unresolved.
- Evidence references: `implementation_roadmap.md`; `research_comparison_addendum_extension_branches.md`; `P10`; `P14`; `P17`; `P19`; `P20`
- What is still unknown: Whether the owner wants to open this branch now or explicitly defer it.
- Why this matters now: It changes architecture, evaluation metrics, reporting, and schedule.
- Consequence of delaying the decision: Uncertainty work may be started informally without the scoring and calibration discipline it needs.
- Default options:
  - Option A: Keep uncertainty-aware outputs as a later extension only.
  - Option B: Run a small parallel uncertainty branch in phase 1.
  - Option C: Make predictive uncertainty a primary phase-1 objective.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 4 | 4 | 8 | 84 |
| Option B | 5 | 5 | 7 | 6 | 7 | 53 |
| Option C | 2 | 2 | 9 | 8 | 4 | 25 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 6
  - Urgency (`1-10`): 5
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 5

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 78
- Rationale: It matches the strongest research guidance and prevents a metric/evaluation branch from displacing the unresolved deterministic benchmark question.
- Final owner decision needed: Explicitly defer or include uncertainty-aware outputs in the active phase plan.
- Blocking status: `Nice-to-have`

### DQ-016: Which branches should be explicitly out of scope until the core benchmark is stable?

- Decision type: `Product Scope`
- Why this decision exists: The research corpus repeatedly warns against dynamic profiles, graph-heavy redesigns, MoE, end-to-end fine-tuning, broad derivatives, and giant live-universe benchmarking as near-term core work.
- What the current research already tells us: These branches are legitimate future directions but poor immediate fits, high benchmark burdens, or both.
- Evidence references: `foundational_deep_research.md`; `restarting_research*.md`; `research_comparison_addendum_extension_branches.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- What is still unknown: Which specific branches the owner wants formally deferred rather than left ambiguous.
- Why this matters now: Explicit deferral is the cleanest control against scope drift.
- Consequence of delaying the decision: Attractive branches will continue to compete with core work for attention.
- Default options:
  - Option A: Explicitly defer dynamic profiles, graph cores, MoE, end-to-end text fine-tuning, broad derivative grids, and full live-universe first-pass benchmarking.
  - Option B: Allow one of those higher-risk branches in parallel with the core benchmark.
  - Option C: Keep all branches notionally open in phase 1.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 3 | 4 | 7 | 83 |
| Option B | 5 | 5 | 6 | 6 | 6 | 52 |
| Option C | 2 | 2 | 8 | 8 | 9 | 36 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 4
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 8

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 82
- Rationale: The repository is unusually consistent in treating those branches as later, risky, or out-of-scope for the first serious benchmark family.
- Final owner decision needed: Approve the explicit phase-1 out-of-scope list.
- Blocking status: `Important`

### DQ-017: Which active theory/design documents must be recreated at the root before any new implementation resumes?

- Decision type: `Delivery`
- Why this decision exists: `AgentRules.md` names required layered theory and design files, but the active root currently lacks them because the old project was archived wholesale.
- What the current research already tells us: The root is intentionally a fresh-start shell; future work should not treat the archived docs as active truth without deliberate reintroduction.
- Evidence references: `AgentRules.md`; root directory listing; `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`
- What is still unknown: Which active documents the owner wants instantiated first and whether the archived docs should be summarized or partially adopted into them.
- Why this matters now: Without active theory/design files, implementation scope is under-governed even though governance rules exist.
- Consequence of delaying the decision: The rebuild may either code without documentation or rely on archived documents as de facto active truth.
- Default options:
  - Option A: Recreate active theory/design docs before coding begins.
  - Option B: Resume coding first and backfill active theory/design docs later.
  - Option C: Treat archived legacy docs as active design truth without recreating active-root documents.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 4 | 6 | 79 |
| Option B | 2 | 2 | 3 | 8 | 7 | 37 |
| Option C | 4 | 4 | 2 | 6 | 4 | 46 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 9
  - Urgency (`1-10`): 9
  - Evidence gap (`1-10`): 6
  - Irreversibility (`1-10`): 7
  - Cross-cutting effect (`1-10`): 9

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 82
- Rationale: It is the only option fully aligned with the active governance constitution and the deprecation boundary established at the root.
- Final owner decision needed: Approve which active theory/design documents should be written next and in what order.
- Blocking status: `Blocking`

### DQ-018: What verification and observability bar is required before the project can claim meaningful active progress?

- Decision type: `Observability`
- Why this decision exists: The repository has strong evidence rules, but current active-root implementation evidence is minimal and visible legacy empirical evidence is smoke-scale only.
- What the current research already tells us: Major claims should rely on frozen datasets, saved predictions, fold-level results, provider verification, and reproducible evidence rather than archived summaries alone.
- Evidence references: `AgentRules.md`; `AgentMemory.md`; `implementation_roadmap.md`; `tests/results/Expanded_Testing_20260319T121411Z.md`; smoke artifact summaries
- What is still unknown: Whether the owner wants only conservative evidence gates or also CI/rerun requirements and structured experiment registry expectations.
- Why this matters now: It defines when phase work is really “done” and how much evidence future claims must carry.
- Consequence of delaying the decision: The project may repeat the pattern of broad documentation with weak active evidence.
- Default options:
  - Option A: Require rerun-capable tests, manual provider checks, structured run summaries, and CI-ready validation before major claims.
  - Option B: Rely mostly on archived docs and artifacts unless a later blocker appears.
  - Option C: Use only lightweight manual checks and ad hoc summaries in phase 1.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 6 | 4 | 6 | 78 |
| Option B | 3 | 3 | 2 | 8 | 8 | 46 |
| Option C | 4 | 4 | 4 | 6 | 9 | 54 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 6
  - Irreversibility (`1-10`): 7
  - Cross-cutting effect (`1-10`): 8

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 72
- Rationale: It best fits the repository's evidence-gated culture and protects the rebuild from leaning on stale legacy confidence.
- Final owner decision needed: Approve the minimum evidence and observability bar for active progress claims.
- Blocking status: `Important`

### DQ-019: What deployment, API, UX, permission, and security boundary is actually in scope for phase 1?

- Decision type: `Infra`
- Why this decision exists: The archived system is CLI- and artifact-driven, but the active root does not currently specify whether the rebuild stays research-local or grows into a service or UI.
- What the current research already tells us: The strongest repo fit is local research workflow, not productized service architecture; no active auth/role system or UI boundary is evidenced.
- Evidence references: root directory listing; legacy snapshot structure; `architecture_overview.md`; `ExecutionFlow.md` references inside research docs; `research_comparison_addendum_repo_fit_and_modularity.md`
- What is still unknown: Whether phase 1 is strictly a local research system, a scheduled batch pipeline, or something user-facing with API/auth concerns.
- Why this matters now: This single decision determines whether API contracts, permissions, secret-management hardening, and UX surfaces are phase-1 work or explicit non-goals.
- Consequence of delaying the decision: The rebuild may accidentally inherit product-like obligations without any approved product scope.
- Default options:
  - Option A: Keep phase 1 as a local CLI- and artifact-driven research system only.
  - Option B: Add scheduled batch execution and lightweight automation, but no user-facing service.
  - Option C: Build a user-facing service, API, or dashboard in phase 1.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 3 | 4 | 9 | 87 |
| Option B | 5 | 5 | 6 | 6 | 6 | 52 |
| Option C | 2 | 2 | 9 | 8 | 3 | 23 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 5
  - Urgency (`1-10`): 4
  - Evidence gap (`1-10`): 6
  - Irreversibility (`1-10`): 5
  - Cross-cutting effect (`1-10`): 6

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 76
- Rationale: No current repository evidence justifies service/API/UI complexity in phase 1, and the archive repeatedly optimizes for local, reproducible research workflows.
- Final owner decision needed: Confirm whether phase 1 is research-local only or whether service/API/UI scope is intentionally included.
- Blocking status: `Important`

### DQ-020: How should active truth, archived truth, contradictions, and stale research be governed once new implementation work restarts?

- Decision type: `Other`
- Why this decision exists: The repository now has an active governance shell, an archived legacy implementation, duplicate backup research, and several stale or contradicted research claims.
- What the current research already tells us: Contradictions must stay visible, lower-authority sources must not silently win, and the archive is reference-only unless deliberately salvaged.
- Evidence references: `AgentRules.md`; `AgentAppendices.md`; `LEGACY_DEPRECATION_SUMMARY.md`; `deprecated_version/.../README.md`; `docs/research_results/bkup/*.md`; contradictory research/log files
- What is still unknown: Who decides when archived material is adopted into new active truth and how stale research gets formally demoted.
- Why this matters now: Without a clear rule, future design docs can drift into a hybrid of active and archived truth with unclear authority.
- Consequence of delaying the decision: Scope and design disagreements will be harder to resolve and easier to rationalize incorrectly.
- Default options:
  - Option A: Keep the archive reference-only and explicitly triage any reused ideas into new active-root theory/design docs.
  - Option B: Use active-root and archived documents together informally as long as conflicts are discussed ad hoc.
  - Option C: Promote archived docs back to active truth unless a newer file explicitly contradicts them.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 4 | 7 | 81 |
| Option B | 3 | 3 | 5 | 7 | 8 | 44 |
| Option C | 4 | 4 | 4 | 7 | 3 | 41 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 7
  - Urgency (`1-10`): 7
  - Evidence gap (`1-10`): 6
  - Irreversibility (`1-10`): 7
  - Cross-cutting effect (`1-10`): 7

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 78
- Rationale: It is the cleanest way to preserve the deprecation boundary and the active governance hierarchy while still enabling deliberate reuse.
- Final owner decision needed: Approve the rule for how archived materials become active truth, if at all.
- Blocking status: `Important`

### DQ-021: What historical date range should define the first serious benchmark family?

- Decision type: `Data Model`
- Why this decision exists: Older design materials assume a broad multi-year window, but current provider adequacy and overlap quality for a serious frozen benchmark remain unverified.
- What the current research already tells us: The first serious benchmark should favor a trustworthy overlapping window over an idealized but weakly verified maximum-history window.
- Evidence references: `RESEARCH_DESIGN_old.md`; `foundational_deep_research.md`; `restarting_research.md`; `implementation_roadmap.md`
- What is still unknown: The exact owner-approved start and end dates for the first serious benchmark family.
- Why this matters now: Date range affects sample size, provider feasibility, benchmark fairness, and whether later experiments are comparable.
- Consequence of delaying the decision: Universe, provider checks, and benchmark freezing remain incomplete.
- Default options:
  - Option A: Freeze a shorter overlapping clean window based on what can be verified now.
  - Option B: Target a longer historical window only if provider overlap is manually verified and rebuilt first.
  - Option C: Keep the older idealized long-window target as the phase-1 default.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 8 | 8 | 4 | 4 | 7 | 76 |
| Option B | 6 | 6 | 7 | 6 | 6 | 57 |
| Option C | 3 | 4 | 7 | 8 | 4 | 36 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 8
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 6
  - Irreversibility (`1-10`): 7
  - Cross-cutting effect (`1-10`): 7

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 68
- Rationale: It best matches the repository's repeated preference for a trustworthy first benchmark over a larger but weakly verified one.
- Final owner decision needed: Approve the exact historical date window for the first frozen serious benchmark.
- Blocking status: `Important`

### DQ-022: What is the official no-news-day policy for the event-state branch?

- Decision type: `Workflow`
- Why this decision exists: No-news handling changes row semantics, model behavior, and benchmark comparability materially.
- What the current research already tells us: No-news handling is benchmark-family-defining, and archived event-state code currently supports empty-window rows with zero vectors and explicit `news_count` values.
- Evidence references: `src/features/event_state.py`; `restarting_research.md`; `research_comparison_addendum_event_representations.md`; `research_comparison_addendum_repo_fit_and_modularity.md`
- What is still unknown: Whether the owner wants no-news days encoded as explicit empty state, masked missing modality, or removed from training/evaluation rows.
- Why this matters now: It directly affects the event-state branch on many dates and determines whether row-universe comparability is preserved.
- Consequence of delaying the decision: The text branch can drift into incompatible semantics while still appearing to test the same benchmark family.
- Default options:
  - Option A: Keep the row and encode an explicit empty event state with no-news indicators.
  - Option B: Keep the row but treat text as missing modality handled by masks.
  - Option C: Drop no-news rows from multimodal training/evaluation.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 8 | 9 | 4 | 4 | 7 | 79 |
| Option B | 6 | 7 | 5 | 5 | 7 | 65 |
| Option C | 3 | 3 | 4 | 7 | 8 | 45 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 7
  - Urgency (`1-10`): 8
  - Evidence gap (`1-10`): 6
  - Irreversibility (`1-10`): 7
  - Cross-cutting effect (`1-10`): 8

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 75
- Rationale: It best preserves row-universe comparability, aligns with the archived event-state implementation pattern, and keeps the no-news condition explicit instead of implicit.
- Final owner decision needed: Approve the canonical no-news-day policy for the first serious benchmark family.
- Blocking status: `Important`

### DQ-023: What exact run-artifact packet must every serious benchmark emit?

- Decision type: `Observability`
- Why this decision exists: The repository strongly prefers saved predictions, manifests, and evidence-backed claims, but the exact mandatory artifact packet is not yet frozen in active scope.
- What the current research already tells us: Serious runs should be traceable through frozen datasets, manifests, configs, fold definitions, saved predictions, and machine-readable evaluation outputs.
- Evidence references: `AgentRules.md`; `AgentMemory.md`; `architecture_overview.md`; `data_layout.md`; `evaluation_protocol.md`
- What is still unknown: Which artifacts are mandatory before a run counts as serious benchmark evidence.
- Why this matters now: Without a fixed artifact packet, serious runs become harder to audit, compare, and trust.
- Consequence of delaying the decision: Evidence quality will vary across runs and encourage weak or non-reproducible claims.
- Default options:
  - Option A: Require dataset version, manifest, resolved config, fold definitions, saved predictions, metrics, and comparison summary for every serious run.
  - Option B: Require only saved predictions and metrics.
  - Option C: Require a much heavier packet including figures and narrative writeups for every run.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 5 | 4 | 7 | 81 |
| Option B | 5 | 5 | 3 | 6 | 8 | 59 |
| Option C | 6 | 6 | 8 | 5 | 6 | 57 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 7
  - Urgency (`1-10`): 7
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 8

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 77
- Rationale: It is the cleanest serious-run packet that matches the repo's architecture and evidence-gated governance without overloading every run with publication polish.
- Final owner decision needed: Approve the minimum artifact packet required for a serious benchmark run to count as evidence.
- Blocking status: `Important`

### DQ-024: What thesis outcome classes are acceptable success conditions for phase 1?

- Decision type: `Delivery`
- Why this decision exists: The research corpus repeatedly argues that robust null or conditional findings can still be academically valuable, but no active scope document states what outcome classes the owner will accept.
- What the current research already tells us: The narrow thesis question is explicitly described as falsifiable and capable of yielding useful negative or conditional results.
- Evidence references: `foundational_deep_research.md`; `restarting_research.md`; `restarting_research_literature_expansion.md`
- What is still unknown: Whether the owner will accept clean null or conditional results, or only clear positive multimodal improvement.
- Why this matters now: It directly affects pressure toward overfitting, metric shopping, and scope creep.
- Consequence of delaying the decision: The project may behave like a must-win system instead of a controlled scientific program.
- Default options:
  - Option A: Accept robust positive, conditional positive, or clean null results as phase-1 thesis success classes.
  - Option B: Require clear positive multimodal improvement for phase 1 to count as success.
  - Option C: Treat only strong positive improvement as satisfactory.

- Option scorecard:

| Option | Evidence alignment | Scope fit | Complexity | Risk | Reversibility | Weighted option score |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Option A | 9 | 9 | 2 | 2 | 8 | 88 |
| Option B | 4 | 5 | 3 | 7 | 5 | 49 |
| Option C | 2 | 3 | 3 | 9 | 3 | 31 |

- Question priority score (`0-100`) using: `Impact*3 + Urgency*2 + Evidence gap*2 + Irreversibility*2 + Cross-cutting effect*1`
- Priority factor breakdown:
  - Impact (`1-10`): 6
  - Urgency (`1-10`): 5
  - Evidence gap (`1-10`): 5
  - Irreversibility (`1-10`): 6
  - Cross-cutting effect (`1-10`): 6

- Recommended current default: Option A
- Recommendation confidence (`0-100`): 83
- Rationale: It best matches the repository's strongest scientific framing and reduces pressure to distort scope or benchmarks just to force a positive result.
- Final owner decision needed: Approve which outcome classes count as acceptable phase-1 success.
- Blocking status: `Important`

## 6. Decision Priority Summary
| Rank | Decision ID | Question | Priority score | Recommended current default | Recommendation confidence | Blocking status |
| ---: | --- | --- | ---: | --- | ---: | --- |
| 1 | `DQ-005` | Which news-alignment policy should be canonical going forward? | 88 | Option A: canonicalize as-of-close same-day | 78 | `Blocking` |
| 2 | `DQ-006` | What exact benchmark family must be frozen before serious implementation resumes? | 86 | Option A: freeze one narrow serious benchmark family first | 84 | `Blocking` |
| 3 | `DQ-001` | Should the active project rebuild with selective salvage, reactivate the snapshot, or start from zero? | 84 | Option A: greenfield rebuild with selective salvage | 82 | `Blocking` |
| 4 | `DQ-012` | What final evaluation protocol should govern serious claims? | 84 | Option A: purged+embargoed walk-forward plus lockbox | 78 | `Blocking` |
| 5 | `DQ-002` | What is the canonical phase-1 project objective? | 82 | Option A: narrow event-state incremental-value thesis | 85 | `Blocking` |
| 6 | `DQ-003` | Which target family should define the first serious benchmark? | 81 | Option A: forward excess returns | 80 | `Blocking` |
| 7 | `DQ-017` | Which active theory/design documents must be recreated at the root before coding? | 80 | Option A: recreate active docs before coding | 82 | `Blocking` |
| 8 | `DQ-018` | What verification and observability bar is required before major claims? | 74 | Option A: rerun-capable tests, provider checks, structured summaries | 72 | `Important` |
| 9 | `DQ-021` | What historical date range should define the first serious benchmark family? | 73 | Option A: shorter overlapping clean window | 68 | `Important` |
| 10 | `DQ-008` | Which external data stack is in scope for phase 1? | 71 | Option A: Twelve Data + Finnhub + SEC only | 74 | `Important` |
| 11 | `DQ-011` | What benchmark model ladder is mandatory before higher-complexity branches? | 71 | Option A: linear + market-only MLP + simple multimodal | 74 | `Important` |
| 12 | `DQ-022` | What is the official no-news-day policy for the event-state branch? | 71 | Option A: explicit empty event state plus no-news indicators | 75 | `Important` |
| 13 | `DQ-007` | What universe should define the first serious benchmark? | 69 | Option A: fixed medium liquid large-cap subset | 70 | `Important` |
| 14 | `DQ-013` | What should count as primary success metrics, and is ranking secondary or co-primary? | 69 | Option A: regression primary, ranking secondary but mandatory | 72 | `Important` |
| 15 | `DQ-016` | Which branches should be explicitly out of scope until the core benchmark is stable? | 68 | Option A: explicitly defer the high-risk branches | 82 | `Important` |
| 16 | `DQ-020` | How should active truth, archived truth, contradictions, and stale research be governed? | 68 | Option A: archive reference-only, active docs absorb reuse deliberately | 78 | `Important` |
| 17 | `DQ-009` | What event-representation family should be the active default? | 67 | Option A: pooled dense embeddings plus scalar enrichments | 66 | `Important` |
| 18 | `DQ-010` | Which multimodal fusion family should be the phase-1 default? | 65 | Option A: simple gated fusion | 60 | `Important` |
| 19 | `DQ-023` | What exact run-artifact packet must every serious benchmark emit? | 65 | Option A: dataset version + manifest + config + folds + predictions + metrics + comparison summary | 77 | `Important` |
| 20 | `DQ-004` | What horizon set is in scope for the first serious benchmark? | 64 | Option A: `1/5/20` core | 72 | `Important` |
| 21 | `DQ-024` | What thesis outcome classes are acceptable success conditions for phase 1? | 56 | Option A: positive, conditional positive, or clean null all count | 83 | `Important` |
| 22 | `DQ-015` | Are uncertainty-aware outputs in scope for phase 1? | 53 | Option A: later extension only | 78 | `Nice-to-have` |
| 23 | `DQ-014` | Should static company metadata or KB features enter phase 1? | 52 | Option A: phase-2 extension only | 70 | `Important` |
| 24 | `DQ-019` | What deployment, API, UX, permission, and security boundary is in scope for phase 1? | 51 | Option A: local CLI/artifact research system only | 76 | `Important` |

## 7. Contradictions And Evidence Gaps

- Direct contradictions across sources:
  - `RESEARCH_DESIGN_old.md` contains an older embargo-style news-use example, while `evaluation_protocol.md` and `src/split/alignment_rules.py` implement as-of-close same-day alignment.
  - `foundational_deep_research.md`, `restarting_research.md`, and some research logs state the active governance validator fails because log files are missing, but the current repository now contains those files and `python scripts/validate_agent_governance.py` passes.
  - `tests/results/Expanded_Testing_20260319T121411Z.md` reports a ridge-baseline NaN failure caused by missing feature imputation, but archived `src/models/baseline_models.py` already contains median imputation in the sklearn pipelines.

- Stale or low-trust research:
  - `docs/research_results/bkup/*.md` are clearly historical duplicates and should not outrank the non-backup versions.
  - `docs/research_results/logs/*.md` are provenance records, not theory or design authority.
  - Several paper notes explicitly preserve uncertainty rather than full verification: `P02`, `P14`, `P17`, `P22`, `P23`, and `S01`.
  - Backup research contains at least one citation inconsistency: `docs/research_results/bkup/restarting_research.md` cites `Price Momentum and Trading Volume` with a different DOI than verified paper note `P12`.

- Claims that sound plausible but are insufficiently supported:
  - That the current active root is ready for implementation without recreating active theory/design docs.
  - That provider plan reality, split-event completeness, and historical company-news coverage are currently adequate for the intended benchmark.
  - That the archived smoke artifacts demonstrate meaningful predictive validity.
  - That the archived company-profile branch is mature enough to enter the first serious benchmark by default.

- Questions that cannot yet be answered from the repository:
  - Which active phase-1 objective the owner formally approves.
  - Which exact benchmark-family values the owner wants frozen.
  - Which historical date range the first serious benchmark should cover.
  - Which no-news-day semantics should be treated as canonical.
  - Whether factor-neutral targets, static metadata, or uncertainty outputs are phase-1 or phase-2.
  - What artifact packet is required before a run counts as serious benchmark evidence.
  - Which thesis outcome classes the owner will accept as phase-1 success.
  - Whether the rebuild is strictly local research tooling or includes any service/API/UI scope.
  - What external compliance or institutional review constraints apply beyond academic research integrity and provider usage limits.

## 8. Suggested Decision Order

1. Decide `DQ-001` and `DQ-017` first.
   - The owner must decide whether the active project is a greenfield rebuild or a legacy reactivation, and whether active theory/design docs must be recreated before coding. These choices define which documents will carry authority next.

2. Decide `DQ-002` next.
   - Once the active baseline is known, the owner should lock the phase-1 objective in one sentence. Every later “core versus extension” choice depends on that sentence.

3. Resolve the scientific problem-definition questions together: `DQ-003`, `DQ-004`, `DQ-005`, and `DQ-021`.
   - Target family, horizon set, news-alignment policy, and date range jointly define the actual forecasting problem. They should not be decided independently.

4. Freeze the evidentiary frame with `DQ-006`, `DQ-012`, `DQ-013`, and `DQ-023`.
   - After the problem is defined, the owner should freeze the benchmark family, the evaluation protocol, the primary metric logic, and the required run-evidence packet. This prevents benchmark drift before implementation resumes.

5. Decide data and integration scope: `DQ-007` and `DQ-008`.
   - Universe size and provider scope determine what data pipelines are actually needed and what manual verification work must happen.

6. Decide the minimum architecture defaults: `DQ-009`, `DQ-010`, `DQ-011`, and `DQ-022`.
   - Event representation, fusion family, benchmark model ladder, and no-news-day semantics should be chosen only after the benchmark family is frozen; otherwise architecture selection is solving the wrong problem.

7. Decide extension boundaries: `DQ-014`, `DQ-015`, and `DQ-016`.
   - These are safest after the core benchmark is defined. They should be written as explicit “not now” or “phase 2” boundaries where appropriate.

8. Decide execution and governance discipline last: `DQ-018`, `DQ-019`, `DQ-020`, and `DQ-024`.
   - Verification bar, deployment boundary, active-versus-archived truth governance, and acceptable outcome classes are easier to specify once the owner knows what is being rebuilt and what claims phase 1 is allowed to make.

What can safely wait:
- Fine-grained extension timing such as static metadata or uncertainty outputs can wait until the first nine decisions are fixed.
- Service/API/auth decisions can wait if the owner explicitly confirms phase 1 is local research only.

## 9. Appendix: Citation Notes
| Citation focus | Path | Concrete location |
| --- | --- | --- |
| Governance hierarchy and hard gates | `AgentRules.md` | Lines 31-72, 98-191, 434-542, 678-737 |
| Research-workflow constraints | `docs/agent/AgentResearchWorkflows.md` | Lines 51-83, 85-120, 122-169 |
| Current active task contract | `docs/agent/agent_log/Current_State.md` | Lines 4-24, 25-59 |
| Root archival boundary | `LEGACY_DEPRECATION_SUMMARY.md` | Lines 3-15, 17-50 |
| Legacy snapshot status | `deprecated_version/legacy_snapshot_20260402T115014Z/README.md` | Lines 5-19 |
| Legacy snapshot archive scope | `deprecated_version/legacy_snapshot_20260402T115014Z/DEPRECATION_MANIFEST.txt` | Lines 8-12, 14-39 |
| Archived system goal and module boundaries | `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/architecture_overview.md` | Lines 5-16, 36-169, 171-193 |
| Archived storage layers and canonical tables | `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/data_layout.md` | Lines 10-18, 39-88, 146-299, 345-374 |
| Archived evaluation doctrine | `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/evaluation_protocol.md` | Lines 15-61, 71-120 |
| Archived implementation maturity and remaining priorities | `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/implementation_roadmap.md` | Lines 7-158, 160-189 |
| Older target framing and older embargo-style alignment example | `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/RESEARCH_DESIGN_old.md` | Lines 13-29, 46-62, 383-404, 409-442 |
| Code-evidenced horizons and label types | `deprecated_version/legacy_snapshot_20260402T115014Z/src/features/labels.py` | Lines 13-64 |
| Code-evidenced event-state construction | `deprecated_version/legacy_snapshot_20260402T115014Z/src/features/event_state.py` | Lines 17-95, 172-210 |
| Code-evidenced alignment logic | `deprecated_version/legacy_snapshot_20260402T115014Z/src/split/alignment_rules.py` | Lines 10-26, 29-59 |
| Code-evidenced purge/embargo logic | `deprecated_version/legacy_snapshot_20260402T115014Z/src/split/purged_embargo_splits.py` | Lines 46-145 |
| Code-evidenced corporate-action handling | `deprecated_version/legacy_snapshot_20260402T115014Z/src/data/corporate_actions.py` | Lines 82-183, 212-237, 326-354 |
| Code-evidenced simple multimodal gating and optional company branch | `deprecated_version/legacy_snapshot_20260402T115014Z/src/models/multimodal_models.py` | Lines 13-35, 59-121 |
| Code-evidenced baseline imputation | `deprecated_version/legacy_snapshot_20260402T115014Z/src/models/baseline_models.py` | Lines 140-171 |
| Smoke-scale empirical artifact evidence only | `deprecated_version/legacy_snapshot_20260402T115014Z/reports/eval_stage14_baseline/evaluation_summary.json` and `runs/*_summary.json` | `evaluation_summary.json` lines 2-10; `baseline_training_summary.json` lines 2-22; `multimodal_training_summary.json` lines 2-20 |
| Historical test-run evidence and stale NaN issue report | `deprecated_version/legacy_snapshot_20260402T115014Z/tests/results/Expanded_Testing_20260319T121411Z.md` | Lines 69-111, 117-166, 239-244 |
| Validator structure and current active-pass recheck | `scripts/validate_agent_governance.py` | Lines 12-23, 157-183, 492-527; manual run output on 2026-04-10: `VALIDATION PASSED` |
| Restart-era narrowing of the core thesis question | `docs/research_results/foundational_deep_research.md` | Lines 3-18, 89-132, 137-162, 1645-1674, 1929-1971 |
| Restart reconstruction and active-root-versus-archive framing | `docs/research_results/restarting_research.md` | Lines 168-236, 238-484, 561-638, 1011-1097 |
| Comparison-layer no-winner methodology | `docs/research_results/research_comparison.md` | Lines 58-76, 130-249, 1092-1175 |
| Category-specific target, feature, evaluation, extension, and repo-fit tradeoffs | `docs/research_results/research_comparison_addendum_*.md` | Targets lines 13-70 and 389-400; Features lines 13-48 and 309-317; Evaluation lines 10-52 and 213-223; Repo-fit lines 10-47 and 270-278 |
| Literature-note uncertainty preservation | `docs/research_results/paper_notes/restarting_research/S01_purge_embargo_validation_source_note.md` and paper notes `P02`, `P14`, `P17`, `P22`, `P23` | S01 lines 7-10 and 83-96; each listed paper note's verification and DOI/venue sections |
| Historical-window ambition and provider uncertainty | `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/RESEARCH_DESIGN_old.md`; `docs/research_results/foundational_deep_research.md`; `docs/research_results/restarting_research.md` | `RESEARCH_DESIGN_old.md` lines 251-277 and 357-373; `foundational_deep_research.md` lines 1645-1650; `restarting_research.md` lines 697-703 and 1093-1097 |
| No-news event-state behavior and benchmark relevance | `deprecated_version/legacy_snapshot_20260402T115014Z/src/features/event_state.py`; `docs/research_results/research_comparison_addendum_event_representations.md` | `event_state.py` lines 42-43 and 179-189; addendum lines 22-39 and 287-302 |
| Evidence packet and acceptable-outcome framing | `AgentRules.md`; `docs/agent/AgentMemory.md`; `docs/research_results/foundational_deep_research.md` | `AgentRules.md` lines 176-191; `AgentMemory.md` lines 190-205 and 749-790; `foundational_deep_research.md` lines 9-11 and 1669-1674 |
