from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.evaluation import compute_date_clustered_ci, compute_diagnostics, compute_stratified_metrics  # noqa: E402
from event_state_forecasting.v1p0.reporting import render_static_report  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402


def test_diagnostics_strata_uncertainty_and_report_fidelity(tmp_path: Path) -> None:
    predictions = _predictions()
    metrics = compute_diagnostics(predictions)
    strata = compute_stratified_metrics(predictions)
    intervals = compute_date_clustered_ci(predictions)
    report_path = render_static_report(metrics, strata, intervals, tmp_path, load_json_config(PROJECT_ROOT / "configs" / "reporting_v1p0.yaml"))

    rendered_metrics = pd.read_csv(tmp_path / "metrics.csv")
    rendered_strata = pd.read_csv(tmp_path / "strata.csv")
    rendered_intervals = pd.read_csv(tmp_path / "uncertainty.csv")
    html = report_path.read_text(encoding="utf-8").lower()

    assert not metrics.empty
    assert not strata.empty
    assert not intervals.empty
    assert rendered_metrics["row_count"].sum() == metrics["row_count"].sum()
    assert len(rendered_strata) == len(strata)
    assert len(rendered_intervals) == len(intervals)
    assert '<section id="metrics"' in html
    assert '<section id="strata"' in html
    assert '<section id="uncertainty"' in html
    assert f'data-row-count="{len(metrics)}"' in html
    assert f'data-row-count="{len(strata)}"' in html
    assert f'data-row-count="{len(intervals)}"' in html
    assert "source: metrics.csv" in html
    assert "source: strata.csv" in html
    assert "source: uncertainty.csv" in html
    assert "<caption>source: metrics.csv</caption>" in html
    assert "<caption>source: strata.csv</caption>" in html
    assert "<caption>source: uncertainty.csv</caption>" in html
    assert "not trading advice" in html
    assert "not a stage 6 reinterpretation" in html
    assert "buy" not in html
    assert "price target" not in html


def _predictions() -> pd.DataFrame:
    rows = []
    for index, split_role in enumerate(["validation", "validation", "lockbox", "lockbox"], start=1):
        rows.append(
            {
                "row_key": f"phase1_top50_v1p0|AAPL|2025-01-0{index}|1d",
                "benchmark_family_id": "phase1_top50_v1p0",
                "canonical_ticker": "AAPL",
                "as_of_date": f"2025-01-0{index}",
                "horizon_id": "1d",
                "fold_id": "fold_001",
                "split_role": split_role,
                "model_id": "market_lag_linear_v1",
                "prediction": 0.01 * index,
                "target": 0.011 * index,
                "no_news_flag": index % 2 == 0,
                "provider_truncation_risk_flag": index == 3,
                "article_count": index - 1,
            }
        )
    return pd.DataFrame(rows)
