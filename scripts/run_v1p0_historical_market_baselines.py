from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.linear_model import Ridge


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.modeling import fit_preprocessor, validate_prediction_schema  # noqa: E402
from event_state_forecasting.v1p0.versioning import load_json_config  # noqa: E402


FEATURE_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
STAGE4_ROOT = PROJECT_ROOT / "data/splits/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z"
ARTIFACT_ID = "market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z"
SPLIT_ARTIFACT_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1__stage4_splits_v1"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full historical v1p0 market lag-linear and fixed-XGBoost baselines.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    started = time.perf_counter()
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    model_config = load_json_config(PROJECT_ROOT / "configs" / "models_v1p0.yaml")
    feature_manifest = json.loads((FEATURE_ROOT / "feature_manifest.json").read_text(encoding="utf-8"))
    frame = _load_training_frame(feature_manifest)
    feature_columns = list(feature_manifest["feature_columns"])

    all_predictions: list[pd.DataFrame] = []
    fit_records: list[dict[str, Any]] = []
    preprocessing_records: list[dict[str, Any]] = []
    blocker_records: list[dict[str, Any]] = []
    for model in model_config["models"]:
        result = _run_model(frame, feature_columns, model)
        if result["blocker"] is not None:
            blocker_records.append(result["blocker"])
            continue
        all_predictions.append(result["predictions"])
        fit_records.extend(result["fit_records"])
        preprocessing_records.extend(result["preprocessing_records"])

    if not all_predictions:
        raise RuntimeError("no model predictions were created")

    predictions = pd.concat(all_predictions, ignore_index=True)
    required_columns = model_config["saved_prediction_schema"]["required_columns"]
    schema_result = validate_prediction_schema(predictions, required_columns)
    prediction_path = output_root / "saved_predictions.parquet"
    fit_path = output_root / "model_fit_manifest.parquet"
    preprocessing_path = output_root / "preprocessing_fit_manifest.parquet"
    predictions.to_parquet(prediction_path, index=False)
    pd.DataFrame(fit_records).to_parquet(fit_path, index=False)
    pd.DataFrame(preprocessing_records).to_parquet(preprocessing_path, index=False)

    prediction_digest = _sha256(prediction_path)
    manifest = {
        "artifact_type": "v1p0_stage19_market_baseline_manifest",
        "artifact_id": ARTIFACT_ID,
        "generated_at_utc": "2026-05-24T06:45:00Z",
        "feature_artifact_id": feature_manifest["artifact_id"],
        "feature_digest_sha256": feature_manifest["feature_digest_sha256"],
        "split_artifact_version": SPLIT_ARTIFACT_VERSION,
        "label_artifact_version": "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1",
        "outputs": {
            "saved_predictions": _rel(prediction_path),
            "model_fit_manifest": _rel(fit_path),
            "preprocessing_fit_manifest": _rel(preprocessing_path),
            "model_manifest": _rel(output_root / "model_manifest.json"),
        },
        "model_ids": sorted(predictions["model_id"].unique().tolist()),
        "model_count": int(predictions["model_id"].nunique()),
        "fold_count": int(predictions["fold_id"].nunique()),
        "horizons": sorted(predictions["horizon_id"].unique().tolist()),
        "prediction_role_counts": {str(k): int(v) for k, v in predictions["split_role"].value_counts().sort_index().items()},
        "saved_prediction_row_count": int(len(predictions)),
        "prediction_digest_sha256": prediction_digest,
        "schema_validation": schema_result,
        "model_fit_count": len(fit_records),
        "preprocessing_fit_count": len(preprocessing_records),
        "blockers": blocker_records,
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "lockbox_policy": {
            "lockbox_predictions_created": bool((predictions["split_role"] == "lockbox").any()),
            "lockbox_metrics_computed": False,
            "lockbox_used_for_selection": False,
        },
        "train_prediction_policy": "train_predictions_are_diagnostic_non_claim_bearing",
        "benchmark_claim": False,
        "non_claims": [
            "not_metrics",
            "not_benchmark_result",
            "not_hyperparameter_search",
            "not_stage6_reinterpretation",
            "not_trading_signal",
        ],
    }
    _write_json(output_root / "model_manifest.json", manifest)
    print(json.dumps({"status": "passed", "model_count": manifest["model_count"], "prediction_rows": len(predictions), "output_root": _rel(output_root)}, sort_keys=True))


