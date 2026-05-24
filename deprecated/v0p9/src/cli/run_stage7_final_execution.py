"""Create Stage 7 final-execution stub without all-data training output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from event_state_forecasting.stage7.artifacts import write_json
from event_state_forecasting.stage7.config import load_stage7_config
from event_state_forecasting.stage7.final_execution import build_final_execution_stub


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "stage7_final_execution" / "phase1_top50" / "stage7_final_execution_stub_v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create Stage 7 final-execution stub without live-use all-data training.")
    parser.add_argument("--stage7-config", type=Path, default=PROJECT_ROOT / "configs" / "stage7_contextual_bandit.yaml")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--run-all-data-training", action="store_true", help="Blocked unless future approval adds real training implementation.")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.run_all_data_training:
        print("STAGE7_FINAL_EXECUTION_BLOCKED: all-data training output is not approved for this run", file=sys.stderr)
        return 2
    if args.output_root.exists() and not args.allow_overwrite:
        print(f"STAGE7_FINAL_EXECUTION_BLOCKED: output root exists: {args.output_root}", file=sys.stderr)
        return 2
    args.output_root.mkdir(parents=True, exist_ok=True)
    config = load_stage7_config(args.stage7_config)
    manifest = build_final_execution_stub(args.output_root, config)
    manifest_path = args.output_root / "final_execution_stub.json"
    write_json(manifest_path, manifest)
    summary = {"status": manifest["status"], "artifact_root": str(args.output_root), "manifest": str(manifest_path)}
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("STAGE7 FINAL EXECUTION STUB")
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
