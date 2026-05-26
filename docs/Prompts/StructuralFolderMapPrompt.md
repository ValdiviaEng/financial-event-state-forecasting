# Structural Folder Map Prompt

Status: final reusable prompt for creating the active-root barebones folder structure in comment-only mode. This prompt is governed by `AgentRules.md`, `docs/agent/AgentMemory.md`, `ScopeDecisionLog.md`, `ResearchTruth.md`, and `ProjectDefinition.md`.

Use this document as the complete instruction set when the user asks to create the live repository folder scaffold. The scaffold must be structural only. It must not implement runtime behavior.

## 1. Prompt To Execute

You are working in the live active root of the `event-state-forecasting` repository. Your task is to create the final barebones project folder structure and comment-only file scaffold for the approved phase-1 rebuild.

Follow `AgentRules.md` and all dependent `docs/agent/Agent*.md` files. Read and obey the active truth stack before writing anything.

Required reading order:

1. `AgentRules.md`
2. `docs/agent/AgentAppendices.md`
3. `docs/agent/AgentMemory.md`
4. `docs/agent/agent_log/Current_State.md`
5. `docs/agent/agent_log/Event_Ledger.ndjson` as needed for continuity
6. `docs/agent/AgentGlossary.md`
7. `docs/agent/AgentTemplates.md`
8. `docs/agent/AgentResearchWorkflows.md` if research comparison is consulted
9. `docs/agent/AgentCompliance.md`
10. `ProjectDefinition.md`
11. `ScopeDecisionLog.md`
12. `ResearchTruth.md`
13. `docs/Implementation_Decisions.md`
14. `Architecture_Map.md`
15. `docs/Execution_Plan.md`
16. validation and operations docs under `docs/`

## 2. Task Objective

Create `src/`, `configs/`, and `tests/` as a comment-only active-root scaffold for the approved phase-1 architecture.

The scaffold must document the intended responsibilities, inputs, outputs, dependencies, logical flow, validation rules, limitations, and blind spots of every future file. It must not contain real implementation.

The scaffold must combine the useful architectural coverage of the deprecated snapshot with the current owner-approved active truth. Do not copy legacy code. Do not reactivate the archive. Treat the deprecated snapshot as reference-only.

## 3. Non-Negotiable Rules

Every generated scaffold file must be comment-only.

For Python files:

1. Allowed lines are blank lines and lines starting with `#`.
2. Do not include `import`, `from`, `def`, `class`, assignments, constants, decorators, docstrings, executable expressions, type aliases, or pass statements.
3. Do not include triple-quoted strings.
4. Do not include code fences inside generated Python files.
5. `__init__.py` files must also be comment-only.

For YAML files:

1. Allowed lines are blank lines and lines starting with `#`.
2. Do not include actual YAML keys or values yet.
3. Planned keys may be described only as comments.

For test files:

1. Test files must be comment-only Python files.
2. They must describe test intent, fixtures, invariants, expected outcomes, edge cases, and known blind spots.
3. They must not contain executable assertions or imports.

For generated docs:

1. Avoid generating new markdown files inside `src/`, `configs/`, or `tests/` unless explicitly required.
2. Existing project docs may be updated normally to record the new file map and current status.

## 4. Hard Scope Boundaries

Do not change the approved phase-1 scope.

Do not change:

| Protected Area | Approved Definition |
| --- | --- |
| Target family | Forward excess returns. |
| Horizons | `1d`, `5d`, `10d`, `20d`, `60d`. |
| Universe | First serious benchmark uses top-50 liquid large-cap universe. |
| Providers | Twelve Data for OHLCV, Alpha Vantage for news, SEC for static/company support only. |
| Alignment | Same-day as-of-close, after-hours and non-trading-day news roll forward. |
| Evaluation | Purged-plus-embargoed walk-forward plus final untouched lockbox. |
| Phase-1 mode | Local CLI/artifact-driven research only. |
| Event representation | Pooled dense embeddings plus scalar enrichments. |
| Fusion default | Simple gated fusion. |
| No-news policy | Keep rows and encode explicit empty event state plus no-news indicators. |

Do not introduce active phase-1 implementations for static company metadata, uncertainty-aware outputs, graph-heavy models, MoE, dynamic profiles, end-to-end text fine-tuning, broad derivative grids, dashboards, APIs, authentication, or full live-universe first-pass benchmarking.

