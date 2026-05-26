from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


MODEL_ROOT = PROJECT_ROOT / "data/models/v1p0/market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z"
FEATURE_ROOT = PROJECT_ROOT / "data/features/v1p0/market_lag_features_v1p0__source_6868e3b8__stage17_20260524T062000Z"
STAGE3_ROOT = PROJECT_ROOT / "data/features/phase1_top50/phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data/diagnostics/v1p0/stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z"
ARTIFACT_ID = "stage20_baseline_diagnostics__stage19_f5bfd7fa__20260524T070000Z"
LINEAR_MODEL = "market_lag_linear_v1"
XGB_MODEL = "market_xgboost_v1_fixed"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute v1p0 Stage 20 diagnostics from Stage 19 saved predictions.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    started = time.perf_counter()
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    frame = _load_prediction_frame()
    metrics = _compute_metrics(frame, ["split_role", "fold_id", "horizon_id", "model_id"])
    gaps = _compute_train_validation_gaps(metrics)
    fold_dispersion = _compute_fold_dispersion(metrics)
    horizon_stability = _compute_horizon_stability(metrics)
    strata = _compute_strata_metrics(frame)
    gate = _diagnostic_gate(metrics, gaps, horizon_stability)

    paths = {
        "metrics": output_root / "metrics.parquet",
        "train_validation_gaps": output_root / "train_validation_gaps.parquet",
        "fold_dispersion": output_root / "fold_dispersion.parquet",
        "horizon_stability": output_root / "horizon_stability.parquet",
        "strata_metrics": output_root / "strata_metrics.parquet",
    }
    metrics.to_parquet(paths["metrics"], index=False)
    gaps.to_parquet(paths["train_validation_gaps"], index=False)
    fold_dispersion.to_parquet(paths["fold_dispersion"], index=False)
    horizon_stability.to_parquet(paths["horizon_stability"], index=False)
    strata.to_parquet(paths["strata_metrics"], index=False)

    manifest = {
        "artifact_type": "v1p0_stage20_diagnostic_manifest",
        "artifact_id": ARTIFACT_ID,
        "generated_at_utc": "2026-05-24T07:00:00Z",
        "source_model_artifact_id": "market_baselines_v1p0__features_e1bdb390__stage19_20260524T064500Z",
        "source_prediction_digest_sha256": json.loads((MODEL_ROOT / "model_manifest.json").read_text(encoding="utf-8"))["prediction_digest_sha256"],
        "outputs": {name: _rel(path) for name, path in paths.items()},
        "counts": {
            "prediction_rows_consumed": int(len(frame)),
            "metric_rows": int(len(metrics)),
            "train_validation_gap_rows": int(len(gaps)),
            "fold_dispersion_rows": int(len(fold_dispersion)),
            "horizon_stability_rows": int(len(horizon_stability)),
            "strata_metric_rows": int(len(strata)),
        },
        "diagnostic_gate": gate,
        "metric_digest_sha256": _sha256(paths["metrics"]),
        "build_duration_seconds": round(time.perf_counter() - started, 3),
        "benchmark_claim": False,
        "lockbox_tuning": False,
        "non_claims": [
            "not_promotion_claim",
            "not_hyperparameter_search",
            "not_stage6_reinterpretation",
            "not_provider_level_article_completeness",
        ],
    }
    _write_json(output_root / "diagnostic_manifest.json", manifest)
    print(json.dumps({"status": "passed", "metric_rows": len(metrics), "strata_rows": len(strata), "output_root": _rel(output_root), "proceed_to_stage21": gate["proceed_to_stage21_from_development_evidence"]}, sort_keys=True))


def _load_prediction_frame() -> pd.DataFrame:
    row_key = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
    predictions = pd.read_parquet(MODEL_ROOT / "saved_predictions.parquet")
    labels = pd.read_parquet(STAGE3_ROOT / "labels.parquet", columns=[*row_key, "forward_excess_return"])
    features = pd.read_parquet(
        FEATURE_ROOT / "market_lag_features.parquet",
        columns=[*row_key, "no_news_flag", "provider_truncation_risk_flag", "aligned_news_count"],
    )
    frame = predictions.merge(labels, on=row_key, how="inner", validate="many_to_one").merge(features, on=row_key, how="inner", validate="many_to_one")
    frame = frame.rename(columns={"forward_excess_return": "target", "aligned_news_count": "article_count"})
    return frame


def _compute_metrics(frame: pd.DataFrame, group_columns: list[str]) -> pd.DataFrame:
    working = frame.copy()
    working["error"] = working["prediction"].astype("float64") - working["target"].astype("float64")
    working["squared_error"] = working["error"] ** 2
    working["absolute_error"] = working["error"].abs()
    records: list[dict[str, Any]] = []
    for keys, group in working.groupby(group_columns, sort=True, observed=True):
        if not isinstance(keys, tuple):
            keys = (keys,)
        record = dict(zip(group_columns, keys))
        target = group["target"].astype("float64")
        denominator = float(np.sum(target**2))
        sse = float(group["squared_error"].sum())
        record.update(
            {
                "row_count": int(len(group)),
                "target_mean": float(target.mean()),
                "prediction_mean": float(group["prediction"].mean()),
                "mse": float(group["squared_error"].mean()),
                "rmse": float(np.sqrt(group["squared_error"].mean())),
                "mae": float(group["absolute_error"].mean()),
                "r2_oos_zero_baseline": float("nan") if denominator == 0.0 else 1.0 - (sse / denominator),
            }
        )
        records.append(record)
    return pd.DataFrame.from_records(records)


