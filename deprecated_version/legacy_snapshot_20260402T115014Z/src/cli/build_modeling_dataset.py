"""CLI entry point for final modeling-dataset assembly."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from src.data.modeling_dataset import ModelingDatasetBuilder
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the final model-ready panel dataset.")
    parser.add_argument("--adjusted-prices-path", required=True)
    parser.add_argument("--benchmark-path", default=None)
    parser.add_argument("--event-state-path", default=None)
    parser.add_argument("--company-features-path", default=None)
    parser.add_argument("--dataset-version", default="panel_v1")
    parser.add_argument("--market-feature-version", default="v1")
    parser.add_argument("--label-version", default="v1")
    parser.add_argument("--event-state-version", default=None)
    parser.add_argument("--company-feature-version", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--log-level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    logger = configure_logging(log_level=args.log_level or settings.environment.default_log_level)
    builder = ModelingDatasetBuilder.from_settings(settings)

    if args.dry_run:
        summary = {
            "stage": "modeling_dataset_build",
            "dry_run": True,
            "dataset_version": args.dataset_version,
            "adjusted_prices_path": args.adjusted_prices_path,
            "benchmark_path": args.benchmark_path,
            "event_state_path": args.event_state_path,
            "company_features_path": args.company_features_path,
            "expected_panel_path": str(builder.panel_path(args.dataset_version)),
            "expected_manifest_path": str(builder.manifest_path(args.dataset_version)),
        }
        logger.info("Modeling dataset dry-run completed.")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    result = builder.build_from_files(
        adjusted_price_path=args.adjusted_prices_path,
        benchmark_path=args.benchmark_path,
        event_state_path=args.event_state_path,
        company_feature_path=args.company_features_path,
        dataset_version=args.dataset_version,
        market_feature_version=args.market_feature_version,
        label_version=args.label_version,
        event_state_version=args.event_state_version,
        company_feature_version=args.company_feature_version,
    )
    logger.info("Modeling dataset build completed for dataset_version=%s", args.dataset_version)
    print(json.dumps(_to_jsonable(result.as_dict()), indent=2, sort_keys=True))
    return 0


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
