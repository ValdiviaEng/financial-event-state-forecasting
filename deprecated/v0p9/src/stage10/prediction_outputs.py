"""Stage 10C local model-output packet generation and validation."""

from __future__ import annotations

import html
import json
import math
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd


SCHEMA_VERSION = "prediction_outputs_v1"
EVENT_STATE_MODEL_ID = "event_state_gated_fusion"
HORIZON_ORDER = ("1d", "5d", "10d", "20d", "60d")
TOP_N = 10
NEWS_SNIPPET_LIMIT = 240
NEWS_ITEMS_PER_ROW = 3
TRAJECTORY_HISTORY_DAYS = 21
REQUIRED_OUTPUT_FILES = {
    "manifest": "prediction_output_manifest.json",
    "model_outputs_parquet": "model_outputs.parquet",
    "model_outputs_csv": "model_outputs.csv",
    "top10_primary_parquet": "top10_primary_event_state.parquet",
    "top10_primary_csv": "top10_primary_event_state.csv",
    "top10_delta_parquet": "top10_delta_over_market.parquet",
    "top10_delta_csv": "top10_delta_over_market.csv",
    "cross_horizon_parquet": "cross_horizon_diagnostic.parquet",
    "cross_horizon_csv": "cross_horizon_diagnostic.csv",
    "relevant_news_parquet": "relevant_news_context.parquet",
    "relevant_news_csv": "relevant_news_context.csv",
    "trajectory_points_parquet": "trajectory_points.parquet",
    "trajectory_points_csv": "trajectory_points.csv",
    "limitations": "limitations.json",
    "report": "report.html",
    "validation_report": "validation_report.json",
}


class Stage10CPacketError(RuntimeError):
    """Raised when Stage 10C packet generation or validation fails."""


@dataclass(frozen=True, slots=True)
class Stage10CInputs:
    model_root: Path
    feature_root: Path
    evaluation_root: Path
    output_base_root: Path
    data_cutoff: str | None = None
    run_date: str | None = None
    allow_overwrite: bool = False


def generate_stage10c_prediction_packet(inputs: Stage10CInputs) -> dict[str, Any]:
    model_root = inputs.model_root
    feature_root = inputs.feature_root
    evaluation_root = inputs.evaluation_root
    stage5_manifest = load_json(model_root / "model_manifest.json")
    evaluation_manifest = load_json(evaluation_root / "evaluation_manifest.json")
    comparison_summary = load_json(evaluation_root / "comparison_summary.json")
    selected_market_hurdles = extract_selected_market_hurdles(evaluation_manifest)

    predictions = pd.read_parquet(model_root / "saved_predictions.parquet")
    snapshot_date = resolve_snapshot_date(predictions, inputs.data_cutoff)
    snapshot = select_snapshot_predictions(predictions, snapshot_date)
    model_outputs = build_model_outputs(snapshot, selected_market_hurdles, feature_root)

    run_date = inputs.run_date or datetime.now(UTC).date().isoformat()
    output_root = build_output_root(
        inputs.output_base_root,
        run_date=run_date,
        data_cutoff=snapshot_date,
        stage5_artifact_version=str(stage5_manifest["identity"]["artifact_version"]),
        row_universe_digest=str(stage5_manifest["identity"]["row_universe_digest"]),
    )
    prepare_output_root(output_root, allow_overwrite=inputs.allow_overwrite)

    top10_primary = build_top10_primary(model_outputs)
    top10_delta = build_top10_delta(model_outputs)
    cross_horizon = build_cross_horizon_diagnostic(model_outputs)
    relevant_news = build_relevant_news_context(top10_primary, feature_root)
    trajectory_points = build_trajectory_points(top10_primary, feature_root)
    limitations = build_limitations_payload(comparison_summary, evaluation_manifest)

    paths = write_packet_files(
        output_root=output_root,
        model_outputs=model_outputs,
        top10_primary=top10_primary,
        top10_delta=top10_delta,
        cross_horizon=cross_horizon,
        relevant_news=relevant_news,
        trajectory_points=trajectory_points,
        limitations=limitations,
    )
    manifest = build_manifest(
        output_root=output_root,
        paths=paths,
        inputs=inputs,
        stage5_manifest=stage5_manifest,
        evaluation_manifest=evaluation_manifest,
        comparison_summary=comparison_summary,
        snapshot_date=snapshot_date,
        model_outputs=model_outputs,
        top10_primary=top10_primary,
        top10_delta=top10_delta,
        cross_horizon=cross_horizon,
        relevant_news=relevant_news,
        trajectory_points=trajectory_points,
        run_date=run_date,
    )
    write_json(output_root / REQUIRED_OUTPUT_FILES["manifest"], manifest)
    write_report(output_root / REQUIRED_OUTPUT_FILES["report"], manifest, top10_primary, top10_delta, cross_horizon, limitations)
    validation = validate_stage10c_packet(output_root)
    write_json(output_root / REQUIRED_OUTPUT_FILES["validation_report"], validation)
    if validation["status"] != "passed":
        raise Stage10CPacketError(f"Stage 10C packet validation failed: {validation['blockers']}")
    return manifest


