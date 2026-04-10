# Notebooks Directory

This directory is reserved for exploratory analysis and visualization only.

Notebook policy for later implementation:
- notebooks should not become the source of truth for pipeline logic,
- important results should be reproducible from scripts or CLI commands,
- notebooks should load existing datasets rather than mutate them in place,
- any conclusion used in the thesis should be reproducible without hidden state.

## Current implementation note

The repository now has enough executable CLI coverage that notebooks should be
used mainly for:
- exploratory diagnostics,
- visual inspection of stored outputs,
- thesis figure prototyping.

They should not replace:
- ingestion pipelines,
- dataset assembly,
- model training,
- evaluation,
- ablation execution.