## 5. Scaffold Design Principles

Use these principles when creating the folder map.

| Principle | Required Meaning |
| --- | --- |
| Documentation first | Every file must explain intended behavior before implementation exists. |
| One responsibility per file | Avoid files that mix provider fetching, feature building, training, evaluation, and operations. |
| Active truth over archive | Borrow legacy coverage only when compatible with `ProjectDefinition.md`, `ScopeDecisionLog.md`, and `ResearchTruth.md`. |
| Benchmark comparability first | File comments must surface rows, labels, split boundaries, and artifact implications. |
| Leakage awareness | Alignment, target, split, feature, and evaluation files must document leakage risks. |
| Raw preservation | Provider data files must preserve raw payloads and manifests; no silent overwrites. |
| Artifact discipline | Benchmark files must make dataset version, manifest, config, folds, predictions, metrics, and comparison summary first-class. |
| Operations visibility | Truncation, ledger sanitization, rollback, and data refresh must have explicit homes. |
| No hidden implementation | Comment-only files must never look runnable. |

## 6. Final Folder Structure

Create this structure unless an active higher-authority document has changed it. If a conflict exists, stop and request clarification.

```text
src/
  event_state_forecasting/
    __init__.py
    cli/
      __init__.py
      audit_raw_data.py
      build_benchmark_dataset.py
      build_features_and_labels.py
      build_market_data.py
      build_news_data.py
      build_splits.py
      run_benchmark.py
      sanitize_provider_ledgers.py
      summarize_run.py
      validate_universe.py
    data/
      __init__.py
      contracts.py
      corporate_actions.py
      manifests.py
      quality_checks.py
      raw_validation.py
      split_events.py
      storage_layout.py
      universe.py
      providers/
        __init__.py
        alphavantage_news.py
        sec_support.py
        twelvedata_ohlcv.py
    dataset/
      __init__.py
      dataset_versioning.py
      panel_builder.py
      row_universe.py
    features/
      __init__.py
      embeddings.py
      event_state.py
      labels.py
      market.py
      news_alignment.py
      no_news_state.py
      text_normalization.py
    split/
      __init__.py
      leakage_checks.py
      lockbox.py
      purged_embargo.py
    models/
      __init__.py
      comparator_ladder.py
      gated_fusion.py
      inference.py
      market_baselines.py
      training.py
    evaluation/
      __init__.py
      comparison_summary.py
      ranking.py
      regression.py
      statistical_tests.py
    benchmark/
      __init__.py
      artifact_packet.py
      registry.py
      runner.py
    ops/
      __init__.py
      data_refresh.py
      ledger_sanitization.py
      rollback.py
      truncation_refinement.py
    utils/
      __init__.py
      hashing.py
      logging.py
      paths.py
      reproducibility.py
      time.py
      validation.py
configs/
  artifact_packet.example.yaml
  data_contracts.example.yaml
  evaluation.example.yaml
  features.example.yaml
  labels.example.yaml
  models.example.yaml
  phase1_top50_benchmark.yaml
  providers.example.yaml
  splits.example.yaml
tests/
  __init__.py
  benchmark/
    test_artifact_packet_contract.py
    test_benchmark_runner_contract.py
  data/
    test_contracts_contract.py
    test_raw_validation_contract.py
    test_universe_contract.py
  dataset/
    test_panel_builder_contract.py
    test_row_universe_contract.py
  evaluation/
    test_metric_contracts.py
  features/
    test_event_state_contract.py
    test_labels_contract.py
    test_market_features_contract.py
    test_news_alignment_contract.py
    test_no_news_state_contract.py
  integration/
    test_pipeline_contract.py
    test_provider_contracts.py
  models/
    test_comparator_ladder_contract.py
    test_gated_fusion_contract.py
  ops/
    test_ledger_sanitization_contract.py
    test_truncation_refinement_contract.py
  split/
    test_leakage_contract.py
    test_purged_embargo_contract.py
  utils/
    test_reproducibility_contract.py
```

## 7. Why This Structure Is The Active Choice

This structure is a hybrid of the deprecated snapshot and the current approved rebuild.

It preserves useful legacy boundaries such as provider clients, data contracts, corporate actions, feature generation, split logic, models, evaluation, CLI entry points, configs, and tests.

It changes the shape where current truth requires it:

