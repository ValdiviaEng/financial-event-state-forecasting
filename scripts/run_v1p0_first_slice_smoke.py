from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.evaluation import compute_date_clustered_ci, compute_diagnostics, compute_stratified_metrics
from event_state_forecasting.v1p0.features import build_market_lag_features
from event_state_forecasting.v1p0.modeling import run_fixed_xgboost_or_blocker, run_lag_linear_predictions, validate_prediction_schema
from event_state_forecasting.v1p0.registry import validate_feature_registry
from event_state_forecasting.v1p0.reporting import render_static_report
from event_state_forecasting.v1p0.versioning import load_json_config, validate_version_manifest


def main() -> int:
    config_root = PROJECT_ROOT / "configs"
    output_root = PROJECT_ROOT / "data" / "v1p0_first_slice_smoke" / "first_slice_smoke_v1"
    output_root.mkdir(parents=True, exist_ok=True)

    version_manifest = validate_version_manifest(load_json_config(config_root / "v1p0_version_manifest.yaml"))
    registry = validate_feature_registry(load_json_config(config_root / "feature_registry_v1p0.yaml"))
    feature_config = load_json_config(config_root / "market_features_v1p0.yaml")
    model_config = load_json_config(config_root / "models_v1p0.yaml")
    report_config = load_json_config(config_root / "reporting_v1p0.yaml")

    frame = _toy_frame()
    features = build_market_lag_features(frame, feature_config)
    model_frame = frame.merge(features, on=[*feature_config["row_key"], "dataset_version"], how="left")
    feature_columns = [column for column in model_frame.columns if "_lag_" in column or "_rolling_" in column]
    lag_linear_predictions = run_lag_linear_predictions(model_frame, feature_columns, model_config["models"][0])
    xgboost_result = run_fixed_xgboost_or_blocker(model_frame, feature_columns, model_config["models"][1])
    if isinstance(xgboost_result, dict):
        predictions = lag_linear_predictions
        xgboost_status = xgboost_result
    else:
        predictions = pd.concat([lag_linear_predictions, xgboost_result], ignore_index=True)
        xgboost_status = {"status": "available", "prediction_rows": int(len(xgboost_result))}
    schema = validate_prediction_schema(predictions, model_config["saved_prediction_schema"]["required_columns"])
    diagnostics = compute_diagnostics(predictions)
    strata = compute_stratified_metrics(predictions)
    intervals = compute_date_clustered_ci(predictions)
    report_path = render_static_report(diagnostics, strata, intervals, output_root, report_config)

    features.to_csv(output_root / "market_lag_features.csv", index=False)
    lag_linear_predictions.to_csv(output_root / "market_lag_linear_predictions.csv", index=False)
    if not isinstance(xgboost_result, dict):
        xgboost_result.to_csv(output_root / "market_xgboost_v1_fixed_predictions.csv", index=False)
    predictions.to_csv(output_root / "saved_predictions.csv", index=False)
    summary = {
        "status": "v1p0_first_slice_smoke_completed",
        "version_manifest_digest": version_manifest["manifest_digest"],
        "registry_digest": registry["registry_digest"],
        "prediction_schema": schema,
        "xgboost_status": xgboost_status,
        "report_path": str(report_path.relative_to(PROJECT_ROOT)),
        "benchmark_claim": False,
        "trading_signal_approved": False,
    }
    (output_root / "v1p0_first_slice_smoke_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


def _toy_frame() -> pd.DataFrame:
    rows = []
    closes = [100.0, 101.0, 103.0, 106.0, 110.0, 111.0, 113.0, 114.0]
    roles = ["train", "train", "train", "train", "train", "train", "validation", "lockbox"]
    for index, (close, role) in enumerate(zip(closes, roles), start=1):
        rows.append(
            {
                "row_key": f"phase1_top50_v1p0|AAPL|2025-01-0{index}|1d",
                "benchmark_family_id": "phase1_top50_v1p0",
                "canonical_ticker": "AAPL",
                "as_of_date": f"2025-01-0{index}",
                "horizon_id": "1d",
                "fold_id": "fold_001",
                "split_role": role,
                "dataset_version": "toy_dataset_v1",
                "feature_artifact_version": "market_lag_features_v1p0_smoke",
                "split_artifact_version": "toy_splits_v1",
                "market_open": close - 1.0,
                "market_close": close,
                "market_volume": 1000 + index,
                "target": 0.001 * index,
                "no_news_flag": index % 2 == 0,
                "provider_truncation_risk_flag": index == 3,
                "article_count": index - 1,
            }
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    raise SystemExit(main())
