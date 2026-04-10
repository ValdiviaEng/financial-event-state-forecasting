# Evaluation Protocol

This document defines the project's current temporal evaluation protocol.

The code-level implementation now lives across:
- `src/split/walk_forward_splits.py`
- `src/split/purged_embargo_splits.py`
- `src/split/alignment_rules.py`
- `src/split/leakage_checks.py`
- `src/models/metric_registry.py`
- `src/models/calibration.py`
- `src/models/statistical_tests.py`
- `src/models/ablation_runner.py`

## Core principles

- All evaluation must be strictly out-of-sample in time.
- No train-only statistic may be fit on validation or test slices.
- Label overlap must be handled explicitly for multi-horizon targets.
- News alignment must use the official as-of-close rule.
- Final reported comparisons should be based on frozen datasets and stored predictions.

## Current split strategy

### Walk-forward folds

The current split builder supports:
- expanding windows,
- optional rolling windows,
- optional validation slices,
- deterministic fold generation from sorted unique trading dates.

The expected baseline pattern is:
- train dates first,
- optional validation dates second,
- test dates last,
- no overlap between groups.

### Purge and embargo

Purging is currently horizon-aware.

For a maximum forecast horizon `H`:
- a train date is purged if its forward label window could overlap the first holdout date,
- optional embargo days can also remove train dates near or immediately after the holdout block.

The current implementation supports:
- generic purge and embargo date filtering,
- purged walk-forward splits driven by actual horizon settings,
- reusable leakage assertions for verifying purge behavior.

## Alignment policy

The official source of truth is `src/split/alignment_rules.py`.

For article features on date `t`:
- only articles available by the market close on `t` may be used,
- after-hours articles roll to the next valid trading day,
- non-trading-day articles also roll to the next valid trading day.

## Leakage checks currently implemented

The current leakage-check module supports assertions for:
- overlapping split dates,
- walk-forward chronology,
- purge/embargo correctness,
- article alignment correctness,
- scaler-fit window contamination,
- future profile effective dates if time-varying profile rows are introduced later.

## Metrics policy

The current metrics layer now supports:

Regression:
- MAE
- RMSE
- `R^2`
- Pearson correlation
- Spearman correlation

Classification:
- AUC
- PR-AUC
- Brier score

Ranking:
- daily information coefficient
- ICIR

Current implementation note:
- evaluation currently writes machine-readable regression and ranking tables first,
- classification and calibration helpers are implemented but will only become central once probability outputs are used more broadly.

## Ablation policy

The intended ablation set remains:
- market-only vs multimodal
- split-adjusted labels vs raw labels
- no-decay vs decay event-state pooling
- embeddings vs sentiment-only
- with-profile vs without-profile
- single-horizon vs multi-horizon training

## Current test coverage

The current test suite already exercises:
- alignment behavior in `tests/test_alignment.py`
- leakage guardrails in `tests/test_leakage.py`
- walk-forward and purged split behavior in `tests/test_walk_forward.py`

These tests should be treated as mandatory gates before any training stage begins.

## Remaining work

Still to be added later:
- broader leakage tests tied to actual scaler objects and model preprocessing,
- richer evaluation-report generation,
- broader prediction-level comparison suites,
- more advanced statistical reporting for thesis tables and confidence intervals.
