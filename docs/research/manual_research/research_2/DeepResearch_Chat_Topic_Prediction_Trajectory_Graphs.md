# DeepResearch Chat Topic: Prediction Trajectory Graphs

Status: proposed deep-research chat prompt only. Do not execute repository code, create charts, alter target definitions, or approve implementation.

## Required Background Files To Read First

| File | Why |
| --- | --- |
| `ResearchTruth.md` | Current target, horizons, Stage 6 result, and Stage 10C packet facts. |
| `ScopeDecisionLog.md` | Stage 10B trajectory decision and Stage 10C approval boundary. |
| `UsageManual.md` | Current Stage 10C artifact root, command usage, inputs, and outputs. |
| `Stage10APrompt.md` | Research basis for trajectory displays. |
| `Stage10BPrompt.md` | Trajectory decision question and selected option. |
| `Stage10CPrompt.md` | Implemented trajectory/report constraints. |
| Current Stage 10C packet under `data/prediction_outputs/phase1_top50/...` | Existing trajectory marker artifacts to treat as baseline evidence. |

## Repository Context

The current target is forward excess return at horizons `1d`, `5d`, `10d`, `20d`, and `60d`. Stage 10C now emits local trajectory marker data and a static report based on existing Stage 5 saved predictions. The display must separate observed market history, historical model outputs, realized labels where available, and any future forecast markers if separately approved later.

## Research Ask

Research chart refinements for displaying recent market behavior and multi-horizon model outputs without implying precise future prices, buy/sell targets, or trading profitability. Treat the current Stage 10C trajectory marker output as the baseline; do not assume true future forecast rows exist.

## Questions

| Question | Desired answer |
| --- | --- |
| Axes and quantities | Should the graph show price, excess return, predicted excess return, ranks, or normalized scores? |
| Last-month context | How should recent realized returns and prior predictions be aligned by as-of date and horizon? |
| Future markers | How should future forecast points be placed when realized labels are unknown? |
| Multi-horizon design | What visual encoding avoids confusion across five horizons? |
| Caveats | How should clean-null Stage 6 evidence and limitation-bearing comparability be communicated? |
| Current artifact fit | Which refinements use current Stage 10C marker tables, and which require approved schema or inference changes? |
| Validation | What checks ensure dates, horizons, and values line up with artifact rows? |

## Desired Output

Return cited visualization alternatives, recommended graph refinements, data schema implications, caveat wording, and tests that prevent horizon/date misalignment. Do not recommend projected price paths or fan charts from excess-return markers as current-scope implementation.