def resolve_snapshot_date(predictions: pd.DataFrame, data_cutoff: str | None) -> str:
    if "as_of_date" not in predictions.columns:
        raise Stage10CPacketError("saved predictions missing as_of_date")
    dates = predictions["as_of_date"].astype(str)
    eligible = dates if data_cutoff is None else dates[dates <= str(data_cutoff)]
    if eligible.empty:
        raise Stage10CPacketError("no saved predictions at or before requested data cutoff")
    return str(eligible.max())


def select_snapshot_predictions(predictions: pd.DataFrame, snapshot_date: str) -> pd.DataFrame:
    required = {
        "benchmark_family_id",
        "canonical_ticker",
        "as_of_date",
        "horizon_id",
        "fold_id",
        "split_role",
        "model_id",
        "model_family",
        "branch",
        "dataset_version",
        "feature_artifact_version",
        "split_artifact_version",
        "stage5_artifact_version",
        "prediction",
    }
    missing = required - set(predictions.columns)
    if missing:
        raise Stage10CPacketError(f"saved predictions missing columns: {sorted(missing)}")
    snapshot = predictions[predictions["as_of_date"].astype(str) == snapshot_date].copy()
    if snapshot.empty:
        raise Stage10CPacketError("snapshot has no saved predictions")
    snapshot["_fold_order"] = snapshot["fold_id"].map(fold_sort_key)
    snapshot = snapshot.sort_values(
        ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id", "model_id", "_fold_order"],
        ascending=[True, True, True, True, True, False],
    )
    dedupe_columns = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id", "model_id"]
    return snapshot.drop_duplicates(dedupe_columns, keep="first").drop(columns=["_fold_order"])