| Deprecated Pattern | Active Scaffold Difference | Reason |
| --- | --- | --- |
| Finnhub was the main news provider. | Alpha Vantage is the phase-1 news provider. | Owner decision DQ-008. |
| Evaluation utilities lived partly under `models/`. | Evaluation has a separate package. | Metrics and saved-prediction comparison are not model internals. |
| Benchmark artifacts were less structurally central. | `benchmark/artifact_packet.py` is first-class. | Serious runs require full artifact packets. |
| Company KB was present in active design. | SEC support is isolated and static metadata is not phase-1 model input. | Owner decision DQ-014. |
| Pipeline code was executable. | Active scaffold is comment-only. | AgentRules documentation-first gate and active rebuild status. |
| Legacy root modules were under `src/` directly. | Active package namespace is `src/event_state_forecasting/`. | Cleaner import namespace for future implementation. |
| Operations were spread across pipeline docs and scripts. | `ops/` has explicit refresh, truncation, ledger, and rollback homes. | Current blockers require visible operational ownership. |

## 8. File Comment Template For Python Files

Every generated Python file must follow this comment-only template.

```text
# File: relative/path/to/file.py
# Status: COMMENT-ONLY SCAFFOLD - NOT IMPLEMENTED
# Layer: [governance-adjacent | data | dataset | features | split | models | evaluation | benchmark | ops | utils | cli | tests]
# Governing docs: AgentRules.md; ProjectDefinition.md; ScopeDecisionLog.md; ResearchTruth.md; Architecture_Map.md; docs/Implementation_Decisions.md
#
# Purpose:
# - Describe the future file responsibility in 2-5 concise comment lines.
#
# In scope:
# - Describe exactly what this future file may own.
#
# Out of scope:
# - Describe what this file must not own.
#
# Expected inputs:
# - Input name: expected type or artifact family; source; required fields; timing assumptions; validation expectations.
#
# Expected outputs:
# - Output name: expected type or artifact family; destination layer; required metadata; downstream consumers.
#
# Planned imported libraries, comments only:
# - Library name: why it may be needed; whether it is standard library or external; approval or dependency status; risk if unavailable.
#
# Planned internal dependencies, comments only:
# - Module path: intended future relationship; why dependency direction is valid; circular-dependency risk.
#
# Planned configuration dependencies, comments only:
# - Config path or key family: intended use; default policy; validation requirement.
#
# Planned variables and constants, comments only:
# - VARIABLE_NAME: meaning; expected type; units; source; allowed values or range; null behavior; leakage or comparability risk.
#
# Planned functions, comments only:
# - function_name:
#   Inputs: names, types, required columns or fields, timestamp assumptions, validation preconditions.
#   Outputs: return artifact, side effects if any, manifest or metadata obligations.
#   Logical flow: high-level ordered behavior without pseudo-code.
#   Error handling: invalid input, missing data, provider failure, schema drift, empty result, timestamp issue.
#   Benchmark implications: whether rows, labels, splits, metrics, or comparability may change.
#   Limitations: known blind spots, assumptions, unresolved decisions.
#
# Planned tests, comments only:
# - Test intent: invariant or behavior future tests must verify.
#
# Known limitations and blind spots:
# - Document leakage risks, provider limits, data incompleteness, timestamp ambiguity, survivorship risk, API-key risk, or benchmark drift risk where relevant.
#
# Completion rule:
# - This file remains non-runnable until the relevant active design contract and tests are approved.
```

Do not include the nested indentation in executable form. It is comment text only.

## 9. File Comment Template For YAML Config Files

Every generated YAML file must be comment-only.

```text
# File: configs/example.yaml
# Status: COMMENT-ONLY CONFIG SCAFFOLD - NOT ACTIVE CONFIG
# Governing docs: ProjectDefinition.md; ScopeDecisionLog.md; ResearchTruth.md; docs/Implementation_Decisions.md
#
# Purpose:
# - Describe which future configuration family this file will control.
#
# Planned config sections, comments only:
# - section_name:
#   Meaning: intended responsibility.
#   Planned keys: key names as comments only.
#   Expected types: string, integer, float, boolean, list, mapping, path, date, duration, enum.
#   Default policy: whether defaults are allowed, explicit, or forbidden.
#   Validation: required checks before use.
#   Benchmark impact: whether changes alter comparability.
#
# Protected values:
# - Target family, horizons, provider stack, universe, alignment, and evaluation protocol must match approved scope unless explicit approval changes them.
#
# Limitations:
# - This file is not active until real keys are approved and implemented.
```

