# Stage1Prompt

Status: execution prompt for Stage 1, Raw Data Security And Coverage Audit. This stage may create audit code or tests only after preserving contracts and documenting test expectations. It does not create a benchmark dataset or result.

## Mission

Make raw provider state safe, parseable, coverage-auditable, truncation-aware, and ready for clean-window and dataset-contract work.

## Ownership

| Area | Owner |
| --- | --- |
| Raw data audit execution | Agent. |
| Credential handling decisions | User approval if destructive, key rotation, or file relocation is needed. |
| Provider boundary | `ScopeDecisionLog.md` DQ-008. |
| Raw data validation contract | `docs/db_Testing.md`, `docs/Data_Update_Strategy.md`. |
| Security evidence | Agent must record safe handling and unresolved risks. |

## Required Context To Read First

| File | Why |
| --- | --- |
| `AgentRules.md` | Safety, evidence, approval gates. |
| `ScopeDecisionLog.md` | Provider stack and universe decisions. |
| `ResearchTruth.md` | Current raw coverage and truncation truth. |
| `ProjectDefinition.md` | Raw-data role and non-claims. |
| `docs/db_Testing.md` | Required raw and dataset checks. |
| `docs/Data_Update_Strategy.md` | Refresh, rollback, and ledger policy. |
| `docs/Data_Separation_And_Overfitting_Control.md` | Stage dependency and downstream row contract. |
| `docs/Detailed_Execution_Stages.md` | Stage 1 detailed requirements. |

## Inputs

| Input | Required handling |
| --- | --- |
| `data/raw/universe/top50_slickcharts_2026-04-10.csv` | Treat as frozen top-50 seed. |
| `data/raw/alphavantage/` | Audit canonical raw news files, summaries, ledgers, and truncation evidence. |
| `data/manifests/alphavantage_top50_raw_merge_2026-05-06.json` | Use as current top-50 raw merge evidence. |
| Raw ledgers and logs | Treat as sensitive until sanitized. |
| Twelve Data OHLCV evidence | Verify if present; otherwise record blocker. |
| SEC support evidence | Verify if needed; otherwise record status. |

## Outputs

| Output | Required contents |
| --- | --- |
| Raw audit report | Coverage, parse status, truncation, empty feeds, duplicates, credential risk, provider limitations. |
| Machine-readable manifest | Counts by ticker/year/source and validation status. |
| Credential-risk report | Files containing provider keys or unsafe URLs and recommended handling. |
| Clean-window input summary | Provider overlap and limitations relevant to Stage 2. |
| Updated memory | Stage status, evidence, blockers, drift checkpoint. |

## Execution Steps

| Step | Action | Output |
| --- | --- | --- |
| 1 | Recover protected universe and provider decisions. | Constraint summary. |
| 2 | Inventory top-50 universe rows and canonical tickers. | Universe validation summary. |
| 3 | Inventory Alpha Vantage canonical expected windows. | Expected file list. |
| 4 | Compare expected windows with actual raw files. | Missing/extra/duplicate report. |
| 5 | Parse canonical JSON payloads. | Parse report. |
| 6 | Count feed rows by ticker and year. | Feed-row table. |
| 7 | Flag likely truncated windows. | Truncation list. |
| 8 | Flag empty-feed windows. | Empty-feed list. |
| 9 | Detect non-canonical files and content conflicts. | Conflict report. |
| 10 | Scan ledgers/logs for API-key-bearing URLs. | Credential-risk report. |
| 11 | Verify Twelve Data OHLCV state or record absence. | OHLCV status. |
| 12 | Verify SEC support state or record absence. | SEC status. |
| 13 | Write audit artifacts and update docs/memory. | Evidence packet. |

## Testing Strategy

| Test | Command or method | Required result |
| --- | --- | --- |
| Universe test | Future executable universe validation. | Top-50 count and canonical tickers match expected. |
| Raw coverage test | Future raw-validation command. | Expected windows accounted for. |
| JSON parse test | Parse every canonical payload. | No parse failures or explicit blockers. |
| Truncation test | Identify provider-limit windows. | Truncation not hidden. |
| Empty-feed test | Identify valid empty responses. | Empty feeds remain explicit. |
| Credential scan | Search ledgers/logs for keys and request URLs. | No unsafe artifact is treated as shareable. |
| Governance validation | `python scripts/validate_agent_governance.py` | `VALIDATION PASSED`. |

## Completion Criteria

| Criterion | Must be true |
| --- | --- |
| Raw status known | Coverage, parse, empty, truncation, duplicate, and credential statuses documented. |
| Sensitive files handled | API-key-bearing artifacts sanitized, isolated, or recorded as blockers. |
| Provider gaps visible | Missing OHLCV/SEC evidence or truncation remains explicit. |
| Stage 2 can proceed | Dataset contract work has trusted raw-state inputs. |
| Memory updated | Evidence and unresolved blockers recorded. |

## Stop Conditions

Stop and ask the user before deleting raw data, overwriting raw data, rotating keys, committing/sharing ledgers, changing providers, changing universe, or accepting truncation limitations as scientifically sufficient.

## Final Response Requirements

Report raw coverage, parse status, truncation count, empty-feed count, credential-risk status, generated artifacts, validation results, and remaining blockers.
