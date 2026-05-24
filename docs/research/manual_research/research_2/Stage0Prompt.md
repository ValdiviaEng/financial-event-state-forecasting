# Stage0BPrompt

Status: execution prompt for Stage 0B, Data Separation And Overfitting Contract. This prompt formalizes the approved Option B validation refinement and does not authorize benchmark-family changes.

## Mission

Create or maintain the active Option B contract requiring strict data separation, train-fold-only preprocessing, predeclared metrics, saved out-of-sample predictions, contamination blockers, and overfitting diagnostics.

## Ownership

| Area | Owner |
| --- | --- |
| Option B contract drafting | Agent. |
| Approval for Option B or any protocol change | User. |
| Evaluation doctrine | `ScopeDecisionLog.md` DQ-012. |
| Metric hierarchy | `ScopeDecisionLog.md` DQ-013. |
| Evidence bar | `ScopeDecisionLog.md` DQ-018 and DQ-023. |
| Clean-window boundary | `ScopeDecisionLog.md` DQ-021. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `ScopeDecisionLog.md` | Confirm DQ-012 remains purged/embargoed walk-forward plus lockbox. |
| `ResearchTruth.md` | Confirm active truth and current non-implementation status. |
| `ProjectDefinition.md` | Confirm broad project boundaries. |
| `docs/Benchmark_Testing.md` | Benchmark artifact and comparability rules. |
| `docs/db_Testing.md` | Dataset and row identity obligations. |
| `docs/Pipeline_Testing.md` | Fail-closed gate order. |
| `docs/Execution_Plan.md` | Stage dependency position. |
| `docs/Detailed_Execution_Stages.md` | Granular Stage 0B requirements. |

## Protected Non-Changes

Option B must not change target family, horizons, provider stack, top-50 universe, news alignment, no-news policy, comparator ladder, evaluation doctrine, final lockbox doctrine, or benchmark comparability rules.

## Inputs

| Input | Required handling |
| --- | --- |
| User approval for Option B | Record in memory and scope/truth docs. |
| Existing validation docs | Update, do not contradict. |
| Comment-only scaffolds | Update comments only. |
| Guidebook and README | Add discoverability references. |

## Outputs

| Output | Required contents |
| --- | --- |
| `docs/Data_Separation_And_Overfitting_Control.md` | Data separation, purge/embargo, lockbox, preprocessing, metrics, diagnostics, blockers, artifacts. |
| Updated scope/truth/project docs | Option B refinement recorded without scope drift. |
| Updated validation docs | Tests and gates reflect Option B. |
| Updated scaffolds | Config/source/test comments mention relevant contracts. |
| Updated memory | Approval, task, evidence, drift, completion. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Confirm approval and protected boundaries. | Approval evidence. |
| 2 | Draft or update central contract. | Contract document. |
| 3 | Define stable row identity and split-role exclusivity. | Dataset contract section. |
| 4 | Define purge/embargo and lockbox rules. | Split and lockbox sections. |
| 5 | Define fold-local preprocessing. | Preprocessing contract. |
| 6 | Define predeclared metrics and saved-prediction schema. | Metric and prediction sections. |
| 7 | Define overfitting diagnostics and search-space summary. | Diagnostic contract. |
| 8 | Define contamination blockers and required artifacts. | Fail-closed list. |
| 9 | Propagate references through docs and scaffolds. | Consistent active docs. |
| 10 | Validate and update memory. | Evidence outputs. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Comment-only validation | Scan scaffolds after comment updates. | `COMMENT_ONLY_VALIDATION PASSED`. |
| Option B consistency search | Search active docs for Option B contract references. | Contract appears where needed. |
| Scope drift check | Compare protected scope values before and after edits. | No protected value changed. |
| Guidebook coverage | Count docs/config sections and prompt references. | Guidebook updated. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Central contract exists | `docs/Data_Separation_And_Overfitting_Control.md` present and complete. |
| Docs propagated | Scope, truth, project, testing, pipeline, operations, README, guidebook updated. |
| Scaffold comments updated | Relevant config/source/test comments reflect Option B. |
| Validation passed | Governance, comment-only, and consistency checks pass. |
| Memory updated | Approval, task completion, and reconciliation logged. |

## Stop Conditions

