# Final Data Layer

This directory stores model-ready datasets.

## Canonical tables expected here

- `event_states_daily`
- `labels_multi_horizon`
- `modeling_panel`

## Rules

- each dataset version should have a manifest,
- row-level uniqueness must be validated where declared,
- final tables should be easy to subset for ablations,
- final tables should be built only from validated upstream raw and interim inputs.

## Current implementation note

The Stage 10 modeling-dataset builder now writes:
- `modeling_panel__<dataset_version>.parquet`

The final panel currently assembles:
- adjusted prices,
- market features,
- multi-horizon labels,
- optional event states,
- optional company features,
- debugging/version metadata such as:
  - `split_adjusted_prices_used`
  - `market_feature_version`
  - `label_version`
  - `event_state_version`
  - `company_feature_version`

The panel is validated to remain unique on `(ticker, date)`.
