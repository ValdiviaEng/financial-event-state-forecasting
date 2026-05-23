# Feedback Prompt For Complete Guidebook Upgrade

Status: final comprehensive feedback prompt. Created 2026-05-07 as a documentation-only prompt after reviewing the active `Complete_guidebook.txt`, the active scaffold files, `ProjectDefinition.md`, `ResearchTruth.md`, `ScopeDecisionLog.md`, and the deprecated guidebooks under `deprecated_version/legacy_snapshot_20260402T115014Z/`.

This prompt does not change project scope. It exists to guide a future AgentRules-compliant upgrade of `Complete_guidebook.txt` if the user asks for that update.

## 1. Purpose

Use this prompt to audit and upgrade `Complete_guidebook.txt` into a comprehensive active-root file map.

The upgraded guidebook should combine the best part of the deprecated guidebook, which was detailed file-by-file coverage, with the best part of the active guidebook, which is current ownership discipline and scope alignment.

The guidebook must remain a repository map. It must never become the source of theory truth, design truth, research truth, scope truth, approval truth, or implementation truth.

## 2. Required Ownership Hierarchy

Before changing anything, read and obey the active truth stack.

Required reading order:

1. `AgentRules.md`
2. `docs/agent/AgentAppendices.md`
3. `docs/agent/AgentMemory.md`
4. `docs/agent/agent_log/Current_State.md`
5. `docs/agent/agent_log/Event_Ledger.ndjson` as needed for continuity
6. `docs/agent/AgentGlossary.md`
7. `docs/agent/AgentTemplates.md`
8. `docs/agent/AgentCompliance.md`
9. `ProjectDefinition.md`
10. `ScopeDecisionLog.md`
11. `ResearchTruth.md`
12. `ScopeDefinition.md`
13. `docs/Implementation_Decisions.md`
14. `docs/Architecture_Map.md`
15. `docs/Execution_Plan.md`
16. `docs/Unit_Testing.md`
17. `docs/db_Testing.md`
18. `docs/Benchmark_Testing.md`
19. `docs/Pipeline_Testing.md`
20. `docs/Data_Update_Strategy.md`
21. `Complete_guidebook.txt`
22. Deprecated guidebooks for comparison only:
    - `deprecated_version/legacy_snapshot_20260402T115014Z/Complete_guidebook.txt`
    - `deprecated_version/legacy_snapshot_20260402T115014Z/docs/Complete_guidebook.txt`
    - `deprecated_version/legacy_snapshot_20260402T115014Z/Theoretical_Background/Complete_guidebook.txt`

## 3. Non-Negotiable Ownership Rules

The ownership hierarchy must not be lost.

| Artifact | Owns | Must Not Own |
| --- | --- | --- |
| `AgentRules.md` | Governance constitution, hierarchy, approval gates, documentation-first discipline, benchmark integrity discipline. | Project theory details or file-by-file implementation contracts. |
| `docs/agent/AgentMemory.md` | Interaction-log and operational-memory procedure. | Project theory, design, benchmark methodology, or implementation scope. |
| `docs/agent/agent_log/Current_State.md` | Current operational snapshot and task state. | Theory truth or owner-approved scope. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Authoritative logged event history where events exist. | Theory truth or benchmark methodology. |
| `ScopeDecisionLog.md` | Owner-approved scope decisions and questionnaire outcomes. | Detailed file map or implementation inventory. |
| `ResearchTruth.md` | Active research-truth synthesis, contradictions, historical-only evidence, unknowns, and current implementation-relevant truths. | Runtime file map or operational task register. |
| `ProjectDefinition.md` | Broad active project definition at architecture, pipeline, responsibility, and benchmark-family level. | Final module-level implementation contract or code behavior. |
| `ScopeDefinition.md` | Pre-decision questionnaire, option framing, evidence table, and contradiction inventory. | Current owner-approved scope after `ScopeDecisionLog.md` overrides it. |
| `docs/Implementation_Decisions.md` | Active design decision ledger and open design decisions. | Theory truth or owner-approved scope changes. |
| `docs/Architecture_Map.md` | Current architecture map and intended active layers. | Per-file exhaustive inventory or benchmark results. |
| Validation docs | Expected validation gates, planned tests, benchmark integrity, and pipeline gates. | Implementation truth or source-of-truth overrides. |
| `Complete_guidebook.txt` | Human-readable repository file map and status index. | Scope decisions, research truth, theory claims, design overrides, or implementation claims not evidenced elsewhere. |
| Deprecated guidebooks | Historical reference for useful guidebook format and coverage style. | Active truth, active implementation status, current provider stack, or current benchmark scope. |

