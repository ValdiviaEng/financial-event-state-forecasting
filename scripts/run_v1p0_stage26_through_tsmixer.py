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
    TSMIXER_FIXED_BATCH_SIZE,
    TSMIXER_FIXED_EPOCHS,
    TSMIXER_FIXED_SEEDS,
    TSMIXER_FIXED_WINDOW_LENGTH,
    run_stage18_sequence_window_materialization,
    run_stage26_finbert_contract,
    run_stage27_article_cache,
    run_stage28_finbert_aggregations,
    run_stage29_event_representation_gate,
    run_stage30_tsmixer_smoke,
    run_stage31_tsmixer_fixed_multiseed,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute v1p0 Stage 26 through fixed multiseed TSMixer with hardened blocker discipline.")
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--max-length", type=int, default=160)
    parser.add_argument("--projection-dim", type=int, default=128)
    parser.add_argument("--tsmixer-window-length", type=int, default=TSMIXER_FIXED_WINDOW_LENGTH)
    parser.add_argument("--tsmixer-epochs", type=int, default=TSMIXER_FIXED_EPOCHS)
    parser.add_argument("--tsmixer-batch-size", type=int, default=TSMIXER_FIXED_BATCH_SIZE)
    args = parser.parse_args()

    stage26 = run_stage26_finbert_contract()
    stage27 = run_stage27_article_cache(stage26, batch_size=args.batch_size, max_length=args.max_length)
    stage28 = run_stage28_finbert_aggregations(stage27, projection_dim=args.projection_dim)
    stage29 = run_stage29_event_representation_gate(stage28)
    stage18 = run_stage18_sequence_window_materialization()
    stage30 = run_stage30_tsmixer_smoke(stage18, window_length=args.tsmixer_window_length)
    stage31 = run_stage31_tsmixer_fixed_multiseed(
        stage18,
        stage30,
        window_length=args.tsmixer_window_length,
        seeds=TSMIXER_FIXED_SEEDS,
        epochs=args.tsmixer_epochs,
        batch_size=args.tsmixer_batch_size,
    )

    classification = stage31.summary["classification"]
    print(
        json.dumps(
            {
                "status": "completed_through_stage31_tsmixer_fixed_multiseed",
                "stage_statuses": {
                    "stage_26": stage26.status,
                    "stage_27": stage27.status,
                    "stage_28": stage28.status,
                    "stage_29": stage29.status,
                    "stage_18": stage18.status,
                    "stage_30": stage30.status,
                    "stage_31": stage31.status,
                },
                "stage31_manifest": stage31.summary["manifest"],
                "stage32_recommendation": classification.get("stage32_recommendation"),
                "positive_claim_approved": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