def build_model_outputs(snapshot: pd.DataFrame, selected_market_hurdles: Mapping[str, str], feature_root: Path) -> pd.DataFrame:
    event_rows = snapshot[snapshot["model_id"] == EVENT_STATE_MODEL_ID].copy()
    if event_rows.empty:
        raise Stage10CPacketError(f"missing required event-state model: {EVENT_STATE_MODEL_ID}")
    baseline_frames = []
    for horizon_id, model_id in selected_market_hurdles.items():
        horizon_baseline = snapshot[(snapshot["horizon_id"] == horizon_id) & (snapshot["model_id"] == model_id)].copy()
        if horizon_baseline.empty:
            raise Stage10CPacketError(f"missing selected market hurdle {model_id} for {horizon_id}")
        baseline_frames.append(horizon_baseline)
    baseline_rows = pd.concat(baseline_frames, ignore_index=True)
    keys = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
    merged = event_rows.merge(
        baseline_rows.loc[:, [*keys, "model_id", "prediction"]].rename(
            columns={"model_id": "market_hurdle_model_id", "prediction": "market_hurdle_prediction"}
        ),
        on=keys,
        how="inner",
    )
    if len(merged) != len(event_rows):
        raise Stage10CPacketError("event-state rows did not fully align to selected market hurdles")
    event_features = pd.read_parquet(
        feature_root / "event_state_features.parquet",
        columns=[
            *keys,
            "stage3_aligned_news_count",
            "provider_empty_feed_flag",
            "provider_truncation_risk_flag",
            "minutes_since_latest_aligned_article",
            "no_news_flag",
            "empty_event_state_flag",
        ],
    )
    market_features = pd.read_parquet(feature_root / "market_features.parquet", columns=[*keys, "market_close"])
    labels = pd.read_parquet(
        feature_root / "labels.parquet",
        columns=[*keys, "label_window_start", "label_window_end", "forward_excess_return", "label_available_flag"],
    )
    merged = merged.merge(event_features, on=keys, how="left").merge(market_features, on=keys, how="left").merge(labels, on=keys, how="left")
    merged = merged.rename(
        columns={
            "model_id": "event_state_model_id",
            "model_family": "event_state_model_family",
            "branch": "event_state_branch",
            "prediction": "event_state_prediction",
            "forward_excess_return": "realized_forward_excess_return",
        }
    )
    merged["row_role"] = np.where(merged["split_role"].isin(["validation", "lockbox"]), "historical_prediction", "diagnostic_only")
    merged["not_trading_advice"] = True
    merged["not_benchmark_result"] = True
    merged["not_stage6_reinterpretation"] = True
    merged["trading_signal_approved"] = False
    merged["service_api_scope"] = False
    merged["forecast_candidate_approved"] = False
    merged["delta_over_market_hurdle"] = merged["event_state_prediction"] - merged["market_hurdle_prediction"]
    merged = assign_rank_columns(merged)
    merged["cross_horizon_score"] = merged.groupby("canonical_ticker")["event_state_percentile_by_horizon"].transform("mean")
    merged["cross_horizon_delta_score"] = merged.groupby("canonical_ticker")["delta_percentile_by_horizon"].transform("mean")
    output_columns = [
        "benchmark_family_id",
        "canonical_ticker",
        "as_of_date",
        "horizon_id",
        "row_role",
        "split_role",
        "fold_id",
        "event_state_model_id",
        "event_state_model_family",
        "event_state_branch",
        "event_state_prediction",
        "market_hurdle_model_id",
        "market_hurdle_prediction",
        "delta_over_market_hurdle",
        "event_state_rank",
        "delta_rank",
        "event_state_percentile_by_horizon",
        "delta_percentile_by_horizon",
        "cross_horizon_score",
        "cross_horizon_delta_score",
        "dataset_version",
        "feature_artifact_version",
        "split_artifact_version",
        "stage5_artifact_version",
        "label_window_start",
        "label_window_end",
        "realized_forward_excess_return",
        "label_available_flag",
        "market_close",
        "stage3_aligned_news_count",
        "provider_empty_feed_flag",
        "provider_truncation_risk_flag",
        "minutes_since_latest_aligned_article",
        "no_news_flag",
        "empty_event_state_flag",
        "not_trading_advice",
        "not_benchmark_result",
        "not_stage6_reinterpretation",
        "trading_signal_approved",
        "service_api_scope",
        "forecast_candidate_approved",
    ]
    return merged.loc[:, output_columns].sort_values(["horizon_id", "event_state_rank", "canonical_ticker"], key=horizon_sort_values)


def assign_rank_columns(frame: pd.DataFrame) -> pd.DataFrame:
    ranked = frame.copy()
    ranked = ranked.sort_values(["horizon_id", "event_state_prediction", "canonical_ticker"], ascending=[True, False, True])
    ranked["event_state_rank"] = ranked.groupby("horizon_id").cumcount() + 1
    ranked = ranked.sort_values(["horizon_id", "delta_over_market_hurdle", "canonical_ticker"], ascending=[True, False, True])
    ranked["delta_rank"] = ranked.groupby("horizon_id").cumcount() + 1
    horizon_counts = ranked.groupby("horizon_id")["canonical_ticker"].transform("count")
    ranked["event_state_percentile_by_horizon"] = (horizon_counts - ranked["event_state_rank"] + 1) / horizon_counts
    ranked["delta_percentile_by_horizon"] = (horizon_counts - ranked["delta_rank"] + 1) / horizon_counts
    return ranked


def build_top10_primary(model_outputs: pd.DataFrame) -> pd.DataFrame:
    frame = model_outputs[model_outputs["event_state_rank"] <= TOP_N].copy()
    frame["view_id"] = "primary_event_state_score"
    frame["view_priority"] = 1
    frame["ranking_caveat"] = "Per-horizon event-state model output; not trading advice and not a benchmark result."
    return frame.sort_values(["horizon_id", "event_state_rank", "canonical_ticker"], key=horizon_sort_values)


def build_top10_delta(model_outputs: pd.DataFrame) -> pd.DataFrame:
    frame = model_outputs[model_outputs["delta_rank"] <= TOP_N].copy()
    frame["view_id"] = "secondary_delta_over_market_hurdle"
    frame["view_priority"] = 2
    frame["ranking_caveat"] = "Delta over selected market hurdle is secondary model-comparison context, not model superiority proof."
    return frame.sort_values(["horizon_id", "delta_rank", "canonical_ticker"], key=horizon_sort_values)


