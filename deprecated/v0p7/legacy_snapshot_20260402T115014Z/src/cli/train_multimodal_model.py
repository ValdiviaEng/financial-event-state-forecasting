"""CLI entry point for training multimodal event-state models."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

import pandas as pd

from src.models.trainer import train_multimodal_fold
from src.split.purged_embargo_splits import build_purged_walk_forward_splits
from src.utils.config_loader import load_project_settings
from src.utils.logging_setup import configure_logging


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train multimodal market + event-state models on the final panel.")
    parser.add_argument("--panel-path", required=True)
    parser.add_argument("--horizons", default=None)
    parser.add_argument("--target-prefix", default="y_excess_ret")
    parser.add_argument("--train-window", type=int, required=True)
    parser.add_argument("--validation-window", type=int, default=0)
    parser.add_argument("--test-window", type=int, required=True)
    parser.add_argument("--step-size", type=int, default=None)
    parser.add_argument("--max-splits", type=int, default=1)
    parser.add_argument("--embargo-days", type=int, default=None)
    parser.add_argument("--rolling", action="store_true")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--device", default=None)
    parser.add_argument("--create-dirs", action="store_true")
    parser.add_argument("--log-level", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    settings = load_project_settings(create_directories=args.create_dirs)
    labels_config = settings.get_config("labels")
    evaluation_config = settings.get_config("evaluation")
    training_config = settings.get_config("training")
    model_config = settings.get_config("model_multimodal")

    horizons = _parse_horizons(args.horizons, labels_config.get("horizons", [1, 5, 20, 60]))
    embargo_days = args.embargo_days
    if embargo_days is None:
        embargo_days = int(evaluation_config.get("validation", {}).get("embargo_trading_days", 0))

    panel = pd.read_parquet(args.panel_path)
    splits = build_purged_walk_forward_splits(
        panel,
        train_window=args.train_window,
        validation_window=args.validation_window,
        test_window=args.test_window,
        step_size=args.step_size,
        max_splits=args.max_splits,
        expanding=not args.rolling,
        horizons=tuple(horizons),
        embargo_days=embargo_days,
    )
    if not splits:
        parser.error("No walk-forward splits could be generated with the provided window settings.")

    run_id = args.run_id or f"multimodal_{uuid4().hex[:8]}"
    logger = configure_logging(
        log_level=args.log_level or settings.environment.default_log_level,
        run_id=run_id,
    )
    run_dir = settings.project_paths.run_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)

    flat_training_config = {
        **training_config.get("trainer", {}),
        **training_config.get("optimization", {}),
        **training_config.get("dataloader", {}),
    }
    if args.device is not None:
        flat_training_config["device"] = args.device

    results: list[dict[str, Any]] = []
    for split in splits:
        logger.info("Training multimodal split %s with %s train dates", split.split_id, len(split.train_dates))
        result = train_multimodal_fold(
            panel=panel,
            train_dates=split.train_dates,
            validation_dates=split.validation_dates,
            test_dates=split.test_dates,
            split_id=split.split_id,
            run_dir=run_dir,
            horizons=horizons,
            target_prefix=args.target_prefix,
            seed=int(settings.environment.default_random_seed),
            training_config=flat_training_config,
            model_config=model_config,
        )
        results.append(result.as_dict())

    summary = {
        "run_id": run_id,
        "panel_path": str(Path(args.panel_path).resolve()),
        "model_name": "multimodal_event_state",
        "horizons": horizons,
        "split_count": len(splits),
        "results": results,
    }
    summary_path = run_dir / "multimodal_training_summary.json"
    summary_path.write_text(json.dumps(_to_jsonable(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(_to_jsonable(summary), indent=2, sort_keys=True))
    return 0


def _parse_horizons(raw: str | None, default_horizons: list[int] | tuple[int, ...]) -> list[int]:
    if raw is None:
        return [int(value) for value in default_horizons]
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


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
