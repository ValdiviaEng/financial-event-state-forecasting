from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from event_state_forecasting.v1p0.final_sprint import (  # noqa: E402
    PROJECT_ROOT as FINAL_PROJECT_ROOT,
    StageOutput,
    TSMIXER_OPTUNA_EPOCHS,
    TSMIXER_OPTUNA_SEEDS,
    TSMIXER_OPTUNA_TRIALS,
    run_stage32_tsmixer_optimization,
)


DEFAULT_STAGE18_MANIFEST = "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage18__sequence_windows__20260525T145000Z__src_6dff1bd__run_052914ca/sequence_window_manifest.json"
DEFAULT_STAGE31_MANIFEST = "data/v1p0_full_results/v1p0__phase1_top50_v1p0__stage31__tsmixer_fixed_multiseed_benchmark__20260525T153000Z__src_6dff1bd__run_9aa67b49/stage31_tsmixer_fixed_multiseed_benchmark_manifest.json"


def _load_stage_output(stage: int, manifest_rel_path: str) -> StageOutput:
    manifest_path = FINAL_PROJECT_ROOT / manifest_rel_path
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary: dict[str, object] = {"manifest": manifest_rel_path}
    if "classification" in payload:
        summary["classification"] = payload["classification"]
    return StageOutput(stage, str(payload.get("status", "completed")), manifest_path.parent, manifest_path, summary)  # type: ignore[arg-type]


def _parse_seeds(value: str) -> tuple[int, ...]:
    seeds = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not seeds:
        raise argparse.ArgumentTypeError("at least one seed is required")
    return seeds


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute v1p0 Stage 32 TSMixer optimization after explicit user override.")
    parser.add_argument("--stage18-manifest", default=DEFAULT_STAGE18_MANIFEST)
    parser.add_argument("--stage31-manifest", default=DEFAULT_STAGE31_MANIFEST)
    parser.add_argument("--approval-id", required=True)
    parser.add_argument("--override-stage31-recommendation", action="store_true")
    parser.add_argument("--trial-count", type=int, default=TSMIXER_OPTUNA_TRIALS)
    parser.add_argument("--epochs", type=int, default=TSMIXER_OPTUNA_EPOCHS)
    parser.add_argument("--seeds", type=_parse_seeds, default=TSMIXER_OPTUNA_SEEDS)
    args = parser.parse_args()

    stage18 = _load_stage_output(18, args.stage18_manifest)
    stage31 = _load_stage_output(31, args.stage31_manifest)
    stage32 = run_stage32_tsmixer_optimization(
        stage18,
        stage31,
        approval_id=args.approval_id,
        override_stage31_recommendation=args.override_stage31_recommendation,
        trial_count=args.trial_count,
        seeds=args.seeds,
        epochs=args.epochs,
    )
    print(
        json.dumps(
            {
                "status": "completed_stage32_tsmixer_optimization",
                "stage32_manifest": stage32.summary["manifest"],
                "best_candidate": stage32.summary["best_candidate"],
                "positive_claim_approved": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
