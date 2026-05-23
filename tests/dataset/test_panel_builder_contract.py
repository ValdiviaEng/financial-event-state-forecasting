from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.data.contracts import APPROVED_HORIZONS, validate_manifest, validate_panel_records  # noqa: E402
from event_state_forecasting.dataset.panel_builder import FULL_WINDOW_FILENAME, build_stage2_benchmark_dataset  # noqa: E402
from event_state_forecasting.dataset.row_universe import row_universe_digest  # noqa: E402


def test_stage2_panel_builder_writes_manifest_backed_partitioned_dataset(tmp_path: Path) -> None:
    fixture = _write_stage2_fixture(tmp_path)

    outputs = build_stage2_benchmark_dataset(
        output_root=fixture["output_root"],
        universe_path=fixture["universe_path"],
        raw_twelvedata_root=fixture["twelvedata_root"],
        raw_alphavantage_root=fixture["alphavantage_root"],
        stage1_manifest_path=fixture["stage1_manifest_path"],
        stage1_ohlcv_manifest_path=fixture["stage1_ohlcv_manifest_path"],
        twelvedata_audit_path=fixture["twelvedata_audit_path"],
        stage2_contract_manifest_path=fixture["stage2_contract_manifest_path"],
    )

    assert outputs.row_count == 50 * 5 * len(APPROVED_HORIZONS)
    assert outputs.panel_path.is_dir()
    assert outputs.manifest_path.exists()
    assert outputs.clean_window_path.exists()
    assert outputs.cvx_patch_manifest_path.exists()

    manifest = json.loads(outputs.manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    assert manifest["identity"]["benchmark_claim"] is False
    assert manifest["coverage"]["support_ticker_excluded_from_rows"] is True
    assert manifest["hashes"]["branch_row_universe_equal"] is True
    assert manifest["availability"]["no_news_row_count"] > 0
    assert manifest["availability"]["rows_with_news_count"] > 0

    frame = pd.read_parquet(outputs.panel_path)
    records = frame.to_dict("records")
    validate_panel_records(records)
    assert "SPY" not in set(frame["canonical_ticker"])
    assert row_universe_digest(records) == outputs.row_digest

    patch_manifest = json.loads(outputs.cvx_patch_manifest_path.read_text(encoding="utf-8"))
    assert patch_manifest["raw_files_mutated"] is False
    assert patch_manifest["patch_event_count"] == 1
    assert patch_manifest["selected_full_window_filename"] == FULL_WINDOW_FILENAME


def test_stage2_panel_builder_accepts_explicit_twelvedata_full_window_filename(tmp_path: Path) -> None:
    raw_filename = "time_series__2010-01-01__2026-05-22.json"
    fixture = _write_stage2_fixture(tmp_path, twelvedata_filename=raw_filename)

    outputs = build_stage2_benchmark_dataset(
        output_root=fixture["output_root"],
        universe_path=fixture["universe_path"],
        raw_twelvedata_root=fixture["twelvedata_root"],
        raw_alphavantage_root=fixture["alphavantage_root"],
        stage1_manifest_path=fixture["stage1_manifest_path"],
        stage1_ohlcv_manifest_path=fixture["stage1_ohlcv_manifest_path"],
        twelvedata_audit_path=fixture["twelvedata_audit_path"],
        stage2_contract_manifest_path=fixture["stage2_contract_manifest_path"],
        twelvedata_full_window_filename=raw_filename,
    )

    manifest = json.loads(outputs.manifest_path.read_text(encoding="utf-8"))
    patch_manifest = json.loads(outputs.cvx_patch_manifest_path.read_text(encoding="utf-8"))
    assert manifest["sources"]["twelvedata_full_window_filename"] == raw_filename
    assert patch_manifest["selected_full_window_filename"] == raw_filename


def _write_stage2_fixture(tmp_path: Path, *, twelvedata_filename: str = FULL_WINDOW_FILENAME) -> dict[str, Path]:
    tickers = ("BRK.B", "CVX", *(f"T{i:02d}" for i in range(48)))
    dates = _business_dates(date(2024, 4, 1), 70)
    universe_path = tmp_path / "universe.csv"
    universe_path.write_text("ticker\n" + "\n".join(tickers) + "\n", encoding="utf-8")

    twelvedata_root = tmp_path / "raw" / "twelvedata"
    for ticker in (*tickers, "SPY"):
        rows = []
        for idx, value in enumerate(dates):
            open_value = 100.0 + idx
            high_value = open_value + 1.0
            low_value = open_value - 1.0
            close_value = open_value + 0.5
            if ticker == "CVX" and idx == 0:
                high_value = open_value - 0.5
            rows.append(
                {
                    "datetime": value.isoformat(),
                    "open": f"{open_value:.2f}",
                    "high": f"{high_value:.2f}",
                    "low": f"{low_value:.2f}",
                    "close": f"{close_value:.2f}",
                    "volume": "1000",
                }
            )
        _write_json(
            twelvedata_root / ticker / twelvedata_filename,
            {"meta": {"symbol": ticker}, "status": "ok", "values": rows},
        )

    alphavantage_root = tmp_path / "raw" / "alphavantage"
    for ticker in tickers:
        feed = []
        if ticker == "BRK.B":
            feed.append({"time_published": "20240401T120000", "title": "fixture"})
        _write_json(alphavantage_root / ticker / "news_sentiment__2024-01-01__2024-12-31.json", {"feed": feed})

    stage1_manifest_path = tmp_path / "stage1_manifest.json"
    _write_json(
        stage1_manifest_path,
        {
            "scope": {"target_family": "forward_excess_returns", "horizons": list(APPROVED_HORIZONS)},
            "alphavantage_top50": {"likely_truncated_windows": 1, "empty_feed_windows": 1},
            "likely_truncated_window_ids": ["BRK.B:2024:1000"],
            "empty_window_ids": ["CVX:2024:0"],
        },
    )
    stage1_ohlcv_manifest_path = tmp_path / "stage1_ohlcv_manifest.json"
    _write_json(
        stage1_ohlcv_manifest_path,
        {
            "active_raw_twelvedata": {
                "clean_window_candidate_from_raw": {
                    "all_horizons_candidate_as_of_start": "2024-04-01",
                    "all_horizons_candidate_as_of_end": "2024-04-05",
                }
            }
        },
    )
    stage2_contract_manifest_path = tmp_path / "stage2_contract_manifest.json"
    _write_json(
        stage2_contract_manifest_path,
        {
            "scope": {
                "benchmark_family_id": "phase1_top50",
                "target_family": "forward_excess_returns",
                "horizons": list(APPROVED_HORIZONS),
            }
        },
    )
    twelvedata_audit_path = tmp_path / "twelvedata_audit.json"
    _write_json(twelvedata_audit_path, {"status": "complete_observed_life_with_late_start_limitations"})
    return {
        "output_root": tmp_path / "datasets" / "phase1_top50",
        "universe_path": universe_path,
        "twelvedata_root": twelvedata_root,
        "alphavantage_root": alphavantage_root,
        "stage1_manifest_path": stage1_manifest_path,
        "stage1_ohlcv_manifest_path": stage1_ohlcv_manifest_path,
        "stage2_contract_manifest_path": stage2_contract_manifest_path,
        "twelvedata_audit_path": twelvedata_audit_path,
    }


def _business_dates(start: date, count: int) -> list[date]:
    values: list[date] = []
    current = start
    while len(values) < count:
        if current.weekday() < 5:
            values.append(current)
        current += timedelta(days=1)
    return values


def _write_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
