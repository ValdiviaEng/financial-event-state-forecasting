"""CLI for Stage 2 benchmark dataset materialization."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from event_state_forecasting.data.universe import DEFAULT_UNIVERSE_PATH
from event_state_forecasting.dataset.panel_builder import (
    DEFAULT_DATASET_OUTPUT_ROOT,
    DEFAULT_RAW_ALPHAVANTAGE_ROOT,
    DEFAULT_RAW_TWELVEDATA_ROOT,
    DEFAULT_STAGE1_MANIFEST,
    DEFAULT_STAGE1_OHLCV_MANIFEST,
    DEFAULT_STAGE2_CONTRACT_MANIFEST,
    DEFAULT_TWELVEDATA_AUDIT,
    FULL_WINDOW_FILENAME,
    PanelBuildError,
    build_stage2_benchmark_dataset,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the approved Stage 2 top-50 benchmark dataset artifacts.")
    parser.add_argument("--output-root", default=str(DEFAULT_DATASET_OUTPUT_ROOT), help="Dataset family output root.")
    parser.add_argument("--universe-path", default=str(DEFAULT_UNIVERSE_PATH), help="Approved universe CSV path.")
    parser.add_argument("--raw-twelvedata-root", default=str(DEFAULT_RAW_TWELVEDATA_ROOT), help="Raw Twelve Data root.")
    parser.add_argument("--raw-alphavantage-root", default=str(DEFAULT_RAW_ALPHAVANTAGE_ROOT), help="Raw Alpha Vantage root.")
    parser.add_argument("--stage1-manifest-path", default=str(DEFAULT_STAGE1_MANIFEST), help="Stage 1 raw security coverage manifest.")
    parser.add_argument("--stage1-ohlcv-manifest-path", default=str(DEFAULT_STAGE1_OHLCV_MANIFEST), help="Stage 1 OHLCV audit manifest.")
    parser.add_argument("--twelvedata-audit-path", default=str(DEFAULT_TWELVEDATA_AUDIT), help="Twelve Data 2010 coverage audit manifest.")
    parser.add_argument("--stage2-contract-manifest-path", default=str(DEFAULT_STAGE2_CONTRACT_MANIFEST), help="Stage 2 contract manifest.")
    parser.add_argument("--twelvedata-full-window-filename", default=FULL_WINDOW_FILENAME, help="Twelve Data raw filename to load for every ticker.")
    parser.add_argument("--allow-overwrite", action="store_true", help="Replace an existing identical-version dataset output directory.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable build summary.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(argv)
    try:
        outputs = build_stage2_benchmark_dataset(
            output_root=Path(args.output_root),
            universe_path=Path(args.universe_path),
            raw_twelvedata_root=Path(args.raw_twelvedata_root),
            raw_alphavantage_root=Path(args.raw_alphavantage_root),
            stage1_manifest_path=Path(args.stage1_manifest_path),
            stage1_ohlcv_manifest_path=Path(args.stage1_ohlcv_manifest_path),
            twelvedata_audit_path=Path(args.twelvedata_audit_path),
            stage2_contract_manifest_path=Path(args.stage2_contract_manifest_path),
            twelvedata_full_window_filename=args.twelvedata_full_window_filename,
            allow_overwrite=args.allow_overwrite,
        )
    except PanelBuildError as exc:
        print(f"STAGE2_DATASET_BUILD_FAILED: {exc}", file=sys.stderr)
        return 2

    summary: dict[str, Any] = {
        "status": "stage2_dataset_built",
        "benchmark_claim": False,
        "dataset_version": outputs.dataset_version,
        "row_count": outputs.row_count,
        "row_universe_digest": outputs.row_digest,
        "dataset_root": str(outputs.dataset_root),
        "panel_path": str(outputs.panel_path),
        "manifest_path": str(outputs.manifest_path),
        "clean_window_path": str(outputs.clean_window_path),
        "cvx_patch_manifest_path": str(outputs.cvx_patch_manifest_path),
    }
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("STAGE2 DATASET BUILD")
        print("status: stage2_dataset_built")
        print("benchmark_claim: false")
        print(f"dataset_version: {outputs.dataset_version}")
        print(f"row_count: {outputs.row_count}")
        print(f"row_universe_digest: {outputs.row_digest}")
        print(f"dataset_root: {outputs.dataset_root}")
        print(f"manifest: {outputs.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
