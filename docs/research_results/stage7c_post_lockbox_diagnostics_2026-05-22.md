# Stage 7C Post-Lockbox Diagnostics

Status: diagnostics-only Stage 7C evidence. `benchmark_claim=false`. This report does not reinterpret Stage 6, approve all-data final-execution training-output, or create live buy/sell signals.

## Artifact

- Stage 7 root: `data/stage7_contextual_bandit/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260225__src_909564d5ebd6__rows_7a440338a923__stage3_features_labels_v1__stage4_splits_v1__stage5_models_v1__stage7_contextual_bandit_v1__post_lockbox_holdout/`
- Holdout dates: `2026-02-17` through `2026-02-25`
- Context rows: `22750` fold-specific rows
- Policy-selection rows: `180180`
- Metric rows: `4620`
- Validation: `STAGE7_COMPLETION_VALIDATION PASSED`

## Primary K=5 All-Row Diagnostics

Average top-minus-bottom spread across horizons:

| Policy | Average spread |
| --- | ---: |
| `market_only_ranker` | `0.087222` |
| `combined_supervised` | `0.086570` |
| `epsilon_greedy_0p05` | `0.082684` |
| `random_top_bottom` | `-0.000190` |

`combined_supervised` spread by horizon:

| Horizon | Top mean | Bottom mean | Spread |
| --- | ---: | ---: | ---: |
| `1d` | `-0.000308` | `-0.000588` | `0.000280` |
| `5d` | `-0.002380` | `-0.002747` | `0.000367` |
| `10d` | `0.013773` | `-0.022794` | `0.036567` |
| `20d` | `0.019661` | `-0.025254` | `0.044915` |
| `60d` | `0.322807` | `-0.027915` | `0.350722` |

## Interpretation

- Stage 7C diagnostics show useful top/bottom separation versus random, concentrated in longer horizons, especially `60d`.
- The market-only ranker is highly competitive with the combined supervised policy on this short holdout, so this is not a contextual-bandit value claim.
- The `1d` and `5d` diagnostics are near zero and should not be framed as robust short-horizon edge.
- The new post-lockbox holdout has only 7 as-of dates and repeated fold-specific lockbox predictions, so final promotion would require a larger/future holdout or explicit governance decision.
- Bottom-k outputs are downside/avoid diagnostics only, not sell or short recommendations.
