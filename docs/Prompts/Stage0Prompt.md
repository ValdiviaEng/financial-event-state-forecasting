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
