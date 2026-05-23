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