def build_cross_horizon_diagnostic(model_outputs: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        model_outputs.groupby("canonical_ticker", as_index=False)
        .agg(
            benchmark_family_id=("benchmark_family_id", "first"),
            as_of_date=("as_of_date", "first"),
            row_role=("row_role", "first"),
            split_role=("split_role", "first"),
            horizon_count=("horizon_id", "nunique"),
            mean_event_state_prediction=("event_state_prediction", "mean"),
            mean_delta_over_market_hurdle=("delta_over_market_hurdle", "mean"),
            cross_horizon_score=("cross_horizon_score", "first"),
            cross_horizon_delta_score=("cross_horizon_delta_score", "first"),
            provider_truncation_risk_any=("provider_truncation_risk_flag", "max"),
            no_news_any=("no_news_flag", "max"),
        )
        .sort_values(["cross_horizon_score", "canonical_ticker"], ascending=[False, True])
    )
    grouped["cross_horizon_rank"] = np.arange(1, len(grouped) + 1)
    grouped["view_id"] = "tertiary_cross_horizon_diagnostic"
    grouped["view_priority"] = 3
    grouped["ranking_caveat"] = "Cross-horizon aggregation is diagnostic only and must not be treated as a trading score."
    grouped["not_trading_advice"] = True
    grouped["not_benchmark_result"] = True
    return grouped.head(TOP_N)


def build_relevant_news_context(top10_primary: pd.DataFrame, feature_root: Path) -> pd.DataFrame:
    keys = ["benchmark_family_id", "canonical_ticker", "as_of_date", "horizon_id"]
    event_features = pd.read_parquet(
        feature_root / "event_state_features.parquet",
        columns=[*keys, "aligned_article_ids", "no_news_flag", "provider_truncation_risk_flag", "stage3_aligned_news_count"],
    )
    article_table = pd.read_parquet(feature_root / "aligned_news.parquet")
    articles = {str(row.article_id): row for row in article_table.itertuples(index=False)}
    selected = top10_primary.loc[:, [*keys, "event_state_rank"]].merge(event_features, on=keys, how="left")
    records: list[dict[str, Any]] = []
    for row in selected.sort_values(["horizon_id", "event_state_rank", "canonical_ticker"], key=horizon_sort_values).itertuples(index=False):
        article_ids = split_article_ids(getattr(row, "aligned_article_ids", None))[:NEWS_ITEMS_PER_ROW]
        if not article_ids:
            records.append(news_record(row, None, None, context_status="no_aligned_news"))
            continue
        for rank, article_id in enumerate(article_ids, start=1):
            article = articles.get(article_id)
            records.append(news_record(row, rank, article, article_id=article_id, context_status="aligned_article_found" if article else "article_id_not_found"))
    return pd.DataFrame.from_records(records)


def news_record(row: Any, rank: int | None, article: Any | None, *, article_id: str | None = None, context_status: str) -> dict[str, Any]:
    return {
        "benchmark_family_id": row.benchmark_family_id,
        "canonical_ticker": row.canonical_ticker,
        "as_of_date": row.as_of_date,
        "horizon_id": row.horizon_id,
        "event_state_rank": int(row.event_state_rank),
        "news_context_rank": rank,
        "context_status": context_status,
        "article_id": article_id if article is None else str(article.article_id),
        "published_timestamp": None if article is None else str(article.published_timestamp),
        "roll_forward_reason": None if article is None else str(article.roll_forward_reason),
        "title_snippet": None if article is None else clip_text(getattr(article, "title", None)),
        "summary_snippet": None if article is None else clip_text(getattr(article, "summary", None)),
        "text_hash": None if article is None else str(article.text_hash),
        "url_included": False,
        "llm_summary_used": False,
        "no_news_flag": bool(getattr(row, "no_news_flag", False)),
        "provider_truncation_risk_flag": bool(getattr(row, "provider_truncation_risk_flag", False)),
        "stage3_aligned_news_count": int(getattr(row, "stage3_aligned_news_count", 0) or 0),
    }