Stop and ask the user if Option B expands into nested CV, CPCV/PBO as a required protocol, lockbox redesign, target changes, horizon changes, provider changes, universe changes, or comparator-ladder changes.

## Final Response Requirements

Report the central contract path, propagation areas, validation results, and remaining executable-test blockers.


# Stage0APrompt

Status: execution prompt for Stage 0A, Comment-Only Structural Scaffold. This prompt is for scaffold creation or audit only. It does not authorize runnable implementation.

## Mission

Create or verify the active-root `src/`, `configs/`, and `tests/` scaffold as comment-only documentation of future responsibilities.

## Ownership

| Area | Owner |
| --- | --- |
| Scaffold creation | Agent. |
| Runtime implementation approval | User. |
| Folder map authority | `StructuralFolderMapPrompt.md`, if present and current. |
| Scope authority | `ScopeDecisionLog.md` and `ResearchTruth.md`. |
| Scaffold status communication | README, guidebook, architecture, implementation, validation docs. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Editing and evidence rules. |
| `ProjectDefinition.md` | Approved architecture and phase boundary. |
| `ScopeDecisionLog.md` | Protected benchmark values. |
| `ResearchTruth.md` | Active truth and current repo reality. |
| `StructuralFolderMapPrompt.md` | Scaffold shape and comment rules. |
| `docs/Architecture_Map.md` | Intended package layers. |
| `docs/Implementation_Decisions.md` | Comment-only scaffold decision. |
| `docs/Detailed_Execution_Stages.md` | Stage 0A requirements. |

## Hard Rule

Every generated `.py` and `.yaml` file must contain only comments or blank lines. No imports, assignments, function definitions, classes, active YAML keys, fixtures, assertions, or executable test bodies are allowed.

## Inputs

| Input | Required handling |
| --- | --- |
| Existing root tree | Verify paths before writing; do not overwrite active implementation. |
| Scaffold prompt | Use as shape reference. |
| Active scope docs | Preserve approved target, horizons, providers, universe, alignment, evaluation. |
| Deprecated snapshot | Reference-only; never copy active claims blindly. |

## Outputs

| Output | Required contents |
| --- | --- |
| `src/event_state_forecasting/` | Comment-only package scaffold with future modules. |
| `configs/` | Comment-only YAML scaffolds with planned sections only. |
| `tests/` | Comment-only planned tests with target modules and expected behaviors. |
| Updated docs | Architecture, implementation, validation, guidebook, README, memory. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Read context and confirm Stage 0 docs exist. | Read evidence. |
| 2 | Check whether `src/`, `configs/`, or `tests/` already exist. | Conflict report. |
| 3 | If no conflict, create scaffold files using comment-only templates. | Scaffold tree. |
| 4 | For each file, include file path, status, layer, governing docs, purpose, scope, inputs, outputs, planned dependencies, planned functions or sections, tests, limitations. | Comment blocks. |
| 5 | Validate every `.py` and `.yaml` file is comments only. | `COMMENT_ONLY_VALIDATION PASSED`. |
| 6 | Update docs and guidebook to record scaffold status and counts. | Discoverability updates. |
| 7 | Update memory and ledger. | Task completion evidence. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Comment-only validation | Scan `src/**/*.py`, `tests/**/*.py`, `configs/**/*.yaml` for non-comment lines. | No non-comment lines. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Coverage check | Count source, config, and test scaffold files and compare guidebook. | Counts match. |
| Import avoidance check | Search scaffold files for `import`, `def`, `class`, `assert`, YAML keys. | No executable constructs. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Scaffold exists | Expected folders and files exist. |
| Scaffold is inert | Files are comments only. |
| Docs are accurate | README and guidebook say scaffold is not implementation. |
| Validation passed | Governance and comment-only checks pass. |
| Memory updated | Events and task status recorded. |

## Stop Conditions

Stop and ask the user if an active implementation already exists in a target path, if a scaffold would overwrite user files, or if the user asks for executable behavior during Stage 0A.

## Final Response Requirements

Report scaffold counts, validation results, changed files, and remaining implementation blockers.



# Stage0Prompt

Status: execution prompt for Stage 0, Active Documentation Repair. This prompt is documentation-first and does not authorize code, active config values, executable tests, datasets, models, or benchmark claims by itself.

## Mission