def _load_training_frame(feature_manifest: dict[str, Any]) -> pd.DataFrame:
    row_key = list(feature_manifest["row_key"])
    features = pd.read_parquet(PROJECT_ROOT / feature_manifest["outputs"]["market_lag_features"])
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*row_key, "forward_excess_return"])
    splits = pd.read_parquet(
        STAGE4_ROOT / "split_assignments.parquet",
        columns=["fold_id", *row_key, "split_role", "lockbox_flag", "preprocessing_fit_allowed"],
    )
    splits = splits[splits["split_role"].isin(["train", "validation", "lockbox"])].copy()
    frame = splits.merge(features, on=row_key, how="inner", validate="many_to_one").merge(labels, on=row_key, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target"})
    frame["row_key"] = frame[row_key].astype(str).agg("|".join, axis=1)
    frame["feature_artifact_version"] = feature_manifest["artifact_id"]
    frame["split_artifact_version"] = SPLIT_ARTIFACT_VERSION
    frame["v1p0_artifact_version"] = ARTIFACT_ID
    return frame


def _run_model(frame: pd.DataFrame, feature_columns: list[str], model: dict[str, Any]) -> dict[str, Any]:
    if model["family"] == "xgboost_regressor":
        try:
            from xgboost import XGBRegressor  # type: ignore
        except ModuleNotFoundError:
            return {"predictions": pd.DataFrame(), "fit_records": [], "preprocessing_records": [], "blocker": {"model_id": model["model_id"], "status": "blocked_missing_dependency", "missing_dependency": "xgboost"}}
    records: list[pd.DataFrame] = []
    fit_records: list[dict[str, Any]] = []
    preprocessing_records: list[dict[str, Any]] = []
    for (fold_id, horizon_id), group in frame.groupby(["fold_id", "horizon_id"], sort=True):
        train = group[group["split_role"] == "train"].copy()
        score = group[group["split_role"].isin(["train", "validation", "lockbox"])].copy()
        if train.empty or score.empty:
            continue
        fit_started = time.perf_counter()
        preprocessor = fit_preprocessor(train, feature_columns, model["preprocessing"])
        if model["family"] == "ridge_linear":
            estimator = Ridge(alpha=float(model["params"].get("alpha", 1.0)))
        elif model["family"] == "xgboost_regressor":
            params = dict(model["params"])
            estimator = XGBRegressor(**params)  # type: ignore[name-defined]
        else:
            raise RuntimeError(f"unsupported v1p0 model family: {model['family']}")
        estimator.fit(preprocessor.transform(train), train["target"].astype("float64"))
        training_time = time.perf_counter() - fit_started
        infer_started = time.perf_counter()
        prediction = estimator.predict(preprocessor.transform(score))
        inference_time = time.perf_counter() - infer_started
        output = score[["row_key", "benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id", "fold_id", "split_role", "dataset_version", "feature_artifact_version", "split_artifact_version", "v1p0_artifact_version"]].copy()
        output["model_id"] = model["model_id"]
        output["model_family"] = model["family"]
        output["branch"] = model["branch"]
        output["prediction"] = prediction
        records.append(output)
        fit_records.append({
            "model_id": model["model_id"],
            "model_family": model["family"],
            "fold_id": fold_id,
            "horizon_id": horizon_id,
            "train_rows": int(len(train)),
            "score_rows": int(len(score)),
            "training_time_seconds": round(training_time, 6),
            "inference_time_seconds": round(inference_time, 6),
            "params_json": json.dumps(model["params"], sort_keys=True),
            "seed": 1729,
        })
        preprocessing_records.append({
            "model_id": model["model_id"],
            "fold_id": fold_id,
            "horizon_id": horizon_id,
            "policy": model["preprocessing"],
            "feature_count": len(feature_columns),
            "fit_row_count": preprocessor.fit_row_count,
        })
    predictions = pd.concat(records, ignore_index=True) if records else pd.DataFrame()
    return {"predictions": predictions, "fit_records": fit_records, "preprocessing_records": preprocessing_records, "blocker": None}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _rel(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT).as_posix()


if __name__ == "__main__":
    main()