## 10. File Comment Template For Test Files

Every generated test file must describe future tests only.

```text
# File: tests/path/test_name.py
# Status: COMMENT-ONLY TEST SCAFFOLD - NOT IMPLEMENTED
# Target future module: src/event_state_forecasting/path/module.py
# Governing docs: docs/Unit_Testing.md; docs/db_Testing.md; docs/Benchmark_Testing.md; docs/Pipeline_Testing.md
#
# Test purpose:
# - Describe the future invariant or contract being tested.
#
# Future fixtures:
# - Fixture name: source, minimal data shape, fields, edge cases, timestamp assumptions.
#
# Expected behaviors:
# - Behavior: condition, expected result, failure mode.
#
# Edge cases:
# - Missing values, no-news rows, empty feeds, truncated provider windows, non-trading days, after-hours news, dotted tickers, split events, horizon endpoints.
#
# Benchmark integrity checks:
# - Explain whether the test protects row equality, label correctness, split leakage, artifact completeness, or comparability.
#
# Blind spots:
# - Explain what this future test will not prove.
```

## 11. Variable Description Rules

When documenting planned variables, constants, config keys, or manifest fields, every entry must include these attributes where relevant.

| Attribute | Required Description |
| --- | --- |
| Name | Planned variable, constant, config key, or field name. |
| Meaning | Plain-English purpose. |
| Type | Expected future type or artifact family. |
| Units | Required for time, returns, volumes, counts, dimensions, and rates. |
| Source | Provider, config, upstream table, manifest, user input, or derived value. |
| Allowed values | Enum, range, nullability, or format constraints. |
| Default policy | Whether defaults are allowed or must be explicit. |
| Validation | How correctness should be checked later. |
| Benchmark impact | Whether changing it can alter benchmark comparability. |
| Security risk | Whether it can expose credentials, paths, provider URLs, or sensitive metadata. |
| Blind spots | Known limitations or failure modes. |

## 12. Function Description Rules

When documenting planned functions, every function comment block must include these attributes.

| Attribute | Required Description |
| --- | --- |
| Function name | Future name in snake_case. |
| Responsibility | One clear responsibility. |
| Inputs | Dataframes, tables, paths, configs, manifests, timestamps, models, or predictions. |
| Input preconditions | Required columns, schemas, sortedness, uniqueness, timestamp availability, and validated upstream state. |
| Outputs | Return artifact, written artifact, manifest update, metrics, or validation result. |
| Logical flow | Ordered natural-language steps without pseudo-code. |
| Side effects | Files written, logs, manifests, provider calls, cache updates, or none. |
| Error handling | Missing data, invalid schema, provider failure, empty result, leakage risk, credential leak, inconsistent row universe. |
| Validation | Future checks before and after execution. |
| Benchmark implications | Whether the function can affect row universe, labels, folds, metrics, artifacts, or comparability. |
| Limitations | Known unresolved decisions and blind spots. |

No function body may be created in this scaffold.

## 13. Imported Library Description Rules

Do not write real imports. Describe planned imports as comments only.

Every planned library comment must include:

| Attribute | Required Description |
| --- | --- |
| Library | Planned future library name. |
| Status | Standard library, likely dependency, optional dependency, or not yet approved. |
| Purpose | Why the future module may need it. |
| Replacement | Simpler fallback if the dependency is not approved. |
| Risk | Security, compute, reproducibility, install burden, or provider-coupling concerns. |
| Approval status | Whether active docs already justify it or future approval is required. |

Do not create `pyproject.toml`, `requirements.txt`, or `Makefile` unless the user explicitly asks. Dependency tooling requires a separate design decision.

## 14. Dependency Direction Rules

The future dependency flow must be one-way where possible.

Allowed conceptual dependency direction:

```text
utils -> data/providers -> data/contracts -> data/validation -> dataset -> features -> split -> models -> evaluation -> benchmark -> ops/cli orchestration
```

Rules:

1. Provider modules must not depend on feature, model, benchmark, or evaluation modules.
2. Feature modules must not make provider calls.
3. Split modules must not train models.
4. Evaluation modules must operate on saved predictions and frozen labels, not hidden training state.
5. Benchmark modules may orchestrate approved components but must not redefine targets, horizons, providers, or split policy.
6. CLI modules may orchestrate workflows but must stay thin and must not own scientific logic.
7. Ops modules may handle refresh, sanitization, rollback, and truncation workflows but must not silently change benchmark definitions.