Repair and maintain the active-root theory, design, validation, operations, onboarding, guidebook, and operational-memory documents so later implementation work has a reliable source-of-truth base.

## Ownership

| Area | Owner |
| --- | --- |
| Execution | Agent operating under `AgentRules.md`. |
| Approval-gated decisions | User. |
| Scope truth | `ScopeDecisionLog.md`. |
| Research truth | `ResearchTruth.md`. |
| Broad project definition | `ProjectDefinition.md`. |
| Operational memory | `docs/agent/AgentMemory.md`, `Current_State.md`, `Event_Ledger.ndjson`. |
| Validation evidence | Agent, with command outputs preserved in memory. |

## Required Context To Read First

Read these before making changes:

| File | Why |
| --- | --- |
| `AgentRules.md` | Governance, approval gates, evidence discipline. |
| `docs/agent/AgentMemory.md` | Required task, event, drift, and reconciliation logging. |
| `docs/agent/agent_log/Current_State.md` | Current task status and blockers. |
| `docs/agent/agent_log/Event_Ledger.ndjson` | Latest event IDs and session history. |
| `ScopeDecisionLog.md` | Protected owner decisions. |
| `ResearchTruth.md` | Active truth and unresolved risks. |
| `ProjectDefinition.md` | Broad phase-1 definition. |
| `docs/Execution_Plan.md` | Stage sequence. |
| `docs/Detailed_Execution_Stages.md` | Granular stage requirements. |

## Protected Scope

Do not change target family, horizons, provider stack, universe, alignment, no-news policy, evaluation protocol, metric hierarchy, comparator ladder, or benchmark comparability without explicit approval.

## Inputs

| Input | Required handling |
| --- | --- |
| Governance docs | Treat as binding. |
| Scope/truth files | Treat as higher authority than design docs. |
| Audit reports | Use as evidence, not as implementation truth. |
| Existing active docs | Repair inconsistencies without deleting user work. |
| Repository state | Inspect before claiming files exist or are implemented. |

## Outputs

| Output | Required contents |
| --- | --- |
| Active theory docs | Scientific objective, non-goals, constraints, evidence pointers. |
| Active design docs | Architecture, implementation decisions, execution sequence. |
| Validation docs | Unit, database, benchmark, pipeline, and testing command expectations. |
| Operations docs | Data update, rollback, refresh, and invalidation rules. |
| Onboarding docs | README and guidebook references. |
| Memory updates | Task status, evidence, drift checkpoint, session reconciliation. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Recover current contract from governance, scope, truth, and memory docs. | Short working summary of constraints. |
| 2 | Inventory active root docs and identify missing or stale files. | File status map. |
| 3 | Repair stale claims about implementation, dataset readiness, provider status, and benchmark readiness. | Updated docs. |
| 4 | Add missing required active-root skeleton docs if absent. | New docs with clear status. |
| 5 | Ensure every doc distinguishes active truth, historical reference, scaffold, and implementation. | Consistent status language. |
| 6 | Update README and guidebook for discoverability. | Current onboarding map. |
| 7 | Update operational memory with task, evidence, blockers, and approvals. | Memory entries. |
| 8 | Run validation. | Command outputs. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |
| Protected-scope check | Search active docs for target, horizons, providers, universe, alignment, evaluation. | No contradictions. |
| Implementation-claim check | Search for claims that active pipeline, tests, dataset, or model exists. | Unsupported claims removed or qualified. |
| Memory check | Read `Current_State.md` and tail event ledger. | Task/evidence/drift/reconciliation present. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Required docs exist | Active theory/design/validation/operations/onboarding docs exist. |
| Scope is stable | No protected value changed without approval. |
| Claims are accurate | Comment-only scaffolds and raw coverage are not treated as implementation readiness. |
| Validation passed | Governance validator passes. |
| Memory updated | Task and ledger reflect work done. |

## Stop Conditions

Stop and ask the user if:

| Trigger | Reason |
| --- | --- |
| A protected scope value appears contradictory. | Requires approval or contradiction resolution. |
| A requested edit would reactivate archived code as active truth. | Requires explicit adoption. |
| A document implies benchmark success without evidence. | Must be corrected or clarified. |
| A user asks for implementation before contracts/tests exist. | Requires staged approval. |

## Final Response Requirements

Report changed files, validations run, current blockers, and any approvals still required. Do not claim benchmark readiness.
