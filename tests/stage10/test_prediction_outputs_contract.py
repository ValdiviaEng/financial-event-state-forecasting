from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.stage10.prediction_outputs import (  # noqa: E402
    HORIZON_ORDER,
    Stage10CInputs,
    generate_stage10c_prediction_packet,
    select_snapshot_predictions,
    validate_stage10c_packet,
)


def test_stage10c_packet_generation_preserves_non_claims_and_outputs(tmp_path: Path) -> None:
    roots = _write_stage10c_inputs(tmp_path)

    manifest = generate_stage10c_prediction_packet(
        Stage10CInputs(
            model_root=roots["model_root"],
            feature_root=roots["feature_root"],
            evaluation_root=roots["evaluation_root"],
            output_base_root=tmp_path / "prediction_outputs" / "phase1_top50",
            data_cutoff="2026-02-13",
            run_date="2026-05-23",
        )
    )

    output_root = Path(manifest["identity"]["artifact_root"])
    validation = validate_stage10c_packet(output_root)
    model_outputs = pd.read_parquet(output_root / "model_outputs.parquet")
    top10_primary = pd.read_parquet(output_root / "top10_primary_event_state.parquet")
    relevant_news = pd.read_parquet(output_root / "relevant_news_context.parquet")
    trajectory = pd.read_parquet(output_root / "trajectory_points.parquet")

    assert validation["status"] == "passed"
    assert manifest["benchmark_claim"] is False
    assert manifest["trading_signal_approved"] is False
    assert manifest["service_api_scope"] is False
    assert manifest["forecast_candidate_semantics_used"] is False
    assert set(model_outputs["row_role"]) == {"historical_prediction"}
    assert bool(model_outputs["trading_signal_approved"].any()) is False
    assert set(top10_primary.groupby("horizon_id").size()) == {10}
    assert "url" not in relevant_news.columns
    assert bool(relevant_news["url_included"].any()) is False
    assert bool(trajectory["projected_price_path"].any()) is False


def test_stage10c_allow_overwrite_removes_stale_packet_files(tmp_path: Path) -> None:
    roots = _write_stage10c_inputs(tmp_path)
    packet_inputs = Stage10CInputs(
        model_root=roots["model_root"],
        feature_root=roots["feature_root"],
        evaluation_root=roots["evaluation_root"],
        output_base_root=tmp_path / "prediction_outputs" / "phase1_top50",
        data_cutoff="2026-02-13",
        run_date="2026-05-23",
        allow_overwrite=True,
    )
    manifest = generate_stage10c_prediction_packet(packet_inputs)
    stale_path = Path(manifest["identity"]["artifact_root"]) / "stale_leftover.txt"
    stale_path.write_text("old", encoding="utf-8")

    generate_stage10c_prediction_packet(packet_inputs)

    assert not stale_path.exists()


def test_snapshot_selection_uses_latest_fold_per_ticker_horizon_model() -> None:
    frame = pd.DataFrame(
        {
            "benchmark_family_id": ["phase1_top50"] * 2,
            "canonical_ticker": ["AAPL", "AAPL"],
            "as_of_date": ["2026-02-13", "2026-02-13"],
            "horizon_id": ["1d", "1d"],
            "fold_id": ["fold_001", "fold_009"],
            "split_role": ["lockbox", "lockbox"],
            "model_id": ["event_state_gated_fusion", "event_state_gated_fusion"],
            "model_family": ["gated", "gated"],
            "branch": ["event_state", "event_state"],
            "dataset_version": ["dataset_v1", "dataset_v1"],
            "feature_artifact_version": ["features_v1", "features_v1"],
            "split_artifact_version": ["splits_v1", "splits_v1"],
            "stage5_artifact_version": ["stage5_v1", "stage5_v1"],
            "prediction": [0.1, 0.9],
        }
    )

    selected = select_snapshot_predictions(frame, "2026-02-13")

    assert len(selected) == 1
    assert selected.iloc[0]["fold_id"] == "fold_009"
    assert selected.iloc[0]["prediction"] == 0.9


