from __future__ import annotations

import json
from pathlib import Path

from src.models.ablation_runner import build_ablation_summary, ensure_run_summaries_comparable, load_run_summary, load_run_metric_rows


def _write_run_summary(base_dir: Path, *, run_id: str, model_name: str, rmse: float) -> Path:
    metrics_path = base_dir / f"{run_id}_metrics.json"
    metrics_payload = {
        "row_count": 4,
        "metrics": {
            "test": {
                "y_excess_ret_1": {
                    "mae": rmse / 2,
                    "rmse": rmse,
                    "r2": 0.5,
                    "weighted_loss": rmse**2,
                }
            }
        },
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2) + "\n", encoding="utf-8")

    summary_path = base_dir / f"{run_id}_summary.json"
    summary_payload = {
        "run_id": run_id,
        "panel_path": str((base_dir / "panel.parquet").resolve()),
        "horizons": [1],
        "split_count": 1,
        "results": [
            {
                "model_name": model_name,
                "split_id": 0,
                "metrics_path": str(metrics_path.resolve()),
            }
        ],
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2) + "\n", encoding="utf-8")
    return summary_path


def test_ablation_runner_loads_and_aggregates_run_summaries(tmp_path: Path) -> None:
    summary_a = _write_run_summary(tmp_path, run_id="baseline_a", model_name="ridge", rmse=0.10)
    summary_b = _write_run_summary(tmp_path, run_id="baseline_b", model_name="ridge", rmse=0.20)

    loaded = load_run_summary(summary_a)
    assert loaded["run_id"] == "baseline_a"

    metric_rows = load_run_metric_rows(summary_a)
    assert len(metric_rows) == 1
    assert metric_rows.iloc[0]["rmse"] == 0.10

    ensure_run_summaries_comparable([load_run_summary(summary_a), load_run_summary(summary_b)])
    ablation = build_ablation_summary([summary_a, summary_b], partition="test", metric_name="rmse")
    assert len(ablation) == 2
    assert sorted(ablation["mean_rmse"].tolist()) == [0.10, 0.20]
