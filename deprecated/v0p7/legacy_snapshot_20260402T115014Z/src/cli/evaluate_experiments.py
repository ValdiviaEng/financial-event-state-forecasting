"""CLI entry point for evaluating stored prediction files against labels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import cast

import pandas as pd

from src.models.metric_registry import evaluate_prediction_frame
from src.utils.config_loader import load_project_settings
from src.utils.io_utils import read_json, write_json, write_parquet
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate stored prediction files against a final modeling panel.")
    parser.add_argument("--panel-path", required=True)
    parser.add_argument("--run-summary", default=None)
    parser.add_argument("--prediction-files", default=None)
    parser.add_argument("--target-prefix", default="y_excess_ret")
    parser.add_argument("--horizons", default=None)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--log-level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)
    horizons = _parse_horizons(args.horizons, settings.get_config("labels").get("horizons", [1, 5, 20, 60]))
    target_columns = [f"{args.target_prefix}_{horizon}" for horizon in horizons]

    prediction_files = _resolve_prediction_files(args)
    if not prediction_files:
        parser.error("Provide either --run-summary or --prediction-files.")

    panel = pd.read_parquet(args.panel_path)
    available_targets = [column for column in target_columns if column in panel.columns]
    if not available_targets:
        parser.error("None of the requested target columns are present in the supplied panel.")
    label_frame = panel.loc[:, ["ticker", "date", *available_targets]].copy()

    output_dir = Path(args.output_dir) if args.output_dir else settings.project_paths.reports_dir / "evaluation_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    all_regression: list[pd.DataFrame] = []
    all_ranking: list[pd.DataFrame] = []
    evaluated_files: list[str] = []
    for prediction_path in prediction_files:
        predictions = pd.read_parquet(prediction_path)
        evaluation = evaluate_prediction_frame(predictions, cast(pd.DataFrame, label_frame), target_columns=available_targets)
        regression = evaluation["regression"]
        ranking = evaluation["ranking"]
        if not regression.empty:
            regression["prediction_file"] = str(prediction_path)
            all_regression.append(regression)
        if not ranking.empty:
            ranking["prediction_file"] = str(prediction_path)
            all_ranking.append(ranking)
        evaluated_files.append(str(prediction_path))

    regression_df = pd.concat(all_regression, ignore_index=True) if all_regression else pd.DataFrame()
    ranking_df = pd.concat(all_ranking, ignore_index=True) if all_ranking else pd.DataFrame()

    summary = {
        "panel_path": str(Path(args.panel_path).resolve()),
        "evaluated_files": evaluated_files,
        "target_columns": available_targets,
        "regression_row_count": int(len(regression_df)),
        "ranking_row_count": int(len(ranking_df)),
    }

    if not regression_df.empty:
        write_parquet(regression_df, output_dir / "regression_metrics.parquet", index=False)
    if not ranking_df.empty:
        write_parquet(ranking_df, output_dir / "ranking_metrics.parquet", index=False)
    write_json(summary, output_dir / "evaluation_summary.json")
    logger.info("Evaluation completed for %s prediction files.", len(evaluated_files))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


def _resolve_prediction_files(args: argparse.Namespace) -> list[Path]:
    if args.prediction_files:
        return [Path(item.strip()) for item in args.prediction_files.split(",") if item.strip()]
    if args.run_summary:
        summary = read_json(args.run_summary)
        return [Path(result["predictions_path"]) for result in summary.get("results", []) if result.get("predictions_path")]
    return []


def _parse_horizons(raw: str | None, default_horizons: list[int] | tuple[int, ...]) -> list[int]:
    if raw is None:
        return [int(value) for value in default_horizons]
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
