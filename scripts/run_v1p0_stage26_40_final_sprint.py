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
    run_stage26_finbert_contract,
    run_stage27_article_cache,
    run_stage28_finbert_aggregations,
    run_stage29_event_representation_gate,
    run_stage30_tsmixer_smoke,
    run_stage34_market_event_fusion,
    run_stage35_full_diagnostics,
    run_stage36_accuracy_overfit_frontier,
    run_stage37_report_packet,
    run_stage38_truth_audit,
    run_stage39_claim_review,
    run_stage40_completion,
    write_deferred_stage,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute v1p0 final sprint stages 26 through 40 with artifact-backed non-claim discipline.")
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--max-length", type=int, default=160)
    args = parser.parse_args()

    outputs = []
    stage26 = run_stage26_finbert_contract()
    outputs.append(stage26)
    stage27 = run_stage27_article_cache(stage26, batch_size=args.batch_size, max_length=args.max_length)
    outputs.append(stage27)
    stage28 = run_stage28_finbert_aggregations(stage27)
    outputs.append(stage28)
    stage29 = run_stage29_event_representation_gate(stage28)
    outputs.append(stage29)
    stage30 = run_stage30_tsmixer_smoke(stage28)
    outputs.append(stage30)

    stage31 = write_deferred_stage(
        31,
        "tsmixer_fixed_multiseed_benchmark",
        "Stage 30 produced smoke-only TSMixer evidence; full historical multiseed TSMixer was not executed in this final-sprint pass.",
        ["full sequence-window artifact", "fixed multiseed compute budget", "Stage 31 run approval after smoke review"],
    )
    outputs.append(stage31)
    stage32 = write_deferred_stage(
        32,
        "tsmixer_optimization_overfit_control",
        "Stage 32 is conditional on promising Stage 31 standalone multiseed evidence, which is not available.",
        ["Stage 31 fixed multiseed benchmark evidence", "explicit optimization approval based on Stage 31"],
    )
    outputs.append(stage32)
    stage33 = write_deferred_stage(
        33,
        "market_ensemble_horizon_meta",
        "Stage 33 requires standalone XGBoost and TSMixer out-of-sample evidence; TSMixer fixed multiseed evidence is deferred.",
        ["Stage 31 or 32 TSMixer evidence", "fold-local meta-combiner config"],
    )
    outputs.append(stage33)

    stage34 = run_stage34_market_event_fusion(stage28, stage29)
    outputs.append(stage34)
    stage35 = run_stage35_full_diagnostics(stage29, stage34)
    outputs.append(stage35)
    stage36 = run_stage36_accuracy_overfit_frontier(stage35)
    outputs.append(stage36)
    stage37 = run_stage37_report_packet(stage35, stage36)
    outputs.append(stage37)
    stage38 = run_stage38_truth_audit(outputs)
    outputs.append(stage38)
    stage39 = run_stage39_claim_review(stage35, stage36, stage37, stage38)
    outputs.append(stage39)
    stage40 = run_stage40_completion(outputs)
    outputs.append(stage40)

    print(
        json.dumps(
            {
                "status": "completed_with_deferred_tsmixer_expansion",
                "stage_statuses": {f"stage_{output.stage:02d}": output.status for output in outputs},
                "stage40_manifest": stage40.summary["manifest"],
                "positive_claim_approved": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
