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
