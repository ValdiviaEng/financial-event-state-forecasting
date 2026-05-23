# Raw Universe Snapshots

This directory stores frozen universe-definition files.

## Current files and roles

- `top50_slickcharts_2026-04-10.csv`: approved first serious benchmark universe seed.
- `top100_slickcharts_2026-04-10.csv`: later expansion input only; not comparable to the top-50 benchmark family by default.
- `latest_universe_snapshot.csv`, `pilot10.csv`, and `sp500_snapshot_2026-03-19.*`: historical or support snapshots retained for traceability.

## Rules

- every universe file should preserve its source and snapshot date,
- pilot subsets should be explicit rather than inferred,
- ticker normalization must preserve dot tickers such as `BRK.B` and `BF.B`,
- later universe expansions require new benchmark-family validation unless explicitly approved as comparable.

## Current implementation note

No active `src.cli.build_universe` command is currently evidenced in the active root. Treat the existing files as frozen inputs until an active universe-building CLI is recreated and documented.