If `Complete_guidebook.txt` conflicts with any higher-authority file, the higher-authority file wins. Fix the guidebook; do not change the higher-authority source to fit the guidebook.

## 4. Current Assessment Of Active `Complete_guidebook.txt`

The active `Complete_guidebook.txt` is correct as a compact high-level map, but it is not yet comprehensive enough for the user's stated goal.

Current strengths:

- It correctly identifies the active governance, scope, truth, docs, scripts, data, scaffold, and historical-reference areas.
- It correctly says the active `src/`, `configs/`, and `tests/` layers are comment-only scaffolds.
- It correctly avoids claiming that the active scaffold is executable implementation.
- It correctly mentions the Alpha Vantage top-50 raw file coverage state and that top-100/top-500 are not comparable by default.
- It is aligned with `ProjectDefinition.md`, `ScopeDecisionLog.md`, and `ResearchTruth.md` at a summary level.

Current weaknesses:

- It does not include a complete file-by-file inventory for all active files.
- It groups most `src/event_state_forecasting/` files by directory and does not list every scaffold file.
- It does not list the planned functions documented inside each comment-only scaffold file.
- It does not list planned variables/constants, planned imports, expected inputs, expected outputs, planned internal dependencies, planned config dependencies, planned tests, known limitations, or blind spots for each scaffold file.
- It does not provide per-file status fields beyond broad directory status.
- It does not provide per-file creation date, last-updated date, source-of-status evidence, implementation status, or owner/authority fields.
- It does not compare each active file against the deprecated guidebook or explain why old items were kept, changed, deferred, or rejected.
- It does not clearly distinguish active executable scripts from comment-only scaffold files at every path.
- It does not include a coverage checklist proving that every active file appears exactly once or in a deliberate grouped exception.
- It does not include a function/comment extraction checklist proving that planned functions in scaffold comments are represented.

Conclusion: active `Complete_guidebook.txt` is acceptable as a skeleton map, but not as the final comprehensive guidebook requested by the user.

## 5. Deprecated Guidebook Comparison

The deprecated guidebook is better in these ways:

- It is much more comprehensive and file-by-file.
- It uses a clear state legend, including `implemented`, `blueprint`, and `mixed`.
- It gives numbered entries for individual files.
- It records current role, current contents, docstring/comment intent, and current implementation notes.
- It includes test-file coverage and describes what tests verify.
- It includes an architectural summary and practical next implementation order.
- It captures implementation reality at the time of the deprecated snapshot, including executable modules, provider clients, data pipelines, feature builders, models, splits, utilities, and tests.

The deprecated guidebook is worse or unsafe in these ways:

- It reflects a historical snapshot, not the active root.
- It treats Finnhub as the historical news provider, while active phase 1 uses Alpha Vantage for news by owner decision DQ-008.
- It includes `pyproject.toml`, `requirements.txt`, `Makefile`, `.env.example`, legacy configs, active runtime modules, and active tests that are not current active-root truth.
- It includes historical package paths like `src/cli`, `src/data`, `src/features`, and `src/models`, while active scaffold uses `src/event_state_forecasting/`.
- It includes static company KB/company profile behavior that is out of phase 1 by owner decision DQ-014 unless later approved.
- It includes optional uncertainty, calibration, profile, and richer extension branches that active phase 1 explicitly defers.
- It claims executable implementation and test status that must not be carried into the active root.
- It lacks the current AgentRules ownership model, current interaction-log requirements, and active truth hierarchy.
- It has stale historical scope and provider assumptions.
- It contains duplicated or patch-like trailing lines near the end, so it should not be copied mechanically.

