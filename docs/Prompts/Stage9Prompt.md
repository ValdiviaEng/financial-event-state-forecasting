# Stage9Prompt

Status: executed on 2026-05-22 as documentation and operational-memory reconciliation after Stage 8 plan-first raw update tooling. Stage 9 is documentation-only and does not authorize feature code, provider calls, raw-data changes, benchmark reruns, result reinterpretation, or sensitive-artifact sharing.

## Mission

Perform a documentation and operational-memory reconciliation after approved future work changes prompts, data-update scripts, update-to-prediction orchestration, visualization artifacts, or contextual-bandit documentation. Do not implement new features in Stage 9.

## Required Context To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Update propagation and DONE-evidence rules. |
| `docs/agent/AgentMemory.md` | Current-state and ledger requirements. |
| `ScopeDecisionLog.md` | Protected decisions to preserve. |
| `ResearchTruth.md` | Active truth to reconcile. |
| `ProjectDefinition.md` | Project boundary and non-goals. |
| `docs/Execution_Plan.md` | Stage status and prompt index. |
| `docs/Detailed_Execution_Stages.md` | Detailed status and prompt map. |
| `ExecutionPipeline.md` | Rebuild methodology. |
| `UsageManual.md` | Current local usage-manual wording. |
| `Complete_guidebook.txt` | File/function/config/test discoverability. |
| `README.md` | Onboarding status. |

## Scope

| In scope | Out of scope |
| --- | --- |
| Repair stale future/current wording. | Writing feature code. |
| Update prompt indexes and guidebook maps. | Running provider downloads. |
| Update usage/runbook docs after approved changes. | Changing Stage 6 result policy. |
| Update memory and event ledger. | Reinterpreting benchmark results. |
| Run documentation/governance validations. | Publishing or sharing sensitive artifacts. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Identify the approved future work that triggered Stage 9. | Trigger summary. |
| 2 | Compare active docs against current files and artifacts. | Stale wording list. |
| 3 | Patch only documentation, indexes, and memory. | Docs update. |
| 4 | Preserve non-claims and comparability caveats. | Drift checkpoint. |
| 5 | Run validation. | Evidence output. |
| 6 | Finalize memory and ledger. | Reconciliation event. |

## Validation Strategy

| Check | Required result |
| --- | --- |
| Governance | `python scripts/validate_agent_governance.py` passes. |
| Scaffold | `python scripts/validate_comment_only_scaffold.py` passes. |
| Ledger | Event ledger parses as JSONL. |
| Targeted stale search | No known stale Stage/status wording remains in active docs. |
| Tests | Run `python -m pytest "tests"` if code changed before Stage 9 or if docs claim executable behavior changed. |

## Stop Conditions

Stop and ask before changing protected scope, changing benchmark-comparability wording beyond evidenced facts, altering Stage 6 result interpretation, modifying raw data, or creating a new implementation under a documentation-only prompt.

## Final Response Requirements

If executed later, report changed docs, stale wording repaired, validations run, non-claims preserved, and remaining blockers.
