#!/usr/bin/env python3
"""Validate Stage 10C local prediction-output packet artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.stage10.prediction_outputs import validate_stage10c_packet  # noqa: E402


DEFAULT_BASE_ROOT = PROJECT_ROOT / "data" / "prediction_outputs" / "phase1_top50"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "manifests" / "stage10c_completion_validation_2026-05-23.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Stage 10C prediction-output packet artifacts.")
    parser.add_argument("--prediction-output-root", type=Path, default=None)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    packet_root = args.prediction_output_root or latest_packet_root(DEFAULT_BASE_ROOT)
    result = validate_stage10c_packet(packet_root)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["status"] != "passed":
        print("STAGE10C_COMPLETION_VALIDATION FAILED")
        for blocker in result["blockers"]:
            print(f"- {blocker}")
        return 1
    print("STAGE10C_COMPLETION_VALIDATION PASSED")
    print("model_output_rows:", result["model_output_rows"])
    print("top10_primary_rows:", result["top10_primary_rows"])
    return 0


def latest_packet_root(base_root: Path) -> Path:
    if not base_root.exists():
        raise RuntimeError(f"missing Stage 10C base root: {base_root}")
    candidates = [path for path in base_root.iterdir() if path.is_dir() and path.name.endswith("__prediction_outputs_v1")]
    if not candidates:
        raise RuntimeError(f"no Stage 10C packet roots found under {base_root}")
    return sorted(candidates, key=lambda path: path.name)[-1]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