## 6. Best Of Both Worlds

The upgraded active guidebook should borrow the deprecated guidebook's format discipline, not its active claims.

Keep from the deprecated guidebook:

- Numbered, file-by-file entries.
- A status legend.
- Per-file current role.
- Per-file comment/docstring intent.
- Per-file implementation note.
- Per-file test note where relevant.
- Top-level architectural summary.
- Practical next-step summary.

Reject from the deprecated guidebook:

- Historical active-status claims.
- Finnhub-as-active-provider assumptions.
- Direct old paths unless clearly marked historical-only.
- Static KB as phase-1 model input.
- Uncertainty-aware outputs as phase-1 defaults.
- Legacy executable pipeline claims.
- Any claim that archived code is active implementation truth.

Add from the active root:

- AgentRules ownership hierarchy.
- Explicit non-overriding role of `Complete_guidebook.txt`.
- Active phase-1 protected values from `ScopeDecisionLog.md`.
- Active current-state reality from `ProjectDefinition.md` and `ResearchTruth.md`.
- Comment-only scaffold status for every generated `.py` and `.yaml` file.
- The fact that generated test files are planned tests only, not executable tests.
- Current Alpha Vantage raw file coverage and truncation blockers.
- API-key-bearing raw ledger risk.
- Evidence pointers and dates where available.

## 7. Required Status Legend For The Upgraded Guidebook

Use this active-root status legend.

| State | Meaning |
| --- | --- |
| `governance-active` | Active governance file that controls agent behavior or continuity. |
| `truth-active` | Active scope, research truth, project definition, or owner-decision file. |
| `design-active` | Active design, architecture, execution, validation, operations, or onboarding doc. |
| `script-active` | Executable active-root script evidenced as current behavior. |
| `data-evidence` | Raw data, manifest, log, or report artifact that evidences current state but is not implementation. |
| `comment-only-scaffold` | Python or YAML scaffold file containing only comments and no runnable behavior. |
| `planned-test-comment-only` | Test scaffold file containing only comments and no executable assertions/imports. |
| `reference-only` | Historical, deprecated, course, reference, or reset material that is not active truth unless explicitly adopted. |
| `generated-or-local` | Local, generated, cache, secret, or runtime artifact that should be excluded or summarized only. |
| `unknown-or-unverified` | File exists but status is not proven; must use `Plausible but unverified.` and propose verification. |

Do not use the deprecated states `implemented`, `blueprint`, and `mixed` without translating them into the active-root legend.

## 8. Required Per-File Entry Template

Every active project-maintained file should have an entry unless it is deliberately grouped with a documented exception.

Use this template for each file:

```text
N) Path: `relative/path`
- State: [governance-active | truth-active | design-active | script-active | data-evidence | comment-only-scaffold | planned-test-comment-only | reference-only | generated-or-local | unknown-or-unverified]
- Created: [date from file, ledger, git, or Not evidenced in repository materials.]
- Last updated: [date from file, ledger, git, or Not evidenced in repository materials.]
- Current owner/authority: [which source owns the file's truth role]
- Current role: [1-3 lines]
- Implementation status: [executable, non-executable comment-only, active data evidence, reference-only, or not evidenced]
- What it currently contains: [concrete content summary]
- What its comments/docstrings say it is supposed to do: [summary]
- Planned functions or implemented functions: [function names and responsibilities, or none]
- Planned variables/constants/config keys: [names and responsibilities, or none]
- Expected inputs: [from comments, docs, or not applicable]
- Expected outputs: [from comments, docs, or not applicable]
- Internal dependencies: [planned or implemented, with direction check]
- Config dependencies: [planned or implemented]
- Tests or planned tests: [linked test files or planned test intent]
- Benchmark implications: [rows, labels, splits, metrics, artifacts, comparability, or none]
- Security/privacy implications: [API keys, raw ledgers, paths, secrets, or none]
- Known limitations and blind spots: [specific limitations]
- Evidence pointers: [file header, docs, ledger event, validation output, or Not evidenced in repository materials.]
```