## 15. File Responsibility Map

Use these responsibilities when writing each scaffold file.

| Path | Future Responsibility |
| --- | --- |
| `src/event_state_forecasting/cli/audit_raw_data.py` | Future CLI orchestration for raw coverage, schema, truncation, and credential-risk audits. |
| `src/event_state_forecasting/cli/build_benchmark_dataset.py` | Future CLI orchestration for manifest-backed benchmark dataset construction. |
| `src/event_state_forecasting/cli/build_features_and_labels.py` | Future CLI orchestration for market features, event-state features, no-news states, and forward excess-return labels. |
| `src/event_state_forecasting/cli/build_market_data.py` | Future CLI orchestration for approved OHLCV ingestion or normalization. |
| `src/event_state_forecasting/cli/build_news_data.py` | Future CLI orchestration for Alpha Vantage news normalization after raw ingestion. |
| `src/event_state_forecasting/cli/build_splits.py` | Future CLI orchestration for purged-plus-embargoed folds and lockbox creation. |
| `src/event_state_forecasting/cli/run_benchmark.py` | Future CLI orchestration for approved benchmark runs and artifact packets. |
| `src/event_state_forecasting/cli/sanitize_provider_ledgers.py` | Future CLI orchestration for API-key-bearing ledger sanitization. |
| `src/event_state_forecasting/cli/summarize_run.py` | Future CLI orchestration for run summaries without changing metrics. |
| `src/event_state_forecasting/cli/validate_universe.py` | Future CLI orchestration for frozen universe validation. |
| `src/event_state_forecasting/data/contracts.py` | Future canonical schema and contract definitions for raw, interim, final, prediction, and artifact tables. |
| `src/event_state_forecasting/data/corporate_actions.py` | Future split and adjustment support for market-data validity. |
| `src/event_state_forecasting/data/manifests.py` | Future manifest field definitions and manifest validation responsibilities. |
| `src/event_state_forecasting/data/quality_checks.py` | Future generic data-quality checks before downstream use. |
| `src/event_state_forecasting/data/raw_validation.py` | Future raw provider payload validation, parse checks, coverage checks, truncation flag checks, and empty-feed checks. |
| `src/event_state_forecasting/data/split_events.py` | Future source and normalization home for split-event evidence. |
| `src/event_state_forecasting/data/storage_layout.py` | Future storage layer conventions for raw, interim, final, embeddings, manifests, and artifacts. |
| `src/event_state_forecasting/data/universe.py` | Future frozen universe reading, validation, ticker normalization policy, and universe manifest responsibilities. |
| `src/event_state_forecasting/data/providers/alphavantage_news.py` | Future Alpha Vantage provider boundary for news only. |
| `src/event_state_forecasting/data/providers/sec_support.py` | Future SEC support boundary, not phase-1 static feature modeling by default. |
| `src/event_state_forecasting/data/providers/twelvedata_ohlcv.py` | Future Twelve Data OHLCV provider boundary. |
| `src/event_state_forecasting/dataset/dataset_versioning.py` | Future dataset version identity, version comparison, and invalidation metadata. |
| `src/event_state_forecasting/dataset/panel_builder.py` | Future market-only and event-state panel assembly on identical row universe. |
| `src/event_state_forecasting/dataset/row_universe.py` | Future row-universe definition, no-news row preservation, and row equality checks. |
| `src/event_state_forecasting/features/embeddings.py` | Future dense text embedding interface and embedding metadata responsibilities. |
| `src/event_state_forecasting/features/event_state.py` | Future pooled dense embedding plus scalar enrichment construction. |
| `src/event_state_forecasting/features/labels.py` | Future forward excess-return labels for approved horizons. |
| `src/event_state_forecasting/features/market.py` | Future end-of-day market feature generation. |
| `src/event_state_forecasting/features/news_alignment.py` | Future same-day as-of-close news alignment with roll-forward rules. |
| `src/event_state_forecasting/features/no_news_state.py` | Future explicit empty event-state and no-news indicator handling. |
| `src/event_state_forecasting/features/text_normalization.py` | Future article text normalization and hashing preparation. |
| `src/event_state_forecasting/split/leakage_checks.py` | Future assertions for timestamp, horizon, row, label, and fold leakage. |
| `src/event_state_forecasting/split/lockbox.py` | Future final untouched lockbox boundary definition. |
| `src/event_state_forecasting/split/purged_embargo.py` | Future purged-plus-embargoed walk-forward fold construction. |
| `src/event_state_forecasting/models/comparator_ladder.py` | Future approved comparator roster and run ordering. |
| `src/event_state_forecasting/models/gated_fusion.py` | Future simple gated fusion model home. |
| `src/event_state_forecasting/models/inference.py` | Future saved-prediction creation interface. |
| `src/event_state_forecasting/models/market_baselines.py` | Future market-only baseline family home. |
| `src/event_state_forecasting/models/training.py` | Future training orchestration primitives, not benchmark interpretation. |
| `src/event_state_forecasting/evaluation/comparison_summary.py` | Future comparison summary generation from saved predictions and metrics. |
| `src/event_state_forecasting/evaluation/ranking.py` | Future mandatory secondary ranking diagnostics. |
| `src/event_state_forecasting/evaluation/regression.py` | Future primary regression metrics. |
| `src/event_state_forecasting/evaluation/statistical_tests.py` | Future paired forecast-comparison tests after saved predictions exist. |
| `src/event_state_forecasting/benchmark/artifact_packet.py` | Future serious-run artifact packet definition and validation. |
| `src/event_state_forecasting/benchmark/registry.py` | Future benchmark-family and run identity registry. |
| `src/event_state_forecasting/benchmark/runner.py` | Future approved benchmark orchestration. |
| `src/event_state_forecasting/ops/data_refresh.py` | Future refresh rules and benchmark invalidation hooks. |
| `src/event_state_forecasting/ops/ledger_sanitization.py` | Future provider-ledger credential sanitization logic. |
| `src/event_state_forecasting/ops/rollback.py` | Future manifest-backed rollback policy. |
| `src/event_state_forecasting/ops/truncation_refinement.py` | Future Alpha Vantage window subdivision or limitation workflow. |
| `src/event_state_forecasting/utils/hashing.py` | Future stable hashing support for text, artifacts, configs, and manifests. |
| `src/event_state_forecasting/utils/logging.py` | Future logging conventions without hiding evidence in logs only. |
| `src/event_state_forecasting/utils/paths.py` | Future canonical path resolution. |
| `src/event_state_forecasting/utils/reproducibility.py` | Future run metadata and deterministic seed documentation. |
| `src/event_state_forecasting/utils/time.py` | Future market-calendar and timestamp utility home. |
| `src/event_state_forecasting/utils/validation.py` | Future generic validation result structures and helpers. |