def build_trajectory_points(top10_primary: pd.DataFrame, feature_root: Path) -> pd.DataFrame:
    tickers = sorted(set(str(value) for value in top10_primary["canonical_ticker"]))
    snapshot_date = str(top10_primary["as_of_date"].max())
    market = pd.read_parquet(feature_root / "market_features.parquet")
    market = market[market["canonical_ticker"].isin(tickers) & (market["as_of_date"].astype(str) <= snapshot_date)]
    market = market.drop_duplicates(["canonical_ticker", "as_of_date"]).sort_values(["canonical_ticker", "as_of_date"])
    history = market.groupby("canonical_ticker", as_index=False, group_keys=False).tail(TRAJECTORY_HISTORY_DAYS).copy()
    history["point_type"] = "observed_close"
    history["horizon_id"] = None
    history["event_state_prediction"] = np.nan
    history["market_hurdle_prediction"] = np.nan
    history["delta_over_market_hurdle"] = np.nan
    history["label_window_end"] = None
    history["realized_forward_excess_return"] = np.nan
    history["projected_price_path"] = False

    markers = top10_primary.copy()
    markers["point_type"] = "forecast_marker"
    markers["projected_price_path"] = False
    marker_columns = [
        "benchmark_family_id",
        "canonical_ticker",
        "as_of_date",
        "horizon_id",
        "point_type",
        "market_close",
        "event_state_prediction",
        "market_hurdle_prediction",
        "delta_over_market_hurdle",
        "label_window_end",
        "realized_forward_excess_return",
        "projected_price_path",
    ]
    history_columns = [
        "benchmark_family_id",
        "canonical_ticker",
        "as_of_date",
        "horizon_id",
        "point_type",
        "market_close",
        "event_state_prediction",
        "market_hurdle_prediction",
        "delta_over_market_hurdle",
        "label_window_end",
        "realized_forward_excess_return",
        "projected_price_path",
    ]
    return pd.concat([history.loc[:, history_columns], markers.loc[:, marker_columns]], ignore_index=True).sort_values(
        ["canonical_ticker", "as_of_date", "point_type", "horizon_id"], key=horizon_sort_values
    )


def build_limitations_payload(comparison_summary: Mapping[str, Any], evaluation_manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "artifact_type": "stage10c_limitations",
        "artifact_schema_version": SCHEMA_VERSION,
        "status": "active_limitations",
        "non_claims": [
            "not_trading_advice",
            "not_buy_sell_signal",
            "not_price_target",
            "not_benchmark_result",
            "not_stage6_reinterpretation",
            "not_provider_completeness_claim",
            "not_service_api_dashboard",
            "not_persisted_inference_package",
        ],
        "stage6_context": {
            "result_class": comparison_summary.get("result_class"),
            "result_reason": comparison_summary.get("result_reason"),
            "comparability_classification": evaluation_manifest.get("comparability_classification"),
            "selected_market_hurdles": evaluation_manifest.get("selected_market_hurdles", {}),
        },
        "row_semantics": "historical_prediction rows extracted from Stage 5 saved predictions; forecast_candidate semantics remain unapproved for feature-only future rows.",
        "sensitive_artifact_policy": "Packets exclude raw provider ledgers, unsanitized request URLs, API keys, provider logs, and raw secrets.",
        "trajectory_policy": "Forecast markers are model-output markers on historical price context; no projected price path or fan chart is generated.",
    }


def write_packet_files(
    *,
    output_root: Path,
    model_outputs: pd.DataFrame,
    top10_primary: pd.DataFrame,
    top10_delta: pd.DataFrame,
    cross_horizon: pd.DataFrame,
    relevant_news: pd.DataFrame,
    trajectory_points: pd.DataFrame,
    limitations: Mapping[str, Any],
) -> dict[str, Path]:
    paths = {name: output_root / filename for name, filename in REQUIRED_OUTPUT_FILES.items()}
    write_table_pair(model_outputs, paths["model_outputs_parquet"], paths["model_outputs_csv"])
    write_table_pair(top10_primary, paths["top10_primary_parquet"], paths["top10_primary_csv"])
    write_table_pair(top10_delta, paths["top10_delta_parquet"], paths["top10_delta_csv"])
    write_table_pair(cross_horizon, paths["cross_horizon_parquet"], paths["cross_horizon_csv"])
    write_table_pair(relevant_news, paths["relevant_news_parquet"], paths["relevant_news_csv"])
    write_table_pair(trajectory_points, paths["trajectory_points_parquet"], paths["trajectory_points_csv"])
    write_json(paths["limitations"], limitations)
    return paths