For comment-only scaffold files, explicitly say:

- `Implementation status: non-executable comment-only scaffold; no imports, functions, assignments, classes, active config, or assertions.`
- `Planned functions or implemented functions:` must list planned function names from comments, not active functions.
- `Benchmark implications:` must describe planned implications only and must not claim current behavior.

For active executable scripts, list actual implemented responsibilities and validation evidence. Do not infer untested behavior.

For data files and manifests, list evidence value, row counts or status where available, and limitations. Do not treat raw data coverage as benchmark readiness.

For deprecated/reference files, state clearly that they are reference-only and cannot override active truth.

## 9. Required File Coverage

At minimum, the upgraded guidebook must cover these active-root areas.

Root files:

- `AgentRules.md`
- `ProjectDefinition.md`
- `StructuralFolderMapPrompt.md`
- `feedbackprompt.md` if this prompt has been created
- `ScopeDefinition.md`
- `ScopeDecisionLog.md`
- `ResearchTruth.md`
- `LEGACY_DEPRECATION_SUMMARY.md`
- `README.md`
- `ExecutionFlow.md`
- `Complete_guidebook.txt`
- `project_one_page.tex`

Active docs:

- `docs/Complete_Theoretical_Background.md`
- `docs/References.md`
- `docs/Implementation_Decisions.md`
- `docs/Architecture_Map.md`
- `docs/Execution_Plan.md`
- `docs/Unit_Testing.md`
- `docs/db_Testing.md`
- `docs/Benchmark_Testing.md`
- `docs/Pipeline_Testing.md`
- `docs/Data_Update_Strategy.md`
- `docs/testing_commands.md`
- `docs/research_results/` with a grouped summary plus key index files if too large for per-file detail
- `docs/agent/` governance companions, each individually listed
- `docs/agent/agent_log/` operational memory and audit/report artifacts, each individually listed if project-maintained
- `docs/course_material/` and `docs/reference_guides/` as grouped reference-only areas unless the user requests per-file mapping

Active scripts:

- `scripts/validate_agent_governance.py`
- `scripts/alphavantage_news_bucket_common.py`
- `scripts/run_alphavantage_news_top50_only_standalone.py`
- `scripts/run_alphavantage_news_top51_100_only_standalone.py`
- `scripts/run_alphavantage_news_top51_75_only_standalone.py`
- `scripts/run_alphavantage_news_top76_100_only_standalone.py`
- `scripts/run_alphavantage_news_top101_200_only_standalone.py`
- `scripts/run_alphavantage_news_top201_300_only_standalone.py`
- `scripts/run_alphavantage_news_top301_400_only_standalone.py`
- `scripts/run_alphavantage_news_top401_500_only_standalone.py`
- `scripts/run_alphavantage_news_multi_bucket_portable_standalone.py`

Active data evidence:

- `data/raw/universe/` and key files under it
- `data/raw/alphavantage/` summarized carefully because raw payload volume may be large
- `data/raw/alphavantage/daemon_summary_top50_only_forward.json`
- `data/raw/alphavantage/news_request_ledger.jsonl` with API-key-bearing risk warning if present
- `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json`
- Any audit or merge report under `docs/agent/agent_log/`

Comment-only scaffold files:

- All 68 Python files under `src/event_state_forecasting/**/*.py` as of the 2026-05-07 scaffold creation.
- All 9 YAML files under `configs/*.yaml` as of the 2026-05-07 scaffold creation.
- All 23 Python files under `tests/**/*.py` as of the 2026-05-07 scaffold creation.

Historical/reference areas:

- `deprecated_version/legacy_snapshot_20260402T115014Z/` as historical-only reference.
- `reset/` as reusable scaffold/reference only.

## 10. Required Scaffold Extraction Rules

For each generated scaffold `.py` file, extract these comment blocks into the guidebook entry:

- `File`
- `Status`
- `Layer`
- `Governing docs`
- `Purpose`
- `In scope`
- `Out of scope`
- `Expected inputs`
- `Expected outputs`
- `Planned imported libraries`
- `Planned internal dependencies`
- `Planned configuration dependencies`
- `Planned variables and constants`
- `Planned functions`
- `Planned tests`
- `Known limitations and blind spots`
- `Completion rule`

