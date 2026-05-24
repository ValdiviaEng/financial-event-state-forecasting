"""Generate Stage 10C local model-output packets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from event_state_forecasting.stage10.prediction_outputs import Stage10CInputs, Stage10CPacketError, generate_stage10c_prediction_packet


PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEATURE_VERSION = "phase1_top50__stage2_dataset_v1__cw_20240401_20260213__src_d26bdc8584c7__rows_6868e3b80086__stage3_features_labels_v1"
SPLIT_VERSION = f"{FEATURE_VERSION}__stage4_splits_v1"
STAGE5_VERSION = f"{SPLIT_VERSION}__stage5_models_v1"
STAGE6_VERSION = f"{STAGE5_VERSION}__stage6_reporting_v1"
DEFAULT_FEATURE_ROOT = PROJECT_ROOT / "data" / "features" / "phase1_top50" / FEATURE_VERSION
DEFAULT_MODEL_ROOT = PROJECT_ROOT / "data" / "models" / "phase1_top50" / STAGE5_VERSION
DEFAULT_EVALUATION_ROOT = PROJECT_ROOT / "data" / "benchmark_runs" / "phase1_top50" / STAGE6_VERSION
DEFAULT_OUTPUT_BASE_ROOT = PROJECT_ROOT / "data" / "prediction_outputs" / "phase1_top50"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a Stage 10C local model-output packet from Stage 5 saved predictions.")
    parser.add_argument("--model-root", type=Path, default=DEFAULT_MODEL_ROOT)
    parser.add_argument("--feature-root", type=Path, default=DEFAULT_FEATURE_ROOT)
    parser.add_argument("--evaluation-root", type=Path, default=DEFAULT_EVALUATION_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_BASE_ROOT, help="Prediction-output family root; the CLI creates a versioned child packet.")
    parser.add_argument("--data-cutoff", default=None, help="Optional max as-of date to extract from saved predictions.")
    parser.add_argument("--run-date", default=None, help="Optional run date for deterministic packet names in tests or reruns.")
    parser.add_argument("--allow-overwrite", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = generate_stage10c_prediction_packet(
            Stage10CInputs(
                model_root=args.model_root,
                feature_root=args.feature_root,
                evaluation_root=args.evaluation_root,
                output_base_root=args.output_root,
                data_cutoff=args.data_cutoff,
                run_date=args.run_date,
                allow_overwrite=args.allow_overwrite,
            )
        )
    except Stage10CPacketError as exc:
        print(f"STAGE10C_PREDICTION_OUTPUTS_FAILED: {exc}", file=sys.stderr)
        return 2

    summary = {
        "status": manifest["stage10c_status"],
        "benchmark_claim": manifest["benchmark_claim"],
        "trading_signal_approved": manifest["trading_signal_approved"],
        "artifact_root": manifest["identity"]["artifact_root"],
        "data_cutoff": manifest["identity"]["data_cutoff"],
        "model_output_rows": manifest["counts"]["model_output_rows"],
        "top10_primary_rows": manifest["counts"]["top10_primary_rows"],
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("STAGE10C PREDICTION OUTPUT PACKET")
        for key, value in summary.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