def _compute_train_validation_gaps(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, group in metrics[metrics["split_role"].isin(["train", "validation"])].groupby(["model_id", "horizon_id", "fold_id"], sort=True):
        model_id, horizon_id, fold_id = keys
        by_role = group.set_index("split_role")
        if "train" not in by_role.index or "validation" not in by_role.index:
            continue
        for metric in ["rmse", "mae"]:
            train_value = float(by_role.loc["train", metric])
            validation_value = float(by_role.loc["validation", metric])
            rows.append(
                {
                    "model_id": model_id,
                    "horizon_id": horizon_id,
                    "fold_id": fold_id,
                    "metric": metric,
                    "train_value": train_value,
                    "validation_value": validation_value,
                    "validation_minus_train": validation_value - train_value,
                    "validation_to_train_ratio": float("inf") if train_value == 0.0 else validation_value / train_value,
                    "gap_flag": bool(validation_value > train_value * 1.25),
                }
            )
    return pd.DataFrame.from_records(rows)


def _compute_fold_dispersion(metrics: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for keys, group in metrics.groupby(["split_role", "model_id", "horizon_id"], sort=True):
        split_role, model_id, horizon_id = keys
        for metric in ["rmse", "mae"]:
            values = group[metric].astype("float64")
            records.append(
                {
                    "split_role": split_role,
                    "model_id": model_id,
                    "horizon_id": horizon_id,
                    "metric": metric,
                    "fold_count": int(values.count()),
                    "mean": float(values.mean()),
                    "std": float(values.std(ddof=1)) if values.count() > 1 else 0.0,
                    "min": float(values.min()),
                    "max": float(values.max()),
                }
            )
    return pd.DataFrame.from_records(records)


def _compute_horizon_stability(metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, group in metrics.groupby(["split_role", "fold_id", "horizon_id"], sort=True):
        split_role, fold_id, horizon_id = keys
        by_model = group.set_index("model_id")
        if LINEAR_MODEL not in by_model.index or XGB_MODEL not in by_model.index:
            continue
        rmse_delta = float(by_model.loc[XGB_MODEL, "rmse"] - by_model.loc[LINEAR_MODEL, "rmse"])
        mae_delta = float(by_model.loc[XGB_MODEL, "mae"] - by_model.loc[LINEAR_MODEL, "mae"])
        rows.append(
            {
                "split_role": split_role,
                "fold_id": fold_id,
                "horizon_id": horizon_id,
                "rmse_delta_xgb_minus_linear": rmse_delta,
                "mae_delta_xgb_minus_linear": mae_delta,
                "rmse_improves": bool(rmse_delta < 0.0),
                "mae_improves": bool(mae_delta < 0.0),
                "both_primary_metrics_improve": bool(rmse_delta < 0.0 and mae_delta < 0.0),
                "one_sided_improvement": bool((rmse_delta < 0.0) != (mae_delta < 0.0)),
            }
        )
    fold_level = pd.DataFrame.from_records(rows)
    if fold_level.empty:
        return fold_level
    summary = (
        fold_level.groupby(["split_role", "horizon_id"], sort=True)
        .agg(
            fold_count=("fold_id", "nunique"),
            mean_rmse_delta_xgb_minus_linear=("rmse_delta_xgb_minus_linear", "mean"),
            mean_mae_delta_xgb_minus_linear=("mae_delta_xgb_minus_linear", "mean"),
            rmse_improvement_rate=("rmse_improves", "mean"),
            mae_improvement_rate=("mae_improves", "mean"),
            both_metric_improvement_rate=("both_primary_metrics_improve", "mean"),
            one_sided_improvement_rate=("one_sided_improvement", "mean"),
        )
        .reset_index()
    )
    return summary


def _compute_strata_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    working = frame.copy()
    working["news_stratum"] = np.where(working["no_news_flag"].astype(bool), "no_news", "news_rich")
    working["truncation_stratum"] = np.where(working["provider_truncation_risk_flag"].astype(bool), "truncation_risk", "no_truncation_flag")
    working["article_count"] = working["article_count"].fillna(0).astype("int64")
    working["article_count_stratum"] = pd.cut(working["article_count"], bins=[-1, 0, 2, np.inf], labels=["articles_0", "articles_1_2", "articles_3_plus"])
    records: list[pd.DataFrame] = []
    for stratum_column in ["news_stratum", "truncation_stratum", "article_count_stratum"]:
        metrics = _compute_metrics(working, ["split_role", "horizon_id", "model_id", stratum_column])
        metrics = metrics.rename(columns={stratum_column: "stratum_value"})
        metrics["stratum_type"] = stratum_column
        metrics["provider_completeness_claim"] = False
        records.append(metrics)
    return pd.concat(records, ignore_index=True)


def _diagnostic_gate(metrics: pd.DataFrame, gaps: pd.DataFrame, horizon_stability: pd.DataFrame) -> dict[str, Any]:
    validation = metrics[metrics["split_role"] == "validation"]
    validation_finite = bool(np.isfinite(validation[["rmse", "mae"]].to_numpy()).all())
    xgb_validation = horizon_stability[horizon_stability["split_role"] == "validation"] if not horizon_stability.empty else pd.DataFrame()
    return {
        "status": "passed_with_cautions" if validation_finite else "blocked_nonfinite_validation_metrics",
        "proceed_to_stage21_from_development_evidence": validation_finite,
        "decision_basis": "development_validation_metrics_only; lockbox metrics are recorded but must not guide tuning",
        "validation_metric_rows": int(len(validation)),
        "train_validation_gap_flags": int(gaps["gap_flag"].sum()) if not gaps.empty else 0,
        "xgboost_validation_both_metric_improvement_rate_mean": None if xgb_validation.empty else float(xgb_validation["both_metric_improvement_rate"].mean()),
        "lockbox_tuning": False,
        "promotion_claim": False,
    }


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