def build_manifest(
    *,
    output_root: Path,
    paths: Mapping[str, Path],
    inputs: Stage10CInputs,
    stage5_manifest: Mapping[str, Any],
    evaluation_manifest: Mapping[str, Any],
    comparison_summary: Mapping[str, Any],
    snapshot_date: str,
    model_outputs: pd.DataFrame,
    top10_primary: pd.DataFrame,
    top10_delta: pd.DataFrame,
    cross_horizon: pd.DataFrame,
    relevant_news: pd.DataFrame,
    trajectory_points: pd.DataFrame,
    run_date: str,
) -> dict[str, Any]:
    return {
        "artifact_type": "stage10c_prediction_output_packet",
        "artifact_schema_version": SCHEMA_VERSION,
        "generated_at_utc": now_utc(),
        "stage10c_status": "stage10c_prediction_output_packet_created",
        "benchmark_claim": False,
        "trading_signal_approved": False,
        "service_api_scope": False,
        "provider_call_executed": False,
        "raw_data_mutated": False,
        "stage6_reinterpretation": False,
        "forecast_candidate_semantics_used": False,
        "row_role": "historical_prediction",
        "identity": {
            "artifact_version": output_root.name,
            "artifact_root": str(output_root),
            "run_date": run_date,
            "data_cutoff": snapshot_date,
            "input_stage5_artifact_version": stage5_manifest["identity"]["artifact_version"],
            "input_feature_artifact_version": stage5_manifest["identity"]["input_feature_artifact_version"],
            "input_split_artifact_version": stage5_manifest["identity"]["input_split_artifact_version"],
            "row_universe_digest": stage5_manifest["identity"]["row_universe_digest"],
        },
        "inputs": {
            "model_root": str(inputs.model_root),
            "feature_root": str(inputs.feature_root),
            "evaluation_root": str(inputs.evaluation_root),
            "saved_predictions": str(inputs.model_root / "saved_predictions.parquet"),
        },
        "counts": {
            "model_output_rows": int(len(model_outputs)),
            "top10_primary_rows": int(len(top10_primary)),
            "top10_delta_rows": int(len(top10_delta)),
            "cross_horizon_rows": int(len(cross_horizon)),
            "relevant_news_rows": int(len(relevant_news)),
            "trajectory_point_rows": int(len(trajectory_points)),
            "ticker_count": int(model_outputs["canonical_ticker"].nunique()),
            "horizon_count": int(model_outputs["horizon_id"].nunique()),
        },
        "ranking_policy": {
            "primary": "per_horizon_event_state_prediction_desc",
            "secondary": "per_horizon_delta_over_selected_market_hurdle_desc",
            "tertiary": "cross_horizon_score_diagnostic_only",
            "top_n": TOP_N,
        },
        "selected_market_hurdles": evaluation_manifest.get("selected_market_hurdles", {}),
        "stage6_context": {
            "result_class": comparison_summary.get("result_class"),
            "comparability_classification": evaluation_manifest.get("comparability_classification"),
        },
        "outputs": {name: str(path) for name, path in paths.items()},
        "non_claims": [
            "not_trading_advice",
            "not_buy_sell_signal",
            "not_price_target",
            "not_benchmark_result",
            "not_stage6_reinterpretation",
            "not_service_api_dashboard",
            "not_live_provider_call",
            "not_raw_data_mutation",
            "not_persisted_inference_package",
        ],
    }


def validate_stage10c_packet(output_root: Path) -> dict[str, Any]:
    blockers: list[str] = []
    paths = {name: output_root / filename for name, filename in REQUIRED_OUTPUT_FILES.items()}
    for name, path in paths.items():
        if name == "validation_report":
            continue
        if not path.exists():
            blockers.append(f"missing_{name}")
    manifest: dict[str, Any] = {}
    model_outputs = pd.DataFrame()
    top10_primary = pd.DataFrame()
    top10_delta = pd.DataFrame()
    cross_horizon = pd.DataFrame()
    relevant_news = pd.DataFrame()
    trajectory_points = pd.DataFrame()
    if not blockers:
        manifest = load_json(paths["manifest"])
        model_outputs = pd.read_parquet(paths["model_outputs_parquet"])
        top10_primary = pd.read_parquet(paths["top10_primary_parquet"])
        top10_delta = pd.read_parquet(paths["top10_delta_parquet"])
        cross_horizon = pd.read_parquet(paths["cross_horizon_parquet"])
        relevant_news = pd.read_parquet(paths["relevant_news_parquet"])
        trajectory_points = pd.read_parquet(paths["trajectory_points_parquet"])
        blockers.extend(validate_manifest(manifest))
        blockers.extend(validate_model_outputs(model_outputs))
        blockers.extend(validate_top10(top10_primary, "event_state_rank"))
        blockers.extend(validate_top10(top10_delta, "delta_rank"))
        if cross_horizon.empty:
            blockers.append("empty_cross_horizon_diagnostic")
        if bool(relevant_news.get("url_included", pd.Series(dtype=bool)).any()):
            blockers.append("relevant_news_includes_urls")
        if bool(relevant_news.get("llm_summary_used", pd.Series(dtype=bool)).any()):
            blockers.append("llm_summary_used")
        if bool(trajectory_points.get("projected_price_path", pd.Series(dtype=bool)).any()):
            blockers.append("projected_price_path_created")
        blockers.extend(validate_sensitive_exclusion(output_root))
    return {
        "artifact_type": "stage10c_completion_validation",
        "artifact_schema_version": SCHEMA_VERSION,
        "generated_at_utc": now_utc(),
        "status": "passed" if not blockers else "failed",
        "prediction_output_root": str(output_root),
        "benchmark_claim": False,
        "model_output_rows": int(len(model_outputs)),
        "top10_primary_rows": int(len(top10_primary)),
        "top10_delta_rows": int(len(top10_delta)),
        "cross_horizon_rows": int(len(cross_horizon)),
        "relevant_news_rows": int(len(relevant_news)),
        "trajectory_point_rows": int(len(trajectory_points)),
        "blockers": blockers,
    }