## 16. Required Blind-Spot Language

Add relevant blind-spot comments to each file. Use the exact issue where applicable.

| Risk Area | Required Comment Focus |
| --- | --- |
| Alpha Vantage truncation | 92 likely truncated top-50 windows remain unresolved until refinement or explicit limitation acceptance. |
| Raw file coverage | 850/850 canonical files is raw coverage, not benchmark readiness. |
| API keys | Raw request ledgers may contain API-key-bearing URLs and must not be committed or shared as-is. |
| No-news rows | No-news days must stay in the row universe with explicit empty event states and indicators. |
| Same-day alignment | After-hours and non-trading-day news must roll forward, not leak backward. |
| Overlapping horizons | Approved horizons require purge and embargo discipline. |
| Universe drift | Top-100 and top-500 expansions are separate benchmark families by default. |
| Static metadata | SEC/company support is not phase-1 static-feature modeling unless later approved. |
| Archive reuse | Deprecated code is reference-only until reintroduced through active docs. |
| Metric shopping | Single split, single metric, or single horizon cannot support serious claims. |
| Lockbox integrity | Final lockbox must not be used for iterative development. |
| Survivorship | Current top-50 historical use may require survivorship-bias acknowledgement unless historical membership is reconstructed. |
| Provider reality | Provider behavior, limits, and coverage require manual validation before serious claims. |

## 17. Generation Workflow

When executing this prompt, follow this workflow.

