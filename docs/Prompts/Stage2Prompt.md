# Stage2Prompt

Status: execution prompt for Stage 2, Dataset Contract Definition. This stage defines and may implement dataset contracts only after tests are explicit. It does not train models or produce benchmark results.

## Mission

Define and validate the canonical benchmark dataset artifact, clean-window decision record, row identity, dataset manifest, row-universe equality, and Option B split-eligibility fields.

## Ownership

| Area | Owner |
| --- | --- |
| Dataset contract design | Agent. |
| Clean-window approval if ambiguous | User. |
| Dataset implementation | Agent only after executable tests or documented pending-test reasons. |
| Scope authority | `ScopeDecisionLog.md`. |
| Row separation authority | `docs/Data_Separation_And_Overfitting_Control.md`. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `ProjectDefinition.md` | Dataset and row identity definition. |
| `ResearchTruth.md` | Current raw data and unknowns. |
| `docs/db_Testing.md` | Dataset validation requirements. |
| `docs/Pipeline_Testing.md` | Pipeline gate order. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Row identity, split role, lockbox, preprocessing artifact needs. |
| `configs/data_contracts.example.yaml` | Planned row and artifact schema sections. |
| `configs/phase1_top50_benchmark.yaml` | Future benchmark-family config scaffold. |
| `docs/Detailed_Execution_Stages.md` | Stage 2 detailed requirements. |

## Inputs

| Input | Required handling |
| --- | --- |
| Stage 1 raw audit artifacts | Treat as prerequisite evidence. |
| Top-50 universe | Frozen first benchmark seed. |
| OHLCV and news coverage summaries | Use for clean-window feasibility. |
| Approved horizons | Preserve exact `1d`, `5d`, `10d`, `20d`, `60d`. |
| Option B contract | Include row identity and split-role fields from the start. |

## Outputs

| Output | Required contents |
| --- | --- |
| Dataset schema | Row key, ticker, as-of date, horizon, feature timestamp, label windows, split fields. |
| Dataset versioning policy | Stable identity, hashes, source manifest references. |
| Dataset manifest schema | Sources, coverage, clean window, exclusions, limitations, row counts. |
| Clean-window decision record | Candidate windows, reasons, validation status, limitations. |
| Executable dataset tests | Schema, row equality, no-news, manifest, split-role checks. |
| Dataset artifact if implemented | Versioned materialized table plus manifest. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Confirm Stage 1 completed or record blocker. | Dependency status. |
| 2 | Define canonical dataset storage and naming. | Storage contract. |
| 3 | Define row identity fields and uniqueness policy. | Row contract. |
| 4 | Define clean-window selection criteria. | Clean-window method. |
| 5 | Evaluate clean-window candidates using OHLCV/news/label/split feasibility. | Candidate table. |
| 6 | Define no-news row preservation and availability indicators. | No-news contract. |
| 7 | Define branch row equality for market-only and event-state views. | Row equality contract. |
| 8 | Define manifest schema and invalidation fields. | Manifest contract. |
| 9 | Write executable tests before implementation completion. | Test files. |
| 10 | Implement dataset builder only if tests/contracts are ready. | Dataset modules and CLI. |
| 11 | Validate dataset artifact and update memory. | Test outputs and evidence. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Contract tests | Future `tests/data/test_contracts_contract.py`. | Missing required fields fail as blockers. |
| Universe tests | Future `tests/data/test_universe_contract.py`. | Top-50 parsing deterministic. |
| Panel tests | Future `tests/dataset/test_panel_builder_contract.py`. | No-news rows retained; branch rows equal. |
| Row-universe tests | Future `tests/dataset/test_row_universe_contract.py`. | Missing, extra, duplicate, or asymmetric rows fail. |
| Manifest tests | Future manifest checks. | Source, version, coverage, limitations present. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Clean window resolved | Window is selected or blocker is explicit. |
| Dataset schema complete | Required Option B row fields included. |
| Tests executable | Dataset tests run and pass for implemented behavior. |
| Dataset manifest complete | Version, sources, coverage, exclusions, limitations recorded. |
| No benchmark claim | Dataset creation is not model skill evidence. |

## Stop Conditions

Stop and ask before changing clean-window doctrine, dropping no-news rows, removing horizons, changing universe, ignoring truncation risk, or changing provider assumptions.

## Final Response Requirements

Report dataset schema decisions, clean-window status, test results, artifact paths, row counts if built, and blockers for Stage 3.
