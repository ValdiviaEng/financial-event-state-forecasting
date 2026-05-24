# DeepResearch Chat Topic: Top10 Multi Horizon Visualization

Status: proposed deep-research chat prompt only. Do not execute repository code, create UI artifacts, change metrics, or approve implementation.

## Required Background Files To Read First

| File | Why |
| --- | --- |
| `ResearchTruth.md` | Current Stage 6 result, Stage 10C packet facts, and non-claims. |
| `ScopeDecisionLog.md` | Stage 10B visualization decisions and Stage 10C approval boundary. |
| `UsageManual.md` | Current Stage 10C artifact root, CLI usage, inputs, and outputs. |
| `Stage10APrompt.md` | Research basis for update-to-prediction visualization. |
| `Stage10BPrompt.md` | Ranking and visualization decision questions. |
| `Stage10CPrompt.md` | Implemented packet/report requirements. |
| `data/manifests/stage10c_completion_validation_2026-05-23.json` | Current validation evidence for generated packet. |
| Current Stage 10C packet under `data/prediction_outputs/phase1_top50/...` | Existing top-10 CSV/Parquet/static-report artifacts to treat as baseline evidence. |

## Repository Context

The current repo writes Stage 5 saved predictions, Stage 6 metric/reporting artifacts, and a Stage 10C local prediction-output packet. Stage 10C now produces dated local static HTML plus CSV/Parquet outputs with top-10 views for each approved horizon: `1d`, `5d`, `10d`, `20d`, and `60d`.

The current Stage 10C prediction value is a numeric forward excess-return model output from saved historical validation/lockbox predictions. It is not a buy/sell recommendation, price target, benchmark result, or true fresh future-inference output.

## Research Ask

Research effective offline visualization refinements for displaying top-10 ranked model outputs across multiple horizons using local artifacts. Compare the current Stage 10C static HTML plus CSV/Parquet baseline against static image bundles, notebooks, and local dashboard approaches, while keeping dashboards out of current scope unless separately approved.

## Questions

| Question | Desired answer |
| --- | --- |
| View layout | What layout best supports separate per-horizon views and cross-horizon comparison? |
| Ranking | How should predicted values, ranks, model IDs, and limitations be displayed without overstating evidence? |
| Uncertainty/caveats | How should clean-null Stage 6 history and provider limitations be shown? |
| Current artifact fit | Which refinements can be represented with existing Stage 10C packet tables, and which require new approved schema fields? |
| Dependencies | Which visualization stack is suitable for a lightweight local repo? |
| Accessibility | How can outputs remain readable in static files and versioned artifacts? |
| Validation | What checks prove the visualization matches prediction artifacts exactly? |

## Desired Output

Return cited visualization patterns, recommended local output refinements, data schema implications, UI caveats, dependency tradeoffs, and tests needed to prevent stale or misleading charts. Preserve the current Stage 10C non-claims.