For each generated YAML file, extract:

- `File`
- `Status`
- `Governing docs`
- `Purpose`
- planned config sections
- planned keys
- expected types
- default policy
- validation
- benchmark impact
- protected values
- limitations

For each generated test file, extract:

- `File`
- `Status`
- target future module
- governing docs
- test purpose
- future fixtures
- expected behaviors
- edge cases
- benchmark integrity checks
- blind spots

If extraction finds a scaffold file missing a required block, do not silently fill it in. Record the gap in a guidebook audit section and recommend a future scaffold correction.

## 11. Required Function Coverage

The user's question asks whether the guidebook includes all comments for all files and all functions. The current guidebook does not.

The upgraded guidebook must include a dedicated section called `Function And Planned-Function Index`.

For active executable scripts:

- list implemented functions/classes only after reading the file directly.
- if unsure, state `Plausible but unverified.` and name the verification step.

For comment-only scaffold files:

- list planned function names exactly as comment text.
- mark each one `planned only; not implemented`.
- include inputs, outputs, logical flow, error handling, benchmark implications, and limitations from the scaffold comments.

For config files:

- list planned config sections and planned keys, not active keys.
- mark them `comment-only planned config; not active config`.

For tests:

- list planned test purposes and target future modules.
- mark them `planned test only; no executable assertions`.

## 12. Required Comparative Analysis Section

Add a section to the upgraded guidebook called `Active vs Deprecated Guidebook Comparison`.

It must answer:

1. What active guidebook does better.
2. What deprecated guidebook does better.
3. What active guidebook does worse.
4. What deprecated guidebook does worse or dangerously.
5. What exact mixed approach is adopted.
6. Why the mixed approach does not change ownership or active truth.

Use this conclusion unless new evidence contradicts it:

- Best approach: use the deprecated guidebook's detailed per-file format and implementation-note discipline, but use only active-root truth from `AgentRules.md`, `ProjectDefinition.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`, active docs, active scripts, active data evidence, and generated scaffold comments.
- Do not copy deprecated implementation claims into active status.
- Do not copy deprecated provider assumptions into active scope.
- Do not copy deprecated static-KB or uncertainty defaults into phase-1 status.
- Do not treat archive code as active implementation.

## 13. Required Active Scope Guardrails

The upgraded guidebook must repeat these protected active definitions in a status section and must not alter them:

| Protected Area | Active Definition |
| --- | --- |
| Target family | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| First serious universe | Reproducible top-50 liquid large-cap universe. |
| OHLCV provider | Twelve Data. |
| News provider | Alpha Vantage. |
| SEC role | Static/company support only; not phase-1 static feature modeling by default. |
| Alignment | Same-day as-of-close; after-hours and non-trading-day news roll forward. |
| Event representation | Pooled dense embeddings plus scalar enrichments. |
| Fusion default | Simple gated fusion. |
| No-news policy | Keep rows and encode explicit empty event state plus no-news indicators. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Phase-1 mode | Local CLI/artifact-driven research only. |
| Serious-run artifacts | Dataset version, manifest, resolved config, folds, saved predictions, metrics, and comparison summary. |

## 14. Required Current-State Cautions

The upgraded guidebook must include these cautions in relevant entries:

- Active `src/`, `configs/`, and `tests/` are comment-only scaffolds.
- No executable pipeline exists in the active `src/` scaffold.
- No active config exists in `configs/`; YAML files are comments only.
- No executable test suite exists under `tests/`; test files are comments only.
- Active implementation currently consists of governance validation and Alpha Vantage standalone scripts under `scripts/`.
- Alpha Vantage top-50 canonical raw file coverage is 850/850, but this is raw file coverage only.
- 92 likely truncated Alpha Vantage top-50 windows remain unresolved.
- Raw request ledgers may contain API-key-bearing URLs and must not be committed or shared as-is.
- Top-100/top-500 expansion data is not comparable to the first top-50 benchmark family unless explicitly approved.
- Deprecated code is reference-only until reintroduced through active docs and approved scope.
- No materialized benchmark dataset, benchmark runner, model result, or serious benchmark claim exists yet.

