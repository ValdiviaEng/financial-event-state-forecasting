# Raw Universe Snapshots

This directory stores frozen universe-definition files.

## Expected files

- latest S&P 500 snapshot used for the current project scope
- pilot ticker subsets such as `pilot10.csv`
- optional historical constituent snapshots if acquired later

## Rules

- every universe file should preserve its source and snapshot date,
- pilot subsets should be explicit rather than inferred,
- ticker normalization must preserve dot tickers such as `BRK.B` and `BF.B`.

## Current implementation note

The repository now includes a dedicated CLI for freezing the current S&P 500 snapshot:

```bash
python -m src.cli.build_universe
```

Current generated files include:
- dated raw HTML snapshot
- dated CSV snapshot
- dated JSON manifest
- `latest_universe_snapshot.csv`
- `pilot10.csv`