def validate_manifest(manifest: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if manifest.get("artifact_schema_version") != SCHEMA_VERSION:
        blockers.append("manifest_schema_mismatch")
    if manifest.get("stage10c_status") != "stage10c_prediction_output_packet_created":
        blockers.append("stage10c_status_not_created")
    for field in ["benchmark_claim", "trading_signal_approved", "service_api_scope", "provider_call_executed", "raw_data_mutated", "stage6_reinterpretation", "forecast_candidate_semantics_used"]:
        if manifest.get(field) is not False:
            blockers.append(f"manifest_{field}_not_false")
    if manifest.get("row_role") != "historical_prediction":
        blockers.append("manifest_row_role_not_historical_prediction")
    return blockers


def validate_model_outputs(model_outputs: pd.DataFrame) -> list[str]:
    blockers: list[str] = []
    required = {
        "canonical_ticker",
        "as_of_date",
        "horizon_id",
        "row_role",
        "event_state_prediction",
        "market_hurdle_prediction",
        "delta_over_market_hurdle",
        "event_state_rank",
        "delta_rank",
        "not_trading_advice",
        "not_benchmark_result",
        "not_stage6_reinterpretation",
        "trading_signal_approved",
        "service_api_scope",
        "forecast_candidate_approved",
    }
    missing = required - set(model_outputs.columns)
    if missing:
        blockers.append(f"model_outputs_missing_columns:{sorted(missing)}")
        return blockers
    if set(model_outputs["horizon_id"]) != set(HORIZON_ORDER):
        blockers.append("model_outputs_horizon_set_mismatch")
    if set(model_outputs["row_role"]) != {"historical_prediction"}:
        blockers.append("unexpected_row_role")
    if bool(model_outputs["trading_signal_approved"].any()):
        blockers.append("trading_signal_approved_in_model_outputs")
    if bool(model_outputs["service_api_scope"].any()):
        blockers.append("service_api_scope_in_model_outputs")
    if bool(model_outputs["forecast_candidate_approved"].any()):
        blockers.append("forecast_candidate_approved_in_model_outputs")
    numeric = model_outputs[["event_state_prediction", "market_hurdle_prediction", "delta_over_market_hurdle"]].to_numpy(dtype="float64")
    if not np.isfinite(numeric).all():
        blockers.append("non_finite_model_output_values")
    return blockers


def validate_top10(frame: pd.DataFrame, rank_column: str) -> list[str]:
    blockers: list[str] = []
    if frame.empty:
        return [f"empty_top10_{rank_column}"]
    if int(frame[rank_column].max()) > TOP_N:
        blockers.append(f"top10_{rank_column}_exceeds_limit")
    counts = frame.groupby("horizon_id").size().to_dict()
    for horizon_id in HORIZON_ORDER:
        if counts.get(horizon_id, 0) != TOP_N:
            blockers.append(f"top10_{rank_column}_{horizon_id}_count_mismatch")
    return blockers


def validate_sensitive_exclusion(output_root: Path) -> list[str]:
    blockers: list[str] = []
    prohibited_path_terms = ("ledger", "request_log", "provider_log", "raw_log")
    prohibited_text_terms = ("apikey=", "function=NEWS_SENTIMENT", "TIME_SERIES_DAILY_ADJUSTED")
    for path in output_root.rglob("*"):
        if not path.is_file():
            continue
        lower_name = path.name.lower()
        if any(term in lower_name for term in prohibited_path_terms):
            blockers.append(f"sensitive_artifact_name:{path.name}")
        if path.suffix.lower() not in {".json", ".csv", ".html", ".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in prohibited_text_terms:
            if term.lower() in text:
                blockers.append(f"sensitive_text_pattern:{term}:{path.name}")
    return sorted(set(blockers))


def extract_selected_market_hurdles(evaluation_manifest: Mapping[str, Any]) -> dict[str, str]:
    hurdles = evaluation_manifest.get("selected_market_hurdles")
    if not isinstance(hurdles, dict):
        raise Stage10CPacketError("evaluation manifest missing selected_market_hurdles")
    missing = [horizon for horizon in HORIZON_ORDER if horizon not in hurdles]
    if missing:
        raise Stage10CPacketError(f"selected market hurdles missing horizons: {missing}")
    return {horizon: str(hurdles[horizon]) for horizon in HORIZON_ORDER}


def build_output_root(output_base_root: Path, *, run_date: str, data_cutoff: str, stage5_artifact_version: str, row_universe_digest: str) -> Path:
    source_digest = payload_digest({"stage5_artifact_version": stage5_artifact_version, "data_cutoff": data_cutoff})[:12]
    row_digest = row_universe_digest[:12]
    stage5_digest = payload_digest(stage5_artifact_version)[:12]
    name = f"{run_date}__cutoff_{compact_date(data_cutoff)}__src_{source_digest}__rows_{row_digest}__stage5_{stage5_digest}__prediction_outputs_v1"
    return output_base_root / name


def prepare_output_root(output_root: Path, *, allow_overwrite: bool) -> None:
    if output_root.exists() and not allow_overwrite:
        raise Stage10CPacketError(f"output root already exists: {output_root}")
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)


def write_report(path: Path, manifest: Mapping[str, Any], top10_primary: pd.DataFrame, top10_delta: pd.DataFrame, cross_horizon: pd.DataFrame, limitations: Mapping[str, Any]) -> None:
    sections = [
        "<h1>Stage 10C Local Model-Output Packet</h1>",
        "<p><strong>Non-claims:</strong> not trading advice, not a benchmark result, not a Stage 6 reinterpretation, not a service/API/dashboard output.</p>",
        f"<p><strong>Data cutoff:</strong> {html.escape(str(manifest['identity']['data_cutoff']))}</p>",
        f"<p><strong>Stage 6 context:</strong> result class {html.escape(str(manifest['stage6_context']['result_class']))}; comparability {html.escape(str(manifest['stage6_context']['comparability_classification']))}.</p>",
        "<h2>Primary Per-Horizon Event-State Top 10</h2>",
        top10_primary.loc[:, ["horizon_id", "event_state_rank", "canonical_ticker", "event_state_prediction", "market_hurdle_model_id", "delta_over_market_hurdle", "provider_truncation_risk_flag", "no_news_flag"]].to_html(index=False, escape=True),
        "<h2>Secondary Delta Over Market Hurdle Top 10</h2>",
        top10_delta.loc[:, ["horizon_id", "delta_rank", "canonical_ticker", "event_state_prediction", "market_hurdle_prediction", "delta_over_market_hurdle"]].to_html(index=False, escape=True),
        "<h2>Tertiary Cross-Horizon Diagnostic</h2>",
        cross_horizon.to_html(index=False, escape=True),
        "<h2>Limitations</h2>",
        "<pre>" + html.escape(json.dumps(to_jsonable(limitations), indent=2, sort_keys=True)) + "</pre>",
    ]
    path.write_text("\n".join(["<!doctype html><html><head><meta charset='utf-8'><title>Stage 10C Report</title></head><body>", *sections, "</body></html>"]) + "\n", encoding="utf-8")


def write_table_pair(frame: pd.DataFrame, parquet_path: Path, csv_path: Path) -> None:
    frame.to_parquet(parquet_path, index=False)
    frame.to_csv(csv_path, index=False)


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(to_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise Stage10CPacketError(f"expected JSON object in {path}")
    return data


def split_article_ids(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return []
    return [item for item in str(value).split(";") if item]


def clip_text(value: Any, limit: int = NEWS_SNIPPET_LIMIT) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[: limit - 3] + "..."


def fold_sort_key(value: Any) -> int:
    text = str(value)
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def horizon_sort_key(value: Any) -> int:
    text = str(value)
    if text.endswith("d") and text[:-1].isdigit():
        return int(text[:-1])
    return 9999


def horizon_sort_values(values: pd.Series) -> pd.Series:
    if values.name == "horizon_id":
        return values.map(horizon_sort_key)
    return values


def compact_date(value: str) -> str:
    return str(value).replace("-", "")


def payload_digest(payload: Any) -> str:
    import hashlib

    text = json.dumps(to_jsonable(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def to_jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        return None if math.isnan(value) or math.isinf(value) else value
    if isinstance(value, np.bool_):
        return bool(value)
    return value
