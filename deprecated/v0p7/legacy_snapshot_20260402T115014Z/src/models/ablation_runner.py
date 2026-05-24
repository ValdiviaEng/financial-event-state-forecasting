"""Helpers for reproducible comparison of related experiment runs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.io_utils import read_json


class AblationError(RuntimeError):
    """Raised when ablation inputs are not directly comparable."""


def load_run_summary(summary_path: str | Path) -> dict[str, Any]:
    """Load a run summary JSON file."""

    payload = read_json(summary_path)
    if not isinstance(payload, dict):
        raise AblationError(f"Run summary at {summary_path} must be a JSON object.")
    return payload


def ensure_run_summaries_comparable(run_summaries: list[dict[str, Any]]) -> None:
    """Ensure ablation run summaries can be compared directly."""

    if len(run_summaries) < 2:
        raise AblationError("At least two run summaries are required for an ablation comparison.")

    reference = run_summaries[0]
    reference_keys = {
        "panel_path": reference.get("panel_path"),
        "horizons": tuple(reference.get("horizons", [])),
        "split_count": reference.get("split_count"),
    }
    for summary in run_summaries[1:]:
        current_keys = {
            "panel_path": summary.get("panel_path"),
            "horizons": tuple(summary.get("horizons", [])),
            "split_count": summary.get("split_count"),
        }
        if current_keys != reference_keys:
            raise AblationError(
                "Run summaries are not directly comparable. Expected matching panel path, horizons, and split count."
            )


def load_run_metric_rows(summary_path: str | Path) -> pd.DataFrame:
    """Load all metric rows referenced by a run summary."""

    summary = load_run_summary(summary_path)
    rows: list[dict[str, Any]] = []
    for result in summary.get("results", []):
        metrics_path = result.get("metrics_path")
        if metrics_path is None:
            continue
        metrics_payload = read_json(metrics_path)
        for partition, partition_metrics in metrics_payload.get("metrics", {}).items():
            for target, target_metrics in partition_metrics.items():
                row = {
                    "run_id": summary.get("run_id"),
                    "panel_path": summary.get("panel_path"),
                    "model_name": result.get("model_name"),
                    "split_id": result.get("split_id"),
                    "partition": partition,
                    "target": target,
                }
                row.update(target_metrics)
                rows.append(row)
    return pd.DataFrame(rows)


def build_ablation_summary(
    summary_paths: list[str | Path],
    *,
    partition: str = "test",
    metric_name: str = "rmse",
) -> pd.DataFrame:
    """Build an aggregated ablation table from comparable run summaries."""

    run_summaries = [load_run_summary(path) for path in summary_paths]
    ensure_run_summaries_comparable(run_summaries)

    metric_rows = [load_run_metric_rows(path) for path in summary_paths]
    combined = pd.concat(metric_rows, ignore_index=True) if metric_rows else pd.DataFrame()
    if combined.empty:
        return combined

    filtered = combined[combined["partition"] == partition].copy()
    if metric_name not in filtered.columns:
        raise AblationError(f"Metric '{metric_name}' is not present in the run metric tables.")

    grouped = (
        filtered.groupby(["run_id", "model_name", "target"], sort=True)[metric_name]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(columns={"mean": f"mean_{metric_name}", "std": f"std_{metric_name}", "count": "fold_count"})
    )
    return grouped