## 15. Verification Requirements

Before writing an upgraded `Complete_guidebook.txt`, verify coverage.

Required checks:

- Count active `src/event_state_forecasting/**/*.py` files and confirm each path appears in the guidebook.
- Count active `configs/*.yaml` files and confirm each path appears in the guidebook.
- Count active `tests/**/*.py` files and confirm each path appears in the guidebook.
- Check every scaffold `.py` file for `Planned functions, comments only` and ensure planned function names appear in the `Function And Planned-Function Index`.
- Check every scaffold YAML file for planned config sections and ensure they appear in the config index.
- Check every test scaffold for target future module and test purpose and ensure they appear in the test index.
- Confirm every scaffold file status is non-runnable/comment-only.
- Confirm no guidebook entry claims active behavior for comment-only scaffold files.
- Confirm deprecated paths are marked reference-only.
- Confirm provider stack is Twelve Data plus Alpha Vantage plus SEC support only.
- Confirm no guidebook text promotes static KB, uncertainty-aware outputs, graph-heavy models, MoE, dynamic profiles, end-to-end text fine-tuning, broad derivative grids, dashboards, APIs, authentication, or full live-universe benchmarking into phase 1.

Recommended validation commands after an actual guidebook update:

```powershell
python scripts/validate_agent_governance.py
```

Run a text coverage check to verify all scaffold paths appear in `Complete_guidebook.txt`. If writing a script for this, keep it temporary unless the user asks to add a permanent validator.

## 16. Editing Rules For A Future Execution

If the user asks to execute this prompt:

1. Update `Complete_guidebook.txt` comprehensively.
2. Do not change protected scope.
3. Do not edit scaffold files unless the user explicitly asks for scaffold corrections.
4. Do not edit `ProjectDefinition.md`, `ScopeDecisionLog.md`, or `ResearchTruth.md` to match the guidebook; fix the guidebook instead.
5. Update operational memory and ledger according to `docs/agent/AgentMemory.md`, unless the user explicitly constrains the task in a way that conflicts with memory edits. If such a conflict exists, stop and ask for clarification.
6. Run governance validation.
7. Report changed files, validation results, guidebook coverage counts, and remaining gaps.

## 17. Final Response Requirements For A Future Execution

When this prompt is executed in the future, the final response must report:

1. Whether `Complete_guidebook.txt` was fully upgraded or only audited.
2. File counts covered by category.
3. Function/planned-function index coverage status.
4. Config section coverage status.
5. Test scaffold coverage status.
6. Deprecated guidebook elements adopted.
7. Deprecated guidebook elements rejected.
8. Ownership protections preserved.
9. Validation commands and results.
10. Explicit statement that the guidebook update did not create an executable pipeline, dataset builder, model, active config, executable test suite, benchmark runner, or benchmark result.

## 18. Current Feedback Summary

Current answer to the user's verification question:

- Does active `Complete_guidebook.txt` correctly include all comments for all files and all functions? No. It is currently a high-level map, not a complete comment/function inventory.
- Does it annotate implementation status? Partly. It correctly marks broad scaffold status as comment-only, but it lacks per-file implementation status and per-file evidence.
- Does it include dates? Partly. It has a top-level created/updated date, but not per-file created/updated dates.
- Does it follow AgentRules and Agent*.md ownership? Mostly at a summary level. It does not appear to violate active truth, but it is not comprehensive enough to serve as the final guidebook requested.
- What is better in the active guidebook? Current truth alignment, compactness, ownership safety, comment-only scaffold caution, and current provider/scope correctness.
- What is better in the deprecated guidebook? File-by-file completeness, state legend, role descriptions, docstring/comment summaries, implementation notes, test summaries, and architectural summary.
- Best path: rebuild the active guidebook using the deprecated guidebook's detailed structure while preserving active ownership, active scope, active provider stack, and comment-only status.

End of feedback prompt.