def _write_stage10c_inputs(tmp_path: Path) -> dict[str, Path]:
    model_root = tmp_path / "models"
    feature_root = tmp_path / "features"
    evaluation_root = tmp_path / "evaluation"
    model_root.mkdir()
    feature_root.mkdir()
    evaluation_root.mkdir()

    tickers = [f"T{i:02d}" for i in range(12)]
    predictions = []
    event_features = []
    labels = []
    market = []
    aligned_news = []
    selected_hurdles = {horizon: "market_ridge" for horizon in HORIZON_ORDER}
    for horizon_index, horizon in enumerate(HORIZON_ORDER):
        for ticker_index, ticker in enumerate(tickers):
            article_id = f"article_{horizon}_{ticker}"
            predictions.append(_prediction_row(ticker, horizon, "event_state_gated_fusion", "event_state", 0.01 * ticker_index + horizon_index))
            predictions.append(_prediction_row(ticker, horizon, "market_ridge", "market_only", 0.005 * ticker_index))
            event_features.append(
                {
                    "benchmark_family_id": "phase1_top50",
                    "canonical_ticker": ticker,
                    "as_of_date": "2026-02-13",
                    "horizon_id": horizon,
                    "aligned_article_ids": article_id,
                    "stage3_aligned_news_count": 1,
                    "provider_empty_feed_flag": False,
                    "provider_truncation_risk_flag": ticker_index % 5 == 0,
                    "minutes_since_latest_aligned_article": 60.0,
                    "no_news_flag": False,
                    "empty_event_state_flag": False,
                }
            )
            labels.append(
                {
                    "benchmark_family_id": "phase1_top50",
                    "canonical_ticker": ticker,
                    "as_of_date": "2026-02-13",
                    "horizon_id": horizon,
                    "label_window_start": "2026-02-17",
                    "label_window_end": "2026-02-20",
                    "forward_excess_return": 0.001 * ticker_index,
                    "label_available_flag": True,
                }
            )
            market.append(
                {
                    "benchmark_family_id": "phase1_top50",
                    "canonical_ticker": ticker,
                    "as_of_date": "2026-02-13",
                    "horizon_id": horizon,
                    "market_close": 100.0 + ticker_index,
                }
            )
            aligned_news.append(
                {
                    "article_id": article_id,
                    "ticker": ticker,
                    "published_timestamp": "2026-02-13T14:00:00-05:00",
                    "aligned_as_of_date": "2026-02-13",
                    "roll_forward_reason": "same_day_as_of_close",
                    "title": f"Title for {ticker}",
                    "summary": f"Summary for {ticker}",
                    "url": "https://example.invalid/news",
                    "text_hash": f"hash_{horizon}_{ticker}",
                }
            )
    for day in range(21):
        date = f"2026-01-{day + 1:02d}"
        for ticker_index, ticker in enumerate(tickers):
            market.append(
                {
                    "benchmark_family_id": "phase1_top50",
                    "canonical_ticker": ticker,
                    "as_of_date": date,
                    "horizon_id": "1d",
                    "market_close": 90.0 + ticker_index + day,
                }
            )

    pd.DataFrame(predictions).to_parquet(model_root / "saved_predictions.parquet", index=False)
    pd.DataFrame(event_features).to_parquet(feature_root / "event_state_features.parquet", index=False)
    pd.DataFrame(labels).to_parquet(feature_root / "labels.parquet", index=False)
    pd.DataFrame(market).to_parquet(feature_root / "market_features.parquet", index=False)
    pd.DataFrame(aligned_news).to_parquet(feature_root / "aligned_news.parquet", index=False)
    _write_json(
        model_root / "model_manifest.json",
        {
            "identity": {
                "artifact_version": "stage5_models_v1",
                "input_feature_artifact_version": "features_v1",
                "input_split_artifact_version": "splits_v1",
                "row_universe_digest": "abcdef0123456789",
            }
        },
    )
    _write_json(
        evaluation_root / "evaluation_manifest.json",
        {
            "selected_market_hurdles": selected_hurdles,
            "comparability_classification": "limitation_bearing",
        },
    )
    _write_json(
        evaluation_root / "comparison_summary.json",
        {
            "result_class": "clean_null",
            "result_reason": "test fixture",
        },
    )
    return {"model_root": model_root, "feature_root": feature_root, "evaluation_root": evaluation_root}


def _prediction_row(ticker: str, horizon: str, model_id: str, branch: str, prediction: float) -> dict[str, object]:
    return {
        "benchmark_family_id": "phase1_top50",
        "canonical_ticker": ticker,
        "as_of_date": "2026-02-13",
        "horizon_id": horizon,
        "fold_id": "fold_009",
        "split_role": "lockbox",
        "model_id": model_id,
        "model_family": model_id,
        "branch": branch,
        "dataset_version": "dataset_v1",
        "feature_artifact_version": "features_v1",
        "split_artifact_version": "splits_v1",
        "stage5_artifact_version": "stage5_models_v1",
        "prediction": prediction,
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
