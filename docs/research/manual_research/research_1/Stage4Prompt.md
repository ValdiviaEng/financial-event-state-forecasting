# Stage4Prompt

Status: execution prompt for Stage 4, Split And Benchmark Runner. This stage implements leakage-controlled split and artifact orchestration gates before model work.

## Mission

Build purged-plus-embargoed walk-forward folds, reserve the final untouched lockbox, enforce contamination blockers, define saved-prediction and artifact-packet requirements, and prepare benchmark runner infrastructure.

## Ownership

| Area | Owner |
| --- | --- |
| Split construction | Agent after tests/contracts. |
| Lockbox policy | `ScopeDecisionLog.md` DQ-012 and `docs/Data_Separation_And_Overfitting_Control.md`. |
| Benchmark runner | Agent after split/artifact tests exist. |
| Artifact packet | `ScopeDecisionLog.md` DQ-023 and `docs/Benchmark_Testing.md`. |
| Approval for protocol changes | User. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `docs/Data_Separation_And_Overfitting_Control.md` | Purge, embargo, lockbox, preprocessing, prediction blockers. |
| `docs/Benchmark_Testing.md` | Required packet and comparability rules. |
| `docs/Pipeline_Testing.md` | Gate order. |
| `configs/splits.example.yaml` | Split config scaffold. |
| `configs/artifact_packet.example.yaml` | Artifact packet scaffold. |
| Stage 3 artifacts | Feature and label inputs. |
| `docs/Detailed_Execution_Stages.md` | Stage 4 detailed requirements. |

## Inputs

| Input | Required handling |
| --- | --- |
| Stage 3 feature/label artifacts | Must include row keys, feature timestamps, label windows. |
| Dataset version | Must be stable and manifest-backed. |
| Clean-window bounds | Must be frozen before serious split construction. |
| Approved horizons | Use maximum horizon to inform purge/embargo unless precise policy approved. |
| Option B contract | All contamination blockers apply. |

## Outputs

| Output | Required contents |
| --- | --- |
| Split manifest | Fold ID, train span, validation span, purge span, embargo span, lockbox boundary, row counts, excluded reasons. |
| Lockbox record | Boundary, membership, access policy, reporting-only status. |
| Leakage validation report | Pass/block status for contamination rules. |
| Artifact packet validator | Required member checks. |
| Benchmark runner | Orchestration only; no hidden training or claims. |
| Executable tests | Split, leakage, artifact-packet, benchmark-runner, integration tests. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Confirm Stage 3 artifacts exist and pass tests. | Dependency status. |
| 2 | Define fold schedule and chronological windows. | Fold plan. |
| 3 | Implement purge logic for overlapping label windows. | Purge report. |
| 4 | Implement embargo policy. | Embargo report. |
| 5 | Reserve lockbox and enforce forbidden-use policy. | Lockbox manifest. |
| 6 | Validate split-role exclusivity. | Split validation. |
| 7 | Implement leakage checks and fail-closed blockers. | Leakage report. |
| 8 | Define preprocessing-fit manifest requirement for Stage 5. | Preprocessing contract hook. |
| 9 | Define saved-prediction schema for Stage 5. | Prediction contract hook. |
| 10 | Implement artifact packet validation. | Packet validator and tests. |
| 11 | Implement benchmark runner only if it cannot bypass gates. | Runner and tests. |
| 12 | Update memory and docs. | Evidence record. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Purge/embargo tests | `tests/split/test_purged_embargo_contract.py`. | Overlapping labels and embargo rows excluded. |
| Leakage tests | `tests/split/test_leakage_contract.py`. | Train/validation/lockbox contamination fails closed. |
| Artifact packet tests | `tests/benchmark/test_artifact_packet_contract.py`. | Missing required members fail. |
| Benchmark runner tests | `tests/benchmark/test_benchmark_runner_contract.py`. | Runner rejects scope or artifact drift. |
| Pipeline integration tests | Future `tests/integration/test_pipeline_contract.py`. | Gate order enforced. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Split manifest valid | Purge, embargo, lockbox, row counts, exclusions recorded. |
| Leakage checks pass | No contamination blocker remains. |
| Artifact packet gate active | Serious claims require full packet. |
| Runner gate-safe | Cannot train, score, or report outside approved artifacts. |
| Stage 5 ready | Models can consume folds and produce saved predictions. |

## Stop Conditions

Stop and ask before changing evaluation protocol, shortening purge/embargo without documented basis, using lockbox for development, or allowing random time-shuffled serious evaluation.

## Final Response Requirements

Report split manifest status, lockbox boundary, leakage checks, artifact packet tests, runner status, and blockers for Stage 5.
