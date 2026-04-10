"""CLI entry point for comparing related run summaries as ablations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from src.models.ablation_runner import build_ablation_summary, ensure_run_summaries_comparable, load_run_summary
from src.utils.config_loader import load_project_settings
from src.utils.io_utils import write_json, write_parquet
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare related run summaries as ablations.")
    parser.add_argument("--run-summaries", required=True, help="Comma-separated run summary JSON paths.")
    parser.add_argument("--partition", default="test")
    parser.add_argument("--metric-name", default="rmse")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--log-level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)

    summary_paths = [Path(item.strip()) for item in args.run_summaries.split(",") if item.strip()]
    run_summaries = [load_run_summary(path) for path in summary_paths]
    ensure_run_summaries_comparable(run_summaries)
    ablation_df = build_ablation_summary(
        [str(path) for path in summary_paths],
        partition=args.partition,
        metric_name=args.metric_name,
    )

    output_dir = Path(args.output_dir) if args.output_dir else settings.project_paths.reports_dir / "ablation_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    if not ablation_df.empty:
        write_parquet(ablation_df, output_dir / "ablation_summary.parquet", index=False)
    summary = {
        "partition": args.partition,
        "metric_name": args.metric_name,
        "run_summaries": [str(path.resolve()) for path in summary_paths],
        "row_count": int(len(ablation_df)),
    }
    write_json(summary, output_dir / "ablation_summary.json")
    logger.info("Ablation comparison completed for %s run summaries.", len(summary_paths))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
