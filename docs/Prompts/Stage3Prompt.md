# Stage3Prompt

Status: execution prompt for Stage 3, Feature And Label Pipeline. This stage creates as-of-safe feature and label artifacts only after dataset contracts and tests are ready.

## Mission

Build market features, aligned event-state features, explicit no-news states, and forward excess-return labels for all approved horizons without look-ahead leakage or row drift.

## Ownership

| Area | Owner |
| --- | --- |
| Feature implementation | Agent after tests/contracts. |
| Label implementation | Agent after tests/contracts. |
| Alignment policy | `ScopeDecisionLog.md` DQ-005. |
| Target and horizons | `ScopeDecisionLog.md` DQ-003 and DQ-004. |
| Row equality | `docs/Data_Separation_And_Overfitting_Control.md`. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `ProjectDefinition.md` | Feature, event-state, target, and evaluation definitions. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Feature timestamp and label-window requirements. |
| `docs/db_Testing.md` | Dataset row identity obligations. |
| `docs/Pipeline_Testing.md` | Stage gate order. |
| `configs/features.example.yaml` | Feature config scaffold. |
| `configs/labels.example.yaml` | Label config scaffold. |
| `docs/Detailed_Execution_Stages.md` | Stage 3 detailed requirements. |

## Inputs

| Input | Required handling |
| --- | --- |
| Stage 2 dataset artifact | Must be versioned and manifest-backed. |
| Market OHLCV data | Use only information available as of prediction timestamp. |
| Alpha Vantage news data | Align by same-day as-of-close and roll-forward rules. |
| Approved horizon set | Generate all approved horizons or explicit blockers. |
| No-news rows | Preserve and encode, never drop silently. |

## Outputs

| Output | Required contents |
| --- | --- |
| Market feature artifact | Row keys, feature availability timestamp, feature manifest. |
| Event-state feature artifact | Row keys, aligned article references, embedding/scalar metadata, no-news indicators. |
| Label artifact | Row keys, horizon, label window start/end, forward excess-return target. |
| Feature/label manifests | Version, inputs, coverage, exclusions, limitations. |
| Executable tests | Market, alignment, event-state, no-news, label tests. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Confirm Stage 2 dataset artifact and tests exist. | Dependency status. |
| 2 | Define market feature contract and as-of timestamp policy. | Market feature contract. |
| 3 | Define news alignment function behavior. | Alignment contract. |
| 4 | Define event-state representation and scalar enrichments in scope. | Event-state contract. |
| 5 | Define no-news state and indicator fields. | No-news contract. |
| 6 | Define label formulas and market benchmark for excess returns. | Label contract. |
| 7 | Write executable feature and label tests. | Test files. |
| 8 | Implement feature and label builders if tests/contracts are ready. | Source modules and CLI. |
| 9 | Produce artifacts and manifests. | Feature and label outputs. |
| 10 | Validate row equality and leakage preconditions. | Validation report. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Market feature tests | Future `tests/features/test_market_features_contract.py`. | No future OHLCV leakage. |
| News alignment tests | Future `tests/features/test_news_alignment_contract.py`. | Same-day, after-hours, and non-trading-day behavior correct. |
| Event-state tests | Future `tests/features/test_event_state_contract.py`. | Event-state features align to row universe. |
| No-news tests | Future `tests/features/test_no_news_state_contract.py`. | No-news rows retained and encoded. |
| Label tests | Future `tests/features/test_labels_contract.py`. | All approved horizon labels correct. |
| Row equality check | Future row digest validation. | Market/event-state/labels share required rows. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| As-of safe | Feature timestamps prove prediction-time availability. |
| Labels valid | Label windows and horizons recorded. |
| No-news preserved | No-news rows explicitly encoded. |
| Tests pass | Feature and label tests pass. |
| Stage 4 ready | Split builder can consume row identity and label windows. |

## Stop Conditions

Stop and ask before changing alignment, target family, horizon set, event representation, no-news policy, or using future information to simplify features.

## Final Response Requirements

Report feature/label artifacts, row counts, test outputs, known limitations, and readiness for Stage 4.