1. Reconstruct context from the required files.
2. Confirm there is no active `src/`, `configs/`, or `tests/` conflict that would require overwrite or merge.
3. If conflicting files exist, stop and ask before modifying them.
4. Prepare the folder and file list from this prompt.
5. Generate comment-only file contents using the templates above.
6. Validate generated contents in memory before writing.
7. Write files only when every generated file passes comment-only validation.
8. Update `Complete_guidebook.txt` for every created file or grouped responsibility.
9. Update `Architecture_Map.md`, `docs/Implementation_Decisions.md`, `docs/Execution_Plan.md`, `docs/Unit_Testing.md`, `docs/db_Testing.md`, `docs/Benchmark_Testing.md`, and `docs/Pipeline_Testing.md` as needed to record the new scaffold status.
10. Update `README.md` only if onboarding current-state text changes.
11. Run `python scripts/validate_agent_governance.py`.
12. Run a scaffold validation check that verifies generated Python and YAML files are comment-only.
13. Update `docs/agent/agent_log/Current_State.md` and append `docs/agent/agent_log/Event_Ledger.ndjson` events according to `AgentMemory.md`.
14. Report created files, validation results, and remaining blockers.

## 18. Comment-Only Validation Rule

Before and after writing, inspect every generated `.py` and `.yaml` file.

For `.py`, fail if any nonblank line does not start with `#`.

For `.yaml`, fail if any nonblank line does not start with `#`.

For all generated files, fail if the content includes any of these as active syntax rather than comment text:

| Forbidden Pattern | Reason |
| --- | --- |
| `def ` | Would define executable function. |
| `class ` | Would define executable class. |
| `import ` | Would activate dependency behavior. |
| `from ` | Would activate dependency behavior. |
| `=` outside comments | Would create executable assignment or config value. |
| `pass` outside comments | Would create executable stub. |
| Triple quotes | Would create docstrings or string literals. |
| YAML keys outside comments | Would create active config. |

## 19. Documentation Update Requirements

After generating the scaffold, update active docs without changing approved scope.

Required updates:

| File | Required Update |
| --- | --- |
| `Complete_guidebook.txt` | Add the new folder groups and file responsibilities. |
| `Architecture_Map.md` | Change missing-layer status to comment-only scaffold exists, if created. |
| `docs/Implementation_Decisions.md` | Record that scaffold files are comment-only and not active implementation. |
| `docs/Execution_Plan.md` | Update Stage 0 or create a design-scaffold substage, but do not mark implementation stages complete. |
| `docs/Unit_Testing.md` | Record comment-only planned tests exist, not executable tests. |
| `docs/db_Testing.md` | Record planned data-validation scaffold exists, not implemented checks. |
| `docs/Benchmark_Testing.md` | Record benchmark scaffold exists, not a benchmark runner or benchmark result. |
| `docs/Pipeline_Testing.md` | Record scaffold status and keep pipeline not implemented. |
| `README.md` | Mention active `src/`, `configs/`, and `tests/` are comment-only scaffolds if created. |
| `docs/agent/agent_log/Current_State.md` | Add or update task status and evidence pointers. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Append request, task, artifact, evidence, drift, and reconciliation events. |

## 20. Completion Criteria

The scaffold task can be marked done only if all of these are true.

| Criterion | Required Evidence |
| --- | --- |
| Folder tree created | Paths exist in active root. |
| Files are comment-only | Validation check proves no active code/config was created. |
| No overwrite conflict | Existing user files were not silently modified or replaced. |
| File map updated | `Complete_guidebook.txt` reflects new responsibilities. |
| Design docs aligned | Architecture and implementation docs describe scaffold status accurately. |
| Validation docs aligned | Testing docs distinguish planned tests from executable tests. |
| Governance validator passes | `python scripts/validate_agent_governance.py` reports pass. |
| Operational memory updated | `Current_State.md` and `Event_Ledger.ndjson` contain evidence-backed events. |
| No benchmark claim made | Final response explicitly says no benchmark pipeline or result exists yet. |

## 21. Final Response Requirements

When finished, report:

1. Files and folders created.
2. Docs updated.
3. Validation commands run and results.
4. Confirmation that generated scaffold files are comment-only.
5. Explicit statement that no executable pipeline, dataset builder, model, test suite, or benchmark result was created.
6. Remaining blockers before real implementation.

## 22. Final Safety Rule

If you are unsure whether creating a file would imply unapproved implementation, do not create that file. Ask the user or create a narrower comment-only placeholder that clearly says it is not implemented.

If a lower-layer convenience conflicts with `ScopeDecisionLog.md`, `ResearchTruth.md`, or `ProjectDefinition.md`, the higher-authority document wins.
